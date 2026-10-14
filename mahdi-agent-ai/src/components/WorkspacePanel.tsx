import { useEffect, useMemo, useState } from 'react';
import { Code2, Download, Eye, ExternalLink, FileText, FolderOpen, History as HistoryIcon, Plus, RefreshCw, RotateCcw, Save, Trash2, X } from 'lucide-react';
import { api, exportUrl, previewUrl } from '../api';
import type { DiffResult, FileInfo, Lang, Version } from '../types';
import { t } from '../i18n';

export type PanelTab = 'files' | 'preview' | 'history';

function timeAgo(iso: string, lang: Lang): string {
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  const fmt = new Intl.RelativeTimeFormat(lang === 'ar' ? 'ar' : 'en', { numeric: 'auto' });
  if (s < 60) return fmt.format(-Math.round(s), 'second');
  if (s < 3600) return fmt.format(-Math.round(s / 60), 'minute');
  if (s < 86400) return fmt.format(-Math.round(s / 3600), 'hour');
  return new Date(iso).toLocaleDateString(lang === 'ar' ? 'ar' : 'en', { month: 'short', day: 'numeric' });
}

/* ---------- Files & editor ---------- */

function FilesTab({ pid, lang, version, onChanged }: { pid: string; lang: Lang; version: number; onChanged: () => void }) {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState('');
  const [saved, setSaved] = useState('');
  const [newName, setNewName] = useState('');
  const [error, setError] = useState('');
  const [flash, setFlash] = useState('');
  const dirty = selected !== null && content !== saved;

  const load = async () => {
    try {
      setFiles((await api.files(pid)).files);
    } catch (e) {
      setError((e as Error).message);
    }
  };

  useEffect(() => {
    setSelected(null);
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pid]);

  useEffect(() => {
    void load();
    if (selected && !dirty) {
      api.readFile(pid, selected).then((r) => {
        setContent(r.content);
        setSaved(r.content);
      }).catch(() => setSelected(null));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [version]);

  const open = async (path: string) => {
    if (dirty && !window.confirm(t(lang, 'unsaved'))) return;
    try {
      const r = await api.readFile(pid, path);
      setSelected(path);
      setContent(r.content);
      setSaved(r.content);
      setError('');
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const save = async () => {
    if (!selected || !dirty) return;
    try {
      await api.saveFile(pid, selected, content);
      setSaved(content);
      setFlash(t(lang, 'saved'));
      setTimeout(() => setFlash(''), 1500);
      onChanged();
      void load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const remove = async (path: string) => {
    if (!window.confirm(t(lang, 'deleteConfirm'))) return;
    await api.deleteFile(pid, path);
    if (selected === path) setSelected(null);
    onChanged();
    void load();
  };

  const createFile = async () => {
    const name = newName.trim();
    if (!name) return;
    try {
      await api.saveFile(pid, name, '');
      setNewName('');
      onChanged();
      await load();
      await open(name);
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const grouped = useMemo(() => {
    const map = new Map<string, FileInfo[]>();
    for (const f of files) {
      const dir = f.path.includes('/') ? f.path.slice(0, f.path.lastIndexOf('/')) : '';
      map.set(dir, [...(map.get(dir) ?? []), f]);
    }
    return [...map.entries()].sort(([a], [b]) => a.localeCompare(b));
  }, [files]);

  return (
    <div className="files-tab">
      <div className="files-list">
        <div className="files-toolbar">
          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && void createFile()}
            placeholder={t(lang, 'newFilePh')}
            aria-label={t(lang, 'newFile')}
          />
          <button className="icon-btn small" onClick={createFile} title={t(lang, 'add')} aria-label={t(lang, 'add')}>
            <Plus size={15} />
          </button>
          <button className="icon-btn small" onClick={() => void load()} title={t(lang, 'refresh')} aria-label={t(lang, 'refresh')}>
            <RefreshCw size={14} />
          </button>
        </div>
        {files.length === 0 && <p className="empty-note">{t(lang, 'emptyWorkspace')}</p>}
        {grouped.map(([dir, items]) => (
          <div key={dir || '/'} className="file-group">
            {dir && (
              <div className="file-dir">
                <FolderOpen size={13} /> {dir}
              </div>
            )}
            {items.map((f) => {
              const name = f.path.split('/').pop();
              return (
                <div key={f.path} className={`file-row ${selected === f.path ? 'active' : ''}`}>
                  <button className="file-name" onClick={() => void open(f.path)} title={f.path}>
                    <FileText size={14} />
                    <span>{name}</span>
                  </button>
                  <span className="file-size">{f.size < 1024 ? `${f.size} B` : `${(f.size / 1024).toFixed(1)} KB`}</span>
                  <button className="icon-btn small ghost danger-hover" onClick={() => void remove(f.path)} aria-label={t(lang, 'delete')} title={t(lang, 'delete')}>
                    <Trash2 size={13} />
                  </button>
                </div>
              );
            })}
          </div>
        ))}
        <a className="export-link" href={exportUrl(pid)}>
          <Download size={14} /> {t(lang, 'export')}
        </a>
      </div>

      <div className="editor">
        {selected ? (
          <>
            <div className="editor-head">
              <span className="editor-path">{selected}</span>
              {dirty && <span className="dirty-dot">● {t(lang, 'unsaved')}</span>}
              {flash && <span className="flash">✓ {flash}</span>}
              <button className="primary-btn small" onClick={save} disabled={!dirty}>
                <Save size={14} /> {t(lang, 'save')}
              </button>
            </div>
            <textarea
              className="code-area"
              spellCheck={false}
              value={content}
              dir="ltr"
              onChange={(e) => setContent(e.target.value)}
              onKeyDown={(e) => {
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
                  e.preventDefault();
                  void save();
                }
                if (e.key === 'Tab') {
                  e.preventDefault();
                  const el = e.currentTarget;
                  const { selectionStart: s, selectionEnd: en } = el;
                  const next = `${content.slice(0, s)}  ${content.slice(en)}`;
                  setContent(next);
                  requestAnimationFrame(() => el.setSelectionRange(s + 2, s + 2));
                }
              }}
            />
          </>
        ) : (
          <div className="editor-empty">
            <Code2 size={34} />
            <p>{t(lang, 'selectFile')}</p>
          </div>
        )}
        {error && (
          <div className="inline-error">
            {error}
            <button onClick={() => setError('')} aria-label={t(lang, 'close')}>
              <X size={14} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/* ---------- Live preview ---------- */

function PreviewTab({ pid, lang, version }: { pid: string; lang: Lang; version: number }) {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [target, setTarget] = useState('index.html');
  const [bust, setBust] = useState(0);
  useEffect(() => {
    api.files(pid).then((r) => setFiles(r.files)).catch(() => setFiles([]));
  }, [pid, version]);
  const htmlFiles = files.filter((f) => /\.html?$/i.test(f.path)).map((f) => f.path);
  const current = htmlFiles.includes(target) ? target : htmlFiles[0];

  if (!current) {
    return (
      <div className="editor-empty">
        <Eye size={34} />
        <p>{t(lang, 'noPreview')}</p>
      </div>
    );
  }
  const src = previewUrl(pid, current, bust + version);
  return (
    <div className="preview-tab">
      <div className="preview-bar">
        <select value={current} onChange={(e) => setTarget(e.target.value)} aria-label="html file">
          {htmlFiles.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <button className="icon-btn small" onClick={() => setBust((b) => b + 1)} title={t(lang, 'refresh')} aria-label={t(lang, 'refresh')}>
          <RefreshCw size={14} />
        </button>
        <a className="icon-btn small" href={src} target="_blank" rel="noreferrer" title={t(lang, 'openTab')} aria-label={t(lang, 'openTab')}>
          <ExternalLink size={14} />
        </a>
      </div>
      <iframe
        key={`${current}-${bust}-${version}`}
        className="preview-frame"
        title="preview"
        src={src}
        sandbox="allow-scripts allow-forms allow-modals allow-popups"
      />
    </div>
  );
}

/* ---------- History ---------- */

function HistoryTab({ pid, lang, version, activePath, onRestored }: { pid: string; lang: Lang; version: number; activePath: string | null; onRestored: () => void }) {
  const [versions, setVersions] = useState<Version[]>([]);
  const [onlyFile, setOnlyFile] = useState(false);
  const [diff, setDiff] = useState<DiffResult | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState('');

  const load = () =>
    api
      .history(pid, onlyFile && activePath ? activePath : undefined)
      .then((r) => setVersions(r.versions))
      .catch((e: Error) => setError(e.message));

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pid, version, onlyFile, activePath]);

  const show = async (v: Version) => {
    setSelectedId(v.id);
    try {
      setDiff(await api.diff(pid, v.id));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const restore = async (v: Version) => {
    if (!window.confirm(t(lang, 'restoreConfirm'))) return;
    try {
      await api.restore(pid, v.id);
      onRestored();
      void load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const actorLabel = (a: Version['actor']) => (a === 'agent' ? t(lang, 'actorAgent') : a === 'user' ? t(lang, 'actorUser') : t(lang, 'actorSystem'));

  return (
    <div className="history-tab">
      <div className="history-toolbar">
        <label className="toggle-inline">
          <input type="checkbox" checked={onlyFile} onChange={(e) => setOnlyFile(e.target.checked)} disabled={!activePath} />
          {t(lang, 'thisFile')}
        </label>
        <button className="icon-btn small" onClick={() => void load()} aria-label={t(lang, 'refresh')} title={t(lang, 'refresh')}>
          <RefreshCw size={14} />
        </button>
      </div>
      {versions.length === 0 && (
        <p className="empty-note">
          <HistoryIcon size={16} /> {t(lang, 'noVersions')}
        </p>
      )}
      <ol className="timeline">
        {versions.map((v) => (
          <li key={v.id} className={`${selectedId === v.id ? 'active' : ''}`}>
            <button className="timeline-item" onClick={() => void show(v)}>
              <span className={`action-badge ${v.action}`}>{v.action}</span>
              <span className="tl-path">{v.path}</span>
              <span className="tl-msg">{v.message}</span>
              <span className="tl-meta">
                {actorLabel(v.actor)} · {timeAgo(v.createdAt, lang)}
              </span>
            </button>
          </li>
        ))}
      </ol>
      {diff && selectedId && (
        <div className="diff-box">
          <div className="diff-head">
            <strong>{diff.version.path}</strong>
            <span className="add-count">+{diff.added}</span>
            <span className="del-count">−{diff.removed}</span>
            <button className="ghost-btn small" onClick={() => void restore(diff.version)}>
              <RotateCcw size={14} /> {t(lang, 'restoreProject')}
            </button>
          </div>
          {diff.lines.length === 0 || (diff.added === 0 && diff.removed === 0) ? (
            <p className="empty-note">{t(lang, 'noChanges')}</p>
          ) : (
            <pre className="diff">
              {diff.lines.slice(0, 1500).map((l, i) => (
                <div key={i} className={`dl ${l.type}`}>
                  <span className="dl-sign">{l.type === 'add' ? '+' : l.type === 'del' ? '−' : ' '}</span>
                  {l.text || ' '}
                </div>
              ))}
            </pre>
          )}
        </div>
      )}
      {error && (
        <div className="inline-error">
          {error}
          <button onClick={() => setError('')} aria-label={t(lang, 'close')}>
            <X size={14} />
          </button>
        </div>
      )}
    </div>
  );
}

/* ---------- Container ---------- */

export function WorkspacePanel({
  pid,
  lang,
  tab,
  onTab,
  version,
  onChanged,
  onClose,
  activePath,
}: {
  pid: string;
  lang: Lang;
  tab: PanelTab;
  onTab: (t: PanelTab) => void;
  version: number;
  onChanged: () => void;
  onClose: () => void;
  activePath: string | null;
}) {
  const tabs: Array<{ id: PanelTab; label: string; icon: React.ReactNode }> = [
    { id: 'files', label: t(lang, 'files'), icon: <Code2 size={15} /> },
    { id: 'preview', label: t(lang, 'preview'), icon: <Eye size={15} /> },
    { id: 'history', label: t(lang, 'history'), icon: <HistoryIcon size={15} /> },
  ];
  return (
    <section className="panel">
      <header className="panel-head">
        <div className="tabs" role="tablist">
          {tabs.map((x) => (
            <button key={x.id} role="tab" aria-selected={tab === x.id} className={`tab ${tab === x.id ? 'active' : ''}`} onClick={() => onTab(x.id)}>
              {x.icon}
              <span>{x.label}</span>
            </button>
          ))}
        </div>
        <button className="icon-btn small" onClick={onClose} aria-label={t(lang, 'close')}>
          <X size={16} />
        </button>
      </header>
      <div className="panel-body">
        {tab === 'files' && <FilesTab pid={pid} lang={lang} version={version} onChanged={onChanged} />}
        {tab === 'preview' && <PreviewTab pid={pid} lang={lang} version={version} />}
        {tab === 'history' && <HistoryTab pid={pid} lang={lang} version={version} activePath={activePath} onRestored={onChanged} />}
      </div>
    </section>
  );
}
