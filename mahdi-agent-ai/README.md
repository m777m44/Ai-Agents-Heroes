<div align="center">

# ✦ MAHDI AGENT AI

**وكيل ذكي متكامل يعمل من متصفح الويب — يفهم، يخطط، ينفّذ، ويحفظ كل تغيير.**
**An all-in-one AI agent workspace in your browser — it understands, plans, executes, and saves every change.**

</div>

---

## المميزات | Features

| | العربية | English |
|---|---|---|
| 💬 | محادثة متدفقة مع الوكيل، وعرض لخطوات التفكير واستدعاء الأدوات | Streaming chat with visible reasoning steps and tool calls |
| 🛠️ | أدوات: الملفات (قراءة/كتابة/تعديل/حذف)، البحث، الحساب، الوقت، إنشاء التطبيقات | Tools: files (read/write/edit/delete), search, math, time, app scaffolding |
| 🚀 | قوالب تطبيقات جاهزة: موقع هبوط، تطبيق مهام، حاسبة، معرض أعمال | Ready-made templates: landing page, todo app, calculator, portfolio |
| 👁️ | معاينة حية للتطبيقات داخل حاوية معزولة (Sandbox) | Live, sandboxed preview of generated apps |
| 🕓 | **سجل إصدارات يحفظ كل تغيير** مع الفروق (diff) واستعادة المشروع إلى أي نقطة | **Version history saving every change**, with diffs and one-click project restore |
| 📝 | محرر ملفات مدمج مع حفظ بـ Ctrl+S | Built-in code editor with Ctrl+S saving |
| 📦 | تصدير المشروع كملف ZIP | Export the whole project as ZIP |
| 🎙️ | إدخال صوتي (التعرف على الكلام) وقراءة الردود بصوت عالٍ | Voice input (speech recognition) and spoken replies |
| 🧠 | نماذج متعددة: MAHDI Demo (بدون مفتاح)، OpenAI، Anthropic Claude، Google Gemini، OpenRouter، Groq، Ollama | Multiple models: MAHDI Demo (no key), OpenAI, Anthropic Claude, Google Gemini, OpenRouter, Groq, Ollama |
| 🌍 | واجهة عربية وإنجليزية مع دعم كامل لاتجاه RTL | Arabic & English UI with full RTL support |
| 🔐 | رمز وصول اختياري لحماية النشر العام | Optional access token for public deployments |

## التشغيل السريع | Quick start

```bash
cd mahdi-agent-ai
npm install
cp .env.example .env     # optional: add model keys
npm run dev              # development (hot reload) → http://localhost:3000
```

للإنتاج | For production:

```bash
npm run build
npm start                # http://localhost:3000
```

> بدون أي مفتاح، يعمل **MAHDI Demo** محلياً بالكامل (إنشاء التطبيقات، الملفات، الحساب، البحث، السجل).
> Without any key, **MAHDI Demo** runs fully offline (apps, files, math, search, history).

## إضافة نماذج الذكاء الاصطناعي | Adding AI models

أضف المفتاح في `.env` ثم أعد التشغيل — يظهر النموذج تلقائياً في قائمة الاختيار.
Add the key to `.env` and restart — the model appears automatically in the picker.

| Provider | Variable |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic Claude | `ANTHROPIC_API_KEY` |
| Google Gemini | `GEMINI_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Ollama (local) | `OLLAMA_BASE_URL` / `OLLAMA_MODEL` |

## البنية | Architecture

```
mahdi-agent-ai/
├── server/                 Node.js + Express + TypeScript backend
│   ├── agent.ts            Agent loop: model → tools → model (streamed, persisted)
│   ├── tools.ts            Tool registry (files, search, apps, math, time)
│   ├── workspace.ts        Sandboxed project files + versioned history + restore
│   ├── providers/          Model adapters (OpenAI-compatible, Anthropic, offline demo)
│   ├── app.ts              REST + SSE API, preview server, ZIP export
│   └── *.test.ts           Unit & API tests (node:test)
├── src/                    React + Vite frontend (chat, files, preview, history, voice)
├── templates/              Starter applications used by the create_app tool
└── .env.example            All configuration options
```

- **الأمان | Safety:** مسارات الملفات مقيّدة داخل مساحة المشروع (لا `..` ولا مسارات مطلقة)، والمعاينة تعمل في `sandbox` بسياسة CSP، والتعبيرات الحسابية تُقيَّم بمحلل آمن (لا `eval`).
- **التخزين | Storage:** `data/` (غير متتبَّع في Git) يحتوي المحادثات وملفات المشاريع وسجل الإصدارات.

## الاختبار | Testing

```bash
npm test          # API, workspace versioning, restore, math & diff tests
npm run typecheck
```

## الترخيص | License

جميع الحقوق محفوظة © **MAHDI AGENT AI**.
All rights reserved © **MAHDI AGENT AI**.

> يتضمن المستودع أيضاً نسخة من مشروع `strands-agents/harness-sdk` في المجلد `../harness-sdk/` ويخضع لرخصته الأصلية Apache 2.0.
> The repository also includes a copy of `strands-agents/harness-sdk` in `../harness-sdk/`, under its original Apache 2.0 license.
