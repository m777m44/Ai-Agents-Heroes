# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import asyncio
import json
import logging
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
log = logging.getLogger("mh3.store")
SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    chat_id        INTEGER PRIMARY KEY,
    model          TEXT    NOT NULL DEFAULT '',
    system         TEXT    NOT NULL DEFAULT '',
    temperature    REAL    NOT NULL DEFAULT 1.0,
    summary        TEXT    NOT NULL DEFAULT '',
    messages       TEXT    NOT NULL DEFAULT '[]',
    show_reasoning INTEGER NOT NULL DEFAULT 0,
    title          TEXT    NOT NULL DEFAULT '',
    steps_total    INTEGER NOT NULL DEFAULT 0,
    updated_at     REAL    NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id    INTEGER NOT NULL,
    title      TEXT    NOT NULL DEFAULT '',
    body       TEXT    NOT NULL DEFAULT '',
    tags       TEXT    NOT NULL DEFAULT '',
    created_at REAL    NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_notes_chat ON notes(chat_id);
CREATE TABLE IF NOT EXISTS usage (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ts            REAL    NOT NULL,
    chat_id       INTEGER NOT NULL,
    model         TEXT    NOT NULL DEFAULT '',
    input_tokens  INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens  INTEGER NOT NULL DEFAULT 0,
    cost_usd      REAL    NOT NULL DEFAULT 0,
    generation_ms INTEGER NOT NULL DEFAULT 0,
    steps         INTEGER NOT NULL DEFAULT 0,
    tool_calls    INTEGER NOT NULL DEFAULT 0,
    ok            INTEGER NOT NULL DEFAULT 1,
    note          TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_usage_ts ON usage(ts);
CREATE TABLE IF NOT EXISTS tool_log (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    ts       REAL    NOT NULL,
    chat_id  INTEGER NOT NULL,
    tool     TEXT    NOT NULL DEFAULT '',
    args     TEXT    NOT NULL DEFAULT '',
    ok       INTEGER NOT NULL DEFAULT 1,
    ms       INTEGER NOT NULL DEFAULT 0,
    preview  TEXT    NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS reminders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id    INTEGER NOT NULL,
    text       TEXT    NOT NULL DEFAULT '',
    due_ts     REAL    NOT NULL DEFAULT 0,
    created_at REAL    NOT NULL DEFAULT 0,
    done       INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS kv (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT ''
);
"""


@dataclass
class Session:
    chat_id: int
    model: str = ""
    system: str = ""
    temperature: float = 1.0
    summary: str = ""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    show_reasoning: bool = False
    title: str = ""
    steps_total: int = 0
    updated_at: float = field(default_factory=time.time)

    def to_row(self) -> tuple:
        return (
            self.chat_id, self.model, self.system, float(self.temperature), self.summary,
            json.dumps(self.messages, ensure_ascii=False), int(self.show_reasoning),
            self.title, int(self.steps_total), time.time(),
        )

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Session":
        try:
            messages = json.loads(row["messages"] or "[]")
        except (ValueError, TypeError):
            messages = []
        return cls(
            chat_id=int(row["chat_id"]),
            model=row["model"] or "",
            system=row["system"] or "",
            temperature=float(row["temperature"] or 1.0),
            summary=row["summary"] or "",
            messages=messages if isinstance(messages, list) else [],
            show_reasoning=bool(row["show_reasoning"]),
            title=row["title"] or "",
            steps_total=int(row["steps_total"] or 0),
            updated_at=float(row["updated_at"] or time.time()),
        )

    @property
    def turn_count(self) -> int:
        return sum(1 for m in self.messages if m.get("role") == "user")


class Store:

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None

    def _db(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.path), check_same_thread=False, timeout=30)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
            self._conn.executescript(SCHEMA)
            self._conn.commit()
        return self._conn

    def _run_sync(self, fn, *args, **kwargs):
        with self._lock:
            db = self._db()
            out = fn(db, *args, **kwargs)
            return out

    async def _run(self, fn, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._run_sync(fn, *args, **kwargs))

    async def init(self) -> None:
        await self._run(lambda db: db.execute("SELECT 1"))
        log.info("قاعدة البيانات جاهزة: %s", self.path)

    async def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    async def load_session(self, chat_id: int, defaults: Optional[Dict[str, Any]] = None) -> Session:

        def _load(db: sqlite3.Connection) -> Optional[Session]:
            row = db.execute("SELECT * FROM sessions WHERE chat_id=?", (chat_id,)).fetchone()
            return Session.from_row(row) if row else None
        sess = await self._run(_load)
        if sess is None:
            sess = Session(chat_id=chat_id)
            if defaults:
                for k, v in defaults.items():
                    if hasattr(sess, k) and v not in (None, ""):
                        setattr(sess, k, v)
            await self.save_session(sess)
        else:
            changed = False
            if defaults:
                if not sess.model and defaults.get("model"):
                    sess.model = defaults["model"]
                    changed = True
            if changed:
                await self.save_session(sess)
        return sess

    async def save_session(self, sess: Session) -> None:

        def _save(db: sqlite3.Connection) -> None:
            db.execute(
                """INSERT INTO sessions
                   (chat_id, model, system, temperature, summary, messages,
                    show_reasoning, title, steps_total, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(chat_id) DO UPDATE SET
                     model=excluded.model, system=excluded.system,
                     temperature=excluded.temperature, summary=excluded.summary,
                     messages=excluded.messages, show_reasoning=excluded.show_reasoning,
                     title=excluded.title, steps_total=excluded.steps_total,
                     updated_at=excluded.updated_at""",
                sess.to_row(),
            )
            db.commit()
        await self._run(_save)

    async def delete_session(self, chat_id: int) -> None:

        def _del(db: sqlite3.Connection) -> None:
            db.execute("DELETE FROM sessions WHERE chat_id=?", (chat_id,))
            db.commit()
        await self._run(_del)

    async def all_sessions(self) -> List[Session]:

        def _all(db: sqlite3.Connection) -> List[Session]:
            return [Session.from_row(r) for r in db.execute("SELECT * FROM sessions").fetchall()]
        return await self._run(_all)

    async def add_note(self, chat_id: int, title: str, body: str, tags: str = "") -> int:

        def _add(db: sqlite3.Connection) -> int:
            cur = db.execute(
                "INSERT INTO notes(chat_id,title,body,tags,created_at) VALUES (?,?,?,?,?)",
                (chat_id, title.strip()[:200], body.strip(), tags.strip()[:200], time.time()),
            )
            db.commit()
            return int(cur.lastrowid or 0)
        return await self._run(_add)

    async def search_notes(self, chat_id: int, query: str = "", limit: int = 8) -> List[Dict[str, Any]]:

        def _search(db: sqlite3.Connection) -> List[Dict[str, Any]]:
            sql = "SELECT id,title,body,tags,created_at FROM notes WHERE chat_id=?"
            params: List[Any] = [chat_id]
            if query:
                like = f"%{query}%"
                sql += " AND (title LIKE ? OR body LIKE ? OR tags LIKE ?)"
                params += [like, like, like]
            sql += " ORDER BY created_at DESC LIMIT ?"
            params.append(int(limit))
            return [dict(r) for r in db.execute(sql, params).fetchall()]
        return await self._run(_search)

    async def delete_note(self, chat_id: int, note_id: int) -> bool:

        def _del(db: sqlite3.Connection) -> bool:
            cur = db.execute("DELETE FROM notes WHERE id=? AND chat_id=?", (note_id, chat_id))
            db.commit()
            return cur.rowcount > 0
        return await self._run(_del)

    async def count_notes(self, chat_id: int) -> int:

        def _c(db: sqlite3.Connection) -> int:
            return int(db.execute("SELECT COUNT(*) c FROM notes WHERE chat_id=?", (chat_id,)).fetchone()["c"])
        return await self._run(_c)

    async def log_usage(self, chat_id: int, model: str, usage: Dict[str, Any],
                        steps: int = 0, tool_calls: int = 0, ok: bool = True, note: str = "") -> None:

        def _log(db: sqlite3.Connection) -> None:
            db.execute(
                """INSERT INTO usage(ts,chat_id,model,input_tokens,output_tokens,total_tokens,
                                     cost_usd,generation_ms,steps,tool_calls,ok,note)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (time.time(), chat_id, model, int(usage.get("input_tokens", 0)),
                 int(usage.get("output_tokens", 0)), int(usage.get("total_tokens", 0)),
                 float(usage.get("cost_usd", 0.0)), int(usage.get("generation_ms", 0)),
                 int(steps), int(tool_calls), int(ok), note[:300]),
            )
            db.execute("DELETE FROM usage WHERE ts < ?", (time.time() - 86400 * 365,))
            db.commit()
        await self._run(_log)

    async def usage_summary(self, chat_id: Optional[int] = None, days: int = 7) -> Dict[str, Any]:

        def _sum(db: sqlite3.Connection) -> Dict[str, Any]:
            since = time.time() - 86400 * days
            sql = """SELECT COUNT(*) requests, COALESCE(SUM(input_tokens),0) in_tok,
                            COALESCE(SUM(output_tokens),0) out_tok,
                            COALESCE(SUM(total_tokens),0) tot,
                            COALESCE(SUM(cost_usd),0) cost,
                            COALESCE(SUM(generation_ms),0) ms,
                            COALESCE(SUM(steps),0) steps,
                            COALESCE(SUM(tool_calls),0) tools,
                            COALESCE(SUM(ok),0) ok
                     FROM usage WHERE ts >= ?"""
            params: List[Any] = [since]
            if chat_id is not None:
                sql += " AND chat_id = ?"
                params.append(chat_id)
            row = db.execute(sql, params).fetchone()
            models = {}
            msql = """SELECT model, COUNT(*) c, COALESCE(SUM(total_tokens),0) t
                      FROM usage WHERE ts >= ?""" + (" AND chat_id=?" if chat_id is not None else "") + \
                   " GROUP BY model ORDER BY c DESC LIMIT 6"
            for r in db.execute(msql, params).fetchall():
                models[r["model"]] = {"requests": r["c"], "tokens": r["t"]}
            return {
                "days": days,
                "requests": int(row["requests"] or 0),
                "input_tokens": int(row["in_tok"] or 0),
                "output_tokens": int(row["out_tok"] or 0),
                "total_tokens": int(row["tot"] or 0),
                "cost_usd": float(row["cost"] or 0.0),
                "generation_ms": int(row["ms"] or 0),
                "steps": int(row["steps"] or 0),
                "tool_calls": int(row["tools"] or 0),
                "ok": int(row["ok"] or 0),
                "models": models,
            }
        return await self._run(_sum)

    async def log_tool(self, chat_id: int, tool: str, args: Any, ok: bool, ms: float, preview: str = "") -> None:

        def _log(db: sqlite3.Connection) -> None:
            try:
                argstr = json.dumps(args, ensure_ascii=False, default=str)[:600]
            except Exception:
                argstr = str(args)[:600]
            db.execute(
                "INSERT INTO tool_log(ts,chat_id,tool,args,ok,ms,preview) VALUES (?,?,?,?,?,?,?)",
                (time.time(), chat_id, tool, argstr, int(ok), int(ms), str(preview)[:400]),
            )
            db.execute("DELETE FROM tool_log WHERE ts < ?", (time.time() - 86400 * 14,))
            db.commit()
        await self._run(_log)

    async def tool_stats(self, chat_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:

        def _stats(db: sqlite3.Connection) -> List[Dict[str, Any]]:
            sql = """SELECT tool, COUNT(*) c, COALESCE(SUM(ok),0) ok, COALESCE(AVG(ms),0) avg_ms
                     FROM tool_log"""
            params: List[Any] = []
            if chat_id is not None:
                sql += " WHERE chat_id=?"
                params.append(chat_id)
            sql += " GROUP BY tool ORDER BY c DESC LIMIT ?"
            params.append(int(limit))
            return [dict(r) for r in db.execute(sql, params).fetchall()]
        return await self._run(_stats)

    async def add_reminder(self, chat_id: int, text: str, due_ts: float) -> int:

        def _add(db: sqlite3.Connection) -> int:
            cur = db.execute(
                "INSERT INTO reminders(chat_id,text,due_ts,created_at,done) VALUES (?,?,?,?,0)",
                (chat_id, text.strip()[:1000], float(due_ts), time.time()),
            )
            db.commit()
            return int(cur.lastrowid or 0)
        return await self._run(_add)

    async def pending_reminders(self) -> List[Dict[str, Any]]:

        def _p(db: sqlite3.Connection) -> List[Dict[str, Any]]:
            return [dict(r) for r in db.execute(
                "SELECT * FROM reminders WHERE done=0 ORDER BY due_ts ASC LIMIT 200").fetchall()]
        return await self._run(_p)

    async def complete_reminder(self, reminder_id: int) -> None:

        def _c(db: sqlite3.Connection) -> None:
            db.execute("UPDATE reminders SET done=1 WHERE id=?", (int(reminder_id),))
            db.commit()
        await self._run(_c)

    async def list_reminders(self, chat_id: int) -> List[Dict[str, Any]]:

        def _l(db: sqlite3.Connection) -> List[Dict[str, Any]]:
            return [dict(r) for r in db.execute(
                "SELECT * FROM reminders WHERE chat_id=? AND done=0 ORDER BY due_ts ASC",
                (chat_id,)).fetchall()]
        return await self._run(_l)

    async def kv_set(self, key: str, value: Any) -> None:

        def _s(db: sqlite3.Connection) -> None:
            db.execute("INSERT INTO kv(key,value) VALUES(?,?) "
                       "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                       (key, json.dumps(value, ensure_ascii=False, default=str)))
            db.commit()
        await self._run(_s)

    async def kv_get(self, key: str, default: Any = None) -> Any:

        def _g(db: sqlite3.Connection) -> Any:
            row = db.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
            if not row:
                return default
            try:
                return json.loads(row["value"])
            except (ValueError, TypeError):
                return row["value"]
        return await self._run(_g)
