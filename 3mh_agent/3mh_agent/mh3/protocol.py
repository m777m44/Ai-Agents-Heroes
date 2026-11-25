# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import json
import random
import secrets
import uuid
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import quote
__all__ = [
    "Frame",
    "Chunk",
    "Trigger",
    "NANOID_ALPHABET",
    "nanoid",
    "new_agent_name",
    "new_pk",
    "new_request_id",
    "new_message_id",
    "build_ws_url",
    "state_frame",
    "mcp_frame",
    "identity_frame",
    "chat_request_frame",
    "tool_result_frame",
    "tool_approval_frame",
    "cancel_frame",
    "chat_messages_frame",
    "text_part",
    "reasoning_part",
    "file_part",
    "tool_part",
    "user_message",
    "assistant_message",
    "client_tool_schema",
    "flatten_text",
]


class Frame:
    IDENTITY = "cf_agent_identity"
    STATE = "cf_agent_state"
    STATE_ERROR = "cf_agent_state_error"
    MCP_SERVERS = "cf_agent_mcp_servers"
    USE_CHAT_REQUEST = "cf_agent_use_chat_request"
    USE_CHAT_RESPONSE = "cf_agent_use_chat_response"
    CHAT_MESSAGES = "cf_agent_chat_messages"
    MESSAGE_UPDATED = "cf_agent_message_updated"
    CHAT_CLEAR = "cf_agent_chat_clear"
    CHAT_REQUEST_CANCEL = "cf_agent_chat_request_cancel"
    CHAT_RECOVERING = "cf_agent_chat_recovering"
    STREAM_RESUMING = "cf_agent_stream_resuming"
    STREAM_RESUME_ACK = "cf_agent_stream_resume_ack"
    STREAM_RESUME_REQUEST = "cf_agent_stream_resume_request"
    STREAM_RESUME_NONE = "cf_agent_stream_resume_none"
    TOOL_RESULT = "cf_agent_tool_result"
    TOOL_APPROVAL = "cf_agent_tool_approval"
    RPC = "rpc"


class Chunk:
    START = "start"
    START_STEP = "start-step"
    TEXT_START = "text-start"
    TEXT_DELTA = "text-delta"
    TEXT_END = "text-end"
    REASONING_START = "reasoning-start"
    REASONING_DELTA = "reasoning-delta"
    REASONING_END = "reasoning-end"
    TOOL_INPUT_START = "tool-input-start"
    TOOL_INPUT_DELTA = "tool-input-delta"
    TOOL_INPUT_AVAILABLE = "tool-input-available"
    TOOL_INPUT_ERROR = "tool-input-error"
    TOOL_OUTPUT_AVAILABLE = "tool-output-available"
    TOOL_OUTPUT_ERROR = "tool-output-error"
    TOOL_OUTPUT_DENIED = "tool-output-denied"
    TOOL_APPROVAL_REQUEST = "tool-approval-request"
    TOOL_APPROVAL_RESPONSE = "tool-approval-response"
    FILE = "file"
    SOURCE_URL = "source-url"
    SOURCE_DOCUMENT = "source-document"
    FINISH_STEP = "finish-step"
    FINISH = "finish"
    ERROR = "error"
    ABORT = "abort"


class Trigger:
    SUBMIT = "submit-message"
    REGENERATE = "regenerate-message"
    RESUME = "resume-stream"
NANOID_ALPHABET = "useandom-26T198340PX75pxJACKVERYMINDBUSHWOLF_GQZbfghjklqvwyzrict"


def nanoid(size: int = 8) -> str:
    return "".join(secrets.choice(NANOID_ALPHABET) for _ in range(size))


def new_agent_name() -> str:
    return "playground-" + "".join(random.choices("0123456789abcdefghijklmnopqrstuvwxyz", k=13))


def new_pk() -> str:
    return str(uuid.uuid4())


def new_request_id() -> str:
    return nanoid(8)


def new_message_id(prefix: str = "msg") -> str:
    return f"{prefix}_{secrets.token_hex(6)}"


def build_ws_url(base_url: str, agent_name: str, pk: str, model: str) -> str:
    return (
        f"{base_url.rstrip('/')}/agents/playground/{agent_name}"
        f"?_pk={pk}&model={quote(model, safe='')}"
    )


def state_frame(
    model: str,
    system: str = "",
    temperature: float = 1.0,
    stream: bool = True,
    *,
    web_search: bool = False,
    web_search_provider: str = "ceramic",
    generative_ui_mode: str = "off",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    state: Dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "stream": stream,
        "system": system or "",
        "useExternalProvider": False,
        "externalProvider": "openai",
        "webSearchEnabled": bool(web_search),
        "webSearchProvider": web_search_provider,
        "generativeUIMode": generative_ui_mode,
        "generativeUI": False,
    }
    if extra:
        state.update(extra)
    return {"state": state, "type": Frame.STATE}


