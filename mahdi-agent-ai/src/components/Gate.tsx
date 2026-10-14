import { useState } from 'react';
import { KeyRound } from 'lucide-react';
import type { Lang } from '../types';
import { t } from '../i18n';
import { Logo } from './Logo';

export function Gate({ lang, error, onSubmit }: { lang: Lang; error: string; onSubmit: (token: string) => void }) {
  const [value, setValue] = useState('');
  return (
    <div className="gate">
      <form
        className="gate-card"
        onSubmit={(e) => {
          e.preventDefault();
          if (value.trim()) onSubmit(value.trim());
        }}
      >
        <Logo size={56} />
        <h1>MAHDI AGENT AI</h1>
        <h2>{t(lang, 'tokenTitle')}</h2>
        <p>{t(lang, 'tokenSub')}</p>
        <label className="token-input">
          <KeyRound size={16} />
          <input type="password" value={value} onChange={(e) => setValue(e.target.value)} placeholder={t(lang, 'tokenPh')} autoFocus />
        </label>
        {error && <p className="gate-error">{error}</p>}
        <button className="primary-btn wide" type="submit">
          {t(lang, 'enter')}
        </button>
      </form>
    </div>
  );
}
