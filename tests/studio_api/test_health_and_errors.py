"""Seam tests for TASK-01: FastAPI bridge core, AppError, StudioLogger, and /health."""

from __future__ import annotations

import io
import json
from pathlib import Path

from fastapi.testclient import TestClient

from studio_api.adapters.fake_adapter import InMemoryFakeAdapter
from studio_api.app import create_app
from studio_api.errors import AppError
from studio_api.logger import get_logger, redact_sensitive


def test_health_echoes_request_id_and_returns_ok(tmp_path: Path) -> None:
    app = create_app(adapter=InMemoryFakeAdapter(episodes_root=tmp_path), episodes_root=tmp_path)
    client = TestClient(app)

    res = client.get("/health", headers={"X-Request-Id": "req-qa-001"})
    assert res.status_code == 200
    assert res.headers["X-Request-Id"] == "req-qa-001"
    body = res.json()
    assert body["status"] == "ok"
    assert body["version"] == "1.0.0"
    assert body["uptimeSec"] >= 0
    assert body["activeJobs"] == 0
    assert isinstance(body["gdriveConfigured"], bool)


def test_app_error_envelope_includes_request_id(tmp_path: Path) -> None:
    app = create_app(adapter=InMemoryFakeAdapter(episodes_root=tmp_path), episodes_root=tmp_path)

    @app.get("/_test/boom")
    def _boom() -> None:
        raise AppError(
            code="VALIDATION_ERROR",
            message="Invalid input payload.",
            status_code=400,
            details={"field": "topic"},
        )

    client = TestClient(app)
    res = client.get("/_test/boom", headers={"X-Request-Id": "req-err-42"})
    assert res.status_code == 400
    assert res.headers["X-Request-Id"] == "req-err-42"
    assert res.json() == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input payload.",
            "requestId": "req-err-42",
            "details": {"field": "topic"},
        }
    }


def test_logger_redacts_secrets_and_emits_single_line_json(monkeypatch) -> None:
    monkeypatch.setenv("STUDIO_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    stream = io.StringIO()
    logger = get_logger("test_module", stream=stream)

    logger.info(
        "auth.attempt",
        "Checking credentials",
        password="super-secret-password",
        token="jwt-abc-123",
        apiKey="sk-live-999",
        authorization="Bearer xyz",
        safeField="visible-value",
    )

    raw_line = stream.getvalue().strip()
    parsed = json.loads(raw_line)
    assert parsed["level"] == "INFO"
    assert parsed["module"] == "test_module"
    assert parsed["action"] == "auth.attempt"
    assert parsed["context"]["password"] == "[REDACTED]"
    assert parsed["context"]["token"] == "[REDACTED]"
    assert parsed["context"]["apiKey"] == "[REDACTED]"
    assert parsed["context"]["authorization"] == "[REDACTED]"
    assert parsed["context"]["safeField"] == "visible-value"


def test_redact_sensitive_nested_structures() -> None:
    payload = {
        "user": "creator@ramdanistudio.com",
        "nested": {"secret": "s3cr3t", "otp": "123456", "ok": 1},
    }
    cleaned = redact_sensitive(payload)
    assert cleaned["user"] == "creator@ramdanistudio.com"
    assert cleaned["nested"]["secret"] == "[REDACTED]"
    assert cleaned["nested"]["otp"] == "[REDACTED]"
    assert cleaned["nested"]["ok"] == 1
