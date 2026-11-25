# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import asyncio
import base64
import io
import json
import logging
import os
import platform
import re
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Tuple
import telegram
from telegram import InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ChatAction, ChatType, ParseMode
from telegram.error import BadRequest, TelegramError, TimedOut
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from .. import __version__ as BOT_VERSION
from .. import memory as MEM
from .. import models as MODELS
from .. import protocol as P
from ..agent import AgentCore
from ..backend import ConnectionPool, probe_model
from ..config import Settings
from ..store import Store
from ..tools import ToolRegistry
from . import keyboards as KB
from . import render
from .stream import StreamRenderer, _no_preview_kwargs
from .ui import help_text, tr
log = logging.getLogger("mh3.handlers")
_TEXT_SUFFIXES = {
    ".txt", ".md", ".json", ".csv", ".tsv", ".log", ".py", ".js", ".ts", ".html", ".css",
    ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".sh", ".sql", ".env", ".rst", ".tex",
    ".java", ".c", ".h", ".cpp", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".ipynb",
}
_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
_MAX_DOC_CHARS = 24_000
_MAX_IMAGE_BYTES = 8 * 1024 * 1024


class BotHandlers:

    def __init__(
        self,
        settings: Settings,
        store: Store,
        registry: ToolRegistry,
        pool: ConnectionPool,
        agent: AgentCore,
        bot_name: str = "3mh agent",
    ) -> None:
        self.settings = settings
        self.store = store
        self.registry = registry
        self.pool = pool
        self.agent = agent
        self.bot_name = bot_name
        self.started_at = time.time()
        self._hits: Dict[int, Deque[float]] = {}
        self._ui: Dict[int, Dict[str, Any]] = {}
        self._pending: Dict[int, Dict[str, Any]] = {}

    def register(self, app: Application) -> None:
        commands: List[Tuple[List[str], Any]] = [
            (["start", "ابدأ"], self.cmd_start),
            (["help", "مساعدة", "اوامر"], self.cmd_help),
            (["id"], self.cmd_id),
            (["model", "نموذج"], self.cmd_model),
            (["models", "النماذج"], self.cmd_models),
            (["system", "persona", "شخصية"], self.cmd_system),
            (["reset", "new", "مسح"], self.cmd_reset),
            (["compact", "ضغط"], self.cmd_compact),
            (["history", "السجل"], self.cmd_history),
            (["export", "تصدير"], self.cmd_export),
            (["tools", "الادوات"], self.cmd_tools),
            (["think", "تفكير"], self.cmd_think),
            (["temp", "temperature"], self.cmd_temp),
            (["maxsteps", "خطوات"], self.cmd_maxsteps),
            (["usage", "الاحصاءات"], self.cmd_usage),
            (["note", "ملاحظة"], self.cmd_note),
            (["notes", "الملاحظات"], self.cmd_notes),
            (["delnote"], self.cmd_delnote),
            (["files", "الملفات"], self.cmd_files),
            (["file", "ملف"], self.cmd_file),
            (["clearfiles"], self.cmd_clearfiles),
            (["reminders", "التذكيرات"], self.cmd_reminders),
            (["stop", "cancel", "ايقاف"], self.cmd_stop),
            (["retry", "again", "اعد"], self.cmd_retry),
            (["status", "الحالة"], self.cmd_status),
            (["ping"], self.cmd_ping),
            (["settings", "الاعدادات"], self.cmd_settings),
            (["lang", "لغة"], self.cmd_lang),
            (["about", "عن"], self.cmd_about),
            (["menu", "القائمة", "لوحة"], self.cmd_menu),
            (["hide"], self.cmd_hide_menu),
        ]
        for names, handler in commands:
            app.add_handler(CommandHandler(names, handler))
        app.add_handler(CallbackQueryHandler(self.on_callback))
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND
            | filters.PHOTO | filters.Document.ALL | filters.VIDEO
            | filters.AUDIO | filters.VOICE | filters.Sticker.ALL,
            self.on_message))
        app.add_handler(MessageHandler(filters.StatusUpdate.ALL, self.on_status_update))
        app.add_error_handler(self.on_error)

    async def gate(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        chat = update.effective_chat
        user = update.effective_user
        if chat is None:
            return False
        lang = self._lang(chat.id, user)
        allowed = self.settings.is_chat_allowed(chat.id, chat.type or "private")
        is_admin = self.settings.is_admin(user.id if user else None,
                                          user.username if user else None)
        if self.settings.access_mode == "admins" and not is_admin:
            await self._send(update, context, tr.t("denied", lang, user_id=user.id if user else 0))
            return False
        if not allowed and not is_admin:
            await self._send(update, context, tr.t("denied_chat", lang, chat_id=chat.id))
            return False
        if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP) and not is_admin:
            if not self._mentioned(update, context):
                return False
        return True

    def _mentioned(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        msg = update.effective_message
        if msg is None:
            return False
        if msg.reply_to_message is not None and msg.reply_to_message.from_user is not None:
            bot_user = context.bot.username or ""
            if msg.reply_to_message.from_user.username == bot_user:
                return True
        bot_user = (context.bot.username or "").lower()
        text = (msg.text or msg.caption or "").lower()
        return bool(bot_user and f"@{bot_user}" in text)

    def rate_limit(self, chat_id: int) -> Optional[int]:
        limit = self.settings.rate_limit_per_min
        if limit <= 0:
            return None
        now = time.monotonic()
        bucket = self._hits.setdefault(chat_id, deque(maxlen=limit * 2))
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= limit:
            return int(60 - (now - bucket[0])) + 1
        bucket.append(now)
        return None

    async def _load_ui(self, chat_id: int) -> Dict[str, Any]:
        cached = self._ui.get(chat_id)
        if cached is not None:
            return cached
        data = await self.store.kv_get(f"ui:{chat_id}", {}) or {}
        defaults = {
            "lang": self.settings.ui_language,
            "trace": self.settings.show_tool_trace,
            "usage": self.settings.show_usage,
            "stream": self.settings.stream_edits,
            "reasoning": self.settings.show_reasoning,
        }
        defaults.update({k: v for k, v in data.items() if k in defaults})
        self._ui[chat_id] = defaults
        return defaults

    def _lang(self, chat_id: int, user: Any = None) -> str:
        cached = self._ui.get(chat_id)
        if cached and cached.get("lang"):
            return str(cached["lang"])
        if self.settings.ui_language != "auto":
            return self.settings.ui_language
        code = getattr(user, "language_code", None) if user else None
        return "ar" if str(code or "").lower().startswith("ar") else "en"

    async def _send(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str,
                    *, reply_markup: Optional[InlineKeyboardMarkup] = None,
                    markdown: bool = True) -> Optional[telegram.Message]:
        chat_id = update.effective_chat.id if update.effective_chat else 0
        if not chat_id:
            return None
        kwargs: Dict[str, Any] = dict(_no_preview_kwargs())
        if reply_markup is not None:
            kwargs["reply_markup"] = reply_markup
        body = render.md_to_html(text) if markdown else render.escape_html(text)
        try:
            return await context.bot.send_message(chat_id=chat_id, text=body[:4096],
                                                  parse_mode=ParseMode.HTML, **kwargs)
        except BadRequest as exc:
            log.warning("فشل الإرسال (HTML): %s", exc)
            try:
                return await context.bot.send_message(
                    chat_id=chat_id, text=render.strip_markdown(text)[:4096], **kwargs)
            except TelegramError as exc2:
                log.error("فشل الإرسال: %s", exc2)
        except TelegramError as exc:
            log.error("فشل الإرسال: %s", exc)
        return None

    async def _answer_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                               text: str = "") -> None:
        query = update.callback_query
        if query is None:
            return
        try:
            await context.bot.answer_callback_query(
                callback_query_id=query.id, text=(text[:200] if text else None))
        except TelegramError:
            pass

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        sess = await self.store.load_session(chat_id, defaults={
            "model": self.settings.default_model, "temperature": self.settings.temperature})
        is_admin = self.settings.is_admin(update.effective_user.id if update.effective_user else None,
                                          update.effective_user.username if update.effective_user else None)
        tools = len(self.registry.enabled(admin=is_admin))
        await self._send(update, context, tr.t(
            "start_welcome", lang, bot_name=self.bot_name,
            role="مشرف" if is_admin else "مستخدم",
            model=sess.model or self.settings.default_model, tools=tools,
            **self._3mh_brand()),
            reply_markup=KB.main_menu_keyboard(self._3mh_brand(), self._3mh_colors()))
        await self._attach_reply_keyboard(update, context)
        if not is_admin:
            await self._send(update, context, tr.t("group_notice", lang))

    async def cmd_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        lang = self._lang(update.effective_chat.id, update.effective_user)
        await self._send(update, context, tr.t("menu_header", lang, bot_name=self.bot_name),
                         reply_markup=KB.main_menu_keyboard(self._3mh_brand(), self._3mh_colors()))
        await self._attach_reply_keyboard(update, context)

    async def cmd_hide_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        lang = self._lang(update.effective_chat.id, update.effective_user)
        await self._send(update, context, tr.t("menu_hidden", lang),
                         reply_markup=ReplyKeyboardRemove())

    def _3mh_colors(self) -> bool:
        return bool(self.settings.button_colors)

    def _3mh_brand(self) -> Dict[str, str]:
        return {"company": self.settings.company_name, "site": self.settings.company_site,
                "support": self.settings.support_url, "channel": self.settings.channel_url}

    async def _attach_reply_keyboard(self, update: Update,
                                     context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self.settings.menu_buttons:
            return
        chat = update.effective_chat
        if chat is None or chat.type not in ("private", "group", "supergroup"):
            return
        try:
            await context.bot.send_chat_action(chat.id, ChatAction.TYPING)
        except TelegramError:
            pass
        try:
            await context.bot.send_message(
                chat_id=chat.id, text="🎛️",
                reply_markup=KB.main_reply_keyboard(self._3mh_colors()))
        except TelegramError as exc:
            log.debug("تعذّر إرفاق لوحة الأزرار: %s", exc)

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        lang = self._lang(update.effective_chat.id, update.effective_user)
        await self._send(update, context, help_text(lang))

    async def cmd_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        user = update.effective_user
        chat = update.effective_chat
        text = (f"🆔 *المعرّفات*\n"
                f"• user_id: `{user.id}`\n"
                f"• chat_id: `{chat.id}`\n"
                f"• username: `{user.username or '—'}`\n"
                f"• نوع المحادثة: `{chat.type}`\n"
                f"• مشرف؟ {'نعم' if self.settings.is_admin(user.id, user.username) else 'لا'}")
        await self._send(update, context, text)

    async def cmd_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        args = (context.args or [])
        sess = await self.store.load_session(chat_id, defaults={"model": self.settings.default_model})
        if not args:
            featured = MODELS.suggest_models("", limit=40)
            await self._send(update, context,
                             tr.t("models_header", lang, page=1, pages=max(1, -(-len(featured) // KB.PER_PAGE_MODELS))),
                             reply_markup=KB.models_keyboard(featured, 0, current=sess.model,
                                                         colors=self._3mh_colors()))
            return
        query = " ".join(args)
        info = MODELS.resolve_model(query)
        if info is None:
            await self._send(update, context, tr.t("model_unknown", lang, query=query))
            return
        sess.model = info.id
        await self.store.save_session(sess)
        await self.pool.close(chat_id)
        await self._send(update, context,
                         f"{tr.t('model_set', lang, model=info.id)}\n\n{MODELS.describe_model(info.id)}")

    async def cmd_models(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        args = context.args or []
        if args and args[0].lower() in ("refresh", "probe", "فحص", "check"):
            await self._probe_models(update, context)
            return
        query = " ".join(args)
        sess = await self.store.load_session(chat_id, defaults={"model": self.settings.default_model})
        found = MODELS.suggest_models(query, limit=60)
        if not found:
            await self._send(update, context, tr.t("model_unknown", lang, query=query))
            return
        lines = [tr.t("models_header", lang, page=1,
                      pages=max(1, -(-len(found) // KB.PER_PAGE_MODELS)))]
        await self._send(update, context, "\n".join(lines),
                         reply_markup=KB.models_keyboard(found, 0, current=sess.model, query=query,
                                                     colors=self._3mh_colors()))

    async def _probe_models(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        msg = await self._send(update, context, "🔎 جارٍ فحص توفّر النماذج… (قد يستغرق دقيقة)")
        models = [m for m in MODELS.CATALOG if not m.gated][:24]
        semaphore = asyncio.Semaphore(3)
        results: Dict[str, Tuple[bool, str, float]] = {}
        done = 0

        async def worker(info: MODELS.ModelInfo) -> None:
            nonlocal done
            async with semaphore:
                results[info.id] = await probe_model(self.settings, info.id, timeout=25)
                done += 1
                if msg is not None and done % 4 == 0:
                    body = _probe_report(results, lang)
                    try:
                        await context.bot.edit_message_text(
                            chat_id=msg.chat_id, message_id=msg.message_id,
                            text=render.md_to_html(body)[:4096], parse_mode=ParseMode.HTML,
                            **_no_preview_kwargs())
                    except TelegramError:
                        pass
        await asyncio.gather(*(worker(m) for m in models), return_exceptions=True)
        body = _probe_report(results, lang)
        ok = sum(1 for v in results.values() if v[0])
        header = tr.t("models_refresh_done", lang, count=len(results), ok=ok,
                      fail=len(results) - ok)
        if msg is not None:
            try:
                await context.bot.edit_message_text(
                    chat_id=msg.chat_id, message_id=msg.message_id,
                    text=render.md_to_html(header + "\n\n" + body)[:4096],
                    parse_mode=ParseMode.HTML, **_no_preview_kwargs())
            except TelegramError:
                await self._send(update, context, header + "\n\n" + body)
        await self.store.kv_set("model_probe", {"ts": time.time(),
                                               "results": {k: [v[0], v[1], round(v[2], 2)]
                                                           for k, v in results.items()}})

    async def cmd_system(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        sess = await self.store.load_session(chat_id, defaults={"model": self.settings.default_model})
        args = context.args or []
        if not args:
            current = sess.system or "(الافتراضي المدمج)"
            await self._send(update, context,
                             f"📜 *برومبت النظام*\n\n{current}\n\n"
                             f"للضبط: `/system نص جديد` — للإلغاء: `/system clear`")
            return
        text = " ".join(args)
        if text.lower() in ("clear", "reset", "مسح", "الغاء"):
            sess.system = ""
            await self.store.save_session(sess)
            await self._send(update, context, "✅ أُعيد برومبت النظام إلى الافتراضي.")
            return
        sess.system = text[:8000]
        await self.store.save_session(sess)
        await self.pool.close(chat_id)
        await self._send(update, context, f"✅ تم ضبط برومبت النظام ({len(sess.system)} حرف).\n"
                                          f"{tr.t('model_current', lang, model=sess.model, info='')}")

    async def cmd_reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        query = update.callback_query
        if query is None and not (context.args and context.args[0].lower() in ("force", "now", "الان")):
            await self._send(update, context, tr.t("reset_confirm", lang),
                             reply_markup=KB.confirm_keyboard("reset", self._3mh_colors()))
            return
        sess = await self.store.load_session(chat_id)
        turns = sess.turn_count
        sess.messages = []
        sess.summary = ""
        sess.title = ""
        await self.store.save_session(sess)
        conn = self.pool.peek(chat_id)
        if conn is not None:
            try:
                await conn.clear_server_history()
            except Exception:
                pass
        await self.pool.close(chat_id)
        await self._send(update, context, tr.t("reset_done", lang,
                                               extra=f" ({turns} جولة)" if turns else ""))

    async def cmd_compact(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        sess = await self.store.load_session(chat_id)
        if len(sess.messages) < 4:
            await self._send(update, context, "ℹ️ السجل قصير — لا حاجة للضغط.")
            return
        msg = await self._send(update, context, "🗜️ جارٍ ضغط الذاكرة…")
        keep = 6
        old = sess.messages[:-keep] if len(sess.messages) > keep else sess.messages
        before = MEM.estimate_messages(sess.messages)
        summary = await MEM.compact_history(
            old, summarize=self.agent._make_summarizer(chat_id), previous_summary=sess.summary)
        if not summary:
            await self._send(update, context, "⚠️ تعذّر الضغط (لم يُرجع النموذج ملخصاً).")
            return
        sess.summary = summary
        sess.messages = sess.messages[-keep:] if len(sess.messages) > keep else []
        await self.store.save_session(sess)
        after = MEM.estimate_messages(sess.messages) + MEM.estimate_tokens(summary)
        if msg:
            try:
                await msg.edit_text(render.md_to_html(
                    f"✅ تم الضغط: *{before}* → *{after}* توكن تقديري\n\n"
                    f"📄 الملخص:\n{summary[:2000]}")[:4096],
                    parse_mode=ParseMode.HTML, **_no_preview_kwargs())
            except TelegramError:
                pass

    async def cmd_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        sess = await self.store.load_session(chat_id)
        limit = int((context.args or ["20"])[0]) if (context.args or ["20"])[0].isdigit() else 20
        if not sess.messages:
            await self._send(update, context, tr.t("history_empty", lang))
            return
        text = MEM.transcript_of(sess.messages, limit=limit)
        header = (f"🕘 آخر {min(limit, len(sess.messages))} رسالة "
                  f"(الإجمالي {len(sess.messages)}، ~{MEM.estimate_messages(sess.messages)} توكن)")
        if sess.summary:
            header += f"\n🗜️ ملخص مضغوط: {len(sess.summary)} حرف"
        await self._send_chunks(update, context, header + "\n\n" + text)

    async def cmd_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        sess = await self.store.load_session(chat_id)
        data = MEM.export_session(sess)
        path = self.settings.workspace_dir / str(chat_id) / f"session_{int(time.time())}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")
        try:
            with open(path, "rb") as fh:
                await context.bot.send_document(chat_id=chat_id, document=fh,
                                                filename=path.name,
                                                caption=tr.t("exported", lang))
        except TelegramError as exc:
            await self._send(update, context, f"⚠️ تعذّر إرسال الملف: {exc}")

    async def cmd_tools(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        is_admin = self.settings.is_admin(update.effective_user.id if update.effective_user else None)
        args = context.args or []
        if args:
            name = args[0].lower()
            spec = self.registry.get(name)
            if spec is None:
                await self._send(update, context, f"❓ أداة غير معروفة: `{name}`")
                return
            if len(args) > 1 and args[1].lower() in ("on", "off", "enable", "disable", "تفعيل", "تعطيل"):
                enable = args[1].lower() in ("on", "enable", "تفعيل")
                if spec.admin_only and not is_admin:
                    await self._send(update, context, tr.t("need_admin", lang))
                    return
                self.registry.set_runtime_enabled(name, enable)
                await self._send(update, context,
                                 f"{'🟢 فُعّلت' if enable else '⚪ عُطّلت'} الأداة `{name}`")
                return
            await self._send(update, context,
                             f"🔧 *{spec.name}*\n\n{spec.description}\n\n"
                             f"التصنيف: `{spec.category}`\n"
                             f"المهلة: `{spec.timeout}` ثانية\n"
                             f"مشرفون فقط: {'نعم' if spec.admin_only else 'لا'}\n"
                             f"الحالة: {'مفعّلة' if self.registry.is_enabled(name) else 'معطّلة'}\n\n"
                             f"المخطط:\n```json\n{json.dumps(spec.parameters, ensure_ascii=False, indent=1)[:2500]}\n```")
            return
        enabled = len(self.registry.enabled(admin=is_admin))
        header = tr.t("tools_header", lang, enabled=enabled, total=len(self.registry.all))
        groups = self.registry.categories()
        lines = [header, ""]
        for category, specs in groups.items():
            lines.append(f"*{category}*")
            for spec in specs:
                lines.append(f"  {spec.line(enabled=self.registry.is_enabled(spec.name))}")
        text = "\n".join(lines)
        if len(text) > 3500:
            await self._send_chunks(update, context, text)
        else:
            await self._send(update, context, text,
                             reply_markup=KB.tools_keyboard(self.registry, 0, admin=is_admin,
                                                     colors=self._3mh_colors()))

    async def cmd_think(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        sess = await self.store.load_session(chat_id)
        ui = await self._load_ui(chat_id)
        if context.args:
            sess.show_reasoning = str(context.args[0]).lower() in ("on", "1", "true", "تفعيل")
        else:
            sess.show_reasoning = not sess.show_reasoning
        ui["reasoning"] = sess.show_reasoning
        self._ui[chat_id] = ui
        await self.store.save_session(sess)
        await self.store.kv_set(f"ui:{chat_id}", ui)
        await self._send(update, context, tr.t("think_on" if sess.show_reasoning else "think_off", lang))

    async def cmd_temp(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        args = context.args or []
        if not args:
            sess = await self.store.load_session(chat_id)
            await self._send(update, context,
                             f"🌡️ الحرارة الحالية: `{sess.temperature}`\nالاستخدام: `/temp 0.7` (0 → 2)")
            return
        try:
            value = float(args[0])
        except ValueError:
            await self._send(update, context, tr.t("invalid_number", lang, value=args[0]))
            return
        value = max(0.0, min(2.0, value))
        sess = await self.store.load_session(chat_id)
        sess.temperature = value
        await self.store.save_session(sess)
        await self._send(update, context, tr.t("temp_set", lang, value=value))

    async def cmd_maxsteps(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        args = context.args or []
        lang = self._lang(update.effective_chat.id, update.effective_user)
        if not args:
            await self._send(update, context,
                             f"🧩 حد الخطوات الحالي: `{self.settings.max_steps}`\n"
                             f"الاستخدام: `/maxsteps 15` (1 → 40)")
            return
        try:
            value = max(1, min(40, int(args[0])))
        except ValueError:
            await self._send(update, context, tr.t("invalid_number", lang, value=args[0]))
            return
        self.settings.max_steps = value
        await self.store.kv_set("max_steps", value)
        await self._send(update, context, f"✅ حد خطوات الوكيل الآن `{value}`")

    async def cmd_usage(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        days = 7
        if context.args and context.args[0].isdigit():
            days = max(1, min(365, int(context.args[0])))
        scope_all = bool(context.args and context.args[-1].lower() in ("all", "global", "الكل"))
        data = await self.store.usage_summary(None if scope_all else chat_id, days=days)
        tools = await self.store.tool_stats(None if scope_all else chat_id, limit=8)
        lines = [tr.t("usage_header", lang, days=days),
                 f"• الطلبات: `{data['requests']}` (ناجح `{data['ok']}`)",
                 f"• التوكنز: `{data['total_tokens']}` "
                 f"(دخل `{data['input_tokens']}` / خرج `{data['output_tokens']}`)",
                 f"• التكلفة التقديرية: `${data['cost_usd']:.4f}`",
                 f"• زمن التوليد: `{data['generation_ms'] / 1000:.1f}` ثانية",
                 f"• خطوات الوكيل: `{data['steps']}` • استدعاءات الأدوات: `{data['tool_calls']}`"]
        if data["models"]:
            lines.append("\n*النماذج*")
            for model, stats in list(data["models"].items())[:6]:
                lines.append(f"• `{model.split('/')[-1]}`: {stats['requests']} طلب، {stats['tokens']} توكن")
        if tools:
            lines.append("\n*أكثر الأدوات استخداماً*")
            for row in tools:
                lines.append(f"• `{row['tool']}`: {int(row['c'])} مرة "
                             f"(نجاح {int(row['ok'])}، متوسط {row['avg_ms']:.0f}م.ث)")
        await self._send_chunks(update, context, "\n".join(lines))

    async def cmd_note(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        text = " ".join(context.args or []).strip()
        if not text:
            await self._send(update, context, "📝 الاستخدام: `/note نص الملاحظة`")
            return
        title = text.splitlines()[0][:80]
        note_id = await self.store.add_note(chat_id, title, text)
        await self._send(update, context, tr.t("note_saved", lang, id=note_id))

    async def cmd_notes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        query = " ".join(context.args or [])
        rows = await self.store.search_notes(chat_id, query, limit=25)
        if not rows:
            await self._send(update, context, tr.t("notes_empty", lang))
            return
        lines = [f"📚 *الملاحظات* ({len(rows)})"]
        for row in rows:
            when = datetime.fromtimestamp(row["created_at"]).strftime("%m-%d %H:%M")
            body = " ".join(str(row["body"]).split())[:90]
            lines.append(f"• #{row['id']} `{when}` *{row['title'] or '—'}* — {body}")
        lines.append("\nللحذف: `/delnote <رقم>`")
        await self._send_chunks(update, context, "\n".join(lines))

    async def cmd_delnote(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        args = context.args or []
        if not args or not args[0].isdigit():
            await self._send(update, context, "🗑️ الاستخدام: `/delnote 12`")
            return
        ok = await self.store.delete_note(chat_id, int(args[0]))
        await self._send(update, context, f"{'✅ حُذفت' if ok else '❓ غير موجودة'} الملاحظة #{args[0]}")

    async def cmd_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        workspace = self.settings.workspace_dir / str(chat_id)
        workspace.mkdir(parents=True, exist_ok=True)
        entries: List[str] = []
        total = 0
        for item in sorted(workspace.rglob("*")):
            if item.is_file():
                size = item.stat().st_size
                total += size
                entries.append(f"• `{item.relative_to(workspace)}` — {_human(size)}")
            else:
                entries.append(f"📁 `{item.relative_to(workspace)}/`")
            if len(entries) >= 120:
                break
        if not entries:
            await self._send(update, context, tr.t("files_empty", lang) +
                             f"\nالمسار: `{workspace}`")
            return
        header = f"📂 *مجلد العمل* ({len(entries)} عنصر، {_human(total)})\n`{workspace}`\n"
        await self._send_chunks(update, context, header + "\n".join(entries))

    async def cmd_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        args = context.args or []
        if not args:
            await self._send(update, context, "📤 الاستخدام: `/file path/to/file`")
            return
        raw = " ".join(args).strip()
        workspace = (self.settings.workspace_dir / str(chat_id)).resolve()
        target = (workspace / raw.lstrip("/")).resolve()
        if workspace not in target.parents and target != workspace:
            await self._send(update, context, "⛔ المسار خارج مجلد العمل.")
            return
        if not target.is_file():
            await self._send(update, context, f"❓ الملف غير موجود: `{raw}`")
            return
        try:
            with open(target, "rb") as fh:
                await context.bot.send_document(chat_id=chat_id, document=fh, filename=target.name)
        except TelegramError as exc:
            await self._send(update, context, f"⚠️ تعذّر الإرسال: {exc}")

    async def cmd_clearfiles(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        query = update.callback_query
        if query is None and not (context.args and context.args[0].lower() in ("force", "now")):
            await self._send(update, context, "⚠️ سيتم حذف *كل* ملفات مجلد العمل لهذه المحادثة. متأكد؟",
                             reply_markup=KB.confirm_keyboard("clearfiles", self._3mh_colors()))
            return
        workspace = self.settings.workspace_dir / str(chat_id)
        if workspace.exists():
            import shutil
            shutil.rmtree(workspace, ignore_errors=True)
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "outputs").mkdir(exist_ok=True)
        await self._send(update, context, tr.t("workspace_cleared", lang))

    async def cmd_reminders(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        rows = await self.store.list_reminders(chat_id)
        if not rows:
            await self._send(update, context, "⏰ لا توجد تذكيرات مجدولة.\n"
                                              "اطلب من الوكيل: «ذكّرني بعد 30 دقيقة بـ …»")
            return
        lines = ["⏰ *التذكيرات*"]
        for row in rows:
            due = datetime.fromtimestamp(row["due_ts"]).strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"• #{row['id']} `{due}` — {row['text'][:120]}")
        await self._send(update, context, "\n".join(lines))

    async def cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id if update.effective_chat else 0
        lang = self._lang(chat_id, update.effective_user)
        if self.agent.request_cancel(chat_id):
            conn = self.pool.peek(chat_id)
            if conn is not None:
                try:
                    await conn.cancel()
                except Exception:
                    pass
            await self._send(update, context, "⏹️ جارٍ إيقاف التوليد…")
        else:
            await self._send(update, context, "ℹ️ لا يوجد توليد جارٍ في هذه المحادثة.")

    async def cmd_retry(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        await self._run_turn(update, context, text="", regenerate=True)

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        sess = await self.store.load_session(chat_id, defaults={"model": self.settings.default_model})
        conn = self.pool.peek(chat_id)
        pool_stats = self.pool.stats()
        uptime = time.time() - self.started_at
        notes = await self.store.count_notes(chat_id)
        ws = self.settings.workspace_dir / str(chat_id)
        files = sum(1 for _ in ws.rglob("*") if _.is_file()) if ws.exists() else 0
        lines = [
            tr.t("status_header", lang),
            f"• الإصدار: `{BOT_VERSION}` • PTB `{telegram.__version__}` • Python `{platform.python_version()}`",
            f"• التشغيل: `{_human_duration(uptime)}`",
            f"• النموذج: `{sess.model}`",
            f"• البدائل: `{', '.join(m.split('/')[-1] for m in self.settings.fallback_models[1:]) or '—'}`",
            f"• الاتصال: {'🟢 متصل' if conn else '⚪ غير متصل'}"
            + (f" — `{json.dumps(conn.info(), ensure_ascii=False)}`" if conn else ""),
            f"• الاتصالات: `{pool_stats['connections']}` (نشط `{pool_stats['active']}`) • الخطوات: `{pool_stats['turns']}`",
            f"• الأدوات: `{len(self.registry.enabled(admin=True))}/{len(self.registry.all)}` مفعّلة",
            f"• الذاكرة: `{len(sess.messages)}` رسالة، `{notes}` ملاحظة، "
            f"`{MEM.estimate_messages(sess.messages)}` توكن تقديري",
            f"• مجلد العمل: `{files}` ملف — `{ws}`",
            f"• حد الخطوات: `{self.settings.max_steps}` • مهلة الخطوة: `{int(self.settings.step_timeout)}ث`",
            f"• وضع الوصول: `{self.settings.access_mode}` • المشرفون: `{len(self.settings.admin_ids)}`",
        ]
        await self._send_chunks(update, context, "\n".join(lines))

    async def cmd_ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        lang = self._lang(update.effective_chat.id, update.effective_user)
        started = time.monotonic()
        msg = await self._send(update, context, "🏓 …")
        ms = int((time.monotonic() - started) * 1000)
        if msg is not None:
            try:
                await msg.edit_text(render.md_to_html(tr.t("pong", lang, ms=ms)),
                                    parse_mode=ParseMode.HTML)
            except TelegramError:
                pass

    async def cmd_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        sess = await self.store.load_session(chat_id, defaults={"model": self.settings.default_model})
        ui = await self._load_ui(chat_id)
        lines = [tr.t("settings_header", lang),
                 f"• النموذج: `{sess.model}`",
                 f"• الحرارة: `{sess.temperature}`",
                 f"• برومبت نظام مخصص: {'نعم' if sess.system else 'لا'}",
                 f"• عرض التفكير: {'🟢' if sess.show_reasoning else '⚪'}",
                 f"• سجل الأدوات: {'🟢' if ui.get('trace') else '⚪'}",
                 f"• الإحصاءات: {'🟢' if ui.get('usage') else '⚪'}",
                 f"• البث الحي: {'🟢' if ui.get('stream') else '⚪'}",
                 f"• اللغة: `{ui.get('lang')}`"]
        await self._send(update, context, "\n".join(lines),
                         reply_markup=KB.settings_keyboard(sess, ui, self._3mh_colors()))

    async def cmd_lang(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        args = context.args or []
        ui = await self._load_ui(chat_id)
        if args and str(args[0]).lower()[:2] in ("ar", "en"):
            ui["lang"] = str(args[0]).lower()[:2]
        else:
            ui["lang"] = "en" if ui.get("lang") == "ar" else "ar"
        self._ui[chat_id] = ui
        await self.store.kv_set(f"ui:{chat_id}", ui)
        await self._send(update, context, tr.t("lang_set", ui["lang"], lang=ui["lang"]))

    async def cmd_about(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        lang = self._lang(update.effective_chat.id, update.effective_user)
        await self._send(update, context, tr.t(
            "about_brand", lang, bot_name=self.bot_name, version=BOT_VERSION,
            **self._3mh_brand()),
            reply_markup=KB.brand_keyboard(self._3mh_colors()))

    async def on_status_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        return None

    async def on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.gate(update, context):
            return
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        if await self._route_menu_button(update, context):
            return
        wait = self.rate_limit(chat_id)
        if wait is not None:
            await self._send(update, context, tr.t("rate_limited", lang,
                                                   limit=self.settings.rate_limit_per_min, wait=wait))
            return
        if self.agent.is_busy(chat_id):
            await self._send(update, context, tr.t("busy", lang))
            return
        await self._run_turn(update, context)

    async def _route_menu_button(self, update: Update,
                                 context: ContextTypes.DEFAULT_TYPE) -> bool:
        _3mh_text = (update.effective_message.text or "").strip() if update.effective_message else ""
        _3mh_map = {v: k for k, v in KB.MENU_LABELS.items()}
        _3mh_key = _3mh_map.get(_3mh_text)
        if _3mh_key is None:
            return False
        context.args = []
        _3mh_route = {
            "model": self.cmd_model, "tools": self.cmd_tools, "files": self.cmd_files,
            "memory": self.cmd_notes, "usage": self.cmd_usage, "settings": self.cmd_settings,
            "stop": self.cmd_stop, "new": self.cmd_reset, "help": self.cmd_help,
            "status": self.cmd_status,
        }.get(_3mh_key)
        if _3mh_route is None:
            return False
        await _3mh_route(update, context)
        return True

    async def _run_turn(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *,
                        text: str = "", regenerate: bool = False) -> None:
        chat = update.effective_chat
        user = update.effective_user
        if chat is None:
            return
        chat_id = chat.id
        lang = self._lang(chat_id, user)
        ui = await self._load_ui(chat_id)
        is_admin = self.settings.is_admin(user.id if user else None,
                                          user.username if user else None)
        sess = await self.store.load_session(chat_id, defaults={
            "model": self.settings.default_model, "temperature": self.settings.temperature})
        if not sess.model:
            sess.model = self.settings.default_model
        message = update.effective_message
        raw_text = text
        attachments: List[Dict[str, Any]] = []
        notes: List[str] = []
        from_callback = update.callback_query is not None
        if not regenerate and message is not None and not from_callback:
            raw_text = raw_text or message.text or message.caption or ""
            reply_to = message.reply_to_message
            if reply_to is not None and not raw_text.startswith("/"):
                quoted = reply_to.text or reply_to.caption or ""
                if quoted:
                    quoted = " ".join(quoted.split())
                    if len(quoted) > 1200:
                        quoted = quoted[:1200] + "…"
                    raw_text = f"[اقتباس من رسالة سابقة]:\n{quoted}\n\n{raw_text}".strip()
            attachments, notes = await self._collect_attachments(
                update, context, chat_id, sess, is_admin)
            if any(a.get("type") == "file" and str(a.get("mediaType", "")).startswith("image/")
                   for a in attachments):
                if not MODELS.is_vision(sess.model):
                    vision = MODELS.vision_models()
                    if vision:
                        chosen = vision[0]
                        notes.append(tr.t("vision_switch", lang, model=chosen.id))
                        sess.model = chosen.id
                        await self.store.save_session(sess)
                        await self.pool.close(chat_id)
        if not raw_text.strip() and not attachments and not regenerate:
            return
        renderer = StreamRenderer(
            update, context, self.settings, lang=lang, model=sess.model,
            show_reasoning=bool(sess.show_reasoning or ui.get("reasoning")),
            show_trace=bool(ui.get("trace", True)), show_usage=bool(ui.get("usage", True)),
            stream=bool(ui.get("stream", True)), max_steps=self.settings.max_steps)

        async def send_file(path: str, caption: str = "") -> None:
            try:
                with open(path, "rb") as fh:
                    await context.bot.send_document(chat_id=chat_id, document=fh,
                                                    filename=os.path.basename(path),
                                                    caption=(caption or "")[:1000] or None)
            except OSError as exc:
                log.warning("تعذّر إرسال الملف %s: %s", path, exc)
            except TelegramError as exc:
                log.warning("فشل إرسال الملف عبر تليجرام: %s", exc)

        async def schedule_reminder(rid: int, target_chat: int, text_: str, delay: float) -> None:
            if context.job_queue is None:
                raise RuntimeError("JobQueue غير مفعّل")
            context.job_queue.run_once(_reminder_job, when=max(1.0, delay),
                                       data={"id": rid, "chat_id": target_chat, "text": text_})
        await renderer.start()
        try:
            result = await self.agent.run(
                chat_id=chat_id,
                user_id=user.id if user else 0,
                username=(user.username if user else "") or "",
                user_name=(user.full_name if user else "") or "",
                is_admin=is_admin,
                chat_type=chat.type or "private",
                text=raw_text,
                files=attachments,
                on_event=renderer.on_event,
                session=sess,
                regenerate=regenerate,
                injected_note=("\n\n".join(notes) if notes else ""),
                send_file=send_file,
                schedule_reminder=schedule_reminder,
            )
        except asyncio.CancelledError:
            await renderer.abort(tr.t("cancelled", lang))
            raise
        except Exception as exc:
            log.exception("فشل تنفيذ الجولة")
            await renderer.abort(f"{type(exc).__name__}: {exc}", error=True)
            return
        stats = result.stats_line() if ui.get("usage", True) else ""
        all_notes = list(notes) + list(result.notes)
        if result.cancelled:
            await renderer.abort(tr.t("cancelled", lang))
        elif result.error:
            await renderer.abort(f"{tr.t('error_generic', lang, error=result.error)}\n"
                                 f"{tr.t('error_hint', lang)}", error=True)
        else:
            await renderer.finish(text=result.text, stats=stats, notes=all_notes,
                                  reply_markup=KB.answer_keyboard(self._3mh_colors(), self.settings.menu_buttons))
        for artifact in result.artifacts:
            if artifact.get("type") == "file":
                await send_file(str(artifact.get("path")), str(artifact.get("caption") or ""))

    async def _collect_attachments(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE,
        chat_id: int, sess: Any, is_admin: bool,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        message = update.effective_message
        attachments: List[Dict[str, Any]] = []
        notes: List[str] = []
        if message is None:
            return attachments, notes
        workspace = self.settings.workspace_dir / str(chat_id) / "uploads"
        workspace.mkdir(parents=True, exist_ok=True)

        async def save_document(doc: Any, kind: str) -> Optional[Path]:
            try:
                file = await context.bot.get_file(doc.file_id)
            except TelegramError as exc:
                notes.append(f"⚠️ تعذّر تنزيل المرفق: {exc}")
                return None
            name = getattr(doc, "file_name", None) or f"{kind}_{int(time.time())}"
            name = re.sub(r"[^\w.\-\u0600-\u06FF]", "_", str(name))[:120]
            target = workspace / name
            try:
                data = await file.download_as_bytearray()
            except TelegramError as exc:
                notes.append(f"⚠️ فشل تنزيل الملف: {exc}")
                return None
            target.write_bytes(bytes(data))
            return target
        photos = message.photo or []
        if photos:
            photo = photos[-1]
            try:
                tg_file = await context.bot.get_file(photo.file_id)
                data = bytes(await tg_file.download_as_bytearray())
            except TelegramError as exc:
                notes.append(f"⚠️ تعذّر تنزيل الصورة: {exc}")
                data = b""
            if data:
                data, media_type = _maybe_shrink_image(data)
                if len(data) > _MAX_IMAGE_BYTES:
                    notes.append("⚠️ الصورة أكبر من الحد المسموح (8MB)")
                else:
                    b64 = base64.b64encode(data).decode()
                    attachments.append(P.file_part(media_type, f"data:{media_type};base64,{b64}",
                                                   filename=f"photo_{int(time.time())}.jpg"))
                    target = workspace / f"photo_{int(time.time())}.jpg"
                    target.write_bytes(data)
                    notes.append(f"📎 صورة محفوظة في `{target.name}` ({_human(len(data))})")
        if message.document is not None:
            doc = message.document
            size = int(getattr(doc, "file_size", 0) or 0)
            name = str(getattr(doc, "file_name", "") or "document")
            suffix = Path(name).suffix.lower()
            if size > 20 * 1024 * 1024:
                notes.append(tr.t("document_too_big", self._lang(chat_id), limit=20))
            elif suffix in _IMAGE_SUFFIXES:
                path = await save_document(doc, "image")
                if path:
                    data = path.read_bytes()
                    data, media_type = _maybe_shrink_image(data)
                    b64 = base64.b64encode(data).decode()
                    attachments.append(P.file_part(media_type, f"data:{media_type};base64,{b64}",
                                                   filename=path.name))
                    notes.append(f"📎 صورة `{path.name}`")
            elif suffix in _TEXT_SUFFIXES or (doc.mime_type or "").startswith("text/"):
                path = await save_document(doc, "doc")
                if path:
                    try:
                        content = path.read_text(encoding="utf-8", errors="replace")
                    except OSError as exc:
                        content = ""
                        notes.append(f"⚠️ تعذّرت قراءة الملف: {exc}")
                    if content:
                        snippet = content[:_MAX_DOC_CHARS]
                        truncated = len(content) > _MAX_DOC_CHARS
                        notes.append(f"📄 ملف `{path.name}` ({_human(len(content))} حرف"
                                     f"{'، مقتطع' if truncated else ''}) — المسار الكامل متاح للأدوات")
                        attachments.append(P.text_part(
                            f"[محتوى الملف {path.name}]\n```\n{snippet}\n```"))
            else:
                path = await save_document(doc, "file")
                if path:
                    notes.append(f"📦 حُفظ `{path.name}` ({_human(size)}) في مجلد العمل — "
                                 f"يمكن معالجته بأدوات python_exec/shell_exec/file_read")
        if message.sticker is not None:
            notes.append("🎭 ملصق — لا أستطيع رؤيته، صِف ما تريده نصاً.")
        for attr in ("voice", "audio", "video"):
            media = getattr(message, attr, None)
            if media is not None:
                path = await save_document(media, attr)
                if path:
                    notes.append(f"🎞️ حُفظ `{path.name}` في مجلد العمل (لا يوجد تحويل صوتي/فيديوي مدمج).")
        return attachments, notes

    async def _send_chunks(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
        for chunk in render.split_markdown(text, render.MD_LIMIT):
            await self._send(update, context, chunk)

    async def on_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        chat = update.effective_chat
        user = update.effective_user
        if query is None or chat is None:
            return
        data = str(query.data or "")
        lang = self._lang(chat.id, user)
        is_admin = self.settings.is_admin(user.id if user else None, user.username if user else None)
        if not self.settings.is_chat_allowed(chat.id, chat.type or "private") and not is_admin:
            await self._answer_callback(update, context,
                                        tr.t("denied_chat", lang, chat_id=chat.id))
            return
        await self._answer_callback(update, context)
        if data in ("close", "noop"):
            if data == "close":
                msg = query.message
                try:
                    if msg is not None:
                        await context.bot.delete_message(chat_id=chat.id,
                                                         message_id=msg.message_id)
                    else:
                        await self._clear_markup(context, query)
                except TelegramError:
                    await self._clear_markup(context, query)
            return
        if data.startswith("menu:") or data.startswith("mem:") or data.startswith("file:"):
            await self._3mh_panel(update, context, data)
            return

        if data.startswith("mset:"):
            model_id = data[5:]
            sess = await self.store.load_session(chat.id, defaults={"model": self.settings.default_model})
            sess.model = model_id
            await self.store.save_session(sess)
            await self.pool.close(chat.id)
            info = MODELS.get(model_id)
            text = f"{tr.t('model_set', lang, model=model_id)}\n\n" + (
                MODELS.describe_model(model_id) if info else "")
            await self._edit_query(query, text, context)
            return
        if data.startswith("mpage:"):
            _, page, *rest = data.split(":", 2)
            query_text = rest[0] if rest else ""
            found = MODELS.suggest_models(query_text, limit=60)
            sess = await self.store.load_session(chat.id)
            await self._edit_markup(context, query,
                                    KB.models_keyboard(found, int(page), current=sess.model,
                                                       query=query_text,
                                                       colors=self._3mh_colors()))
            return
        if data == "mprobe":
            await self._edit_query(query, "🔎 جارٍ الفحص… (سيستغرق حتى دقيقة)", context)
            context.application.create_task(self._probe_models(update, context))
            return
        if data.startswith("ttog:"):
            name = data[5:]
            spec = self.registry.get(name)
            if spec is None:
                return
            if spec.admin_only and not is_admin:
                await self._edit_query(query, tr.t("need_admin", lang), context)
                return
            now_enabled = self.registry.is_enabled(name)
            self.registry.set_runtime_enabled(name, not now_enabled)
            state = "⚪ عُطّلت" if now_enabled else "🟢 فُعّلت"
            await self._edit_markup(context, query,
                                    KB.tools_keyboard(self.registry, 0, admin=is_admin,
                                                      colors=self._3mh_colors()))
            await self._send(update, context, f"{state} `{name}`")
            return
        if data.startswith("tpage:"):
            try:
                await self._edit_markup(context, query,
                                        KB.tools_keyboard(self.registry,
                                                          int(data.split(":")[1]), admin=is_admin,
                                                          colors=self._3mh_colors()))
            except ValueError:
                pass
            return
        if data.startswith("stg:"):
            await self._toggle_setting(update, context, data[4:])
            return
        if data.startswith("act:"):
            action = data[4:]
            if action == "regen":
                await self._edit_query(query, tr.t("regenerating", lang), context)
                context.application.create_task(self._run_turn(update, context, regenerate=True))
                return
            if action == "continue":
                context.application.create_task(
                    self._run_turn(update, context, text="أكمل من حيث توقفت بدقة."))
                return
            if action == "model":
                sess = await self.store.load_session(chat.id)
                found = MODELS.suggest_models("", limit=40)
                await self._send(update, context, "🧠 اختر نموذجاً:",
                                 reply_markup=KB.models_keyboard(found, 0, current=sess.model,
                                                                 colors=self._3mh_colors()))
                return
            if action == "tools":
                await self._send(update, context, "🔧 الأدوات:",
                                 reply_markup=KB.tools_keyboard(self.registry, 0, admin=is_admin,
                                                     colors=self._3mh_colors()))
                return
            if action == "resetq":
                await self._send(update, context, tr.t("reset_confirm", lang),
                                 reply_markup=KB.confirm_keyboard("reset", self._3mh_colors()))
                return
        if data.startswith("yes:") or data.startswith("no:"):
            approved = data.startswith("yes:")
            action = data.split(":", 1)[1]
            await self._clear_markup(context, query)
            if not approved:
                await self._send(update, context, "↩️ أُلغيت العملية.")
                return
            if action == "reset":
                context.args = ["force"]
                await self.cmd_reset(update, context)
            elif action == "clearfiles":
                context.args = ["force"]
                await self.cmd_clearfiles(update, context)
            return

    async def _3mh_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                         data: str) -> None:
        _3mh_key = data.split(":", 1)[1]
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        colors = self._3mh_colors()
        context.args = []
        if _3mh_key == "home":
            await self._send(update, context, tr.t("menu_header", lang, bot_name=self.bot_name),
                             reply_markup=KB.main_menu_keyboard(self._3mh_brand(), colors))
        elif _3mh_key in ("model", "models"):
            await self.cmd_model(update, context)
        elif _3mh_key == "tools":
            await self.cmd_tools(update, context)
        elif _3mh_key == "files":
            await self.cmd_files(update, context)
            await self._send(update, context, "📂 *إجراءات الملفات*",
                             reply_markup=KB.files_keyboard(colors))
        elif _3mh_key == "memory":
            await self._send(update, context, "💾 *الذاكرة والملاحظات*",
                             reply_markup=KB.memory_keyboard(colors))
        elif _3mh_key in ("notes",):
            await self.cmd_notes(update, context)
        elif _3mh_key == "reminders":
            await self.cmd_reminders(update, context)
        elif _3mh_key == "compact":
            await self.cmd_compact(update, context)
        elif _3mh_key == "history":
            await self.cmd_history(update, context)
        elif _3mh_key == "export":
            await self.cmd_export(update, context)
        elif _3mh_key == "usage":
            await self.cmd_usage(update, context)
        elif _3mh_key == "settings":
            await self.cmd_settings(update, context)
        elif _3mh_key == "status":
            await self.cmd_status(update, context)
        elif _3mh_key == "help":
            await self.cmd_help(update, context)
        elif _3mh_key == "resetq":
            await self._send(update, context, tr.t("reset_confirm", lang),
                             reply_markup=KB.confirm_keyboard("reset", colors))
        elif _3mh_key == "clearq":
            await self._send(update, context,
                             "⚠️ سيتم حذف *كل* ملفات مجلد العمل لهذه المحادثة. متأكد؟",
                             reply_markup=KB.confirm_keyboard("clearfiles", colors))
        elif _3mh_key == "list":
            await self.cmd_files(update, context)
        elif _3mh_key == "stop":
            await self.cmd_stop(update, context)

    async def _toggle_setting(self, update: Update, context: ContextTypes.DEFAULT_TYPE, key: str) -> None:
        chat_id = update.effective_chat.id
        lang = self._lang(chat_id, update.effective_user)
        sess = await self.store.load_session(chat_id, defaults={"model": self.settings.default_model})
        ui = await self._load_ui(chat_id)
        if key == "think":
            sess.show_reasoning = not sess.show_reasoning
            ui["reasoning"] = sess.show_reasoning
            await self.store.save_session(sess)
        elif key == "trace":
            ui["trace"] = not bool(ui.get("trace", True))
        elif key == "usage":
            ui["usage"] = not bool(ui.get("usage", True))
        elif key == "stream":
            ui["stream"] = not bool(ui.get("stream", True))
        elif key == "temp":
            sess.temperature = 0.3 if sess.temperature >= 1.5 else (
                0.7 if sess.temperature >= 1.0 else (1.0 if sess.temperature >= 0.7 else 1.5))
            await self.store.save_session(sess)
        elif key == "menu":
            self.settings.menu_buttons = not bool(self.settings.menu_buttons)
            if self.settings.menu_buttons:
                await self._attach_reply_keyboard(update, context)
            else:
                try:
                    await context.bot.send_message(chat_id=chat_id, text="🎛️",
                                                   reply_markup=ReplyKeyboardRemove())
                except TelegramError:
                    pass
            ui["menu"] = self.settings.menu_buttons
            await self.store.kv_set("menu_buttons", self.settings.menu_buttons)
            return
        elif key == "model":
            found = MODELS.suggest_models("", limit=40)
            await self._send(update, context, "🧠 اختر نموذجاً:",
                             reply_markup=KB.models_keyboard(found, 0, current=sess.model))
            return
        elif key == "reset":
            await self._send(update, context, tr.t("reset_confirm", lang),
                             reply_markup=KB.confirm_keyboard("reset", self._3mh_colors()))
            return
        self._ui[chat_id] = ui
        await self.store.kv_set(f"ui:{chat_id}", ui)
        query = update.callback_query
        if query is not None:
            await self._edit_markup(context, query,
                                    KB.settings_keyboard(sess, ui, self._3mh_colors()))

    async def _edit_query(self, query: Any, text: str,
                          context: Optional[ContextTypes.DEFAULT_TYPE] = None) -> None:
        body = render.md_to_html(text)[:4096]
        bot = context.bot if context is not None else None
        message = getattr(query, "message", None)
        try:
            if bot is not None and message is not None:
                await bot.edit_message_text(
                    chat_id=message.chat_id, message_id=message.message_id,
                    text=body, parse_mode=ParseMode.HTML, **_no_preview_kwargs())
            else:
                await query.edit_message_text(body, parse_mode=ParseMode.HTML,
                                              **_no_preview_kwargs())
        except BadRequest as exc:
            if "not modified" not in str(exc).lower():
                log.debug("تعذّر تعديل رسالة اللوحة: %s", exc)
        except TelegramError as exc:
            log.debug("تعذّر تعديل رسالة اللوحة: %s", exc)

    async def _edit_markup(self, context: ContextTypes.DEFAULT_TYPE, query: Any,
                           markup: Optional[InlineKeyboardMarkup]) -> None:
        message = getattr(query, "message", None)
        if message is None:
            return
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=message.chat_id, message_id=message.message_id, reply_markup=markup)
        except TelegramError as exc:
            log.debug("تعذّر تعديل أزرار اللوحة: %s", exc)

    async def _clear_markup(self, context: ContextTypes.DEFAULT_TYPE, query: Any) -> None:
        await self._edit_markup(context, query, None)

    async def on_error(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        exc = context.error
        log.error("خطأ في المعالج: %s", exc, exc_info=exc)
        if isinstance(exc, TimedOut):
            return
        chat = getattr(update, "effective_chat", None)
        if chat is None:
            return
        lang = self._lang(chat.id, getattr(update, "effective_user", None))
        text = tr.t("error_generic", lang, error=f"{type(exc).__name__}: {exc}"[:400])
        try:
            await context.bot.send_message(chat_id=chat.id, text=render.md_to_html(text),
                                           parse_mode=ParseMode.HTML, **_no_preview_kwargs())
        except TelegramError:
            pass


async def _reminder_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.job.data if context.job else {}
    handlers: BotHandlers = context.application.bot_data.get("handlers")
    chat_id = int(data.get("chat_id") or 0)
    text = str(data.get("text") or "")
    rid = int(data.get("id") or 0)
    if not chat_id or not text:
        return
    lang = handlers._lang(chat_id) if handlers is not None else "ar"
    body = render.md_to_html(tr.t("reminder_fire", lang, text=text))
    try:
        await context.bot.send_message(chat_id=chat_id, text=body[:4096],
                                       parse_mode=ParseMode.HTML, **_no_preview_kwargs())
    except TelegramError as exc:
        log.warning("تعذّر إرسال التذكير: %s", exc)
    if handlers is not None and rid:
        try:
            await handlers.store.complete_reminder(rid)
        except Exception:
            pass


def _probe_report(results: Dict[str, Tuple[bool, str, float]], lang: str) -> str:
    lines: List[str] = []
    for model, (ok, message, elapsed) in sorted(results.items(),
                                                key=lambda kv: (not kv[1][0], kv[0])):
        mark = "✅" if ok else "❌"
        short = model.split("/")[-1]
        detail = (message[:70] if not ok else f"{elapsed:.1f}ث")
        lines.append(f"{mark} `{short}` — {detail}")
    return "\n".join(lines) if lines else "(لا نتائج)"


def _human(size: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}GB"


def _human_duration(seconds: float) -> str:
    seconds = int(seconds)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days:
        return f"{days}ي {hours}س {minutes}د"
    if hours:
        return f"{hours}س {minutes}د"
    if minutes:
        return f"{minutes}د {secs}ث"
    return f"{secs}ث"


def _maybe_shrink_image(data: bytes) -> Tuple[bytes, str]:
    media_type = "image/jpeg"
    lowered = data[:12].lower()
    if lowered.startswith(b"\x89png"):
        media_type = "image/png"
    elif lowered.startswith(b"gif8"):
        media_type = "image/gif"
    elif lowered.startswith(b"riff") and b"webp" in data[:16]:
        media_type = "image/webp"
    try:
        from PIL import Image
        if len(data) <= 1_200_000:
            return data, media_type
        image = Image.open(io.BytesIO(data))
        image = image.convert("RGB")
        image.thumbnail((1568, 1568))
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=88, optimize=True)
        out = buf.getvalue()
        if len(out) < len(data):
            return out, "image/jpeg"
    except Exception:
        pass
    return data, media_type