def mcp_frame(
    prompts: Optional[Sequence[Any]] = None,
    resources: Optional[Sequence[Any]] = None,
    servers: Optional[Dict[str, Any]] = None,
    tools: Optional[Sequence[Any]] = None,
) -> Dict[str, Any]:
    return {
        "mcp": {
            "prompts": list(prompts or []),
            "resources": list(resources or []),
            "servers": dict(servers or {}),
            "tools": list(tools or []),
        },
        "type": Frame.MCP_SERVERS,
    }


def identity_frame(agent_name: str, agent: str = "playground") -> Dict[str, Any]:
    return {"name": agent_name, "agent": agent, "type": Frame.IDENTITY}


def chat_request_frame(
    request_id: str,
    messages: Sequence[Dict[str, Any]],
    *,
    trigger: str = Trigger.SUBMIT,
    client_tools: Optional[Sequence[Dict[str, Any]]] = None,
    message_id: Optional[str] = None,
    extra_body: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "messages": list(messages),
        "trigger": trigger,
    }
    if client_tools:
        body["clientTools"] = list(client_tools)
    if message_id:
        body["messageId"] = message_id
    if extra_body:
        body.update(extra_body)
    return {
        "id": request_id,
        "init": {"method": "POST", "body": json.dumps(body, ensure_ascii=False)},
        "type": Frame.USE_CHAT_REQUEST,
    }


def tool_result_frame(
    tool_call_id: str,
    tool_name: str,
    output: Any,
    *,
    auto_continue: bool = False,
    client_tools: Optional[Sequence[Dict[str, Any]]] = None,
    state: Optional[str] = None,
    error_text: Optional[str] = None,
) -> Dict[str, Any]:
    frame: Dict[str, Any] = {
        "type": Frame.TOOL_RESULT,
        "toolCallId": tool_call_id,
        "toolName": tool_name,
        "output": output,
        "autoContinue": auto_continue,
    }
    if client_tools:
        frame["clientTools"] = list(client_tools)
    if state:
        frame["state"] = state
    if error_text is not None:
        frame["errorText"] = error_text
    return frame


def tool_approval_frame(tool_call_id: str, approved: bool, auto_continue: bool = False) -> Dict[str, Any]:
    return {
        "type": Frame.TOOL_APPROVAL,
        "toolCallId": tool_call_id,
        "approved": bool(approved),
        "autoContinue": auto_continue,
    }


def cancel_frame(request_id: str) -> Dict[str, Any]:
    return {"id": request_id, "type": Frame.CHAT_REQUEST_CANCEL}


def chat_messages_frame(messages: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {"messages": list(messages), "type": Frame.CHAT_MESSAGES}


def text_part(text: str) -> Dict[str, Any]:
    return {"type": "text", "text": text}


def reasoning_part(text: str, state: str = "done") -> Dict[str, Any]:
    return {"type": "reasoning", "text": text, "state": state}


def file_part(media_type: str, data_url: str, filename: Optional[str] = None) -> Dict[str, Any]:
    part: Dict[str, Any] = {"type": "file", "mediaType": media_type, "url": data_url}
    if filename:
        part["filename"] = filename
    return part


def tool_part(
    tool_name: str,
    tool_call_id: str,
    tool_input: Any,
    output: Any,
    *,
    state: str = "output-available",
    error_text: Optional[str] = None,
) -> Dict[str, Any]:
    part: Dict[str, Any] = {
        "type": f"tool-{tool_name}",
        "toolCallId": tool_call_id,
        "state": state,
        "input": tool_input,
    }
    if state == "output-error":
        part["errorText"] = error_text or "tool error"
    else:
        part["output"] = output
    return part


def user_message(text: str, *, message_id: Optional[str] = None,
                 files: Optional[Sequence[Dict[str, Any]]] = None) -> Dict[str, Any]:
    parts: List[Dict[str, Any]] = list(files or [])
    if text:
        parts.append(text_part(text))
    return {
        "role": "user",
        "parts": parts or [text_part("")],
        "id": message_id or new_message_id("msg"),
    }


def assistant_message(parts: Sequence[Dict[str, Any]], *, message_id: Optional[str] = None) -> Dict[str, Any]:
    return {
        "role": "assistant",
        "parts": list(parts),
        "id": message_id or new_message_id("assistant"),
    }


def client_tool_schema(name: str, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    return {"name": name, "description": description, "parameters": parameters}


def flatten_text(message: Dict[str, Any]) -> str:
    parts = message.get("parts")
    if isinstance(parts, list):
        return "".join(p.get("text", "") for p in parts if isinstance(p, dict) and p.get("type") == "text")
    content = message.get("content")
    if isinstance(content, list):
        return "".join(p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text")
    return str(content or "")


def is_tool_part(part: Any) -> bool:
    if not isinstance(part, dict):
        return False
    ptype = part.get("type", "")
    return isinstance(ptype, str) and (ptype.startswith("tool-") or ptype == "dynamic-tool")


def tool_name_of(part: Dict[str, Any]) -> str:
    if part.get("type") == "dynamic-tool":
        return str(part.get("toolName", ""))
    return "-".join(str(part.get("type", "")).split("-")[1:])


def dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)
