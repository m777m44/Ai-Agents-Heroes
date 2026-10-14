import { useState } from 'react';
import { Languages, MessageSquarePlus, MoreHorizontal, Pencil, Pin, PinOff, Search, Settings, Trash2 } from 'lucide-react';
import type { ConversationSummary, Lang } from '../types';
import { t } from '../i18n';
import { Logo } from './Logo';

function ChatRow({
  c,
  active,
  lang,
  onSelect,
  onRename,
  onPin,
  onDelete,
}: {
  c: ConversationSummary;
  active: boolean;
  lang: Lang;
  onSelect: () => void;
  onRename: () => void;
  onPin: () => void;
  onDelete: () => void;
}) {
  const [menu, setMenu] = useState(false);
  return (
    <div className={`chat-row ${active ? 'active' : ''}`}>
      <button className="chat-main" onClick={onSelect} title={c.title}>
        {c.pinned && <Pin size={12} className="pin-ico" />}
        <span className="chat-title">{c.title || t(lang, 'untitled')}</span>
      </button>
      <button className="icon-btn small ghost" onClick={() => setMenu((m) => !m)} aria-label={t(lang, 'conversationMenu')}>
        <MoreHorizontal size={15} />
      </button>
      {menu && (
        <div className="menu" onMouseLeave={() => setMenu(false)}>
          <button onClick={() => { setMenu(false); onRename(); }}>
            <Pencil size={14} /> {t(lang, 'rename')}
          </button>
          <button onClick={() => { setMenu(false); onPin(); }}>
            {c.pinned ? <PinOff size={14} /> : <Pin size={14} />} {c.pinned ? t(lang, 'unpin') : t(lang, 'pin')}
          </button>
          <button className="danger" onClick={() => { setMenu(false); onDelete(); }}>
            <Trash2 size={14} /> {t(lang, 'deleteChat')}
          </button>
        </div>
      )}
    </div>
  );
}

export function Sidebar(props: {
  lang: Lang;
  conversations: ConversationSummary[];
  activeId: string | null;
  query: string;
  onQuery: (q: string) => void;
  onNew: () => void;
  onSelect: (id: string) => void;
  onRename: (c: ConversationSummary) => void;
  onPin: (c: ConversationSummary) => void;
  onDelete: (c: ConversationSummary) => void;
  onSettings: () => void;
  onToggleLang: () => void;
  className?: string;
}) {
  const { lang } = props;
  const pinned = props.conversations.filter((c) => c.pinned);
  const recent = props.conversations.filter((c) => !c.pinned);
  return (
    <aside className={`sidebar ${props.className ?? ''}`}>
      <div className="brand-row">
        <Logo size={34} />
        <div>
          <div className="brand-name">MAHDI AGENT AI</div>
          <div className="brand-tag">{t(lang, 'tagline')}</div>
        </div>
      </div>

      <button className="new-chat" onClick={props.onNew}>
        <MessageSquarePlus size={17} />
        <span>{t(lang, 'newChat')}</span>
      </button>

      <label className="search">
        <Search size={15} />
        <input value={props.query} onChange={(e) => props.onQuery(e.target.value)} placeholder={t(lang, 'searchChats')} />
      </label>

      <div className="chat-list">
        {props.conversations.length === 0 && <p className="empty-note">{props.query ? t(lang, 'noResults') : t(lang, 'noChats')}</p>}
        {pinned.length > 0 && <div className="group-label">{t(lang, 'pinned')}</div>}
        {pinned.map((c) => (
          <ChatRow key={c.id} c={c} lang={lang} active={c.id === props.activeId} onSelect={() => props.onSelect(c.id)} onRename={() => props.onRename(c)} onPin={() => props.onPin(c)} onDelete={() => props.onDelete(c)} />
        ))}
        {recent.length > 0 && <div className="group-label">{t(lang, 'recent')}</div>}
        {recent.map((c) => (
          <ChatRow key={c.id} c={c} lang={lang} active={c.id === props.activeId} onSelect={() => props.onSelect(c.id)} onRename={() => props.onRename(c)} onPin={() => props.onPin(c)} onDelete={() => props.onDelete(c)} />
        ))}
      </div>

      <div className="sidebar-foot">
        <button className="ghost-btn" onClick={props.onToggleLang} title={t(lang, 'language')}>
          <Languages size={16} /> {lang === 'ar' ? 'English' : 'العربية'}
        </button>
        <button className="icon-btn" onClick={props.onSettings} aria-label={t(lang, 'settings')} title={t(lang, 'settings')}>
          <Settings size={17} />
        </button>
      </div>
      <p className="rights">{t(lang, 'rights')}</p>
    </aside>
  );
}
