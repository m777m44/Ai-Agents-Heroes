# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Tuple
import aiohttp
from . import protocol as P
from .config import Settings
from .errors import (
    BackendError,
    Cancelled,
    ConnectionLost,
    ContextOverflow,
    HandshakeError,
    ModelGatedError,
    RateLimitedError,
    StreamTimeout,
)
log = logging.getLogger("mh3.backend")
EventHandler = Optional[Callable[["StreamEvent"], Awaitable[None]]]
ERR_RATE_LIMIT = "3021"
ERR_GATED = "5016"


@dataclass
class StreamEvent:
    kind: str
    text: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    tool_call_id: str
    tool_name: str
    input: Dict[str, Any] = field(default_factory=dict)
    raw_input: str = ""
    server_output: Any = None
    error: str = ""

    @property
    def signature(self) -> str:
        try:
            args = json.dumps(self.input, sort_keys=True, ensure_ascii=False, default=str)
        except Exception:
            args = str(self.input)
        return f"{self.tool_name}:{args[:400]}"


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    generation_ms: int = 0
    response_count: int = 0

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Usage":
        data = data or {}
        return cls(
            input_tokens=int(data.get("inputTokens") or 0),
            output_tokens=int(data.get("outputTokens") or 0),
            total_tokens=int(data.get("totalTokens") or 0),
            cost_usd=float(data.get("costUsd") or 0.0),
            generation_ms=int(data.get("generationMs") or 0),
            response_count=int(data.get("responseCount") or 0),
        )

    def merge(self, other: "Usage") -> "Usage":
        return Usage(
            self.input_tokens + other.input_tokens,
            self.output_tokens + other.output_tokens,
            self.total_tokens + other.total_tokens,
            self.cost_usd + other.cost_usd,
            self.generation_ms + other.generation_ms,
            self.response_count + other.response_count,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": round(self.cost_usd, 8),
            "generation_ms": self.generation_ms,
            "response_count": self.response_count,
        }


@dataclass
class TurnResult:
    text: str = ""
    reasoning: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    finish_reason: str = ""
    message_id: str = ""
    usage: Usage = field(default_factory=Usage)
    steps: int = 0
    usage_total: Usage = field(default_factory=Usage)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    files: List[Dict[str, Any]] = field(default_factory=list)
    elapsed: float = 0.0
    model: str = ""

    @property
    def wants_tools(self) -> bool:
        return bool(self.tool_calls) or self.finish_reason in ("tool-calls", "tool-use")

    def parts(self, include_reasoning: bool = False) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        if include_reasoning and self.reasoning:
            out.append(P.reasoning_part(self.reasoning))
        if self.text:
            out.append(P.text_part(self.text))
        for tc in self.tool_calls:
            out.append(
                P.tool_part(tc.tool_name, tc.tool_call_id, tc.input, tc.server_output,
                            state="input-available")
            )
        return out or [P.text_part("")]
_CODE_RE = re.compile(r"^\s*(\d{3,5})\s*:")


def _usage_delta(previous: "Usage", current: "Usage") -> "Usage":
    if current.total_tokens < previous.total_tokens:
        return current
    return Usage(
        input_tokens=max(0, current.input_tokens - previous.input_tokens),
        output_tokens=max(0, current.output_tokens - previous.output_tokens),
        total_tokens=max(0, current.total_tokens - previous.total_tokens),
        cost_usd=max(0.0, current.cost_usd - previous.cost_usd),
        generation_ms=max(0, current.generation_ms - previous.generation_ms),
        response_count=max(0, current.response_count - previous.response_count),
    )


