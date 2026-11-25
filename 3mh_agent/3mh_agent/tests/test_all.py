#!/usr/bin/env python3
# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import asyncio
import json
import os
import shutil
import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from mh3 import memory as MEM
from mh3 import models as MODELS
from mh3 import protocol as P
from mh3.agent import AgentCore
from mh3.backend import ConnectionPool, StreamEvent, Usage
from mh3.config import Settings
from mh3.errors import RateLimitedError
from mh3.store import Store
from mh3.tools import ToolContext, build_registry
from mh3.tg import render
from fake_playground import FakePlayground, FakeTurn


def make_settings(base_url: str = "", tmp: Optional[Path] = None) -> Settings:
    tmp = tmp or Path(tempfile.mkdtemp(prefix="3mh-test-"))
    settings = Settings(
        bot_token="123456:TEST",
        admin_ids=[111],
        access_mode="admins",
        default_model="@cf/test/model",
        fallback_models=[],
        utility_model="@cf/test/model",
        workspace_dir=tmp / "workspace",
        db_path=tmp / "bot.sqlite3",
        max_steps=5,
        step_timeout=25.0,
        tool_timeout=15.0,
        enable_python=True,
        enable_shell=True,
        rate_limit_per_min=1000,
        stream_edit_interval=0.05,
        log_file="",
    )
    if base_url:
        settings.cf_base_url = base_url
        settings.ws_heartbeat = 0.0
        settings.ws_handshake_drain = 0.25
    settings.validate()
    return settings


class EventCollector:

    def __init__(self) -> None:
        self.events: List[StreamEvent] = []

    async def __call__(self, ev: StreamEvent) -> None:
        self.events.append(ev)

    def __iter__(self):
        return iter(self.events)

    def kinds(self) -> List[str]:
        return [e.kind for e in self.events]

    def text(self) -> str:
        return "".join(e.text for e in self.events if e.kind == "text")


class NoSleep:

    def __enter__(self) -> "NoSleep":
        import mh3.agent as agent_mod
        self._module = agent_mod
        self._orig = asyncio.sleep

        async def _instant(_seconds: float, *args: Any, **kwargs: Any) -> None:
            await self._orig(0)
        agent_mod.asyncio.sleep = _instant
        return self

    def __exit__(self, *exc: Any) -> None:
        self._module.asyncio.sleep = self._orig


def test_protocol_builders() -> None:
    url = P.build_ws_url("wss://x.example", "playground-abc", "pk-1", "@cf/a/b")
    assert url == "wss://x.example/agents/playground/playground-abc?_pk=pk-1&model=%40cf%2Fa%2Fb"
    frame = P.chat_request_frame("r1", [P.user_message("hi")],
                                 client_tools=[P.client_tool_schema("t", "d", {"type": "object"})])
    assert frame["type"] == P.Frame.USE_CHAT_REQUEST
    body = json.loads(frame["init"]["body"])
    assert body["trigger"] == "submit-message"
    assert body["messages"][0]["parts"][0]["text"] == "hi"
    assert body["clientTools"][0] == {"name": "t", "description": "d", "parameters": {"type": "object"}}
    part = P.tool_part("calc", "id1", {"x": 1}, {"y": 2})
    assert part["type"] == "tool-calc" and part["state"] == "output-available"
    err_part = P.tool_part("calc", "id2", {}, None, state="output-error", error_text="boom")
    assert err_part["errorText"] == "boom" and "output" not in err_part
    state = P.state_frame("@cf/a/b", system="S", temperature=0.5)
    assert state["state"]["model"] == "@cf/a/b" and state["state"]["temperature"] == 0.5
    result = P.tool_result_frame("c1", "calc", {"v": 1}, state="output-error", error_text="bad")
    assert result["state"] == "output-error" and result["errorText"] == "bad"
    ok_result = P.tool_result_frame("c2", "calc", {"v": 2}, client_tools=[{"name": "calc"}])
    assert ok_result["autoContinue"] is False and ok_result["clientTools"][0]["name"] == "calc"
    assert len(P.nanoid(8)) == 8 and len({P.nanoid(8) for _ in range(50)}) == 50
    assert P.flatten_text({"content": [{"type": "text", "text": "a"}, {"type": "text", "text": "b"}]}) == "ab"
    assert P.tool_name_of({"type": "tool-web_search"}) == "web_search"


def test_error_classification() -> None:
    from mh3.backend import classify_error
    from mh3.errors import BackendError, ContextOverflow, ModelGatedError
    err = classify_error(json.dumps({
        "message": "The model is currently rate limited.",
        "details": "3021: rate limiting: inference request per min rate reached"}))
    assert isinstance(err, RateLimitedError) and err.retryable and err.try_fallback
    gated = classify_error(json.dumps({
        "message": "The model failed to generate a response.",
        "details": "5016: Prior to using this model, you must submit the prompt 'agree'."}))
    assert isinstance(gated, ModelGatedError)
    overflow = classify_error(json.dumps({"message": "Prompt exceeds maximum context length"}))
    assert isinstance(overflow, ContextOverflow)
    generic = classify_error("something odd happened")
    assert isinstance(generic, BackendError)


def test_models_catalog() -> None:
    assert MODELS.resolve_model("glm5").id == "@cf/zai-org/glm-5.2"
    assert MODELS.resolve_model("gpt-oss-120b").id == "@cf/openai/gpt-oss-120b"
    assert MODELS.resolve_model("@cf/qwen/qwen3-30b-a3b-fp8") is not None
    assert MODELS.resolve_model("Gemma 4 26B") is not None
    assert MODELS.resolve_model("لا يوجد نموذج بهذا الاسم إطلاقاً") is None
    assert MODELS.is_vision("@cf/google/gemma-4-26b-a4b-it")
    assert not MODELS.is_vision("@cf/zai-org/glm-4.7-flash")
    assert len(MODELS.suggest_models("glm")) >= 3
    assert len({m.id for m in MODELS.CATALOG}) == len(MODELS.CATALOG)


