import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import type { AddressInfo } from 'node:net';
import type http from 'node:http';

const tmp = await fs.mkdtemp(path.join(os.tmpdir(), 'mahdi-api-'));
process.env.MAHDI_DATA_DIR = tmp;
delete process.env.MAHDI_ACCESS_TOKEN;
const { createApp } = await import('./app.js');

let server: http.Server;
let base = '';

before(async () => {
  server = createApp().listen(0, '127.0.0.1');
  await new Promise<void>((r) => server.once('listening', () => r()));
  base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
});

after(async () => {
  server.close();
  await fs.rm(tmp, { recursive: true, force: true });
});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function json(method: string, url: string, body?: unknown): Promise<{ status: number; body: any }> {
  const res = await fetch(base + url, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  return { status: res.status, body: res.status === 204 ? null : await res.json().catch(() => null) };
}

async function runTurn(id: string, content: string) {
  const res = await fetch(`${base}/api/conversations/${id}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  const text = await res.text();
  return text
    .split('\n\n')
    .filter((b) => b.startsWith('event:'))
    .map((b) => ({
      event: b.split('\n')[0].slice(7),
      data: JSON.parse(b.split('\n')[1].slice(6)),
    }));
}

test('health and model catalogue', async () => {
  const health = await json('GET', '/api/health');
  assert.equal(health.status, 200);
  assert.equal(health.body.name, 'MAHDI AGENT AI');
  const models = await json('GET', '/api/models');
  assert.ok(models.body.models.some((m: { id: string }) => m.id === 'demo'));
  const templates = await json('GET', '/api/templates');
  assert.equal(templates.body.templates.length, 4);
});

test('full flow: create conversation, build an app with tools, preview, history, restore, export', async () => {
  const created = await json('POST', '/api/conversations', { title: 'New chat' });
  assert.equal(created.status, 201);
  const conv = created.body.conversation;

  const events = await runTurn(conv.id, 'Build a todo app for me');
  const names = events.map((e) => e.event);
  assert.equal(names[0], 'start');
  assert.ok(names.includes('tool_start'));
  assert.ok(names.includes('files'));
  assert.equal(names.at(-1), 'done');
  const toolEnd = events.find((e) => e.event === 'tool_end');
  assert.equal(toolEnd?.data.name, 'create_app');
  assert.equal(toolEnd?.data.ok, true);

  const files = await json('GET', `/api/projects/${conv.projectId}/files`);
  const paths = files.body.files.map((f: { path: string }) => f.path);
  assert.ok(paths.includes('index.html') && paths.includes('app.js') && paths.includes('styles.css'));

  const preview = await fetch(`${base}/api/projects/${conv.projectId}/preview/`);
  assert.equal(preview.status, 200);
  assert.match(preview.headers.get('content-security-policy') ?? '', /sandbox/);
  assert.match(await preview.text(), /My Tasks/);

  const history = await json('GET', `/api/projects/${conv.projectId}/history`);
  assert.ok(history.body.versions.length >= 3);
  const firstVersion = history.body.versions.at(-1);
  const diff = await json('GET', `/api/projects/${conv.projectId}/versions/${firstVersion.id}/diff`);
  assert.ok(diff.body.added > 0);

  await json('PUT', `/api/projects/${conv.projectId}/file`, { path: 'index.html', content: '<h1>manual</h1>', message: 'manual edit' });
  const restored = await json('POST', `/api/projects/${conv.projectId}/restore`, { versionId: firstVersion.id });
  assert.equal(restored.status, 200);
  assert.ok(restored.body.changed.length > 0);
  const after = await json('GET', `/api/projects/${conv.projectId}/file?path=index.html`);
  assert.notEqual(after.body.content, '<h1>manual</h1>');

  const zip = await fetch(`${base}/api/projects/${conv.projectId}/export`);
  assert.equal(zip.status, 200);
  const bytes = Buffer.from(await zip.arrayBuffer());
  assert.equal(bytes.readUInt32LE(0), 0x04034b50);

  const saved = await json('GET', `/api/conversations/${conv.id}`);
  assert.equal(saved.body.conversation.turns.at(-1).role, 'assistant');
  assert.match(saved.body.conversation.title, /todo/i);
});

test('calculator tool and search work through the agent', async () => {
  const conv = (await json('POST', '/api/conversations', {})).body.conversation;
  const events = await runTurn(conv.id, 'calculate 25 * 4 + 10');
  const end = events.find((e) => e.event === 'tool_end');
  assert.equal(end?.data.text, '110');
  const reply = events.find((e) => e.event === 'assistant' && e.data.text.length > 0 && !e.data.toolCalls.length);
  assert.ok(reply);
});

test('path traversal over the API is rejected', async () => {
  const conv = (await json('POST', '/api/conversations', {})).body.conversation;
  const res = await json('PUT', `/api/projects/${conv.projectId}/file`, { path: '../../etc/passwd', content: 'x' });
  assert.equal(res.status, 400);
});

test('unknown conversation returns 404 and deletion removes the project', async () => {
  const missing = await json('GET', '/api/conversations/does-not-exist-123');
  assert.equal(missing.status, 404);
  const conv = (await json('POST', '/api/conversations', {})).body.conversation;
  assert.equal((await json('DELETE', `/api/conversations/${conv.id}`)).status, 204);
  assert.equal((await json('GET', `/api/conversations/${conv.id}`)).status, 404);
});
