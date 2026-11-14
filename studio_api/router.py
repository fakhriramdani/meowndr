"""REST and SSE endpoints for @meowndr Automation Reels Maker Studio."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import FileResponse, StreamingResponse

from studio_api.adapters.pipeline_adapter import PipelinePort
from studio_api.auth import SESSION_COOKIE_NAME, AuthService, extract_client_ip
from studio_api.episode_store import resolve_safe_episode_path
from studio_api.errors import AppError
from studio_api.job_runner import BackgroundJobRunner
from studio_api.logger import get_logger, get_request_id
from studio_api.schemas import (
    ArchiveEpisodeRequest,
    AuthSessionState,
    CreateEpisodeRequest,
    Gate1ApproveRequest,
    GateApproveNotesRequest,
    GateRevisionRequest,
    LoginRequest,
    ScriptBeat,
    TrendDiscoverRequest,
    UpdateScriptRequest,
)

_log = get_logger("router")

_VALID_NICHES = {"science", "history", "geography", "technology", "mystery"}
_VALID_AGES = {"Remaja 13-17", "Dewasa Muda 18-35", "Umum"}
_RANGE_RE = re.compile(r"bytes=(\d+)-(\d*)")


def build_router(
    adapter: PipelinePort,
    runner: BackgroundJobRunner,
    auth_service: AuthService,
    require_auth: bool,
) -> APIRouter:
    """Construct the API router with injected PipelinePort, JobRunner, and AuthService."""
    router = APIRouter(prefix="/api")

    def require_session(request: Request) -> AuthSessionState | None:
        if not require_auth:
            return None
        token = request.cookies.get(SESSION_COOKIE_NAME)
        return auth_service.verify_session(token)

    # ------------------------------------------------------------------
    # Authentication (/api/auth/*)
    # ------------------------------------------------------------------

    @router.post("/auth/login")
    def login(payload: LoginRequest, request: Request, response: Response) -> dict[str, Any]:
        client_ip = extract_client_ip(request)
        token, session = auth_service.authenticate(payload.email, payload.password, client_ip)
        auth_service.issue_session_cookie(response, token)
        return session.model_dump()

    @router.post("/auth/logout")
    def logout(response: Response) -> dict[str, Any]:
        auth_service.clear_session_cookie(response)
        _log.info("auth.logout", "Creator signed out")
        return {"authenticated": False}

    @router.get("/auth/me")
    def auth_me(request: Request) -> dict[str, Any]:
        token = request.cookies.get(SESSION_COOKIE_NAME)
        session = auth_service.verify_session(token)
        return session.model_dump()

    # ------------------------------------------------------------------
    # Trend Discovery (/api/trends/*)
    # ------------------------------------------------------------------

    @router.post("/trends/discover")
    @router.post("/trends/research")
    def discover_trends(
        payload: TrendDiscoverRequest,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        niche = payload.niche.strip().lower()
        age = payload.ageCategory.strip()
        if niche not in _VALID_NICHES or age not in _VALID_AGES:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Select both Niche and AgeCategory to start TopicResearchMode.",
                status_code=400,
                details={"niche": payload.niche, "ageCategory": payload.ageCategory},
            )
        opportunities = adapter.discover_trends(
            niche=niche,  # type: ignore[arg-type]
            age_category=age,  # type: ignore[arg-type]
            exclude_premises=payload.excludePremises,
        )
        return {
            "opportunities": [item.model_dump() for item in opportunities],
            "requestId": get_request_id(),
        }

    # ------------------------------------------------------------------
    # Episodes (/api/episodes/*)
    # ------------------------------------------------------------------

    @router.get("/episodes")
    def list_episodes(
        includeArchived: bool = False,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        items = adapter.store.list_episodes(include_archived=includeArchived)
        return {"episodes": [item.model_dump() for item in items]}

    def _create_episode_impl(payload: CreateEpisodeRequest) -> dict[str, Any]:
        niche = payload.niche.strip().lower()
        age = payload.ageCategory.strip()
        if niche not in _VALID_NICHES or age not in _VALID_AGES:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Select both Niche and AgeCategory.",
                status_code=400,
            )
        topic_text = (payload.topic or payload.premise or "").strip()
        if len(topic_text) < 5 or len(topic_text) > 200:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Topic must be between 5 and 200 characters.",
                status_code=400,
                details={"field": "topic"},
            )
        slug, stages = adapter.create_episode(payload)
        job_id = runner.enqueue(
            slug=slug,
            action="fact_and_hooks",
            stages=stages,
            worker_fn=lambda emit: adapter.run_fact_and_hooks(slug, emit),
        )
        adapter.store.write_studio_meta(slug, {"activeJobId": job_id})
        episode = adapter.store.get_episode(slug)
        return {"episode": episode.model_dump(), "jobId": job_id}

    @router.post("/episodes", status_code=202)
    @router.post("/episodes/from-trend", status_code=202)
    @router.post("/episodes/direct", status_code=202)
    def create_episode(
        payload: CreateEpisodeRequest,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        return _create_episode_impl(payload)

    @router.get("/episodes/{slug}")
    def get_episode(
        slug: str,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        return adapter.store.get_episode(slug).model_dump()

    @router.post("/episodes/{slug}/archive")
    def archive_episode(
        slug: str,
        payload: ArchiveEpisodeRequest,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        summary = adapter.store.archive_episode(slug, confirmed=payload.confirmed)
        return summary.model_dump()

    # ------------------------------------------------------------------
    # Gate 1: Topic & Hook
    # ------------------------------------------------------------------

    @router.post("/episodes/{slug}/gates/1/approve", status_code=202)
    @router.post("/episodes/{slug}/gates/1", status_code=202)
    def approve_gate_1(
        slug: str,
        payload: Gate1ApproveRequest,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        if runner.lock_manager.is_locked(slug):
            raise AppError(
                code="EPISODE_LOCKED",
                message="Episode is currently executing a stage; wait for completion before triggering another action.",
                status_code=409,
            )
        stages = adapter.approve_gate_1(slug=slug, hook_id=payload.hookId, notes=payload.notes)
        job_id = runner.enqueue(
            slug=slug,
            action="script_generation",
            stages=stages,
            worker_fn=lambda emit: adapter.run_script_generation(slug, emit),
        )
        adapter.store.write_studio_meta(slug, {"activeJobId": job_id})
        episode = adapter.store.get_episode(slug)
        return {"episode": episode.model_dump(), "jobId": job_id}

    @router.post("/episodes/{slug}/gate1/revise")
    def revise_gate_1(
        slug: str,
        payload: GateRevisionRequest,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        if runner.lock_manager.is_locked(slug):
            raise AppError(
                code="EPISODE_LOCKED",
                message="Episode is currently executing a stage; wait for completion before triggering another action.",
                status_code=409,
            )
        episode = adapter.revise_gate_1(slug=slug, instructions=payload.instructions)
        return {"episode": episode.model_dump(), "requestId": get_request_id()}

    # ------------------------------------------------------------------
    # Gate 2: NarrationScript & Pacing Guard
    # ------------------------------------------------------------------

    @router.put("/episodes/{slug}/script")
    def update_script(
        slug: str,
        payload: UpdateScriptRequest,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        beats = [ScriptBeat(**b.model_dump()) for b in payload.beats]
        script = adapter.save_and_validate_script(slug=slug, beats=beats)
        return {"script": script.model_dump()}

    @router.post("/episodes/{slug}/script/condense")
    def condense_script(
        slug: str,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        script = adapter.condense_script(slug=slug)
        return {"script": script.model_dump()}

    @router.post("/episodes/{slug}/gates/2/approve", status_code=202)
    @router.post("/episodes/{slug}/gates/2", status_code=202)
    def approve_gate_2(
        slug: str,
        payload: GateApproveNotesRequest | None = None,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        if runner.lock_manager.is_locked(slug):
            raise AppError(
                code="EPISODE_LOCKED",
                message="Episode is currently executing a stage; wait for completion before triggering another action.",
                status_code=409,
            )
        notes = payload.notes if payload else None
        stages = adapter.prepare_gate_2_approval(slug=slug, notes=notes)
        job_id = runner.enqueue(
            slug=slug,
            action="render_pipeline",
            stages=stages,
            worker_fn=lambda emit: adapter.execute_render_pipeline(slug, stages, emit),
        )
        adapter.store.write_studio_meta(slug, {"activeJobId": job_id})
        episode = adapter.store.get_episode(slug)
        return {"episode": episode.model_dump(), "jobId": job_id}

    @router.post("/episodes/{slug}/gate2/revise")
    def revise_gate_2(
        slug: str,
        payload: GateRevisionRequest,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        if runner.lock_manager.is_locked(slug):
            raise AppError(
                code="EPISODE_LOCKED",
                message="Episode is currently executing a stage; wait for completion before triggering another action.",
                status_code=409,
            )
        episode = adapter.revise_gate_2(slug=slug, instructions=payload.instructions)
        return {"episode": episode.model_dump(), "requestId": get_request_id()}

    @router.post("/episodes/{slug}/gate2/reopen")
    def reopen_gate_2(
        slug: str,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        if runner.lock_manager.is_locked(slug):
            raise AppError(
                code="EPISODE_LOCKED",
                message="Episode is currently executing a stage; wait for completion before triggering another action.",
                status_code=409,
            )
        episode = adapter.reopen_gate_2(slug=slug)
        return {"episode": episode.model_dump(), "requestId": get_request_id()}

    @router.post("/episodes/{slug}/gate3/revise", status_code=202)
    def revise_gate_3(
        slug: str,
        payload: GateRevisionRequest,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        if runner.lock_manager.is_locked(slug):
            raise AppError(
                code="EPISODE_LOCKED",
                message="Episode is currently executing a stage; wait for completion before triggering another action.",
                status_code=409,
            )
        stages = adapter.prepare_gate_3_revision(slug=slug, instructions=payload.instructions)
        job_id = runner.enqueue(
            slug=slug,
            action="gate3_revision",
            stages=stages,
            worker_fn=lambda emit: adapter.execute_render_pipeline(slug, stages, emit),
        )
        adapter.store.write_studio_meta(slug, {"activeJobId": job_id})
        episode = adapter.store.get_episode(slug)
        return {"episode": episode.model_dump(), "jobId": job_id, "requestId": get_request_id()}

    # ------------------------------------------------------------------
    # Stages 7-11 Retry & SSE Job Streaming
    # ------------------------------------------------------------------

    @router.post("/episodes/{slug}/stages/{stage}/retry", status_code=202)
    def retry_stage(
        slug: str,
        stage: int,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        if runner.lock_manager.is_locked(slug):
            raise AppError(
                code="EPISODE_LOCKED",
                message="Episode is currently executing a stage; wait for completion before triggering another action.",
                status_code=409,
            )
        stages = adapter.prepare_retry_stage(slug=slug, stage=stage)
        job_id = runner.enqueue(
            slug=slug,
            action=f"retry_stage_{stage}",
            stages=stages,
            worker_fn=lambda emit: adapter.execute_render_pipeline(slug, stages, emit),
        )
        adapter.store.write_studio_meta(slug, {"activeJobId": job_id})
        episode = adapter.store.get_episode(slug)
        return {"episode": episode.model_dump(), "jobId": job_id}

    @router.get("/episodes/{slug}/jobs/{jobId}/events")
    async def stream_job_events(
        slug: str,
        jobId: str,
        _: AuthSessionState | None = Depends(require_session),
    ) -> StreamingResponse:
        resolve_safe_episode_path(adapter.store.episodes_root, slug)
        job = runner.get_job(jobId)
        if job.episodeSlug != slug:
            raise AppError("JOB_NOT_FOUND", f"Job '{jobId}' not found for '{slug}'.", 404)
        return StreamingResponse(
            runner.stream_events(jobId),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get("/episodes/{slug}/events")
    async def stream_latest_episode_events(
        slug: str,
        _: AuthSessionState | None = Depends(require_session),
    ) -> StreamingResponse:
        ep = adapter.store.get_episode(slug)
        if not ep.activeJobId:
            raise AppError("JOB_NOT_FOUND", f"No active job for episode '{slug}'.", 404)
        return StreamingResponse(
            runner.stream_events(ep.activeJobId),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get("/episodes/{slug}/jobs/{jobId}")
    def get_job_status(
        slug: str,
        jobId: str,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        resolve_safe_episode_path(adapter.store.episodes_root, slug)
        job = runner.get_job(jobId)
        if job.episodeSlug != slug:
            raise AppError("JOB_NOT_FOUND", f"Job '{jobId}' not found for '{slug}'.", 404)
        return job.model_dump()

    # ------------------------------------------------------------------
    # Gate 3: CloudArchive Upload & Media Streaming
    # ------------------------------------------------------------------

    @router.post("/episodes/{slug}/gates/3/approve")
    @router.post("/episodes/{slug}/gates/3/upload")
    def approve_gate_3(
        slug: str,
        payload: GateApproveNotesRequest | None = None,
        _: AuthSessionState | None = Depends(require_session),
    ) -> dict[str, Any]:
        runner.lock_manager.acquire(slug, "gate_3_upload")
        try:
            notes = payload.notes if payload else None
            episode, dest = adapter.approve_gate_3_and_upload(slug=slug, notes=notes)
            return {"episode": episode.model_dump(), "gdriveDestination": dest}
        finally:
            runner.lock_manager.release(slug)

    @router.get("/episodes/{slug}/media/{assetType}")
    def get_media(
        slug: str,
        assetType: str,
        request: Request,
        _: AuthSessionState | None = Depends(require_session),
    ) -> Response:
        ep_dir = resolve_safe_episode_path(adapter.store.episodes_root, slug)
        if assetType == "thumbnail":
            thumb = ep_dir / "papercut" / "out" / "opening-frame.png"
            if not thumb.exists():
                raise AppError("ASSET_NOT_FOUND", "Thumbnail not found.", 404)
            return FileResponse(thumb, media_type="image/png")
        if assetType != "video":
            raise AppError("VALIDATION_ERROR", f"Unsupported assetType '{assetType}'.", 400)

        video = ep_dir / "papercut" / "out" / f"episode-{slug}.mp4"
        if not video.exists():
            raise AppError("ASSET_NOT_FOUND", "VideoAsset not found.", 404)

        file_size = video.stat().st_size
        range_header = request.headers.get("Range")
        if not range_header:
            return FileResponse(video, media_type="video/mp4")

        match = _RANGE_RE.match(range_header.strip())
        if not match:
            return FileResponse(video, media_type="video/mp4")
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else file_size - 1
        end = min(end, file_size - 1)
        if start > end or start >= file_size:
            raise AppError("VALIDATION_ERROR", "Requested range not satisfiable.", 416)
        length = end - start + 1
        with video.open("rb") as fh:
            fh.seek(start)
            chunk = fh.read(length)
        return Response(
            content=chunk,
            status_code=206,
            media_type="video/mp4",
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length),
            },
        )

    return router