def test_render_markdown() -> None:
    html = render.md_to_html("**bold** *it* `code` ~~x~~ [link](https://a.b)")
    assert "<b>bold</b>" in html and "<i>it</i>" in html
    assert "<code>code</code>" in html and "<s>x</s>" in html
    assert '<a href="https://a.b">link</a>' in html
    assert "<script>" not in render.md_to_html("<script>alert(1)</script>")
    assert "&lt;script&gt;" in render.md_to_html("<script>alert(1)</script>")
    partial = render.md_to_html("```python\nprint(1)")
    assert partial.count("<pre>") == 1 and "</pre>" in partial
    assert "<b>عنوان</b>" in render.md_to_html("## عنوان")
    assert "<blockquote>" in render.md_to_html("> اقتباس")
    assert "some_var_name" in render.md_to_html("some_var_name")


def test_render_splitting() -> None:
    long_text = "\n\n".join(f"فقرة {i} " + "نص " * 80 for i in range(80))
    chunks = render.split_markdown(long_text, render.MD_LIMIT)
    assert len(chunks) > 1
    assert all(len(c) <= render.MD_LIMIT + 8 for c in chunks)
    assert "".join(chunks).replace("\n", "").replace(" ", "") == \
        long_text.replace("\n", "").replace(" ", "")
    fenced = "بداية\n```python\n" + "x = 1\n" * 1200 + "```\nنهاية"
    chunks = render.split_markdown(fenced, render.MD_LIMIT)
    assert all(c.count("```") % 2 == 0 for c in chunks), "كتل الكود يجب أن تبقى مغلقة"
    assert render.split_markdown("قصير") == ["قصير"]
    assert render.tail_text("abcdefghij", 4).endswith("ghij")


def test_calculator_safety() -> None:
    from mh3.tools.core import safe_eval
    assert safe_eval("(12+30)*2") == 84
    assert abs(safe_eval("sqrt(2)") - 1.4142135623) < 1e-6
    assert abs(safe_eval("50% * 200") - 100) < 1e-9
    assert safe_eval("2**10") == 1024
    assert safe_eval("max(1,2,3)") == 3
    assert safe_eval("3 > 2") is True
    for bad in ("__import__('os').system('id')", "open('/etc/passwd').read()",
                "().__class__", "lambda: 1"):
        try:
            safe_eval(bad)
            raise AssertionError(f"لم يُمنع: {bad}")
        except Exception as exc:
            assert not isinstance(exc, AssertionError), str(exc)


async def test_tools_core(tmp_path: Path) -> None:
    settings = make_settings(tmp=tmp_path)
    registry = build_registry(settings)
    ctx = ToolContext(chat_id=1, is_admin=True, settings=settings, store=None,
                      workspace=settings.workspace_dir / "1")
    ctx.workspace.mkdir(parents=True, exist_ok=True)
    ctx.extra["registry"] = registry
    res = await registry.execute("current_time", {"timezone": "Asia/Riyadh"}, ctx)
    assert res.ok and res.output["timezone"] == "Asia/Riyadh" and res.output["date"]
    res = await registry.execute("current_time", {"timezone": "Mars/Olympus"}, ctx)
    assert not res.ok or "error" in res.output
    res = await registry.execute("calculator", {"expression": "15% of 2480".replace(" of ", "*")}, ctx)
    assert res.ok and res.output["result"] == 372
    res = await registry.execute("text_tool", {"operation": "count", "text": "hello world"}, ctx)
    assert res.ok and res.output["words"] == 2
    res = await registry.execute("text_tool", {"operation": "hash", "text": "abc", "algorithm": "sha256"}, ctx)
    assert res.ok and res.output["hash"].startswith("ba7816bf")
    res = await registry.execute("json_tool", {
        "operation": "query", "json_text": '{"a":{"b":[10,20]}}', "path": "a.b[1]"}, ctx)
    assert res.ok and res.output["value"] == 20
    res = await registry.execute("random_tool", {"operation": "dice", "dice": "2d6"}, ctx)
    assert res.ok and 2 <= res.output["total"] <= 12
    res = await registry.execute("self_info", {"section": "tools"}, ctx)
    assert res.ok and res.output["tools_enabled"] > 10


async def test_tools_files(tmp_path: Path) -> None:
    settings = make_settings(tmp=tmp_path)
    registry = build_registry(settings)
    ws = settings.workspace_dir / "7"
    ws.mkdir(parents=True, exist_ok=True)
    ctx = ToolContext(chat_id=7, is_admin=True, settings=settings, store=None, workspace=ws)
    res = await registry.execute("file_write", {"path": "notes/a.txt", "content": "سطر أول\nسطر ثاني"}, ctx)
    assert res.ok and (ws / "notes" / "a.txt").exists()
    res = await registry.execute("file_read", {"path": "notes/a.txt"}, ctx)
    assert res.ok and "سطر أول" in res.output["content"]
    res = await registry.execute("file_write", {"path": "notes/b.md", "content": "# عنوان\nكلمة سرية"}, ctx)
    assert res.ok
    res = await registry.execute("file_search", {"query": "سرية"}, ctx)
    assert res.ok and res.output["matches"] >= 1
    res = await registry.execute("file_list", {"recursive": True}, ctx)
    assert res.ok and res.output["count"] >= 2
    res = await registry.execute("file_read", {"path": "../../etc/passwd"}, ctx)
    assert not res.ok or "error" in res.output
    res = await registry.execute("file_read", {"path": "/etc/passwd"}, ctx)
    assert "error" in (res.output or {})
    ctx_user = ToolContext(chat_id=7, is_admin=False, settings=settings, store=None, workspace=ws)
    res = await registry.execute("file_delete", {"path": "notes/a.txt"}, ctx_user)
    assert not res.ok
    res = await registry.execute("file_delete", {"path": "notes/a.txt"}, ctx)
    assert res.ok


