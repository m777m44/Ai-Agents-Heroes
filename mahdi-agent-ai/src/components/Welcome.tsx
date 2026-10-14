import { ArrowUpLeft, Sparkles } from 'lucide-react';
import type { Lang, TemplateInfo } from '../types';
import { t } from '../i18n';
import { Logo } from './Logo';

const SUGGESTIONS: Record<Lang, string[]> = {
  ar: ['اصنع موقع هبوط لمقهى فاخر', 'أنشئ تطبيق مهام', 'احسب 25 * 4 + 10', 'اعرض الملفات', 'ما الوقت الآن؟', 'ابحث عن hero'],
  en: ['Build a landing page for a coffee shop', 'Create a todo app', 'calculate 25 * 4 + 10', 'list files', 'what time is it?', 'search for hero'],
};

const TEMPLATE_PROMPTS: Record<string, Record<Lang, string>> = {
  landing: { ar: 'اصنع موقع هبوط احترافي', en: 'Build a landing page' },
  todo: { ar: 'أنشئ تطبيق المهام', en: 'Create a todo app' },
  calculator: { ar: 'أنشئ تطبيق حاسبة', en: 'Create a calculator app' },
  portfolio: { ar: 'أنشئ معرض أعمال', en: 'Create a portfolio' },
};

export function Welcome({
  lang,
  templates,
  onPick,
}: {
  lang: Lang;
  templates: TemplateInfo[];
  onPick: (text: string) => void;
}) {
  return (
    <div className="welcome">
      <div className="hero-mark">
        <div className="halo" />
        <Logo size={64} />
      </div>
      <h1>{t(lang, 'welcomeTitle')}</h1>
      <p className="welcome-sub">{t(lang, 'welcomeSub')}</p>

      <section className="welcome-block">
        <h3>
          <Sparkles size={15} /> {t(lang, 'templates')}
        </h3>
        <div className="template-grid">
          {templates.map((tpl) => (
            <button key={tpl.id} className="template-card" onClick={() => onPick(TEMPLATE_PROMPTS[tpl.id]?.[lang] ?? tpl.name[lang])}>
              <span className="tpl-icon">{tpl.icon}</span>
              <span className="tpl-name">{tpl.name[lang]}</span>
              <span className="tpl-desc">{tpl.description[lang]}</span>
              <ArrowUpLeft size={15} className="tpl-arrow" />
            </button>
          ))}
        </div>
      </section>

      <section className="welcome-block">
        <h3>{t(lang, 'suggestions')}</h3>
        <div className="suggestions">
          {SUGGESTIONS[lang].map((s) => (
            <button key={s} className="suggestion" onClick={() => onPick(s)}>
              {s}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
