"""Per-Episode concurrency lock manager and async BackgroundJobRunner with SSE streaming."""

from __future__ import annotations

import asyncio
import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, AsyncIterator, Callable

from studio_api.errors import AppError
from studio_api.logger import get_logger
from studio_api.schemas import JobStageState, JobStatus, StageRunStatus

_log = get_logger("job_runner")

STAGE_LABELS: dict[int, str] = {
    2: "FactResearch",
    3: "HookVariant Generation",
    5: "NarrationScript",
    7: "Storyboard",
    8: "Visual Directing",
    9: "Audio Production",
    10: "Animation Render",
    11: "4D QualityAudit",
}


class EpisodeLockManager:
    """In-process per-Episode execution lock preventing concurrent stage/gate mutations."""

    # shortcut: in-process lock table; upgrade to Redis/file-flock for multi-worker deployment
    def __init__(self) -> None:
        self._guard = threading.Lock()
        self._active: dict[str, str] = {}

    def acquire(self, slug: str, action: str) -> None:
        with self._guard:
            if slug in self._active:
                raise AppError(
                    code="EPISODE_LOCKED",
                    message=(
                        "Episode is currently executing a stage; wait for completion before "
                        "triggering another action."
                    ),
                    status_code=409,
                    details={"slug": slug, "activeAction": self._active[slug]},
                )
            self._active[slug] = action

    def release(self, slug: str) -> None:
        with self._guard:
            self._active.pop(slug, None)

    def is_locked(self, slug: str) -> bool:
        with self._guard:
            return slug in self._active

    def active_action(self, slug: str) -> str | None:
        with self._guard:
            return self._active.get(slug)


class _JobRecord:
    def __init__(self, job_id: str, slug: str, stages: list[int]) -> None:
        self.status = JobStatus(
            jobId=job_id,
            episodeSlug=slug,
            status="RUNNING",
            currentStage=stages[0] if stages else 0,
            stageStates=[
                JobStageState(stage=s, name=STAGE_LABELS.get(s, f"Stage {s}"), status="PENDING")
                for s in stages
            ],
            logs=[],
        )
        self.events: list[dict[str, Any]] = []
        self.subscribers: list[tuple[asyncio.AbstractEventLoop, asyncio.Queue[dict[str, Any] | None]]] = []
        self.done = False
        self.lock = threading.Lock()


class BackgroundJobRunner:
    """Executes blocking production stages in a bounded thread pool and streams SSE events."""

    def __init__(
        self,
        lock_manager: EpisodeLockManager,
        max_workers: int = 2,
    ) -> None:
        self.lock_manager = lock_manager
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="studio-job")
        self._jobs: dict[str, _JobRecord] = {}
        self._jobs_guard = threading.Lock()

    @property
    def active_job_count(self) -> int:
        with self._jobs_guard:
            return sum(1 for rec in self._jobs.values() if not rec.done)

    def get_job(self, job_id: str) -> JobStatus:
        with self._jobs_guard:
            rec = self._jobs.get(job_id)
        if rec is None:
            raise AppError(
                code="JOB_NOT_FOUND",
                message=f"Job '{job_id}' was not found.",
                status_code=404,
                details={"jobId": job_id},
            )
        with rec.lock:
            return rec.status.model_copy(deep=True)

    def _publish(self, rec: _JobRecord, event: dict[str, Any]) -> None:
        with rec.lock:
            rec.events.append(event)
            subs = list(rec.subscribers)
        for loop, queue in subs:
            if not loop.is_closed():
                loop.call_soon_threadsafe(queue.put_nowait, event)

    def _finish_subscribers(self, rec: _JobRecord) -> None:
        with rec.lock:
            rec.done = True
            subs = list(rec.subscribers)
        for loop, queue in subs:
            if not loop.is_closed():
                loop.call_soon_threadsafe(queue.put_nowait, None)

    def enqueue(
        self,
        slug: str,
        action: str,
        stages: list[int],
        worker_fn: Callable[[Callable[[int, StageRunStatus, str], None]], dict[str, Any]],
    ) -> str:
        """Acquire Episode lock and schedule worker_fn asynchronously."""
        self.lock_manager.acquire(slug, action)
        job_id = f"job-{uuid.uuid4().hex[:10]}"
        rec = _JobRecord(job_id=job_id, slug=slug, stages=stages)
        with self._jobs_guard:
            self._jobs[job_id] = rec

        def emit_stage(stage: int, status: StageRunStatus, log_line: str) -> None:
            with rec.lock:
                rec.status.currentStage = stage
                for item in rec.status.stageStates:
                    if item.stage == stage:
                        item.status = status
                if log_line:
                    rec.status.logs.append(log_line)
                    if len(rec.status.logs) > 200:
                        rec.status.logs = rec.status.logs[-200:]
            self._publish(
                rec,
                {
                    "type": "stage",
                    "jobId": job_id,
                    "episodeSlug": slug,
                    "stage": stage,
                    "stageName": STAGE_LABELS.get(stage, f"Stage {stage}"),
                    "status": status,
                    "logLine": log_line,
                },
            )

        def run_wrapper() -> None:
            try:
                result = worker_fn(emit_stage)
                final_status = str(result.get("status", "COMPLETED"))
                with rec.lock:
                    rec.status.status = final_status  # type: ignore[assignment]
                    rec.status.gate = result.get("gate")
                    rec.status.measuredDurationSec = result.get("measuredDurationSec")
                    rec.status.error = result.get("error")
                self._publish(
                    rec,
                    {
                        "type": "terminal",
                        "jobId": job_id,
                        "episodeSlug": slug,
                        "status": final_status,
                        "gate": result.get("gate"),
                        "measuredDurationSec": result.get("measuredDurationSec"),
                        "error": result.get("error"),
                    },
                )
            except Exception as exc:
                _log.error("job.failed", "Background job failed", exc=exc, episodeSlug=slug, jobId=job_id)
                with rec.lock:
                    rec.status.status = "FAILED"
                    rec.status.error = str(exc)
                    for item in rec.status.stageStates:
                        if item.status == "RUNNING":
                            item.status = "FAILED"
                    rec.status.logs.append(f"ERROR: {exc}")
                self._publish(
                    rec,
                    {
                        "type": "terminal",
                        "jobId": job_id,
                        "episodeSlug": slug,
                        "status": "FAILED",
                        "stage": rec.status.currentStage,
                        "error": str(exc),
                    },
                )
            finally:
                self._finish_subscribers(rec)
                self.lock_manager.release(slug)

        self._executor.submit(run_wrapper)
        return job_id

    async def stream_events(self, job_id: str) -> AsyncIterator[str]:
        """Yield SSE-formatted event strings for a jobId until completion."""
        with self._jobs_guard:
            rec = self._jobs.get(job_id)
        if rec is None:
            raise AppError(
                code="JOB_NOT_FOUND",
                message=f"Job '{job_id}' was not found.",
                status_code=404,
            )

        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()

        with rec.lock:
            backlog = list(rec.events)
            already_done = rec.done
            if not already_done:
                rec.subscribers.append((loop, queue))

        try:
            for ev in backlog:
                yield f"event: {ev.get('type', 'message')}\ndata: {json.dumps(ev)}\n\n"
            if already_done:
                return
            while True:
                ev = await queue.get()
                if ev is None:
                    break
                yield f"event: {ev.get('type', 'message')}\ndata: {json.dumps(ev)}\n\n"
        finally:
            with rec.lock:
                rec.subscribers = [(l, q) for (l, q) in rec.subscribers if q is not queue]