async def test_tools_code(tmp_path: Path) -> None:
    settings = make_settings(tmp=tmp_path)
    registry = build_registry(settings)
    ws = settings.workspace_dir / "9"
    ws.mkdir(parents=True, exist_ok=True)
    ctx = ToolContext(chat_id=9, is_admin=True, settings=settings, store=None, workspace=ws)
    res = await registry.execute("python_exec", {
        "code": "import json, math\nprint(json.dumps({'pi': round(math.pi, 3)}))"}, ctx)
    assert res.ok, res.output
    assert '"pi": 3.142' in res.output["stdout"]
    res = await registry.execute("python_exec", {
        "code": "open('out/data.csv','w').write('a,b\\n1,2\\n')\nimport os\nos.makedirs('out',exist_ok=True)"}, ctx)
    res = await registry.execute("python_exec", {
        "code": "import os\nos.makedirs('out', exist_ok=True)\nopen('out/data.csv','w').write('a,b\\n1,2\\n')\nprint('done')"}, ctx)
    assert res.ok and res.output.get("files_created"), res.output
    assert (ws / "out" / "data.csv").exists()
    res = await registry.execute("python_exec", {"code": "import time\nwhile True: time.sleep(0.1)",
                                                 "timeout_seconds": 3}, ctx)
    assert res.output.get("timed_out") is True
    os.environ["BOT_TOKEN"] = "SECRET-SHOULD-NOT-LEAK"
    res = await registry.execute("python_exec", {"code": "import os;print(os.environ.get('BOT_TOKEN'))"}, ctx)
    assert "SECRET-SHOULD-NOT-LEAK" not in res.output["stdout"]
    del os.environ["BOT_TOKEN"]
    res = await registry.execute("shell_exec", {"command": "echo hello && pwd"}, ctx)
    assert res.ok and "hello" in res.output["stdout"]
    ctx_user = ToolContext(chat_id=9, is_admin=False, settings=settings, store=None, workspace=ws)
    res = await registry.execute("shell_exec", {"command": "echo hi"}, ctx_user)
    assert not res.ok
    res = await registry.execute("sandbox_info", {}, ctx)
    assert res.ok and res.output["python"]


async def test_registry_permissions(tmp_path: Path) -> None:
    settings = make_settings(tmp=tmp_path)
    registry = build_registry(settings)
    admin_tools = {s.name for s in registry.enabled(admin=True)}
    user_tools = {s.name for s in registry.enabled(admin=False)}
    assert "shell_exec" in admin_tools and "shell_exec" not in user_tools
    registry.set_runtime_enabled("web_search", False)
    assert not registry.is_enabled("web_search")
    registry.set_runtime_enabled("web_search", True)
    assert registry.is_enabled("web_search")
    settings.disabled_tools = {"calculator"}
    assert not registry.is_enabled("calculator")
    settings.disabled_tools = set()
    settings.enable_web_tools = False
    assert not registry.is_enabled("web_fetch")
    settings.enable_web_tools = True
    settings.enable_shell = False
    assert not registry.is_enabled("shell_exec")
    schemas = registry.client_tools(admin=True)
    assert all(set(s) == {"name", "description", "parameters"} for s in schemas)
    assert all(s["parameters"]["type"] == "object" for s in schemas)


async def test_store(tmp_path: Path) -> None:
    settings = make_settings(tmp=tmp_path)
    store = Store(settings.db_path)
    await store.init()
    sess = await store.load_session(5, defaults={"model": "@cf/x/y"})
    assert sess.model == "@cf/x/y" and sess.messages == []
    sess.messages = [P.user_message("مرحبا")]
    sess.summary = "ملخص"
    await store.save_session(sess)
    loaded = await store.load_session(5)
    assert loaded.summary == "ملخص" and len(loaded.messages) == 1
    assert loaded.turn_count == 1
    note_id = await store.add_note(5, "عنوان", "محتوى الملاحظة", "وسم")
    assert note_id > 0
    found = await store.search_notes(5, "محتوى")
    assert found and found[0]["id"] == note_id
    assert await store.count_notes(5) == 1
    assert await store.delete_note(5, note_id) is True
    assert await store.count_notes(5) == 0
    await store.log_usage(5, "@cf/x/y", {"input_tokens": 10, "output_tokens": 5,
                                         "total_tokens": 15, "cost_usd": 0.001,
                                         "generation_ms": 500}, steps=2, tool_calls=1)
    summary = await store.usage_summary(5, days=1)
    assert summary["requests"] == 1 and summary["total_tokens"] == 15
    await store.log_tool(5, "calculator", {"expression": "1+1"}, True, 3.2, '{"result":2}')
    stats = await store.tool_stats(5)
    assert stats and stats[0]["tool"] == "calculator"
    rid = await store.add_reminder(5, "تذكير", time.time() + 60)
    pending = await store.pending_reminders()
    assert any(r["id"] == rid for r in pending)
    await store.complete_reminder(rid)
    assert not any(r["id"] == rid for r in await store.pending_reminders())
    await store.kv_set("k", {"a": 1})
    assert (await store.kv_get("k"))["a"] == 1
    await store.close()


