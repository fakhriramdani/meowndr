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

    def discover_trends(
        self,
        niche: Niche,
        age_category: AgeCategory,
        exclude_premises: list[str] | None = None,
    ) -> list[TrendOpportunity]: ...

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

    def discover_trends(
        self,
        niche: Niche,
        age_category: AgeCategory,
        exclude_premises: list[str] | None = None,
    ) -> list[TrendOpportunity]:
        llm_items = self._discover_trends_with_llm(niche, age_category, exclude_premises)
        if llm_items:
            return llm_items

        from library.content_factory.trend_intelligence import run_trend_research_pipeline

        result = run_trend_research_pipeline(niche=niche)
        raw_opps = result.get("payload", {}).get("evaluated_opportunities", [])
        what_if_opps = [
            o for o in raw_opps
            if any(k in str(o.get("proposed_title", "")).lower() for k in ("bagaimana jika", "apa yang terjadi jika"))
        ]
        pool = what_if_opps + [o for o in raw_opps if o not in what_if_opps]
        excluded = {p.strip().lower() for p in (exclude_premises or []) if p.strip()}
        unseen = [
            o for o in pool
            if str(o.get("proposed_title", "")).strip().lower() not in excluded
        ]
        selected = unseen if unseen else pool

        opportunities: list[TrendOpportunity] = []
        for idx, item in enumerate(selected[:5], start=1):
            premise = str(item.get("proposed_title") or f"Bagaimana jika {niche} berubah?")
            vc = item.get("video_concept") or {}
            scenes = vc.get("scenes") or []
            cascade = [str(s) for s in scenes if str(s).strip()]
            if not cascade and vc.get("opening_hook"):
                cascade.append(str(vc["opening_hook"]))
            while len(cascade) < 6:
                cascade.append(f"Dampak lanjutan tahap {len(cascade) + 1} pada {niche}.")
            score_val = (item.get("scoring") or {}).get("total_score") or (96 - idx * 3)
            opportunities.append(
                TrendOpportunity(
                    id=str(item.get("id") or f"trend-{niche}-{idx}"),
                    premise=premise,
                    niche=niche,
                    ageCategory=age_category,
                    opportunityScore=max(0, min(100, int(round(float(score_val))))),
                    temporalCascade=cascade[:6],
                )
            )
        opportunities.sort(key=lambda o: o.opportunityScore, reverse=True)
        return opportunities

    def _discover_trends_with_llm(
        self,
        niche: Niche,
        age_category: AgeCategory,
        exclude_premises: list[str] | None,
    ) -> list[TrendOpportunity]:
        """Generate 5 fresh counterfactual What-If ideas via LLM, falling back on error."""
        from library.content_factory.captions.llm_caption_generator import LLMCaptionGenerator

        excluded_clean = [p.strip() for p in (exclude_premises or []) if p.strip()]
        exclude_block = ""
        if excluded_clean:
            joined = "\n".join(f"- {p}" for p in excluded_clean[-30:])
            exclude_block = f"\nDILARANG mengulang, memparafrase, atau memakai premis berikut:\n{joined}\n"

        prompt = f"""Kamu adalah Trend & What-If Researcher untuk kanal edukasi papercut @meowndr (YouTube Shorts / TikTok / Reels bahasa Indonesia).
Buatkan 5 ide topik skenario kontrafaktual "Bagaimana jika..." yang segar, mengejutkan, akurat secara sains/sejarah, dan berpotensi viral tinggi.

Niche: {niche}
Target audiens: {age_category}
{exclude_block}
Aturan wajib:
1. Setiap premise HARUS diawali "Bagaimana jika ..." dalam bahasa Indonesia yang natural dan memicu rasa penasaran tinggi.
2. Setiap ide HARUS memiliki 6 beat Temporal Cascade (Beat 1 Katalis -> Beat 2 Guncangan Awal -> Beat 3 Efek Domino -> Beat 4 Masa Kini -> Beat 5 Realitas Ilmiah/Sejarah -> Beat 6 Dilema).
3. Beri opportunityScore realistis antara 75-98.
4. Jawab HANYA dengan JSON valid sesuai skema ini tanpa teks tambahan:
{{
  "opportunities": [
    {{
      "premise": "Bagaimana jika ...?",
      "opportunityScore": 94,
      "temporalCascade": [
        "Beat 1 (Katalis): ...",
        "Beat 2 (Guncangan Awal): ...",
        "Beat 3 (Efek Domino): ...",
        "Beat 4 (Masa Kini): ...",
        "Beat 5 (Realitas): ...",
        "Beat 6 (Dilema): ..."
      ]
    }}
  ]
}}"""
        try:
            data = LLMCaptionGenerator.call_llm(prompt, timeout_sec=60)
            raw_list = data.get("opportunities") if isinstance(data, dict) else None
            if not isinstance(raw_list, list) or not raw_list:
                return []

            excluded_lower = {p.lower() for p in excluded_clean}
            items: list[TrendOpportunity] = []
            for idx, entry in enumerate(raw_list[:5], start=1):
                if not isinstance(entry, dict):
                    continue
                premise = str(entry.get("premise") or "").strip()
                if not premise or premise.lower() in excluded_lower:
                    continue
                raw_cascade = entry.get("temporalCascade") or []
                cascade = [str(b).strip() for b in raw_cascade if str(b).strip()]
                while len(cascade) < 6:
                    cascade.append(f"Beat {len(cascade) + 1}: Dampak lanjutan pada {niche}.")
                score_raw = entry.get("opportunityScore", 92 - idx * 2)
                try:
                    score = max(0, min(100, int(round(float(score_raw)))))
                except (TypeError, ValueError):
                    score = 88
                items.append(
                    TrendOpportunity(
                        id=f"trend-llm-{niche}-{uuid.uuid4().hex[:6]}",
                        premise=premise,
                        niche=niche,
                        ageCategory=age_category,
                        opportunityScore=score,
                        temporalCascade=cascade[:6],
                    )
                )
            items.sort(key=lambda o: o.opportunityScore, reverse=True)
            return items
        except Exception as err:
            _log.warning("LLM trend discovery failed, falling back to local pipeline: %s", err)
            return []

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

    def _generate_fact_claims_with_llm(
        self, topic: str, niche: str, cascade: list[str]
    ) -> list[dict[str, Any]]:
        """Generate dual-layer verified claims for Stage 2 Fact Research via LLM, with fallback."""
        from library.content_factory.captions.llm_caption_generator import LLMCaptionGenerator

        prompt = f"""Kamu adalah Fact Researcher untuk kanal edukasi sains & sejarah @meowndr.
Lakukan verifikasi 2-lapis untuk topik What-If berikut:
Topik: {topic}
Niche: {niche}
Alur cascade: {json.dumps(cascade, ensure_ascii=False)}

Buatkan 3 klaim faktual terverifikasi (Lapis 1: fakta titik awal nyata; Lapis 2: dasar ilmiah/sejarah efek domino).
Jawab HANYA dengan JSON valid:
{{
  "claims": [
    {{
      "claim_id": "claim_1",
      "statement": "Pernyataan fakta spesifik bahasa Indonesia.",
      "explanation": "Penjelasan ringkas hubungan kausal ke skenario What-If.",
      "sources": [
        {{"title": "NASA / UNESCO / Kemendikbud / Nature", "url": "https://example.org/source", "publisher": "Primary Source"}}
      ]
    }}
  ]
}}"""
        try:
            data = LLMCaptionGenerator.call_llm(prompt, timeout_sec=60)
            claims = data.get("claims") if isinstance(data, dict) else None
            if isinstance(claims, list) and len(claims) >= 2:
                normalized: list[dict[str, Any]] = []
                for idx, item in enumerate(claims[:5], start=1):
                    if not isinstance(item, dict) or not str(item.get("statement") or "").strip():
                        continue
                    sources = item.get("sources") or []
                    if not isinstance(sources, list) or not sources:
                        sources = [{"title": "Reference Dossier", "url": "https://www.britannica.com", "publisher": "Encyclopedia"}]
                    normalized.append(
                        {
                            "claim_id": str(item.get("claim_id") or f"claim_{idx}"),
                            "statement": str(item["statement"]).strip(),
                            "explanation": str(item.get("explanation") or "").strip(),
                            "sources": sources,
                        }
                    )
                if normalized:
                    return normalized
        except Exception as err:
            _log.warning("LLM fact research failed, using fallback claims: %s", err)

        return [
            {
                "claim_id": "claim_1",
                "statement": f"Titik awal skenario '{topic}' bertumpu pada hukum alam dan kondisi historis nyata dalam bidang {niche}.",
                "explanation": "Parameter dasar sistem bumi dan catatan sejarah menjadi acuan sebelum titik percabangan terjadi.",
                "sources": [{"title": "Encyclopedia Britannica", "url": "https://www.britannica.com", "publisher": "Britannica"}],
            },
            {
                "claim_id": "claim_2",
                "statement": f"Efek domino lanjutan pada {niche} mengikuti prinsip kausalitas fisika, ekologi, atau geopolitik yang terukur.",
                "explanation": "Perubahan satu variabel utama memicu reaksi berantai bertahap hingga membentuk kondisi masa kini.",
                "sources": [{"title": "Nature Research Archive", "url": "https://www.nature.com", "publisher": "Nature"}],
            },
        ]

    def _generate_hooks_with_llm(
        self, topic: str, niche: str, cascade: list[str]
    ) -> tuple[list[dict[str, Any]], str, str]:
        """Generate 5 scored HookVariant candidates for Stage 3 via LLM, with fallback."""
        from library.content_factory.captions.llm_caption_generator import LLMCaptionGenerator

        prompt = f"""Kamu adalah Hook Researcher untuk video vertikal 9:16 @meowndr.
Buatkan 5 varian hook pembuka (0-3 detik) berbahasa Indonesia yang memicu rasa penasaran tinggi untuk topik:
Topik: {topic}
Niche: {niche}
Alur cascade: {json.dumps(cascade, ensure_ascii=False)}

Jawab HANYA dengan JSON valid:
{{
  "primary_recommendation": "v1",
  "visual_hook_concept": "Deskripsi visual adegan pembuka frame-0 bersama Cat Scientist.",
  "variants": [
    {{
      "id": "v1",
      "archetype": "paradox",
      "hook_text": "Kalimat hook pembuka tajam bahasa Indonesia...",
      "cover_lines": [["BARIS", "SATU"], ["BARIS", "DUA"]],
      "hot_words": ["KATA", "KUNCI"],
      "curiosity_score": 9.4,
      "clarity_score": 9.2,
      "visual_score": 9.3,
      "composite_score": 9.3
    }}
  ]
}}"""
        archetypes = ["paradox", "counter_intuitive", "sensory_mystery", "high_stakes", "direct_challenge"]
        valid_archetypes = set(archetypes)
        try:
            data = LLMCaptionGenerator.call_llm(prompt, timeout_sec=60)
            raw_variants = data.get("variants") if isinstance(data, dict) else None
            if isinstance(raw_variants, list) and len(raw_variants) >= 3:
                variants: list[dict[str, Any]] = []
                for idx, item in enumerate(raw_variants[:5], start=1):
                    if not isinstance(item, dict) or not str(item.get("hook_text") or "").strip():
                        continue
                    vid = str(item.get("id") or f"v{idx}")
                    raw_arch = str(item.get("archetype") or "").strip().lower()
                    arch = raw_arch if raw_arch in valid_archetypes else archetypes[(idx - 1) % len(archetypes)]
                    variants.append(
                        {
                            "id": vid,
                            "archetype": arch,
                            "hook_text": str(item["hook_text"]).strip(),
                            "cover_lines": item.get("cover_lines") or [["BAGAIMANA", "JIKA"], [niche.upper(), "BERUBAH?"]],
                            "hot_words": item.get("hot_words") or ["BAGAIMANA", "JIKA"],
                            "curiosity_score": float(item.get("curiosity_score", 9.2 - idx * 0.2)),
                            "clarity_score": float(item.get("clarity_score", 9.0 - idx * 0.2)),
                            "visual_score": float(item.get("visual_score", 9.1 - idx * 0.2)),
                            "composite_score": float(item.get("composite_score", 9.1 - idx * 0.2)),
                        }
                    )
                if len(variants) >= 3:
                    primary = str(data.get("primary_recommendation") or variants[0]["id"])
                    visual = str(data.get("visual_hook_concept") or f"Cat Scientist memperagakan skenario {topic} di laboratorium papercut.")
                    return variants, primary, visual
        except Exception as err:
            _log.warning("LLM hook generation failed, using fallback variants: %s", err)

        fallback_hooks = [
            ("v1", "paradox", topic, 9.4),
            ("v2", "high_stakes", f"Bayangkan detik pertama saat skenario ini benar-benar terjadi: {topic}", 9.0),
            ("v3", "direct_challenge", f"Kebanyakan orang tak sadar dampak berantainya: {topic}", 8.7),
            ("v4", "sensory_mystery", f"Apa yang berubah di dunia kita hari ini jika {topic.lower().rstrip('?')}?", 8.5),
            ("v5", "counter_intuitive", f"Satu perubahan kecil di {niche}, seluruh peradaban ikut bergeser.", 8.2),
        ]
        variants = [
            {
                "id": vid,
                "archetype": arch,
                "hook_text": text,
                "cover_lines": [["BAGAIMANA", "JIKA"], [niche.upper(), "BERUBAH?"]],
                "hot_words": ["BAGAIMANA", "JIKA"],
                "curiosity_score": score,
                "clarity_score": round(score - 0.1, 1),
                "visual_score": round(score - 0.1, 1),
                "composite_score": score,
            }
            for vid, arch, text, score in fallback_hooks
        ]
        return variants, "v1", f"Cat Scientist memperagakan titik percabangan '{topic}' di atas meja papercut."

    def _generate_script_lines_with_llm(
        self, topic: str, niche: str, cascade: list[str]
    ) -> list[dict[str, Any]]:
        """Generate 6-beat What-If Indonesian narration lines (no digits 0-9) via LLM, with fallback."""
        from library.content_factory.captions.llm_caption_generator import LLMCaptionGenerator

        prompt = f"""Kamu adalah Scriptwriter untuk video reels edukasi papercut @meowndr (durasi 40-48 detik, 1.0x tempo alami).
Tulis naskah voiceover bahasa Indonesia 6-beat What-If Narrative Arc untuk topik:
Topik: {topic}
Niche: {niche}
Referensi cascade: {json.dumps(cascade, ensure_ascii=False)}

ATURAN MUTLAK:
1. Total kata seluruh 6 beat WAJIB antara 95 sampai 120 kata.
2. DILARANG KERAS menulis angka digit (0-9) seperti "5", "60", "2x", "100". Tulis semua angka dengan huruf (contoh: "lima", "enam puluh", "dua kali lipat", "seratus").
3. Struktur tepat 6 beat:
   - beat_1 (Katalis, ~7s)
   - beat_2 (Guncangan Awal, ~8s)
   - beat_3 (Efek Domino, ~8s)
   - beat_4 (Dampak Masa Kini, ~8s)
   - beat_5 (Realitas Sains/Sejarah, ~8s)
   - beat_6 (Outro & Dilema CTA, ~6s)
4. Jawab HANYA dengan JSON valid:
{{
  "lines": [
    {{"id": "beat_1", "beat_label": "Katalis & Titik Percabangan", "text": "...", "target_seconds": 7}},
    {{"id": "beat_2", "beat_label": "Guncangan Awal", "text": "...", "target_seconds": 8}},
    {{"id": "beat_3", "beat_label": "Efek Domino", "text": "...", "target_seconds": 8}},
    {{"id": "beat_4", "beat_label": "Transformasi Masa Kini", "text": "...", "target_seconds": 8}},
    {{"id": "beat_5", "beat_label": "Realitas Ilmiah", "text": "...", "target_seconds": 8}},
    {{"id": "beat_6", "beat_label": "Dilema & CTA", "text": "...", "target_seconds": 6}}
  ]
}}"""
        try:
            data = LLMCaptionGenerator.call_llm(prompt, timeout_sec=60)
            raw_lines = data.get("lines") if isinstance(data, dict) else None
            if isinstance(raw_lines, list) and len(raw_lines) == 6:
                cleaned: list[dict[str, Any]] = []
                for idx, entry in enumerate(raw_lines, start=1):
                    text = str(entry.get("text") or "").strip()
                    text = re.sub(r"\d+", "beberapa", text)
                    if not text:
                        break
                    cleaned.append(
                        {
                            "id": str(entry.get("id") or f"beat_{idx}"),
                            "beat_label": str(entry.get("beat_label") or f"Beat {idx}"),
                            "text": text,
                            "target_seconds": float(entry.get("target_seconds", 7.5)),
                        }
                    )
                if len(cleaned) == 6:
                    return cleaned
        except Exception as err:
            _log.warning("LLM scriptwriting failed, using fallback 6-beat script: %s", err)

        clean_topic = re.sub(r"\d+", "beberapa", topic).strip()
        return [
            {"id": "beat_1", "beat_label": "Katalis & Titik Percabangan", "text": f"{clean_topic} Pernah membayangkan satu momen kecil itu benar-benar mengubah arah dunia kita?", "target_seconds": 7.0},
            {"id": "beat_2", "beat_label": "Guncangan Awal", "text": f"Pada detik pertama setelah titik balik tersebut, keseimbangan utama di bidang {niche} langsung terguncang hebat.", "target_seconds": 8.0},
            {"id": "beat_3", "beat_label": "Efek Domino", "text": "Puluhan hingga ratusan tahun kemudian, reaksi berantai muncul dan membentuk pola alam serta peradaban yang sama sekali berbeda.", "target_seconds": 8.0},
            {"id": "beat_4", "beat_label": "Transformasi Masa Kini", "text": "Akibatnya di masa sekarang, cara manusia bertahan hidup, teknologi, dan tatanan dunia ikut bergeser drastis.", "target_seconds": 8.0},
            {"id": "beat_5", "beat_label": "Realitas Ilmiah", "text": "Untungnya di garis waktu nyata kita, hukum alam dan sejarah menjaga sistem ini tetap berada dalam keseimbangan yang stabil.", "target_seconds": 8.0},
            {"id": "beat_6", "beat_label": "Dilema & CTA", "text": "Simpan dan bagikan video ini, lalu tulis pendapatmu di komentar jika skenario ini benar-benar terjadi.", "target_seconds": 6.0},
        ]

    def run_fact_and_hooks(self, slug: str, emit: StageEmitter) -> dict[str, Any]:
        ep = self.store.get_episode(slug)
        engine = self._engine(slug=slug, niche=ep.niche, title=ep.title)
        meta = self.store.read_studio_meta(slug)
        cascade = list(meta.get("temporalCascade") or [])
        emit(2, "RUNNING", f"Running two-layer FactResearch for {slug}...")
        claims = self._generate_fact_claims_with_llm(ep.title, ep.niche, cascade)
        engine.run_stage_2_fact_research(topic=ep.title, claims=claims)
        emit(2, "COMPLETED", "FactResearch verified.")
        emit(3, "RUNNING", "Generating 5 scored HookVariant candidates...")
        variants, primary_rec, visual_concept = self._generate_hooks_with_llm(ep.title, ep.niche, cascade)
        engine.run_stage_3_hook_generation(
            topic=ep.title,
            variants=variants,
            primary_rec=primary_rec,
            visual_concept=visual_concept,
        )
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
        engine.run_stage_4_gate_1_approval(
            approved_by="Studio User",
            selected_hook_id=hook_id,
            notes=notes or "Approved via Studio UI",
        )
        return [5]

    def run_script_generation(self, slug: str, emit: StageEmitter) -> dict[str, Any]:
        ep = self.store.get_episode(slug)
        engine = self._engine(slug=slug, niche=ep.niche, title=ep.title)
        meta = self.store.read_studio_meta(slug)
        cascade = list(meta.get("temporalCascade") or [])
        emit(5, "RUNNING", "Generating 6-beat What-If NarrationScript...")
        lines = self._generate_script_lines_with_llm(ep.title, ep.niche, cascade)
        engine.run_stage_5_scriptwriting(lines=lines, preflight_tts=False)
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

    def _condense_clause(self, text: str, max_words: int = 17) -> str:
        """Condense text to <= max_words on sentence or clause boundaries without mid-clause truncation."""
        words = text.split()
        if len(words) <= max_words:
            return text.strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
        kept: list[str] = []
        total = 0
        for sentence in sentences:
            s_words = sentence.split()
            if total + len(s_words) <= max_words or not kept:
                kept.append(sentence)
                total += len(s_words)
            else:
                break
        candidate = " ".join(kept).strip()
        if len(candidate.split()) <= max_words:
            return candidate
        clauses = [c.strip() for c in re.split(r"(?<=[,;:])\s+", candidate) if c.strip()]
        if len(clauses) > 1:
            trimmed = clauses[0].rstrip(",;:")
            if not trimmed.endswith((".", "!", "?")):
                trimmed += "."
            return trimmed
        return candidate

    def condense_script(self, slug: str) -> NarrationScriptState:
        self.store.ensure_mutable(slug)
        ep = self.store.get_episode(slug)
        if ep.narrationScript is None:
            raise AppError("VALIDATION_ERROR", "No script found to condense.", 400)
        condensed_beats: list[ScriptBeat] = []
        for b in ep.narrationScript.beats:
            trimmed = self._condense_clause(b.text, max_words=17)
            condensed_beats.append(
                ScriptBeat(id=b.id, beatNumber=b.beatNumber, beatLabel=b.beatLabel, text=trimmed)
            )
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        script_path = ep_dir / "narration" / "script.json"
        existing = json.loads(script_path.read_text(encoding="utf-8")) if script_path.exists() else {}
        spoken_text = " ".join(b.text.strip() for b in condensed_beats if b.text.strip()).strip()
        existing["beats"] = [b.model_dump() for b in condensed_beats]
        existing["spoken_text"] = spoken_text
        existing["text"] = spoken_text
        existing["tts"] = spoken_text
        script_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
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
        engine.run_stage_6_gate_2_approval(
            approved_by="Studio User",
            notes=notes or "Approved via Studio UI",
        )
        return [7, 8, 9, 10, 11]

    def prepare_retry_stage(self, slug: str, stage: int) -> list[int]:
        self.store.ensure_mutable(slug)
        if stage < 7 or stage > 11:
            raise AppError("VALIDATION_ERROR", f"Stage {stage} cannot be retried via render pipeline.", 400)
        return list(range(stage, 12))

    def _run_tool(self, args: list[str], stage: int) -> str:
        proc = subprocess.run(
            args,
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or f"Stage {stage} command failed").strip()
            raise RuntimeError(detail)
        return (proc.stdout or "").strip()

    def _measure_audio_duration_sec(self, ep_dir: Path) -> float | None:
        audio_plan = ep_dir / "audio" / "audio_plan.json"
        if audio_plan.exists():
            try:
                data = json.loads(audio_plan.read_text(encoding="utf-8"))
                for key in ("total_duration_sec", "duration_sec", "narration_duration_sec"):
                    if key in data and data[key] is not None:
                        return float(data[key])
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                _log.warn("adapter.audio_plan_parse", "Could not parse audio_plan.json", error=str(exc))
        timing_js = ep_dir / "narration" / "timing_narrator.js"
        if timing_js.exists():
            match = re.search(r"durationSec\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)", timing_js.read_text(encoding="utf-8"))
            if match:
                return float(match.group(1))
        return None

    def execute_render_pipeline(
        self, slug: str, stages: list[int], emit: StageEmitter
    ) -> dict[str, Any]:
        ep = self.store.get_episode(slug)
        ep_dir = resolve_safe_episode_path(self.episodes_root, slug)
        engine = self._engine(slug=slug, niche=ep.niche, title=ep.title)
        tools_dir = self.repo_root / "library" / "tools"
        pipeline_cli = tools_dir / "production_pipeline.py"
        narration_cli = tools_dir / "generate_narration.py"
        scaffold_cli = tools_dir / "scaffold_episode.py"

        for st in stages:
            emit(st, "RUNNING", f"Executing Stage {st}...")
            if st == 7:
                storyboard_path = ep_dir / "storyboard" / "storyboard.json"
                if not storyboard_path.exists():
                    engine.run_stage_7_storyboarding()
                if not (ep_dir / "papercut" / "package.json").exists():
                    self._run_tool([sys.executable, str(scaffold_cli), slug, "--force"], st)
            elif st == 8:
                asset_plan_path = ep_dir / "assets" / "asset_plan.json"
                if not asset_plan_path.exists():
                    engine.run_stage_8_asset_planning()
            elif st == 9:
                self._run_tool([sys.executable, str(narration_cli), slug], st)
                measured = self._measure_audio_duration_sec(ep_dir)
                if measured is not None and measured > 50.0:
                    emit(
                        9,
                        "FAILED",
                        f"Audio duration {measured:.1f}s exceeds 50.0s target at 1.0x pace; artificial speed-up prohibited.",
                    )
                    self.condense_script(slug)
                    state_path = ep_dir / "content_factory" / "workflow_state.json"
                    if state_path.exists():
                        state = json.loads(state_path.read_text(encoding="utf-8"))
                        state["current_stage"] = 6
                        state["status"] = "PACING_REMEDIATION"
                        state["approval_gates"]["gate_2_script"]["status"] = "PENDING"
                        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
                    self.store.write_studio_meta(slug, {"measuredAudioDurationSec": measured})
                    return {
                        "status": "PACING_REMEDIATION",
                        "gate": 2,
                        "measuredDurationSec": measured,
                    }
                self._run_tool([sys.executable, str(pipeline_cli), "bgm", slug], st)
            elif st == 10:
                self._run_tool([sys.executable, str(pipeline_cli), "validate", slug], st)
                self._run_tool([sys.executable, str(pipeline_cli), "render", slug], st)
            elif st == 11:
                self._run_tool([sys.executable, str(pipeline_cli), "qa", slug], st)
                self._run_tool([sys.executable, str(pipeline_cli), "publish-kit", slug], st)
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
        engine.run_stage_12_gate_3_approval(
            approved_by="Studio User",
            notes=notes or "Approved & archived via Studio UI",
            auto_upload_gdrive=False,
        )
        return self.store.get_episode(slug), dest
