import { X, Sparkles, Mic, Volume2, Languages, Info } from 'lucide-react';
import type { Lang, ModelInfo } from '../types';
import { t } from '../i18n';
import { VOICE_LANGS } from '../voice';
import { Logo } from './Logo';

export interface Prefs {
  lang: Lang;
  voiceLang: string;
  autoSpeak: boolean;
}

export function SettingsModal({
  prefs,
  onChange,
  onClose,
  models,
  version,
}: {
  prefs: Prefs;
  onChange: (p: Prefs) => void;
  onClose: () => void;
  models: ModelInfo[];
  version: string;
}) {
  const lang = prefs.lang;
  return (
    <div className="modal-backdrop" onMouseDown={onClose}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={t(lang, 'settingsTitle')} onMouseDown={(e) => e.stopPropagation()}>
        <header className="modal-head">
          <div className="modal-title">
            <Logo size={26} />
            <h2>{t(lang, 'settingsTitle')}</h2>
          </div>
          <button className="icon-btn small" onClick={onClose} aria-label={t(lang, 'close')}>
            <X size={16} />
          </button>
        </header>

        <div className="setting">
          <div className="setting-label">
            <Languages size={16} /> {t(lang, 'language')}
          </div>
          <div className="segmented">
            <button className={lang === 'ar' ? 'on' : ''} onClick={() => onChange({ ...prefs, lang: 'ar', voiceLang: prefs.voiceLang.startsWith('ar') ? prefs.voiceLang : 'ar-SA' })}>
              العربية
            </button>
            <button className={lang === 'en' ? 'on' : ''} onClick={() => onChange({ ...prefs, lang: 'en', voiceLang: prefs.voiceLang.startsWith('en') ? prefs.voiceLang : 'en-US' })}>
              English
            </button>
          </div>
        </div>

        <div className="setting">
          <div className="setting-label">
            <Mic size={16} /> {t(lang, 'voiceInput')}
          </div>
          <select value={prefs.voiceLang} onChange={(e) => onChange({ ...prefs, voiceLang: e.target.value })}>
            {VOICE_LANGS.map((v) => (
              <option key={v.value} value={v.value}>
                {v.label}
              </option>
            ))}
          </select>
        </div>

        <label className="setting toggle-row">
          <div>
            <div className="setting-label">
              <Volume2 size={16} /> {t(lang, 'autoSpeak')}
            </div>
            <small>{t(lang, 'autoSpeakSub')}</small>
          </div>
          <input type="checkbox" className="switch" checked={prefs.autoSpeak} onChange={(e) => onChange({ ...prefs, autoSpeak: e.target.checked })} />
        </label>

        <div className="setting">
          <div className="setting-label">
            <Sparkles size={16} /> {t(lang, 'model')}
          </div>
          <ul className="model-list">
            {models.map((m) => (
              <li key={m.id}>
                <span className="model-name">{m.label}</span>
                <small>{m.description}</small>
              </li>
            ))}
          </ul>
          <small className="muted">
            {lang === 'ar'
              ? 'أضف مفاتيح مزودي النماذج في ملف .env (انظر .env.example) ثم أعد تشغيل الخادم.'
              : 'Add model provider keys in your .env file (see .env.example), then restart the server.'}
          </small>
        </div>

        <div className="setting about">
          <div className="setting-label">
            <Info size={16} /> {t(lang, 'about')}
          </div>
          <p>{t(lang, 'featureList')}</p>
          <p className="muted">
            {t(lang, 'version')} {version} · {t(lang, 'rights')}
          </p>
        </div>
      </div>
    </div>
  );
}