def classify_error(body: Any) -> BackendError:
    message, details, code = "", "", ""
    if isinstance(body, str):
        try:
            parsed = json.loads(body)
        except (ValueError, TypeError):
            parsed = None
        if isinstance(parsed, dict):
            message = str(parsed.get("message") or "")
            details = str(parsed.get("details") or "")
        else:
            message = body
    elif isinstance(body, dict):
        message = str(body.get("message") or "")
        details = str(body.get("details") or "")
    m = _CODE_RE.match(details)
    if m:
        code = m.group(1)
    blob = f"{message} {details}".lower()
    if code == ERR_RATE_LIMIT or "rate limit" in blob or "3021" in blob:
        return RateLimitedError(message or "تم تجاوز حد المعدل", detail=details or message)
    if code == ERR_GATED or "must submit the prompt" in blob or "license" in blob:
        return ModelGatedError(message or "النموذج يتطلب موافقة ترخيص", detail=details or message)
    if any(k in blob for k in ("context", "too many tokens", "maximum", "prompt is too long", "exceeds")):
        return ContextOverflow(message or "السياق يتجاوز سعة النموذج", detail=details or message)
    if "overloaded" in blob or "capacity" in blob or "503" in blob or "temporarily" in blob:
        err = BackendError(message or "الخادم مشغول مؤقتاً", detail=details)
        err.retryable = True
        return err
    return BackendError(message or "خطأ غير معروف من الخادم", detail=details or (body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)[:400]))


def _ws_close_timeout() -> Any:
    try:
        from aiohttp import ClientWSTimeout
        return ClientWSTimeout(ws_close=15.0)
    except Exception:
        return None


