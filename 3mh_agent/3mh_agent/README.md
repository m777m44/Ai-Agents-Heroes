# 🤖 3mh agent

**وكيل ذكاء اصطناعي كامل داخل تليجرام — بأزرار ملوّنة**

> تطوير **3MH TECHNOLOGIES**
> 🌐 http://3mh.pages.dev • 🆘 t.me/j49_c • 📢 t.me/bshshshkk

بوت تليجرام يحوّل نماذج **Cloudflare Workers AI** إلى وكيل مستقل له «جهاز داخلي»:
٢٨ أداة، تنفيذ كود في صندوق معزول، ملفات، بحث ويب، ذاكرة دائمة، تذكيرات، وتفويض نماذج فرعية —
عبر **استدعاء أدوات أصلي (native tool calling)** وليس بتحليل النص.
الواجهة كلها **أزرار ملوّنة أصلية** (Bot API 9.4+: `style = primary | success | danger`).

---

## 🎨 الأزرار الملوّنة

| اللون | المعنى | أمثلة |
|---|---|---|
| 🟢 `success` | تفعيل / تشغيل / تأكيد | أداة مفعّلة، «نعم»، النموذج الحالي، «أكمل» |
| 🔵 `primary` | عرض / تنقّل | النماذج، الملفات، الإحصاءات، «التالي» |
| 🔴 `danger` | إيقاف / حذف / رفض | «إيقاف»، «مسح السجل»، «لا»، أداة معطّلة |

- **لوحة أزرار دائمة** أسفل صندوق الإدخال (٨ أزرار ملوّنة) تُشغّل البوت بالكامل دون كتابة أمر:
  `🧠 النموذج` `🔧 الأدوات` `📂 الملفات` `💾 الذاكرة` `📊 الإحصاءات` `⚙️ الإعدادات` `⛔ إيقاف` `🧹 محادثة جديدة`
- **قوائم Inline ملوّنة** لكل قسم + أزرار روابط: `📢 القناة` `🆘 الدعم` `🌐 3MH TECHNOLOGIES`
- الرموز 🟢🔵🔴 مضافة أيضاً في النص لتكون واضحة على العملاء القدامى
  (الألوان الأصلية تحتاج Telegram حديثاً؛ البوت يعمل على الكل).
- تفعيل/تعطيل: `BUTTON_COLORS=true` و `MENU_BUTTONS=true` في `.env`، أو من زر «أزرار القائمة» في الإعدادات.

---

## ✨ المزايا

| المجال | التفاصيل |
|---|---|
| **حلقة الوكيل** | حتى ٤٠ خطوة: نموذج ← أدوات (بالتوازي) ← تنفيذ ← متابعة ← إجابة |
| **الأدوات** | ٢٨ أداة في ٦ فئات: `core` `web` `files` `code` `memory` `agent` |
| **تنفيذ الكود** | Python و shell في عمليات فرعية معزولة: مهلة، حدود ذاكرة/عمليات، بيئة نظيفة من الأسرار |
| **النماذج** | كتالوج ٣٥+ نموذجاً مع اختصارات (`glm5`, `gpt`, `gemma`…) وفحص توفّر حيّ |
| **المرونة** | إعادة محاولة + تبديل تلقائي لنموذج بديل عند `3021` أو `5016` |
| **الرؤية** | إرسال صور للنماذج متعددة الوسائط + تبديل تلقائي لنموذج رؤية |
| **الذاكرة** | سجل لكل محادثة في SQLite + ضغط تلخيصي تلقائي + ملاحظات دائمة + استعادة بعد إعادة التشغيل |
| **الواجهة** | بث حيّ بتعديل الرسالة، سجل خطوات الأدوات، تقطيع ذكي، ماركداون→HTML آمن، أزرار ملوّنة |
| **التحكم** | ٣١ أمراً (عربي/إنجليزي) + تشغيل كامل بالأزرار + إحصاءات توكنز/تكلفة + تذكيرات |
| **الأمان** | بوابة مشرفين، حماية SSRF، منع الهروب من مجلد العمل، حجب أنماط shell الخطرة |
| **الجودة** | ٢٥ اختباراً معزولاً (خادم WebSocket وهمي + طبقة تليجرام وهمية) — بلا إنترنت |