async def test_memory_compaction(tmp_path: Path) -> None:
    msgs: List[Dict[str, Any]] = []
    for i in range(30):
        msgs.append(P.user_message(f"سؤال رقم {i} " + "تفاصيل " * 40))
        msgs.append(P.assistant_message([P.text_part(f"جواب {i} " + "شرح " * 40)]))
    before = MEM.estimate_messages(msgs)
    trimmed = MEM.trim_messages(msgs, 800)
    assert MEM.estimate_messages(trimmed) < before
    assert len(trimmed) >= 6

    async def fake_summarize(prompt: str, system: str) -> str:
        assert "سؤال رقم 0" in prompt
        return "- الأهداف: اختبار\n- الملفات: لا شيء"
    summary = await MEM.compact_history(msgs[:20], summarize=fake_summarize, max_words=100)
    assert "الأهداف" in summary

    async def failing(prompt: str, system: str) -> str:
        raise RuntimeError("boom")
    assert await MEM.compact_history(msgs[:4], summarize=failing, previous_summary="قديم") == "قديم"
    orphan = [{"role": "assistant", "parts": [
        P.text_part("سأنفّذ"), P.tool_part("calculator", "c1", {"expression": "1+1"}, None,
                                           state="input-available")]}]
    cleaned = MEM.drop_orphan_tool_results(orphan)
    assert len(cleaned[0]["parts"]) == 1
    system = MEM.build_system_prompt(MEM.PromptContext(
        user_name="علي", chat_id=1, model="@cf/x/y",
        tools_summary=MEM.tools_summary_lines([]), summary="ملخص قديم",
        pinned_notes="- ملاحظة"))
    assert "علي" in system and "@cf/x/y" in system and "ملخص قديم" in system and "ملاحظة" in system


async def test_backend_stream() -> None:
    fake = FakePlayground([FakeTurn(text="مرحباً من الخادم الوهمي", reasoning="تفكير داخلي",
                                    usage={"inputTokens": 11, "outputTokens": 7,
                                           "totalTokens": 18, "costUsd": 0.0001,
                                           "generationMs": 300, "responseCount": 1})])
    base = await fake.start()
    try:
        settings = make_settings(base_url=base)
        pool = ConnectionPool(settings)
        events = EventCollector()
        conn = await pool.get(1, model="@cf/test/model", system="أنت مساعد", temperature=1.0)
        assert conn.connected
        turn = await conn.stream_turn([P.user_message("اختبر")], None, on_event=events)
        assert turn.text == "مرحباً من الخادم الوهمي"
        assert turn.reasoning == "تفكير داخلي"
        assert turn.finish_reason == "stop"
        assert turn.usage.input_tokens == 11 and turn.usage.total_tokens == 18
        assert "text" in events.kinds() and "finish" in events.kinds()
        assert fake.requests and fake.requests[0]["system"] == "أنت مساعد"
        await pool.close_all()
    finally:
        await fake.stop()


async def test_backend_usage_is_per_turn_not_cumulative() -> None:
    fake = FakePlayground([
        FakeTurn(text="أول", usage={"inputTokens": 100, "outputTokens": 10, "totalTokens": 110,
                                    "costUsd": 0.001, "generationMs": 100, "responseCount": 1}),
        FakeTurn(text="ثاني", usage={"inputTokens": 250, "outputTokens": 30, "totalTokens": 280,
                                     "costUsd": 0.003, "generationMs": 250, "responseCount": 2}),
    ])
    base = await fake.start()
    try:
        settings = make_settings(base_url=base)
        pool = ConnectionPool(settings)
        conn = await pool.get(2, model="@cf/test/model")
        first = await conn.stream_turn([P.user_message("١")], None)
        second = await conn.stream_turn([P.user_message("٢")], None)
        assert first.usage.total_tokens == 110, first.usage
        assert second.usage.total_tokens == 170, second.usage
        assert second.usage.input_tokens == 150
        await pool.close_all()
    finally:
        await fake.stop()


async def test_backend_rate_limit_error() -> None:
    fake = FakePlayground([FakeTurn(error={
        "message": "The model is currently rate limited. Please wait a moment and try again.",
        "details": "3021: rate limiting: inference request per min rate reached"})])
    base = await fake.start()
    try:
        settings = make_settings(base_url=base)
        pool = ConnectionPool(settings)
        conn = await pool.get(3, model="@cf/test/model")
        try:
            await conn.stream_turn([P.user_message("hi")], None)
            raise AssertionError("يجب أن يرفع RateLimitedError")
        except RateLimitedError as exc:
            assert "rate" in (exc.detail or "").lower() or "معدل" in exc.message
        await pool.close_all()
    finally:
        await fake.stop()


async def test_backend_model_switch_requires_new_connection() -> None:
    fake = FakePlayground([FakeTurn(text="ok")])
    base = await fake.start()
    try:
        settings = make_settings(base_url=base)
        pool = ConnectionPool(settings)
        conn1 = await pool.get(4, model="@cf/test/model-a")
        first_agent = conn1.agent_name
        await conn1.set_state(model="@cf/test/model-b")
        assert conn1.url_model == "@cf/test/model-a"
        conn2 = await pool.get(4, model="@cf/test/model-b")
        assert conn2.agent_name != first_agent
        assert conn2.url_model == "@cf/test/model-b"
        await pool.close_all()
    finally:
        await fake.stop()


async def test_backend_cancel() -> None:
    fake = FakePlayground([FakeTurn(text="نص طويل جداً " * 200, chunk_delay=0.01)])
    base = await fake.start()
    try:
        settings = make_settings(base_url=base)
        pool = ConnectionPool(settings)
        conn = await pool.get(6, model="@cf/test/model")
        cancel = asyncio.Event()

        async def stopper() -> None:
            await asyncio.sleep(0.25)
            cancel.set()
        task = asyncio.create_task(stopper())
        from mh3.errors import Cancelled
        try:
            await conn.stream_turn([P.user_message("hi")], None, cancel_event=cancel)
            raise AssertionError("يجب أن يرفع Cancelled")
        except Cancelled:
            pass
        await task
        await asyncio.sleep(0.05)
        assert fake.cancels, "يجب إرسال إطار إلغاء للخادم"
        await pool.close_all()
    finally:
        await fake.stop()


