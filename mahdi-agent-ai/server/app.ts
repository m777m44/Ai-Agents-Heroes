import crypto from 'node:crypto';
import path from 'node:path';
import express, { type NextFunction, type Request, type Response } from 'express';
import { ACCESS_TOKEN, APP_NAME } from './config.js';
import { AppError } from './errors.js';
import { DEFAULT_MODEL_ID, listModels } from './providers/index.js';
import { runAgentTurn } from './agent.js';
import { diffLines } from './diff.js';
import { createZip } from './zip.js';
import { TEMPLATE_META } from './templates.js';
import {
  createConversation,
  deleteConversation,
  getConversation,
  listConversations,
  newId,
  updateConversation,
} from './store.js';
import { assertProjectId, normalizeRelPath, Workspace } from './workspace.js';

const APP_VERSION = '1.0.0';

const MIME: Record<string, string> = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.txt': 'text/plain; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
};

function tokenOk(req: Request): boolean {
  if (!ACCESS_TOKEN) return true;
  const supplied =
    (req.headers['x-mahdi-token'] as string | undefined) ??
    (req.headers.authorization?.startsWith('Bearer ') ? req.headers.authorization.slice(7) : undefined) ??
    (typeof req.query.token === 'string' ? req.query.token : undefined) ??
    '';
  const a = Buffer.from(supplied);
  const b = Buffer.from(ACCESS_TOKEN);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

const wrap =
  (fn: (req: Request, res: Response) => Promise<unknown>) =>
  (req: Request, res: Response, next: NextFunction) => {
    fn(req, res).catch(next);
  };

function param(req: Request, name: string): string {
  const value = req.params[name];
  return Array.isArray(value) ? value[0] : String(value ?? '');
}

export function createApp(): express.Express {
  const app = express();
  app.disable('x-powered-by');
  app.use(express.json({ limit: '2mb' }));

  app.use('/api', (req, res, next) => {
    if (req.path === '/health') return next();
    if (!tokenOk(req)) return res.status(401).json({ error: 'Access token required' });
    next();
  });

  app.get('/api/health', (_req, res) => {
    res.json({
      ok: true,
      name: APP_NAME,
      version: APP_VERSION,
      authRequired: Boolean(ACCESS_TOKEN),
      defaultModel: DEFAULT_MODEL_ID,
    });
  });

  app.get('/api/models', (_req, res) => res.json({ models: listModels(), defaultModel: DEFAULT_MODEL_ID }));
  app.get('/api/templates', (_req, res) => res.json({ templates: TEMPLATE_META }));

  app.get(
    '/api/conversations',
    wrap(async (req, res) => {
      const q = typeof req.query.q === 'string' ? req.query.q : '';
      res.json({ conversations: await listConversations(q) });
    }),
  );

  app.post(
    '/api/conversations',
    wrap(async (req, res) => {
      const body = (req.body ?? {}) as { title?: string; model?: string };
      const projectId = newId();
      const ws = new Workspace(projectId);
      await ws.ensure();
      const conv = await createConversation({
        title: (body.title ?? '').trim().slice(0, 120) || 'New chat',
        model: body.model || DEFAULT_MODEL_ID,
        projectId,
      });
      res.status(201).json({ conversation: conv });
    }),
  );

  app.get(
    '/api/conversations/:id',
    wrap(async (req, res) => {
      res.json({ conversation: await getConversation(param(req, 'id')) });
    }),
  );

  app.patch(
    '/api/conversations/:id',
    wrap(async (req, res) => {
      const body = (req.body ?? {}) as { title?: string; pinned?: boolean; model?: string };
      const conv = await updateConversation(param(req, 'id'), body);
      res.json({ conversation: conv });
    }),
  );

  app.delete(
    '/api/conversations/:id',
    wrap(async (req, res) => {
      const removed = await deleteConversation(param(req, 'id'));
      await new Workspace(removed.projectId).removeAll();
      res.status(204).end();
    }),
  );

  // Streams one agent turn as Server-Sent Events.
  app.post(
    '/api/conversations/:id/messages',
    wrap(async (req, res) => {
      const body = (req.body ?? {}) as { content?: string; model?: string };
      const content = typeof body.content === 'string' ? body.content.trim() : '';
      if (!content) throw new AppError(400, 'Message is empty');
      if (content.length > 20_000) throw new AppError(413, 'Message is too long');
      const conv = await getConversation(param(req, 'id'));

      res.writeHead(200, {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache, no-transform',
        Connection: 'keep-alive',
        'X-Accel-Buffering': 'no',
      });
      const controller = new AbortController();
      res.on('close', () => {
        if (!res.writableFinished) controller.abort();
      });
      const heartbeat = setInterval(() => res.write(': ping\n\n'), 15_000);
      const emit = (event: string, data: unknown) => {
        if (!res.writableEnded) res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
      };
      try {
        await runAgentTurn({ conversation: conv, content, modelId: body.model, emit, signal: controller.signal });
      } finally {
        clearInterval(heartbeat);
        res.end();
      }
    }),
  );

  app.get(
    '/api/projects/:pid/files',
    wrap(async (req, res) => {
      const pid = param(req, 'pid');
      assertProjectId(pid);
      res.json({ files: await new Workspace(pid).listFiles() });
    }),
  );

  app.get(
    '/api/projects/:pid/file',
    wrap(async (req, res) => {
      const pid = param(req, 'pid');
      assertProjectId(pid);
      const p = normalizeRelPath(req.query.path);
      res.json({ path: p, content: await new Workspace(pid).readFile(p) });
    }),
  );

  // Manual edit from the editor panel (recorded as a user version).
  app.put(
    '/api/projects/:pid/file',
    wrap(async (req, res) => {
      const pid = param(req, 'pid');
      assertProjectId(pid);
      const body = (req.body ?? {}) as { path?: string; content?: string; message?: string };
      if (typeof body.content !== 'string') throw new AppError(400, 'content must be a string');
      const ws = new Workspace(pid);
      const result = await ws.writeFile(body.path, body.content, {
        actor: 'user',
        message: body.message?.trim().slice(0, 200) || 'Edited in editor',
      });
      res.json({ changed: result.changed, version: result.version });
    }),
  );

  app.delete(
    '/api/projects/:pid/file',
    wrap(async (req, res) => {
      const pid = param(req, 'pid');
      assertProjectId(pid);
      const version = await new Workspace(pid).deleteFile(req.query.path, { actor: 'user', message: 'Deleted in files panel' });
      res.json({ version });
    }),
  );

  app.get(
    '/api/projects/:pid/history',
    wrap(async (req, res) => {
      const pid = param(req, 'pid');
      assertProjectId(pid);
      const ws = new Workspace(pid);
      const all = await ws.history();
      const filter = typeof req.query.path === 'string' && req.query.path ? normalizeRelPath(req.query.path) : null;
      const versions = (filter ? all.filter((v) => v.path === filter) : all)
        .slice()
        .reverse()
        .map(({ content: _content, ...meta }) => meta);
      res.json({ versions });
    }),
  );

  // Diff of one version against the previous version of the same file.
  app.get(
    '/api/projects/:pid/versions/:vid/diff',
    wrap(async (req, res) => {
      const pid = param(req, 'pid');
      assertProjectId(pid);
      const history = await new Workspace(pid).history();
      const index = history.findIndex((v) => v.id === param(req, 'vid'));
      if (index === -1) throw new AppError(404, 'Version not found');
      const target = history[index];
      let before = '';
      for (let i = index - 1; i >= 0; i--) {
        if (history[i].path === target.path) {
          before = history[i].content ?? '';
          break;
        }
      }
      const diff = diffLines(before, target.content ?? '');
      res.json({ version: target, ...diff });
    }),
  );

  app.post(
    '/api/projects/:pid/restore',
    wrap(async (req, res) => {
      const pid = param(req, 'pid');
      assertProjectId(pid);
      const versionId = String((req.body as { versionId?: string })?.versionId ?? '');
      if (!versionId) throw new AppError(400, 'versionId is required');
      const changed = await new Workspace(pid).restore(versionId, 'user');
      res.json({ changed });
    }),
  );

  app.get(
    '/api/projects/:pid/search',
    wrap(async (req, res) => {
      const pid = param(req, 'pid');
      assertProjectId(pid);
      res.json({ results: await new Workspace(pid).search(String(req.query.q ?? '')) });
    }),
  );

  app.get(
    '/api/projects/:pid/export',
    wrap(async (req, res) => {
      const pid = param(req, 'pid');
      assertProjectId(pid);
      const zip = createZip(await new Workspace(pid).snapshot());
      res.setHeader('Content-Type', 'application/zip');
      res.setHeader('Content-Disposition', `attachment; filename="mahdi-project-${pid.slice(0, 8)}.zip"`);
      res.send(zip);
    }),
  );

  // Serves the project's files for the live preview, sandboxed (no same-origin access).
  const PREVIEW_RE = /^\/api\/projects\/([^/]+)\/preview(?:\/(.*))?$/;
  app.get(PREVIEW_RE, (req, res, next) => {
    const match = req.path.match(PREVIEW_RE);
    if (!match) return next();
    (async () => {
      const pid = match[1];
      assertProjectId(pid);
      let rel = decodeURIComponent(match[2] ?? '');
      if (!rel || rel.endsWith('/')) rel += 'index.html';
      const content = await new Workspace(pid).readFile(rel);
      const ext = path.extname(rel).toLowerCase();
      res.setHeader('Content-Type', MIME[ext] ?? 'application/octet-stream');
      res.setHeader('X-Content-Type-Options', 'nosniff');
      res.setHeader('Content-Security-Policy', 'sandbox allow-scripts allow-forms allow-modals allow-popups');
      res.setHeader('Cache-Control', 'no-store');
      res.send(content);
    })().catch(next);
  });

  app.use('/api', (_req, res) => {
    res.status(404).json({ error: 'Not found' });
  });

  app.use((error: unknown, _req: Request, res: Response, _next: NextFunction) => {
    if (res.headersSent) {
      if (!res.writableEnded) res.end();
      return;
    }
    if (error instanceof AppError) {
      res.status(error.status).json({ error: error.message });
      return;
    }
    console.error(error);
    res.status(500).json({ error: 'Internal server error' });
  });

  return app;
}
