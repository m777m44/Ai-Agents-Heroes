<!-- 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev -->
# 📡 بروتوكول Cloudflare Agents Playground (WebSocket) — توثيق مرجعي

> مُستخرج بالاستخراج العكسي من الحزمة الرسمية
> `playground.ai.cloudflare.com/assets/index-*.js` ومُتحقَّق منه عملياً مقابل الخادم الحيّ.
> هذا ما يبني عليه `mh3/backend.py` و `mh3/protocol.py`.

---

## 1) الاتصال

```
wss://playground.ai.cloudflare.com/agents/playground/{AGENT_NAME}?_pk={PK}&model={MODEL}
```

| الحقل | القيمة | ملاحظة |
|---|---|---|
| `AGENT_NAME` | `playground-` + 13 حرفاً `[0-9a-z]` | اسم مثيل الوكيل (Durable Object) |
| `_pk` | UUID4 | معرّف جلسة العميل |
| `model` | معرّف نموذج مُرمَّز URL | **مثبّت لهذا الاتصال** (انظر §7) |

**الترويسات المطلوبة:**
```
User-Agent: Mozilla/5.0 …            (أي UA متصفح)
Origin: https://playground.ai.cloudflare.com
Referer: https://playground.ai.cloudflare.com/?model={MODEL}
```

---

## 2) المصافحة (عميل ← خادم)

بالترتيب:
```jsonc
{"type":"cf_agent_stream_resume_request"}                       // هل يوجد بثّ جارٍ؟
{"name":"{AGENT_NAME}","agent":"playground","type":"cf_agent_identity"}
{"type":"cf_agent_state","state":{…}}                           // انظر §3
{"type":"cf_agent_mcp_servers","mcp":{"prompts":[],"resources":[],"servers":{},"tools":[]}}
{"type":"cf_agent_stream_resume_none"}                          // لا يوجد ما يُستأنف
```

**الخادم يردّ** (echo) بإطارات: `cf_agent_identity`، `cf_agent_state` (حالته *الافتراضية*)،
`cf_agent_mcp_servers`، `cf_agent_state` مرة أخرى، ثم `cf_agent_stream_resume_none`
(أو `cf_agent_stream_resuming` مع `id` إن كان هناك بثّ قائم ← يجب الرد بـ
`{"type":"cf_agent_stream_resume_ack","id":…}`).

---

## 3) الحالة `cf_agent_state`

```jsonc
{"type":"cf_agent_state","state":{
  "model":   "@cf/zai-org/glm-4.7-flash",   // يجب أن يطابق نموذج الرابط
  "temperature": 1,
  "stream":  true,
  "system":  "برومبت النظام…",
  "useExternalProvider": false,             // AI Gateway خاصتك
  "externalProvider": "openai",
  "webSearchEnabled": false,                // تتطلب AI Gateway (accountId+gatewayId+apiKey)
  "webSearchProvider": "ceramic",
  "generativeUIMode": "off"
}}
```
الحقول التي يعيدها الخادم في `state`: `model, temperature, stream, system,
useExternalProvider, externalProvider, webSearchEnabled, webSearchProvider, generativeUIMode`
(+ `usage` بعد كل توليد).

برومبت النظام الافتراضي للخادم يبدأ بـ:
> "You are a helpful assistant that completes tasks using MCP tools. … Act, don't narrate…"

---

## 4) طلب التوليد

```jsonc
{"id":"{RID}",                                  // 8 محارف من أبجدية nanoid
 "type":"cf_agent_use_chat_request",
 "init":{"method":"POST","body":"<JSON نصي>"}}
```
ومحتوى `body`:
```jsonc
{
  "messages":[                                  // صيغة UIMessage (AI SDK v5)
    {"role":"user","id":"msg_0","parts":[
      {"type":"text","text":"…"},
      {"type":"file","mediaType":"image/png","filename":"a.png","url":"data:image/png;base64,…"}
    ]},
    {"role":"assistant","id":"assistant_…","parts":[
      {"type":"text","text":"…"},
      {"type":"reasoning","text":"…","state":"done"},
      {"type":"tool-{TOOL_NAME}","toolCallId":"…","state":"output-available",
       "input":{…},"output":{…}}
    ]}
  ],
  "trigger":"submit-message",                   // أو regenerate-message / resume-stream
  "clientTools":[{"name":"…","description":"…","parameters":{ /* JSON Schema */ }}]
}
```

