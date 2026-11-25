# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import json
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List
from . import ToolRegistry, truncate
__version__ = "1.0.0"


def _parse_when(raw: Any) -> float:
    if raw is None:
        raise ValueError("لا يوجد وقت")
    if isinstance(raw, (int, float)):
        val = float(raw)
        return time.time() + val if val < 10_000 else val
    text = str(raw).strip().lower()
    if not text:
        raise ValueError("وقت فارغ")
    now = datetime.now()
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(s|sec|second|seconds|ث|ثانية|دقيقة)?\s*", text)
    if m and not m.group(2):
        return time.time() + float(m.group(1))
    units = {
        "s": 1, "sec": 1, "second": 1, "seconds": 1, "ث": 1, "ثانية": 1, "ثواني": 1,
        "m": 60, "min": 60, "minute": 60, "minutes": 60, "د": 60, "دقيقة": 60, "دقائق": 60,
        "h": 3600, "hr": 3600, "hour": 3600, "hours": 3600, "س": 3600, "ساعة": 3600, "ساعات": 3600,
        "d": 86400, "day": 86400, "days": 86400, "ي": 86400, "يوم": 86400, "أيام": 86400,
        "w": 604800, "week": 604800, "weeks": 604800, "أسبوع": 604800, "اسبوع": 604800,
    }
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([a-z\u0600-\u06FF]+)\s*", text)
    if m and m.group(2) in units:
        return time.time() + float(m.group(1)) * units[m.group(2)]
    if text in ("now", "الآن", "الاَن"):
        return time.time()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M %z", "%Y-%m-%d", "%d/%m/%Y %H:%M",
                "%H:%M:%S", "%H:%M"):
        try:
            parsed = datetime.strptime(text, fmt)
            if fmt in ("%H:%M:%S", "%H:%M"):
                parsed = now.replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)
                if parsed <= now:
                    parsed += timedelta(days=1)
            elif fmt == "%Y-%m-%d":
                parsed = parsed.replace(hour=9)
            return parsed.timestamp()
        except ValueError:
            continue
    raise ValueError(f"تعذّر فهم الوقت: {raw}")


