/** Safe arithmetic evaluator: numbers, + - * / % ^, parentheses, sqrt(), abs(). No eval. */
const DIGITS: Record<string, string> = { '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4', '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9' };

export function evaluateExpression(input: string): number {
  const src = input.replace(/[٠-٩]/g, (d) => DIGITS[d]).replace(/×/g, '*').replace(/÷/g, '/').replace(/\s+/g, '');
  if (!src || src.length > 200) throw new Error('Expression is empty or too long');
  if (!/^[0-9+\-*/%^().,a-z]*$/i.test(src)) throw new Error('Unsupported characters in expression');
  let pos = 0;

  const peek = () => src[pos];
  const fail = (msg: string): never => {
    throw new Error(msg);
  };

  function parseExpr(): number {
    let v = parseTerm();
    while (peek() === '+' || peek() === '-') {
      const op = src[pos++];
      const r = parseTerm();
      v = op === '+' ? v + r : v - r;
    }
    return v;
  }
  function parseTerm(): number {
    let v = parseUnary();
    while (peek() === '*' || peek() === '/' || peek() === '%') {
      const op = src[pos++];
      const r = parseUnary();
      if (op === '*') v *= r;
      else if (op === '/') {
        if (r === 0) fail('Division by zero');
        v /= r;
      } else v %= r;
    }
    return v;
  }
  function parseUnary(): number {
    if (peek() === '-') {
      pos++;
      return -parseUnary();
    }
    if (peek() === '+') {
      pos++;
      return parseUnary();
    }
    return parsePower();
  }
  function parsePower(): number {
    const base = parseAtom();
    if (peek() === '^') {
      pos++;
      return base ** parseUnary();
    }
    return base;
  }
  function parseAtom(): number {
    if (peek() === '(') {
      pos++;
      const v = parseExpr();
      if (peek() !== ')') fail('Missing closing parenthesis');
      pos++;
      return v;
    }
    const fn = src.slice(pos).match(/^(sqrt|abs)\(/i);
    if (fn) {
      pos += fn[0].length;
      const v = parseExpr();
      if (peek() !== ')') fail('Missing closing parenthesis');
      pos++;
      return fn[1].toLowerCase() === 'sqrt' ? Math.sqrt(v) : Math.abs(v);
    }
    const num = src.slice(pos).match(/^\d+(\.\d+)?/);
    if (!num) fail(`Unexpected token at position ${pos + 1}`);
    pos += num![0].length;
    return Number(num![0]);
  }

  const result = parseExpr();
  if (pos !== src.length) fail(`Unexpected input at position ${pos + 1}`);
  if (!Number.isFinite(result)) fail('Result is not a finite number');
  return result;
}
