# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence
from . import memory as M
from . import models as MODELS
from . import protocol as P
from .backend import (
    ConnectionPool,
    PlaygroundConnection,
    StreamEvent,
    ToolCall,
    TurnResult,
    Usage,
)
from .config import Settings
from .errors import (
    BackendError,
    BotError,
    Cancelled,
    ConnectionLost,
    ModelGatedError,
    RateLimitedError,
    StreamTimeout,
)
from .store import Session, Store
from .tools import ToolContext, ToolRegistry, truncate
log = logging.getLogger("mh3.agent")
EventFn = Optional[Callable[[StreamEvent], Awaitable[None]]]
BOT_NAME_DEFAULT = "3mh agent"


@dataclass
class ToolTrace:
    name: str
    args: Dict[str, Any]
    ok: bool
    ms: float
    output_preview: str
    error: str = ""


@dataclass
class AgentResult:
    text: str = ""
    reasoning: str = ""
    model: str = ""
    steps: int = 0
    usage: Usage = field(default_factory=Usage)
    elapsed: float = 0.0
    tools: List[ToolTrace] = field(default_factory=list)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    error: str = ""
    cancelled: bool = False
    compacted: bool = False
    notes: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.error and not self.cancelled

    def stats_line(self) -> str:
        bits = [f"النموذج: {self.model.split('/')[-1]}", f"الخطوات: {self.steps}"]
        if self.tools:
            ok = sum(1 for t in self.tools if t.ok)
            bits.append(f"الأدوات: {ok}/{len(self.tools)}")
        if self.usage.total_tokens:
            bits.append(f"التوكنز: {self.usage.total_tokens}")
        if self.usage.cost_usd:
            bits.append(f"التكلفة: ${self.usage.cost_usd:.5f}")
        bits.append(f"الزمن: {self.elapsed:.1f}ث")
        return " • ".join(bits)