---

## 🚀 التشغيل

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # ضع BOT_TOKEN ثم ADMIN_IDS
```

```bash
python run.py --check       # فحص الإعدادات + الأدوات + الاتصال بالنموذج
python run.py --selftest    # فحوصات داخلية سريعة بلا شبكة
python run.py               # تشغيل البوت
```

**تشخيص بلا تليجرام:**
```bash
python run.py --ask "ما الوقت في الرياض؟ وكم 23*7؟"
python run.py --chat
python run.py --probe "@cf/zai-org/glm-5.2"
```

**ضبط `ADMIN_IDS`:** شغّل البوت وأرسل له `/id` — سيعيد رقمك مع رسالة توضيحية، فأضفه إلى `.env` وأعد التشغيل.

---

## 🩻 المعمارية

```
┌─────────────┐  تحديثات  ┌───────────────────────────────────────────────┐
│  Telegram   │◄──────────►│ mh3/tg  (handlers • stream • keyboards)       │
│ أزرار ملوّنة │            │  بوابة المشرفين • البث الحي • توجيه الأزرار     │
└─────────────┘            └───────────────────┬───────────────────────────┘
                                               │ StreamEvent
                           ┌───────────────────▼───────────────────────────┐
                           │ mh3/agent.py — نواة الوكيل                     │
                           │ الحلقة • الأدوات • حماية التكرار • التبديل • الإلغاء│
                           └─────┬──────────────────────────┬──────────────┘
                 ┌───────────────▼──────────┐   ┌───────────▼─────────────┐
                 │ mh3/tools — ٢٨ أداة       │   │ mh3/backend.py          │
                 │ core/web/files/code/     │   │ WebSocket دائم لكل محادثة │
                 │ memory/agent             │   │ مصافحة • بثّ • نتائج أدوات │
                 └───────────────┬──────────┘   └───────────┬─────────────┘
                 ┌───────────────▼──────────┐               │
                 │ mh3/store.py (SQLite)    │   ┌───────────▼──────────────────┐
                 │ جلسات•ملاحظات•استخدام•تذكير│   │ playground.ai.cloudflare.com │
                 └──────────────────────────┘   └──────────────────────────────┘
