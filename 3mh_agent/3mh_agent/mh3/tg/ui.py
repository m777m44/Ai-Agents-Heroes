# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
from typing import Any, Dict
AR: Dict[str, str] = {
    "start_welcome": (
        "🤖 *{bot_name}*\n"
        "وكيل ذكاء اصطناعي كامل داخل تليجرام — من تطوير *{company}*\n\n"
        "يعمل على نماذج Cloudflare Workers AI، ومعه جهاز داخلي: "
        "{tools} أداة، تنفيذ كود، ملفات، بحث ويب، وذاكرة دائمة.\n\n"
        "اكتب طلبك وسيتصرف الوكيل بنفسه، أو استخدم الأزرار الملوّنة بالأسفل.\n\n"
        "👤 الصلاحية: *{role}*\n"
        "🧠 النموذج: `{model}`\n\n"
        "📢 القناة: {channel}\n"
        "🆘 الدعم: {support}\n"
        "🌐 الموقع: {site}"
    ),
    "menu_header": (
        "🎛️ *لوحة التحكم* — {bot_name}\n"
        "اختر من الأزرار الملوّنة:\n\n"
        "🟢 أخضر = تفعيل/تشغيل • 🔵 أزرق = عرض/تنقّل • 🔴 أحمر = إيقاف/حذف"
    ),
    "menu_hidden": "أُخفيت اللوحة. أرسل /menu لإعادتها.",
    "menu_shown": "🎛️ هذه لوحات التحكم. أزرار الأسفل تعمل في أي وقت.",
    "denied": (
        "⛔ هذا البوت مقصور على المشرفين.\n"
        "معرّفك: `{user_id}`\n"
        "للتفعيل أضف هذا الرقم إلى `ADMIN_IDS` في ملف `.env` ثم أعد التشغيل."
    ),
    "denied_chat": "⛔ هذه المحادثة غير مصرّح لها باستخدام البوت (chat_id = `{chat_id}`).",
    "busy": "⏳ يوجد طلب قيد التنفيذ في هذه المحادثة.\nاستخدم /stop لإيقافه ثم أعد المحاولة.",
    "rate_limited": "⚠️ تجاوزت حد الطلبات ({limit}/دقيقة). انتظر {wait} ثانية.",
    "thinking": "🤔 أفكّر…",
    "working": "⚙️ جارٍ العمل… (الخطوة {step}/{max})",
    "tool_start": "🔧 `{tool}`",
    "tool_done": "✅ `{tool}` — {ms}م.ث",
    "tool_fail": "❌ `{tool}` — {error}",
    "fallback": "🔁 النموذج `{model}` تعذّر ({error}) — التبديل إلى `{next_model}`",
    "retrying": "⏳ إعادة المحاولة بعد {wait}ث ({error})",
    "subagent": "🧩 تفويض نموذج فرعي: `{model}`",
    "compacting": "🗜️ ضغط ذاكرة المحادثة…",
    "cancelled": "⏹️ أُلغي التوليد بطلبك.",
    "error_generic": "⚠️ حدث خطأ:\n`{error}`",
    "error_hint": "💡 جرّب: /status للتحقق، /model للتبديل، /reset لمسح السياق.",
    "empty_answer": "(لم يُرجع النموذج نصاً — جرّب /retry أو غيّر النموذج بـ /model)",
    "model_current": "🧠 النموذج الحالي: `{model}`\n{info}",
    "model_set": "✅ تم ضبط النموذج إلى `{model}`",
    "model_unknown": (
        "❓ لم أتعرّف على `{query}`.\n"
        "استخدم /models لعرض القائمة، أو /model للاختيار بالأزرار."
    ),
    "models_header": "📚 *النماذج المتاحة* (صفحة {page}/{pages}) — اضغط للاختيار:",
    "models_refresh_done": "🔎 نتيجة فحص {count} نموذجاً:\n✅ {ok} متاح • ❌ {fail} غير متاح",
    "reset_done": "🧹 تم مسح سجل المحادثة{extra}.",
    "reset_confirm": "هل تريد فعلاً مسح سجل المحادثة والذاكرة المؤقتة؟",
    "history_empty": "لا يوجد سجل بعد.",
    "usage_header": "📊 *إحصاءات آخر {days} يوم*",
    "tools_header": "🔧 *الأدوات الداخلية* ({enabled}/{total} مفعّلة) — اضغط للتبديل:",
    "note_saved": "📝 حُفظت الملاحظة (#{id}).",
    "notes_empty": "لا توجد ملاحظات محفوظة.",
    "reminder_set": "⏰ تذكير #{id} بعد {when}:\n{text}",
    "reminder_fire": "⏰ *تذكير* {text}",
    "files_empty": "📂 مجلد العمل فارغ.",
    "settings_header": "⚙️ *الإعدادات*",
    "lang_set": "🌐 لغة الواجهة: {lang}",
    "think_on": "🧠 عرض تفكير النموذج: *مفعّل*",
    "think_off": "🧠 عرض تفكير النموذج: *معطّل*",
    "temp_set": "🌡️ درجة العشوائية: `{value}`",
    "invalid_number": "❗ قيمة رقمية غير صالحة: `{value}`",
    "pong": "🏓 زمن الاستجابة: {ms} م.ث",
    "status_header": "🩺 *حالة البوت*",
    "confirm_yes": "✅ نعم",
    "confirm_no": "❌ لا",
    "back": "↩️ رجوع",
    "next": "التالي ▶",
    "prev": "◀ السابق",
    "close": "✖️ إغلاق",
    "need_admin": "🔐 هذا الإجراء للمشرفين فقط.",
    "vision_switch": "🖼️ أرسلت صورة والنموذج الحالي لا يدعم الرؤية — التبديل تلقائياً إلى `{model}`.",
    "document_too_big": "⚠️ الملف أكبر من {limit}MB — تم تجاهله.",
    "document_unsupported": "⚠️ نوع الملف غير مدعوم للقراءة كنص: `{name}`",
    "group_notice": "👥 في المجموعات: أردّ على الرسائل التي تذكرني أو تردّ عليّ، أو استخدم الأوامر.",
    "max_steps_note": "⚠️ توقفت عند حد الخطوات ({steps}). استخدم /maxsteps لرفعه.",
    "artifacts": "📎 مرفقات:",
    "regenerating": "🔄 إعادة التوليد…",
    "workspace_cleared": "🗑️ تم إفراغ مجلد العمل.",
    "exported": "📤 تم تصدير الجلسة.",
    "about_brand": (
        "🤖 *{bot_name}* `{version}`\n\n"
        "وكيل ذكاء اصطناعي كامل داخل تليجرام يعمل على نماذج Cloudflare Workers AI.\n\n"
        "*القدرات*\n"
        "• حلقة وكيل متعددة الخطوات مع استدعاء أدوات أصلي\n"
        "• تنفيذ Python و shell في صندوق معزول\n"
        "• ملفات، بحث ويب، جلب صفحات، ويكيبيديا\n"
        "• ذاكرة دائمة + ضغط تلقائي للسياق\n"
        "• بث حي، أزرار ملوّنة، وتبديل تلقائي للنماذج\n"
        "• تذكيرات، تصدير جلسات، وإحصاءات توكنز/تكلفة\n\n"
        "*{company}*\n"
        "📢 {channel} • 🆘 {support}\n"
        "🌐 {site}"
    ),
}
EN: Dict[str, str] = {
    "start_welcome": (
        "🤖 *{bot_name}*\n"
        "A full AI agent inside Telegram — built by *{company}*\n\n"
        "Powered by Cloudflare Workers AI with an internal machine: {tools} tools, "
        "code execution, files, web search and persistent memory.\n\n"
        "Type a request or use the colored buttons below.\n\n"
        "👤 Role: *{role}*\n🧠 Model: `{model}`\n\n"
        "📢 Channel: {channel}\n🆘 Support: {support}\n🌐 Site: {site}"
    ),
    "menu_header": (
        "🎛️ *Control panel* — {bot_name}\n"
        "Pick from the colored buttons:\n\n"
        "🟢 green = enable/run • 🔵 blue = view/navigate • 🔴 red = stop/delete"
    ),
    "menu_hidden": "Panel hidden. Send /menu to bring it back.",
    "menu_shown": "🎛️ Control panel ready. The bottom buttons work anytime.",
    "denied": (
        "⛔ This bot is restricted to administrators.\nYour id: `{user_id}`\n"
        "Add it to `ADMIN_IDS` in `.env` and restart."
    ),
    "denied_chat": "⛔ This chat is not authorised (chat_id = `{chat_id}`).",
    "busy": "⏳ A request is already running here. Use /stop then retry.",
    "rate_limited": "⚠️ Rate limit reached ({limit}/min). Wait {wait}s.",
    "thinking": "🤔 Thinking…",
    "working": "⚙️ Working… (step {step}/{max})",
    "tool_start": "🔧 `{tool}`",
    "tool_done": "✅ `{tool}` — {ms}ms",
    "tool_fail": "❌ `{tool}` — {error}",
    "fallback": "🔁 `{model}` failed ({error}) → switching to `{next_model}`",
    "retrying": "⏳ Retrying in {wait}s ({error})",
    "subagent": "🧩 Delegating to sub-model: `{model}`",
    "compacting": "🗜️ Compressing conversation memory…",
    "cancelled": "⏹️ Generation cancelled.",
    "error_generic": "⚠️ Error:\n`{error}`",
    "error_hint": "💡 Try: /status, /model to switch, /reset to clear context.",
    "empty_answer": "(the model returned no text — try /retry or switch model with /model)",
    "model_current": "🧠 Current model: `{model}`\n{info}",
    "model_set": "✅ Model set to `{model}`",
    "model_unknown": "❓ Unknown model `{query}`. Use /models or /model buttons.",
    "models_header": "📚 *Available models* (page {page}/{pages}) — tap to select:",
    "models_refresh_done": "🔎 Probed {count} models:\n✅ {ok} available • ❌ {fail} unavailable",
    "reset_done": "🧹 Conversation history cleared{extra}.",
    "reset_confirm": "Really clear the conversation history and temporary memory?",
    "history_empty": "No history yet.",
    "usage_header": "📊 *Stats for the last {days} days*",
    "tools_header": "🔧 *Internal tools* ({enabled}/{total} enabled) — tap to toggle:",
    "note_saved": "📝 Note saved (#{id}).",
    "notes_empty": "No saved notes.",
    "reminder_set": "⏰ Reminder #{id} in {when}:\n{text}",
    "reminder_fire": "⏰ *Reminder* {text}",
    "files_empty": "📂 Workspace is empty.",
    "settings_header": "⚙️ *Settings*",
    "lang_set": "🌐 UI language: {lang}",
    "think_on": "🧠 Reasoning display: *ON*",
    "think_off": "🧠 Reasoning display: *OFF*",
    "temp_set": "🌡️ Temperature: `{value}`",
    "invalid_number": "❗ Invalid number: `{value}`",
    "pong": "🏓 Latency: {ms} ms",
    "status_header": "🩺 *Bot status*",
    "confirm_yes": "✅ Yes",
    "confirm_no": "❌ No",
    "back": "↩️ Back",
    "next": "Next ▶",
    "prev": "◀ Prev",
    "close": "✖️ Close",
    "need_admin": "🔐 Admins only.",
    "vision_switch": "🖼️ You sent an image and the current model has no vision — switching to `{model}`.",
    "document_too_big": "⚠️ File larger than {limit}MB — ignored.",
    "document_unsupported": "⚠️ Unsupported file type for text reading: `{name}`",
    "group_notice": "👥 In groups I answer replies/mentions and commands.",
    "max_steps_note": "⚠️ Stopped at the step limit ({steps}). Raise it with /maxsteps.",
    "artifacts": "📎 Attachments:",
    "regenerating": "🔄 Regenerating…",
    "workspace_cleared": "🗑️ Workspace cleared.",
    "exported": "📤 Session exported.",
    "about_brand": (
        "🤖 *{bot_name}* `{version}`\n\n"
        "A full AI agent inside Telegram running on Cloudflare Workers AI.\n\n"
        "*Capabilities*\n"
        "• Multi-step agent loop with native tool calling\n"
        "• Sandboxed Python and shell execution\n"
        "• Files, web search, page fetching, Wikipedia\n"
        "• Persistent memory + automatic context compaction\n"
        "• Live streaming, colored buttons, automatic model fallback\n"
        "• Reminders, session export, token/cost statistics\n\n"
        "*{company}*\n"
        "📢 {channel} • 🆘 {support}\n"
        "🌐 {site}"
    ),
}
TABLES = {"ar": AR, "en": EN}