class AgentCore:

    def __init__(
        self,
        settings: Settings,
        store: Store,
        registry: ToolRegistry,
        pool: ConnectionPool,
        *,
        bot_name: str = BOT_NAME_DEFAULT,
    ) -> None:
        self.settings = settings
        self.store = store
        self.registry = registry
        self.pool = pool
        self.bot_name = bot_name or BOT_NAME_DEFAULT
        self._locks: Dict[int, asyncio.Lock] = {}
        self._cancels: Dict[int, asyncio.Event] = {}
        self._busy: Dict[int, bool] = {}

    def lock_for(self, chat_id: int) -> asyncio.Lock:
        lock = self._locks.get(chat_id)
        if lock is None:
            lock = self._locks[chat_id] = asyncio.Lock()
        return lock

    def is_busy(self, chat_id: int) -> bool:
        return bool(self._busy.get(chat_id))

    def cancel_event(self, chat_id: int) -> asyncio.Event:
        ev = self._cancels.get(chat_id)
        if ev is None:
            ev = self._cancels[chat_id] = asyncio.Event()
        return ev

    def request_cancel(self, chat_id: int) -> bool:
        if not self.is_busy(chat_id):
            return False
        self.cancel_event(chat_id).set()
        return True

    async def run(
        self,
        *,
        chat_id: int,
        user_id: int = 0,
        username: str = "",
        user_name: str = "",
        is_admin: bool = False,
        chat_type: str = "private",
        text: str = "",
        files: Optional[Sequence[Dict[str, Any]]] = None,
        on_event: EventFn = None,
        session: Optional[Session] = None,
        regenerate: bool = False,
        injected_note: str = "",
        send_file: Optional[Callable[..., Awaitable[None]]] = None,
        schedule_reminder: Optional[Callable[..., Awaitable[None]]] = None,
    ) -> AgentResult:
        started = time.monotonic()
        result = AgentResult()
        cancel_event = self.cancel_event(chat_id)
        cancel_event.clear()
        self._busy[chat_id] = True

        async def emit(kind: str, txt: str = "", **data: Any) -> None:
            if on_event is None:
                return
            try:
                await on_event(StreamEvent(kind=kind, text=txt, data=data))
            except Exception:
                log.exception("فشل معالج أحداث الوكيل")
        try:
            sess = session or await self.store.load_session(
                chat_id, defaults={"model": self.settings.default_model,
                                   "temperature": self.settings.temperature})
            if not sess.model:
                sess.model = self.settings.default_model
            result.model = sess.model
            workspace = self.settings.workspace_dir / str(chat_id)
            workspace.mkdir(parents=True, exist_ok=True)
            specs = self.registry.enabled(admin=is_admin)
            client_tools = [s.schema() for s in specs]
            ctx = ToolContext(
                chat_id=chat_id, user_id=user_id, username=username, is_admin=is_admin,
                settings=self.settings, store=self.store, workspace=workspace,
                language=self.settings.ui_language, cancel_event=cancel_event,
                emit=lambda msg: emit("notice", str(msg)),
                ask_model=self._make_ask_model(chat_id, emit),
                send_file=send_file,
                schedule_reminder=schedule_reminder,
                extra={"registry": self.registry, "session": sess},
            )
            _3mh_notes = ""
            try:
                notes = await self.store.search_notes(chat_id, "", limit=5)
                if notes:
                    _3mh_notes = "\n".join(
                        f"- [{n['title'] or 'بدون عنوان'}] {truncate(n['body'], 400)}" for n in notes)
            except Exception:
                pass
            file_count = sum(1 for _ in workspace.rglob("*") if _.is_file())
            _3mh_ctx = M.PromptContext(
                user_name=user_name or username or str(user_id),
                user_id=user_id, chat_id=chat_id, chat_type=chat_type,
                is_admin=is_admin, model=sess.model,
                tools_summary=M.tools_summary_lines(specs),
                workspace_files=file_count, summary=sess.summary,
                pinned_notes=_3mh_notes, language=self.settings.ui_language,
                bot_name=self.bot_name,
                extra=injected_note,
            )
            system_prompt = self.settings.system_prompt or M.build_system_prompt(_3mh_ctx)
            history = M.drop_orphan_tool_results(list(sess.messages or []))
            if not regenerate:
                user_parts: List[Dict[str, Any]] = list(files or [])
                if text:
                    user_parts.append(P.text_part(text))
                if not user_parts:
                    user_parts = [P.text_part("")]
                history.append({"role": "user", "parts": user_parts,
                                "id": P.new_message_id("msg")})
            else:
                while history and history[-1].get("role") == "assistant":
                    history.pop()
                if not history:
                    history.append(P.user_message(text or "أكمل المهمة السابقة."))
            budget = max(2000, int(self.settings.max_context_tokens))
            history = M.trim_messages(history, budget - estimate_system(system_prompt) - 1500)
            messages = history
            _3mh_chain = self._model_chain(sess.model)
            step = 0
            _3mh_seen: Dict[str, int] = {}
            total_usage = Usage()
            final_text = ""
            final_reasoning = ""
            deadline = time.monotonic() + min(self.settings.step_timeout * max(self.settings.max_steps, 1), 900)
            while step < self.settings.max_steps:
                if cancel_event.is_set():
                    raise Cancelled("أُلغي الطلب")
                if time.monotonic() > deadline:
                    result.notes.append("انتهت ميزانية الوقت الكلية — أُوقفت الحلقة")
                    break
                step += 1
                await emit("turn", "", step=step, max_steps=self.settings.max_steps)
                turn = await self._stream_step(
                    chat_id=chat_id,
                    messages=messages,
                    client_tools=client_tools,
                    _3mh_chain=_3mh_chain,
                    on_event=on_event,
                    cancel_event=cancel_event,
                    emit=emit,
                    step=step,
                    system_prompt=system_prompt,
                    temperature=float(sess.temperature),
                )
                active = self.pool.peek(chat_id)
                if active is not None:
                    result.model = active.url_model
                total_usage = total_usage.merge(turn.usage)
                result.steps = step
                if turn.text:
                    final_text = turn.text
                if turn.reasoning:
                    final_reasoning = turn.reasoning
                result.sources.extend(turn.sources)
                asst_parts: List[Dict[str, Any]] = []
                if turn.reasoning:
                    asst_parts.append(P.reasoning_part(turn.reasoning))
                if turn.text:
                    asst_parts.append(P.text_part(turn.text))
                for tc in turn.tool_calls:
                    asst_parts.append(P.tool_part(tc.tool_name, tc.tool_call_id, tc.input,
                                                  tc.server_output, state="input-available"))
                messages.append(P.assistant_message(asst_parts, message_id=turn.message_id or None))
                if not turn.tool_calls:
                    break
                blocked: List[ToolCall] = []
                runnable: List[ToolCall] = []
                for tc in turn.tool_calls:
                    _3mh_seen[tc.signature] = _3mh_seen.get(tc.signature, 0) + 1
                    if _3mh_seen[tc.signature] > 3:
                        blocked.append(tc)
                    else:
                        runnable.append(tc)
                if blocked and not runnable:
                    result.notes.append(
                        "أُوقفت الحلقة: تكرار نفس استدعاء الأداة أكثر من 3 مرات")
                    await emit("status", "", status="loop-stopped")
                    break
                outputs = await self._execute_tools(runnable + blocked, ctx, emit, blocked_ids={
                    tc.tool_call_id for tc in blocked})
                last_assistant = messages[-1]
                new_parts: List[Dict[str, Any]] = []
                for part in last_assistant.get("parts", []):
                    if isinstance(part, dict) and str(part.get("type", "")).startswith("tool-"):
                        tcid = part.get("toolCallId")
                        info = outputs.get(tcid)
                        if info is not None:
                            new_parts.append(P.tool_part(
                                info["name"], tcid, info["input"], info["output"],
                                state="output-available" if info["ok"] else "output-error",
                                error_text=None if info["ok"] else info["error"]))
                            continue
                    new_parts.append(part)
                last_assistant["parts"] = new_parts
                active_conn = self.pool.peek(chat_id)
                if active_conn is not None:
                    for tcid, info in outputs.items():
                        try:
                            await active_conn.send_tool_result(
                                tcid, info["name"], info["output"],
                                client_tools=client_tools, ok=info["ok"],
                                error_text=None if info["ok"] else info["error"],
                                auto_continue=False)
                        except ConnectionLost:
                            log.warning("انقطع الاتصال أثناء إرسال نتيجة أداة")
                        except Exception:
                            log.exception("فشل إرسال نتيجة أداة")
                for tcid, info in outputs.items():
                    result.tools.append(ToolTrace(
                        name=info["name"], args=info["input"], ok=info["ok"],
                        ms=info["ms"], output_preview=truncate(
                            info["output"] if isinstance(info["output"], str)
                            else json.dumps(info["output"], ensure_ascii=False, default=str), 400),
                        error=info["error"]))
            else:
                result.notes.append(f"بلغ الحد الأقصى للخطوات ({self.settings.max_steps})")
            result.text = final_text or (
                "" if result.tools else "(لم يُرجع النموذج نصاً)")
            result.reasoning = final_reasoning
            result.usage = total_usage
            result.elapsed = time.monotonic() - started
            result.artifacts = list(ctx.artifacts)
            sess.messages = M.drop_orphan_tool_results(messages)[-40:]
            sess.model = result.model or sess.model
            sess.steps_total += result.steps
            sess.updated_at = time.time()
            if not sess.title and text:
                sess.title = text.strip().splitlines()[0][:60]
            await self.store.save_session(sess)
            try:
                await self.store.log_usage(
                    chat_id, result.model, total_usage.to_dict(),
                    steps=result.steps, tool_calls=len(result.tools), ok=True)
            except Exception:
                log.exception("فشل تسجيل الاستخدام")
            if self.settings.compact_ratio > 0:
                budget_tokens = max(2000, int(self.settings.max_context_tokens))
                if M.estimate_messages(sess.messages) > budget_tokens * self.settings.compact_ratio:
                    await emit("status", "", status="compacting")
                    keep = 6
                    old = sess.messages[:-keep] if len(sess.messages) > keep else []
                    if old:
                        summary = await M.compact_history(
                            old, summarize=self._make_summarizer(chat_id),
                            previous_summary=sess.summary)
                        if summary:
                            sess.summary = summary
                            sess.messages = sess.messages[-keep:]
                            await self.store.save_session(sess)
                            result.compacted = True
                            result.notes.append("تم ضغط ذاكرة المحادثة تلقائياً")
            return result
        except Cancelled:
            result.cancelled = True
            result.text = result.text or ""
            result.elapsed = time.monotonic() - started
            await emit("status", "", status="cancelled")
            return result
        except BotError as exc:
            result.error = f"{exc.message}{' — ' + exc.detail if getattr(exc, 'detail', None) else ''}"
            result.elapsed = time.monotonic() - started
            await emit("error", result.error, error_type=type(exc).__name__)
            try:
                await self.store.log_usage(chat_id, result.model, {}, steps=result.steps,
                                           tool_calls=len(result.tools), ok=False,
                                           note=result.error[:200])
            except Exception:
                pass
            return result
        except Exception as exc:
            log.exception("خطأ غير متوقع في نواة الوكيل")
            result.error = f"{type(exc).__name__}: {exc}"
            result.elapsed = time.monotonic() - started
            await emit("error", result.error)
            return result
        finally:
            self._busy[chat_id] = False
            cancel_event.clear()

    async def _stream_step(
        self,
        *,
        chat_id: int,
        messages: Sequence[Dict[str, Any]],
        client_tools: Sequence[Dict[str, Any]],
        _3mh_chain: Sequence[str],
        on_event: EventFn,
        cancel_event: asyncio.Event,
        emit: Callable[..., Awaitable[None]],
        step: int,
        system_prompt: str,
        temperature: float,
    ) -> TurnResult:
        last_error: Optional[BotError] = None
        for index, model in enumerate(_3mh_chain):
            attempts = 2 if index == 0 else 1
            switch_to_next = False
            for attempt in range(attempts):
                if cancel_event.is_set():
                    raise Cancelled("أُلغي الطلب")
                try:
                    conn = await self.pool.get(
                        chat_id, model=model, system=system_prompt, temperature=temperature)
                    return await conn.stream_turn(
                        messages, client_tools,
                        on_event=on_event, cancel_event=cancel_event,
                        step_timeout=self.settings.step_timeout,
                        include_reasoning=self.settings.show_reasoning,
                    )
                except Cancelled:
                    raise
                except (RateLimitedError, ModelGatedError, StreamTimeout, ConnectionLost) as exc:
                    last_error = exc
                    await self.pool.close(chat_id)
                    if attempt + 1 < attempts and not isinstance(exc, ModelGatedError):
                        wait = 6.0 * (attempt + 1) if isinstance(exc, RateLimitedError) else 2.0 * (attempt + 1)
                        await emit("status", "", status="retrying", model=model,
                                   error=exc.message, wait=wait, attempt=attempt + 1)
                        await asyncio.sleep(wait)
                        continue
                    if index + 1 < len(_3mh_chain):
                        await emit("status", "", status="fallback", model=model,
                                   next_model=_3mh_chain[index + 1], error=exc.message)
                        switch_to_next = True
                        break
                    raise
                except BackendError as exc:
                    last_error = exc
                    await self.pool.close(chat_id)
                    if exc.try_fallback and index + 1 < len(_3mh_chain):
                        await emit("status", "", status="fallback", model=model,
                                   next_model=_3mh_chain[index + 1], error=exc.message)
                        switch_to_next = True
                        break
                    raise
            if not switch_to_next:
                continue
        if last_error:
            raise last_error
        raise BackendError("تعذّر إكمال الخطوة")

    def _model_chain(self, primary: str) -> List[str]:
        chain = [primary]
        for model in self.settings.fallback_models:
            if model and model not in chain:
                chain.append(model)
        return chain

    async def _execute_tools(
        self,
        calls: Sequence[ToolCall],
        ctx: ToolContext,
        emit: Callable[..., Awaitable[None]],
        blocked_ids: Optional[set] = None,
    ) -> Dict[str, Dict[str, Any]]:
        blocked_ids = blocked_ids or set()
        outputs: Dict[str, Dict[str, Any]] = {}
        if not calls:
            return outputs
        semaphore = asyncio.Semaphore(4)

        async def runner(tc: ToolCall) -> None:
            async with semaphore:
                if tc.tool_call_id in blocked_ids:
                    outputs[tc.tool_call_id] = {
                        "name": tc.tool_name, "input": tc.input, "ok": False, "ms": 0.0,
                        "output": {"error": "blocked: repeated identical call"},
                        "error": "تم حظر الاستدعاء المتكرر — غيّر الاستراتيجية أو أعطِ الإجابة النهائية",
                    }
                    await emit("tool_result", "", tool_name=tc.tool_name, ok=False,
                               blocked=True, ms=0)
                    return
                if tc.error and not tc.input:
                    outputs[tc.tool_call_id] = {
                        "name": tc.tool_name, "input": {}, "ok": False, "ms": 0.0,
                        "output": {"error": tc.error}, "error": tc.error}
                    await emit("tool_result", "", tool_name=tc.tool_name, ok=False, ms=0)
                    return
                await emit("tool_start", "", tool_name=tc.tool_name, args=tc.input)
                res = await self.registry.execute(tc.tool_name, tc.input, ctx)
                outputs[tc.tool_call_id] = {
                    "name": tc.tool_name, "input": tc.input, "ok": res.ok,
                    "ms": res.ms, "output": res.payload, "error": res.error,
                }
                if res.artifacts:
                    ctx.artifacts.extend(res.artifacts)
                await emit("tool_result", "", tool_name=tc.tool_name, ok=res.ok,
                           ms=round(res.ms), error=res.error,
                           preview=truncate(
                               res.output if isinstance(res.output, str)
                               else json.dumps(res.output, ensure_ascii=False, default=str), 300))
        await asyncio.gather(*(runner(tc) for tc in calls), return_exceptions=True)
        return outputs

    def _make_ask_model(self, chat_id: int, emit: Callable[..., Awaitable[None]]):

        async def ask_model(*, prompt: str, model: str = "", system: str = "",
                            temperature: Optional[float] = None) -> tuple:
            info = MODELS.resolve_model(model) if model else None
            chosen = info.id if info else (model or self.settings.utility_model)
            key = f"sub:{chat_id}:{chosen}"
            await emit("status", "", status="subagent", model=chosen)
            conn = await self.pool.get(key, model=chosen)
            await conn.set_state(model=chosen, system=system or "", temperature=temperature)
            messages = [P.user_message(prompt)]
            turn = await conn.stream_turn(messages, None, step_timeout=self.settings.step_timeout)
            return turn.text or "(لا يوجد نص)", chosen
        return ask_model

    def _make_summarizer(self, chat_id: int) -> M.SummarizeFn:

        async def summarize(prompt: str, system: str) -> str:
            answer, _ = await self._make_ask_model(chat_id, _noop_emit)(
                prompt=prompt, model=self.settings.utility_model, system=system, temperature=0.3)
            return answer
        return summarize


async def _noop_emit(*args: Any, **kwargs: Any) -> None:
    return None


def estimate_system(text: str) -> int:
    return M.estimate_tokens(text or "")
