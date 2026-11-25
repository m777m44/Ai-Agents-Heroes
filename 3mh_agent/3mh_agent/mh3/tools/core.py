# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import ast
import base64
import hashlib
import json
import math
import operator
import random as _random
import re
import secrets
import time as _time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from . import ToolRegistry, ToolResult, truncate
try:
    from zoneinfo import ZoneInfo, available_timezones
    _HAS_ZONEINFO = True
except Exception:
    ZoneInfo = None
    _HAS_ZONEINFO = False

    def available_timezones():
        return set()
_BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_CMP = {
    ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
    ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
}
_FUNCS: Dict[str, Any] = {
    "abs": abs, "round": round, "min": min, "max": max, "sum": sum, "len": len,
    "int": int, "float": float, "sqrt": math.sqrt, "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
    "log": math.log, "log2": math.log2, "log10": math.log10, "exp": math.exp,
    "sin": math.sin, "cos": math.cos, "tan": math.tan, "asin": math.asin,
    "acos": math.acos, "atan": math.atan, "atan2": math.atan2, "degrees": math.degrees,
    "radians": math.radians, "floor": math.floor, "ceil": math.ceil, "trunc": math.trunc,
    "factorial": math.factorial, "gcd": math.gcd, "hypot": math.hypot, "pow": pow,
}
_CONSTS: Dict[str, float] = {
    "pi": math.pi, "e": math.e, "tau": math.tau, "inf": math.inf,
    "phi": (1 + math.sqrt(5)) / 2,
}


def _eval_node(node: ast.AST, depth: int = 0) -> Any:
    if depth > 40:
        raise ValueError("التعبير معقّد جداً")
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, depth + 1)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float, complex)):
            return node.value
        raise ValueError("يُسمح بالأرقام فقط")
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left = _eval_node(node.left, depth + 1)
        right = _eval_node(node.right, depth + 1)
        if type(node.op) is ast.Pow and isinstance(right, (int, float)) and abs(right) > 512:
            raise ValueError("الأس كبير جداً")
        return _BIN_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand, depth + 1))
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, depth + 1)
        for op, comp in zip(node.ops, node.comparators):
            right = _eval_node(comp, depth + 1)
            if type(op) not in _CMP or not _CMP[type(op)](left, right):
                return False
            left = right
        return True
    if isinstance(node, ast.BoolOp):
        values = [_eval_node(v, depth + 1) for v in node.values]
        return all(values) if isinstance(node.op, ast.And) else any(values)
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _FUNCS:
            raise ValueError("دالة غير مسموحة")
        args = [_eval_node(a, depth + 1) for a in node.args]
        return _FUNCS[node.func.id](*args)
    if isinstance(node, ast.Name):
        if node.id in _CONSTS:
            return _CONSTS[node.id]
        raise ValueError(f"متغير غير معروف: {node.id}")
    if isinstance(node, ast.List):
        return [_eval_node(e, depth + 1) for e in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_eval_node(e, depth + 1) for e in node.elts)
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.List):
        seq = _eval_node(node.value, depth + 1)
        sl = node.slice
        idx = _eval_node(sl, depth + 1) if not isinstance(sl, ast.Slice) else None
        return seq[int(idx)]
    raise ValueError("صيغة غير مدعومة")


def safe_eval(expression: str) -> Any:
    expr = (expression or "").strip()
    if not expr:
        raise ValueError("تعبير فارغ")
    expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**")
    expr = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", expr)
    expr = expr.replace("\n", " ").strip().rstrip(";")
    if len(expr) > 2000:
        raise ValueError("التعبير طويل جداً")
    tree = ast.parse(expr, mode="eval")
    return _eval_node(tree)


