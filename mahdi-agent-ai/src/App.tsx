import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Menu, PanelRightOpen, Sparkles } from 'lucide-react';
import { api, ApiError, getToken, setToken, streamTurn } from './api';
import type { Conversation, ConversationSummary, Lang, ModelInfo, TemplateInfo, Turn } from './types';
import { t } from './i18n';
import { Sidebar } from './components/Sidebar';
import { Welcome } from './components/Welcome';
import { Composer } from './components/Composer';
import { TranscriptView } from './components/Chat';
import { WorkspacePanel, type PanelTab } from './components/WorkspacePanel';
import { SettingsModal, type Prefs } from './components/SettingsModal';
import { Gate } from './components/Gate';
import { Logo } from './components/Logo';
import { speak } from './voice';

const PREFS_KEY = 'mahdi-agent-prefs';

function loadPrefs(): Prefs {
  const fallbackLang: Lang = navigator.language?.toLowerCase().startsWith('en') ? 'en' : 'ar';
  try {
    const raw = JSON.parse(localStorage.getItem(PREFS_KEY) ?? '{}') as Partial<Prefs>;
    const lang: Lang = raw.lang === 'en' || raw.lang === 'ar' ? raw.lang : fallbackLang;
    return {
      lang,
      voiceLang: raw.voiceLang ?? (lang === 'ar' ? 'ar-SA' : 'en-US'),
      autoSpeak: Boolean(raw.autoSpeak),
    };
  } catch {
    return { lang: fallbackLang, voiceLang: fallbackLang === 'ar' ? 'ar-SA' : 'en-US', autoSpeak: false };
  }
}

