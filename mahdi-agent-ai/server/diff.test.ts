import { test } from 'node:test';
import assert from 'node:assert/strict';
import { diffLines } from './diff.js';

test('diff reports additions and removals line by line', () => {
  const r = diffLines('a\nb\nc', 'a\nB\nc\nd');
  assert.equal(r.added, 2);
  assert.equal(r.removed, 1);
  assert.deepEqual(
    r.lines.map((l) => l.type),
    ['equal', 'del', 'add', 'equal', 'add'],
  );
});

test('diff handles empty sides', () => {
  assert.deepEqual(diffLines('', 'x').lines, [{ type: 'add', text: 'x' }]);
  assert.deepEqual(diffLines('x', '').lines, [{ type: 'del', text: 'x' }]);
});
