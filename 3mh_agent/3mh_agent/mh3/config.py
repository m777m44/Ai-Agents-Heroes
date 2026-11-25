# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
BOT_NAME = "3mh agent"
BOT_VERSION = "2.0.0"
COMPANY_NAME = "3MH TECHNOLOGIES"
COMPANY_SITE = "http://3mh.pages.dev"
SUPPORT_USERNAME = "j49_c"
CHANNEL_USERNAME = "bshshshkk"
SUPPORT_URL = "t.me/j49_c"
CHANNEL_URL = "t.me/bshshshkk"
ENV_FILE = ".env"
BOT_TOKEN = ""
ADMIN_IDS = ""
ACCESS_MODE = "admins"
ALLOWED_CHATS = ""
ALLOW_GROUPS = "false"
DEFAULT_MODEL = "@cf/zai-org/glm-4.7-flash"
FALLBACK_MODELS = "@cf/zai-org/glm-5.2,@cf/openai/gpt-oss-120b,@cf/google/gemma-4-26b-a4b-it"
UTILITY_MODEL = "@cf/zai-org/glm-4.7-flash"
SYSTEM_PROMPT = ""
MAX_STEPS = "10"
STEP_TIMEOUT = "180"
TOOL_TIMEOUT = "45"
MAX_TOOL_OUTPUT = "8000"
TEMPERATURE = "1"
ENABLE_PYTHON = "true"
ENABLE_SHELL = "true"
ENABLE_WEB_TOOLS = "true"
WORKSPACE_DIR = "./data/workspace"
DISABLED_TOOLS = ""
ENABLED_TOOLS_ONLY = ""
SANDBOX_MEMORY_MB = "1024"
MAX_CONTEXT_TOKENS = "24000"
COMPACT_RATIO = "0.85"
UI_LANGUAGE = "ar"
STREAM_EDITS = "true"
STREAM_EDIT_INTERVAL = "1.0"
SHOW_REASONING = "false"
SHOW_TOOL_TRACE = "true"
SHOW_USAGE = "true"
RATE_LIMIT_PER_MIN = "20"
DB_PATH = "./data/bot.sqlite3"
USAGE_RETENTION_DAYS = "60"
CF_BASE_URL = "wss://playground.ai.cloudflare.com"
CF_ORIGIN = "https://playground.ai.cloudflare.com"
WS_MAX_RETRIES = "4"
WS_HANDSHAKE_DRAIN = "1.2"
WS_IDLE_TIMEOUT = "120"
WS_HEARTBEAT = "25"
SEARCH_PROVIDER = "auto"
SEARCH_API_KEY = ""
SEARXNG_URL = ""
WIKI_USER_AGENT = "3mh-agent/2.0 (+http://3mh.pages.dev; contact: t.me/j49_c)"
WEBHOOK_URL = ""
WEBHOOK_SECRET = ""
WEBHOOK_PORT = "8443"
PROXY_URL = ""
LOG_LEVEL = "INFO"
LOG_FILE = "./data/bot.log"
MENU_BUTTONS = "true"
BUTTON_COLORS = "true"
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set
__all__ = ["Settings", "load_settings"]
_TRUE = {"1", "true", "yes", "y", "on", "نعم"}
_FALSE = {"0", "false", "no", "n", "off", "لا"}


def _env(key: str, default: str = "") -> str:
    val = os.environ.get(key)
    return default if val is None else val.strip()


def _bool(key: str, default: bool) -> bool:
    raw = _env(key).lower()
    if not raw:
        return default
    if raw in _TRUE:
        return True
    if raw in _FALSE:
        return False
    return default


def _int(key: str, default: int) -> int:
    try:
        return int(float(_env(key) or default))
    except (TypeError, ValueError):
        return default


def _float(key: str, default: float) -> float:
    try:
        return float(_env(key) or default)
    except (TypeError, ValueError):
        return default


def _list(key: str, default: Optional[List[str]] = None) -> List[str]:
    raw = _env(key) or ",".join(default or [])
    if not raw:
        return list(default or [])
    return [item.strip() for item in raw.replace(";", ",").split(",") if item.strip()]


def _int_list(key: str, fallback: str = "") -> List[int]:
    out: List[int] = []
    for item in _list(key, [i.strip() for i in fallback.split(",") if i.strip()]):
        try:
            out.append(int(item))
        except ValueError:
            continue
    return out