def register(reg: ToolRegistry) -> None:
    t = reg.tool

    @t(name="memory_save", category="memory", timeout=15,
       description=(
           "Save a durable note/memory for this chat (facts, preferences, decisions, task state, "
           "credentials the user asked to remember, plans). Memories persist across restarts and "
           "are searchable later with memory_search. Save proactively when the user shares "
           "something worth remembering."
       ),
       parameters={
           "type": "object",
           "properties": {
               "title": {"type": "string", "description": "Short label (max 200 chars)"},
               "body": {"type": "string", "description": "The content to remember"},
               "tags": {"type": "string", "description": "Comma-separated tags for retrieval"},
           },
           "required": ["title", "body"],
           "additionalProperties": False,
       })

    async def memory_save(args: Dict[str, Any], ctx) -> Any:
        title = str(args.get("title") or "").strip()[:200]
        body = str(args.get("body") or "").strip()
        if not body:
            return {"error": "المحتوى فارغ"}
        note_id = await ctx.store.add_note(ctx.chat_id, title, body[:20000],
                                           str(args.get("tags") or ""))
        return {"saved": True, "id": note_id, "title": title, "chars": len(body)}

    @t(name="memory_search", category="memory", timeout=15,
       description=(
           "Search saved memories/notes for this chat by keyword. Returns matching notes with ids. "
           "Use it before answering questions about earlier decisions, saved data, or user preferences."
       ),
       parameters={
           "type": "object",
           "properties": {
               "query": {"type": "string", "description": "Keyword(s); empty string lists recent notes"},
               "limit": {"type": "integer", "description": "Max notes to return (default 8)"},
           },
           "required": [],
           "additionalProperties": False,
       })

    async def memory_search(args: Dict[str, Any], ctx) -> Any:
        rows = await ctx.store.search_notes(ctx.chat_id, str(args.get("query") or ""),
                                            int(args.get("limit") or 8))
        return {"count": len(rows), "notes": [
            {"id": r["id"], "title": r["title"], "tags": r["tags"],
             "body": truncate(r["body"], 2000),
             "created": datetime.fromtimestamp(r["created_at"]).strftime("%Y-%m-%d %H:%M")}
            for r in rows]}

    @t(name="memory_delete", category="memory", timeout=15,
       description="Delete a saved memory by id.",
       parameters={
           "type": "object",
           "properties": {"note_id": {"type": "integer"}},
           "required": ["note_id"],
           "additionalProperties": False,
       })

    async def memory_delete(args: Dict[str, Any], ctx) -> Any:
        ok = await ctx.store.delete_note(ctx.chat_id, int(args.get("note_id") or 0))
        return {"deleted": ok, "id": int(args.get("note_id") or 0)}

    @t(name="set_reminder", category="memory", timeout=20,
       description=(
           "Schedule a message to be delivered to this chat later. 'when' accepts relative forms "
           "('30s', '15m', '2h', '3d', '1 week') or absolute ('2026-10-25 09:00', '17:30'). "
           "Use it for follow-ups, timers, scheduled reports. Also list or cancel reminders."
       ),
       parameters={
           "type": "object",
           "properties": {
               "action": {"type": "string", "enum": ["create", "list", "cancel"]},
               "when": {"type": "string", "description": "When to fire (for create)"},
               "message": {"type": "string", "description": "Reminder text to send"},
               "reminder_id": {"type": "integer", "description": "For cancel"},
           },
           "required": ["action"],
           "additionalProperties": False,
       })

    async def set_reminder(args: Dict[str, Any], ctx) -> Any:
        action = str(args.get("action") or "create")
        if action == "list":
            rows = await ctx.store.list_reminders(ctx.chat_id)
            return {"count": len(rows), "reminders": [
                {"id": r["id"], "text": r["text"],
                 "due": datetime.fromtimestamp(r["due_ts"]).strftime("%Y-%m-%d %H:%M:%S"),
                 "in_seconds": max(0, int(r["due_ts"] - time.time()))} for r in rows]}
        if action == "cancel":
            rid = int(args.get("reminder_id") or 0)
            await ctx.store.complete_reminder(rid)
            return {"cancelled": rid}
        try:
            due = _parse_when(args.get("when"))
        except ValueError as exc:
            return {"error": str(exc),
                    "examples": ["30s", "15m", "2h", "3d", "2026-10-25 09:00", "17:30"]}
        delay = due - time.time()
        if delay < 1:
            return {"error": "الوقت في الماضي أو أقل من ثانية"}
        if delay > 400 * 86400:
            return {"error": "الحد الأقصى للتذكير 400 يوم"}
        message = str(args.get("message") or "⏰ تذكير").strip()[:1000]
        rid = await ctx.store.add_reminder(ctx.chat_id, message, due)
        if ctx.schedule_reminder is not None:
            try:
                await ctx.schedule_reminder(rid, ctx.chat_id, message, delay)
            except Exception as exc:
                return {"error": f"تعذّر جدولة التذكير: {exc}", "id": rid}
        return {"scheduled": True, "id": rid, "message": message,
                "due": datetime.fromtimestamp(due).strftime("%Y-%m-%d %H:%M:%S"),
                "in_seconds": int(delay)}

    @t(name="ask_model", category="agent", timeout=170,
       description=(
           "Delegate a self-contained sub-task to another model (a specialist or a stronger/weaker "
           "one) and get its text answer. The sub-agent has NO tools and NO access to this "
           "conversation — put everything it needs in the prompt. Use for: second opinions, "
           "translation with a specific model, code review by a coding model, summarising a huge "
           "document, or comparing answers. Specify model by id or alias (e.g. 'glm5', 'gpt', "
           "'qwen', 'kimi', '@cf/openai/gpt-oss-120b')."
       ),
       parameters={
           "type": "object",
           "properties": {
               "prompt": {"type": "string", "description": "Complete instructions + data for the sub-agent"},
               "model": {"type": "string", "description": "Model id or alias (default: bot's utility model)"},
               "system": {"type": "string", "description": "Optional system prompt for the sub-agent"},
               "temperature": {"type": "number"},
           },
           "required": ["prompt"],
           "additionalProperties": False,
       })

    async def ask_model(args: Dict[str, Any], ctx) -> Any:
        if ctx.ask_model is None:
            return {"error": "تفويض النماذج غير متاح في هذا السياق"}
        prompt = str(args.get("prompt") or "").strip()
        if not prompt:
            return {"error": "موجز فارغ"}
        if len(prompt) > 60_000:
            return {"error": "الموجز طويل جداً (الحد 60 ألف حرف)"}
        started = time.monotonic()
        try:
            answer, used_model = await ctx.ask_model(
                prompt=prompt,
                model=str(args.get("model") or ""),
                system=str(args.get("system") or ""),
                temperature=args.get("temperature"),
            )
        except Exception as exc:
            return {"error": f"فشل التفويض: {type(exc).__name__}: {exc}"[:400]}
        return {"model": used_model, "seconds": round(time.monotonic() - started, 1),
                "answer": truncate(answer, 12000)}

    @t(name="self_info", category="agent", timeout=15,
       description=(
           "Report the bot's own current configuration: active model and fallbacks, enabled tools "
           "by category, workspace path and files, agent settings (max steps, timeouts), memory "
           "stats, and server time. Call it to answer 'what can you do?' accurately instead of guessing."
       ),
       parameters={
           "type": "object",
           "properties": {"section": {"type": "string",
                                     "enum": ["all", "tools", "model", "workspace", "memory"]}},
           "required": [],
           "additionalProperties": False,
       })

    async def self_info(args: Dict[str, Any], ctx) -> Any:
        section = str(args.get("section") or "all")
        registry = ctx.extra.get("registry")
        session = ctx.extra.get("session")
        out: Dict[str, Any] = {
            "version": __version__,
            "now": datetime.now().isoformat(timespec="seconds"),
            "chat_id": ctx.chat_id,
            "is_admin": ctx.is_admin,
            "language": ctx.language,
        }
        if section in ("all", "model"):
            out["model"] = getattr(session, "model", None) or (ctx.settings.default_model if ctx.settings else "")
            out["fallbacks"] = list(ctx.settings.fallback_models) if ctx.settings else []
            out["temperature"] = getattr(session, "temperature", 1.0)
            out["max_steps"] = ctx.settings.max_steps if ctx.settings else 10
            out["step_timeout"] = ctx.settings.step_timeout if ctx.settings else 0
        enabled = registry.enabled(admin=ctx.is_admin) if registry is not None else []
        grouped: Dict[str, List[str]] = {}
        for spec in enabled:
            grouped.setdefault(spec.category, []).append(spec.name)
        out["tools_enabled"] = len(enabled)
        out["tools_total"] = len(registry.all) if registry is not None else 0
        out["tools_by_category"] = grouped
        if section in ("all", "workspace"):
            ws = ctx.workspace
            files = [str(p.relative_to(ws)) for p in ws.rglob("*") if p.is_file()][:200]
            out["workspace"] = str(ws)
            out["workspace_files"] = len(files)
            out["files"] = files[:60]
        if section in ("all", "memory"):
            out["notes"] = await ctx.store.count_notes(ctx.chat_id)
            out["history_messages"] = len(getattr(session, "messages", []) or [])
            out["summary_chars"] = len(getattr(session, "summary", "") or "")
        return out