```

**دورة الخطوة:** إرسال `cf_agent_use_chat_request` مع `messages` و`clientTools` ←
استقبال `text-delta` / `tool-input-available` / `usage` / `finish` ← تنفيذ الأدوات محلياً بالتوازي ←
إرسال `cf_agent_tool_result` ← إضافة أجزاء `tool-<name>` بحالة `output-available` ← طلب متابعة ←
التكرار حتى `finishReason: stop`.

التفاصيل الكاملة للبروتوكول في [`docs/PROTOCOL.md`](docs/PROTOCOL.md).

---

## 📟 الأوامر

**المحادثة:** `/stop` `/retry` `/reset` `/compact` `/history` `/export`
**النموذج:** `/model [glm5]` `/models [refresh]` `/temp 0.7` `/maxsteps 15` `/think` `/system <نص>`
**الأدوات والملفات:** `/tools [اسم] [on|off]` `/files` `/file <مسار>` `/clearfiles`
**الذاكرة:** `/note <نص>` `/notes` `/delnote <id>` `/reminders`
**التشخيص:** `/status` `/usage [أيام] [all]` `/ping` `/id` `/settings` `/lang ar|en` `/about`
**الواجهة:** `/menu` (اللوحات الملوّنة) • `/hide` (إخفاء لوحة الأزرار) • `/help`

---

## 🔧 الأدوات (٢٨)

| الفئة | الأدوات |
|---|---|
| `core` | `current_time` `calculator` `text_tool` `json_tool` `random_tool` `sleep` |
| `web` | `web_search` `web_fetch` `wikipedia` `http_request` `url_info` |
| `files` | `file_read` `file_write` `file_list` `file_search` `file_info` `file_copy` `file_delete`🔐 `send_file` |
| `code` | `python_exec` `shell_exec`🔐 `sandbox_info` |
| `memory` | `memory_save` `memory_search` `memory_delete` `set_reminder` |
| `agent` | `ask_model` (تفويض نموذج فرعي) `self_info` |

🔐 = للمشرفين فقط. كل أداة لها مهلة مستقلة، واقتطاع للمخرجات، وتسجيل في قاعدة البيانات.

---

## ⚙️ الإعدادات (`.env`)

| المتغير | الافتراضي | الوصف |
|---|---|---|
| `BOT_TOKEN` | — | **إلزامي** — من BotFather |
| `ADMIN_IDS` | — | أرقام المشرفين (بفاصلة) |
| `ACCESS_MODE` | `admins` | `admins` / `allowlist` / `open` |
| `BOT_NAME` | `3mh agent` | اسم الوكيل الظاهر |
| `BUTTON_COLORS` / `MENU_BUTTONS` | `true` | الأزرار الملوّنة / اللوحة الدائمة |
| `DEFAULT_MODEL` | `@cf/zai-org/glm-4.7-flash` | النموذج الأساسي |
| `FALLBACK_MODELS` | glm-5.2, gpt-oss-120b, gemma-4 | بدائل تلقائية عند الفشل |
| `MAX_STEPS` | `10` | حد خطوات الوكيل (1–40) |
| `STEP_TIMEOUT` / `TOOL_TIMEOUT` | `180` / `45` | المَهلات بالثواني |
| `ENABLE_PYTHON` / `ENABLE_SHELL` | `true` | أدوات التنفيذ |
| `DISABLED_TOOLS` | — | أدوات معطّلة (أسماء بفاصلة) |
| `SANDBOX_MEMORY_MB` | `1024` | حد ذاكرة صندوق الكود |
| `MAX_CONTEXT_TOKENS` / `COMPACT_RATIO` | `24000` / `0.85` | ميزانية السياق والضغط التلقائي |
| `STREAM_EDITS` / `STREAM_EDIT_INTERVAL` | `true` / `1.0` | البث الحيّ |
| `SEARCH_PROVIDER` / `SEARCH_API_KEY` / `SEARXNG_URL` | `auto` | `tavily` `brave` `serper` `searxng` |
| `WIKI_USER_AGENT` | `3mh-agent/2.0 (+http://3mh.pages.dev; …)` | ويكيميديا ترفض UA المتصفحات من مراكز البيانات |
| `WEBHOOK_URL` / `WEBHOOK_SECRET` / `WEBHOOK_PORT` | — | وضع Webhook بدل Polling |
| `PROXY_URL` | — | بروكسي HTTP/SOCKS |
| `DB_PATH` / `WORKSPACE_DIR` / `LOG_FILE` | `./data/…` | مسارات التخزين |

كل القيم لها أيضاً ثوابت `UPPERCASE` مقروءة في أعلى `mh3/config.py` و `run.py`
(تُقرأ من البيئة/`.env` مع رجوع لهذه الثوابت).

---

## 🔐 الأمان

1. **بوابة المشرفين** — مع `ACCESS_MODE=admins` لا يردّ إلا على `ADMIN_IDS`.
2. **صندوق معزول** — لكل محادثة `WORKSPACE_DIR/<chat_id>`؛ الأدوات لا تخرج منه.
3. **بيئة نظيفة** — عمليات الكود لا ترى `BOT_TOKEN` أو أي سرّ.
4. **حدود موارد** — `RLIMIT_AS/CPU/NPROC/FSIZE` + مهلة + قتل مجموعة العمليات (`killpg`).
5. **حماية SSRF** — حجب العناوين الخاصة/المحلية/`metadata` لغير المشرفين.
6. **حاسبة بلا `eval`** — تقييم AST بعقدة بيضاء؛ `__import__` و`open` ممنوعان.
7. **`shell_exec` للمشرفين فقط** + حجب أنماط خطرة + قابل للتعطيل.
8. **تهريب HTML** — مخرجات النموذج تُهرَّب فلا حقن وسوم.
9. **حدود المعدل** — `RATE_LIMIT_PER_MIN` لكل محادثة + قفل تسلسل.

> **ملاحظة تشغيلية:** الواجهة المستخدمة هي Playground العامة التفاعلية ولها حدود معدل؛
> للحمل العالي استخدم Workers AI API بمفتاح حسابك. راجع شروط الخدمة قبل النشر التجاري.

---

## 🐳 النشر

```bash
docker build -t 3mh-agent .
docker run -d --name 3mh-agent --env-file .env -v mh3-data:/app/data --restart unless-stopped 3mh-agent
# أو
docker compose up -d && docker compose logs -f
```

**systemd:**
```ini
[Unit]
Description=3mh agent — 3MH TECHNOLOGIES
After=network-online.target

[Service]
Type=simple
User=mh3
WorkingDirectory=/opt/3mh_agent
ExecStart=/opt/3mh_agent/.venv/bin/python run.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

**Webhook:** اضبط `WEBHOOK_URL` و`WEBHOOK_SECRET` و`WEBHOOK_PORT` في `.env` (يتطلب TLS أو عكس بروكسي).

---

## 🧪 الاختبارات

```bash
python tests/test_all.py            # ٢٥ اختباراً معزولاً (~٧ ثوانٍ)
python tests/test_all.py -k agent   # تصفية بالاسم
pytest tests/test_all.py            # متوافق مع pytest
python run.py --selftest
```

- `tests/fake_playground.py` — خادم WebSocket وهمي يطبّق البروتوكول كاملاً
  (مصافحة، بثّ، أدوات، إلغاء، `3021`/`5016`، استخدام تراكمي).
- `tests/fake_telegram.py` — طبقة تليجرام وهمية تسجّل كل نداءات Bot API
  (تُستخدم للتحقق من وصول `style` الألوان فعلياً).

---

## 🛠️ استكشاف الأخطاء

| العَرَض | السبب | الحل |
|---|---|---|
| `3021: rate limiting` | تجاوز حد الطلبات/دقيقة | التبديل تلقائي؛ أضف نماذج إلى `FALLBACK_MODELS` |
| `5016: submit the prompt 'agree'` | نموذج يتطلب موافقة ترخيص | وافق من لوحة Cloudflare أو بدّل النموذج |
| الأزرار بلا ألوان | عميل Telegram قديم | حدّث التطبيق؛ الرموز 🟢🔵🔴 تبقى ظاهرة |
| البوت لا يردّ | `ADMIN_IDS` فارغ | أرسل `/id` وأضف رقمك ثم أعد التشغيل |
| `web_search` بلا نتائج | حجب DDG/Bing لعنوان مركز البيانات | اضبط `SEARCH_PROVIDER` + `SEARCH_API_KEY` أو SearXNG |
| ويكيبيديا `403` | ويكيميديا تحجب UA المتصفحات | `WIKI_USER_AGENT` يجب أن يحتوي رابط اتصال |
| استهلاك توكنز مرتفع | ٢٨ أداة معلنة لكل طلب | عطّل ما لا تحتاجه من `/tools` أو `DISABLED_TOOLS` |

---

## 📁 البنية

```
3mh_agent/
├── run.py                     # التشغيل + --ask/--chat/--check/--probe/--selftest
├── requirements.txt  .env.example  Dockerfile  docker-compose.yml  README.md
├── docs/PROTOCOL.md           # توثيق البروتوكول الكامل
├── mh3/
│   ├── config.py              # CONFIG block + الإعدادات من .env
│   ├── protocol.py            # إطارات WebSocket وأجزاء البث وبناة الرسائل
│   ├── backend.py             # اتصال دائم، بثّ، أدوات، إعادة اتصال، Usage، فحص النماذج
│   ├── agent.py               # نواة الوكيل: الحلقة، التبديل، الحماية، الإلغاء، الضغط
│   ├── memory.py              # برومبت النظام، تقدير التوكنز، القصّ، الضغط التلخيصي
│   ├── store.py               # SQLite: جلسات/ملاحظات/استخدام/أدوات/تذكيرات/KV
│   ├── models.py  errors.py
│   ├── tools/                 # __init__ (السجلّ) + core web files code brain
│   └── tg/                    # app handlers stream keyboards render ui
└── tests/                     # fake_playground.py  fake_telegram.py  test_all.py
```

---

**3MH TECHNOLOGIES** — 🌐 http://3mh.pages.dev • 🆘 t.me/j49_c • 📢 t.me/bshshshkk
