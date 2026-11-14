"""Unified AppError exception hierarchy for studio_api."""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Domain and transport error serialized into the standard JSON error envelope."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: Any = None,
        cause: BaseException | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        self.headers = headers or {}
        if cause is not None:
            self.__cause__ = cause

    def to_envelope(self, request_id: str) -> dict[str, Any]:
        """Serialize error into { error: { code, message, requestId, details? } }."""
        body: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "requestId": request_id,
        }
        if self.details is not None:
            body["details"] = self.details
        return {"error": body}
