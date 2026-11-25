# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.constants import KeyboardButtonStyle
from .. import models as MODELS
from ..tools import ToolRegistry
PER_PAGE_MODELS = 8
PER_PAGE_TOOLS = 8
BLUE = KeyboardButtonStyle.PRIMARY
GREEN = KeyboardButtonStyle.SUCCESS
RED = KeyboardButtonStyle.DANGER
MENU_LABELS: Dict[str, str] = {
    "model": "🧠 النموذج",
    "tools": "🔧 الأدوات",
    "files": "📂 الملفات",
    "memory": "💾 الذاكرة",
    "usage": "📊 الإحصاءات",
    "settings": "⚙️ الإعدادات",
    "stop": "⛔ إيقاف",
    "new": "🧹 محادثة جديدة",
    "help": "❓ المساعدة",
    "status": "🩺 الحالة",
}
MENU_ORDER = ["model", "tools", "files", "memory", "usage", "settings", "stop", "new"]
MENU_STYLE = {
    "model": BLUE, "tools": GREEN, "files": BLUE, "memory": GREEN,
    "usage": BLUE, "settings": BLUE, "stop": RED, "new": RED,
}


def _3mh_btn(text: str, callback: Optional[str] = None, url: Optional[str] = None,
             style: Optional[Any] = None, colors: bool = True) -> InlineKeyboardButton:
    _3mh_kw: Dict[str, Any] = {"text": text}
    if callback is not None:
        _3mh_kw["callback_data"] = callback
    elif url is not None:
        _3mh_kw["url"] = url
    if colors and style is not None:
        _3mh_kw["style"] = style
    return InlineKeyboardButton(**_3mh_kw)


def _3mh_kbtn(text: str, style: Optional[Any] = None, colors: bool = True) -> KeyboardButton:
    _3mh_kw: Dict[str, Any] = {"text": text}
    if colors and style is not None:
        _3mh_kw["style"] = style
    return KeyboardButton(**_3mh_kw)


def main_reply_keyboard(colors: bool = True, compact: bool = False) -> ReplyKeyboardMarkup:
    _3mh_keys = MENU_ORDER if not compact else MENU_ORDER[:6]
    _3mh_rows = [[_3mh_kbtn(MENU_LABELS[k], MENU_STYLE[k], colors) for k in _3mh_keys[i:i + 2]]
                 for i in range(0, len(_3mh_keys), 2)]
    return ReplyKeyboardMarkup(_3mh_rows, resize_keyboard=True, is_persistent=True,
                               input_field_placeholder="اكتب طلبك أو اختر من الأزرار…")


def main_menu_keyboard(brand: Dict[str, str], colors: bool = True) -> InlineKeyboardMarkup:
    _3mh_rows: List[List[InlineKeyboardButton]] = [
        [_3mh_btn("🧠 النموذج", "menu:model", style=BLUE, colors=colors),
         _3mh_btn("🔧 الأدوات", "menu:tools", style=GREEN, colors=colors)],
        [_3mh_btn("📂 الملفات", "menu:files", style=BLUE, colors=colors),
         _3mh_btn("💾 الذاكرة", "menu:memory", style=GREEN, colors=colors)],
        [_3mh_btn("📊 الإحصاءات", "menu:usage", style=BLUE, colors=colors),
         _3mh_btn("⚙️ الإعدادات", "menu:settings", style=GREEN, colors=colors)],
        [_3mh_btn("🩺 الحالة", "menu:status", style=BLUE, colors=colors),
         _3mh_btn("❓ المساعدة", "menu:help", style=GREEN, colors=colors)],
        [_3mh_btn("📢 القناة", url=brand.get("channel_url", "t.me/bshshshkk"),
                  style=BLUE, colors=colors),
         _3mh_btn("🆘 الدعم", url=brand.get("support_url", "t.me/j49_c"),
                  style=GREEN, colors=colors)],
        [_3mh_btn("🌐 3MH TECHNOLOGIES", url=brand.get("site", "http://3mh.pages.dev"),
                  style=BLUE, colors=colors),
         _3mh_btn("⚫ إخفاء", "close", style=RED, colors=colors)],
    ]
    return InlineKeyboardMarkup(_3mh_rows)


