import fs from 'node:fs/promises';
import path from 'node:path';
import { TEMPLATES_DIR } from './config.js';
import { AppError } from './errors.js';

export interface TemplateMeta {
  id: string;
  name: { ar: string; en: string };
  description: { ar: string; en: string };
  icon: string;
}

export const TEMPLATE_META: TemplateMeta[] = [
  {
    id: 'landing',
    icon: '🚀',
    name: { ar: 'موقع هبوط احترافي', en: 'Landing page' },
    description: { ar: 'صفحة تسويق أنيقة مع مزايا وأسعار ونموذج اشتراك', en: 'Elegant marketing page with features, pricing and signup' },
  },
  {
    id: 'todo',
    icon: '✅',
    name: { ar: 'تطبيق المهام', en: 'Todo app' },
    description: { ar: 'قائمة مهام بفلاتر وحفظ محلي', en: 'Task list with filters and local persistence' },
  },
  {
    id: 'calculator',
    icon: '🧮',
    name: { ar: 'الحاسبة', en: 'Calculator' },
    description: { ar: 'حاسبة بتصميم فاخر ودعم لوحة المفاتيح', en: 'Premium calculator with keyboard support' },
  },
  {
    id: 'portfolio',
    icon: '🎨',
    name: { ar: 'معرض الأعمال', en: 'Portfolio' },
    description: { ar: 'سيرة ذاتية ومعرض أعمال بتصميم حديث', en: 'Personal portfolio with a modern showcase grid' },
  },
];

const TEMPLATE_IDS = new Set(TEMPLATE_META.map((t) => t.id));

export function isTemplateId(id: unknown): id is string {
  return typeof id === 'string' && TEMPLATE_IDS.has(id);
}

async function walk(dir: string, prefix = ''): Promise<Array<{ rel: string; abs: string }>> {
  const out: Array<{ rel: string; abs: string }> = [];
  for (const e of await fs.readdir(dir, { withFileTypes: true })) {
    const rel = prefix ? `${prefix}/${e.name}` : e.name;
    if (e.isDirectory()) out.push(...(await walk(path.join(dir, e.name), rel)));
    else if (e.isFile()) out.push({ rel, abs: path.join(dir, e.name) });
  }
  return out;
}

/** Loads every file of a starter template as { relativePath: content }. */
export async function loadTemplateFiles(id: string): Promise<Record<string, string>> {
  if (!isTemplateId(id)) throw new AppError(400, `Unknown template: ${id}`);
  const files: Record<string, string> = {};
  for (const f of await walk(path.join(TEMPLATES_DIR, id))) {
    files[f.rel] = await fs.readFile(f.abs, 'utf8');
  }
  return files;
}
