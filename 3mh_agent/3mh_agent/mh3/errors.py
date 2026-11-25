# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
from typing import Optional
__all__ = [
    "BotError",
    "BackendError",
    "RateLimitedError",
    "ModelGatedError",
    "ConnectionLost",
    "HandshakeError",
    "StreamTimeout",
    "Cancelled",
    "ToolError",
    "ToolNotFound",
    "ToolDenied",
    "ToolTimeout",
    "ContextOverflow",
    "ConfigError",
]


class BotError(Exception):
    retryable: bool = False
    try_fallback: bool = False

    def __init__(self, message: str, *, detail: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail


class BackendError(BotError):
    pass


class RateLimitedError(BackendError):
    retryable = True
    try_fallback = True


class ModelGatedError(BackendError):
    try_fallback = True


class ContextOverflow(BackendError):
    try_fallback = True


class ConnectionLost(BackendError):
    retryable = True


class HandshakeError(BackendError):
    retryable = True


class StreamTimeout(BackendError):
    retryable = True


class Cancelled(BotError):
    pass


class ToolError(BotError):
    pass


class ToolNotFound(ToolError):
    pass


class ToolDenied(ToolError):
    pass


class ToolTimeout(ToolError):
    pass


class ConfigError(BotError):
    pass
