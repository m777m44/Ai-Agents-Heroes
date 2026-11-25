# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
import asyncio
import json
import os
import re
import shutil
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from . import ToolRegistry, truncate
_ENV_PASSTHROUGH = ("PATH", "LANG", "LC_ALL", "TZ", "TERM", "HOME", "PYTHONPATH", "TMPDIR")
_MAX_OUTPUT = 60_000


def _clean_env(ctx, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for key in _ENV_PASSTHROUGH:
        val = os.environ.get(key)
        if val:
            env[key] = val
    env.setdefault("PATH", "/usr/local/bin:/usr/bin:/bin")
    env.setdefault("LANG", "C.UTF-8")
    env["HOME"] = str(ctx.workspace)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    libs = ctx.workspace / "pylibs"
    if libs.is_dir():
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{libs}{os.pathsep}{existing}" if existing else str(libs)
    for secret in ("BOT_TOKEN", "TELEGRAM_TOKEN", "ADMIN_IDS", "WEBHOOK_SECRET", "PROXY_URL"):
        env.pop(secret, None)
    if extra:
        env.update({str(k): str(v) for k, v in extra.items()})
    return env


def _limits(memory_mb: int, cpu_seconds: int):

    def _apply() -> None:
        try:
            os.setsid()
        except OSError:
            pass
        try:
            import resource
            if memory_mb > 0:
                limit = memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
            if cpu_seconds > 0:
                resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 5))
            try:
                resource.setrlimit(resource.RLIMIT_NPROC, (256, 512))
            except (ValueError, OSError):
                pass
            try:
                resource.setrlimit(resource.RLIMIT_FSIZE, (256 * 1024 * 1024, 256 * 1024 * 1024))
            except (ValueError, OSError):
                pass
        except Exception:
            pass
    return _apply


async def _run_subprocess(
    argv: Sequence[str],
    *,
    cwd: Path,
    env: Dict[str, str],
    timeout: float,
    stdin_text: str = "",
    memory_mb: int = 1024,
    cpu_seconds: int = 0,
) -> Dict[str, Any]:
    cwd.mkdir(parents=True, exist_ok=True)
    preexec = _limits(memory_mb, cpu_seconds) if os.name == "posix" else None
    started = time.monotonic()
    try:
        proc = await asyncio.create_subprocess_exec(
            *argv,
            cwd=str(cwd),
            env=env,
            stdin=asyncio.subprocess.PIPE if stdin_text else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=preexec,
        )
    except FileNotFoundError as exc:
        return {"ok": False, "exit_code": 127, "stdout": "", "stderr": f"الأمر غير موجود: {exc}",
                "ms": 0, "timed_out": False}
    except Exception as exc:
        return {"ok": False, "exit_code": -1, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}",
                "ms": 0, "timed_out": False}
    timed_out = False
    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(stdin_text.encode() if stdin_text else None), timeout=timeout)
    except asyncio.TimeoutError:
        timed_out = True
        stdout_b, stderr_b = b"", b""
        await _kill_tree(proc)
        try:
            stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=5)
        except Exception:
            pass
    except asyncio.CancelledError:
        await _kill_tree(proc)
        raise
    ms = int((time.monotonic() - started) * 1000)
    stdout = _decode(stdout_b)
    stderr = _decode(stderr_b)
    return {
        "ok": proc.returncode == 0 and not timed_out,
        "exit_code": proc.returncode if proc.returncode is not None else -1,
        "stdout": truncate(stdout, _MAX_OUTPUT),
        "stderr": truncate(stderr, 20_000),
        "ms": ms,
        "timed_out": timed_out,
        "stdout_bytes": len(stdout_b or b""),
        "stderr_bytes": len(stderr_b or b""),
    }


def _decode(data: Optional[bytes]) -> str:
    if not data:
        return ""
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return repr(data[:2000])


async def _kill_tree(proc: asyncio.subprocess.Process) -> None:
    if proc.returncode is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(os.getpgid(proc.pid), 9)
        else:
            proc.kill()
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except Exception:
            pass


def _snapshot(directory: Path, limit: int = 300) -> Dict[str, int]:
    out: Dict[str, int] = {}
    if not directory.is_dir():
        return out
    for item in directory.rglob("*"):
        if len(out) >= limit:
            break
        try:
            if item.is_file():
                out[str(item.relative_to(directory))] = item.stat().st_size
        except OSError:
            continue
    return out


