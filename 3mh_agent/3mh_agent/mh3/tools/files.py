# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import fnmatch
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List
from . import ToolRegistry, ToolResult, truncate
_MAX_READ = 400_000
_MAX_FILE_BYTES = 20 * 1024 * 1024
_TEXT_SUFFIXES = {
    ".txt", ".md", ".json", ".csv", ".tsv", ".log", ".py", ".js", ".ts", ".html",
    ".css", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".sh", ".sql", ".env",
    ".rst", ".tex", ".java", ".c", ".h", ".cpp", ".go", ".rs", ".rb", ".php", ".swift",
}


def _relative(ctx, path: Path) -> str:
    try:
        return str(path.relative_to(ctx.workspace.resolve()))
    except ValueError:
        return str(path)


def register(reg: ToolRegistry) -> None:
    t = reg.tool

    @t(name="file_read", category="files", timeout=20,
       description=(
           "Read a text file from the bot's sandboxed workspace (relative path). "
           "Optionally read a line range. Returns content plus metadata. "
           "Use file_list first to discover available files."
       ),
       parameters={
           "type": "object",
           "properties": {
               "path": {"type": "string", "description": "Relative path inside the workspace, e.g. notes/plan.md"},
               "start_line": {"type": "integer", "description": "1-based first line (optional)"},
               "end_line": {"type": "integer", "description": "1-based last line, inclusive (optional)"},
               "encoding": {"type": "string", "description": "Default utf-8"},
           },
           "required": ["path"],
           "additionalProperties": False,
       })

    async def file_read(args: Dict[str, Any], ctx) -> Any:
        try:
            target = ctx.resolve_path(str(args.get("path") or ""), must_exist=True)
        except (PermissionError, FileNotFoundError) as exc:
            return {"error": str(exc)}
        if target.is_dir():
            return {"error": "المسار مجلد وليس ملفاً — استخدم file_list",
                    "entries": [p.name for p in sorted(target.iterdir())[:200]]}
        size = target.stat().st_size
        if size > _MAX_FILE_BYTES:
            return {"error": f"الملف كبير جداً ({size // (1024 * 1024)}MB)", "path": _relative(ctx, target)}
        encoding = str(args.get("encoding") or "utf-8")
        try:
            text = target.read_text(encoding=encoding, errors="replace")
        except (OSError, LookupError) as exc:
            return {"error": f"تعذّرت القراءة: {exc}"}
        lines = text.splitlines()
        start = int(args.get("start_line") or 1)
        end = int(args.get("end_line") or len(lines))
        sliced = lines[max(start - 1, 0): max(end, start)]
        content = "\n".join(sliced)
        return {
            "path": _relative(ctx, target), "bytes": size, "lines_total": len(lines),
            "lines_returned": len(sliced), "truncated": len(content) > _MAX_READ,
            "content": truncate(content, _MAX_READ),
        }

    @t(name="file_write", category="files", timeout=25,
       description=(
           "Write (create or overwrite) a text file inside the sandboxed workspace, or append to it. "
           "Parent directories are created automatically. Use this to save generated code, reports, "
           "data files, CSV/JSON exports. Afterwards you can deliver it to the user with send_file."
       ),
       parameters={
           "type": "object",
           "properties": {
               "path": {"type": "string"},
               "content": {"type": "string"},
               "mode": {"type": "string", "enum": ["overwrite", "append"], "description": "Default overwrite"},
               "encoding": {"type": "string"},
           },
           "required": ["path", "content"],
           "additionalProperties": False,
       })

    async def file_write(args: Dict[str, Any], ctx) -> Any:
        raw_path = str(args.get("path") or "")
        content = args.get("content")
        if content is None:
            return {"error": "لا يوجد محتوى"}
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False, indent=2)
        try:
            target = ctx.resolve_path(raw_path)
        except PermissionError as exc:
            return {"error": str(exc)}
        if len(content) > 5_000_000:
            return {"error": "المحتوى كبير جداً (الحد 5MB)"}
        mode = str(args.get("mode") or "overwrite")
        encoding = str(args.get("encoding") or "utf-8")
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "a" if mode == "append" else "w", encoding=encoding) as fh:
                fh.write(content)
        except OSError as exc:
            return {"error": f"تعذّرت الكتابة: {exc}"}
        return {"path": _relative(ctx, target), "bytes": target.stat().st_size,
                "mode": mode, "lines": content.count("\n") + 1}

    @t(name="file_list", category="files", timeout=15,
       description=(
           "List files and folders in the sandboxed workspace (recursive optional), with sizes. "
           "Supports a glob pattern like '*.py' or 'reports/*'. Use it before reading or writing files."
       ),
       parameters={
           "type": "object",
           "properties": {
               "path": {"type": "string", "description": "Subdirectory (default: workspace root)"},
               "pattern": {"type": "string", "description": "Glob pattern to filter names"},
               "recursive": {"type": "boolean"},
               "limit": {"type": "integer", "description": "Max entries (default 200)"},
           },
           "required": [],
           "additionalProperties": False,
       })

    async def file_list(args: Dict[str, Any], ctx) -> Any:
        try:
            base = ctx.resolve_path(str(args.get("path") or "."), must_exist=True)
        except (PermissionError, FileNotFoundError) as exc:
            return {"error": str(exc)}
        if not base.is_dir():
            return {"error": "ليس مجلداً", "path": _relative(ctx, base)}
        recursive = bool(args.get("recursive"))
        pattern = str(args.get("pattern") or "").strip()
        limit = min(int(args.get("limit") or 200), 1000)
        entries: List[Dict[str, Any]] = []
        walker = base.rglob("*") if recursive else base.glob("*")
        for item in sorted(walker, key=lambda p: (not p.is_dir(), str(p).lower())):
            rel = _relative(ctx, item)
            if pattern and not (fnmatch.fnmatch(item.name, pattern) or fnmatch.fnmatch(rel, pattern)):
                continue
            try:
                stat = item.stat()
            except OSError:
                continue
            entries.append({
                "name": rel, "type": "dir" if item.is_dir() else "file",
                "bytes": 0 if item.is_dir() else stat.st_size,
                "modified": int(stat.st_mtime),
            })
            if len(entries) >= limit:
                break
        total = sum(e["bytes"] for e in entries if e["type"] == "file")
        return {"path": _relative(ctx, base), "count": len(entries), "total_bytes": total,
                "entries": entries, "workspace": str(ctx.workspace)}

    @t(name="file_search", category="files", timeout=30,
       description=(
           "Search file contents (grep) or file names inside the workspace using a regular "
           "expression or plain text. Returns matching lines with file and line number."
       ),
       parameters={
           "type": "object",
           "properties": {
               "query": {"type": "string", "description": "Regex or plain text"},
               "path": {"type": "string", "description": "Directory or file to search in (default: workspace)"},
               "is_regex": {"type": "boolean", "description": "Treat query as regex (default false)"},
               "ignore_case": {"type": "boolean"},
               "max_matches": {"type": "integer", "description": "Default 60"},
               "name_pattern": {"type": "string", "description": "Only search files matching glob, e.g. *.py"},
           },
           "required": ["query"],
           "additionalProperties": False,
       })

    async def file_search(args: Dict[str, Any], ctx) -> Any:
        query = str(args.get("query") or "")
        if not query:
            return {"error": "استعلام فارغ"}
        try:
            base = ctx.resolve_path(str(args.get("path") or "."), must_exist=True)
        except (PermissionError, FileNotFoundError) as exc:
            return {"error": str(exc)}
        flags = re.IGNORECASE if args.get("ignore_case", True) else 0
        try:
            rx = re.compile(query, flags) if args.get("is_regex") else None
        except re.error as exc:
            return {"error": f"تعبير نمطي غير صالح: {exc}"}
        needle = query.lower() if not args.get("ignore_case", True) else query.lower()
        name_pattern = str(args.get("name_pattern") or "")
        max_matches = min(int(args.get("max_matches") or 60), 500)
        matches: List[Dict[str, Any]] = []
        files = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file()]
        scanned = 0
        for file in files:
            if name_pattern and not fnmatch.fnmatch(file.name, name_pattern):
                continue
            if file.suffix.lower() not in _TEXT_SUFFIXES and file.stat().st_size > 2_000_000:
                continue
            if file.stat().st_size > _MAX_FILE_BYTES:
                continue
            scanned += 1
            try:
                text = file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                hit = bool(rx.search(line)) if rx else (needle in line.lower())
                if hit:
                    matches.append({"file": _relative(ctx, file), "line": lineno,
                                    "text": line.strip()[:300]})
                    if len(matches) >= max_matches:
                        break
            if len(matches) >= max_matches:
                break
        return {"query": query, "files_scanned": scanned, "matches": len(matches),
                "results": matches, "truncated": len(matches) >= max_matches}

    @t(name="file_delete", category="files", timeout=15, admin_only=True, dangerous=True,
       description="Delete a file or empty directory inside the workspace. Admin only. Use with care.",
       parameters={
           "type": "object",
           "properties": {
               "path": {"type": "string"},
               "recursive": {"type": "boolean", "description": "Delete non-empty directories recursively"},
           },
           "required": ["path"],
           "additionalProperties": False,
       })

    async def file_delete(args: Dict[str, Any], ctx) -> Any:
        try:
            target = ctx.resolve_path(str(args.get("path") or ""), must_exist=True)
        except (PermissionError, FileNotFoundError) as exc:
            return {"error": str(exc)}
        if target == ctx.workspace.resolve():
            return {"error": "لا يمكن حذف مجلد العمل نفسه"}
        try:
            if target.is_dir():
                if args.get("recursive"):
                    import shutil
                    shutil.rmtree(target)
                else:
                    target.rmdir()
            else:
                target.unlink()
        except OSError as exc:
            return {"error": f"تعذّر الحذف: {exc}"}
        return {"deleted": _relative(ctx, target)}

    @t(name="file_copy", category="files", timeout=15,
       description="Copy or move/rename a file inside the workspace.",
       parameters={
           "type": "object",
           "properties": {
               "source": {"type": "string"}, "destination": {"type": "string"},
               "move": {"type": "boolean", "description": "Move instead of copy"},
           },
           "required": ["source", "destination"],
           "additionalProperties": False,
       })

    async def file_copy(args: Dict[str, Any], ctx) -> Any:
        import shutil
        try:
            src = ctx.resolve_path(str(args.get("source") or ""), must_exist=True)
            dst = ctx.resolve_path(str(args.get("destination") or ""))
        except (PermissionError, FileNotFoundError) as exc:
            return {"error": str(exc)}
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if args.get("move"):
                shutil.move(str(src), str(dst))
            elif src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        except OSError as exc:
            return {"error": f"فشلت العملية: {exc}"}
        return {"from": _relative(ctx, src), "to": _relative(ctx, dst),
                "moved": bool(args.get("move"))}

    @t(name="file_info", category="files", timeout=15,
       description="Get metadata about a file or directory: size, type, modified time, line count for text files, and a short preview.",
       parameters={
           "type": "object",
           "properties": {"path": {"type": "string"}},
           "required": ["path"],
           "additionalProperties": False,
       })

    async def file_info(args: Dict[str, Any], ctx) -> Any:
        try:
            target = ctx.resolve_path(str(args.get("path") or ""), must_exist=True)
        except (PermissionError, FileNotFoundError) as exc:
            return {"error": str(exc)}
        stat = target.stat()
        out: Dict[str, Any] = {
            "path": _relative(ctx, target), "type": "dir" if target.is_dir() else "file",
            "bytes": stat.st_size, "modified": int(stat.st_mtime),
            "suffix": target.suffix, "absolute": str(target),
        }
        if target.is_file() and target.suffix.lower() in _TEXT_SUFFIXES and stat.st_size < 2_000_000:
            try:
                text = target.read_text(encoding="utf-8", errors="replace")
                out["lines"] = text.count("\n") + 1
                out["preview"] = truncate(text, 800)
            except OSError:
                pass
        elif target.is_dir():
            children = sorted(target.iterdir(), key=lambda p: p.name)
            out["entries"] = len(children)
            out["names"] = [c.name for c in children[:100]]
        return out

    @t(name="send_file", category="files", timeout=30,
       description=(
           "Deliver a file from the workspace to the current Telegram chat (as a document, "
           "or as a photo when it is an image). Use this after generating a report, chart data, "
           "code file, CSV/JSON export, etc. The file is sent immediately and also mentioned "
           "in your final answer."
       ),
       parameters={
           "type": "object",
           "properties": {
               "path": {"type": "string", "description": "File path inside the workspace"},
               "caption": {"type": "string", "description": "Optional caption text"},
           },
           "required": ["path"],
           "additionalProperties": False,
       })

    async def send_file(args: Dict[str, Any], ctx) -> Any:
        try:
            target = ctx.resolve_path(str(args.get("path") or ""), must_exist=True)
        except (PermissionError, FileNotFoundError) as exc:
            return {"error": str(exc)}
        if target.is_dir():
            return {"error": "لا يمكن إرسال مجلد"}
        if target.stat().st_size > 45 * 1024 * 1024:
            return {"error": "الملف أكبر من 45MB (حد تليجرام للبوتات)"}
        caption = str(args.get("caption") or "")[:1000]
        if ctx.send_file is not None:
            try:
                await ctx.send_file(str(target), caption)
            except Exception as exc:
                return {"error": f"فشل الإرسال: {exc}", "path": _relative(ctx, target)}
            return {"delivered": True, "status": "sent_to_chat_now",
                    "path": _relative(ctx, target), "bytes": target.stat().st_size,
                    "caption": caption}
        ctx.artifacts.append({"type": "file", "path": str(target), "caption": caption})
        return {"delivered": True, "status": "queued_for_final_reply",
                "note": "The file is attached to the final answer automatically. "
                        "Do not retry or call this tool again for the same file.",
                "path": _relative(ctx, target), "bytes": target.stat().st_size,
                "caption": caption}