def _tz(name: str) -> timezone:
    if not name:
        return timezone.utc
    name = name.strip()
    if _HAS_ZONEINFO:
        try:
            return ZoneInfo(name)
        except Exception:
            pass
    m = re.fullmatch(r"(?:UTC|GMT)?\s*([+-]?)(\d{1,2})(?::?(\d{2}))?", name, re.I)
    if m:
        sign = -1 if m.group(1) == "-" else 1
        hours = int(m.group(2))
        minutes = int(m.group(3) or 0)
        if 0 <= hours <= 14 and 0 <= minutes <= 59:
            return timezone(sign * timedelta(hours=hours, minutes=minutes))
    raise ValueError(f"منطقة زمنية غير معروفة: {name}")


def register(reg: ToolRegistry) -> None:
    t = reg.tool

    @t(name="current_time", category="core", timeout=10,
       description=(
           "Get the current date and time, optionally in a specific timezone. "
           "ALWAYS call this tool for any question about the current time, date, day of week, "
           "or relative dates — never guess them."
       ),
       parameters={
           "type": "object",
           "properties": {
               "timezone": {"type": "string", "description":
                            "IANA timezone name (e.g. Asia/Riyadh, Africa/Cairo, Europe/London) "
                            "or a UTC offset like UTC+3. Defaults to UTC."},
               "format": {"type": "string", "enum": ["iso", "human", "unix", "all"],
                          "description": "Output format. Default: all"},
           },
           "required": [],
           "additionalProperties": False,
       })

    async def current_time(args: Dict[str, Any], ctx) -> Dict[str, Any]:
        tzname = str(args.get("timezone") or "UTC")
        fmt = str(args.get("format") or "all").lower()
        try:
            tz = _tz(tzname)
        except ValueError as exc:
            sample = sorted(list(available_timezones()))[:0]
            hints = ["Asia/Riyadh", "Africa/Cairo", "Asia/Dubai", "Europe/London",
                     "America/New_York", "Asia/Tokyo", "UTC"]
            return {"error": str(exc), "examples": hints + sample}
        now = datetime.now(tz)
        out: Dict[str, Any] = {"timezone": tzname, "utc_offset": str(now.strftime("%z"))}
        if fmt in ("iso", "all"):
            out["iso"] = now.isoformat(timespec="seconds")
        if fmt in ("human", "all"):
            out["date"] = now.strftime("%Y-%m-%d")
            out["time"] = now.strftime("%H:%M:%S")
            out["day_of_week"] = now.strftime("%A")
            out["week"] = int(now.strftime("%V"))
        if fmt in ("unix", "all"):
            out["unix"] = int(now.timestamp())
        return out

    @t(name="calculator", category="core", timeout=10,
       description=(
           "Evaluate a mathematical expression precisely. Supports + - * / // % ** (), "
           "comparisons, lists, and functions: sqrt, log, log2, log10, exp, sin, cos, tan, "
           "asin, acos, atan, atan2, floor, ceil, round, abs, min, max, sum, factorial, gcd, "
           "hypot, and constants pi, e, tau, phi, inf. Percent is supported (50% = 0.5). "
           "Use this instead of doing arithmetic mentally."
       ),
       parameters={
           "type": "object",
           "properties": {
               "expression": {"type": "string", "description":
                              "The expression, e.g. '(12+30)*2', 'sqrt(2)', '15% of 200' → '0.15*200'"},
               "precision": {"type": "integer", "description": "Decimal places to round to (optional)"},
           },
           "required": ["expression"],
           "additionalProperties": False,
       })

    async def calculator(args: Dict[str, Any], ctx) -> Dict[str, Any]:
        expr = str(args.get("expression") or "")
        value = safe_eval(expr)
        precision = args.get("precision")
        result: Any = value
        if isinstance(value, float):
            if value == int(value) and abs(value) < 1e15:
                result = int(value)
            elif precision is not None:
                result = round(value, int(precision))
            else:
                result = round(value, 12)
        return {"expression": expr, "result": result, "type": type(value).__name__}

    @t(name="text_tool", category="core", timeout=15,
       description=(
           "Transform or analyse text. Operations: count (chars/words/lines), "
           "upper, lower, title, reverse, sort_lines, unique_lines, dedupe, "
           "regex_find, regex_replace, split, join, slugify, hash (md5/sha1/sha256), "
           "base64_encode, base64_decode, url_encode, url_decode, word_freq, truncate."
       ),
       parameters={
           "type": "object",
           "properties": {
               "operation": {"type": "string", "enum": [
                   "count", "upper", "lower", "title", "reverse", "sort_lines",
                   "unique_lines", "regex_find", "regex_replace", "split", "join",
                   "slugify", "hash", "base64_encode", "base64_decode",
                   "url_encode", "url_decode", "word_freq", "truncate"]},
               "text": {"type": "string", "description": "Input text"},
               "pattern": {"type": "string", "description": "Regex pattern (for regex_find/regex_replace/hash)"},
               "replacement": {"type": "string"},
               "separator": {"type": "string", "description": "For split/join (default newline)"},
               "algorithm": {"type": "string", "enum": ["md5", "sha1", "sha256", "sha512"]},
               "limit": {"type": "integer"},
           },
           "required": ["operation"],
           "additionalProperties": False,
       })

    async def text_tool(args: Dict[str, Any], ctx) -> Any:
        op = str(args.get("operation") or "").lower()
        text = str(args.get("text") or "")
        sep = args.get("separator")
        if op == "count":
            return {"chars": len(text), "chars_no_spaces": len(re.sub(r"\s", "", text)),
                    "words": len(text.split()), "lines": text.count("\n") + (1 if text else 0),
                    "sentences": len([s for s in re.split(r"[.!?؟]+\s", text) if s.strip()]),
                    "approx_tokens": max(1, len(text) // 4)}
        if op in ("upper", "lower", "title"):
            return {"result": getattr(text, op)()}
        if op == "reverse":
            return {"result": text[::-1]}
        if op == "sort_lines":
            lines = sorted(text.splitlines(), reverse=bool(args.get("reverse")))
            return {"result": "\n".join(lines), "lines": len(lines)}
        if op in ("unique_lines", "dedupe"):
            seen, out = set(), []
            for line in text.splitlines():
                key = line.strip()
                if key and key not in seen:
                    seen.add(key)
                    out.append(line)
            return {"result": "\n".join(out), "unique": len(out)}
        if op == "regex_find":
            pattern = str(args.get("pattern") or "")
            limit = int(args.get("limit") or 25)
            matches = [m.group(0) for m in re.finditer(pattern, text)][:limit]
            groups = [list(m.groups()) for m in re.finditer(pattern, text)][:limit]
            return {"count": len(matches), "matches": matches, "groups": groups}
        if op == "regex_replace":
            return {"result": re.sub(str(args.get("pattern") or ""),
                                     str(args.get("replacement") or ""), text)}
        if op == "split":
            parts = text.split(sep if sep is not None else "\n")
            limit = int(args.get("limit") or 100)
            return {"count": len(parts), "parts": parts[:limit]}
        if op == "join":
            try:
                items = json.loads(text) if text.strip().startswith("[") else text.splitlines()
            except Exception:
                items = text.splitlines()
            return {"result": (sep if sep is not None else "\n").join(str(i) for i in items)}
        if op == "slugify":
            slug = re.sub(r"[^\w\s-]", "", text.lower()).strip()
            slug = re.sub(r"[\s_]+", "-", slug)
            return {"result": slug}
        if op == "hash":
            algo = str(args.get("algorithm") or "sha256").lower()
            h = hashlib.new(algo) if algo in hashlib.algorithms_available else hashlib.sha256()
            h.update(text.encode("utf-8"))
            return {"algorithm": h.name, "hash": h.hexdigest()}
        if op == "base64_encode":
            return {"result": base64.b64encode(text.encode("utf-8")).decode()}
        if op == "base64_decode":
            try:
                return {"result": base64.b64decode(text.encode(), validate=False).decode("utf-8", "replace")}
            except Exception as exc:
                return {"error": f"base64 decode failed: {exc}"}
        if op == "url_encode":
            from urllib.parse import quote
            return {"result": quote(text, safe="")}
        if op == "url_decode":
            from urllib.parse import unquote
            return {"result": unquote(text)}
        if op == "word_freq":
            words = re.findall(r"[\w\u0600-\u06FF']+", text.lower())
            freq: Dict[str, int] = {}
            for w in words:
                freq[w] = freq.get(w, 0) + 1
            top = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[: int(args.get("limit") or 20)]
            return {"unique_words": len(freq), "total_words": len(words), "top": top}
        if op == "truncate":
            return {"result": truncate(text, int(args.get("limit") or 2000))}
        return {"error": f"عملية غير مدعومة: {op}"}

    @t(name="json_tool", category="core", timeout=15,
       description=(
           "Parse, validate, query or reshape JSON. Use 'query' with a dot/bracket path "
           "like 'data.items[0].name' to extract a value, 'format' to pretty-print, "
           "'minify' to compress, 'keys' to list top-level structure, 'convert' to turn "
           "JSON into CSV/markdown table."
       ),
       parameters={
           "type": "object",
           "properties": {
               "operation": {"type": "string", "enum": ["parse", "format", "minify", "query", "keys", "convert"]},
               "json_text": {"type": "string", "description": "The JSON document as text"},
               "path": {"type": "string", "description": "Dot path for query, e.g. items[2].id"},
               "output_format": {"type": "string", "enum": ["csv", "markdown"], "description": "For convert"},
           },
           "required": ["operation", "json_text"],
           "additionalProperties": False,
       })

    async def json_tool(args: Dict[str, Any], ctx) -> Any:
        op = str(args.get("operation") or "parse")
        raw = str(args.get("json_text") or "")
        try:
            data = json.loads(raw)
        except Exception as exc:
            return {"error": f"JSON غير صالح: {exc}"}
        if op == "parse":
            return {"valid": True, "type": type(data).__name__, "data": data}
        if op == "format":
            return {"result": truncate(json.dumps(data, ensure_ascii=False, indent=2), 12000)}
        if op == "minify":
            return {"result": truncate(json.dumps(data, ensure_ascii=False, separators=(",", ":")), 12000)}
        if op == "keys":

            def shape(obj: Any, depth: int = 0) -> Any:
                if depth > 4:
                    return "…"
                if isinstance(obj, dict):
                    return {k: shape(v, depth + 1) for k, v in list(obj.items())[:40]}
                if isinstance(obj, list):
                    return [shape(obj[0], depth + 1), f"…({len(obj)} items)"] if obj else []
                return type(obj).__name__
            return {"shape": shape(data)}
        if op == "query":
            path = str(args.get("path") or "")
            cur: Any = data
            try:
                for token in re.findall(r"[^.\[\]]+|\[\d+\]", path):
                    if token.startswith("["):
                        cur = cur[int(token[1:-1])]
                    else:
                        cur = cur[token] if not isinstance(cur, list) else cur[int(token)]
                return {"path": path, "value": cur}
            except Exception as exc:
                return {"error": f"المسار غير موجود: {exc}", "path": path}
        if op == "convert":
            fmt = str(args.get("output_format") or "markdown")
            rows = data if isinstance(data, list) else [data]
            if not rows or not isinstance(rows[0], dict):
                return {"error": "التحويل يتطلب مصفوفة كائنات"}
            cols = list({k for r in rows if isinstance(r, dict) for k in r})
            if fmt == "csv":
                import csv as _csv
                import io
                buf = io.StringIO()
                w = _csv.DictWriter(buf, fieldnames=cols)
                w.writeheader()
                for r in rows:
                    w.writerow({c: r.get(c, "") for c in cols})
                return {"result": truncate(buf.getvalue(), 12000), "rows": len(rows)}
            head = "| " + " | ".join(str(c) for c in cols) + " |"
            line = "|" + "|".join(["---"] * len(cols)) + "|"
            body = ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows[:200]]
            return {"result": truncate("\n".join([head, line] + body), 12000), "rows": len(rows)}
        return {"error": f"عملية غير مدعومة: {op}"}

    @t(name="random_tool", category="core", timeout=10,
       description=(
           "Generate randomness: 'number' (min/max integers), 'float', 'choice' (pick from list), "
           "'shuffle' (reorder list), 'dice' (e.g. 2d6), 'uuid', 'password' (secure), 'sample'."
       ),
       parameters={
           "type": "object",
           "properties": {
               "operation": {"type": "string", "enum":
                             ["number", "float", "choice", "shuffle", "dice", "uuid", "password", "sample"]},
               "minimum": {"type": "integer"}, "maximum": {"type": "integer"},
               "items": {"type": "array", "items": {"type": "string"}},
               "dice": {"type": "string", "description": "Like 2d6 or 1d20"},
               "length": {"type": "integer"},
               "count": {"type": "integer"},
           },
           "required": ["operation"],
           "additionalProperties": False,
       })

    async def random_tool(args: Dict[str, Any], ctx) -> Any:
        op = str(args.get("operation") or "number")
        if op == "number":
            lo, hi = int(args.get("minimum", 1)), int(args.get("maximum", 100))
            if lo > hi:
                lo, hi = hi, lo
            return {"result": _random.randint(lo, hi), "min": lo, "max": hi}
        if op == "float":
            lo, hi = float(args.get("minimum", 0)), float(args.get("maximum", 1))
            return {"result": round(_random.uniform(lo, hi), 6)}
        if op in ("choice", "sample"):
            items = args.get("items") or []
            if not items:
                return {"error": "القائمة فارغة"}
            if op == "choice":
                return {"result": _random.choice(items)}
            count = min(int(args.get("count") or 1), len(items))
            return {"result": _random.sample(list(items), count)}
        if op == "shuffle":
            items = list(args.get("items") or [])
            _random.shuffle(items)
            return {"result": items}
        if op == "dice":
            spec = str(args.get("dice") or "1d6")
            m = re.fullmatch(r"\s*(\d{1,3})\s*[dD]\s*(\d{1,4})\s*([+-]\s*\d{1,3})?\s*", spec)
            if not m:
                return {"error": f"صيغة نرد غير صالحة: {spec}"}
            n, sides = min(int(m.group(1)), 100), min(int(m.group(2)), 1000)
            modifier = int((m.group(3) or "0").replace(" ", ""))
            rolls = [_random.randint(1, sides) for _ in range(max(n, 1))]
            return {"rolls": rolls, "modifier": modifier, "total": sum(rolls) + modifier}
        if op == "uuid":
            import uuid as _uuid
            return {"result": str(_uuid.uuid4())}
        if op == "password":
            length = min(max(int(args.get("length") or 16), 4), 128)
            alphabet = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*-_"
            return {"result": "".join(secrets.choice(alphabet) for _ in range(length)), "length": length}
        return {"error": f"عملية غير مدعومة: {op}"}

    @t(name="sleep", category="core", timeout=130,
       description=(
           "Wait for a number of seconds before continuing. Use only when a delay is truly "
           "required (e.g. polling an external service). Maximum 120 seconds."
       ),
       parameters={
           "type": "object",
           "properties": {"seconds": {"type": "number", "description": "Seconds to wait (max 120)"}},
           "required": ["seconds"],
           "additionalProperties": False,
       })

    async def sleep_tool(args: Dict[str, Any], ctx) -> Dict[str, Any]:
        seconds = float(min(max(float(args.get("seconds") or 0), 0), 120))
        started = _time.monotonic()
        while _time.monotonic() - started < seconds:
            if ctx.cancel_event is not None and ctx.cancel_event.is_set():
                return {"slept": round(_time.monotonic() - started, 2), "cancelled": True}
            await _async_sleep(0.25)
        return {"slept": round(seconds, 2)}

    async def _async_sleep(seconds: float) -> None:
        import asyncio
        await asyncio.sleep(seconds)
