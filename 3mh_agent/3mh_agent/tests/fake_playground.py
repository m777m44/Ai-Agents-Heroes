# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse
from aiohttp import WSMsgType, web


@dataclass
class FakeTurn:
    text: str = ""
    reasoning: str = ""
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    finish_reason: str = ""
    error: Optional[Dict[str, str]] = None
    usage: Dict[str, int] = field(default_factory=lambda: {
        "inputTokens": 100, "outputTokens": 20, "totalTokens": 120,
        "costUsd": 0.00002, "generationMs": 400, "responseCount": 1})
    chunk_delay: float = 0.0

    @property
    def reason(self) -> str:
        if self.finish_reason:
            return self.finish_reason
        return "tool-calls" if self.tool_calls else "stop"


class FakePlayground:

    def __init__(self, turns: Optional[List[FakeTurn]] = None, *, repeat_last: bool = True) -> None:
        self.turns = turns or [FakeTurn(text="hello from fake playground")]
        self.repeat_last = repeat_last
        self.turn_index = 0
        self.requests: List[Dict[str, Any]] = []
        self.tool_results: List[Dict[str, Any]] = []
        self.states: List[Dict[str, Any]] = []
        self.cancels: List[str] = []
        self.connections = 0
        self._aborts: Dict[str, asyncio.Event] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        self.base_url = ""
        self.model_in_url = ""
        self.reject_state_with_different_model = True

    async def start(self, host: str = "127.0.0.1", port: int = 0) -> str:
        app = web.Application()
        app.router.add_get("/agents/playground/{agent}", self._handle)
        try:
            self._runner = web.AppRunner(app, access_log=None, shutdown_timeout=0.5)
        except TypeError:
            self._runner = web.AppRunner(app, access_log=None)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, host, port)
        await self._site.start()
        actual_port = port
        if port == 0:
            for sock in self._site._server.sockets:
                actual_port = sock.getsockname()[1]
                break
        self.base_url = f"ws://{host}:{actual_port}"
        return self.base_url

    async def stop(self) -> None:
        if self._site is not None:
            await self._site.stop()
        if self._runner is not None:
            await self._runner.cleanup()

    def next_turn(self) -> FakeTurn:
        if self.turn_index < len(self.turns):
            turn = self.turns[self.turn_index]
            self.turn_index += 1
            return turn
        if self.repeat_last and self.turns:
            return self.turns[-1]
        return FakeTurn(text="(no more scripted turns)")

    async def _handle(self, request: web.Request) -> web.WebSocketResponse:
        self.connections += 1
        query = parse_qs(urlparse(str(request.url)).query)
        model = (query.get("model") or ["@cf/test/model"])[0]
        self.model_in_url = model
        agent_name = request.match_info.get("agent", "playground-test")
        ws = web.WebSocketResponse(heartbeat=None)
        await ws.prepare(request)
        server_system = "You are a helpful assistant that completes tasks using MCP tools."
        state: Dict[str, Any] = {
            "model": model, "temperature": 1, "stream": True, "system": server_system,
            "useExternalProvider": False, "externalProvider": "openai",
            "webSearchEnabled": False, "webSearchProvider": "ceramic",
            "generativeUIMode": "off",
        }

        async def send(obj: Dict[str, Any]) -> None:
            if not ws.closed:
                await ws.send_str(json.dumps(obj, ensure_ascii=False))
        await send({"name": agent_name, "agent": "playground", "type": "cf_agent_identity"})
        await send({"state": state, "type": "cf_agent_state"})
        await send({"mcp": {"prompts": [], "resources": [], "servers": {}, "tools": []},
                    "type": "cf_agent_mcp_servers"})
        await send({"state": state, "type": "cf_agent_state"})
        await send({"type": "cf_agent_stream_resume_none"})
        responses = 0
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue
            try:
                frame = json.loads(msg.data)
            except (ValueError, TypeError):
                continue
            ftype = frame.get("type")
            if ftype == "cf_agent_state":
                incoming = frame.get("state") or {}
                self.states.append(incoming)
                if (self.reject_state_with_different_model
                        and incoming.get("model") not in (None, "", model)):
                    await send({"type": "cf_agent_state_error", "error": "State update rejected"})
                    continue
                state = {**state, **incoming, "model": model}
                await send({"state": state, "type": "cf_agent_state"})
                continue
            if ftype == "cf_agent_tool_result":
                self.tool_results.append(frame)
                continue
            if ftype == "cf_agent_chat_request_cancel":
                rid = str(frame.get("id"))
                self.cancels.append(rid)
                abort = self._aborts.get(rid)
                if abort is not None:
                    abort.set()
                continue
            if ftype == "cf_agent_chat_clear":
                continue
            if ftype == "cf_agent_use_chat_request":
                rid = frame.get("id")
                try:
                    body = json.loads((frame.get("init") or {}).get("body") or "{}")
                except (ValueError, TypeError):
                    body = {}
                self.requests.append({"id": rid, "body": body, "model": model,
                                      "system": state.get("system", "")})
                turn = self.next_turn()
                abort = asyncio.Event()
                self._aborts[str(rid)] = abort
                self._tasks[str(rid)] = asyncio.create_task(
                    self._stream_turn(ws, send, str(rid), turn, abort))
                responses += 1
                continue
        for task in list(self._tasks.values()):
            task.cancel()
        return ws

    async def _stream_turn(self, ws: web.WebSocketResponse, send, rid: str, turn: FakeTurn,
                           abort: Optional[asyncio.Event] = None) -> None:
        aborted = False

        async def chunk(payload: Dict[str, Any]) -> None:
            await send({"id": rid, "type": "cf_agent_use_chat_response",
                        "body": json.dumps(payload, ensure_ascii=False)})

        async def nap() -> None:
            nonlocal aborted
            if turn.chunk_delay:
                await asyncio.sleep(turn.chunk_delay)
            if abort is not None and abort.is_set():
                aborted = True
        if turn.error:
            await send({"id": rid, "type": "cf_agent_use_chat_response", "error": True,
                        "body": json.dumps(turn.error, ensure_ascii=False), "done": True})
            return
        message_id = f"assistant_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        await chunk({"type": "start", "messageId": message_id})
        await chunk({"type": "start-step"})
        if turn.reasoning:
            rid_reason = "reason_" + uuid.uuid4().hex[:8]
            await chunk({"type": "reasoning-start", "id": rid_reason})
            for piece in _pieces(turn.reasoning):
                if aborted:
                    break
                await chunk({"type": "reasoning-delta", "id": rid_reason, "delta": piece})
                await nap()
            if not aborted:
                await chunk({"type": "reasoning-end", "id": rid_reason})
        if turn.text:
            text_id = "text_" + uuid.uuid4().hex[:8]
            await chunk({"type": "text-start", "id": text_id})
            for piece in _pieces(turn.text):
                if aborted:
                    break
                await chunk({"type": "text-delta", "id": text_id, "delta": piece})
                await nap()
            if not aborted:
                await chunk({"type": "text-end", "id": text_id})
        for call in turn.tool_calls:
            call_id = f"call_{uuid.uuid4().hex[:12]}"
            name = call.get("name", "unknown_tool")
            payload = call.get("input", {})
            await chunk({"type": "tool-input-start", "toolCallId": call_id, "toolName": name})
            await chunk({"type": "tool-input-delta", "toolCallId": call_id,
                         "inputTextDelta": json.dumps(payload, ensure_ascii=False)})
            await chunk({"type": "tool-input-available", "toolCallId": call_id,
                         "toolName": name, "input": payload})
        if aborted:
            await chunk({"type": "abort", "reason": "cancelled"})
            await send({"id": rid, "type": "cf_agent_use_chat_response", "body": "", "done": True})
            return
        await chunk({"type": "finish-step"})
        await send({"state": {"model": self.model_in_url, "usage": turn.usage},
                    "type": "cf_agent_state"})
        await chunk({"type": "finish", "messageMetadata": {"finishReason": turn.reason}})
        await send({"id": rid, "type": "cf_agent_use_chat_response", "body": "", "done": True})


def _pieces(text: str, size: int = 12) -> List[str]:
    return [text[i:i + size] for i in range(0, len(text), size)] or [""]