class Translator:

    def __init__(self, default: str = "ar") -> None:
        self.default = default if default in TABLES else "ar"

    def pick(self, lang: Any = None) -> str:
        if not lang:
            return self.default
        code = str(lang).lower()[:2]
        return code if code in TABLES else self.default

    def t(self, key: str, lang: Any = None, **kwargs: Any) -> str:
        table = TABLES[self.pick(lang)]
        template = table.get(key) or AR.get(key) or EN.get(key) or key
        try:
            return template.format(**kwargs) if kwargs else template
        except (KeyError, IndexError):
            return template
tr = Translator("ar")


def configure(default_lang: str) -> None:
    global tr
    tr = Translator(default_lang)


def help_text(lang: str = "ar") -> str:
    if Translator().pick(lang) == "ar":
        return """📖 *دليل الأوامر*
*المحادثة*
• أرسل نصاً أو صورة أو ملفاً → ينفّذ الوكيل المهمة بأدواته
• /stop — إيقاف التوليد الجاري
• /retry — إعادة توليد آخر رد
• /reset — مسح السجل (يطلب تأكيداً)
• /compact — ضغط الذاكرة الآن
• /history — عرض آخر الرسائل
• /export — تصدير الجلسة JSON
*النموذج*
• /model — اختيار بالأزرار
• /models — القائمة الكاملة (+ /models refresh لفحص التوفر)
• /temp 0.7 — درجة العشوائية
• /maxsteps 15 — حد خطوات الوكيل
• /think — إظهار/إخفاء تفكير النموذج
*الأدوات والملفات*
• /tools — قائمة الأدوات وتفعيلها/تعطيلها
• /files — محتوى مجلد العمل
• /file <مسار> — إرسال ملف إليك
• /clearfiles — إفراغ مجلد العمل
*الذاكرة*
• /note <نص> — حفظ ملاحظة سريعة
• /notes — عرض الملاحظات
• /delnote <رقم> — حذف ملاحظة
• /reminders — التذكيرات المجدولة
*التشخيص*
• /status — حالة الاتصال والإعدادات
• /usage — إحصاءات التوكنز والتكلفة
• /ping — زمن الاستجابة
• /id — معرّفاتك (للإدارة)
• /settings — لوحة الإعدادات
• /lang ar|en — لغة الواجهة
• /help — هذه الرسالة
"""
    return """📖 *Command guide*
*Chat*
• Send text/photo/document → the agent does the work with its tools
• /stop — cancel the running generation
• /retry — regenerate the last answer
• /reset — clear history (asks for confirmation)
• /compact — compress memory now
• /history — show recent messages
• /export — export the session as JSON
*Model*
• /model — button picker
• /models — full list (+ /models refresh to probe availability)
• /temp 0.7 — sampling temperature
• /maxsteps 15 — agent step limit
• /think — toggle reasoning display
*Tools & files*
• /tools — list and toggle tools
• /files — workspace contents
• /file <path> — send a file to you
• /clearfiles — empty the workspace
*Memory*
• /note <text> — quick save
• /notes — list notes
• /delnote <id> — delete a note
• /reminders — scheduled reminders
*Diagnostics*
• /status — connection & settings
• /usage — token/cost statistics
• /ping — latency
• /id — your ids (for ADMIN_IDS)
• /settings — settings panel
• /lang ar|en — UI language
• /help — this message
"""
