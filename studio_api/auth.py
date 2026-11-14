"""Single-admin AuthService, sliding-window IpRateLimiter, and StudioSessionMiddleware."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import threading
import time
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from fastapi import Request, Response

from studio_api.errors import AppError
from studio_api.logger import get_logger
from studio_api.schemas import AuthSessionState

_log = get_logger("auth")

SESSION_COOKIE_NAME = "StudioSession"
SESSION_TTL_HOURS = 24
MAX_FAILED_ATTEMPTS = 5
WINDOW_SECONDS = 15 * 60


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


class IpRateLimiter:
    """Sliding-window IP rate limiter blocking after max_attempts within window_seconds."""

    # shortcut: in-memory IP window; upgrade to Redis if running multiple API replicas
    def __init__(
        self,
        max_attempts: int = MAX_FAILED_ATTEMPTS,
        window_seconds: int = WINDOW_SECONDS,
    ) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._guard = threading.Lock()
        self._attempts: dict[str, deque[float]] = {}

    def _prune(self, dq: deque[float], now: float) -> None:
        cutoff = now - self.window_seconds
        while dq and dq[0] <= cutoff:
            dq.popleft()

    def check_blocked(self, client_ip: str, now: float | None = None) -> int | None:
        """Return Retry-After seconds if blocked, else None."""
        ts = now if now is not None else time.monotonic()
        with self._guard:
            dq = self._attempts.get(client_ip)
            if not dq:
                return None
            self._prune(dq, ts)
            if len(dq) >= self.max_attempts:
                retry_after = max(1, int(self.window_seconds - (ts - dq[0])))
                return retry_after
            return None

    def record_failure(self, client_ip: str, now: float | None = None) -> None:
        ts = now if now is not None else time.monotonic()
        with self._guard:
            dq = self._attempts.setdefault(client_ip, deque())
            self._prune(dq, ts)
            dq.append(ts)

    def reset(self, client_ip: str) -> None:
        with self._guard:
            self._attempts.pop(client_ip, None)


class AuthService:
    """Single-admin Creator credential verifier and HS256 StudioSession JWT issuer."""

    def __init__(
        self,
        admin_email: str | None = None,
        password_hash: str | None = None,
        jwt_secret: str | None = None,
        cookie_secure: bool | None = None,
        rate_limiter: IpRateLimiter | None = None,
    ) -> None:
        self.admin_email = (admin_email if admin_email is not None else os.getenv("STUDIO_ADMIN_EMAIL", "")).strip()
        self.password_hash = (
            password_hash if password_hash is not None else os.getenv("STUDIO_ADMIN_PASSWORD_HASH", "")
        ).strip()
        self.jwt_secret = (
            jwt_secret
            if jwt_secret is not None
            else os.getenv("STUDIO_JWT_SECRET", "dev-insecure-change-me-in-production")
        )
        env_mode = os.getenv("STUDIO_ENV", "development").strip().lower()
        if env_mode == "production" and (
            not self.jwt_secret or self.jwt_secret == "dev-insecure-change-me-in-production"
        ):
            raise RuntimeError(
                "STUDIO_JWT_SECRET must be set to a strong secret when STUDIO_ENV=production."
            )
        if cookie_secure is None:
            env_secure = os.getenv("STUDIO_COOKIE_SECURE", "true").strip().lower()
            self.cookie_secure = env_secure not in {"false", "0", "no"}
        else:
            self.cookie_secure = cookie_secure
        self.rate_limiter = rate_limiter or IpRateLimiter()

    def _verify_password(self, plain: str) -> bool:
        if not self.password_hash:
            return False
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), self.password_hash.encode("utf-8"))
        except Exception:
            return False

    def _sign_jwt(self, email: str, exp_dt: datetime) -> str:
        header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode("utf-8"))
        payload = _b64url_encode(
            json.dumps({"sub": email, "exp": int(exp_dt.timestamp())}).encode("utf-8")
        )
        signing_input = f"{header}.{payload}".encode("ascii")
        sig = hmac.new(self.jwt_secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
        return f"{header}.{payload}.{_b64url_encode(sig)}"

    def verify_session(self, token: str | None) -> AuthSessionState:
        if not token or token.count(".") != 2:
            raise AppError("AUTH_UNAUTHORIZED", "Authentication required.", status_code=401)
        header_b64, payload_b64, sig_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        expected_sig = hmac.new(self.jwt_secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
        try:
            actual_sig = _b64url_decode(sig_b64)
            if not hmac.compare_digest(expected_sig, actual_sig):
                raise AppError("AUTH_UNAUTHORIZED", "Invalid session token.", status_code=401)
            payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        except AppError:
            raise
        except Exception as exc:
            raise AppError("AUTH_UNAUTHORIZED", "Invalid session token.", status_code=401, cause=exc)

        exp = int(payload.get("exp", 0))
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if exp <= now_ts:
            raise AppError("AUTH_UNAUTHORIZED", "Session expired.", status_code=401)

        email = str(payload.get("sub", ""))
        expires_iso = datetime.fromtimestamp(exp, tz=timezone.utc).isoformat()
        return AuthSessionState(authenticated=True, email=email, expiresAt=expires_iso)

    def authenticate(self, email: str, password: str, client_ip: str) -> tuple[str, AuthSessionState]:
        retry_after = self.rate_limiter.check_blocked(client_ip)
        if retry_after is not None:
            _log.warn("auth.rate_limited", "Login rate limit exceeded", clientIp=client_ip)
            raise AppError(
                code="RATE_LIMITED",
                message="Too many failed login attempts. Try again in 15 minutes.",
                status_code=429,
                headers={"Retry-After": str(retry_after)},
            )

        email_ok = bool(self.admin_email) and secrets.compare_digest(
            email.strip().lower(), self.admin_email.lower()
        )
        pass_ok = self._verify_password(password)
        if not (email_ok and pass_ok):
            self.rate_limiter.record_failure(client_ip)
            _log.warn("auth.failed", "Invalid login credentials", clientIp=client_ip)
            raise AppError(
                code="AUTH_UNAUTHORIZED",
                message="Invalid email or password.",
                status_code=401,
            )

        self.rate_limiter.reset(client_ip)
        exp_dt = datetime.now(timezone.utc) + timedelta(hours=SESSION_TTL_HOURS)
        token = self._sign_jwt(self.admin_email, exp_dt)
        session = AuthSessionState(
            authenticated=True,
            email=self.admin_email,
            expiresAt=exp_dt.isoformat(),
        )
        _log.info("auth.login", "Creator signed in", email=self.admin_email)
        return token, session

    def issue_session_cookie(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=token,
            httponly=True,
            secure=self.cookie_secure,
            samesite="lax",
            path="/",
            max_age=SESSION_TTL_HOURS * 3600,
        )

    def clear_session_cookie(self, response: Response) -> None:
        response.delete_cookie(
            key=SESSION_COOKIE_NAME,
            httponly=True,
            secure=self.cookie_secure,
            samesite="lax",
            path="/",
        )


def extract_client_ip(request: Request) -> str:
    trust_proxy = os.getenv("STUDIO_TRUST_PROXY", "false").strip().lower() in {"true", "1", "yes"}
    if trust_proxy:
        forwarded = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if forwarded:
            return forwarded
    return request.client.host if request.client else "127.0.0.1"
