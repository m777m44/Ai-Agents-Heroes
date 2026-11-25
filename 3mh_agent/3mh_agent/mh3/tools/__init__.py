# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import asyncio
import inspect
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence
from ..config import Settings
log = logging.getLogger("mh3.tools")
__all__ = [
    "ToolSpec", "ToolResult", "ToolContext", "ToolRegistry", "tool",
    "truncate", "safe_json", "json_schema", "build_registry",
]


def truncate(text: Any, limit: int = 8000, note: str = "…[اقتُطع]") -> str:
    s = text if isinstance(text, str) else safe_json(text)
    if len(s) <= limit:
        return s
    keep = max(200, limit - len(note) - 2)
    head = s[: keep // 2]
    tail = s[-keep // 2 :]
    removed = len(s) - len(head) - len(tail)
    return f"{head}\n{note} حُذف {removed} حرفاً من المنتصف {note}\n{tail}"


def safe_json(obj: Any, limit: Optional[int] = None) -> str:
    try:
        text = json.dumps(obj, ensure_ascii=False, indent=None, default=str)
    except Exception:
        text = str(obj)
    return truncate(text, limit) if limit else text


def json_schema(**properties: Any) -> Dict[str, Any]:
    required = []
    for name, spec in properties.items():
        if isinstance(spec, dict) and spec.get("required"):
            required.append(name)
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


@dataclass
class ToolResult:
    ok: bool = True
    output: Any = None
    error: str = ""
    ms: float = 0.0
    artifacts: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def payload(self) -> Any:
        if self.ok:
            return self.output
        return {"error": self.error or "tool failed"}


@dataclass
class ToolContext:
    chat_id: int = 0
    user_id: int = 0
    username: str = ""
    is_admin: bool = False
    settings: Optional[Settings] = None
    store: Any = None
    workspace: Path = Path("./workspace")
    language: str = "ar"
    cancel_event: Optional[asyncio.Event] = None
    emit: Optional[Callable[..., Awaitable[None]]] = None
    ask_model: Optional[Callable[..., Awaitable[str]]] = None
    send_file: Optional[Callable[..., Awaitable[None]]] = None
    schedule_reminder: Optional[Callable[..., Awaitable[None]]] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)

    def resolve_path(self, raw: str, *, must_exist: bool = False) -> Path:
        ws = self.workspace.resolve()
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            candidate = ws / candidate
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError):
            resolved = candidate.absolute()
        if resolved != ws and ws not in resolved.parents:
            raise PermissionError(f"المسار خارج مجلد العمل المعزول: {raw}")
        if must_exist and not resolved.exists():
            raise FileNotFoundError(f"غير موجود: {raw}")
        return resolved

    async def notify(self, text: str) -> None:
        if self.emit is not None:
            try:
                await self.emit(text)
            except Exception:
                pass


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[..., Awaitable[Any]]
    timeout: float = 45.0
    admin_only: bool = False
    category: str = "general"
    dangerous: bool = False
    needs_web: bool = False
    needs_code: bool = False
    max_output: int = 8000

    def schema(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description, "parameters": self.parameters}

    def line(self, *, enabled: bool = True) -> str:
        marks = []
        if self.admin_only:
            marks.append("🔐 مشرف")
        if self.dangerous:
            marks.append("⚠️")
        if self.needs_web:
            marks.append("🌐")
        if self.needs_code:
            marks.append("🐍")
        flag = "🟢" if enabled else "⚪"
        return f"{flag} `{self.name}` — {self.description.splitlines()[0]}" + (f" [{'، '.join(marks)}]" if marks else "")


