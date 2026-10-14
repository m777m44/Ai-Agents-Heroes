import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { DATA_DIR, MAX_FILE_BYTES, MAX_FILES_PER_PROJECT, MAX_VERSIONS_PER_PROJECT } from './config.js';
import { AppError } from './errors.js';
import { readJson, withLock, writeJsonAtomic } from './store.js';

export type Actor = 'user' | 'agent' | 'system';
export type VersionAction = 'create' | 'update' | 'delete' | 'restore' | 'template' | 'import';

/** One immutable entry in the project's history. `content: null` means the file was deleted. */
export interface VersionRecord {
  id: string;
  path: string;
  action: VersionAction;
  content: string | null;
  actor: Actor;
  message: string;
  size: number;
  hash: string | null;
  createdAt: string;
}

export interface FileInfo {
  path: string;
  size: number;
}

const ID_RE = /^[a-zA-Z0-9-]{8,64}$/;
const MAX_DEPTH = 8;

export function assertProjectId(id: string): void {
  if (!ID_RE.test(id)) throw new AppError(400, 'Invalid project id');
}

/** Validates a user/agent supplied relative path and returns its normalised form. */
export function normalizeRelPath(input: unknown): string {
  if (typeof input !== 'string') throw new AppError(400, 'A file path is required');
  const cleaned = input.replace(/\\/g, '/').replace(/^\/+/, '').trim();
  if (!cleaned || cleaned.includes('\0')) throw new AppError(400, 'Invalid file path');
  const parts = cleaned.split('/').filter(Boolean);
  if (parts.some((p) => p === '.' || p === '..')) throw new AppError(400, 'Path traversal is not allowed');
  if (parts.length > MAX_DEPTH) throw new AppError(400, 'Path is too deep');
  if (parts.some((p) => /[<>:"|?*]/.test(p))) throw new AppError(400, 'Path contains invalid characters');
  return parts.join('/');
}

const hashOf = (text: string): string => crypto.createHash('sha256').update(text).digest('hex').slice(0, 16);

export class Workspace {
  readonly projectId: string;
  readonly filesDir: string;
  readonly historyFile: string;

  constructor(projectId: string) {
    assertProjectId(projectId);
    this.projectId = projectId;
    const root = path.join(DATA_DIR, 'projects', projectId);
    this.filesDir = path.join(root, 'files');
    this.historyFile = path.join(root, 'history.json');
  }

  private lockKey(): string {
    return `project:${this.projectId}`;
  }

  private resolve(rel: unknown): { rel: string; full: string } {
    const normalized = normalizeRelPath(rel);
    const full = path.resolve(this.filesDir, normalized);
    if (!full.startsWith(this.filesDir + path.sep)) throw new AppError(400, 'Path escapes the workspace');
    return { rel: normalized, full };
  }

  async ensure(): Promise<void> {
    await fs.mkdir(this.filesDir, { recursive: true });
  }

  async listFiles(): Promise<FileInfo[]> {
    await this.ensure();
    const out: FileInfo[] = [];
    const walk = async (dir: string, prefix: string): Promise<void> => {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      for (const e of entries.sort((a, b) => a.name.localeCompare(b.name))) {
        const rel = prefix ? `${prefix}/${e.name}` : e.name;
        if (e.isDirectory()) await walk(path.join(dir, e.name), rel);
        else if (e.isFile()) {
          const st = await fs.stat(path.join(dir, e.name));
          out.push({ path: rel, size: st.size });
        }
        if (out.length >= MAX_FILES_PER_PROJECT) return;
      }
    };
    await walk(this.filesDir, '');
    return out;
  }

  async readFile(rel: unknown): Promise<string> {
    const { rel: p, full } = this.resolve(rel);
    try {
      const st = await fs.stat(full);
      if (st.size > MAX_FILE_BYTES) throw new AppError(413, `File is larger than ${MAX_FILE_BYTES} bytes`);
      return await fs.readFile(full, 'utf8');
    } catch (error) {
      if (error instanceof AppError) throw error;
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') throw new AppError(404, `File not found: ${p}`);
      throw error;
    }
  }

  async exists(rel: unknown): Promise<boolean> {
    const { full } = this.resolve(rel);
    try {
      await fs.access(full);
      return true;
    } catch {
      return false;
    }
  }

  async history(): Promise<VersionRecord[]> {
    return readJson<VersionRecord[]>(this.historyFile, []);
  }

  private async append(record: Omit<VersionRecord, 'id' | 'createdAt'>): Promise<VersionRecord> {
    const list = await this.history();
    const entry: VersionRecord = {
      ...record,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
    };
    list.push(entry);
    if (list.length > MAX_VERSIONS_PER_PROJECT) list.splice(0, list.length - MAX_VERSIONS_PER_PROJECT);
    await writeJsonAtomic(this.historyFile, list);
    return entry;
  }

  private async writeInternal(
    rel: unknown,
    content: string,
    opts: { actor: Actor; message: string; action?: VersionAction },
  ): Promise<{ version: VersionRecord | null; changed: boolean }> {
    const { rel: p, full } = this.resolve(rel);
    if (Buffer.byteLength(content, 'utf8') > MAX_FILE_BYTES) {
      throw new AppError(413, `Content is larger than ${MAX_FILE_BYTES} bytes`);
    }
    await this.ensure();
    let previous: string | null = null;
    try {
      previous = await fs.readFile(full, 'utf8');
    } catch {
      previous = null;
    }
    if (previous === content) return { version: null, changed: false };
    if (previous === null) {
      const files = await this.listFiles();
      if (files.length >= MAX_FILES_PER_PROJECT) throw new AppError(400, 'Project file limit reached');
    }
    await fs.mkdir(path.dirname(full), { recursive: true });
    await fs.writeFile(full, content, 'utf8');
    const version = await this.append({
      path: p,
      action: opts.action ?? (previous === null ? 'create' : 'update'),
      content,
      actor: opts.actor,
      message: opts.message,
      size: Buffer.byteLength(content, 'utf8'),
      hash: hashOf(content),
    });
    return { version, changed: true };
  }

  private async deleteInternal(
    rel: unknown,
    opts: { actor: Actor; message: string; action?: VersionAction },
  ): Promise<VersionRecord> {
    const { rel: p, full } = this.resolve(rel);
    try {
      await fs.unlink(full);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') throw new AppError(404, `File not found: ${p}`);
      throw error;
    }
    return this.append({
      path: p,
      action: opts.action ?? 'delete',
      content: null,
      actor: opts.actor,
      message: opts.message,
      size: 0,
      hash: null,
    });
  }

  async writeFile(
    rel: unknown,
    content: string,
    opts: { actor: Actor; message?: string; action?: VersionAction },
  ): Promise<{ version: VersionRecord | null; changed: boolean }> {
    return withLock(this.lockKey(), () =>
      this.writeInternal(rel, content, { actor: opts.actor, message: opts.message ?? 'Saved', action: opts.action }),
    );
  }

  async deleteFile(rel: unknown, opts: { actor: Actor; message?: string }): Promise<VersionRecord> {
    return withLock(this.lockKey(), () =>
      this.deleteInternal(rel, { actor: opts.actor, message: opts.message ?? 'Deleted' }),
    );
  }

  /** Replaces the first occurrence of `oldText`; fails when it is missing or ambiguous. */
  async editFile(
    rel: unknown,
    oldText: string,
    newText: string,
    opts: { actor: Actor; message?: string },
  ): Promise<{ version: VersionRecord | null; changed: boolean }> {
    return withLock(this.lockKey(), async () => {
      const { rel: p } = this.resolve(rel);
      const current = await this.readFile(p);
      const count = oldText ? current.split(oldText).length - 1 : 0;
      if (count === 0) throw new AppError(409, 'The text to replace was not found in the file');
      if (count > 1) throw new AppError(409, `The text appears ${count} times; include more surrounding context`);
      return this.writeInternal(p, current.replace(oldText, newText), {
        actor: opts.actor,
        message: opts.message ?? 'Edited',
      });
    });
  }

  async search(query: string, limit = 50): Promise<Array<{ path: string; line: number; text: string }>> {
    const needle = query.trim().toLowerCase();
    if (!needle) throw new AppError(400, 'Search query is empty');
    const results: Array<{ path: string; line: number; text: string }> = [];
    for (const file of await this.listFiles()) {
      if (file.size > MAX_FILE_BYTES) continue;
      const text = await fs.readFile(path.join(this.filesDir, file.path), 'utf8').catch(() => '');
      const lines = text.split('\n');
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].toLowerCase().includes(needle)) {
          results.push({ path: file.path, line: i + 1, text: lines[i].trim().slice(0, 200) });
          if (results.length >= limit) return results;
        }
      }
    }
    return results;
  }

  /** Replays history up to (and including) `versionId`; without an id it returns the latest state. */
  async stateAt(versionId?: string): Promise<Map<string, string>> {
    const state = new Map<string, string>();
    for (const v of await this.history()) {
      if (v.content === null) state.delete(v.path);
      else state.set(v.path, v.content);
      if (versionId && v.id === versionId) break;
    }
    return state;
  }

  async snapshot(): Promise<Map<string, string>> {
    const map = new Map<string, string>();
    for (const f of await this.listFiles()) {
      map.set(f.path, await fs.readFile(path.join(this.filesDir, f.path), 'utf8'));
    }
    return map;
  }

  /** Restores the whole project to the state recorded at `versionId`, recording the restore as new versions. */
  async restore(versionId: string, actor: Actor): Promise<string[]> {
    const history = await this.history();
    const target = history.find((v) => v.id === versionId);
    if (!target) throw new AppError(404, 'Version not found');
    return withLock(this.lockKey(), async () => {
      const desired = await this.stateAt(versionId);
      const current = await this.snapshot();
      const changed: string[] = [];
      const message = `Restored to ${target.createdAt}`;
      for (const [p, content] of desired) {
        if (current.get(p) !== content) {
          await this.writeInternal(p, content, { actor, message, action: 'restore' });
          changed.push(p);
        }
      }
      for (const p of current.keys()) {
        if (!desired.has(p)) {
          await this.deleteInternal(p, { actor, message, action: 'restore' });
          changed.push(p);
        }
      }
      return changed;
    });
  }

  async removeAll(): Promise<void> {
    await fs.rm(path.dirname(this.filesDir), { recursive: true, force: true });
  }
}