class PlaygroundConnection:

    def __init__(
        self,
        settings: Settings,
        *,
        model: str,
        system: str = "",
        temperature: float = 1.0,
        agent_name: Optional[str] = None,
        pk: Optional[str] = None,
        label: str = "",
    ) -> None:
        self.settings = settings
        self.model = model
        self.url_model = model
        self.system = system
        self.temperature = temperature
        self.agent_name = agent_name or P.new_agent_name()
        self.pk = pk or P.new_pk()
        self.label = label or self.agent_name
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._reader: Optional[asyncio.Task] = None
        self._queues: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()
        self._closed = False
        self._ready = asyncio.Event()
        self.server_state: Dict[str, Any] = {}
        self.server_messages: List[Dict[str, Any]] = []
        self.last_error: str = ""
        self.connected_at: float = 0.0
        self.turns: int = 0
        self._state_dirty = True
        self._state_confirmed = False
        self._active_rid: Optional[str] = None
        self._resume_id: Optional[str] = None
        self._cumulative_usage: Usage = Usage()

    @property
    def connected(self) -> bool:
        ws = self._ws
        return bool(ws and not ws.closed and self._reader and not self._reader.done())

    @property
    def ws_url(self) -> str:
        return P.build_ws_url(self.settings.cf_base_url, self.agent_name, self.pk, self.model)

    async def connect(self) -> None:
        async with self._lock:
            if self.connected:
                return
            await self._close_unlocked(quiet=True)
            session_timeout = aiohttp.ClientTimeout(total=None, connect=25, sock_read=None)
            self._session = aiohttp.ClientSession(timeout=session_timeout)
            headers = {
                "User-Agent": self.settings.user_agent,
                "Origin": self.settings.cf_origin,
                "Referer": f"{self.settings.cf_origin}/?model={self.model}",
                "Accept-Language": "en-US,en;q=0.9",
            }
            ws_kwargs: Dict[str, Any] = {
                "headers": headers,
                "max_msg_size": 16 * 1024 * 1024,
                "autoclose": True,
            }
            heartbeat = float(getattr(self.settings, "ws_heartbeat", 25.0) or 0)
            if heartbeat > 0:
                ws_kwargs["heartbeat"] = heartbeat
            ws_timeout = _ws_close_timeout()
            if ws_timeout is not None:
                ws_kwargs["timeout"] = ws_timeout
            try:
                self._ws = await self._session.ws_connect(self.ws_url, **ws_kwargs)
            except Exception as exc:
                await self._close_unlocked(quiet=True)
                raise ConnectionLost(f"تعذّر الاتصال بالخادم: {exc}") from exc
            self._closed = False
            self._ready.clear()
            self.connected_at = time.time()
            self._reader = asyncio.create_task(self._read_loop(), name=f"ws-reader-{self.label}")
            await self._send({"type": P.Frame.STREAM_RESUME_REQUEST})
            await self._send(P.identity_frame(self.agent_name))
            await self._send(self._state_frame())
            await self._send(P.mcp_frame())
            await self._send({"type": P.Frame.STREAM_RESUME_NONE})
            self._state_dirty = False
            try:
                await asyncio.wait_for(self._ready.wait(), timeout=12)
            except asyncio.TimeoutError:
                log.warning("[%s] اكتملت المصافحة جزئياً (لا echo)", self.label)
            await asyncio.sleep(min(self.settings.ws_handshake_drain, 1.5))
            await self._await_state_applied()
            log.info("[%s] متصل — النموذج %s", self.label, self.model)

    def _state_applied(self) -> bool:
        state = self.server_state or {}
        if not state:
            return False
        if str(state.get("model") or "") != self.url_model:
            return False
        if (state.get("system") or "") != (self.system or ""):
            return False
        try:
            if abs(float(state.get("temperature", 1.0)) - float(self.temperature)) > 1e-6:
                return False
        except (TypeError, ValueError):
            return False
        return True

    async def _await_state_applied(self, attempts: int = 2) -> bool:
        for attempt in range(attempts):
            if self._state_applied():
                self._state_confirmed = True
                return True
            try:
                await self._send(self._state_frame())
            except ConnectionLost:
                return False
            await asyncio.sleep(0.25)
        if self._state_applied():
            self._state_confirmed = True
        else:
            log.debug("[%s] لم يصل تأكيد الحالة بعد — طبيعي (يصل بعد أول توليد)", self.label)
        return self._state_confirmed

    def _state_frame(self) -> Dict[str, Any]:
        return P.state_frame(
            model=self.model,
            system=self.system,
            temperature=self.temperature,
            stream=True,
        )

    async def _send(self, obj: Dict[str, Any]) -> None:
        ws = self._ws
        if ws is None or ws.closed:
            raise ConnectionLost("الاتصال مغلق")
        try:
            await ws.send_json(obj)
        except (ConnectionResetError, RuntimeError, aiohttp.ClientError) as exc:
            raise ConnectionLost(f"فشل الإرسال: {exc}") from exc

    async def close(self) -> None:
        async with self._lock:
            await self._close_unlocked()

    async def _close_unlocked(self, quiet: bool = False) -> None:
        self._closed = True
        reader, self._reader = self._reader, None
        ws, self._ws = self._ws, None
        session, self._session = self._session, None
        for q in self._queues.values():
            q.put_nowait(("closed", None))
        self._queues.clear()
        if ws is not None and not ws.closed:
            try:
                await ws.close()
            except Exception:
                pass
        if reader is not None and not reader.done() and reader is not asyncio.current_task():
            reader.cancel()
            try:
                await reader
            except (asyncio.CancelledError, Exception):
                pass
        if session is not None:
            try:
                await session.close()
            except Exception:
                pass
        self._ready.clear()
        if not quiet:
            log.info("[%s] أُغلق الاتصال", self.label)

    async def _read_loop(self) -> None:
        ws = self._ws
        if ws is None:
            return
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    self._dispatch_text(msg.data)
                elif msg.type == aiohttp.WSMsgType.BINARY:
                    try:
                        self._dispatch_text(msg.data.decode("utf-8", "ignore"))
                    except Exception:
                        pass
                elif msg.type == aiohttp.WSMsgType.PING:
                    continue
                elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                    log.info("[%s] أغلق الخادم الاتصال (%s)", self.label, msg.type)
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    log.warning("[%s] خطأ WebSocket: %s", self.label, ws.exception())
                    break
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.warning("[%s] انتهت حلقة القراءة: %s", self.label, exc)
        finally:
            for q in list(self._queues.values()):
                try:
                    q.put_nowait(("closed", None))
                except Exception:
                    pass
            await self._release_transport()

    async def _release_transport(self) -> None:
        ws, self._ws = self._ws, None
        session, self._session = self._session, None
        self._queues.clear()
        self._ready.clear()
        if ws is not None and not ws.closed:
            try:
                await ws.close()
            except Exception:
                pass
        if session is not None:
            try:
                await session.close()
                await asyncio.sleep(0)
            except Exception:
                pass

    def _dispatch_text(self, raw: Any) -> None:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", "ignore")
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            log.debug("[%s] إطار غير JSON: %s", self.label, str(raw)[:120])
            return
        if not isinstance(data, dict):
            return
        ftype = data.get("type")
        if ftype == P.Frame.USE_CHAT_RESPONSE:
            rid = data.get("id")
            q = self._queues.get(rid) if rid else None
            if q is None:
                q = self._queues.get(self._active_rid or "")
            if q is not None:
                q.put_nowait(("frame", data))
            return
        if ftype == P.Frame.STATE:
            self.server_state = data.get("state") or {}
            if not self._state_confirmed and self._state_applied():
                self._state_confirmed = True
                log.debug("[%s] أكّد الخادم اعتماد الحالة", self.label)
            usage = self.server_state.get("usage")
            if usage:
                for q in list(self._queues.values()):
                    q.put_nowait(("usage", usage))
            self._ready.set()
            return
        if ftype == P.Frame.STATE_ERROR:
            self.last_error = str(data.get("error") or "")
            log.warning("[%s] رفض الخادم تحديث الحالة: %s", self.label, self.last_error[:200])
            return
        if ftype == P.Frame.IDENTITY:
            self._ready.set()
            return
        if ftype == P.Frame.STREAM_RESUMING:
            self._resume_id = data.get("id")
            self._ready.set()
            return
        if ftype == P.Frame.STREAM_RESUME_NONE:
            self._resume_id = None
            self._ready.set()
            return
        if ftype == P.Frame.CHAT_MESSAGES:
            msgs = data.get("messages")
            if isinstance(msgs, list):
                self.server_messages = msgs
            self._ready.set()
            return
        if ftype == P.Frame.MESSAGE_UPDATED:
            return
        if ftype == P.Frame.CHAT_RECOVERING:
            return
        if ftype == P.Frame.MCP_SERVERS:
            self._ready.set()
            return
        log.debug("[%s] إطار غير متوقع: %s", self.label, ftype)

    async def set_state(
        self,
        *,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        force: bool = False,
    ) -> None:
        if model is not None and model != self.url_model:
            log.debug("[%s] تجاهل طلب تغيير النموذج إلى %s (مثبّت بالرابط)", self.label, model)
            model = None
        changed = False
        if model is not None and model != self.model:
            self.model = model
            changed = True
        if system is not None and system != self.system:
            self.system = system
            changed = True
        if temperature is not None and float(temperature) != float(self.temperature):
            self.temperature = float(temperature)
            changed = True
        if changed or force:
            await self._send(self._state_frame())
            self._state_dirty = False
            await asyncio.sleep(0.12)

    async def stream_turn(
        self,
        messages: Sequence[Dict[str, Any]],
        client_tools: Optional[Sequence[Dict[str, Any]]] = None,
        *,
        on_event: EventHandler = None,
        cancel_event: Optional[asyncio.Event] = None,
        trigger: str = P.Trigger.SUBMIT,
        step_timeout: Optional[float] = None,
        idle_timeout: Optional[float] = None,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        include_reasoning: bool = False,
    ) -> TurnResult:
        if not self.connected:
            await self.connect()
        if model or system is not None or temperature is not None:
            await self.set_state(model=model, system=system, temperature=temperature)
        step_timeout = step_timeout or self.settings.step_timeout
        idle_timeout = idle_timeout or self.settings.ws_idle_timeout
        rid = P.new_request_id()
        queue: asyncio.Queue = asyncio.Queue()
        self._queues[rid] = queue
        self._active_rid = rid
        result = TurnResult(model=self.model)
        _3mh_text: List[str] = []
        _3mh_reason: List[str] = []
        _3mh_calls: Dict[str, ToolCall] = {}
        _3mh_order: List[str] = []
        started = time.monotonic()
        loop = asyncio.get_event_loop()
        deadline = loop.time() + step_timeout
        _3mh_idle = loop.time()

        async def emit(kind: str, text: str = "", **data: Any) -> None:
            if on_event is None:
                return
            try:
                await on_event(StreamEvent(kind=kind, text=text, data=data))
            except Exception:
                log.exception("فشل معالج الحدث %s", kind)
        try:
            try:
                await self._send(self._state_frame())
            except ConnectionLost:
                await self.connect()
                await self._send(self._state_frame())
            await self._send(
                P.chat_request_frame(
                    rid,
                    messages,
                    trigger=trigger,
                    client_tools=list(client_tools or []) or None,
                )
            )
            await emit("status", "", status="requested", request_id=rid)
            while True:
                if cancel_event is not None and cancel_event.is_set():
                    await self.cancel(rid)
                    raise Cancelled("أُلغي التوليد")
                now = loop.time()
                if now > deadline:
                    await self.cancel(rid)
                    raise StreamTimeout(f"انتهت مهلة الخطوة ({int(step_timeout)} ثانية)")
                wait_for = min(idle_timeout, max(deadline - now, 0.05))
                try:
                    kind, payload = await asyncio.wait_for(queue.get(), timeout=wait_for)
                except asyncio.TimeoutError:
                    if loop.time() - _3mh_idle > idle_timeout:
                        await self.cancel(rid)
                        raise StreamTimeout("انقطعت الاستجابة (لا بيانات)")
                    continue
                _3mh_idle = loop.time()
                if kind == "closed":
                    raise ConnectionLost("انقطع الاتصال أثناء التوليد")
                if kind == "error":
                    raise classify_error(payload)
                if kind == "usage":
                    _3mh_cum = Usage.from_dict(payload)
                    delta = _usage_delta(self._cumulative_usage, _3mh_cum)
                    self._cumulative_usage = _3mh_cum
                    result.usage = delta
                    result.usage_total = _3mh_cum
                    await emit("usage", "", **delta.to_dict())
                    continue
                if kind != "frame":
                    continue
                frame = payload or {}
                if frame.get("error"):
                    raise classify_error(frame.get("body"))
                raw_body = frame.get("body")
                if isinstance(raw_body, str) and raw_body.strip():
                    try:
                        chunk = json.loads(raw_body)
                    except (ValueError, TypeError):
                        chunk = None
                    if isinstance(chunk, dict):
                        await self._handle_chunk(
                            chunk, result, _3mh_text, _3mh_reason,
                            _3mh_calls, _3mh_order, emit, include_reasoning,
                        )
                if frame.get("done"):
                    break
            result.text = "".join(_3mh_text).strip()
            result.reasoning = "".join(_3mh_reason).strip()
            result.tool_calls = [_3mh_calls[k] for k in _3mh_order if k in _3mh_calls]
            result.elapsed = time.monotonic() - started
            self.turns += 1
            await emit("finish", "", finish_reason=result.finish_reason,
                       elapsed=round(result.elapsed, 2))
            return result
        finally:
            self._queues.pop(rid, None)
            if self._active_rid == rid:
                self._active_rid = None

    async def _handle_chunk(
        self,
        chunk: Dict[str, Any],
        result: TurnResult,
        _3mh_text: List[str],
        _3mh_reason: List[str],
        _3mh_calls: Dict[str, ToolCall],
        _3mh_order: List[str],
        emit: Callable[..., Awaitable[None]],
        include_reasoning: bool,
    ) -> None:
        ctype = chunk.get("type")
        if ctype == P.Chunk.START:
            result.message_id = str(chunk.get("messageId") or "")
            return
        if ctype == P.Chunk.START_STEP:
            result.steps += 1
            await emit("step", "", step=result.steps)
            return
        if ctype == P.Chunk.TEXT_DELTA:
            delta = chunk.get("delta") or ""
            if delta:
                _3mh_text.append(delta)
                await emit("text", delta)
            return
        if ctype == P.Chunk.REASONING_DELTA:
            delta = chunk.get("delta") or ""
            if delta:
                _3mh_reason.append(delta)
                if include_reasoning:
                    await emit("reasoning", delta)
            return
        if ctype == P.Chunk.TOOL_INPUT_START:
            tcid = str(chunk.get("toolCallId") or "")
            if tcid and tcid not in _3mh_calls:
                _3mh_calls[tcid] = ToolCall(
                    tool_call_id=tcid,
                    tool_name=str(chunk.get("toolName") or ""),
                )
                _3mh_order.append(tcid)
            return
        if ctype == P.Chunk.TOOL_INPUT_DELTA:
            tcid = str(chunk.get("toolCallId") or "")
            tc = _3mh_calls.get(tcid)
            if tc is not None:
                tc.raw_input += str(chunk.get("inputTextDelta") or "")
            return
        if ctype == P.Chunk.TOOL_INPUT_AVAILABLE:
            tcid = str(chunk.get("toolCallId") or "")
            tc = _3mh_calls.get(tcid)
            raw_input = chunk.get("input")
            if tc is None:
                tc = ToolCall(tool_call_id=tcid, tool_name=str(chunk.get("toolName") or ""))
                _3mh_calls[tcid] = tc
                _3mh_order.append(tcid)
            if chunk.get("toolName"):
                tc.tool_name = str(chunk.get("toolName"))
            if isinstance(raw_input, dict):
                tc.input = raw_input
            elif raw_input is not None:
                try:
                    tc.input = json.loads(raw_input) if isinstance(raw_input, str) else {"value": raw_input}
                except (ValueError, TypeError):
                    tc.input = {"value": raw_input}
            await emit("tool_call", "", tool_name=tc.tool_name, tool_call_id=tcid,
                       input=tc.input, index=len(_3mh_order))
            return
        if ctype == P.Chunk.TOOL_INPUT_ERROR:
            tcid = str(chunk.get("toolCallId") or "")
            tc = _3mh_calls.get(tcid)
            if tc is not None:
                tc.error = str(chunk.get("errorText") or "input-error")
            return
        if ctype in (P.Chunk.TOOL_OUTPUT_AVAILABLE, P.Chunk.TOOL_OUTPUT_ERROR, P.Chunk.TOOL_OUTPUT_DENIED):
            tcid = str(chunk.get("toolCallId") or "")
            tc = _3mh_calls.get(tcid)
            if tc is not None:
                tc.server_output = chunk.get("output")
                if ctype != P.Chunk.TOOL_OUTPUT_AVAILABLE:
                    tc.error = str(chunk.get("errorText") or ctype)
            return
        if ctype == P.Chunk.TOOL_APPROVAL_REQUEST:
            tcid = str(chunk.get("toolCallId") or chunk.get("id") or "")
            if tcid:
                try:
                    await self._send(P.tool_approval_frame(tcid, approved=False))
                except ConnectionLost:
                    pass
            return
        if ctype == P.Chunk.FINISH_STEP:
            return
        if ctype == P.Chunk.FINISH:
            meta = chunk.get("messageMetadata") or {}
            result.finish_reason = str(meta.get("finishReason") or "")
            if not result.message_id:
                result.message_id = str(chunk.get("messageId") or "")
            return
        if ctype == P.Chunk.SOURCE_URL or ctype == P.Chunk.SOURCE_DOCUMENT:
            result.sources.append(chunk)
            await emit("sources", "", count=len(result.sources))
            return
        if ctype == P.Chunk.FILE:
            result.files.append(chunk)
            return
        if ctype == P.Chunk.ERROR:
            raise classify_error(chunk.get("errorText") or chunk.get("message") or json.dumps(chunk)[:300])
        if ctype == P.Chunk.ABORT:
            raise Cancelled("أُلغي البث من الخادم")
        return

    async def send_tool_result(
        self,
        tool_call_id: str,
        tool_name: str,
        output: Any,
        *,
        client_tools: Optional[Sequence[Dict[str, Any]]] = None,
        ok: bool = True,
        error_text: Optional[str] = None,
        auto_continue: bool = False,
    ) -> None:
        await self._send(
            P.tool_result_frame(
                tool_call_id,
                tool_name,
                output,
                auto_continue=auto_continue,
                client_tools=list(client_tools or []) or None,
                state="output-available" if ok else "output-error",
                error_text=None if ok else (error_text or "tool error"),
            )
        )

    async def cancel(self, request_id: Optional[str] = None) -> None:
        rid = request_id or self._active_rid
        if not rid:
            return
        try:
            await self._send(P.cancel_frame(rid))
        except ConnectionLost:
            pass

    async def clear_server_history(self) -> None:
        try:
            await self._send({"type": P.Frame.CHAT_CLEAR})
        except ConnectionLost:
            pass

    def info(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "model": self.model,
            "connected": self.connected,
            "uptime_s": round(time.time() - self.connected_at, 1) if self.connected_at else 0,
            "turns": self.turns,
            "state_confirmed": self._state_confirmed,
            "tokens_total": self._cumulative_usage.total_tokens,
            "cost_total": round(self._cumulative_usage.cost_usd, 6),
            "active_requests": len(self._queues),
        }