@dataclass
class Settings:
    bot_name: str = BOT_NAME
    bot_version: str = BOT_VERSION
    company_name: str = COMPANY_NAME
    company_site: str = COMPANY_SITE
    support_url: str = SUPPORT_URL
    channel_url: str = CHANNEL_URL
    menu_buttons: bool = MENU_BUTTONS == "true"
    button_colors: bool = BUTTON_COLORS == "true"
    bot_token: str = ""
    admin_ids: List[int] = field(default_factory=list)
    admin_usernames: Set[str] = field(default_factory=set)
    access_mode: str = "admins"
    allowed_chats: List[int] = field(default_factory=list)
    allow_groups: bool = False
    default_model: str = DEFAULT_MODEL
    fallback_models: List[str] = field(default_factory=list)
    utility_model: str = "@cf/zai-org/glm-4.7-flash"
    system_prompt: str = ""
    max_steps: int = 10
    step_timeout: float = 180.0
    tool_timeout: float = 45.0
    max_tool_output: int = 8000
    temperature: float = 1.0
    enable_python: bool = True
    enable_shell: bool = True
    enable_web_tools: bool = True
    search_provider: str = "auto"
    search_api_key: str = ""
    searxng_url: str = ""
    wiki_user_agent: str = WIKI_USER_AGENT
    workspace_dir: Path = Path("./data/workspace")
    disabled_tools: Set[str] = field(default_factory=set)
    enabled_tools_only: Set[str] = field(default_factory=set)
    sandbox_memory_mb: int = 1024
    max_context_tokens: int = 24000
    compact_ratio: float = 0.85
    ui_language: str = "ar"
    stream_edits: bool = True
    stream_edit_interval: float = 1.0
    show_reasoning: bool = False
    show_tool_trace: bool = True
    show_usage: bool = True
    rate_limit_per_min: int = 20
    db_path: Path = Path("./data/bot.sqlite3")
    usage_retention_days: int = 60
    cf_base_url: str = CF_BASE_URL
    cf_origin: str = CF_ORIGIN
    ws_max_retries: int = 4
    ws_handshake_drain: float = 1.2
    ws_idle_timeout: float = 120.0
    ws_heartbeat: float = 25.0
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    )
    webhook_url: str = ""
    webhook_secret: str = ""
    webhook_port: int = 8443
    proxy_url: str = ""
    log_level: str = "INFO"
    log_file: str = "./data/bot.log"

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Settings":
        if env_file is None:
            env_file = _env("ENV_FILE", ENV_FILE)
        _load_dotenv(env_file)
        admins_raw = _list("ADMIN_IDS", [a.strip() for a in ADMIN_IDS.split(",") if a.strip()])
        admin_ids = _int_list("ADMIN_IDS", ADMIN_IDS)
        admin_usernames = {
            item.lower().lstrip("@")
            for item in admins_raw
            if not item.lstrip("-").isdigit()
        }
        self = cls(
            bot_token=_env("BOT_TOKEN", BOT_TOKEN),
            bot_name=_env("BOT_NAME", BOT_NAME),
            menu_buttons=_bool("MENU_BUTTONS", MENU_BUTTONS == "true"),
            button_colors=_bool("BUTTON_COLORS", BUTTON_COLORS == "true"),
            admin_ids=admin_ids,
            admin_usernames=admin_usernames,
            access_mode=(_env("ACCESS_MODE", ACCESS_MODE).lower() or "admins"),
            allowed_chats=_int_list("ALLOWED_CHATS", ALLOWED_CHATS),
            allow_groups=_bool("ALLOW_GROUPS", ALLOW_GROUPS == "true"),
            default_model=_env("DEFAULT_MODEL", DEFAULT_MODEL),
            fallback_models=_list("FALLBACK_MODELS", [m.strip() for m in FALLBACK_MODELS.split(",") if m.strip()]),
            utility_model=_env("UTILITY_MODEL", UTILITY_MODEL),
            system_prompt=_env("SYSTEM_PROMPT", SYSTEM_PROMPT),
            max_steps=_int("MAX_STEPS", int(MAX_STEPS)),
            step_timeout=_float("STEP_TIMEOUT", float(STEP_TIMEOUT)),
            tool_timeout=_float("TOOL_TIMEOUT", float(TOOL_TIMEOUT)),
            max_tool_output=_int("MAX_TOOL_OUTPUT", int(MAX_TOOL_OUTPUT)),
            temperature=_float("TEMPERATURE", float(TEMPERATURE)),
            enable_python=_bool("ENABLE_PYTHON", ENABLE_PYTHON == "true"),
            enable_shell=_bool("ENABLE_SHELL", ENABLE_SHELL == "true"),
            enable_web_tools=_bool("ENABLE_WEB_TOOLS", ENABLE_WEB_TOOLS == "true"),
            search_provider=_env("SEARCH_PROVIDER", SEARCH_PROVIDER).lower() or "auto",
            search_api_key=_env("SEARCH_API_KEY", SEARCH_API_KEY),
            searxng_url=_env("SEARXNG_URL", SEARXNG_URL).rstrip("/"),
            wiki_user_agent=_env("WIKI_USER_AGENT", WIKI_USER_AGENT),
            workspace_dir=Path(_env("WORKSPACE_DIR", WORKSPACE_DIR)),
            disabled_tools={t.lower() for t in _list("DISABLED_TOOLS", [t.strip() for t in DISABLED_TOOLS.split(",") if t.strip()])},
            enabled_tools_only={t.lower() for t in _list("ENABLED_TOOLS_ONLY", [t.strip() for t in ENABLED_TOOLS_ONLY.split(",") if t.strip()])},
            sandbox_memory_mb=_int("SANDBOX_MEMORY_MB", int(SANDBOX_MEMORY_MB)),
            max_context_tokens=_int("MAX_CONTEXT_TOKENS", int(MAX_CONTEXT_TOKENS)),
            compact_ratio=_float("COMPACT_RATIO", float(COMPACT_RATIO)),
            ui_language=_env("UI_LANGUAGE", UI_LANGUAGE).lower() or "ar",
            stream_edits=_bool("STREAM_EDITS", STREAM_EDITS == "true"),
            stream_edit_interval=_float("STREAM_EDIT_INTERVAL", float(STREAM_EDIT_INTERVAL)),
            show_reasoning=_bool("SHOW_REASONING", SHOW_REASONING == "true"),
            show_tool_trace=_bool("SHOW_TOOL_TRACE", SHOW_TOOL_TRACE == "true"),
            show_usage=_bool("SHOW_USAGE", SHOW_USAGE == "true"),
            rate_limit_per_min=_int("RATE_LIMIT_PER_MIN", int(RATE_LIMIT_PER_MIN)),
            db_path=Path(_env("DB_PATH", DB_PATH)),
            usage_retention_days=_int("USAGE_RETENTION_DAYS", int(USAGE_RETENTION_DAYS)),
            cf_base_url=_env("CF_BASE_URL", CF_BASE_URL).rstrip("/"),
            cf_origin=_env("CF_ORIGIN", CF_ORIGIN).rstrip("/"),
            ws_max_retries=_int("WS_MAX_RETRIES", int(WS_MAX_RETRIES)),
            ws_handshake_drain=_float("WS_HANDSHAKE_DRAIN", float(WS_HANDSHAKE_DRAIN)),
            ws_idle_timeout=_float("WS_IDLE_TIMEOUT", float(WS_IDLE_TIMEOUT)),
            ws_heartbeat=_float("WS_HEARTBEAT", float(WS_HEARTBEAT)),
            user_agent=_env("CF_USER_AGENT", cls.user_agent),
            webhook_url=_env("WEBHOOK_URL", WEBHOOK_URL),
            webhook_secret=_env("WEBHOOK_SECRET", WEBHOOK_SECRET),
            webhook_port=_int("WEBHOOK_PORT", int(WEBHOOK_PORT)),
            proxy_url=_env("PROXY_URL", PROXY_URL),
            log_level=_env("LOG_LEVEL", LOG_LEVEL).upper(),
            log_file=_env("LOG_FILE", LOG_FILE),
        )
        self.validate()
        return self

    def validate(self) -> None:
        if not self.bot_token or ":" not in self.bot_token:
            raise SystemExit(
                "\n[إعدادات] BOT_TOKEN مفقود أو غير صالح.\n"
                "  1) انسخ .env.example إلى .env\n"
                "  2) ضع التوكن من @BotFather في BOT_TOKEN\n"
                "  3) ضع رقمك في ADMIN_IDS (اعرفه بأمر /id)\n"
            )
        if self.access_mode not in ("admins", "allowlist", "open"):
            self.access_mode = "admins"
        if self.max_steps < 1:
            self.max_steps = 1
        if self.max_steps > 40:
            self.max_steps = 40
        if self.stream_edit_interval < 0.4:
            self.stream_edit_interval = 0.4
        if self.default_model not in self.fallback_models:
            self.fallback_models = [self.default_model] + list(self.fallback_models)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        (self.workspace_dir / "outputs").mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.log_file:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

    def is_admin(self, user_id: Optional[int], username: Optional[str] = None) -> bool:
        if user_id is not None and user_id in self.admin_ids:
            return True
        if username and username.lower().lstrip("@") in self.admin_usernames:
            return True
        return False

    def is_chat_allowed(self, chat_id: int, chat_type: str = "private") -> bool:
        if self.access_mode == "open":
            return True
        if chat_id in self.admin_ids:
            return True
        if self.access_mode == "allowlist" and chat_id in self.allowed_chats:
            return True
        if chat_type in ("group", "supergroup") and self.allow_groups and chat_id in self.allowed_chats:
            return True
        return False

    def to_safe_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["bot_token"] = "***"
        data["webhook_secret"] = "***" if self.webhook_secret else ""
        data["proxy_url"] = "***" if self.proxy_url else ""
        data["workspace_dir"] = str(self.workspace_dir)
        data["db_path"] = str(self.db_path)
        data["admin_usernames"] = sorted(self.admin_usernames)
        data["disabled_tools"] = sorted(self.disabled_tools)
        data["enabled_tools_only"] = sorted(self.enabled_tools_only)
        return data


def _load_dotenv(path: str) -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(path, override=False)
        return
    except Exception:
        pass
    p = Path(path)
    if not p.is_file():
        return
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
    except OSError:
        pass


def load_settings(env_file: Optional[str] = None) -> Settings:
    return Settings.from_env(env_file)