def models_keyboard(models: Sequence[MODELS.ModelInfo], page: int = 0, current: str = "",
                    query: str = "", colors: bool = True) -> InlineKeyboardMarkup:
    _3mh_pages = max(1, -(-len(models) // PER_PAGE_MODELS))
    page = max(0, min(page, _3mh_pages - 1))
    _3mh_rows: List[List[InlineKeyboardButton]] = []
    for _3mh_info in models[page * PER_PAGE_MODELS:(page + 1) * PER_PAGE_MODELS]:
        _3mh_sel = _3mh_info.id == current
        _3mh_style = GREEN if _3mh_sel or _3mh_info.verified else BLUE
        if _3mh_info.gated:
            _3mh_style = RED
        _3mh_mark = "🟢" if _3mh_sel else ("✅" if _3mh_info.verified else ("🔒" if _3mh_info.gated else "🔵"))
        _3mh_rows.append([_3mh_btn(f"{_3mh_mark} {_3mh_info.label}", f"mset:{_3mh_info.id}",
                                   style=_3mh_style, colors=colors)])
    _3mh_rows.append(_3mh_nav(page, _3mh_pages, "mpage", query, colors))
    _3mh_rows.append([_3mh_btn("🔎 فحص التوفر", "mprobe", style=BLUE, colors=colors),
                      _3mh_btn("🏠 القائمة", "menu:home", style=GREEN, colors=colors),
                      _3mh_btn("⚫", "close", style=RED, colors=colors)])
    return InlineKeyboardMarkup(_3mh_rows)


def tools_keyboard(registry: ToolRegistry, page: int = 0, admin: bool = True,
                   colors: bool = True) -> InlineKeyboardMarkup:
    _3mh_specs = sorted(registry.all, key=lambda s: (s.category, s.name))
    _3mh_pages = max(1, -(-len(_3mh_specs) // PER_PAGE_TOOLS))
    page = max(0, min(page, _3mh_pages - 1))
    _3mh_rows: List[List[InlineKeyboardButton]] = []
    for _3mh_spec in _3mh_specs[page * PER_PAGE_TOOLS:(page + 1) * PER_PAGE_TOOLS]:
        _3mh_on = registry.is_enabled(_3mh_spec.name)
        _3mh_lock = "🔐" if _3mh_spec.admin_only else ""
        _3mh_rows.append([_3mh_btn(
            f"{'🟢' if _3mh_on else '🔴'}{_3mh_lock} {_3mh_spec.name}",
            f"ttog:{_3mh_spec.name}", style=GREEN if _3mh_on else RED, colors=colors)])
    _3mh_rows.append(_3mh_nav(page, _3mh_pages, "tpage", "", colors))
    return InlineKeyboardMarkup(_3mh_rows)


def _3mh_nav(page: int, pages: int, prefix: str, query: str = "",
             colors: bool = True) -> List[InlineKeyboardButton]:
    if pages <= 1:
        return [_3mh_btn("🏠 القائمة", "menu:home", style=GREEN, colors=colors),
                _3mh_btn("⚫", "close", style=RED, colors=colors)]
    _3mh_row: List[InlineKeyboardButton] = []
    if page > 0:
        _3mh_row.append(_3mh_btn("◀ السابق", f"{prefix}:{page - 1}:{query}", style=BLUE, colors=colors))
    _3mh_row.append(_3mh_btn(f"📄 {page + 1}/{pages}", "noop", colors=False))
    if page < pages - 1:
        _3mh_row.append(_3mh_btn("التالي ▶", f"{prefix}:{page + 1}:{query}", style=BLUE, colors=colors))
    _3mh_row.append(_3mh_btn("⚫", "close", style=RED, colors=colors))
    return _3mh_row


def settings_keyboard(session: Any, flags: Dict[str, bool], colors: bool = True) -> InlineKeyboardMarkup:
    def _3mh_sw(on: bool) -> Any:
        return GREEN if on else RED
    return InlineKeyboardMarkup([
        [_3mh_btn(f"{'🟢' if session.show_reasoning else '🔴'} إظهار التفكير", "stg:think",
                  style=_3mh_sw(session.show_reasoning), colors=colors),
         _3mh_btn(f"{'🟢' if flags.get('trace', True) else '🔴'} سجل الأدوات", "stg:trace",
                  style=_3mh_sw(flags.get("trace", True)), colors=colors)],
        [_3mh_btn(f"{'🟢' if flags.get('usage', True) else '🔴'} الإحصاءات", "stg:usage",
                  style=_3mh_sw(flags.get("usage", True)), colors=colors),
         _3mh_btn(f"{'🟢' if flags.get('stream', True) else '🔴'} البث الحي", "stg:stream",
                  style=_3mh_sw(flags.get("stream", True)), colors=colors)],
        [_3mh_btn(f"{'🟢' if flags.get('menu', True) else '🔴'} أزرار القائمة", "stg:menu",
                  style=_3mh_sw(flags.get("menu", True)), colors=colors),
         _3mh_btn(f"🌡️ {session.temperature}", "stg:temp", style=BLUE, colors=colors)],
        [_3mh_btn("🧠 النموذج", "stg:model", style=BLUE, colors=colors),
         _3mh_btn("🧹 مسح السجل", "stg:reset", style=RED, colors=colors)],
        [_3mh_btn("🏠 القائمة", "menu:home", style=GREEN, colors=colors),
         _3mh_btn("⚫ إغلاق", "close", style=RED, colors=colors)],
    ])


def memory_keyboard(colors: bool = True) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [_3mh_btn("💾 الملاحظات", "mem:notes", style=GREEN, colors=colors),
         _3mh_btn("⏰ التذكيرات", "mem:reminders", style=BLUE, colors=colors)],
        [_3mh_btn("🗜️ ضغط الذاكرة", "mem:compact", style=BLUE, colors=colors),
         _3mh_btn("🕘 السجل", "mem:history", style=GREEN, colors=colors)],
        [_3mh_btn("📤 تصدير", "mem:export", style=BLUE, colors=colors),
         _3mh_btn("🧹 مسح", "mem:resetq", style=RED, colors=colors)],
        [_3mh_btn("🏠 القائمة", "menu:home", style=GREEN, colors=colors),
         _3mh_btn("⚫ إغلاق", "close", style=RED, colors=colors)],
    ])


def files_keyboard(colors: bool = True) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [_3mh_btn("📂 عرض الملفات", "file:list", style=GREEN, colors=colors),
         _3mh_btn("🗑️ إفراغ المجلد", "file:clearq", style=RED, colors=colors)],
        [_3mh_btn("🏠 القائمة", "menu:home", style=BLUE, colors=colors),
         _3mh_btn("⚫ إغلاق", "close", style=RED, colors=colors)],
    ])