async def test_agent_tool_loop() -> None:
    fake = FakePlayground([
        FakeTurn(text="سأحسب ذلك.", tool_calls=[
            {"name": "calculator", "input": {"expression": "6*7"}},
            {"name": "current_time", "input": {"timezone": "UTC"}},
        ]),
        FakeTurn(text="الناتج 42 والوقت متاح."),
    ])
    base = await fake.start()
    tmp_path = Path(tempfile.mkdtemp(prefix="3mh-agent-"))
    try:
        settings = make_settings(base_url=base, tmp=tmp_path)
        store = Store(settings.db_path)
        await store.init()
        registry = build_registry(settings)
        pool = ConnectionPool(settings)
        agent = AgentCore(settings, store, registry, pool)
        events = EventCollector()
        result = await agent.run(chat_id=11, user_id=111, username="tester",
                                 user_name="Tester", is_admin=True, text="احسب 6*7",
                                 on_event=events)
        assert result.ok, result.error
        assert result.text == "الناتج 42 والوقت متاح."
        assert result.steps == 2
        assert len(result.tools) == 2 and all(t.ok for t in result.tools)
        assert {t.name for t in result.tools} == {"calculator", "current_time"}
        assert len(fake.tool_results) == 2
        outputs = {r["toolName"]: r["output"] for r in fake.tool_results}
        assert outputs["calculator"]["result"] == 42
        assert all(r["autoContinue"] is False for r in fake.tool_results)
        second_body = fake.requests[1]["body"]
        assistant_msgs = [m for m in second_body["messages"] if m["role"] == "assistant"]
        tool_parts = [p for m in assistant_msgs for p in m["parts"]
                      if str(p.get("type", "")).startswith("tool-")]
        assert tool_parts and all(p["state"] == "output-available" for p in tool_parts)
        assert second_body["clientTools"] and any(
            t["name"] == "calculator" for t in second_body["clientTools"])
        sess = await store.load_session(11)
        assert sess.messages and sess.turn_count >= 1
        assert "turn" in events.kinds() and "tool_call" in events.kinds()
        await pool.close_all()
        await store.close()
    finally:
        await fake.stop()
        shutil.rmtree(tmp_path, ignore_errors=True)


async def test_agent_loop_protection() -> None:
    same = {"name": "calculator", "input": {"expression": "1+1"}}
    fake = FakePlayground([FakeTurn(tool_calls=[same])] * 8, repeat_last=True)
    base = await fake.start()
    tmp_path = Path(tempfile.mkdtemp(prefix="3mh-loop-"))
    try:
        settings = make_settings(base_url=base, tmp=tmp_path)
        settings.max_steps = 8
        store = Store(settings.db_path)
        await store.init()
        registry = build_registry(settings)
        pool = ConnectionPool(settings)
        agent = AgentCore(settings, store, registry, pool)
        result = await agent.run(chat_id=12, user_id=111, is_admin=True, text="كرر")
        assert result.steps <= 5, result.steps
        assert any("تكرار" in n for n in result.notes), result.notes
        await pool.close_all()
        await store.close()
    finally:
        await fake.stop()
        shutil.rmtree(tmp_path, ignore_errors=True)


async def test_agent_model_fallback() -> None:
    rate_limited = FakeTurn(error={
        "message": "The model is currently rate limited.",
        "details": "3021: rate limiting: inference request per min rate reached"})
    fake = FakePlayground([rate_limited, rate_limited, FakeTurn(text="جواب من البديل")])
    base = await fake.start()
    tmp_path = Path(tempfile.mkdtemp(prefix="3mh-fb-"))
    try:
        settings = make_settings(base_url=base, tmp=tmp_path)
        settings.fallback_models = ["@cf/backup/model"]
        store = Store(settings.db_path)
        await store.init()
        registry = build_registry(settings)
        pool = ConnectionPool(settings)
        agent = AgentCore(settings, store, registry, pool)
        events = EventCollector()
        with NoSleep():
            result = await agent.run(chat_id=13, user_id=111, is_admin=True,
                                     text="اختبر التبديل", on_event=events)
        assert result.ok, result.error
        assert result.text == "جواب من البديل"
        assert result.model == "@cf/backup/model"
        statuses = [e.data.get("status") for e in events if e.kind == "status"]
        assert "fallback" in statuses
        await pool.close_all()
        await store.close()
    finally:
        await fake.stop()
        shutil.rmtree(tmp_path, ignore_errors=True)


async def test_agent_cancellation() -> None:
    fake = FakePlayground([FakeTurn(text="كلام كثير " * 300, chunk_delay=0.01)])
    base = await fake.start()
    tmp_path = Path(tempfile.mkdtemp(prefix="3mh-cancel-"))
    try:
        settings = make_settings(base_url=base, tmp=tmp_path)
        store = Store(settings.db_path)
        await store.init()
        registry = build_registry(settings)
        pool = ConnectionPool(settings)
        agent = AgentCore(settings, store, registry, pool)

        async def cancel_soon() -> None:
            await asyncio.sleep(0.3)
            assert agent.request_cancel(14) is True
        task = asyncio.create_task(cancel_soon())
        result = await agent.run(chat_id=14, user_id=111, is_admin=True, text="ألغِ")
        await task
        assert result.cancelled is True
        assert agent.is_busy(14) is False
        await pool.close_all()
        await store.close()
    finally:
        await fake.stop()
        shutil.rmtree(tmp_path, ignore_errors=True)


