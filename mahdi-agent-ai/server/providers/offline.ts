import type { ChatMessage, ModelAdapter, ModelResponse, ToolCall, ToolSpec } from './types.js';

/**
 * MAHDI Demo — a deterministic, offline planner. It needs no API key, so the
 * whole product (tools, versions, previews, voice UI) works out of the box.
 * With a real model configured, the LLM takes over the same tool interface.
 */

const ARABIC = /[\u0600-\u06FF]/;
const TEMPLATE_KEYWORDS: Array<[string, RegExp]> = [
  ['todo', /todo|task|tasks|مهام|قائمة|المهام/i],
  ['calculator', /calculator|calc|حاسبة|آلة حاسبة|الة حاسبة/i],
  ['portfolio', /portfolio|resume|cv|معرض|سيرة|بورتفوليو/i],
  ['landing', /landing|website|site|page|موقع|صفحة|هبوط/i],
];

function lang(text: string): 'ar' | 'en' {
  return ARABIC.test(text) ? 'ar' : 'en';
}

function call(name: string, args: Record<string, unknown>, index: number): ToolCall {
  return { id: `demo_${Date.now().toString(36)}_${index}`, name, args };
}

function helpText(l: 'ar' | 'en'): string {
  if (l === 'ar') {
    return [
      'أنا MAHDI Demo، وكيل يعمل محلياً بدون مفتاح API. أستطيع:',
      '- **إنشاء تطبيق أو موقع جاهز**: قل مثلاً "اصنع موقع هبوط" أو "أنشئ تطبيق مهام" (المتاح: موقع، مهام، حاسبة، معرض أعمال).',
      '- **عرض الملفات** و**قراءة ملف**: "اعرض الملفات" أو "اقرأ index.html".',
      '- **البحث في الملفات**: "ابحث عن كلمة".',
      '- **الحساب**: "احسب 25 * 4 + 10".',
      '- **الوقت الحالي**: "ما الوقت الآن؟"',
      '',
      'لتفعيل نماذج اللغة الكبيرة (OpenAI, Anthropic, Gemini, OpenRouter, Groq, Ollama) أضف المفتاح في ملف البيئة.',
    ].join('\n');
  }
  return [
    'I am MAHDI Demo, an offline agent that works without an API key. I can:',
    '- **Build a ready-made app or site**: try "build a landing page" or "create a todo app" (available: landing, todo, calculator, portfolio).',
    '- **List files** and **read a file**: "list files" or "read index.html".',
    '- **Search** the project: "search for hero".',
    '- **Calculate**: "calculate 25 * 4 + 10".',
    '- **Tell the time**: "what time is it?"',
    '',
    'To enable full large language models (OpenAI, Anthropic, Gemini, OpenRouter, Groq, Ollama), add a key to the environment file.',
  ].join('\n');
}

function planFor(text: string): { preface: string; calls: ToolCall[] } | null {
  const l = lang(text);
  const lower = text.toLowerCase();
  let idx = 0;

  const build = /(build|create|make|generate|scaffold|design|اصنع|أنشئ|انشئ|ابن|اعمل|طور|صمم|سوي)/i.test(text);
  if (build) {
    const template = TEMPLATE_KEYWORDS.find(([, re]) => re.test(text))?.[0] ?? 'landing';
    const names: Record<string, [string, string]> = {
      landing: ['Landing page', 'موقع هبوط'],
      todo: ['Todo app', 'تطبيق المهام'],
      calculator: ['Calculator app', 'تطبيق الحاسبة'],
      portfolio: ['Portfolio', 'معرض الأعمال'],
    };
    const [en, ar] = names[template];
    return {
      preface: l === 'ar' ? `سأنشئ ${ar} الآن داخل مساحة المشروع.` : `I will create a ${en} inside the project workspace.`,
      calls: [call('create_app', { template }, idx++)],
    };
  }

  if (/(list|show all files|files|ملفات|الملفات|اعرض)/i.test(text) && !/(read|اقرأ)/i.test(text)) {
    return {
      preface: l === 'ar' ? 'سأعرض ملفات المشروع.' : 'Listing the project files.',
      calls: [call('list_files', {}, idx++)],
    };
  }

  const readMatch = text.match(/(?:read|open|show|اقرأ|افتح|اعرض)\s+([\w./-]+\.\w+)/i);
  if (readMatch) {
    return {
      preface: l === 'ar' ? `سأقرأ الملف ${readMatch[1]}.` : `Reading ${readMatch[1]}.`,
      calls: [call('read_file', { path: readMatch[1] }, idx++)],
    };
  }

  const searchMatch = text.match(/(?:search for|search|find|ابحث عن|ابحث|جد)\s+(.+)/i);
  if (searchMatch) {
    const query = searchMatch[1].trim().replace(/[?؟.!]+$/, '');
    return {
      preface: l === 'ar' ? `سأبحث عن "${query}" في الملفات.` : `Searching files for "${query}".`,
      calls: [call('search_files', { query }, idx++)],
    };
  }

  if (/(time|date|clock|الوقت|الساعة|التاريخ)/i.test(lower)) {
    return { preface: l === 'ar' ? 'سأتحقق من الوقت.' : 'Checking the time.', calls: [call('current_time', {}, idx++)] };
  }

  const exprMatch = text.match(/([-+*/().^%\d\s]{3,})$/);
  if (exprMatch && /\d/.test(exprMatch[1]) && /[-+*/^%]/.test(exprMatch[1])) {
    const expression = exprMatch[1].trim();
    return {
      preface: l === 'ar' ? `سأحسب ${expression}.` : `Calculating ${expression}.`,
      calls: [call('calculate', { expression }, idx++)],
    };
  }

  return null;
}

