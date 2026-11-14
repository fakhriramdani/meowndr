"""PipelinePort protocol and LiveLibraryAdapter bridging studio_api to library/."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Protocol, runtime_checkable

from studio_api.episode_store import EpisodeStore, resolve_safe_episode_path
from studio_api.errors import AppError
from studio_api.logger import get_logger
from studio_api.pacing import analyze_narration_beats
from studio_api.schemas import (
    AgeCategory,
    CreateEpisodeRequest,
    EpisodeDetail,
    NarrationScriptState,
    Niche,
    ScriptBeat,
    StageRunStatus,
    TrendOpportunity,
)

_log = get_logger("pipeline_adapter")

StageEmitter = Callable[[int, StageRunStatus, str], None]

_WHAT_IF_PREFIX_RE = re.compile(r"(bagaimana\s+jika|what\s+if|seandainya)", re.IGNORECASE)
_SLUG_SANITIZE_RE = re.compile(r"[^a-z0-9]+")


def slugify_topic(niche: str, topic: str) -> str:
    """Create a safe ^[a-z0-9-]+$ episode slug from niche and topic."""
    base = _SLUG_SANITIZE_RE.sub("-", topic.lower()).strip("-")[:36].strip("-")
    suffix = uuid.uuid4().hex[:6]
    return f"{niche.lower()}-{base}-{suffix}" if base else f"{niche.lower()}-ep-{suffix}"


def is_what_if_phrasing(topic: str) -> bool:
    return bool(_WHAT_IF_PREFIX_RE.search(topic))


@runtime_checkable
class PipelinePort(Protocol):
    """Public seam between FastAPI control plane and production engine."""

    store: EpisodeStore

    def discover_trends(self, niche: Niche, age_category: AgeCategory) -> list[TrendOpportunity]: ...

    def create_episode(self, req: CreateEpisodeRequest) -> tuple[str, list[int]]: ...

    def run_fact_and_hooks(self, slug: str, emit: StageEmitter) -> dict[str, Any]: ...

    def approve_gate_1(self, slug: str, hook_id: str, notes: str | None = None) -> list[int]: ...

    def run_script_generation(self, slug: str, emit: StageEmitter) -> dict[str, Any]: ...

    def save_and_validate_script(self, slug: str, beats: list[ScriptBeat]) -> NarrationScriptState: ...

    def condense_script(self, slug: str) -> NarrationScriptState: ...

    def prepare_gate_2_approval(self, slug: str, notes: str | None = None) -> list[int]: ...

    def prepare_retry_stage(self, slug: str, stage: int) -> list[int]: ...

    def execute_render_pipeline(
        self, slug: str, stages: list[int], emit: StageEmitter
    ) -> dict[str, Any]: ...

    def approve_gate_3_and_upload(
        self, slug: str, notes: str | None = None
    ) -> tuple[EpisodeDetail, str]: ...


class LiveLibraryAdapter:
    """Production adapter delegating to library/content_factory & library/tools."""

    def __init__(self, repo_root: Path, episodes_root: Path) -> None:
        self.repo_root = repo_root
        self.episodes_root = episodes_root
        self.store = EpisodeStore(episodes_root=episodes_root)
        repo_str = str(self.repo_root)
        if repo_str not in sys.path:
            sys.path.insert(0, repo_str)

    def _engine(self, slug: str, niche: str = "science", title: str = "") -> Any:
        from library.content_factory.workflow_engine import WorkflowEngine

        return WorkflowEngine(
            episode_slug=slug,
            niche=niche,
            title=title,
            base_dir=str(self.episodes_root),
        )

    def discover_trends(self, niche: Niche, age_category: AgeCategory) -> list[TrendOpportunity]:
        from library.content_factory.trend_intelligence import discover_what_if_trends

        raw_items = discover_what_if_trends(niche=niche, count=5)
        opportunities: list[TrendOpportunity] = []
        for idx, item in enumerate(raw_items[:5], start=1):
            premise = str(item.get("premise") or item.get("title") or f"Bagaimana jika {niche} berubah?")
            cascade = list(item.get("temporalCascade") or item.get("beats") or [])
            while len(cascade) < 6:
                cascade.append(f"Dampak lanjutan tahap {len(cascade) + 1} pada {niche}.")
            opportunities.append(
                TrendOpportunity(
                    id=str(item.get("id") or f"trend-{niche}-{idx}"),
                    premise=premise,
                    niche=niche,
                    ageCategory=age_category,
                    opportunityScore=max(0, min(100, int(item.get("opportunityScore") or (96 - idx * 3)))),
                    temporalCascade=cascade[:6],
                )
            )
        opportunities.sort(key=lambda o: o.opportunityScore, reverse=True)
        return opportunities

    def create_episode(self, req: CreateEpisodeRequest) -> tuple[str, list[int]]:
        niche = str(req.niche).lower()
        topic = (req.topic or req.premise or "").strip()
        slug = slugify_topic(niche, topic)
        non_what_if_notice = (
            None
            if is_what_if_phrasing(topic)
            else "Topic will be framed as a What-If Point of Divergence with a 6-beat TemporalCascade."
        )
        self._engine(slug=slug, niche=niche, title=topic)
        self.store.write_studio_meta(
            slug,
            {
                "title": topic,
                "ageCategory": req.ageCategory,
                "workflowMode": req.workflowMode,
                "isArchived": False,
                "nonWhatIfNotice": non_what_if_notice,
                "temporalCascade": req.temporalCascade or [],
            },
        )
        return slug, [2, 3]

    def run_fact_and_hooks(self, slug: str, emit: StageEmitter) -> dict[str, Any]:
        ep = self.store.get_episode(slug)
        engine = self._engine(slug=slug, niche=ep.niche, title=ep.title)
        emit(2, "RUNNING", f"Running two-layer FactResearch for {slug}...")
        engine.run_stage_2_fact_research()
        emit(2, "COMPLETED", "FactResearch verified.")
        emit(3, "RUNNING", "Generating 5 scored HookVariant candidates...")
        engine.run_stage_3_hooks()
        emit(3, "COMPLETED", "Generated 5 HookVariant candidates. Halting at Gate 1.")
        return {"status": "COMPLETED", "gate": 1}

    def approve_gate_1(self, slug: str, hook_id: str, notes: str | None = None) -> list[int]:
        self.store.ensure_mutable(slug)
        ep = self.store.get_episode(slug)
        if not hook_id.strip():
            raise AppError(
                code="VALIDATION_ERROR",
                message="Select 1 of the 5 HookVariant candidates before approving Gate 1.",
                status_code=400,
            )
        valid_ids = {h.hookId for h in ep.hookVariants}
        if valid_ids and hook_id not in valid_ids:
            raise AppError(
                code="VALIDATION_ERROR",
                message=f"HookVariant '{hook_id}' not found for episode '{slug}'.",
                status_code=400,
            )
        engine = self._engine(slug=slug, niche=ep.niche, title=ep.title)
        engine.approve_gate_1(selected_hook_id=hook_id, notes=notes or "Approved via Studio UI")
        return [5]

    def run_script_generation(self, slug: str, emit: StageEmitter) -> dict[str, Any]:
        ep = self.store.get_episode(slug)
        engine = self._engine(slug=slug, niche=ep.niche, title=ep.title)
        emit(5, "RUNNING", "Generating 6-beat What-If NarrationScript...")
        engine.run_stage_5_script()
        emit(5, "COMPLETED", "NarrationScript ready for review at Gate 2.")
        return {"status": "COMPLETED", "gate": 2}

    def save_and_validate_script(self, slug: str, beats: list[ScriptBeat]) -> NarrationScriptState:
        self.store.ensure_mutable(slug)
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        script_path = ep_dir / "narration" / "script.json"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        existing = json.loads(script_path.read_text(encoding="utf-8")) if script_path.exists() else {}
        existing["beats"] = [b.model_dump() for b in beats]
        existing["spoken_text"] = " ".join(b.text.strip() for b in beats)
        script_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
        report = analyze_narration_beats(beats)
        if not report.isCompliant:
            code = "SPOKEN_DIGITS_FORBIDDEN" if report.hasNumericDigits else "PACING_CEILING_EXCEEDED"
            raise AppError(
                code=code,
                message=" ".join(report.violations),
                status_code=422,
                details=report.model_dump(),
            )
        return report

    def condense_script(self, slug: str) -> NarrationScriptState:
        self.store.ensure_mutable(slug)
        ep = self.store.get_episode(slug)
        if ep.narrationScript is None:
            raise AppError("VALIDATION_ERROR", "No script found to condense.", 400)
        condensed_beats: list[ScriptBeat] = []
        for b in ep.narrationScript.beats:
            words = b.text.split()
            trimmed = " ".join(words[:16])
            condensed_beats.append(
                ScriptBeat(id=b.id, beatNumber=b.beatNumber, beatLabel=b.beatLabel, text=trimmed)
            )
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        script_path = ep_dir / "narration" / "script.json"
        script_path.write_text(
            json.dumps({"beats": [b.model_dump() for b in condensed_beats]}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return analyze_narration_beats(condensed_beats)

    def prepare_gate_2_approval(self, slug: str, notes: str | None = None) -> list[int]:
        self.store.ensure_mutable(slug)
        ep = self.store.get_episode(slug)
        if ep.gates.gate1 != "APPROVED":
            raise AppError(
                code="GATE_BYPASS_BLOCKED",
                message="Gate 1 (Topic & Hook) must be approved before advancing to Script.",
                status_code=409,
            )
        if ep.narrationScript is None or not ep.narrationScript.isCompliant:
            violations = ep.narrationScript.violations if ep.narrationScript else ["Script missing."]
            code = (
                "SPOKEN_DIGITS_FORBIDDEN"
                if ep.narrationScript and ep.narrationScript.hasNumericDigits
                else "PACING_CEILING_EXCEEDED"
            )
            raise AppError(code=code, message=" ".join(violations), status_code=422)
        engine = self._engine(slug=slug, niche=ep.niche, title=ep.title)
        engine.approve_gate_2(word_count=ep.narrationScript.wordCount, notes=notes or "Approved via Studio UI")
        return [7, 8, 9, 10, 11]

    def prepare_retry_stage(self, slug: str, stage: int) -> list[int]:
        self.store.ensure_mutable(slug)
        if stage < 7 or stage > 11:
            raise AppError("VALIDATION_ERROR", f"Stage {stage} cannot be retried via render pipeline.", 400)
        return list(range(stage, 12))

    def execute_render_pipeline(
        self, slug: str, stages: list[int], emit: StageEmitter
    ) -> dict[str, Any]:
        pipeline_cli = self.repo_root / "library" / "tools" / "production_pipeline.py"
        for st in stages:
            emit(st, "RUNNING", f"Executing Stage {st}...")
            if st == 9:
                proc = subprocess.run(
                    [sys.executable, str(pipeline_cli), "bgm", slug],
                    cwd=str(self.repo_root),
                    capture_output=True,
                    text=True,
                )
                if proc.returncode != 0:
                    raise RuntimeError(proc.stderr or proc.stdout or f"Stage {st} failed")
            emit(st, "COMPLETED", f"Stage {st} completed.")
        return {"status": "COMPLETED", "gate": 3}

    def approve_gate_3_and_upload(
        self, slug: str, notes: str | None = None
    ) -> tuple[EpisodeDetail, str]:
        self.store.ensure_mutable(slug)
        ep = self.store.get_episode(slug)
        if ep.gates.gate3 == "APPROVED" and ep.gdriveDestination:
            raise AppError(
                code="ALREADY_ARCHIVED",
                message=f"Episode '{slug}' is already archived in CloudArchive.",
                status_code=409,
            )
        if ep.qualityAudit is None or ep.qualityAudit.overallStatus != "PASS":
            raise AppError(
                code="AUDIT_NOT_PASSED",
                message="4D QualityAudit must PASS before uploading to CloudArchive.",
                status_code=409,
            )
        from library.content_factory.gdrive_uploader import upload_episode_to_gdrive

        ok, details, errors = upload_episode_to_gdrive(episode_slug=slug)
        if not ok:
            raise AppError(
                code="CLOUD_ARCHIVE_FAILED",
                message="; ".join(errors) or "CloudArchive upload failed.",
                status_code=502,
            )
        dest = str(details.get("destination") or f"gdrive-new:Antigravity/Videos/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_{slug}")
        self.store.write_studio_meta(slug, {"gdriveDestination": dest})
        engine = self._engine(slug=slug, niche=ep.niche, title=ep.title)
        engine.approve_gate_3(notes=notes or "Approved & archived via Studio UI")
        return self.store.get_episode(slug), dest
