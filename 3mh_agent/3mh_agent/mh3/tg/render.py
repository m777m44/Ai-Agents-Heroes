# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import html as _html
import re
from typing import List, Optional
__all__ = ["escape_html", "md_to_html", "split_markdown", "split_html", "tail_text", "TG_LIMIT"]
TG_LIMIT = 4096
MD_LIMIT = 3200
_FENCE_RE = re.compile(r"^```([^\n`]*)\n(.*?)^```[ \t]*$", re.S | re.M)
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_LINK_RE = re.compile(r"\[([^\]\n]{1,200})\]\(\s*(https?://[^\s)]+|tg://[^\s)]+)\s*\)")
_BOLD_RE = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", re.S)
_BOLD2_RE = re.compile(r"__(?=\S)(.+?)(?<=\S)__", re.S)
_ITALIC_RE = re.compile(r"(?<![\*\w])\*(?=\S)([^*\n]{1,300})(?<=\S)\*(?!\*)")
_ITALIC2_RE = re.compile(r"(?<![_\w])_(?=\S)([^_\n]{1,300})(?<=\S)_(?![_\w])")
_STRIKE_RE = re.compile(r"~~(?=\S)(.+?)(?<=\S)~~", re.S)
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", re.M)
_QUOTE_RE = re.compile(r"^\s{0,3}(?:&gt;|>)\s?(.*)$", re.M)
_SAFE_URL = re.compile(r"^(https?://|tg://)", re.I)


def escape_html(text: str) -> str:
    return _html.escape(str(text or ""), quote=False)


def _balance_fences(text: str) -> str:
    if text.count("```") % 2 == 1:
        return text.rstrip("\n") + "\n```"
    return text


def md_to_html(text: str, *, balance: bool = True) -> str:
    if not text:
        return ""
    text = str(text).replace("\r\n", "\n").replace("\r", "\n")
    if balance:
        text = _balance_fences(text)
    placeholders: List[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"\x00{len(placeholders) - 1}\x00"

    def repl_fence(m: re.Match) -> str:
        lang = (m.group(1) or "").strip().split()[0] if m.group(1) else ""
        body = m.group(2)
        body = body.rstrip("\n")
        escaped = escape_html(body)
        if lang and re.fullmatch(r"[A-Za-z0-9_+\-.]{1,24}", lang):
            return stash(f'<pre><code class="language-{lang}">{escaped}</code></pre>')
        return stash(f"<pre>{escaped}</pre>")
    text = _FENCE_RE.sub(repl_fence, text)

    def repl_inline(m: re.Match) -> str:
        return stash(f"<code>{escape_html(m.group(1))}</code>")
    text = _INLINE_CODE_RE.sub(repl_inline, text)
    text = escape_html(text)

    def repl_link(m: re.Match) -> str:
        label, url = m.group(1), m.group(2)
        if not _SAFE_URL.match(url):
            return label
        return f'<a href="{_html.escape(url, quote=True)}">{label}</a>'
    text = _LINK_RE.sub(repl_link, text)
    text = _HEADING_RE.sub(lambda m: f"<b>{m.group(1).strip()}</b>", text)
    text = _QUOTE_RE.sub(lambda m: f"<blockquote>{m.group(1)}</blockquote>", text)
    text = _BOLD_RE.sub(r"<b>\1</b>", text)
    text = _BOLD2_RE.sub(r"<b>\1</b>", text)
    text = _STRIKE_RE.sub(r"<s>\1</s>", text)
    text = _ITALIC_RE.sub(r"<i>\1</i>", text)
    text = _ITALIC2_RE.sub(r"<i>\1</i>", text)

    def restore(m: re.Match) -> str:
        try:
            return placeholders[int(m.group(1))]
        except (ValueError, IndexError):
            return m.group(0)
    text = re.sub(r"\x00(\d+)\x00", restore, text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_markdown(text: str, limit: int = MD_LIMIT) -> List[str]:
    text = (text or "").replace("\r\n", "\n")
    if len(text) <= limit:
        return [text] if text else []
    lines = text.split("\n")
    chunks: List[str] = []
    current: List[str] = []
    size = 0
    in_fence = False
    fence_lang = ""

    def flush() -> None:
        nonlocal current, size
        if current:
            chunks.append("\n".join(current))
            current = []
            size = 0
    for line in lines:
        stripped = line.lstrip()
        is_fence = stripped.startswith("```")
        add = len(line) + 1
        if size + add > limit and not in_fence and current:
            split_at = -1
            for idx in range(len(current) - 1, max(len(current) - 40, -1), -1):
                if not current[idx].strip():
                    split_at = idx
                    break
            if split_at > 0:
                keep = current[split_at + 1 :]
                current = current[:split_at]
                flush()
                current = list(keep)
                size = sum(len(x) + 1 for x in current)
            else:
                flush()
        if size + add > limit and in_fence and current:
            current.append("```")
            flush()
            current = [f"```{fence_lang}".rstrip(), line if is_fence else line]
            if is_fence:
                current = [line]
                in_fence = False
            else:
                current = [f"```{fence_lang}".rstrip(), line]
            size = sum(len(x) + 1 for x in current)
            continue
        current.append(line)
        size += add
        if is_fence:
            if not in_fence:
                in_fence = True
                fence_lang = stripped[3:].strip()
            else:
                in_fence = False
                fence_lang = ""
    if in_fence and current:
        current.append("```")
    flush()
    final: List[str] = []
    for chunk in chunks:
        while len(chunk) > limit:
            final.append(chunk[:limit])
            chunk = chunk[limit:]
        if chunk:
            final.append(chunk)
    return final or [""]


def split_html(text: str, limit: int = TG_LIMIT) -> List[str]:
    return [md_to_html(chunk) for chunk in split_markdown(text, MD_LIMIT)]


def tail_text(text: str, limit: int, marker: str = "…") -> str:
    if len(text) <= limit:
        return text
    cut = text[-limit:]
    nl = cut.find("\n")
    if 0 < nl < 200:
        cut = cut[nl + 1 :]
    return marker + " " + cut


def strip_markdown(text: str) -> str:
    text = re.sub(r"```[^\n]*\n(.*?)```", r"\1", text or "", flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.S)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", text, flags=re.S)
    text = re.sub(r"~~(.+?)~~", r"\1", text, flags=re.S)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.M)
    return text.strip()
