"""Filesystem EpisodeStore with path-traversal guard, sidecar meta, and baseline protection."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from studio_api.errors import AppError
from studio_api.logger import get_logger
from studio_api.pacing import analyze_narration_beats
from studio_api.schemas import (
    AgeCategory,
    EpisodeDetail,
    EpisodeSummary,
    GateStates,
    HookVariant,
    Niche,
    PublishingKit,
    QualityAuditDimensions,
    QualityAuditReport,
    ScriptBeat,
    WorkflowMode,
)

_log = get_logger("episode_store")

SLUG_RE = re.compile(r"^[a-z0-9-]+$")
PROTECTED_SLUGS: frozenset[str] = frozenset({"episode-01-v4"})

_VALID_NICHES: frozenset[str] = frozenset({"science", "history", "geography", "technology", "mystery"})
_VALID_AGES: frozenset[str] = frozenset({"Remaja 13-17", "Dewasa Muda 18-35", "Umum"})
_VALID_MODES: frozenset[str] = frozenset({"TopicResearchMode", "DirectTopicMode"})


def resolve_safe_episode_path(episodes_root: Path, slug: str) -> Path:
    """Validate slug format and resolve episode directory safely inside episodes_root."""
    if not slug or ".." in slug or "/" in slug or "\\" in slug or not SLUG_RE.match(slug):
        raise AppError(
            code="VALIDATION_ERROR",
            message=f"Invalid episode slug '{slug}'. Must match ^[a-z0-9-]+$.",
            status_code=400,
            details={"slug": slug},
        )
    root_resolved = episodes_root.resolve()
    target = (root_resolved / slug).resolve()
    if target.parent != root_resolved:
        raise AppError(
            code="VALIDATION_ERROR",
            message="Path traversal rejected.",
            status_code=400,
        )
    return target


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


class EpisodeStore:
    """Reads and persists Episode artifacts and studio_meta.json sidecars."""

    def __init__(
        self,
        episodes_root: Path,
        protected_slugs: frozenset[str] = PROTECTED_SLUGS,
    ) -> None:
        self.episodes_root = episodes_root
        self.protected_slugs = protected_slugs
        self.episodes_root.mkdir(parents=True, exist_ok=True)

    def is_baseline_protected(self, slug: str) -> bool:
        return slug in self.protected_slugs

    def ensure_mutable(self, slug: str) -> None:
        resolve_safe_episode_path(self.episodes_root, slug)
        if self.is_baseline_protected(slug):
            raise AppError(
                code="BASELINE_PROTECTED",
                message=f"Episode '{slug}' is a protected baseline and cannot be modified or archived.",
                status_code=409,
                details={"slug": slug},
            )

    def read_studio_meta(self, ep_dir: Path) -> dict[str, Any]:
        meta_path = ep_dir / "content_factory" / "studio_meta.json"
        raw = _read_json(meta_path)
        if isinstance(raw, dict):
            return raw
        return {}

    def write_studio_meta(self, slug: str, updates: dict[str, Any]) -> dict[str, Any]:
        self.ensure_mutable(slug)
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        meta_path = ep_dir / "content_factory" / "studio_meta.json"
        current = self.read_studio_meta(ep_dir)
        current.update(updates)
        _write_json(meta_path, current)
        return current

    def _normalize_niche(self, value: Any) -> Niche:
        val = str(value or "science").lower()
        return val if val in _VALID_NICHES else "science"  # type: ignore[return-value]

    def _normalize_age(self, value: Any) -> AgeCategory:
        val = str(value or "Umum")
        return val if val in _VALID_AGES else "Umum"  # type: ignore[return-value]

    def _normalize_mode(self, value: Any) -> WorkflowMode:
        val = str(value or "DirectTopicMode")
        return val if val in _VALID_MODES else "DirectTopicMode"  # type: ignore[return-value]

    def _build_summary(self, slug: str, ep_dir: Path) -> EpisodeSummary | None:
        state_path = ep_dir / "content_factory" / "workflow_state.json"
        state = _read_json(state_path)
        if not isinstance(state, dict):
            return None
        meta = self.read_studio_meta(ep_dir)
        title = str(meta.get("title") or slug.replace("-", " ").title())
        return EpisodeSummary(
            episodeSlug=slug,
            title=title,
            niche=self._normalize_niche(state.get("niche")),
            ageCategory=self._normalize_age(meta.get("ageCategory")),
            workflowMode=self._normalize_mode(meta.get("workflowMode")),
            currentStage=int(state.get("current_stage", 1)),
            status=str(state.get("status", "INITIALIZED")),
            isArchived=bool(meta.get("isArchived", False)),
            isBaselineProtected=self.is_baseline_protected(slug),
            activeJobId=meta.get("activeJobId"),
            lastUpdated=str(state.get("last_updated") or _utc_now_iso()),
        )

    def list_episodes(self, include_archived: bool = False) -> list[EpisodeSummary]:
        items: list[EpisodeSummary] = []
        if not self.episodes_root.exists():
            return items
        for child in sorted(self.episodes_root.iterdir()):
            if not child.is_dir() or not SLUG_RE.match(child.name):
                continue
            summary = self._build_summary(child.name, child)
            if summary is None:
                continue
            if not include_archived and summary.isArchived:
                continue
            items.append(summary)
        items.sort(key=lambda item: item.lastUpdated, reverse=True)
        return items

    def get_episode(self, slug: str) -> EpisodeDetail:
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        state_path = ep_dir / "content_factory" / "workflow_state.json"
        state = _read_json(state_path)
        if not isinstance(state, dict):
            raise AppError(
                code="EPISODE_NOT_FOUND",
                message=f"Episode '{slug}' was not found.",
                status_code=404,
                details={"slug": slug},
            )
        summary = self._build_summary(slug, ep_dir)
        assert summary is not None
        meta = self.read_studio_meta(ep_dir)
        gates_raw = state.get("approval_gates", {})
        g1 = gates_raw.get("gate_1_topic_hook", {})
        g2 = gates_raw.get("gate_2_script", {})
        g3 = gates_raw.get("gate_3_final_video", {})

        gates = GateStates(
            gate1=str(g1.get("status", "PENDING")),  # type: ignore[arg-type]
            gate2=str(g2.get("status", "PENDING")),  # type: ignore[arg-type]
            gate3=str(g3.get("status", "PENDING")),  # type: ignore[arg-type]
        )

        fact_summary = self._load_fact_summary(ep_dir)
        hook_variants = self._load_hook_variants(ep_dir)
        script_state = self._load_script_state(ep_dir, meta)
        qa_report = self._load_quality_audit(ep_dir)
        pub_kit = self._load_publishing_kit(ep_dir)

        video_file = ep_dir / "papercut" / "out" / f"episode-{slug}.mp4"
        thumb_file = ep_dir / "papercut" / "out" / "opening-frame.png"
        video_url = f"/api/episodes/{slug}/media/video" if video_file.exists() else None
        thumb_url = f"/api/episodes/{slug}/media/thumbnail" if thumb_file.exists() else None

        return EpisodeDetail(
            **summary.model_dump(),
            factResearchSummary=fact_summary,
            hookVariants=hook_variants,
            selectedHookId=g1.get("selected_hook_id"),
            narrationScript=script_state,
            qualityAudit=qa_report,
            publishingKit=pub_kit,
            videoUrl=video_url,
            thumbnailUrl=thumb_url,
            gdriveDestination=meta.get("gdriveDestination"),
            gates=gates,
            nonWhatIfNotice=meta.get("nonWhatIfNotice"),
        )

    def archive_episode(self, slug: str, confirmed: bool = True) -> EpisodeSummary:
        if not confirmed:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Archival requires explicit confirmation.",
                status_code=400,
            )
        self.ensure_mutable(slug)
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        if not (ep_dir / "content_factory" / "workflow_state.json").exists():
            raise AppError(
                code="EPISODE_NOT_FOUND",
                message=f"Episode '{slug}' was not found.",
                status_code=404,
            )
        self.write_studio_meta(slug, {"isArchived": True, "archivedAt": _utc_now_iso()})
        summary = self._build_summary(slug, ep_dir)
        assert summary is not None
        return summary

    def _load_fact_summary(self, ep_dir: Path) -> list[str]:
        dossier = _read_json(ep_dir / "research" / "dossier.json")
        if isinstance(dossier, dict):
            summary = dossier.get("summary")
            if isinstance(summary, list):
                return [str(x) for x in summary]
            layer1 = dossier.get("layer1_baseline")
            layer2 = dossier.get("layer2_domino")
            items: list[str] = []
            if layer1:
                items.append(str(layer1))
            if layer2:
                items.append(str(layer2))
            if items:
                return items
        return []

    def _load_hook_variants(self, ep_dir: Path) -> list[HookVariant]:
        raw = _read_json(ep_dir / "research" / "hook_matrix.json")
        if not isinstance(raw, dict):
            return []
        hooks = raw.get("hooks", [])
        if not isinstance(hooks, list):
            return []
        result: list[HookVariant] = []
        for idx, item in enumerate(hooks, start=1):
            if not isinstance(item, dict):
                continue
            result.append(
                HookVariant(
                    hookId=str(item.get("hookId") or item.get("id") or f"hook-{idx}"),
                    openingLine=str(item.get("openingLine") or item.get("hook") or ""),
                    frame0CoverConcept=str(
                        item.get("frame0CoverConcept") or item.get("visual_cover") or "Papercraft Cat Scientist Frame 0"
                    ),
                    hookScore=int(item.get("hookScore") or item.get("score") or 85),
                )
            )
        return result

    def _load_script_state(self, ep_dir: Path, meta: dict[str, Any]) -> Any:
        raw = _read_json(ep_dir / "narration" / "script.json")
        if not isinstance(raw, dict):
            return None
        beats_raw = raw.get("beats", [])
        beats: list[ScriptBeat] = []
        if isinstance(beats_raw, list) and len(beats_raw) == 6:
            for idx, item in enumerate(beats_raw, start=1):
                if isinstance(item, dict):
                    beats.append(
                        ScriptBeat(
                            id=str(item.get("id") or f"beat-{idx}"),
                            beatNumber=int(item.get("beatNumber") or idx),  # type: ignore[arg-type]
                            beatLabel=str(item.get("beatLabel") or f"Beat {idx}"),
                            text=str(item.get("text") or ""),
                        )
                    )
        if not beats:
            return None
        measured = meta.get("measuredAudioDurationSec")
        measured_float = float(measured) if measured is not None else None
        return analyze_narration_beats(beats, measured_audio_duration_sec=measured_float)

    def _load_quality_audit(self, ep_dir: Path) -> QualityAuditReport | None:
        raw = _read_json(ep_dir / "qa" / "qa_report.json")
        if not isinstance(raw, dict):
            return None
        dims = raw.get("dimensions", {})
        return QualityAuditReport(
            overallStatus=str(raw.get("overallStatus", "PENDING")),  # type: ignore[arg-type]
            dimensions=QualityAuditDimensions(
                visual=bool(dims.get("visual", False)),
                audio=bool(dims.get("audio", False)),
                technical=bool(dims.get("technical", False)),
                factual=bool(dims.get("factual", False)),
            ),
            diagnostics=[str(d) for d in raw.get("diagnostics", [])],
        )

    def _load_publishing_kit(self, ep_dir: Path) -> PublishingKit | None:
        raw = _read_json(ep_dir / "publishing" / "publishing-kit.json")
        if not isinstance(raw, dict):
            return None
        try:
            return PublishingKit(**raw)
        except Exception as exc:
            _log.warn(
                "store.publishing_kit_invalid",
                "Failed to parse publishing-kit.json",
                path=str(ep_dir / "publishing" / "publishing-kit.json"),
                error=str(exc),
            )
            return None