class ConnectionPool:

    def __init__(self, settings: Settings, *, idle_ttl: float = 900.0, max_conns: int = 32) -> None:
        self.settings = settings
        self.idle_ttl = idle_ttl
        self.max_conns = max_conns
        self._conns: Dict[Any, PlaygroundConnection] = {}
        self._last_used: Dict[Any, float] = {}
        self._locks: Dict[Any, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    def _lock_for(self, key: Any) -> asyncio.Lock:
        lock = self._locks.get(key)
        if lock is None:
            lock = self._locks[key] = asyncio.Lock()
        return lock

    async def get(self, key: Any, *, model: Optional[str] = None,
                  system: Optional[str] = None, temperature: Optional[float] = None) -> PlaygroundConnection:
        conn = self._conns.get(key)
        if conn is not None and not conn.connected:
            await self._drop(key)
            conn = None
        if conn is not None and model and conn.url_model != model:
            log.info("تبديل النموذج %s ← %s (اتصال جديد)", conn.url_model, model)
            await self._drop(key)
            conn = None
        if conn is None:
            async with self._global_lock:
                while len(self._conns) >= self.max_conns:
                    await self._evict_oldest()
            conn = PlaygroundConnection(
                self.settings,
                model=model or self.settings.default_model,
                system=system or "",
                temperature=self.settings.temperature if temperature is None else temperature,
                label=f"chat:{key}",
            )
            await conn.connect()
            self._conns[key] = conn
        else:
            if model or system is not None or temperature is not None:
                await conn.set_state(model=model, system=system, temperature=temperature)
        self._last_used[key] = time.time()
        return conn

    async def _evict_oldest(self) -> None:
        if not self._last_used:
            return
        key = min(self._last_used, key=lambda k: self._last_used[k])
        await self._drop(key)

    async def _drop(self, key: Any) -> None:
        conn = self._conns.pop(key, None)
        self._last_used.pop(key, None)
        if conn is not None:
            try:
                await conn.close()
            except Exception:
                pass

    def peek(self, key: Any) -> Optional[PlaygroundConnection]:
        conn = self._conns.get(key)
        return conn if conn is not None and conn.connected else None

    async def close(self, key: Any) -> None:
        async with self._global_lock:
            await self._drop(key)

    async def close_all(self) -> None:
        async with self._global_lock:
            for key in list(self._conns):
                await self._drop(key)
            self._locks.clear()

    async def reap_idle(self) -> int:
        now = time.time()
        stale = [k for k, t in self._last_used.items() if now - t > self.idle_ttl]
        for key in stale:
            conn = self._conns.get(key)
            if conn is not None and conn._active_rid:
                continue
            await self._drop(key)
        return len(stale)

    def stats(self) -> Dict[str, Any]:
        return {
            "connections": len(self._conns),
            "active": sum(1 for c in self._conns.values() if c.connected),
            "turns": sum(c.turns for c in self._conns.values()),
        }


async def probe_model(
    settings: Settings,
    model: str,
    *,
    prompt: str = "Reply with the single word: OK",
    timeout: float = 35.0,
) -> Tuple[bool, str, float]:
    conn = PlaygroundConnection(settings, model=model, system="", temperature=1.0, label=f"probe:{model}")
    started = time.monotonic()
    try:
        await asyncio.wait_for(conn.connect(), timeout=25)
        messages = [P.user_message(prompt)]
        turn = await asyncio.wait_for(
            conn.stream_turn(messages, None, step_timeout=timeout),
            timeout=timeout + 5,
        )
        elapsed = time.monotonic() - started
        if turn.text:
            return True, turn.text[:60].replace("\n", " "), elapsed
        return False, "لا يوجد نص في الاستجابة", elapsed
    except BackendError as exc:
        return False, f"{exc.message}{' — ' + exc.detail if exc.detail else ''}"[:160], time.monotonic() - started
    except asyncio.TimeoutError:
        return False, "انتهت المهلة", time.monotonic() - started
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"[:160], time.monotonic() - started
    finally:
        try:
            await conn.close()
        except Exception:
            pass
