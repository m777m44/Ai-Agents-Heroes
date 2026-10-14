let current = '0';
let previous = '';
let operator = null;
let fresh = true;

const $ = (sel) => document.querySelector(sel);

function compute(a, op, b) {
  const x = parseFloat(a);
  const y = parseFloat(b);
  switch (op) {
    case '+': return x + y;
    case '-': return x - y;
    case '*': return x * y;
    case '/': return y === 0 ? NaN : x / y;
    case '%': return x % y;
    default: return y;
  }
}

function show() {
  $('#result').textContent = current;
  $('#expr').textContent = operator ? `${previous} ${operator}` : '';
}

function press(key) {
  if (/\d/.test(key)) {
    current = fresh || current === '0' ? key : current + key;
    fresh = false;
  } else if (key === '.') {
    if (fresh) { current = '0.'; fresh = false; }
    else if (!current.includes('.')) current += '.';
  } else if (key === 'AC') {
    current = '0'; previous = ''; operator = null; fresh = true;
  } else if (key === 'DEL') {
    current = current.length > 1 ? current.slice(0, -1) : '0';
  } else if (key === '=') {
    if (operator) {
      const result = compute(previous, operator, current);
      current = Number.isFinite(result) ? String(Math.round(result * 1e10) / 1e10) : 'Error';
      previous = ''; operator = null; fresh = true;
    }
  } else {
    if (operator && !fresh) {
      current = String(compute(previous, operator, current));
    }
    previous = current; operator = key; fresh = true;
  }
  show();
}

document.querySelectorAll('button[data-k]').forEach((b) => b.addEventListener('click', () => press(b.dataset.k)));
document.addEventListener('keydown', (e) => {
  const map = { Enter: '=', Backspace: 'DEL', Escape: 'AC', '*': '*', '/': '/', '+': '+', '-': '-', '%': '%', '.': '.' };
  const k = e.key in map ? map[e.key] : /\d/.test(e.key) ? e.key : null;
  if (k) { e.preventDefault(); press(k); }
});
show();
