#!/usr/bin/env python3
# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
BOT_NAME = "3mh agent"
BOT_VERSION = "2.0.0"
COMPANY_NAME = "3MH TECHNOLOGIES"
COMPANY_SITE = "http://3mh.pages.dev"
SUPPORT_URL = "t.me/j49_c"
CHANNEL_URL = "t.me/bshshshkk"
ENV_FILE = ".env"
DEFAULT_MODEL = "@cf/zai-org/glm-4.7-flash"
CLI_CHAT_ID = -1000
CLI_CHAT_ID_INTERACTIVE = -1001
CLI_USER_ID = 1
PROBE_TIMEOUT = 35
SELFTEST_MIN_TOOLS = 15
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from mh3 import __version__
from mh3.config import Settings
BANNER = (
    "╭──────────────────────────────────────────────────────────╮\n"
    f"│  🤖 {BOT_NAME} — {COMPANY_NAME:<28}        │\n"
    f"│  الإصدار {BOT_VERSION:<6} • {SUPPORT_URL:<16} • {CHANNEL_URL:<15} │\n"
    f"│  {COMPANY_SITE:<53}   │\n"
    "╰──────────────────────────────────────────────────────────╯"
)


def _load_settings(cli: bool = False) -> Settings:
    if cli and not os.environ.get("BOT_TOKEN"):
        os.environ.setdefault("BOT_TOKEN", "0:cli-mode")
        if Path(".env").is_file():
            pass
    settings = Settings.from_env()
    if cli and settings.bot_token == "0:cli-mode":
        settings.access_mode = "open"
    return settings


def _print_event(kind: str, text: str, data: Dict[str, Any]) -> None:
    dim = "\033[2m"
    cyan = "\033[36m"
    yellow = "\033[33m"
    red = "\033[31m"
    green = "\033[32m"
    reset = "\033[0m"
    if kind == "status":
        status = data.get("status")
        if status == "fallback":
            print(f"\n{yellow}🔁 تبديل إلى {data.get('next_model')} ({data.get('error')}){reset}")
        elif status == "retrying":
            print(f"\n{yellow}⏳ إعادة محاولة بعد {data.get('wait')}ث{reset}")
        elif status == "subagent":
            print(f"\n{cyan}🧩 تفويض {data.get('model')}{reset}")
        elif status == "compacting":
            print(f"\n{dim}🗜️ ضغط الذاكرة…{reset}")
    elif kind == "tool_call":
        args = json.dumps(data.get("input") or {}, ensure_ascii=False)
        print(f"\n{cyan}🔧 {data.get('tool_name')} {args[:160]}{reset}")
    elif kind == "tool_result":
        mark = f"{green}✅{reset}" if data.get("ok") else f"{red}❌ {data.get('error')}{reset}"
        preview = str(data.get("preview") or "")[:200].replace("\n", " ")
        print(f"{mark} {dim}{data.get('ms')}م.ث — {preview}{reset}")
    elif kind == "turn":
        print(f"\n{dim}── خطوة {data.get('step')}/{data.get('max_steps')} ──{reset}")
    elif kind == "error":
        print(f"\n{red}⚠️ {text}{reset}")
    elif kind == "notice":
        print(f"\n{dim}ℹ️ {text}{reset}")


async def _cli_turn(settings: Settings, prompt: str, chat_id: int = CLI_CHAT_ID) -> None:
    from mh3.agent import AgentCore
    from mh3.backend import ConnectionPool, StreamEvent
    from mh3.store import Store
    from mh3.tools import build_registry
    store = Store(settings.db_path)
    await store.init()
    registry = build_registry(settings)
    pool = ConnectionPool(settings)
    agent = AgentCore(settings, store, registry, pool, bot_name=BOT_NAME)

    async def on_event(ev: StreamEvent) -> None:
        if ev.kind == "text":
            sys.stdout.write(ev.text)
            sys.stdout.flush()
        else:
            _print_event(ev.kind, ev.text, ev.data)
    print(f"{BANNER}")
    print(f"🧠 {settings.default_model} | 🔧 {len(registry.all)} أداة | 💬 {prompt[:80]}\n")
    try:
        result = await agent.run(
            chat_id=chat_id, user_id=CLI_USER_ID, username="cli", user_name="CLI",
            is_admin=True, chat_type="private", text=prompt, on_event=on_event)
        print()
        if result.error:
            print(f"\n\033[31mخطأ: {result.error}\033[0m")
        elif result.cancelled:
            print("\n\033[33mأُلغي\033[0m")
        print(f"\n\033[2m{result.stats_line()}\033[0m")
        if result.tools:
            print(f"\033[2mالأدوات: {', '.join(t.name for t in result.tools)}\033[0m")
    finally:
        await pool.close_all()
        await store.close()


