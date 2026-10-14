import { useEffect, useRef, useState } from 'react';
import { ArrowUp, Mic, Square } from 'lucide-react';
import type { Lang, ModelInfo } from '../types';
import { t } from '../i18n';
import { listen, speechSupported } from '../voice';

export function Composer({
  lang,
  voiceLang,
  models,
  model,
  onModelChange,
  busy,
  onSend,
  onStop,
  onNotice,
}: {
  lang: Lang;
  voiceLang: string;
  models: ModelInfo[];
  model: string;
  onModelChange: (id: string) => void;
  busy: boolean;
  onSend: (text: string) => void;
  onStop: () => void;
  onNotice: (msg: string) => void;
}) {
  const [text, setText] = useState('');
  const [listening, setListening] = useState(false);
  const stopRef = useRef<(() => void) | null>(null);
  const areaRef = useRef<HTMLTextAreaElement>(null);
  const baseRef = useRef('');

  useEffect(() => {
    const el = areaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 220)}px`;
  }, [text]);

  useEffect(() => () => stopRef.current?.(), []);

  const submit = () => {
    const value = text.trim();
    if (!value || busy) return;
    stopRef.current?.();
    setListening(false);
    setText('');
    onSend(value);
  };

  const toggleMic = () => {
    if (!speechSupported.input()) {
      onNotice(t(lang, 'micUnsupported'));
      return;
    }
    if (listening) {
      stopRef.current?.();
      return;
    }
    baseRef.current = text ? `${text.trimEnd()} ` : '';
    setListening(true);
    stopRef.current = listen(
      voiceLang,
      (value, isFinal) => {
        setText(baseRef.current + value);
        if (isFinal) setListening(false);
      },
      (error) => {
        setListening(false);
        if (error && error !== 'no-speech' && error !== 'aborted') onNotice(error === 'unsupported' ? t(lang, 'micUnsupported') : `🎙️ ${error}`);
      },
    );
  };

  return (
    <div className="composer-wrap">
      <div className={`composer ${busy ? 'is-busy' : ''}`}>
        <textarea
          ref={areaRef}
          rows={1}
          value={text}
          dir="auto"
          placeholder={listening ? t(lang, 'listening') : t(lang, 'placeholder')}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault();
              submit();
            }
          }}
          aria-label={t(lang, 'placeholder')}
        />
        <div className="composer-bar">
          <div className="composer-left">
            <select
              className="model-select"
              value={model}
              onChange={(e) => onModelChange(e.target.value)}
              aria-label={t(lang, 'model')}
              title={models.find((m) => m.id === model)?.description}
            >
              {models.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>
          <div className="composer-right">
            <button
              className={`icon-btn round ${listening ? 'recording' : ''}`}
              onClick={toggleMic}
              title={t(lang, 'speak')}
              aria-label={t(lang, 'speak')}
              type="button"
            >
              <Mic size={18} />
            </button>
            {busy ? (
              <button className="send-btn stop" onClick={onStop} type="button" aria-label={t(lang, 'stop')}>
                <Square size={14} fill="currentColor" />
                <span>{t(lang, 'stop')}</span>
              </button>
            ) : (
              <button className="send-btn" onClick={submit} disabled={!text.trim()} type="button" aria-label={t(lang, 'send')}>
                <ArrowUp size={18} />
              </button>
            )}
          </div>
        </div>
      </div>
      <p className="composer-foot">MAHDI AGENT AI · {t(lang, 'sendHint')}</p>
    </div>
  );
}
