"""Dual-mode structured logger with X-Request-Id correlation and secret redaction."""

from __future__ import annotations

import contextvars
import json
import os
import re
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, TextIO

_request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

_SENSITIVE_PATTERN = re.compile(
    r"(password|pass|token|access_token|refresh_token|secret|api_key|apikey|authorization|cookie|otp|pin|cvv|credit_card|creditcard)",
    re.IGNORECASE,
)

_LEVEL_ORDER = {"debug": 10, "info": 20, "warn": 30, "warning": 30, "error": 40}


def set_request_id(request_id: str) -> contextvars.Token[str]:
    """Bind requestId to the current async/thread context."""
    return _request_id_var.set(request_id)


def reset_request_id(token: contextvars.Token[str]) -> None:
    """Restore previous requestId context."""
    _request_id_var.reset(token)


def get_request_id() -> str:
    """Return active requestId or '-' when outside a request."""
    return _request_id_var.get()


def redact_sensitive(value: Any) -> Any:
    """Recursively scrub sensitive dictionary keys to '[REDACTED]'."""
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            if _SENSITIVE_PATTERN.search(str(key)):
                cleaned[str(key)] = "[REDACTED]"
            else:
                cleaned[str(key)] = redact_sensitive(item)
        return cleaned
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    if isinstance(value, tuple):
        return [redact_sensitive(item) for item in value]
    return value


class StudioLogger:
    """Structured logger supporting pretty dev output and single-line JSON in prod/test."""

    def __init__(self, module: str, stream: TextIO | None = None) -> None:
        self.module = module
        self._stream = stream

    def _active_level(self) -> int:
        raw = os.getenv("LOG_LEVEL", "info").strip().lower()
        return _LEVEL_ORDER.get(raw, 20)

    def _is_json_mode(self) -> bool:
        env = os.getenv("STUDIO_ENV", "development").strip().lower()
        return env in {"production", "prod", "test"}

    def _emit(
        self,
        level_name: str,
        level_num: int,
        action: str,
        message: str,
        context: dict[str, Any],
    ) -> None:
        if level_num < self._active_level():
            return
        now = datetime.now(timezone.utc)
        req_id = get_request_id()
        safe_context = redact_sensitive(context) if context else {}
        duration_ms = safe_context.pop("durationMs", None) if isinstance(safe_context, dict) else None
        out = self._stream or sys.stdout

        if self._is_json_mode():
            record: dict[str, Any] = {
                "timestamp": now.isoformat(),
                "level": level_name,
                "requestId": req_id,
                "module": self.module,
                "action": action,
                "message": message,
            }
            if duration_ms is not None:
                record["durationMs"] = duration_ms
            if safe_context:
                record["context"] = safe_context
            out.write(json.dumps(record, default=str) + "\n")
            out.flush()
            return

        ts = now.strftime("%H:%M:%S.%f")[:-3]
        suffix = f" {json.dumps(safe_context, default=str)}" if safe_context else ""
        dur = f" ({duration_ms}ms)" if duration_ms is not None else ""
        out.write(f"[{ts}] {level_name:<5} [{self.module}:{action}] (reqId:{req_id}){dur} {message}{suffix}\n")
        out.flush()

    def debug(self, action: str, message: str, **context: Any) -> None:
        self._emit("DEBUG", 10, action, message, context)

    def info(self, action: str, message: str, **context: Any) -> None:
        self._emit("INFO", 20, action, message, context)

    def warn(self, action: str, message: str, **context: Any) -> None:
        self._emit("WARN", 30, action, message, context)

    def error(
        self,
        action: str,
        message: str,
        exc: BaseException | None = None,
        **context: Any,
    ) -> None:
        if exc is not None:
            context["errorType"] = type(exc).__name__
            context["errorDetail"] = str(exc)
            context["stack"] = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        self._emit("ERROR", 40, action, message, context)


def get_logger(module: str, stream: TextIO | None = None) -> StudioLogger:
    """Create a StudioLogger scoped to a module name."""
    return StudioLogger(module=module, stream=stream)
