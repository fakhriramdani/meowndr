"""Seam tests for TASK-09: Single-Admin Auth, StudioSessionMiddleware, Rate Limiter, and CORS."""

from __future__ import annotations

from pathlib import Path

import bcrypt
from fastapi.testclient import TestClient

from studio_api.adapters.fake_adapter import InMemoryFakeAdapter
from studio_api.app import create_app
from studio_api.auth import AuthService


def _make_auth_client(tmp_path: Path, cookie_secure: bool = True) -> tuple[TestClient, str, str]:
    email = "creator@ramdanistudio.com"
    password = "correct-horse-battery-staple"
    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    auth = AuthService(
        admin_email=email,
        password_hash=pw_hash,
        jwt_secret="test-jwt-secret-key",
        cookie_secure=cookie_secure,
    )
    app = create_app(
        adapter=InMemoryFakeAdapter(tmp_path),
        episodes_root=tmp_path,
        auth_service=auth,
        require_auth=True,
    )
    return TestClient(app, base_url="https://testserver"), email, password


def test_unauthenticated_routes_return_401_while_health_is_public(tmp_path: Path) -> None:
    client, _, _ = _make_auth_client(tmp_path)
    assert client.get("/health").status_code == 200
    assert client.get("/api/episodes").status_code == 401
    assert client.get("/api/episodes/ep-1").status_code == 401
    assert client.post("/api/trends/discover", json={"niche": "science", "ageCategory": "Umum"}).status_code == 401
    assert client.post("/api/auth/signup", json={}).status_code in (404, 405)
    assert client.post("/api/auth/register", json={}).status_code in (404, 405)


def test_login_issues_httponly_secure_samesite_cookie_and_logout_clears(tmp_path: Path) -> None:
    client, email, password = _make_auth_client(tmp_path, cookie_secure=True)
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200
    body = login_res.json()
    assert body["authenticated"] is True
    assert body["email"] == email

    set_cookie = login_res.headers.get("set-cookie", "")
    assert "StudioSession=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Secure" in set_cookie
    assert "SameSite=lax" in set_cookie or "SameSite=Lax" in set_cookie

    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    eps_res = client.get("/api/episodes")
    assert eps_res.status_code == 200

    logout_res = client.post("/api/auth/logout", json={})
    assert logout_res.status_code == 200
    assert logout_res.json()["authenticated"] is False

    client.cookies.clear()
    assert client.get("/api/auth/me").status_code == 401


def test_invalid_credentials_generic_401_and_rate_limit_429(tmp_path: Path) -> None:
    client, email, password = _make_auth_client(tmp_path, cookie_secure=False)

    bad_email = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": password})
    assert bad_email.status_code == 401
    assert bad_email.json()["error"]["message"] == "Invalid email or password."

    for _ in range(4):
        res = client.post("/api/auth/login", json={"email": email, "password": "wrong-password"})
        assert res.status_code == 401
        assert res.json()["error"]["message"] == "Invalid email or password."

    # 6th attempt within 15 minutes must return 429 even with valid credentials
    blocked = client.post("/api/auth/login", json={"email": email, "password": password})
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMITED"
    assert "Retry-After" in blocked.headers


def test_trusted_origins_cors_allows_subdomain_and_rejects_evil(tmp_path: Path) -> None:
    client, _, _ = _make_auth_client(tmp_path)
    ok_cors = client.options(
        "/api/auth/login",
        headers={
            "Origin": "https://reels.ramdanistudio.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert ok_cors.headers.get("access-control-allow-origin") == "https://reels.ramdanistudio.com"
    assert ok_cors.headers.get("access-control-allow-credentials") == "true"

    evil_cors = client.options(
        "/api/auth/login",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert evil_cors.headers.get("access-control-allow-origin") is None


def test_production_fails_fast_when_jwt_secret_is_insecure(monkeypatch) -> None:
    monkeypatch.setenv("STUDIO_ENV", "production")
    monkeypatch.delenv("STUDIO_JWT_SECRET", raising=False)
    try:
        AuthService(admin_email="creator@ramdanistudio.com", password_hash="x")
        assert False, "Expected RuntimeError for default JWT secret in production"
    except RuntimeError as exc:
        assert "STUDIO_JWT_SECRET" in str(exc)

    monkeypatch.setenv("STUDIO_JWT_SECRET", "dev-insecure-change-me-in-production")
    try:
        AuthService(admin_email="creator@ramdanistudio.com", password_hash="x")
        assert False, "Expected RuntimeError for dev-insecure secret in production"
    except RuntimeError as exc:
        assert "STUDIO_JWT_SECRET" in str(exc)
