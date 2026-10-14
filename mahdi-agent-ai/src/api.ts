import type {
  Conversation,
  ConversationSummary,
  DiffResult,
  FileInfo,
  ModelInfo,
  StreamEvent,
  TemplateInfo,
  Version,
} from './types';

const TOKEN_KEY = 'mahdi-agent-token';

export const getToken = (): string => localStorage.getItem(TOKEN_KEY) ?? '';
export const setToken = (token: string): void => {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
};

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

function authHeaders(extra: Record<string, string> = {}): Record<string, string> {
  const token = getToken();
  return token ? { ...extra, 'x-mahdi-token': token } : extra;
}

async function request<T>(method: string, url: string, body?: unknown): Promise<T> {
  const res = await fetch(url, {
    method,
    headers: authHeaders(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return undefined as T;
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(res.status, (json as { error?: string }).error ?? `HTTP ${res.status}`);
  return json as T;
}

const enc = encodeURIComponent;

export const api = {
  health: () => request<{ ok: boolean; name: string; version: string; authRequired: boolean; defaultModel: string }>('GET', '/api/health'),
  models: () => request<{ models: ModelInfo[]; defaultModel: string }>('GET', '/api/models'),
  templates: () => request<{ templates: TemplateInfo[] }>('GET', '/api/templates'),
  conversations: (q = '') => request<{ conversations: ConversationSummary[] }>('GET', `/api/conversations?q=${enc(q)}`),
  createConversation: (body: { title?: string; model?: string }) =>
    request<{ conversation: Conversation }>('POST', '/api/conversations', body),
  conversation: (id: string) => request<{ conversation: Conversation }>('GET', `/api/conversations/${enc(id)}`),
  patchConversation: (id: string, body: { title?: string; pinned?: boolean; model?: string }) =>
    request<{ conversation: Conversation }>('PATCH', `/api/conversations/${enc(id)}`, body),
  deleteConversation: (id: string) => request<void>('DELETE', `/api/conversations/${enc(id)}`),
  files: (pid: string) => request<{ files: FileInfo[] }>('GET', `/api/projects/${enc(pid)}/files`),
  readFile: (pid: string, path: string) =>
    request<{ path: string; content: string }>('GET', `/api/projects/${enc(pid)}/file?path=${enc(path)}`),
  saveFile: (pid: string, path: string, content: string) =>
    request<{ changed: boolean; version: Version | null }>('PUT', `/api/projects/${enc(pid)}/file`, { path, content, message: 'Saved from editor' }),
  deleteFile: (pid: string, path: string) =>
    request<{ version: Version }>('DELETE', `/api/projects/${enc(pid)}/file?path=${enc(path)}`),
  history: (pid: string, path?: string) =>
    request<{ versions: Version[] }>('GET', `/api/projects/${enc(pid)}/history${path ? `?path=${enc(path)}` : ''}`),
  diff: (pid: string, versionId: string) =>
    request<DiffResult>('GET', `/api/projects/${enc(pid)}/versions/${enc(versionId)}/diff`),
  restore: (pid: string, versionId: string) =>
    request<{ changed: string[] }>('POST', `/api/projects/${enc(pid)}/restore`, { versionId }),
  search: (pid: string, q: string) =>
    request<{ results: Array<{ path: string; line: number; text: string }> }>('GET', `/api/projects/${enc(pid)}/search?q=${enc(q)}`),
};

export function previewUrl(pid: string, path = 'index.html', bust = 0): string {
  const token = getToken();
  const clean = path.split('/').map(enc).join('/');
  const qs = new URLSearchParams();
  if (token) qs.set('token', token);
  if (bust) qs.set('v', String(bust));
  const q = qs.toString();
  return `/api/projects/${enc(pid)}/preview/${clean}${q ? `?${q}` : ''}`;
}

export function exportUrl(pid: string): string {
  const token = getToken();
  return `/api/projects/${enc(pid)}/export${token ? `?token=${enc(token)}` : ''}`;
}

/** Sends one user message and streams the agent's events (Server-Sent Events over POST). */
export async function streamTurn(
  conversationId: string,
  body: { content: string; model?: string },
  onEvent: (e: StreamEvent) => void,
  signal: AbortSignal,
): Promise<void> {
  const res = await fetch(`/api/conversations/${enc(conversationId)}/messages`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json', Accept: 'text/event-stream' }),
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok || !res.body) {
    const json = await res.json().catch(() => ({}));
    throw new ApiError(res.status, (json as { error?: string }).error ?? `HTTP ${res.status}`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let idx: number;
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const block = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      let event = 'message';
      let data = '';
      for (const line of block.split('\n')) {
        if (line.startsWith('event:')) event = line.slice(6).trim();
        else if (line.startsWith('data:')) data += line.slice(5).trim();
      }
      if (data) onEvent({ event, data: JSON.parse(data) });
    }
  }
}
