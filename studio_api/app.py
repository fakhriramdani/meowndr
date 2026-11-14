"""FastAPI application factory for @meowndr Automation Reels Maker Studio."""

from __future__ import annotations

import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from studio_api.adapters.pipeline_adapter import LiveLibraryAdapter, PipelinePort
from studio_api.auth import AuthService
from studio_api.errors import AppError
from studio_api.job_runner import BackgroundJobRunner, EpisodeLockManager
from studio_api.logger import (
    get_logger,
    get_request_id,
    reset_request_id,
    set_request_id,
)
from studio_api.router import build_router
from studio_api.schemas import HealthResponse

_log = get_logger("app")

_DEFAULT_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://reels.ramdanistudio.com",
]


def _resolve_trusted_origins() -> list[str]:
    raw = os.getenv("TRUSTED_ORIGINS", "").strip()
    if not raw:
        return list(_DEFAULT_TRUSTED_ORIGINS)
    extra = [item.strip() for item in raw.split(",") if item.strip()]
    merged = list(dict.fromkeys(_DEFAULT_TRUSTED_ORIGINS + extra))
    return merged


def create_app(
    adapter: PipelinePort | None = None,
    episodes_root: Path | None = None,
    auth_service: AuthService | None = None,
    require_auth: bool | None = None,
    serve_static: bool | None = None,
) -> FastAPI:
    """Create and configure the FastAPI studio_api application."""
    repo_root = Path(__file__).resolve().parent.parent
    resolved_episodes = episodes_root or (repo_root / "episodes")
    resolved_adapter: PipelinePort = adapter or LiveLibraryAdapter(
        repo_root=repo_root,
        episodes_root=resolved_episodes,
    )
    resolved_auth = auth_service or AuthService()
    if require_auth is None:
        env_mode = os.getenv("STUDIO_ENV", "development").strip().lower()
        enforce_auth = env_mode == "production" or bool(resolved_auth.admin_email)
    else:
        enforce_auth = require_auth

    lock_manager = EpisodeLockManager()
    runner = BackgroundJobRunner(lock_manager=lock_manager, max_workers=2)
    started_at = time.monotonic()

    app = FastAPI(title="@meowndr Automation Reels Maker Studio", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_resolve_trusted_origins(),
        allow_origin_regex=r"^https://[a-z0-9-]+\.ramdanistudio\.com$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-Id"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next: Any) -> Any:
        req_id = request.headers.get("X-Request-Id") or f"req-{uuid.uuid4().hex[:12]}"
        token = set_request_id(req_id)
        t0 = time.monotonic()
        try:
            response = await call_next(request)
            response.headers["X-Request-Id"] = req_id
            dur_ms = round((time.monotonic() - t0) * 1000, 1)
            _log.info(
                "http.request",
                f"{request.method} {request.url.path} -> {response.status_code}",
                durationMs=dur_ms,
                status=response.status_code,
            )
            return response
        finally:
            reset_request_id(token)

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        req_id = get_request_id()
        if exc.status_code >= 500:
            _log.error("http.app_error", exc.message, exc=exc, code=exc.code)
        else:
            _log.warn("http.app_error", exc.message, code=exc.code, status=exc.status_code)
        headers = {"X-Request-Id": req_id, **exc.headers}
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_envelope(req_id),
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        req_id = get_request_id()
        _log.warn("http.validation_error", "Request validation failed", errors=exc.errors())
        err = AppError(
            code="VALIDATION_ERROR",
            message="Request payload validation failed.",
            status_code=400,
            details=exc.errors(),
        )
        return JSONResponse(
            status_code=400,
            content=err.to_envelope(req_id),
            headers={"X-Request-Id": req_id},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = get_request_id()
        _log.error("http.unhandled", "Unhandled server error", exc=exc)
        err = AppError(
            code="INTERNAL_ERROR",
            message="An unexpected internal error occurred.",
            status_code=500,
        )
        return JSONResponse(
            status_code=500,
            content=err.to_envelope(req_id),
            headers={"X-Request-Id": req_id},
        )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        gdrive_ok = bool(shutil.which("rclone")) or Path.home().joinpath(".config/rclone/rclone.conf").exists()
        return HealthResponse(
            status="ok",
            version="1.0.0",
            uptimeSec=round(time.monotonic() - started_at, 2),
            activeJobs=runner.active_job_count,
            gdriveConfigured=gdrive_ok,
        )

    app.include_router(
        build_router(
            adapter=resolved_adapter,
            runner=runner,
            auth_service=resolved_auth,
            require_auth=enforce_auth,
        )
    )

    dist_dir = repo_root / "studio-ui" / "dist"
    should_serve_static = (
        serve_static
        if serve_static is not None
        else os.getenv("STUDIO_ENV", "development").strip().lower() == "production"
    )
    if should_serve_static and dist_dir.is_dir() and (dist_dir / "index.html").is_file():
        assets_dir = dist_dir / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        def serve_spa(full_path: str) -> FileResponse:
            if full_path == "api" or full_path.startswith("api/"):
                raise AppError("NOT_FOUND", "API endpoint not found.", 404)
            candidate = (dist_dir / full_path).resolve()
            if full_path and candidate.is_file() and str(candidate).startswith(str(dist_dir.resolve())):
                return FileResponse(candidate)
            return FileResponse(dist_dir / "index.html")

    return app