class ToolRegistry:

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings
        self._tools: Dict[str, ToolSpec] = {}
        self._runtime_disabled: set = set()

    def register(self, spec: ToolSpec) -> ToolSpec:
        self._tools[spec.name] = spec
        return spec

    def tool(self, **kwargs: Any):

        def deco(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            spec = ToolSpec(
                name=kwargs.get("name", fn.__name__),
                description=kwargs.get("description") or (inspect.getdoc(fn) or fn.__name__),
                parameters=kwargs.get("parameters") or {"type": "object", "properties": {}},
                handler=fn,
                timeout=float(kwargs.get("timeout", 45.0)),
                admin_only=bool(kwargs.get("admin_only", False)),
                category=kwargs.get("category", "general"),
                dangerous=bool(kwargs.get("dangerous", False)),
                needs_web=bool(kwargs.get("needs_web", False)),
                needs_code=bool(kwargs.get("needs_code", False)),
                max_output=int(kwargs.get("max_output", 8000)),
            )
            self.register(spec)
            return fn
        return deco

    def get(self, name: str) -> Optional[ToolSpec]:
        return self._tools.get(name)

    @property
    def all(self) -> List[ToolSpec]:
        return list(self._tools.values())

    def is_enabled(self, name: str) -> bool:
        spec = self._tools.get(name)
        if spec is None:
            return False
        if name in self._runtime_disabled:
            return False
        s = self.settings
        if s is None:
            return True
        if name in {t.lower() for t in s.disabled_tools}:
            return False
        if s.enabled_tools_only and name not in {t.lower() for t in s.enabled_tools_only}:
            return False
        if spec.needs_web and not s.enable_web_tools:
            return False
        if spec.needs_code:
            if spec.name == "python_exec" and not s.enable_python:
                return False
            if spec.name == "shell_exec" and not s.enable_shell:
                return False
        return True

    def enabled(self, *, admin: bool = True) -> List[ToolSpec]:
        return [
            spec for name, spec in self._tools.items()
            if self.is_enabled(name) and (admin or not spec.admin_only)
        ]

    def categories(self) -> Dict[str, List[ToolSpec]]:
        out: Dict[str, List[ToolSpec]] = {}
        for spec in self._tools.values():
            out.setdefault(spec.category, []).append(spec)
        for group in out.values():
            group.sort(key=lambda s: s.name)
        return dict(sorted(out.items()))

    def client_tools(self, *, admin: bool = True) -> List[Dict[str, Any]]:
        return [spec.schema() for spec in self.enabled(admin=admin)]

    def set_runtime_enabled(self, name: str, enabled: bool) -> bool:
        if name not in self._tools:
            return False
        if enabled:
            self._runtime_disabled.discard(name)
        else:
            self._runtime_disabled.add(name)
        return True

    async def execute(self, name: str, args: Any, ctx: ToolContext) -> ToolResult:
        spec = self._tools.get(name)
        if spec is None:
            return ToolResult(ok=False, error=f"أداة غير معروفة: {name}", output={"error": f"unknown tool: {name}"})
        if not self.is_enabled(name):
            return ToolResult(ok=False, error=f"الأداة معطّلة: {name}", output={"error": f"tool disabled: {name}"})
        if spec.admin_only and not ctx.is_admin:
            return ToolResult(ok=False, error="هذه الأداة للمشرفين فقط",
                              output={"error": "admin-only tool"})
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except (ValueError, TypeError):
                args = {"input": args}
        if not isinstance(args, dict):
            args = {"value": args}
        timeout = float(spec.timeout or 45.0)
        if ctx.settings is not None:
            timeout = min(max(timeout, 5.0), max(ctx.settings.tool_timeout, 10.0) * 4)
        started = time.monotonic()
        try:
            coro = spec.handler(args, ctx)
            raw = await asyncio.wait_for(coro, timeout=timeout)
            ok, output, error, artifacts = _normalize(raw, spec.max_output)
        except asyncio.TimeoutError:
            ok, output, error, artifacts = False, None, f"انتهت مهلة الأداة ({timeout:.0f} ثانية)", []
        except asyncio.CancelledError:
            raise
        except PermissionError as exc:
            ok, output, error, artifacts = False, None, f"مرفوض: {exc}", []
        except Exception as exc:
            log.exception("فشل تنفيذ الأداة %s", name)
            ok, output, error, artifacts = False, None, f"{type(exc).__name__}: {exc}"[:600], []
        ms = (time.monotonic() - started) * 1000
        result = ToolResult(ok=ok, output=output, error=error, ms=ms, artifacts=artifacts)
        if ctx.store is not None:
            try:
                await ctx.store.log_tool(ctx.chat_id, name, args, ok, ms, safe_json(output)[:300])
            except Exception:
                pass
        return result


def _normalize(raw: Any, max_output: int) -> tuple:
    if isinstance(raw, ToolResult):
        out = raw.output
        if isinstance(out, str):
            out = truncate(out, max_output)
        return raw.ok, out, raw.error, raw.artifacts
    if isinstance(raw, tuple) and len(raw) == 2 and isinstance(raw[0], bool):
        ok, payload = raw
        if isinstance(payload, str):
            payload = truncate(payload, max_output)
        return ok, payload, ("" if ok else str(payload)[:300]), []
    if isinstance(raw, str):
        return True, truncate(raw, max_output), "", []
    if raw is None:
        return True, {"status": "ok"}, "", []
    if isinstance(raw, (dict, list, int, float, bool)):
        try:
            text = json.dumps(raw, ensure_ascii=False, default=str)
        except Exception:
            text = str(raw)
        if len(text) > max_output:
            return True, {"truncated": truncate(text, max_output)}, "", []
        return True, raw, "", []
    return True, truncate(str(raw), max_output), "", []


def tool(registry: ToolRegistry, **kwargs: Any):
    return registry.tool(**kwargs)


def build_registry(settings: Optional[Settings] = None) -> ToolRegistry:
    registry = ToolRegistry(settings)
    from . import core as _core
    from . import web as _web
    from . import files as _files
    from . import code as _code
    from . import brain as _brain
    for module in (_core, _web, _files, _code, _brain):
        module.register(registry)
    return registry