async def _cli_chat(settings: Settings) -> None:
    print(BANNER)
    print("محادثة تشخيصية في الطرفية — اكتب /exit للخروج، /model <id> للتبديل، /reset للمسح\n")
    chat_id = CLI_CHAT_ID_INTERACTIVE
    model = settings.default_model
    from mh3.agent import AgentCore
    from mh3.backend import ConnectionPool, StreamEvent
    from mh3.store import Store
    from mh3.tools import build_registry
    store = Store(settings.db_path)
    await store.init()
    registry = build_registry(settings)
    pool = ConnectionPool(settings)
    agent = AgentCore(settings, store, registry, pool, bot_name=BOT_NAME)

    async def on_event(ev: StreamEvent) -> None:
        if ev.kind == "text":
            sys.stdout.write(ev.text)
            sys.stdout.flush()
        else:
            _print_event(ev.kind, ev.text, ev.data)
    try:
        while True:
            try:
                line = input(f"\033[1;38;5;173mأنت ❯\033[0m ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                continue
            if line in ("/exit", "/quit", "exit"):
                break
            if line.startswith("/model"):
                model = line.split(maxsplit=1)[1].strip() if len(line.split()) > 1 else settings.default_model
                settings.default_model = model
                await pool.close(chat_id)
                sess = await store.load_session(chat_id)
                sess.model = model
                await store.save_session(sess)
                print(f"\033[2m→ النموذج: {model}\033[0m")
                continue
            if line == "/reset":
                sess = await store.load_session(chat_id)
                sess.messages, sess.summary = [], ""
                await store.save_session(sess)
                print("\033[2m→ مُسح السجل\033[0m")
                continue
            print(f"\033[1;38;5;108mالوكيل ❯\033[0m ", end="", flush=True)
            result = await agent.run(
                chat_id=chat_id, user_id=CLI_USER_ID, username="cli", user_name="CLI",
                is_admin=True, chat_type="private", text=line, on_event=on_event)
            print()
            if result.error:
                print(f"\033[31mخطأ: {result.error}\033[0m")
            print(f"\033[2m{result.stats_line()}\033[0m")
    finally:
        await pool.close_all()
        await store.close()


async def _check(settings: Settings) -> int:
    from mh3.backend import probe_model
    from mh3.tools import build_registry
    print(BANNER)
    problems: List[str] = []
    print("▸ فحص الإعدادات…")
    if not settings.bot_token or settings.bot_token == "0:cli-mode":
        problems.append("BOT_TOKEN غير مضبوط")
    else:
        print(f"  ✅ BOT_TOKEN مضبوط ({settings.bot_token.split(':')[0]}…)")
    if not settings.admin_ids and settings.access_mode == "admins":
        problems.append("ADMIN_IDS فارغ — لن يتمكن أحد من استخدام البوت")
    else:
        print(f"  ✅ المشرفون: {settings.admin_ids}")
    print(f"  ✅ قاعدة البيانات: {settings.db_path}")
    print(f"  ✅ مجلد العمل: {settings.workspace_dir}")
    registry = build_registry(settings)
    enabled = registry.enabled(admin=True)
    print(f"\n▸ الأدوات: {len(enabled)}/{len(registry.all)} مفعّلة")
    for spec in sorted(enabled, key=lambda s: (s.category, s.name)):
        flags = []
        if spec.admin_only:
            flags.append("مشرف")
        if spec.dangerous:
            flags.append("حساس")
        suffix = f" [{', '.join(flags)}]" if flags else ""
        print(f"  • {spec.name:<16} {spec.category:<8}{suffix}")
    print(f"\n▸ اختبار الاتصال بالنموذج {settings.default_model} …")
    ok, message, elapsed = await probe_model(settings, settings.default_model, timeout=PROBE_TIMEOUT)
    if ok:
        print(f"  ✅ الرد: {message!r} ({elapsed:.1f} ثانية)")
    else:
        problems.append(f"فشل اختبار النموذج: {message}")
        print(f"  ❌ {message}")
    print("\n" + ("⚠️  توجد مشاكل:\n  - " + "\n  - ".join(problems) if problems
                  else "✅ كل الفحوصات ناجحة — شغّل: python run.py"))
    return 1 if problems else 0


async def _probe(settings: Settings, model: str) -> int:
    from mh3.backend import probe_model
    print(f"▸ فحص {model} …")
    ok, message, elapsed = await probe_model(settings, model, timeout=40)
    print(("✅ " if ok else "❌ ") + f"{message} ({elapsed:.1f} ثانية)")
    return 0 if ok else 1


def _selftest() -> int:
    print(BANNER)
    failures: List[str] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        print(f"  {'✅' if condition else '❌'} {name}" + (f" — {detail}" if detail else ""))
        if not condition:
            failures.append(name)
    print("▸ الاستيراد")
    try:
        from mh3 import agent, backend, memory, models, protocol, store
        from mh3.tools import build_registry
        from mh3.tg import app, handlers, keyboards, render, stream, ui
        check("كل الوحدات", True)
    except Exception as exc:
        check("كل الوحدات", False, f"{type(exc).__name__}: {exc}")
        return 1
    print("▸ سجل الأدوات")
    from mh3.config import Settings
    settings = Settings(bot_token="0:test", admin_ids=[CLI_USER_ID])
    registry = build_registry(settings)
    check(f"عدد الأدوات >= {SELFTEST_MIN_TOOLS}", len(registry.all) >= SELFTEST_MIN_TOOLS,
          f"{len(registry.all)} أداة")
    check("مخططات JSON صالحة", all(
        isinstance(s.schema()["parameters"], dict) for s in registry.all))
    check("أسماء فريدة", len({s.name for s in registry.all}) == len(registry.all))
    print("▸ تحويل ماركداون → HTML")
    from mh3.tg import render
    html = render.md_to_html("**عريض** و`كود` و[رابط](https://x.com)\n```python\nprint(1)\n```")
    check("Bold", "<b>عريض</b>" in html, html[:80])
    check("Inline code", "<code>كود</code>" in html)
    check("Link", '<a href="https://x.com">رابط</a>' in html)
    check("Code block", '<pre><code class="language-python">print(1)</code></pre>' in html)
    check("تهريب HTML", "&lt;script&gt;" in render.md_to_html("<script>alert(1)</script>"))
    check("إغلاق كتلة مفتوحة", render.md_to_html("```py\nx=1").count("<pre>") == 1)
    print("▸ تقطيع الرسائل")
    long_text = "\n\n".join(f"فقرة رقم {i} " + "كلام " * 60 for i in range(60))
    chunks = render.split_markdown(long_text, render.MD_LIMIT)
    check("التقطيع يحفظ المحتوى", "".join(chunks).replace("\n", "") .replace(" ", "") ==
          long_text.replace("\n", "").replace(" ", ""))
    check("لا قطعة تتجاوز الحد", all(len(c) <= render.MD_LIMIT + 8 for c in chunks),
          f"{max(len(c) for c in chunks)} حرف")
    fence = "بداية\n```python\n" + "x = 1\n" * 900 + "```\nنهاية"
    chunks2 = render.split_markdown(fence, render.MD_LIMIT)
    check("كتل الكود تُغلق عند التقطيع",
          all(c.count("```") % 2 == 0 for c in chunks2))
    print("▸ الحاسبة الآمنة")
    from mh3.tools.core import safe_eval
    check("عمليات", safe_eval("(12+30)*2") == 84)
    check("دوال", abs(safe_eval("sqrt(2)") - 1.41421356) < 1e-6)
    check("نسبة مئوية", abs(safe_eval("50% * 200") - 100) < 1e-9)
    blocked = False
    try:
        safe_eval("__import__('os').system('id')")
    except Exception:
        blocked = True
    check("منع الاستيراد", blocked)
    print("▸ النماذج")
    from mh3 import models as MODELS
    check("حلّ الاختصار", MODELS.resolve_model("glm5").id == "@cf/zai-org/glm-5.2")
    check("حلّ الاسم", MODELS.resolve_model("gpt-oss-120b") is not None)
    check("حلّ المعرّف الكامل", MODELS.resolve_model("@cf/qwen/qwen3-30b-a3b-fp8") is not None)
    check("نماذج الرؤية", len(MODELS.vision_models()) > 0)
    print("▸ البروتوكول")
    from mh3 import protocol as P
    frame = P.chat_request_frame("abc123", [P.user_message("hi")],
                                 client_tools=[P.client_tool_schema("t", "d", {"type": "object"})])
    body = json.loads(frame["init"]["body"])
    check("بنية الطلب", frame["type"] == P.Frame.USE_CHAT_REQUEST and body["trigger"] == "submit-message")
    check("clientTools", body["clientTools"][0]["name"] == "t")
    part = P.tool_part("calc", "id1", {"x": 1}, {"y": 2})
    check("جزء أداة", part["type"] == "tool-calc" and part["state"] == "output-available")
    check("nanoid", len(P.nanoid(8)) == 8)
    print("▸ تقدير التوكنز والقصّ")
    from mh3 import memory as M
    msgs = [P.user_message("مرحباً " * 100), P.assistant_message([P.text_part("أهلاً " * 100)])] * 12
    trimmed = M.trim_messages(msgs, 500)
    check("القصّ يقلّل الحجم", M.estimate_messages(trimmed) < M.estimate_messages(msgs),
          f"{M.estimate_messages(msgs)} → {M.estimate_messages(trimmed)}")
    small = [P.user_message("مرحباً") for _ in range(80)]
    trimmed_small = M.trim_messages(small, 60)
    check("القصّ يحترم الميزانية للرسائل الصغيرة", M.estimate_messages(trimmed_small) <= 90,
          f"{M.estimate_messages(trimmed_small)} توكن")
    check("القصّ يحفظ آخر 6 رسائل على الأقل", len(trimmed) >= 6, f"{len(trimmed)} رسالة")
    check("drop_orphan", isinstance(M.drop_orphan_tool_results(
        [{"role": "assistant", "parts": [P.tool_part("x", "1", {}, None, state="input-available")]}]), list))
    check("أجزاء الأدوات اليتيمة تُحذف", not any(
        str(p.get("type", "")).startswith("tool-")
        for p in M.drop_orphan_tool_results(
            [{"role": "assistant", "parts": [
                P.tool_part("x", "1", {}, None, state="input-available")]}])[0]["parts"]))
    print("\n" + (f"❌ فشلت {len(failures)} فحوصات: {', '.join(failures)}"
                  if failures else "✅ كل الاختبارات الداخلية ناجحة"))
    return 1 if failures else 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=f"{BOT_NAME} — {COMPANY_NAME} | {SUPPORT_URL} | {COMPANY_SITE}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("--env", default=None, help="مسار ملف البيئة (افتراضي .env)")
    parser.add_argument("--bot-name", default=os.environ.get("BOT_NAME", BOT_NAME),
                        help="اسم الوكيل الظاهر في برومبت النظام")
    parser.add_argument("--check", action="store_true", help="فحص الإعدادات والاتصال ثم الخروج")
    parser.add_argument("--probe", metavar="MODEL", help="اختبار نموذج معين ثم الخروج")
    parser.add_argument("--ask", metavar="TEXT", help="جولة واحدة من الطرفية (تشخيص)")
    parser.add_argument("--chat", action="store_true", help="محادثة طرفية تفاعلية (تشخيص)")
    parser.add_argument("--selftest", action="store_true", help="اختبارات داخلية بلا شبكة")
    parser.add_argument("--version", action="store_true", help="عرض الإصدار")
    args = parser.parse_args(argv)
    if args.version:
        print(f"{BOT_NAME} {BOT_VERSION} — {COMPANY_NAME} — {COMPANY_SITE}")
        return 0
    if args.selftest:
        return _selftest()
    if args.env:
        os.environ["ENV_FILE"] = args.env
    if args.ask or args.chat or args.check or args.probe:
        settings = _load_settings(cli=True)
        if args.probe:
            return asyncio.run(_probe(settings, args.probe))
        if args.check:
            return asyncio.run(_check(settings))
        if args.chat:
            try:
                asyncio.run(_cli_chat(settings))
            except KeyboardInterrupt:
                print("\n👋")
            return 0
        try:
            asyncio.run(_cli_turn(settings, args.ask))
        except KeyboardInterrupt:
            print("\n👋")
        return 0
    from mh3.tg.app import run as run_bot
    settings = _load_settings(cli=False)
    print(BANNER)
    try:
        run_bot(settings, bot_name=args.bot_name)
    except KeyboardInterrupt:
        print("\n👋 أُلغي التشغيل")
    except SystemExit:
        raise
    except Exception as exc:
        print(f"\n❌ فشل التشغيل: {type(exc).__name__}: {exc}\n", file=sys.stderr)
        return 1
    return 0
if __name__ == "__main__":
    sys.exit(main())