def register(reg: ToolRegistry) -> None:
    t = reg.tool

    @t(name="python_exec", category="code", needs_code=True, timeout=120, dangerous=True,
       description=(
           "Execute Python 3 code in a sandboxed subprocess and return stdout, stderr, exit code "
           "and any files created. The working directory is the chat's workspace. Available "
           "libraries: Python standard library (json, math, csv, sqlite3, datetime, re, statistics, "
           "urllib, itertools, collections, hashlib, base64, textwrap, decimal, fractions, zipfile, "
           "asyncio) plus anything listed by installed_packages. Use it for calculations, data "
           "processing, parsing, generating CSV/JSON/charts-data, or prototyping. Print the result "
           "to stdout to see it. Long-running or infinite loops are killed by the timeout."
       ),
       parameters={
           "type": "object",
           "properties": {
               "code": {"type": "string", "description": "Python source code to execute"},
               "stdin": {"type": "string", "description": "Optional text passed to stdin"},
               "timeout_seconds": {"type": "integer", "description": "Max runtime (default 60, hard max 110)"},
               "install_packages": {"type": "array", "items": {"type": "string"},
                                    "description": "pip packages to install into the sandbox first (admin only)"},
               "list_installed": {"type": "boolean",
                                  "description": "Just list importable third-party packages and exit"},
           },
           "required": [],
           "additionalProperties": False,
       })

    async def python_exec(args: Dict[str, Any], ctx) -> Any:
        code = str(args.get("code") or "")
        if args.get("list_installed"):
            return await _list_packages(ctx)
        if not code.strip():
            return {"error": "لا يوجد كود للتنفيذ"}
        if len(code) > 200_000:
            return {"error": "الكود كبير جداً (الحد 200KB)"}
        runs = ctx.workspace / "runs"
        run_id = uuid.uuid4().hex[:10]
        run_dir = runs / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        script = run_dir / "main.py"
        script.write_text(code, encoding="utf-8")
        installed: List[str] = []
        packages = args.get("install_packages") or []
        if packages and ctx.is_admin:
            installed = await _pip_install(ctx, packages)
        elif packages:
            return {"error": "تثبيت الحزم متاح للمشرفين فقط"}
        before = _snapshot(ctx.workspace)
        timeout = min(max(float(args.get("timeout_seconds") or 60), 3), 110)
        cpu = int(timeout) + 5
        result = await _run_subprocess(
            [sys.executable, "-I", "-B", str(script)],
            cwd=ctx.workspace,
            env=_clean_env(ctx),
            timeout=timeout,
            stdin_text=str(args.get("stdin") or ""),
            memory_mb=int(getattr(ctx.settings, "sandbox_memory_mb", 1024) or 1024),
            cpu_seconds=cpu,
        )
        after = _snapshot(ctx.workspace)
        created = sorted(set(after) - set(before))[:40]
        modified = sorted(k for k in set(after) & set(before) if after[k] != before[k])[:40]
        try:
            if not created and not modified:
                shutil.rmtree(run_dir, ignore_errors=True)
        except Exception:
            pass
        payload = {
            "ok": result["ok"],
            "exit_code": result["exit_code"],
            "timed_out": result["timed_out"],
            "ms": result["ms"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        }
        if created:
            payload["files_created"] = created
        if modified:
            payload["files_modified"] = modified
        if installed:
            payload["installed_packages"] = installed
        if result["timed_out"]:
            payload["hint"] = f"انتهت المهلة بعد {timeout:.0f} ثانية — قُلّل العمل أو زد timeout_seconds"
        return payload

    @t(name="shell_exec", category="code", needs_code=True, timeout=120,
       admin_only=True, dangerous=True,
       description=(
           "ADMIN ONLY. Run a shell command (bash -lc) inside the sandboxed workspace directory "
           "and return stdout/stderr/exit code. Useful for file operations, text processing "
           "(grep/awk/sed/sort), git, package inspection, ffmpeg/pandoc if installed. "
           "The process is killed on timeout; the environment contains no bot secrets."
       ),
       parameters={
           "type": "object",
           "properties": {
               "command": {"type": "string", "description": "Shell command line"},
               "cwd": {"type": "string", "description": "Subdirectory of the workspace (default: root)"},
               "timeout_seconds": {"type": "integer", "description": "Default 60, hard max 110"},
               "stdin": {"type": "string"},
           },
           "required": ["command"],
           "additionalProperties": False,
       })

    async def shell_exec(args: Dict[str, Any], ctx) -> Any:
        command = str(args.get("command") or "").strip()
        if not command:
            return {"error": "أمر فارغ"}
        if len(command) > 20_000:
            return {"error": "الأمر طويل جداً"}
        blocked = re.compile(
            r"(\.env|bot\.sqlite3|/proc/self/environ|MH3_|BOT_TOKEN|shutdown|reboot|mkfs|dd\s+if=)", re.I)
        if blocked.search(command):
            return {"error": "الأمر يحتوي نمطاً محظوراً لأسباب أمنية"}
        try:
            cwd = ctx.resolve_path(str(args.get("cwd") or "."))
        except PermissionError as exc:
            return {"error": str(exc)}
        cwd.mkdir(parents=True, exist_ok=True)
        shell = shutil.which("bash") or shutil.which("sh")
        if not shell:
            return {"error": "لا يوجد bash/sh في النظام"}
        timeout = min(max(float(args.get("timeout_seconds") or 60), 3), 110)
        result = await _run_subprocess(
            [shell, "-lc", command],
            cwd=cwd,
            env=_clean_env(ctx),
            timeout=timeout,
            stdin_text=str(args.get("stdin") or ""),
            memory_mb=int(getattr(ctx.settings, "sandbox_memory_mb", 1024) or 1024),
            cpu_seconds=int(timeout) + 5,
        )
        result["command"] = command[:500]
        result["cwd"] = str(cwd)
        return result

    @t(name="sandbox_info", category="code", needs_code=True, timeout=30,
       description=(
           "Report capabilities of the sandbox: python version, available third-party packages, "
           "common CLI tools (git, ffmpeg, pandoc, curl, sqlite3…), CPU/memory, workspace path "
           "and disk usage. Call this before writing code that depends on an external tool."
       ),
       parameters={"type": "object", "properties": {}, "required": [], "additionalProperties": False})

    async def sandbox_info(args: Dict[str, Any], ctx) -> Any:
        info = await _list_packages(ctx)
        tools: Dict[str, bool] = {}
        for name in ("git", "ffmpeg", "pandoc", "curl", "wget", "sqlite3", "convert",
                     "jq", "node", "pip", "tar", "zip", "unzip", "python3"):
            tools[name] = bool(shutil.which(name))
        try:
            usage = shutil.disk_usage(str(ctx.workspace))
            disk = {"total_gb": round(usage.total / 1e9, 2), "free_gb": round(usage.free / 1e9, 2)}
        except OSError:
            disk = {}
        size = sum(f.stat().st_size for f in ctx.workspace.rglob("*") if f.is_file())
        return {
            "python": sys.version.split()[0],
            "platform": sys.platform,
            "os": os.name,
            "workspace": str(ctx.workspace),
            "workspace_bytes": size,
            "disk": disk,
            "cli_tools": tools,
            "packages": info.get("packages", []),
            "cpu_count": os.cpu_count(),
            "memory_limit_mb": int(getattr(ctx.settings, "sandbox_memory_mb", 1024) or 0),
        }


async def _list_packages(ctx) -> Dict[str, Any]:
    code = (
        "import importlib.util, json, sys\n"
        "mods = ['numpy','pandas','matplotlib','requests','bs4','lxml','PIL','aiohttp','yaml',"
        "'scipy','openpyxl','regex','plotly','seaborn','sklearn','tabulate','feedparser']\n"
        "avail = [m for m in mods if importlib.util.find_spec(m)]\n"
        "print(json.dumps({'python': sys.version.split()[0], 'available': avail}))\n"
    )
    result = await _run_subprocess(
        [sys.executable, "-I", "-B", "-c", code],
        cwd=ctx.workspace, env=_clean_env(ctx), timeout=25,
        memory_mb=int(getattr(ctx.settings, "sandbox_memory_mb", 1024) or 1024),
    )
    packages: List[str] = []
    python_version = sys.version.split()[0]
    try:
        data = json.loads((result.get("stdout") or "").strip().splitlines()[-1])
        packages = data.get("available") or []
        python_version = data.get("python") or python_version
    except Exception:
        pass
    return {"python": python_version, "packages": packages, "stderr": result.get("stderr", "")[:400]}


async def _pip_install(ctx, packages: Sequence[str]) -> List[str]:
    names = [str(p).strip() for p in packages if str(p).strip()][:8]
    if not names:
        return []
    safe = [n for n in names if re.fullmatch(r"[A-Za-z0-9._\-\[\]]{1,60}", n)]
    if not safe:
        return []
    target = ctx.workspace / "pylibs"
    target.mkdir(parents=True, exist_ok=True)
    await ctx.notify(f"📦 تثبيت {len(safe)} حزمة في الصندوق المعزول…")
    await _run_subprocess(
        [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
         "--target", str(target), *safe],
        cwd=ctx.workspace, env=_clean_env(ctx), timeout=240, memory_mb=0,
    )
    return safe