async def test_agent_subagent_and_notes() -> None:
    fake = FakePlayground([
        FakeTurn(tool_calls=[{"name": "memory_save",
                              "input": {"title": "تفضيل", "body": "يحب التقارير المختصرة"}},
                             {"name": "ask_model",
                              "input": {"prompt": "لخّص: النص", "model": "@cf/sub/model"}}]),
        FakeTurn(text="ملخص فرعي من النموذج الآخر"),
        FakeTurn(text="تم الحفظ والتفويض."),
    ])
    base = await fake.start()
    tmp_path = Path(tempfile.mkdtemp(prefix="3mh-sub-"))
    store = None
    pool = None
    try:
        settings = make_settings(base_url=base, tmp=tmp_path)
        settings.utility_model = "@cf/sub/model"
        store = Store(settings.db_path)
        await store.init()
        registry = build_registry(settings)
        pool = ConnectionPool(settings)
        agent = AgentCore(settings, store, registry, pool)
        result = await agent.run(chat_id=15, user_id=111, is_admin=True, text="احفظ ولخّص")
        assert result.ok, result.error
        assert result.text == "تم الحفظ والتفويض.", result.text
        assert all(t.ok for t in result.tools), [(t.name, t.error) for t in result.tools]
        assert await store.count_notes(15) == 1, "يجب أن تُحفظ الملاحظة"
        sub_tools = [r for r in fake.tool_results if r["toolName"] == "ask_model"]
        assert sub_tools, "يجب إرسال نتيجة أداة ask_model"
        payload = json.dumps(sub_tools[0]["output"], ensure_ascii=False)
        assert "ملخص فرعي" in payload, payload
        assert sub_tools[0]["output"]["model"] == "@cf/sub/model"
        assert any("sub:" in str(k) for k in pool._conns.keys()), list(pool._conns)
        assert fake.connections >= 2, fake.connections
        await pool.close_all()
        await store.close()
    finally:
        if pool is not None:
            await pool.close_all()
        if store is not None:
            await store.close()
        await fake.stop()
        shutil.rmtree(tmp_path, ignore_errors=True)


class StubAgent:

    def __init__(self, text: str = "**تم** بنجاح", tools: Optional[List[str]] = None) -> None:
        self.text = text
        self.tool_names = tools or ["calculator"]
        self.calls: List[Dict[str, Any]] = []
        self._busy = False

    def is_busy(self, chat_id: int) -> bool:
        return self._busy

    def request_cancel(self, chat_id: int) -> bool:
        return False

    def lock_for(self, chat_id: int) -> asyncio.Lock:
        return asyncio.Lock()

    async def run(self, **kwargs: Any) -> Any:
        from mh3.agent import AgentResult, ToolTrace
        from mh3.backend import Usage
        self.calls.append(kwargs)
        on_event = kwargs.get("on_event")
        if on_event is not None:
            await on_event(StreamEvent(kind="turn", data={"step": 1, "max_steps": 5}))
            await on_event(StreamEvent(kind="tool_call", data={
                "tool_name": "calculator", "tool_call_id": "c1", "input": {"expression": "1+1"}}))
            await on_event(StreamEvent(kind="tool_result", data={
                "tool_name": "calculator", "ok": True, "ms": 12, "preview": '{"result": 2}'}))
            await on_event(StreamEvent(kind="text", text=self.text))
            await on_event(StreamEvent(kind="finish", data={"finish_reason": "stop"}))
        return AgentResult(
            text=self.text, model="@cf/test/model", steps=1,
            usage=Usage(10, 5, 15, 0.0001, 400, 1), elapsed=1.23,
            tools=[ToolTrace(name=n, args={}, ok=True, ms=12, output_preview="…")
                   for n in self.tool_names])

    def _make_summarizer(self, chat_id: int) -> Any:

        async def summarize(prompt: str, system: str) -> str:
            return "ملخص"
        return summarize