def confirm_keyboard(action: str, colors: bool = True, yes: str = "🟢 نعم",
                     no: str = "🔴 لا") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [_3mh_btn(yes, f"yes:{action}", style=GREEN, colors=colors),
         _3mh_btn(no, f"no:{action}", style=RED, colors=colors)],
    ])


def answer_keyboard(colors: bool = True, menu: bool = True) -> InlineKeyboardMarkup:
    _3mh_rows = [[
        _3mh_btn("🔄 إعادة", "act:regen", style=BLUE, colors=colors),
        _3mh_btn("⏭️ أكمل", "act:continue", style=GREEN, colors=colors),
        _3mh_btn("🧹 جديد", "act:resetq", style=RED, colors=colors),
    ]]
    if menu:
        _3mh_rows.append([
            _3mh_btn("🧠 نموذج", "act:model", style=BLUE, colors=colors),
            _3mh_btn("🔧 أدوات", "act:tools", style=GREEN, colors=colors),
            _3mh_btn("🏠 القائمة", "menu:home", style=BLUE, colors=colors),
        ])
    return InlineKeyboardMarkup(_3mh_rows)


def error_keyboard(colors: bool = True) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [_3mh_btn("🔄 إعادة المحاولة", "act:regen", style=GREEN, colors=colors),
         _3mh_btn("🧠 تغيير النموذج", "act:model", style=BLUE, colors=colors)],
        [_3mh_btn("🩺 الحالة", "menu:status", style=BLUE, colors=colors),
         _3mh_btn("🆘 الدعم", url="t.me/j49_c", style=GREEN, colors=colors)],
    ])


def brand_keyboard(colors: bool = True) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [_3mh_btn("📢 t.me/bshshshkk", url="t.me/bshshshkk", style=BLUE, colors=colors),
         _3mh_btn("🆘 t.me/j49_c", url="t.me/j49_c", style=GREEN, colors=colors)],
        [_3mh_btn("🌐 3mh.pages.dev", url="http://3mh.pages.dev", style=BLUE, colors=colors),
         _3mh_btn("⚫ إغلاق", "close", style=RED, colors=colors)],
    ])


def close_keyboard(colors: bool = True) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[_3mh_btn("⚫ إغلاق", "close", style=RED, colors=colors)]])