---

## 5) البثّ (خادم ← عميل)

كل جزء يصل في إطار مستقل:
```jsonc
{"id":"{RID}","type":"cf_agent_use_chat_response","body":"<JSON جزء>","done":false}
{"id":"{RID}","type":"cf_agent_use_chat_response","body":"","done":true}   // النهاية
{"id":"{RID}","type":"cf_agent_use_chat_response","error":true,"body":"{\"message\":…}"}
```

**أنواع الأجزاء (`body`):**

| المجموعة | الأنواع |
|---|---|
| البنية | `start` (فيه `messageId`)، `start-step`، `finish-step`، `finish` (فيه `messageMetadata.finishReason`) |
| النص | `text-start`، `text-delta` (`delta`)، `text-end` |
| التفكير | `reasoning-start`، `reasoning-delta`، `reasoning-end` |
| الأدوات | `tool-input-start` (`toolCallId`,`toolName`)، `tool-input-delta` (`inputTextDelta`)، `tool-input-available` (`input`)، `tool-input-error`، `tool-output-available`، `tool-output-error`، `tool-output-denied`، `tool-approval-request`، `tool-approval-response` |
| مصادر/ملفات | `file` (`mediaType`,`url`)، `source-url`، `source-document` |
| أخرى | `data-*` (بيانات مخصصة)، `error`، `abort` |

`finishReason` المرصودة: `stop`، `tool-calls`، `length`.

**إطار الاستخدام** (يصل بين `finish-step` و `finish`):
```jsonc
{"type":"cf_agent_state","state":{"model":"…","usage":{
  "inputTokens":214,"outputTokens":64,"totalTokens":278,
  "costUsd":0.0000384,"generationMs":1232,"responseCount":1}}}
```
> ⚠️ `usage` **تراكمي لكل جلسة الوكيل** (لاحظ `responseCount`). احسب الفرق بين
> قراءتين للحصول على استخدام الخطوة الواحدة — هذا ما يفعله `backend._usage_delta`.

---

## 6) دورة الأدوات (client-side tools)

1. declare الأدوات في `clientTools` مع كل طلب.
2. النموذج يُصدر `tool-input-start` → `tool-input-delta` → `tool-input-available`.
3. تنتهي الخطوة بـ `finish` مع `finishReason: "tool-calls"` و `done: true`.
4. نفّذ الأدوات محلياً، ثم أرسل لكل منها:
```jsonc
{"type":"cf_agent_tool_result","toolCallId":"…","toolName":"…","output":{…},
 "autoContinue":false,"clientTools":[…],
 "state":"output-available"}            // أو "output-error" مع "errorText"
```
5. أرسل **طلباً جديداً** بالتاريخ المحدّث (أجزاء `tool-<name>` بحالة `output-available`)
   لمواصلة الدورة. (`autoContinue:true` يجعل الخادم يواصل بنفسه — البوت يقود الحلقة
   بنفسه تحكّماً أفضل.)
6. الموافقة على أدوات الخادم: `{"type":"cf_agent_tool_approval","toolCallId":"…","approved":true}`.

**مثال حقيقي مُلتقط:** النموذج استدعى أداتين **بالتوازي** في خطوة واحدة
(`get_current_time` و `add_numbers`)، ثم أُعيدت النتيجتان، فأجاب في الخطوة الثانية.

---

## 7) ⚠️ نقطتان حرجتان اكتُشفتا بالتجربة

### أ) النموذج مثبّت في الرابط
إرسال `cf_agent_state` بقيمة `model` مختلفة عن model الرابط يجعل الخادم يردّ:
```json
{"type":"cf_agent_state_error","error":"State update rejected"}
```
**ويرفض التحديث كاملاً** — أي أن برومبت النظام في نفس الإطار يضيع أيضاً!
→ **التبديل بين النماذج يتطلب اتصالاً جديداً** (تنفذه `ConnectionPool` تلقائياً).

### ب) تأكيد الحالة متأخر
أثناء المصافحة يبثّ الخادم حالته **الافتراضية** (وليس حالتك)، ولا يعيد بثّ الحالة
المعتمدة إلا بعد أول توليد (مع `usage`). الحالة تُعتمد فعلياً (تحقّقنا ببرومبت
"أنت قرصان" فأجاب بـ `PIRATE_OK`) — لذا يعيد البوت إرسال الحالة قبل كل طلب
(إطار صغير) ولا يعتمد على echo المصافحة.

