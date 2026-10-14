import { test } from 'node:test';
import assert from 'node:assert/strict';
import { evaluateExpression } from './calc.js';

test('evaluates arithmetic with precedence and parentheses', () => {
  assert.equal(evaluateExpression('25 * 4 + 10'), 110);
  assert.equal(evaluateExpression('(2 + 3) * 4'), 20);
  assert.equal(evaluateExpression('2 ^ 3 ^ 2'), 512);
  assert.equal(evaluateExpression('-3 + 5'), 2);
  assert.equal(evaluateExpression('10 % 4'), 2);
  assert.equal(evaluateExpression('sqrt(81) + abs(-2)'), 11);
});

test('supports Arabic-Indic digits and ×/÷ symbols', () => {
  assert.equal(evaluateExpression('٢ × ٣ + ٤'), 10);
  assert.equal(evaluateExpression('٨ ÷ ٢'), 4);
});

test('rejects unsafe or malformed input', () => {
  assert.throws(() => evaluateExpression('process.exit()'));
  assert.throws(() => evaluateExpression('1 / 0'));
  assert.throws(() => evaluateExpression('(1 + 2'));
  assert.throws(() => evaluateExpression(''));
  assert.throws(() => evaluateExpression('constructor'));
});