async def test_telegram_flow() -> None:
    from telegram.ext import ApplicationBuilder, ContextTypes
    from fake_telegram import FakeRequest, callback_update, make_bot, text_update
    from mh3.tg.handlers import BotHandlers
    from mh3.tg.stream import StreamRenderer
    tmp_path = Path(tempfile.mkdtemp(prefix="3mh-tg-"))
    try:
        settings = make_settings(tmp=tmp_path)
        settings.access_mode = "admins"
        settings.admin_ids = [111]
        store = Store(settings.db_path)
        await store.init()
        registry = build_registry(settings)
        pool = ConnectionPool(settings)
        stub = StubAgent()
        handlers = BotHandlers(settings, store, registry, pool, stub, bot_name="TestBot")
        bot, req = make_bot()
        app = ApplicationBuilder().bot(bot).build()
        app.bot_data.update({"settings": settings, "store": store, "registry": registry,
                             "pool": pool, "agent": stub, "handlers": handlers})
        req.calls.clear()
        update = text_update("مرحبا", user_id=999)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        await handlers.on_message(update, ctx)
        assert any("مقصور" in t or "restricted" in t.lower() for t in req.sent_texts()), req.sent_texts()
        req.calls.clear()
        update = text_update("احسب 1+1", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        await handlers.on_message(update, ctx)
        methods = req.methods()
        assert "sendMessage" in methods, methods
        assert "editMessageText" in methods, methods
        edits = req.edited_texts()
        assert any("<b>تم</b>" in e for e in edits), edits[-1:]
        assert any("calculator" in e for e in edits), "يجب أن يظهر سجل الأدوات"
        assert any("sendChatAction" == m for m in methods)
        assert stub.calls and stub.calls[0]["text"] == "احسب 1+1"
        assert stub.calls[0]["is_admin"] is True
        req.calls.clear()
        update = text_update("/id", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        ctx.args = []
        await handlers.cmd_id(update, ctx)
        assert any("111" in t for t in req.sent_texts())
        req.calls.clear()
        update = text_update("/model glm5", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        ctx.args = ["glm5"]
        await handlers.cmd_model(update, ctx)
        sess = await store.load_session(111 if False else 42)
        assert sess.model == "@cf/zai-org/glm-5.2"
        assert any("glm-5.2" in t for t in req.sent_texts())
        req.calls.clear()
        update = text_update("/tools", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        ctx.args = []
        await handlers.cmd_tools(update, ctx)
        assert any("calculator" in t for t in req.sent_texts())
        req.calls.clear()
        update = text_update("/status", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        ctx.args = []
        await handlers.cmd_status(update, ctx)
        assert any("الإصدار" in t for t in req.sent_texts())
        req.calls.clear()
        update = text_update("/note تفضيل مهم", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        ctx.args = ["تفضيل", "مهم"]
        await handlers.cmd_note(update, ctx)
        assert await store.count_notes(42) == 1
        req.calls.clear()
        update = callback_update("mset:@cf/openai/gpt-oss-120b", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        await handlers.on_callback(update, ctx)
        sess = await store.load_session(42)
        assert sess.model == "@cf/openai/gpt-oss-120b"
        req.calls.clear()
        update = callback_update("ttog:calculator", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        await handlers.on_callback(update, ctx)
        assert not registry.is_enabled("calculator")
        update = callback_update("ttog:calculator", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        await handlers.on_callback(update, ctx)
        assert registry.is_enabled("calculator")
        req.calls.clear()
        long_answer = "\n\n".join(f"## قسم {i}\n" + "نص طويل. " * 120 for i in range(8))
        update = text_update("اكتب تقريراً", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        renderer = StreamRenderer(update, ctx, settings, lang="ar", model="@cf/test/model",
                                  show_trace=False, show_usage=False)
        await renderer.start()
        await renderer.on_event(StreamEvent(kind="text", text=long_answer))
        await renderer.finish(text=long_answer, stats="إحصاءات")
        sent = req.sent_texts() + req.edited_texts()
        assert any(len(s) <= 4096 for s in sent)
        assert sum(1 for m in req.methods() if m == "sendMessage") >= 2
        await app.shutdown()
        await store.close()
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


async def test_telegram_attachments_and_group_gate() -> None:
    from telegram.ext import ApplicationBuilder, ContextTypes
    from fake_telegram import make_bot, text_update
    from mh3.tg.handlers import BotHandlers
    tmp_path = Path(tempfile.mkdtemp(prefix="3mh-tg2-"))
    try:
        settings = make_settings(tmp=tmp_path)
        settings.access_mode = "admins"
        settings.admin_ids = [111]
        settings.allow_groups = False
        store = Store(settings.db_path)
        await store.init()
        registry = build_registry(settings)
        pool = ConnectionPool(settings)
        stub = StubAgent(text="حسنًا")
        handlers = BotHandlers(settings, store, registry, pool, stub, bot_name="TestBot")
        bot, req = make_bot()
        app = ApplicationBuilder().bot(bot).build()
        app.bot_data.update({"settings": settings, "store": store, "registry": registry,
                             "pool": pool, "agent": stub, "handlers": handlers})
        req.calls.clear()
        update = text_update("مرحبا", user_id=999, chat_id=-100200, chat_type="supergroup")
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        await handlers.on_message(update, ctx)
        assert not req.sent_texts() or all("غير مصرّح" in t or "مقصور" in t for t in req.sent_texts())
        settings.rate_limit_per_min = 2
        req.calls.clear()
        for _ in range(3):
            update = text_update("رسالة", user_id=111)
            ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
            await handlers.on_message(update, ctx)
        assert any("تجاوزت حد الطلبات" in t for t in req.sent_texts()), req.sent_texts()
        settings.rate_limit_per_min = 1000
        req.calls.clear()
        stub.calls.clear()
        update = text_update("اشرح أكثر", user_id=111, reply_to_bot=True)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        await handlers.on_message(update, ctx)
        assert stub.calls and "اقتباس" in stub.calls[0]["text"]
        await app.shutdown()
        await store.close()
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
async def test_colored_buttons() -> None:
    from telegram.constants import KeyboardButtonStyle
    from telegram.ext import ApplicationBuilder, ContextTypes

    from fake_telegram import FakeRequest, callback_update, make_bot, text_update
    from mh3.tg import keyboards as KB
    from mh3.tg.handlers import BotHandlers

    brand = {"company": "3MH TECHNOLOGIES", "site": "http://3mh.pages.dev",
             "support": "t.me/j49_c", "channel": "t.me/bshshshkk"}
    styles = {KeyboardButtonStyle.PRIMARY.value, KeyboardButtonStyle.SUCCESS.value,
              KeyboardButtonStyle.DANGER.value}
    assert styles == {"primary", "success", "danger"}

    menu = KB.main_menu_keyboard(brand).to_dict()
    flat = [b for row in menu["inline_keyboard"] for b in row]
    assert any(b.get("style") == "success" for b in flat)
    assert any(b.get("style") == "danger" for b in flat)
    assert any(b.get("url") == "t.me/j49_c" for b in flat)
    assert any(b.get("url") == "t.me/bshshshkk" for b in flat)
    assert any(b.get("url") == "http://3mh.pages.dev" for b in flat)

    reply_kb = KB.main_reply_keyboard().to_dict()
    assert reply_kb["resize_keyboard"] is True and reply_kb["is_persistent"] is True
    labels = [b["text"] for row in reply_kb["keyboard"] for b in row]
    assert KB.MENU_LABELS["tools"] in labels and KB.MENU_LABELS["stop"] in labels
    assert any(b.get("style") == "danger" for row in reply_kb["keyboard"] for b in row)

    tmp_path = Path(tempfile.mkdtemp(prefix="3mh-btn-"))
    store = None
    pool = None
    try:
        settings = make_settings(tmp=tmp_path)
        store = Store(settings.db_path)
        await store.init()
        registry = build_registry(settings)
        pool = ConnectionPool(settings)
        stub = StubAgent(text="**جاهز**")
        handlers = BotHandlers(settings, store, registry, pool, stub, bot_name="3mh agent")
        bot, req = make_bot()
        app = ApplicationBuilder().bot(bot).build()
        app.bot_data.update({"settings": settings, "store": store, "registry": registry,
                             "pool": pool, "agent": stub, "handlers": handlers})

        req.calls.clear()
        update = text_update("/start", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        ctx.args = []
        await handlers.cmd_start(update, ctx)
        payload = json.dumps([prm for _, prm in req.calls], ensure_ascii=False)
        assert "3MH TECHNOLOGIES" in payload
        _3mh_marks = [json.loads(prm["reply_markup"]) for _, prm in req.calls
                      if "reply_markup" in prm]
        assert _3mh_marks, "يجب إرسال لوحة أزرار"
        _3mh_all = [b for kb in _3mh_marks for row in kb.get("inline_keyboard", kb.get("keyboard", []))
                    for b in row]
        _3mh_styles = {b.get("style") for b in _3mh_all}
        assert "success" in _3mh_styles and "danger" in _3mh_styles, _3mh_styles
        assert any(b.get("resize_keyboard") for b in []) or \
            any(kb.get("resize_keyboard") for kb in _3mh_marks), "لوحة مفاتيح دائمة"
        assert any(b.get("url") == "t.me/j49_c" for b in _3mh_all)

        req.calls.clear()
        stub.calls.clear()
        update = text_update(KB.MENU_LABELS["tools"], user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        await handlers.on_message(update, ctx)
        assert not stub.calls
        assert any("calculator" in t for t in req.sent_texts()), req.sent_texts()

        req.calls.clear()
        update = callback_update("menu:tools", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        await handlers.on_callback(update, ctx)
        assert any("calculator" in t for t in req.sent_texts())

        req.calls.clear()
        update = callback_update("menu:memory", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        await handlers.on_callback(update, ctx)
        body = json.dumps([prm for _, prm in req.calls], ensure_ascii=False)
        assert "mem:notes" in body and "mem:compact" in body

        req.calls.clear()
        update = text_update("قل شيئاً", user_id=111)
        ctx = ContextTypes.DEFAULT_TYPE.from_update(update, app)
        await handlers.on_message(update, ctx)
        body = json.dumps([prm for _, prm in req.calls], ensure_ascii=False)
        _3mh_kb = [json.loads(prm["reply_markup"]) for _, prm in req.calls if "reply_markup" in prm]
        _3mh_btns = [b for kb in _3mh_kb for row in kb["inline_keyboard"] for b in row]
        assert any(b.get("callback_data") == "act:regen" for b in _3mh_btns)
        assert any(b.get("style") for b in _3mh_btns), "أزرار الرد يجب أن تكون ملوّنة"

        await app.shutdown()
    finally:
        if pool is not None:
            await pool.close_all()
        if store is not None:
            await store.close()
        shutil.rmtree(tmp_path, ignore_errors=True)


TESTS = [
    test_protocol_builders,
    test_error_classification,
    test_models_catalog,
    test_render_markdown,
    test_render_splitting,
    test_calculator_safety,
    test_tools_core,
    test_tools_files,
    test_tools_code,
    test_registry_permissions,
    test_store,
    test_memory_compaction,
    test_backend_stream,
    test_backend_usage_is_per_turn_not_cumulative,
    test_backend_rate_limit_error,
    test_backend_model_switch_requires_new_connection,
    test_backend_cancel,
    test_agent_tool_loop,
    test_agent_loop_protection,
    test_agent_model_fallback,
    test_agent_cancellation,
    test_agent_subagent_and_notes,
    test_telegram_flow,
    test_telegram_attachments_and_group_gate,
    test_colored_buttons,
]


async def _run_one(fn, keyword: str = "") -> bool:
    name = fn.__name__
    if keyword and keyword.lower() not in name.lower():
        return True
    started = time.monotonic()
    tmp_path = Path(tempfile.mkdtemp(prefix="3mh-t-"))
    try:
        if asyncio.iscoroutinefunction(fn):
            params = fn.__code__.co_varnames[:fn.__code__.co_argcount]
            if "tmp_path" in params:
                await fn(tmp_path)
            else:
                await fn()
        else:
            params = fn.__code__.co_varnames[:fn.__code__.co_argcount]
            if "tmp_path" in params:
                fn(tmp_path)
            else:
                fn()
        elapsed = time.monotonic() - started
        print(f"  \033[32m✅ {name}\033[0m \033[2m({elapsed:.2f}s)\033[0m")
        return True
    except AssertionError as exc:
        print(f"  \033[31m❌ {name}\033[0m — AssertionError: {exc}")
        traceback.print_exc(limit=3)
        return False
    except Exception as exc:
        print(f"  \033[31m❌ {name}\033[0m — {type(exc).__name__}: {exc}")
        traceback.print_exc(limit=4)
        return False
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


async def main(keyword: str = "") -> int:
    print("\n🧪 اختبارات 3mh agent — 3MH TECHNOLOGIES (معزولة)\n")
    results: List[bool] = []
    for fn in TESTS:
        results.append(await _run_one(fn, keyword))
    total = len([r for r in results])
    failed = results.count(False)
    print(f"\n{'✅ كلها ناجحة' if not failed else f'❌ فشل {failed}'} — {total - failed}/{total} اختبار")
    return 1 if failed else 0
if __name__ == "__main__":
    keyword = ""
    if "-k" in sys.argv:
        keyword = sys.argv[sys.argv.index("-k") + 1]
    sys.exit(asyncio.run(main(keyword)))