export function App() {
  const [prefs, setPrefs] = useState<Prefs>(loadPrefs);
  const lang = prefs.lang;
  const [gate, setGate] = useState<'checking' | 'open' | 'locked'>('checking');
  const [gateError, setGateError] = useState('');
  const [version, setVersion] = useState('');
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [defaultModel, setDefaultModel] = useState('demo');
  const [templates, setTemplates] = useState<TemplateInfo[]>([]);
  const [summaries, setSummaries] = useState<ConversationSummary[]>([]);
  const [query, setQuery] = useState('');
  const [activeId, setActiveId] = useState<string | null>(null);
  const [conv, setConv] = useState<Conversation | null>(null);
  const [live, setLive] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [panelTab, setPanelTab] = useState<PanelTab>('files');
  const [panelOpen, setPanelOpen] = useState(() => window.matchMedia('(min-width: 1100px)').matches);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [fsVersion, setFsVersion] = useState(0);
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [model, setModel] = useState('');
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.title = 'MAHDI AGENT AI';
  }, [prefs, lang]);

  const bootstrap = useCallback(async () => {
    try {
      const health = await api.health();
      setVersion(health.version);
      if (health.authRequired && !getToken()) {
        setGate('locked');
        return;
      }
      const [m, tpl] = await Promise.all([api.models(), api.templates()]);
      setModels(m.models);
      setDefaultModel(m.defaultModel);
      setTemplates(tpl.templates);
      setGate('open');
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        setGate('locked');
        setGateError(t(lang, 'invalidToken'));
      } else {
        setGate('open');
        setError(t(lang, 'connError'));
      }
    }
  }, [lang]);

  useEffect(() => {
    void bootstrap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const refreshList = useCallback(async (q = query) => {
    try {
      setSummaries((await api.conversations(q)).conversations);
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) setGate('locked');
    }
  }, [query]);

  useEffect(() => {
    if (gate !== 'open') return;
    const timer = setTimeout(() => void refreshList(query), query ? 250 : 0);
    return () => clearTimeout(timer);
  }, [query, gate, refreshList]);

  const loadConversation = useCallback(async (id: string) => {
    try {
      const { conversation } = await api.conversation(id);
      setConv(conversation);
      setModel(conversation.model);
      setActiveFile(null);
      setError('');
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  useEffect(() => {
    if (activeId) void loadConversation(activeId);
    else {
      setConv(null);
      setLive([]);
    }
  }, [activeId, loadConversation]);

  const newChat = async (): Promise<string | null> => {
    try {
      const { conversation } = await api.createConversation({ model: model || defaultModel });
      setSummaries((s) => [
        { id: conversation.id, title: conversation.title, projectId: conversation.projectId, model: conversation.model, pinned: false, createdAt: conversation.createdAt, updatedAt: conversation.updatedAt, messageCount: 0, preview: '' },
        ...s,
      ]);
      setActiveId(conversation.id);
      setConv(conversation);
      setLive([]);
      setSidebarOpen(false);
      return conversation.id;
    } catch (e) {
      setError((e as Error).message);
      return null;
    }
  };

  const send = async (text: string, explicitId?: string) => {
    let id = explicitId ?? conv?.id ?? activeId;
    if (!id) id = await newChat();
    if (!id) return;
    const chosenModel = model || defaultModel;
    const controller = new AbortController();
    abortRef.current = controller;
    setBusy(true);
    setError('');
    setNotice('');
    setStatusText('');
    setLive([{ role: 'user', content: text }]);
    let lastAssistant = '';
    try {
      await streamTurn(
        id,
        { content: text, model: chosenModel },
        ({ event, data }) => {
          switch (event) {
            case 'status':
              setStatusText(`${t(lang, 'step')} ${data.step} · ${data.model}`);
              break;
            case 'assistant':
              lastAssistant = data.text || lastAssistant;
              setLive((l) => [...l, { role: 'assistant', content: data.text ?? '', toolCalls: data.toolCalls ?? [] }]);
              break;
            case 'tool_end':
              setLive((l) => [...l, { role: 'tool', content: data.text ?? '', toolCallId: data.id, toolName: data.name }]);
              break;
            case 'files':
              setFsVersion((v) => v + 1);
              break;
            case 'limit':
              setNotice(t(lang, 'stepLimit'));
              break;
            case 'stopped':
              setNotice(t(lang, 'stopped'));
              break;
            case 'error':
              setError(String(data.message ?? 'error'));
              break;
          }
        },
        controller.signal,
      );
    } catch (e) {
      if ((e as Error).name !== 'AbortError') setError((e as Error).message || t(lang, 'connError'));
    } finally {
      abortRef.current = null;
      setBusy(false);
      setStatusText('');
      setLive([]);
      setFsVersion((v) => v + 1);
      await loadConversation(id!);
      await refreshList();
      if (prefs.autoSpeak && lastAssistant) speak(lastAssistant, lang);
    }
  };

  const stop = () => abortRef.current?.abort();

  const changeModel = async (id: string) => {
    setModel(id);
    if (conv) {
      try {
        const { conversation } = await api.patchConversation(conv.id, { model: id });
        setConv(conversation);
      } catch {
        /* keep local selection */
      }
    }
  };

  const rename = async (c: ConversationSummary) => {
    const title = window.prompt(t(lang, 'renamePrompt'), c.title);
    if (!title?.trim()) return;
    await api.patchConversation(c.id, { title });
    await refreshList();
    if (conv?.id === c.id) void loadConversation(c.id);
  };

  const togglePin = async (c: ConversationSummary) => {
    await api.patchConversation(c.id, { pinned: !c.pinned });
    await refreshList();
  };

  const remove = async (c: ConversationSummary) => {
    if (!window.confirm(t(lang, 'deleteChatConfirm'))) return;
    await api.deleteConversation(c.id);
    if (activeId === c.id) {
      setActiveId(null);
      setConv(null);
    }
    await refreshList();
  };

  const toggleLang = () => setPrefs((p) => ({ ...p, lang: p.lang === 'ar' ? 'en' : 'ar', voiceLang: p.lang === 'ar' ? 'en-US' : 'ar-SA' }));

  const turns = conv?.turns ?? [];
  const hasContent = turns.length > 0 || live.length > 0;
  const isChatEmpty = !hasContent;
  const activeSummary = useMemo(() => summaries.find((s) => s.id === activeId), [summaries, activeId]);
  const modelLabel = models.find((m) => m.id === (model || defaultModel))?.label ?? '';
  const isDemo = (model || defaultModel) === 'demo';

  if (gate === 'checking') {
    return (
      <div className="boot">
        <Logo size={56} className="pulse" />
        <p>{t(lang, 'loading')}</p>
      </div>
    );
  }
  if (gate === 'locked') {
    return (
      <Gate
        lang={lang}
        error={gateError}
        onSubmit={(token) => {
          setToken(token);
          setGateError('');
          setGate('checking');
          void bootstrap();
        }}
      />
    );
  }

  return (
    <div className={`app ${conv && panelOpen ? 'with-panel' : ''} ${sidebarOpen ? 'sidebar-open' : ''}`}>
      <Sidebar
        className={sidebarOpen ? 'open' : ''}
        lang={lang}
        conversations={summaries}
        activeId={activeId}
        query={query}
        onQuery={setQuery}
        onNew={() => void newChat()}
        onSelect={(id) => {
          setActiveId(id);
          setSidebarOpen(false);
        }}
        onRename={rename}
        onPin={togglePin}
        onDelete={remove}
        onSettings={() => setSettingsOpen(true)}
        onToggleLang={toggleLang}
      />

      <main className="chat-area">
        <header className="topbar">
          <button className="icon-btn menu-toggle" onClick={() => setSidebarOpen((o) => !o)} aria-label={t(lang, 'menu')}>
            <Menu size={18} />
          </button>
          <div className="topbar-title">
            <span>{conv?.title ?? activeSummary?.title ?? 'MAHDI AGENT AI'}</span>
          </div>
          <div className="topbar-actions">
            {conv && (
              <span className="model-chip" title={t(lang, 'model')}>
                <Sparkles size={13} /> {modelLabel}
              </span>
            )}
            {conv && (
              <button className="icon-btn" onClick={() => setPanelOpen((o) => !o)} aria-label={t(lang, 'panel')} title={t(lang, 'panel')}>
                <PanelRightOpen size={18} />
              </button>
            )}
          </div>
        </header>

        {isDemo && conv && <div className="demo-banner">{t(lang, 'demoHint')}</div>}

        {!conv ? (
          <div className="empty-stage">
            <Welcome
              lang={lang}
              templates={templates}
              onPick={(text) => {
                void (async () => {
                  const id = await newChat();
                  if (id) void send(text, id);
                })();
              }}
            />
            <Composer lang={lang} voiceLang={prefs.voiceLang} models={models} model={model || defaultModel} onModelChange={setModel} busy={false} onSend={(text) => void send(text)} onStop={stop} onNotice={setNotice} />
          </div>
        ) : (
          <>
            <div className="chat-scroll">
              {isChatEmpty ? (
                <Welcome lang={lang} templates={templates} onPick={(text) => void send(text)} />
              ) : (
                <TranscriptView turns={turns} live={live} lang={lang} busy={busy} statusText={statusText} />
              )}
              {notice && <div className="notice">{notice}</div>}
              {error && (
                <div className="error-banner">
                  <strong>{t(lang, 'errorTitle')}:</strong> {error}
                  <button onClick={() => setError('')} aria-label={t(lang, 'close')}>
                    ×
                  </button>
                </div>
              )}
            </div>
            <Composer lang={lang} voiceLang={prefs.voiceLang} models={models} model={model || defaultModel} onModelChange={changeModel} busy={busy} onSend={(text) => void send(text)} onStop={stop} onNotice={setNotice} />
          </>
        )}
      </main>

      {conv && panelOpen && (
        <WorkspacePanel
          pid={conv.projectId}
          lang={lang}
          tab={panelTab}
          onTab={setPanelTab}
          version={fsVersion}
          onChanged={() => setFsVersion((v) => v + 1)}
          onClose={() => setPanelOpen(false)}
          activePath={activeFile}
        />
      )}

      {settingsOpen && (
        <SettingsModal prefs={prefs} onChange={setPrefs} onClose={() => setSettingsOpen(false)} models={models} version={version} />
      )}
      {sidebarOpen && <div className="scrim" onClick={() => setSidebarOpen(false)} />}
    </div>
  );
}
