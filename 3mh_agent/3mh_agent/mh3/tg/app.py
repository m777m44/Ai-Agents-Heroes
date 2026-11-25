# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import asyncio
import logging
import logging.handlers
import time
from pathlib import Path
from typing import Any, Dict, Optional
from telegram import BotCommand, BotCommandScopeDefault, Update
from telegram.error import TelegramError
from telegram.ext import Application, ContextTypes
from .. import __version__ as BOT_VERSION
from ..agent import AgentCore
from ..backend import ConnectionPool
from ..config import Settings
from ..store import Store
from ..tools import build_registry
from .handlers import BotHandlers, _reminder_job
from .ui import configure as configure_ui
log = logging.getLogger("mh3.app")
BOT_COMMANDS = [
    ("help", "دليل الأوامر / Command guide"),
    ("model", "اختيار النموذج / Pick model"),
    ("models", "قائمة النماذج وفحصها / Model list"),
    ("tools", "الأدوات الداخلية وتفعيلها / Internal tools"),
    ("status", "حالة البوت والاتصال / Bot status"),
    ("usage", "إحصاءات التوكنز والتكلفة / Usage stats"),
    ("reset", "مسح المحادثة / Clear history"),
    ("compact", "ضغط الذاكرة / Compress memory"),
    ("history", "عرض السجل / Show history"),
    ("export", "تصدير الجلسة / Export session"),
    ("files", "ملفات مجلد العمل / Workspace files"),
    ("notes", "الملاحظات المحفوظة / Saved notes"),
    ("note", "حفظ ملاحظة / Save a note"),
    ("reminders", "التذكيرات / Reminders"),
    ("settings", "لوحة الإعدادات / Settings panel"),
    ("stop", "إيقاف التوليد / Stop generation"),
    ("retry", "إعادة التوليد / Regenerate"),
    ("think", "إظهار التفكير / Toggle reasoning"),
    ("temp", "درجة العشوائية / Temperature"),
    ("system", "برومبت النظام / System prompt"),
    ("ping", "زمن الاستجابة / Latency"),
    ("id", "معرّفاتك / Your ids"),
]


def setup_logging(settings: Settings) -> None:
    level = getattr(logging, str(settings.log_level).upper(), logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s", datefmt="%H:%M:%S")
    root = logging.getLogger()
    root.setLevel(level)
    for handler in list(root.handlers):
        root.removeHandler(handler)
    stream = logging.StreamHandler()
    stream.setFormatter(fmt)
    root.addHandler(stream)
    if settings.log_file:
        try:
            Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                settings.log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
            file_handler.setFormatter(fmt)
            root.addHandler(file_handler)
        except OSError as exc:
            log.warning("تعذّر إنشاء ملف السجل: %s", exc)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)


async def _post_init(app: Application) -> None:
    settings: Settings = app.bot_data["settings"]
    configure_ui(settings.ui_language)
    store = Store(settings.db_path)
    await store.init()
    registry = build_registry(settings)
    pool = ConnectionPool(settings)
    agent = AgentCore(settings, store, registry, pool, bot_name=app.bot_data.get("bot_name", "3mh agent"))
    handlers = BotHandlers(settings, store, registry, pool, agent,
                           bot_name=app.bot_data.get("bot_name", "3mh agent"))
    app.bot_data.update({
        "store": store, "registry": registry, "pool": pool,
        "agent": agent, "handlers": handlers, "started_at": time.time(),
    })
    handlers.register(app)
    saved_steps = await store.kv_get("max_steps", None)
    if isinstance(saved_steps, int) and 1 <= saved_steps <= 40:
        settings.max_steps = saved_steps
    saved_menu = await store.kv_get("menu_buttons", None)
    if isinstance(saved_menu, bool):
        settings.menu_buttons = saved_menu
    try:
        await app.bot.set_my_commands(
            [BotCommand(name, desc) for name, desc in BOT_COMMANDS],
            scope=BotCommandScopeDefault())
    except TelegramError as exc:
        log.warning("تعذّر ضبط قائمة الأوامر: %s", exc)
    if app.job_queue is not None:
        pending = await store.pending_reminders()
        restored = 0
        for row in pending:
            delay = float(row["due_ts"]) - time.time()
            if delay <= 0:
                delay = 2.0
            app.job_queue.run_once(
                _reminder_job, when=delay,
                data={"id": row["id"], "chat_id": row["chat_id"], "text": row["text"]})
            restored += 1
        if restored:
            log.info("أُعيدت جدولة %d تذكيراً", restored)
    if app.job_queue is not None:
        app.job_queue.run_repeating(_reap_job, interval=300, first=120, name="reap-connections")
    me = await app.bot.get_me()
    log.info("✅ البوت جاهز: @%s (id=%s) — الإصدار %s", me.username, me.id, BOT_VERSION)
    log.info("   النموذج الافتراضي: %s | الأدوات: %d | المشرفون: %d",
             settings.default_model, len(registry.all), len(settings.admin_ids))
    if not settings.admin_ids and settings.access_mode == "admins":
        log.warning("⚠️  ADMIN_IDS فارغ — لن يستطيع أحد استخدام البوت. أرسل /id للبوت ثم أضف رقمك.")


