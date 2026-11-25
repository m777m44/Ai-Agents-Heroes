# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from telegram import InlineKeyboardMarkup, Message, Update
from telegram.constants import ChatAction, ParseMode
from telegram.error import BadRequest, RetryAfter, TelegramError, TimedOut
from telegram.ext import ContextTypes
from ..backend import StreamEvent, Usage
from ..config import Settings
from . import render
from .ui import tr
log = logging.getLogger("mh3.stream")
try:
    from telegram import LinkPreviewOptions
    _HAS_LPO = True
except Exception:
    LinkPreviewOptions = None
    _HAS_LPO = False


def _no_preview_kwargs() -> Dict[str, Any]:
    if _HAS_LPO:
        return {"link_preview_options": LinkPreviewOptions(is_disabled=True)}
    return {"disable_web_page_preview": True}


class StreamRenderer:

    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        settings: Settings,
        *,
        lang: str = "ar",
        model: str = "",
        show_reasoning: bool = False,
        show_trace: bool = True,
        show_usage: bool = True,
        stream: bool = True,
        max_steps: int = 10,
    ) -> None:
        self.update = update
        self.context = context
        self.settings = settings
        self.lang = lang
        self.model = model
        self.show_reasoning = show_reasoning
        self.show_trace = show_trace
        self.show_usage = show_usage
        self.stream = stream and settings.stream_edits
        self.max_steps = max_steps
        self.chat_id: int = update.effective_chat.id if update.effective_chat else 0
        self.message: Optional[Message] = update.effective_message
        self.reply_msg: Optional[Message] = None
        self._text_parts: List[str] = []
        self._reasoning_parts: List[str] = []
        self._trace: List[str] = []
        self._notices: List[str] = []
        self._status: str = ""
        self._step: int = 0
        self._server_steps: int = 0
        self._usage: Usage = Usage()
        self._tools_started: Dict[str, float] = {}
        self._tools_by_call: Dict[str, int] = {}
        self._started = time.monotonic()
        self._last_edit = 0.0
        self._3mh_flush: Optional[asyncio.Task] = None
        self._closed = False
        self._edits = 0
        self._3mh_broken = False
        self._3mh_typing = asyncio.Lock()

    async def start(self, initial_text: str = "") -> None:
        if not self.chat_id:
            return
        placeholder = initial_text or f"{tr.t('thinking', self.lang)}"
        try:
            await self._typing()
            self.reply_msg = await self._reply(placeholder)
        except TelegramError as exc:
            log.warning("تعذّر إرسال الرسالة المؤقتة: %s", exc)
        self._last_edit = time.monotonic()

    async def _reply(self, text: str, **kwargs: Any) -> Optional[Message]:
        params: Dict[str, Any] = dict(kwargs)
        chat = self.update.effective_chat
        msg = self.message
        in_group = chat is not None and chat.type in ("group", "supergroup")
        if in_group and msg is not None:
            try:
                from telegram import ReplyParameters
                params["reply_parameters"] = ReplyParameters(
                    message_id=msg.message_id, allow_sending_without_reply=True)
            except ImportError:
                params["reply_to_message_id"] = msg.message_id
                params["allow_sending_without_reply"] = True
        return await self.context.bot.send_message(chat_id=self.chat_id, text=text, **params)

    async def _typing(self) -> None:
        if self._3mh_typing.locked():
            return
        async with self._3mh_typing:
            try:
                await self.context.bot.send_chat_action(self.chat_id, ChatAction.TYPING)
            except TelegramError:
                pass

    async def on_event(self, ev: StreamEvent) -> None:
        if self._closed:
            return
        kind = ev.kind
        if kind == "text":
            if ev.text:
                self._text_parts.append(ev.text)
                self._schedule_edit()
            return
        if kind == "reasoning":
            if ev.text and self.show_reasoning:
                self._reasoning_parts.append(ev.text)
                self._schedule_edit()
            return
        if kind == "tool_call":
            name = str(ev.data.get("tool_name") or "?")
            call_id = str(ev.data.get("tool_call_id") or "")
            args = ev.data.get("input") or {}
            self._tools_started[name] = time.monotonic()
            line = f"🔧 `{name}` {_args_preview(args)}"
            if call_id:
                self._tools_by_call[call_id] = len(self._trace)
            self._trace.append(line)
            self._schedule_edit()
            return
        if kind == "tool_start":
            name = str(ev.data.get("tool_name") or "?")
            if self._trace and name in self._trace[-1]:
                return
            self._tools_started[name] = time.monotonic()
            self._trace.append(f"🔧 `{name}` {_args_preview(ev.data.get('args') or {})}")
            self._schedule_edit()
            return
        if kind == "tool_result":
            name = str(ev.data.get("tool_name") or "?")
            ok = bool(ev.data.get("ok"))
            ms = ev.data.get("ms") or 0
            blocked = bool(ev.data.get("blocked"))
            if ok:
                mark = "✅" if not blocked else "⛔"
            else:
                mark = "❌"
            preview = str(ev.data.get("preview") or ev.data.get("error") or "")
            line = f"{mark} `{name}` · {int(float(ms))}م.ث"
            if not ok and ev.data.get("error"):
                line += f" — {_one_line(str(ev.data['error']))[:120]}"
            elif preview and self.show_trace:
                line += f" — {_one_line(preview)[:110]}"
            self._trace.append(line)
            self._schedule_edit()
            return
        if kind == "status":
            status = str(ev.data.get("status") or "")
            if status == "fallback":
                self._notice(tr.t("fallback", self.lang,
                                  model=_short_model(ev.data.get("model")),
                                  next_model=_short_model(ev.data.get("next_model")),
                                  error=str(ev.data.get("error") or "")[:80]))
            elif status == "retrying":
                self._notice(tr.t("retrying", self.lang, wait=int(float(ev.data.get("wait") or 0)),
                                  error=str(ev.data.get("error") or "")[:80]))
            elif status == "subagent":
                self._notice(tr.t("subagent", self.lang, model=_short_model(ev.data.get("model"))))
            elif status == "compacting":
                self._notice(tr.t("compacting", self.lang))
            elif status == "loop-stopped":
                self._notice("🔁 تكرار نفس الاستدعاء — أُوقفت الحلقة")
            return
        if kind == "notice":
            if ev.text:
                self._notice(ev.text)
            return
        if kind == "turn":
            self._step = int(ev.data.get("step") or self._step + 1)
            self._status = tr.t("working", self.lang, step=self._step, max=self.max_steps)
            self._schedule_edit()
            return
        if kind == "step":
            self._server_steps += 1
            return
        if kind == "usage":
            self._usage = Usage.from_dict(ev.data)
            return
        if kind == "finish":
            return
        if kind == "error":
            self._notice(f"⚠️ {_one_line(ev.text)[:200]}")
            return

    def _notice(self, text: str) -> None:
        self._notices.append(text)
        self._notices = self._notices[-6:]
        self._schedule_edit()

    def _schedule_edit(self) -> None:
        if not self.stream or self._closed or self._3mh_broken:
            return
        if self._3mh_flush is not None and not self._3mh_flush.done():
            return
        elapsed = time.monotonic() - self._last_edit
        delay = max(0.0, self.settings.stream_edit_interval - elapsed)
        self._3mh_flush = asyncio.create_task(self._delayed_flush(delay))

    async def _delayed_flush(self, delay: float) -> None:
        try:
            if delay > 0:
                await asyncio.sleep(delay)
            await self.flush()
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("فشل تحديث الرسالة الحيّة")

    async def flush(self, *, force: bool = False) -> None:
        if self._closed or self.reply_msg is None or self._3mh_broken:
            return
        now = time.monotonic()
        if not force and now - self._last_edit < self.settings.stream_edit_interval * 0.9:
            return
        content = self._render(progress=True)
        try:
            await self._edit(content)
            self._last_edit = time.monotonic()
            self._edits += 1
        except BadRequest as exc:
            if "not modified" in str(exc).lower():
                self._last_edit = time.monotonic()
                return
            log.warning("BadRequest أثناء التعديل: %s", exc)
            self._3mh_broken = True
        except (TimedOut, TelegramError) as exc:
            log.warning("تعذّر تعديل الرسالة: %s", exc)
            self._3mh_broken = True

    async def _edit(self, content: str, reply_markup: Optional[InlineKeyboardMarkup] = None) -> None:
        if self.reply_msg is None:
            return
        kwargs: Dict[str, Any] = dict(_no_preview_kwargs())
        if reply_markup is not None:
            kwargs["reply_markup"] = reply_markup
        chat_id = self.reply_msg.chat_id
        message_id = self.reply_msg.message_id
        try:
            await self.context.bot.edit_message_text(
                chat_id=chat_id, message_id=message_id, text=content,
                parse_mode=ParseMode.HTML, **kwargs)
        except BadRequest as exc:
            message = str(exc).lower()
            if "not modified" in message:
                raise
            if "parse" in message or "entities" in message or "tag" in message:
                await self.context.bot.edit_message_text(
                    chat_id=chat_id, message_id=message_id,
                    text=render.strip_markdown(self._plain_body())[:4096], **kwargs)
                return
            raise
        if self._edits % 3 == 0:
            await self._typing()

    def _plain_body(self) -> str:
        return "".join(self._text_parts)

    def _render(self, *, progress: bool = False, final_text: Optional[str] = None,
                stats: str = "", reply_markup: Optional[InlineKeyboardMarkup] = None) -> str:
        body = final_text if final_text is not None else "".join(self._text_parts)
        blocks: List[str] = []
        if self.show_reasoning and self._reasoning_parts:
            reasoning = "".join(self._reasoning_parts).strip()
            if reasoning:
                quoted = "\n".join(f"> {line}" for line in reasoning[-1200:].splitlines())
                blocks.append(f"💭 <i>تفكير</i>\n{render.md_to_html(quoted)}")
        if body.strip():
            limit = 3000 if progress else render.MD_LIMIT
            blocks.append(render.md_to_html(render.tail_text(body, limit) if progress else body))
        elif progress:
            blocks.append(f"<i>{render.escape_html(self._status or tr.t('thinking', self.lang))}</i>")
        if self.show_trace and self._trace:
            trace = self._trace[-8:] if progress else self._trace[-6:]
            blocks.append(render.md_to_html("\n".join(trace)))
        if self._notices:
            blocks.append(render.md_to_html("\n".join(self._notices[-3:])))
        footer_bits: List[str] = []
        if progress:
            elapsed = time.monotonic() - self._started
            footer_bits.append(f"⏱ {elapsed:.0f}ث")
            if self._step:
                footer_bits.append(f"🧩 خطوة {self._step}")
            if self.model:
                footer_bits.append(f"🧠 {_short_model(self.model)}")
            footer_bits.append("▌")
        elif stats:
            footer_bits.append(stats)
        if footer_bits:
            blocks.append(f"<code>{render.escape_html(' • '.join(footer_bits))}</code>")
        content = "\n\n".join(b for b in blocks if b)
        if len(content) > 4096:
            content = content[:4090] + "\n<code>…</code>"
        return content

    async def finish(
        self,
        *,
        text: str,
        stats: str = "",
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        notes: Optional[List[str]] = None,
    ) -> None:
        if self._closed:
            return
        self._closed = True
        await self._cancel_flush()
        final_text = text or tr.t("empty_answer", self.lang)
        if notes:
            final_text = final_text + "\n\n" + "\n".join(f"_{n}_" for n in notes)
        chunks = render.split_markdown(final_text, render.MD_LIMIT)
        if not chunks:
            chunks = [final_text or "…"]
        if len(chunks) == 1:
            content = self._render(final_text=chunks[0], stats=stats)
            if self.reply_msg is not None and not self._3mh_broken:
                try:
                    await self._edit(content, reply_markup=reply_markup)
                    return
                except RetryAfter as exc:
                    await asyncio.sleep(exc.retry_after + 0.3)
                    try:
                        await self._edit(content, reply_markup=reply_markup)
                        return
                    except TelegramError as exc2:
                        log.warning("فشل التعديل النهائي: %s", exc2)
                except TelegramError as exc:
                    log.warning("فشل التعديل النهائي: %s", exc)
            await self._send_html(chunks[0], stats=stats, reply_markup=reply_markup)
            return
        for index, chunk in enumerate(chunks):
            is_last = index == len(chunks) - 1
            if index == 0 and self.reply_msg is not None and not self._3mh_broken:
                try:
                    await self._edit(render.md_to_html(chunk) + (
                        "" if is_last else "\n\n<code>…يتبع</code>"))
                    continue
                except TelegramError as exc:
                    log.warning("تعذّر تعديل الرسالة الأولى: %s", exc)
            await self._send_html(chunk,
                                  stats=stats if is_last else "",
                                  reply_markup=reply_markup if is_last else None)

    async def _send_html(self, markdown_text: str, *, stats: str = "",
                         reply_markup: Optional[InlineKeyboardMarkup] = None) -> None:
        body = render.md_to_html(markdown_text)
        if stats:
            body = f"{body}\n\n<code>{render.escape_html(stats)}</code>"
        kwargs: Dict[str, Any] = dict(_no_preview_kwargs())
        if reply_markup is not None:
            kwargs["reply_markup"] = reply_markup
        try:
            await self._reply(body[:4096], parse_mode=ParseMode.HTML, **kwargs)
        except BadRequest:
            try:
                plain = render.strip_markdown(markdown_text)[:4096]
                if stats:
                    plain += f"\n\n{stats}"
                await self._reply(plain, **kwargs)
            except TelegramError as exc:
                log.error("تعذّر إرسال الرد النهائي: %s", exc)
        except TelegramError as exc:
            log.error("تعذّر إرسال الرد النهائي: %s", exc)

    async def abort(self, reason: str, *, error: bool = False) -> None:
        if self._closed:
            return
        self._closed = True
        await self._cancel_flush()
        prefix = "⚠️" if error else "⏹️"
        body = f"{prefix} {reason}"
        partial = "".join(self._text_parts).strip()
        if partial:
            body += "\n\n" + render.md_to_html(render.tail_text(partial, 1500))
        if self.show_trace and self._trace:
            body += "\n\n" + render.md_to_html("\n".join(self._trace[-5:]))
        content = body[:4096]
        if self.reply_msg is not None and not self._3mh_broken:
            try:
                await self._edit(content)
                return
            except TelegramError as exc:
                log.warning("تعذّر تحديث رسالة الإلغاء: %s", exc)
        try:
            await self._reply(content, parse_mode=ParseMode.HTML, **_no_preview_kwargs())
        except TelegramError:
            pass

    async def _cancel_flush(self) -> None:
        task, self._3mh_flush = self._3mh_flush, None
        if task is not None and not task.done():
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass


def _args_preview(args: Any, limit: int = 90) -> str:
    if not args:
        return ""
    try:
        import json
        text = json.dumps(args, ensure_ascii=False, default=str)
    except Exception:
        text = str(args)
    text = text.replace("\n", " ").replace("`", "'")
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return f"`{text}`"


def _one_line(text: str) -> str:
    return " ".join(str(text).split())


def _short_model(model: str) -> str:
    return str(model or "").split("/")[-1]