function summarize(results: ChatMessage[], l: 'ar' | 'en'): string {
  const ar = l === 'ar';
  const parts: string[] = [];
  let changed = false;
  for (const r of results) {
    const content = r.content.trim();
    if (content.startsWith('Error:')) {
      parts.push(`⚠️ ${content.slice(6).trim()}`);
      continue;
    }
    switch (r.toolName) {
      case 'create_app':
        changed = true;
        parts.push(ar ? `✅ تم إنشاء التطبيق وحفظ ملفاته في مساحة العمل.\n\n${content}` : `✅ The app was created and its files were saved to the workspace.\n\n${content}`);
        break;
      case 'write_file':
      case 'edit_file':
      case 'delete_file':
        changed = true;
        parts.push(`✅ ${content}`);
        break;
      case 'list_files': {
        const lines = content.split('\n').filter(Boolean);
        parts.push(
          (ar ? `📁 الملفات (${lines.length}):\n` : `📁 Files (${lines.length}):\n`) +
            lines.map((line) => `- \`${line.replace(/ \(\d+ bytes\)$/, '')}\``).join('\n'),
        );
        break;
      }
      case 'read_file': {
        const body = content.length > 1500 ? `${content.slice(0, 1500)}\n…` : content;
        parts.push('```\n' + body + '\n```');
        break;
      }
      case 'search_files': {
        const hits = content.split('\n').filter(Boolean);
        parts.push(
          content === 'No matches.'
            ? ar ? 'لم أجد نتائج مطابقة.' : 'No matches found.'
            : (ar ? `🔎 نتائج البحث (${hits.length}):\n` : `🔎 Search results (${hits.length}):\n`) +
                hits.slice(0, 30).map((h) => `- \`${h.split(':').slice(0, 2).join(':')}\` ${h.split(': ').slice(1).join(': ')}`).join('\n'),
        );
        break;
      }
      case 'calculate':
        parts.push(ar ? `🧮 **النتيجة:** ${content}` : `🧮 **Result:** ${content}`);
        break;
      case 'current_time':
        parts.push(ar ? `🕒 الوقت الحالي (UTC): ${content}` : `🕒 Current time (UTC): ${content}`);
        break;
      default:
        parts.push(content);
    }
  }
  const tail = changed
    ? ar
      ? 'كل تغيير تم حفظه تلقائياً في **سجل الإصدارات**، ويمكنك معاينة التطبيق أو استعادة أي نسخة سابقة في أي وقت.'
      : 'Every change was saved automatically to the **version history**. You can preview the app or restore any earlier version at any time.'
    : '';
  return [parts.join('\n\n'), tail].filter(Boolean).join('\n\n');
}

export function createDemoAdapter(): ModelAdapter {
  return {
    info: {
      id: 'demo',
      label: 'MAHDI Demo (offline)',
      provider: 'built-in',
      model: 'mahdi-demo-planner',
      available: true,
      description: 'Works without any API key. Uses tools for files, apps, search, time and math.',
    },
    async complete(messages: ChatMessage[], _tools: ToolSpec[]): Promise<ModelResponse> {
      const lastUserIndex = messages.map((m) => m.role).lastIndexOf('user');
      const userText = messages[lastUserIndex]?.content ?? '';
      const l = lang(userText);
      const trailing: ChatMessage[] = [];
      for (let i = messages.length - 1; i > lastUserIndex; i--) {
        if (messages[i].role === 'tool') trailing.unshift(messages[i]);
      }
      const last = messages[messages.length - 1];
      if (last.role === 'tool' && trailing.length) {
        return { text: summarize(trailing, l), toolCalls: [] };
      }
      const plan = planFor(userText);
      if (!plan) return { text: helpText(l), toolCalls: [] };
      return { text: plan.preface, toolCalls: plan.calls };
    },
  };
}