---

## 8) أطر التحكم الأخرى

| الإطار | الاتجاه | الوظيفة |
|---|---|---|
| `cf_agent_chat_request_cancel` `{id}` | ← | إيقاف توليد جارٍ |
| `cf_agent_chat_clear` | ← | مسح سجل الخادم للمحادثة |
| `cf_agent_chat_messages` `{messages}` | ↔ | مزامنة/ضبط قائمة الرسائل |
| `cf_agent_message_updated` | → | تحديث رسالة محددة |
| `cf_agent_chat_recovering` | → | الخادم يستعيد الحالة |
| `cf_agent_stream_resuming` `{id}` | → | يوجد بثّ قابل للاستئناف |
| `cf_agent_stream_resume_ack` `{id}` | ← | تأكيد الاستئناف |
| `rpc` `{id,success,result,error}` | ↔ | نداءات RPC عامة |

**قائمة أنواع الإطارات الكاملة** (من ثابت `xO` في الحزمة الرسمية):
`cf_agent_chat_clear`, `cf_agent_chat_messages`, `cf_agent_chat_recovering`,
`cf_agent_chat_request_cancel`, `cf_agent_identity`, `cf_agent_mcp_servers`,
`cf_agent_message_updated`, `cf_agent_state`, `cf_agent_state_error`,
`cf_agent_stream_resume_ack`, `cf_agent_stream_resume_none`, `cf_agent_stream_resume_request`,
`cf_agent_stream_resuming`, `cf_agent_tool_approval`, `cf_agent_tool_result`,
`cf_agent_use_chat_request`, `cf_agent_use_chat_response`.

---

## 9) رموز الأخطاء المرصودة

| الرمز | المعنى | التصرف في البوت |
|---|---|---|
| `3021` | rate limiting: inference request per min rate reached | إعادة محاولة (٦ث/١٢ث) ثم تبديل لنموذج بديل |
| `5016` | requires license agreement (`submit the prompt 'agree'`) | تبديل فوري لنموذج بديل + رسالة للمستخدم |
| — | `Prompt exceeds maximum context length` | `ContextOverflow` ← قصّ التاريخ |
| — | `overloaded` / `capacity` | إعادة محاولة |

---

## 10) نماذج مؤكَّدة عملياً (تاريخ الفحص)

| النموذج | الحالة |
|---|---|
| `@cf/zai-org/glm-4.7-flash` | ✅ يعمل (افتراضي، يدعم الأدوات + التفكير) |
| `@cf/zai-org/glm-5.2` | ✅ يعمل |
| `@cf/zai-org/glm-5.3-flash` | ✅ يعمل (قد يظهر `3021` في الذروة) |
| `@cf/moonshotai/kimi-k2.6` | ✅ يعمل |
| `@cf/google/gemma-4-26b-a4b-it` | ✅ يعمل + **رؤية مؤكَّدة** (قرأ نص صورة) |
| `@cf/meta/llama-2-7b-chat-fp16` | ✅ يعمل (قديم) |
| `@cf/meta/llama-3.2-11b-vision-instruct` | 🔒 `5016` يتطلب موافقة ترخيص Meta |

استخدم `/models refresh` داخل البوت لفحص الكتالوج كاملاً لحظياً.

---

## 11) نقاط إضافية مفيدة

- **الصور:** جزء `{"type":"file","mediaType":"image/png","url":"data:image/png;base64,…"}`
  يعمل مع النماذج متعددة الوسائط (مؤكَّد على gemma-4).
- **نبض WebSocket:** الخادم يردّ على PING؛ اتصال خامل بقي حياً ٨٢+ ثانية في الاختبار.
  البوت يستخدم `heartbeat=25`.
- **أبجدية nanoid الرسمية:**
  `useandom-26T198340PX75pxJACKVERYMINDBUSHWOLF_GQZbfghjklqvwyzrict`
- **نقاط HTTP عامة:** `/api/config` (إعدادات عامة + sandboxHost)، `/api/sources`
  (مصادر التوثيق)، `/api/mcp/scan` (فحص خوادم MCP)، `/api/benchmark/*`.
- **البحث المدمج** (`webSearchEnabled`) يتطلب AI Gateway بحسابك — لذلك ينفّذ البوت
  البحث بأدواته الخاصة بدلاً منه.