async def _reap_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    pool: Optional[ConnectionPool] = context.application.bot_data.get("pool")
    if pool is not None:
        try:
            closed = await pool.reap_idle()
            if closed:
                log.debug("أُغلقت %d اتصالاً خاملًا", closed)
        except Exception:
            log.exception("فشل تنظيف الاتصالات الخاملة")


async def _post_shutdown(app: Application) -> None:
    pool: Optional[ConnectionPool] = app.bot_data.get("pool")
    store: Optional[Store] = app.bot_data.get("store")
    if pool is not None:
        try:
            await pool.close_all()
        except Exception:
            log.exception("فشل إغلاق الاتصالات")
    if store is not None:
        try:
            await store.close()
        except Exception:
            log.exception("فشل إغلاق قاعدة البيانات")
    log.info("👋 تم الإيقاف النظيف")


def build_application(settings: Settings, bot_name: str = "3mh agent") -> Application:
    setup_logging(settings)
    builder = Application.builder().token(settings.bot_token)
    builder = (
        builder
        .concurrent_updates(True)
        .read_timeout(60.0)
        .write_timeout(60.0)
        .connect_timeout(25.0)
        .pool_timeout(25.0)
        .post_init(_post_init)
        .post_shutdown(_post_shutdown)
    )
    if settings.proxy_url:
        if hasattr(builder, "proxy_url"):
            try:
                builder = builder.proxy_url(settings.proxy_url)
            except Exception:
                log.warning("تعذّر ضبط البروكسي — سيتم تجاهله")
        else:
            try:
                from telegram.request import HTTPXRequest
                builder = builder.request(
                    HTTPXRequest(proxy_url=settings.proxy_url, read_timeout=60, write_timeout=60))
                builder = builder.get_updates_request(
                    HTTPXRequest(proxy_url=settings.proxy_url, read_timeout=60, write_timeout=60))
            except Exception:
                log.warning("تعذّر ضبط البروكسي — سيتم تجاهله")
    app = builder.build()
    app.bot_data["settings"] = settings
    app.bot_data["bot_name"] = bot_name
    return app


def run(settings: Optional[Settings] = None, bot_name: str = "3mh agent") -> None:
    settings = settings or Settings.from_env()
    app = build_application(settings, bot_name=bot_name)
    if settings.webhook_url:
        log.info("تشغيل وضع Webhook على المنفذ %s", settings.webhook_port)
        app.run_webhook(
            listen="0.0.0.0",
            port=settings.webhook_port,
            url_path=settings.webhook_secret or "webhook",
            webhook_url=settings.webhook_url.rstrip("/") + "/" + (settings.webhook_secret or "webhook"),
            secret_token=settings.webhook_secret or None,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        log.info("تشغيل وضع Long Polling…")
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False,
        )
