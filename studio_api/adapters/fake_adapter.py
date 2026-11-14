"""Deterministic InMemoryFakeAdapter implementing PipelinePort for TDD and headless QA."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from studio_api.adapters.pipeline_adapter import (
    StageEmitter,
    is_what_if_phrasing,
    slugify_topic,
)
from studio_api.episode_store import EpisodeStore, resolve_safe_episode_path
from studio_api.errors import AppError
from studio_api.pacing import analyze_narration_beats
from studio_api.schemas import (
    AgeCategory,
    CreateEpisodeRequest,
    EpisodeDetail,
    NarrationScriptState,
    Niche,
    ScriptBeat,
    TrendOpportunity,
)

# 118 Indonesian words, 0 numeric digits (~44.5s at 1.0x natural pace)
_DEFAULT_BEATS: list[dict[str, Any]] = [
    {
        "id": "beat-1",
        "beatNumber": 1,
        "beatLabel": "Beat 1 — Katalis & Titik Percabangan",
        "text": (
            "Bagaimana jika kadar oksigen di atmosfer bumi mendadak naik dua kali lipat "
            "hari ini dan mengubah seluruh ekosistem planet kita?"
        ),
    },
    {
        "id": "beat-2",
        "beatNumber": 2,
        "beatLabel": "Beat 2 — Guncangan Awal",
        "text": (
            "Pada detik pertama, tekanan udara melonjak drastis sehingga api menyala jauh "
            "lebih panas dan pembakaran hutan terjadi sangat cepat."
        ),
    },
    {
        "id": "beat-3",
        "beatNumber": 3,
        "beatLabel": "Beat 3 — Efek Domino Era Berikutnya",
        "text": (
            "Dalam beberapa generasi, serangga menyerap oksigen lebih banyak melalui sistem "
            "trakea mereka hingga tubuhnya membesar menjadi raksasa seperti zaman purba."
        ),
    },
    {
        "id": "beat-4",
        "beatNumber": 4,
        "beatLabel": "Beat 4 — Transformasi Dunia Masa Kini",
        "text": (
            "Peradaban manusia harus merancang kota tahan api karena percikan listrik kecil "
            "saja sanggup memicu kebakaran besar yang sulit dipadamkan."
        ),
    },
    {
        "id": "beat-5",
        "beatNumber": 5,
        "beatLabel": "Beat 5 — Realitas Ilmiah",
        "text": (
            "Di garis waktu nyata, fotosintesis tumbuhan dan pelapukan batuan menjaga "
            "keseimbangan oksigen atmosfer tetap aman pada kisaran dua puluh satu persen."
        ),
    },
    {
        "id": "beat-6",
        "beatNumber": 6,
        "beatLabel": "Beat 6 — Outro & Dilema",
        "text": (
            "Simpan video ini jika menarik, lalu tulis pendapatmu di komentar: berani "
            "hidup di bumi penuh serangga raksasa?"
        ),
    },
]

# 99 Indonesian words, 0 numeric digits (~37.4s at 1.0x natural pace)
_CONDENSED_BEATS: list[dict[str, Any]] = [
    {
        "id": "beat-1",
        "beatNumber": 1,
        "beatLabel": "Beat 1 — Katalis & Titik Percabangan",
        "text": "Bagaimana jika kadar oksigen di atmosfer bumi mendadak naik dua kali lipat hari ini juga?",
    },
    {
        "id": "beat-2",
        "beatNumber": 2,
        "beatLabel": "Beat 2 — Guncangan Awal",
        "text": (
            "Seketika tekanan udara melonjak tajam sehingga api menyala jauh lebih panas "
            "dan membakar hutan dengan sangat cepat di seluruh permukaan bumi."
        ),
    },
    {
        "id": "beat-3",
        "beatNumber": 3,
        "beatLabel": "Beat 3 — Efek Domino Era Berikutnya",
        "text": (
            "Dalam beberapa generasi ke depan, serangga menyerap oksigen berlimpah hingga ukuran "
            "tubuhnya tumbuh besar menjadi raksasa seperti zaman purba."
        ),
    },
    {
        "id": "beat-4",
        "beatNumber": 4,
        "beatLabel": "Beat 4 — Transformasi Dunia Masa Kini",
        "text": (
            "Kota modern wajib dirancang tahan api karena percikan listrik kecil saja sanggup memicu "
            "kebakaran besar yang sangat berbahaya."
        ),
    },
    {
        "id": "beat-5",
        "beatNumber": 5,
        "beatLabel": "Beat 5 — Realitas Ilmiah",
        "text": (
            "Faktanya, keseimbangan fotosintesis tumbuhan dan pelapukan batuan menjaga kadar "
            "oksigen bumi tetap stabil pada dua puluh satu persen."
        ),
    },
    {
        "id": "beat-6",
        "beatNumber": 6,
        "beatLabel": "Beat 6 — Outro & Dilema",
        "text": "Simpan dan bagikan video ini sekarang. Berani hidup di bumi penuh serangga raksasa?",
    },
]


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class InMemoryFakeAdapter:
    """Deterministic PipelinePort implementation with zero external API or rclone calls."""

    def __init__(
        self,
        episodes_root: Path,
        simulate_pacing_failure: bool = False,
        simulate_audit_failure: bool = False,
        simulate_upload_failure: bool = False,
        simulate_stage_failure_at: int | None = None,
        stage_delay_sec: float = 0.01,
    ) -> None:
        self.episodes_root = episodes_root
        self.store = EpisodeStore(episodes_root=episodes_root)
        self.simulate_pacing_failure = simulate_pacing_failure
        self.simulate_audit_failure = simulate_audit_failure
        self.simulate_upload_failure = simulate_upload_failure
        self.simulate_stage_failure_at = simulate_stage_failure_at
        self.stage_delay_sec = stage_delay_sec
        self.executed_stages: dict[str, list[int]] = {}
        self.upload_count: dict[str, int] = {}

    def discover_trends(self, niche: Niche, age_category: AgeCategory) -> list[TrendOpportunity]:
        scores = [95, 91, 87, 82, 76]
        premises = [
            f"Bagaimana jika hukum dasar {niche} berubah mendadak selama lima detik?",
            f"Bagaimana jika fenomena utama {niche} tidak pernah terjadi di bumi?",
            f"Bagaimana jika kapasitas {niche} manusia meningkat dua kali lipat?",
            f"Bagaimana jika titik balik sejarah {niche} tertunda satu abad?",
            f"Bagaimana jika anomali {niche} terjadi tepat di garis khatulistiwa?",
        ]
        items: list[TrendOpportunity] = []
        for idx, (score, premise) in enumerate(zip(scores, premises), start=1):
            items.append(
                TrendOpportunity(
                    id=f"trend-{niche}-{idx}",
                    premise=premise,
                    niche=niche,
                    ageCategory=age_category,
                    opportunityScore=score,
                    temporalCascade=[
                        f"Beat 1 (Katalis): {premise}",
                        "Beat 2 (Guncangan Awal): Reaksi fisik langsung pada detik pertama.",
                        "Beat 3 (Efek Domino): Perubahan ekosistem selama puluhan tahun.",
                        "Beat 4 (Masa Kini): Transformasi peradaban modern hari ini.",
                        "Beat 5 (Realitas): Prinsip sains dan sejarah nyata di garis waktu kita.",
                        "Beat 6 (Dilema): Pertanyaan debat untuk kolom komentar.",
                    ],
                )
            )
        return items

    def create_episode(self, req: CreateEpisodeRequest) -> tuple[str, list[int]]:
        niche = str(req.niche).lower()
        topic = (req.topic or req.premise or "").strip()
        slug = slugify_topic(niche, topic)
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        now = datetime.now(timezone.utc).isoformat()
        state = {
            "episode_id": slug,
            "niche": niche,
            "current_stage": 2,
            "status": "INITIALIZED",
            "completed_stages": [1] if req.workflowMode == "TopicResearchMode" else [],
            "approval_gates": {
                "gate_1_topic_hook": {
                    "status": "PENDING",
                    "approved_at": None,
                    "approved_by": None,
                    "selected_hook_id": None,
                    "notes": None,
                },
                "gate_2_script": {
                    "status": "PENDING",
                    "approved_at": None,
                    "approved_by": None,
                    "word_count": None,
                    "notes": None,
                },
                "gate_3_final_video": {
                    "status": "PENDING",
                    "approved_at": None,
                    "approved_by": None,
                    "render_path": None,
                    "notes": None,
                },
            },
            "artifacts": {},
            "last_updated": now,
        }
        _write_json(ep_dir / "content_factory" / "workflow_state.json", state)
        notice = (
            None
            if is_what_if_phrasing(topic)
            else "Topic will be framed as a What-If Point of Divergence with a 6-beat TemporalCascade."
        )
        self.store.write_studio_meta(
            slug,
            {
                "title": topic,
                "ageCategory": req.ageCategory,
                "workflowMode": req.workflowMode,
                "isArchived": False,
                "nonWhatIfNotice": notice,
            },
        )
        return slug, [2, 3]

    def run_fact_and_hooks(self, slug: str, emit: StageEmitter) -> dict[str, Any]:
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        emit(2, "RUNNING", f"Verifying 2-layer FactResearch for {slug}...")
        time.sleep(self.stage_delay_sec)
        _write_json(
            ep_dir / "research" / "dossier.json",
            {
                "summary": [
                    "Lapis 1 (Titik Awal): Parameter awal terverifikasi dari referensi ilmiah.",
                    "Lapis 2 (Efek Domino): Simulasi dampak jangka menengah & modern konsisten.",
                ]
            },
        )
        emit(2, "COMPLETED", "FactResearch verified.")

        emit(3, "RUNNING", "Generating 5 HookVariant candidates...")
        time.sleep(self.stage_delay_sec)
        hooks = [
            {
                "hookId": f"hook-{i}",
                "openingLine": f"Bagaimana jika skenario ke-{i} ini terjadi dalam lima detik?",
                "frame0CoverConcept": f"Cat Scientist terkejut melihat eksperimen ke-{i}",
                "hookScore": 96 - i * 3,
            }
            for i in range(1, 6)
        ]
        _write_json(ep_dir / "research" / "hook_matrix.json", {"hooks": hooks})

        state_path = ep_dir / "content_factory" / "workflow_state.json"
        state = _read_json(state_path)
        state["current_stage"] = 4
        state["status"] = "PENDING_USER_APPROVAL"
        state["completed_stages"] = sorted(set(state["completed_stages"] + [2, 3]))
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        _write_json(state_path, state)

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
                message=f"HookVariant '{hook_id}' is not valid for episode '{slug}'.",
                status_code=400,
            )

        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        state_path = ep_dir / "content_factory" / "workflow_state.json"
        state = _read_json(state_path)
        state["approval_gates"]["gate_1_topic_hook"] = {
            "status": "APPROVED",
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "approved_by": "user",
            "selected_hook_id": hook_id,
            "notes": notes,
        }
        state["current_stage"] = 5
        state["status"] = "IN_PROGRESS"
        state["completed_stages"] = sorted(set(state["completed_stages"] + [4]))
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        _write_json(state_path, state)
        return [5]

    def run_script_generation(self, slug: str, emit: StageEmitter) -> dict[str, Any]:
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        emit(5, "RUNNING", "Writing 6-beat What-If NarrationScript...")
        time.sleep(self.stage_delay_sec)
        _write_json(ep_dir / "narration" / "script.json", {"beats": _DEFAULT_BEATS})

        state_path = ep_dir / "content_factory" / "workflow_state.json"
        state = _read_json(state_path)
        state["current_stage"] = 6
        state["status"] = "PENDING_USER_APPROVAL"
        state["completed_stages"] = sorted(set(state["completed_stages"] + [5]))
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        _write_json(state_path, state)
        emit(5, "COMPLETED", "NarrationScript ready at Gate 2.")
        return {"status": "COMPLETED", "gate": 2}

    def save_and_validate_script(self, slug: str, beats: list[ScriptBeat]) -> NarrationScriptState:
        self.store.ensure_mutable(slug)
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        report = analyze_narration_beats(beats)
        _write_json(
            ep_dir / "narration" / "script.json",
            {"beats": [b.model_dump() for b in beats]},
        )
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
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        beats = [ScriptBeat(**b) for b in _CONDENSED_BEATS]
        _write_json(
            ep_dir / "narration" / "script.json",
            {"beats": [b.model_dump() for b in beats]},
        )
        state_path = ep_dir / "content_factory" / "workflow_state.json"
        state = _read_json(state_path)
        state["approval_gates"]["gate_2_script"]["status"] = "PENDING"
        _write_json(state_path, state)
        self.store.write_studio_meta(slug, {"measuredAudioDurationSec": None})
        return analyze_narration_beats(beats)

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

        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        state_path = ep_dir / "content_factory" / "workflow_state.json"
        state = _read_json(state_path)
        state["approval_gates"]["gate_2_script"] = {
            "status": "APPROVED",
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "approved_by": "user",
            "word_count": ep.narrationScript.wordCount,
            "notes": notes,
        }
        state["current_stage"] = 7
        state["status"] = "IN_PROGRESS"
        state["completed_stages"] = sorted(set(state["completed_stages"] + [6]))
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        _write_json(state_path, state)
        return [7, 8, 9, 10, 11]

    def prepare_retry_stage(self, slug: str, stage: int) -> list[int]:
        self.store.ensure_mutable(slug)
        if stage < 7 or stage > 11:
            raise AppError("VALIDATION_ERROR", f"Stage {stage} cannot be retried.", 400)
        return list(range(stage, 12))

    def execute_render_pipeline(
        self, slug: str, stages: list[int], emit: StageEmitter
    ) -> dict[str, Any]:
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        state_path = ep_dir / "content_factory" / "workflow_state.json"
        history = self.executed_stages.setdefault(slug, [])

        for st in stages:
            emit(st, "RUNNING", f"Running Stage {st}...")
            history.append(st)
            time.sleep(self.stage_delay_sec)

            if self.simulate_stage_failure_at == st:
                state = _read_json(state_path)
                state["current_stage"] = st
                state["status"] = "STAGE_FAILED"
                _write_json(state_path, state)
                emit(st, "FAILED", f"Simulated provider failure at Stage {st}.")
                return {"status": "FAILED", "error": f"Stage {st} provider failure"}

            if st == 9 and self.simulate_pacing_failure:
                measured = 54.2
                emit(
                    9,
                    "FAILED",
                    f"Audio duration {measured}s exceeds 50.0s target at 1.0x pace; artificial speed-up prohibited.",
                )
                beats = [ScriptBeat(**b) for b in _CONDENSED_BEATS]
                _write_json(
                    ep_dir / "narration" / "script.json",
                    {"beats": [b.model_dump() for b in beats]},
                )
                state = _read_json(state_path)
                state["current_stage"] = 6
                state["status"] = "PACING_REMEDIATION"
                state["approval_gates"]["gate_2_script"]["status"] = "PENDING"
                _write_json(state_path, state)
                self.store.write_studio_meta(slug, {"measuredAudioDurationSec": measured})
                return {"status": "PACING_REMEDIATION", "gate": 2, "measuredDurationSec": measured}

            if st == 11:
                if self.simulate_audit_failure:
                    _write_json(
                        ep_dir / "qa" / "qa_report.json",
                        {
                            "overallStatus": "FAIL",
                            "dimensions": {
                                "visual": True,
                                "audio": False,
                                "technical": True,
                                "factual": True,
                            },
                            "diagnostics": ["Audio: music.wav is silent or missing BGM bed."],
                        },
                    )
                    state = _read_json(state_path)
                    state["current_stage"] = 11
                    state["status"] = "AUDIT_FAILED"
                    _write_json(state_path, state)
                    emit(11, "FAILED", "4D QualityAudit failed on Audio dimension.")
                    return {"status": "FAILED", "error": "4D QualityAudit failed: Audio"}

                _write_json(
                    ep_dir / "qa" / "qa_report.json",
                    {
                        "overallStatus": "PASS",
                        "dimensions": {
                            "visual": True,
                            "audio": True,
                            "technical": True,
                            "factual": True,
                        },
                        "diagnostics": [],
                    },
                )
                self._write_demo_media_and_kit(slug, ep_dir)

            state = _read_json(state_path)
            state["completed_stages"] = sorted(set(state["completed_stages"] + [st]))
            state["current_stage"] = 12 if st == 11 else st + 1
            if st == 11:
                state["status"] = "PENDING_USER_APPROVAL"
            _write_json(state_path, state)
            emit(st, "COMPLETED", f"Stage {st} completed.")

        return {"status": "COMPLETED", "gate": 3}

    def _write_demo_media_and_kit(self, slug: str, ep_dir: Path) -> None:
        out_dir = ep_dir / "papercut" / "out"
        out_dir.mkdir(parents=True, exist_ok=True)
        # Deterministic byte payload for Range streaming tests
        (out_dir / f"episode-{slug}.mp4").write_bytes(b"FTYPMP4DEMO" * 256)
        (out_dir / "opening-frame.png").write_bytes(b"\x89PNG\r\n\x1a\nDEMO")
        _write_json(
            ep_dir / "publishing" / "publishing-kit.json",
            {
                "youtube": {
                    "titleWithHashtags": "Bagaimana Jika Oksigen Bumi Naik Dua Kali Lipat? #Shorts #Sains",
                    "description": (
                        "Lonjakan oksigen atmosfer membuat api menyala jauh lebih panas dan mendorong "
                        "serangga tumbuh menjadi raksasa seperti era Karbon ratusan juta tahun lalu."
                    ),
                    "tags": ["what if", "sains", "eksperimen", "meowndr", "shorts"],
                    "pinnedComment": "Menurutmu manusia bisa bertahan atau tidak di kondisi ini?",
                },
                "tiktok": {
                    "caption": "Oksigen bumi naik dua kali lipat: serangga membesar dan api menyala lebih cepat! Berani hidup di era ini?",
                    "tags": ["#whatif", "#sains", "#edukasi"],
                },
                "instagram": {
                    "caption": (
                        "Ketika oksigen melonjak dua kali lipat, tekanan udara meningkat dan serangga menyerap lebih banyak energi.\n\n"
                        "Di era Karbon dahulu, kadar oksigen tinggi memang melahirkan capung raksasa selebar burung elang.\n\n"
                        "Simpan dan bagikan ke temanmu!"
                    ),
                    "hashtags": ["#sains", "#whatif", "#faktaunik", "#meowndr"],
                },
            },
        )

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
        if self.simulate_upload_failure:
            raise AppError(
                code="CLOUD_ARCHIVE_FAILED",
                message="rclone gdrive-new unreachable; local VideoAsset and PublishingKit preserved.",
                status_code=502,
            )

        self.upload_count[slug] = self.upload_count.get(slug, 0) + 1
        dest = f"gdrive-new:Antigravity/Videos/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_{slug}"
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        state_path = ep_dir / "content_factory" / "workflow_state.json"
        state = _read_json(state_path)
        state["approval_gates"]["gate_3_final_video"] = {
            "status": "APPROVED",
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "approved_by": "user",
            "render_path": str(ep_dir / "papercut" / "out" / f"episode-{slug}.mp4"),
            "notes": notes,
        }
        state["status"] = "COMPLETED"
        state["completed_stages"] = sorted(set(state["completed_stages"] + [12]))
        _write_json(state_path, state)
        self.store.write_studio_meta(slug, {"gdriveDestination": dest})
        return self.store.get_episode(slug), dest
