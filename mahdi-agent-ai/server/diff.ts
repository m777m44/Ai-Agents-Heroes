export interface DiffLine {
  type: 'equal' | 'add' | 'del';
  text: string;
}

/** Line-based diff using a longest-common-subsequence table (bounded for very large inputs). */
export function diffLines(before: string, after: string): { lines: DiffLine[]; added: number; removed: number } {
  const a = before === '' ? [] : before.split('\n');
  const b = after === '' ? [] : after.split('\n');
  const n = a.length;
  const m = b.length;
  if (n * m > 4_000_000) {
    const lines: DiffLine[] = [
      ...a.map((text) => ({ type: 'del' as const, text })),
      ...b.map((text) => ({ type: 'add' as const, text })),
    ];
    return { lines, added: b.length, removed: a.length };
  }
  const dp: Uint32Array[] = Array.from({ length: n + 1 }, () => new Uint32Array(m + 1));
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
    }
  }
  const lines: DiffLine[] = [];
  let i = 0;
  let j = 0;
  let added = 0;
  let removed = 0;
  while (i < n && j < m) {
    if (a[i] === b[j]) {
      lines.push({ type: 'equal', text: a[i] });
      i++;
      j++;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      lines.push({ type: 'del', text: a[i++] });
      removed++;
    } else {
      lines.push({ type: 'add', text: b[j++] });
      added++;
    }
  }
  while (i < n) {
    lines.push({ type: 'del', text: a[i++] });
    removed++;
  }
  while (j < m) {
    lines.push({ type: 'add', text: b[j++] });
    added++;
  }
  return { lines, added, removed };
}
