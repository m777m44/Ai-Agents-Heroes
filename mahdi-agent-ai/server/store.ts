import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { DATA_DIR } from './config.js';
import { AppError } from './errors.js';
import type { ChatMessage } from './providers/types.js';

export interface Conversation {
  id: string;
  title: string;
  projectId: string;
  model: string;
  pinned: boolean;
  createdAt: string;
  updatedAt: string;
  /** Model-facing transcript: user / assistant (with tool calls) / tool results. */
  turns: ChatMessage[];
}

export interface ConversationSummary {
  id: string;
  title: string;
  projectId: string;
  model: string;
  pinned: boolean;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  preview: string;
}

const DB_FILE = path.join(DATA_DIR, 'db.json');
let cache: Conversation[] | null = null;
const locks = new Map<string, Promise<unknown>>();

/** Serialises async work per key (used for the database and per-project file operations). */
export function withLock<T>(key: string, fn: () => Promise<T>): Promise<T> {
  const prev = locks.get(key) ?? Promise.resolve();
  const run = prev.catch(() => undefined).then(fn);
  const tail = run.catch(() => undefined);
  locks.set(key, tail);
  void tail.then(() => {
    if (locks.get(key) === tail) locks.delete(key);
  });
  return run;
}

export async function writeJsonAtomic(file: string, data: unknown): Promise<void> {
  await fs.mkdir(path.dirname(file), { recursive: true });
  const tmp = `${file}.${process.pid}.${crypto.randomBytes(4).toString('hex')}.tmp`;
  await fs.writeFile(tmp, JSON.stringify(data, null, 2), 'utf8');
  await fs.rename(tmp, file);
}

export async function readJson<T>(file: string, fallback: T): Promise<T> {
  try {
    return JSON.parse(await fs.readFile(file, 'utf8')) as T;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return fallback;
    throw error;
  }
}

async function loadDb(): Promise<Conversation[]> {
  if (!cache) {
    const db = await readJson<{ conversations: Conversation[] }>(DB_FILE, { conversations: [] });
    cache = Array.isArray(db.conversations) ? db.conversations : [];
  }
  return cache;
}

async function persist(): Promise<void> {
  await writeJsonAtomic(DB_FILE, { version: 1, conversations: cache ?? [] });
}

function summarize(conv: Conversation): ConversationSummary {
  const lastText = [...conv.turns].reverse().find((t) => t.role === 'assistant' && t.content);
  const preview = (lastText?.content ?? conv.turns.find((t) => t.role === 'user')?.content ?? '').slice(0, 140);
  return {
    id: conv.id,
    title: conv.title,
    projectId: conv.projectId,
    model: conv.model,
    pinned: conv.pinned,
    createdAt: conv.createdAt,
    updatedAt: conv.updatedAt,
    messageCount: conv.turns.filter((t) => t.role === 'user' || t.role === 'assistant').length,
    preview,
  };
}

export async function listConversations(query = ''): Promise<ConversationSummary[]> {
  const all = await loadDb();
  const q = query.trim().toLowerCase();
  return all
    .filter((c) => {
      if (!q) return true;
      const hay = `${c.title}\n${c.turns.map((t) => t.content).join('\n')}`.toLowerCase();
      return hay.includes(q);
    })
    .map(summarize)
    .sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.updatedAt.localeCompare(a.updatedAt));
}

export async function getConversation(id: string): Promise<Conversation> {
  const conv = (await loadDb()).find((c) => c.id === id);
  if (!conv) throw new AppError(404, 'Conversation not found');
  return conv;
}

export function newId(): string {
  return crypto.randomUUID();
}

export async function createConversation(init: { title: string; model: string; projectId: string }): Promise<Conversation> {
  return withLock('db', async () => {
    const all = await loadDb();
    const now = new Date().toISOString();
    const conv: Conversation = {
      id: newId(),
      title: init.title,
      projectId: init.projectId,
      model: init.model,
      pinned: false,
      createdAt: now,
      updatedAt: now,
      turns: [],
    };
    all.unshift(conv);
    await persist();
    return conv;
  });
}

export async function updateConversation(
  id: string,
  patch: Partial<Pick<Conversation, 'title' | 'pinned' | 'model'>>,
): Promise<Conversation> {
  return withLock('db', async () => {
    const conv = await getConversation(id);
    if (patch.title !== undefined) conv.title = patch.title.trim().slice(0, 120) || conv.title;
    if (patch.pinned !== undefined) conv.pinned = Boolean(patch.pinned);
    if (patch.model !== undefined) conv.model = patch.model;
    conv.updatedAt = new Date().toISOString();
    await persist();
    return conv;
  });
}

/** Persists the transcript of a conversation (called after every step of an agent run). */
export async function saveTurns(id: string, turns: ChatMessage[], title?: string): Promise<void> {
  await withLock('db', async () => {
    const conv = await getConversation(id);
    conv.turns = turns;
    if (title) conv.title = title;
    conv.updatedAt = new Date().toISOString();
    await persist();
  });
}

export async function deleteConversation(id: string): Promise<Conversation> {
  return withLock('db', async () => {
    const all = await loadDb();
    const index = all.findIndex((c) => c.id === id);
    if (index === -1) throw new AppError(404, 'Conversation not found');
    const [removed] = all.splice(index, 1);
    await persist();
    return removed;
  });
}
