import { useEffect, useMemo, useRef, useState } from 'react';
import { CheckCircle2, ChevronDown, Loader2, Volume2, VolumeX, Wrench, XCircle } from 'lucide-react';
import type { Lang, Turn } from '../types';
import { t } from '../i18n';
import { Markdown } from './Markdown';
import { Logo } from './Logo';
import { isSpeaking, speak, stopSpeaking, speechSupported } from '../voice';

const TOOL_LABELS: Record<string, { ar: string; en: string }> = {
  list_files: { ar: 'عرض الملفات', en: 'List files' },
  read_file: { ar: 'قراءة ملف', en: 'Read file' },
  write_file: { ar: 'كتابة ملف', en: 'Write file' },
  edit_file: { ar: 'تعديل ملف', en: 'Edit file' },
  delete_file: { ar: 'حذف ملف', en: 'Delete file' },
  search_files: { ar: 'بحث في الملفات', en: 'Search files' },
  create_app: { ar: 'إنشاء تطبيق', en: 'Create app' },
  calculate: { ar: 'حساب', en: 'Calculate' },
  current_time: { ar: 'الوقت الحالي', en: 'Current time' },
};

export function toolLabel(name: string, lang: Lang): string {
  return TOOL_LABELS[name]?.[lang] ?? name;
}

function argPreview(args: Record<string, unknown>): string {
  const entries = Object.entries(args).filter(([k]) => !['content', 'new_text', 'old_text'].includes(k));
  const s = entries.map(([k, v]) => `${k}: ${String(v)}`).join(' · ');
  return s.length > 90 ? `${s.slice(0, 90)}…` : s;
}

export function ToolCard({
  name,
  args,
  result,
  lang,
  pending,
}: {
  name: string;
  args?: Record<string, unknown>;
  result?: string;
  lang: Lang;
  pending: boolean;
}) {
  const [open, setOpen] = useState(false);
  const failed = !pending && result?.startsWith('Error:');
  const status = pending ? 'running' : failed ? 'failed' : 'ok';
  return (
    <div className={`tool-card ${status}`}>
      <button className="tool-head" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        <Wrench size={14} className="tool-ico" />
        <span className="tool-name">{toolLabel(name, lang)}</span>
        <span className="tool-args">{args ? argPreview(args) : ''}</span>
        <span className="tool-status">
          {pending ? (
            <>
              <Loader2 size={14} className="spin" /> {t(lang, 'running')}
            </>
          ) : failed ? (
            <>
              <XCircle size={14} /> {t(lang, 'failed')}
            </>
          ) : (
            <>
              <CheckCircle2 size={14} /> {t(lang, 'ok')}
            </>
          )}
        </span>
        <ChevronDown size={14} className={`chev ${open ? 'open' : ''}`} />
      </button>
      {open && result !== undefined && <pre className="tool-result">{result}</pre>}
    </div>
  );
}

function AgentMessage({
  turn,
  lang,
  results,
  busy,
}: {
  turn: Turn;
  lang: Lang;
  results: Map<string, Turn>;
  busy: boolean;
}) {
  const [speaking, setSpeaking] = useState(false);
  const canSpeak = speechSupported.output() && turn.content.trim().length > 0;
  return (
    <div className="msg agent">
      <div className="avatar-agent">
        <Logo size={22} />
      </div>
      <div className="agent-body">
        <div className="agent-meta">
          <span className="agent-name">MAHDI AGENT AI</span>
          {canSpeak && (
            <button
              className="icon-btn small"
              title={speaking ? t(lang, 'stopSpeaking') : t(lang, 'listen')}
              aria-label={speaking ? t(lang, 'stopSpeaking') : t(lang, 'listen')}
              onClick={() => {
                if (speaking || isSpeaking()) {
                  stopSpeaking();
                  setSpeaking(false);
                } else {
                  setSpeaking(true);
                  speak(turn.content, lang, () => setSpeaking(false));
                }
              }}
            >
              {speaking ? <VolumeX size={14} /> : <Volume2 size={14} />}
            </button>
          )}
        </div>
        {turn.content && <Markdown text={turn.content} lang={lang} />}
        {turn.toolCalls?.length ? (
          <div className="tool-stack">
            {turn.toolCalls.map((c) => {
              const res = results.get(c.id);
              return (
                <ToolCard
                  key={c.id}
                  name={c.name}
                  args={c.args}
                  lang={lang}
                  pending={!res && busy}
                  result={res?.content}
                />
              );
            })}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export function TranscriptView({
  turns,
  live,
  lang,
  busy,
  statusText,
}: {
  turns: Turn[];
  live: Turn[];
  lang: Lang;
  busy: boolean;
  statusText: string;
}) {
  const endRef = useRef<HTMLDivElement>(null);
  const all = useMemo(() => [...turns, ...live], [turns, live]);
  const results = useMemo(() => {
    const map = new Map<string, Turn>();
    for (const turn of all) if (turn.role === 'tool' && turn.toolCallId) map.set(turn.toolCallId, turn);
    return map;
  }, [all]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [all.length, busy]);

  return (
    <div className="transcript">
      {all.map((turn, i) => {
        if (turn.role === 'tool') return null; // rendered inside the assistant message that called it
        if (turn.role === 'user') {
          return (
            <div key={`u-${i}`} className="msg user">
              <div className="bubble user-bubble">{turn.content}</div>
            </div>
          );
        }
        const hasText = Boolean(turn.content.trim());
        const hasCalls = Boolean(turn.toolCalls?.length);
        if (!hasText && !hasCalls) return null;
        return <AgentMessage key={`a-${i}`} turn={turn} lang={lang} results={results} busy={busy && i >= turns.length} />;
      })}
      {busy && (
        <div className="thinking">
          <span className="dots">
            <i />
            <i />
            <i />
          </span>
          <span>{statusText || t(lang, 'thinking')}</span>
        </div>
      )}
      <div ref={endRef} />
    </div>
  );
}
