import { test, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

const tmp = await fs.mkdtemp(path.join(os.tmpdir(), 'mahdi-ws-'));
process.env.MAHDI_DATA_DIR = tmp;
const { Workspace, normalizeRelPath } = await import('./workspace.js');
const { AppError } = await import('./errors.js');
const PID = 'test-project-0001';

test('normalizeRelPath blocks traversal and absolute escapes', () => {
  assert.equal(normalizeRelPath('/src//app.js'), 'src/app.js');
  assert.equal(normalizeRelPath('a\\b.txt'), 'a/b.txt');
  assert.throws(() => normalizeRelPath('../secret'), AppError);
  assert.throws(() => normalizeRelPath('a/../../b'), AppError);
  assert.throws(() => normalizeRelPath(''), AppError);
  assert.throws(() => normalizeRelPath('a\0b'), AppError);
});

test('writes are versioned and identical writes are not duplicated', async () => {
  const ws = new Workspace(PID);
  await ws.ensure();
  const first = await ws.writeFile('index.html', '<h1>v1</h1>', { actor: 'agent', message: 'first' });
  assert.equal(first.changed, true);
  assert.equal(first.version?.action, 'create');
  const again = await ws.writeFile('index.html', '<h1>v1</h1>', { actor: 'agent' });
  assert.equal(again.changed, false);
  const second = await ws.writeFile('index.html', '<h1>v2</h1>', { actor: 'user', message: 'edit' });
  assert.equal(second.version?.action, 'update');
  const history = await ws.history();
  assert.equal(history.length, 2);
  assert.equal(await ws.readFile('index.html'), '<h1>v2</h1>');
});

test('editFile requires a unique match', async () => {
  const ws = new Workspace(PID);
  await ws.writeFile('dup.txt', 'x\nx\n', { actor: 'agent' });
  await assert.rejects(ws.editFile('dup.txt', 'x', 'y', { actor: 'agent' }), /appears 2 times/);
  await assert.rejects(ws.editFile('dup.txt', 'nope', 'y', { actor: 'agent' }), /not found/);
  await ws.writeFile('one.txt', 'hello world', { actor: 'agent' });
  await ws.editFile('one.txt', 'world', 'MAHDI', { actor: 'agent' });
  assert.equal(await ws.readFile('one.txt'), 'hello MAHDI');
});

test('restore returns the whole project to an earlier version and records it', async () => {
  const ws = new Workspace(PID);
  await ws.writeFile('a.txt', 'A1', { actor: 'agent' });
  const checkpoint = (await ws.history()).at(-1)!;
  await ws.writeFile('a.txt', 'A2', { actor: 'agent' });
  await ws.writeFile('b.txt', 'B', { actor: 'agent' });
  const changed = await ws.restore(checkpoint.id, 'user');
  assert.ok(changed.includes('a.txt'));
  assert.ok(changed.includes('b.txt'));
  assert.equal(await ws.readFile('a.txt'), 'A1');
  assert.equal(await ws.exists('b.txt'), false);
  const last = (await ws.history()).at(-1)!;
  assert.equal(last.content, null);
  assert.equal(last.action, 'restore');
});

test('search finds lines case-insensitively', async () => {
  const ws = new Workspace(PID);
  await ws.writeFile('notes/todo.md', 'Buy Milk\nwalk dog', { actor: 'user' });
  const hits = await ws.search('milk');
  assert.equal(hits.length, 1);
  assert.equal(hits[0].path, 'notes/todo.md');
  assert.equal(hits[0].line, 1);
});

after(async () => {
  await fs.rm(tmp, { recursive: true, force: true });
});
