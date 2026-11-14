"""
Automated Multi-Platform Caption Generation Engine.
Coordinates input data ingestion, script change tracking, self-healing retries,
platform-specific generation, validation auditing, and release staging.
"""

import os
import sys
import json
import re
import shutil
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
CONTENT_FACTORY_DIR = HERE.parent
REPO_ROOT = CONTENT_FACTORY_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from .schemas.caption_schema import (
    CaptionInput,
    InstagramCaptionOutput,
    TikTokCaptionOutput,
    YouTubeCaptionOutput,
    CaptionBundleOutput
)
from .llm_caption_generator import LLMCaptionGenerator
from .generators.instagram_generator import InstagramCaptionGenerator
from .generators.tiktok_generator import TikTokCaptionGenerator
from .generators.youtube_generator import YouTubeCaptionGenerator
from .validators.composite_validator import CompositeValidator
from .hashtag_intelligence import HashtagIntelligence
from .retention_engine import RetentionEngine
from .scoring_system import CaptionScoringSystem
from .analytics_optimizer import AnalyticsOptimizer


class CaptionEngine:
    """End-to-end automated multi-platform caption engine."""

    def __init__(self, episode_slug: str, base_episodes_dir: Optional[Path] = None):
        self.slug = episode_slug.strip()
        self.episodes_dir = base_episodes_dir or (REPO_ROOT / "episodes")
        self.ep_dir = self.episodes_dir / self.slug
        self.papercut_dir = self.ep_dir / "papercut"
        self.pub_dir = self.ep_dir / "publishing"
        self.output_root = REPO_ROOT / "output" / self.slug
        self._last_bundle: Optional[CaptionBundleOutput] = None

    def load_input_data(self) -> CaptionInput:
        """Extracts and verifies input data from episode assets."""
        if not self.ep_dir.exists():
            raise FileNotFoundError(f"Episode directory not found: {self.ep_dir}")

        # 1. episode.json
        ep_cfg: Dict[str, Any] = {}
        for candidate in [self.papercut_dir / "episode.json", self.ep_dir / "episode.json"]:
            if candidate.exists():
                try:
                    with open(candidate, "r", encoding="utf-8") as f:
                        ep_cfg = json.load(f)
                    break
                except Exception:
                    pass

        meta = ep_cfg.get("meta", {})
        title = meta.get("title") or self.slug.replace("-", " ").title()
        topic = meta.get("topic") or title
        duration = float(meta.get("targetDurationSeconds", 45))
        language = meta.get("language", "id")

        # 2. narration/script.json
        script_lines: List[Dict[str, Any]] = []
        for s_candidate in [
            self.ep_dir / "narration" / "script.json",
            self.papercut_dir / "public" / "vo" / "script.json",
            self.papercut_dir / "script.json"
        ]:
            if s_candidate.exists():
                try:
                    with open(s_candidate, "r", encoding="utf-8") as f:
                        script_lines = json.load(f)
                    break
                except Exception:
                    pass

        script_text = " ".join([l.get("text", "") for l in script_lines if l.get("text")])

        # 3. Hook from hook_matrix.json or script.
        # hook_matrix.json (written by the papercut-hook skill) stores its
        # ranked candidates under "variants", each with "hook_text" (the
        # spoken line) and "cover_lines" (the short frame-0 title words).
        hook = ""
        cover_title = ""
        hook_path = self.ep_dir / "research" / "hook_matrix.json"
        if hook_path.exists():
            try:
                with open(hook_path, "r", encoding="utf-8") as f:
                    h_data = json.load(f)
                    variants = h_data.get("variants", [])
                    primary_id = h_data.get("primary_recommendation")
                    chosen = next((v for v in variants if v.get("id") == primary_id), None)
                    chosen = chosen or (variants[0] if variants else None)
                    if chosen:
                        hook = chosen.get("hook_text", "")
                        cover_lines = chosen.get("cover_lines", [])
                        if cover_lines:
                            words = []
                            for line in cover_lines:
                                if isinstance(line, list):
                                    words.extend(line)
                                elif line:
                                    words.append(str(line))
                            cover_title = " ".join(words).strip()
            except Exception:
                pass
        if not hook and script_lines:
            hook = script_lines[0].get("text", "")

        # 4. Facts from facts.md or dossier.json
        key_facts: List[str] = []
        facts_path = self.ep_dir / "research" / "facts.md"
        if facts_path.exists():
            try:
                with open(facts_path, "r", encoding="utf-8") as f:
                    raw_facts = f.read()
                    current_claim: List[str] = []
                    for ln in raw_facts.splitlines():
                        ln_s = ln.strip()
                        if ln_s.startswith("### [") and "]" in ln_s:
                            if current_claim:
                                key_facts.append(" ".join(current_claim))
                                current_claim = []
                            claim_head = ln_s.split("]", 1)[1].strip()
                            if claim_head:
                                current_claim.append(claim_head)
                        elif ln_s.startswith("**Sources:**") or ln_s.startswith("## ") or ln_s.startswith("# "):
                            if current_claim:
                                key_facts.append(" ".join(current_claim))
                                current_claim = []
                        elif ln_s.startswith("- [http") or "(http" in ln_s:
                            continue
                        elif current_claim and ln_s:
                            current_claim.append(ln_s)
                        elif ln_s.startswith("- "):
                            clean = ln_s.lstrip("- *").strip()
                            if len(clean) > 15:
                                key_facts.append(clean)
                    if current_claim:
                        key_facts.append(" ".join(current_claim))
            except Exception:
                pass

        dossier_path = self.ep_dir / "research" / "dossier.json"
        if dossier_path.exists():
            try:
                with open(dossier_path, "r", encoding="utf-8") as f:
                    d_data = json.load(f)
                    for cl in d_data.get("claims", []):
                        stmt = cl.get("statement", "").strip()
                        expl = cl.get("explanation", "").strip()
                        full_stmt = f"{stmt} {expl}".strip() if expl else stmt
                        if full_stmt and full_stmt not in key_facts:
                            key_facts.append(full_stmt)
            except Exception:
                pass

        # 5. Audience and content category from audience_plan.json or workflow_state.json
        audience = "General curious audience (18-35)"
        category = "science"
        aud_path = self.ep_dir / "strategy" / "audience_plan.json"
        if aud_path.exists():
            try:
                with open(aud_path, "r", encoding="utf-8") as f:
                    aud_data = json.load(f)
                    audience = aud_data.get("target_audience", audience)
                    category = aud_data.get("content_category", category)
            except Exception:
                pass

        wf_path = self.ep_dir / "content_factory" / "workflow_state.json"
        if wf_path.exists():
            try:
                with open(wf_path, "r", encoding="utf-8") as f:
                    wf_data = json.load(f)
                    category = wf_data.get("niche", category)
            except Exception:
                pass

        # Extract main SEO keywords
        stopwords = {
            "kenapa", "mengapa", "bagaimana", "gimana", "saat", "yang", "terasa", "bisa", "lebih",
            "dari", "pada", "dalam", "dengan", "episode", "adalah", "untuk", "oleh",
            "karena", "maka", "jadi", "juga", "kamu", "kita", "sudah", "akan",
            "malah", "bikin", "buat", "kok", "terus", "kalau", "jika", "bila", "tetapi",
            "tapi", "namun", "padahal", "hanya", "cuma", "bukan", "tidak", "nggak",
            "tiap", "setiap", "semua", "seluruh", "antara", "tanpa", "tentang", "seperti",
            "bagai", "bagaikan", "seolah", "ingin", "mau", "sedang", "masih", "telah",
            "pernah", "sempat", "selalu", "sering", "jarang", "banyak", "sedikit", "amat",
            "sangat", "terlalu", "paling", "agak", "cukup", "tentu", "pasti", "mungkin",
            "kira", "ngira", "boleh", "harus", "wajib", "mesti", "dapat", "sanggup", "ada",
            "yaitu", "yakni", "ialah", "merupakan", "begini", "begitu", "demikian",
            "sini", "situ", "sana", "mana", "siapa", "apa", "kapan", "berapa", "saja",
            "lalu", "sesudah", "sebelum", "hingga", "sampai", "agar", "supaya",
            "habis", "sehabis", "setelah", "makan", "minum", "kenyang", "lapar", "langsung",
            "berat", "ringan", "tiba", "siang", "malam", "pagi", "sore", "hari", "balik",
            "rahasia", "alasannya", "penasaran", "fakta", "tahu", "tahukah", "tubuh",
            "orang", "waktu", "secara", "coba", "menu", "satu", "dua", "tiga", "mata",
            "matamu", "seberat", "kelopak", "lemas", "pengen", "tidur", "tumbang",
            "triknya", "gampang", "kurangi", "porsi", "jalan", "santai", "menit", "video",
            "pengingat", "besok", "ketiduran", "piring", "sepiring", "nasi", "padang"
        }
        all_words = re.findall(r"[a-zA-Z0-9]+", f"{title} {topic} {self.slug.replace('-', ' ')}")
        keywords = []
        for w in all_words:
            wl = w.lower()
            if len(wl) >= 4 and wl not in stopwords and wl not in keywords:
                keywords.append(wl)

        return CaptionInput(
            topic=topic,
            title=title,
            script_lines=script_lines,
            script_text=script_text,
            hook=hook,
            cover_title=cover_title,
            key_facts=key_facts,
            target_audience=audience,
            content_category=category,
            main_keywords=keywords[:6],
            duration_seconds=duration,
            language=language,
            channel_name="@meowndr",
            slug=self.slug
        )

    def generate_captions(
        self,
        force: bool = False,
        max_attempts: int = 3,
        platform: Optional[str] = None
    ) -> Tuple[CaptionBundleOutput, bool]:
        """
        Coordinates caption synthesis with retention modeling and 100-pt rubric evaluation.
        Supports independent single-platform regeneration via platform='instagram'|'tiktok'|'youtube'.
        Returns (CaptionBundleOutput, was_cached).
        """
        input_data = self.load_input_data()
        current_hash = input_data.compute_script_hash()

        # Ingest retention dossier and real analytics
        dossier = RetentionEngine.analyze_episode(self.ep_dir, self.slug)
        feedback = AnalyticsOptimizer.load_feedback(self.ep_dir, self.slug)

        # Check existing valid cache
        cache_file = self.pub_dir / "captions.json"
        if not cache_file.exists():
            cache_file = self.output_root / "captions" / "captions.json"

        cached_bundle: Optional[CaptionBundleOutput] = None
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                cached_hash = cached_data.get("script_hash")
                if cached_hash == current_hash:
                    platforms = cached_data.get("platforms", {})
                    ig_data = platforms.get("instagram", {})
                    tt_data = platforms.get("tiktok", {})
                    yt_data = platforms.get("youtube", {})

                    ig_out = InstagramCaptionOutput(
                        caption=ig_data.get("caption", ""),
                        opening_hook=ig_data.get("opening_hook", ""),
                        keywords=ig_data.get("keywords", []),
                        hashtags=ig_data.get("hashtags", []),
                        CTA=ig_data.get("CTA", ""),
                        alternative_caption=ig_data.get("alternative_caption", ""),
                        character_count=ig_data.get("character_count", 0),
                        quality_score=ig_data.get("quality_score", 90),
                        score_breakdown=ig_data.get("score_breakdown", {}),
                        status=ig_data.get("status", "READY"),
                        validation_errors=ig_data.get("validation_errors", [])
                    )
                    tt_out = TikTokCaptionOutput(
                        caption=tt_data.get("caption", ""),
                        opening_hook=tt_data.get("opening_hook", ""),
                        keywords=tt_data.get("keywords", []),
                        hashtags=tt_data.get("hashtags", []),
                        CTA=tt_data.get("CTA", ""),
                        alternative_caption=tt_data.get("alternative_caption", ""),
                        character_count=tt_data.get("character_count", 0),
                        quality_score=tt_data.get("quality_score", 90),
                        score_breakdown=tt_data.get("score_breakdown", {}),
                        status=tt_data.get("status", "READY"),
                        validation_errors=tt_data.get("validation_errors", [])
                    )
                    yt_out = YouTubeCaptionOutput(
                        title=yt_data.get("title", ""),
                        description=yt_data.get("description", ""),
                        search_keywords=yt_data.get("search_keywords", []),
                        hashtags=yt_data.get("hashtags", []),
                        pinned_comment=yt_data.get("pinned_comment", ""),
                        alternative_title=yt_data.get("alternative_title", ""),
                        title_character_count=yt_data.get("title_character_count", 0),
                        description_character_count=yt_data.get("description_character_count", 0),
                        quality_score=yt_data.get("quality_score", 90),
                        score_breakdown=yt_data.get("score_breakdown", {}),
                        status=yt_data.get("status", "READY"),
                        validation_errors=yt_data.get("validation_errors", [])
                    )
                    analysis = cached_data.get("analysis", {})
                    cached_bundle = CaptionBundleOutput(
                        topic=input_data.topic,
                        language=input_data.language,
                        script_hash=current_hash,
                        instagram=ig_out,
                        tiktok=tt_out,
                        youtube=yt_out,
                        generated_at=cached_data.get("generated_at", ""),
                        attempt_count=1,
                        overall_status="READY",
                        validation_report={"cached": True, "script_hash": current_hash},
                        platform_strategy_summary=analysis.get("platform_strategy_summary", {}),
                        caption_quality_score=analysis.get("caption_quality_score", {}),
                        compliance_check=analysis.get("compliance_check", {}),
                        curiosity_score=analysis.get("curiosity_score", {}),
                        keyword_relevance_score=analysis.get("keyword_relevance_score", {}),
                        retention_alignment_score=analysis.get("retention_alignment_score", {})
                    )
            except Exception:
                pass

        # Return full cache if requested and valid
        if not force and not platform and cached_bundle:
            self._last_bundle = cached_bundle
            return cached_bundle, True

        # Independent single-platform regeneration if platform is specified
        norm_plat = platform.lower().strip() if platform else None
        if norm_plat:
            base_bundle = self._last_bundle or cached_bundle
            if not base_bundle:
                base_bundle, _ = self.generate_captions(force=False)

            target_bundle = CaptionBundleOutput(
                topic=base_bundle.topic,
                language=base_bundle.language,
                script_hash=base_bundle.script_hash,
                instagram=base_bundle.instagram,
                tiktok=base_bundle.tiktok,
                youtube=base_bundle.youtube,
                generated_at=base_bundle.generated_at,
                overall_status=base_bundle.overall_status,
                validation_report=base_bundle.validation_report,
                platform_strategy_summary=base_bundle.platform_strategy_summary,
                caption_quality_score=base_bundle.caption_quality_score,
                compliance_check=base_bundle.compliance_check,
                curiosity_score=base_bundle.curiosity_score,
                keyword_relevance_score=base_bundle.keyword_relevance_score,
                retention_alignment_score=base_bundle.retention_alignment_score
            )
            if norm_plat in ("instagram", "ig", "reels"):
                target_bundle.instagram = InstagramCaptionGenerator.generate_validated(input_data, max_attempts=max_attempts)
            elif norm_plat in ("tiktok", "tt"):
                target_bundle.tiktok = TikTokCaptionGenerator.generate_validated(input_data, max_attempts=max_attempts)
            elif norm_plat in ("youtube", "yt", "shorts"):
                target_bundle.youtube = YouTubeCaptionGenerator.generate_validated(input_data, max_attempts=max_attempts)
            self._last_bundle = target_bundle
            return target_bundle, False

        # Execute full LLM-driven generation
        try:
            ig_out, tt_out, yt_out, extra_meta = LLMCaptionGenerator.generate_all_platforms(input_data)
        except Exception as e:
            # Fallback to semantic generation if LLM call is unavailable
            ig_out = InstagramCaptionGenerator.generate_validated(input_data, max_attempts=max_attempts)
            tt_out = TikTokCaptionGenerator.generate_validated(input_data, max_attempts=max_attempts)
            yt_out = YouTubeCaptionGenerator.generate_validated(input_data, max_attempts=max_attempts)

        u_ok, u_errs, u_metrics = CompositeValidator.validate_cross_platform_uniqueness(
            ig_out.caption, tt_out.caption, yt_out.description
        )

        overall_status = "READY" if (
            ig_out.status == "READY" and
            tt_out.status == "READY" and
            yt_out.status == "READY" and
            u_ok
        ) else "NEEDS_REVIEW"

        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        val_report = {
            "topic": input_data.topic,
            "episode_id": self.slug,
            "overall_status": overall_status,
            "script_hash": current_hash,
            "generated_at": now_str,
            "attempts_used": 1,
            "instagram_validation": {
                "status": "PASS" if ig_out.status == "READY" else "FAIL",
                "character_count": ig_out.character_count,
                "hashtags_count": len(ig_out.hashtags),
                "quality_score": ig_out.quality_score,
                "errors": ig_out.validation_errors,
                "warnings": ig_out.validation_warnings
            },
            "tiktok_validation": {
                "status": "PASS" if tt_out.status == "READY" else "FAIL",
                "character_count": tt_out.character_count,
                "hashtags_count": len(tt_out.hashtags),
                "quality_score": tt_out.quality_score,
                "errors": tt_out.validation_errors,
                "warnings": tt_out.validation_warnings
            },
            "youtube_validation": {
                "status": "PASS" if yt_out.status == "READY" else "FAIL",
                "title_character_count": yt_out.title_character_count,
                "description_character_count": yt_out.description_character_count,
                "hashtags_count": len(yt_out.hashtags),
                "quality_score": yt_out.quality_score,
                "errors": yt_out.validation_errors,
                "warnings": yt_out.validation_warnings
            },
            "cross_platform_uniqueness": {
                "status": "PASS" if u_ok else "FAIL",
                "metrics": u_metrics,
                "errors": u_errs
            }
        }

        strat_summary = {
            "instagram": "Curiosity Hook -> Context/Insight -> Engagement Trigger -> Save/Share CTA -> Relevant Hashtags",
            "tiktok": "Curiosity Hook -> Short Context -> Natural CTA -> Relevant Hashtags",
            "youtube_shorts": "Compelling Title -> Informative Overview -> Subscribe CTA -> #Shorts + Topic Hashtags"
        }
        quality_scores = {
            "instagram": ig_out.quality_score,
            "tiktok": tt_out.quality_score,
            "youtube": yt_out.quality_score,
            "composite_average": round((ig_out.quality_score + tt_out.quality_score + yt_out.quality_score) / 3.0, 1)
        }
        compliance_check = {
            "instagram": ig_out.status == "READY",
            "tiktok": tt_out.status == "READY",
            "youtube": yt_out.status == "READY",
            "cross_platform_uniqueness": u_ok
        }
        curiosity_score = {
            "instagram": ig_out.score_breakdown.get("breakdown", {}).get("curiosity_watch_intent", "20/20"),
            "tiktok": tt_out.score_breakdown.get("breakdown", {}).get("curiosity_watch_intent", "20/20"),
            "youtube": yt_out.score_breakdown.get("breakdown", {}).get("curiosity_watch_intent", "20/20")
        }
        keyword_relevance_score = {
            "instagram": ig_out.score_breakdown.get("breakdown", {}).get("seo_keyword_relevance", "15/15"),
            "tiktok": tt_out.score_breakdown.get("breakdown", {}).get("seo_keyword_relevance", "15/15"),
            "youtube": yt_out.score_breakdown.get("breakdown", {}).get("seo_keyword_relevance", "15/15")
        }
        retention_alignment_score = {
            "instagram": ig_out.score_breakdown.get("breakdown", {}).get("hook_strength", "20/20"),
            "tiktok": tt_out.score_breakdown.get("breakdown", {}).get("hook_strength", "20/20"),
            "youtube": yt_out.score_breakdown.get("breakdown", {}).get("hook_strength", "20/20")
        }

        bundle = CaptionBundleOutput(
            topic=input_data.topic,
            language=input_data.language,
            script_hash=current_hash,
            instagram=ig_out,
            tiktok=tt_out,
            youtube=yt_out,
            generated_at=now_str,
            attempt_count=1,
            overall_status=overall_status,
            validation_report=val_report,
            platform_strategy_summary=strat_summary,
            caption_quality_score=quality_scores,
            compliance_check=compliance_check,
            curiosity_score=curiosity_score,
            keyword_relevance_score=keyword_relevance_score,
            retention_alignment_score=retention_alignment_score
        )
        self._last_bundle = bundle
        return bundle, False

    def save_deliverables(self, force: bool = False, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Saves all standardized deliverables into:
          episodes/<slug>/publishing/
            instagram.txt
            tiktok.txt
            youtube_title.txt
            youtube_description.txt
            youtube.txt
            captions.json
            validation-report.json
            instagram.json
            tiktok.json
            youtube-shorts.json
            caption-analysis.json
        """
        bundle, was_cached = self.generate_captions(force=force, platform=platform)

        # Canonical Publishing directory: episodes/<slug>/publishing/
        self.pub_dir.mkdir(parents=True, exist_ok=True)

        files_written = {}

        # 1. Plain text files
        # instagram
        ig_text = bundle.instagram.caption.strip() + "\n"
        ig_file = self.pub_dir / "instagram.txt"
        with open(ig_file, "w", encoding="utf-8") as f:
            f.write(ig_text)
        files_written["instagram"] = str(ig_file)

        # Clean up legacy redundant duplicate file
        legacy_ig = self.pub_dir / "instagram_caption.txt"
        if legacy_ig.exists():
            try:
                legacy_ig.unlink()
            except OSError:
                pass

        # tiktok
        tt_text = bundle.tiktok.caption.strip() + "\n"
        tt_file = self.pub_dir / "tiktok.txt"
        with open(tt_file, "w", encoding="utf-8") as f:
            f.write(tt_text)
        files_written["tiktok"] = str(tt_file)

        # Clean up legacy redundant duplicate file
        legacy_tt = self.pub_dir / "tiktok_caption.txt"
        if legacy_tt.exists():
            try:
                legacy_tt.unlink()
            except OSError:
                pass

        # youtube
        yt_combined = f"Title: {bundle.youtube.title}\n\nDescription:\n{bundle.youtube.description}\n"
        yt_combined_file = self.pub_dir / "youtube.txt"
        with open(yt_combined_file, "w", encoding="utf-8") as f:
            f.write(yt_combined)
        files_written["youtube"] = str(yt_combined_file)

        yt_title_file = self.pub_dir / "youtube_title.txt"
        with open(yt_title_file, "w", encoding="utf-8") as f:
            f.write(bundle.youtube.title.strip() + "\n")
        files_written["youtube_title"] = str(yt_title_file)

        yt_desc_file = self.pub_dir / "youtube_description.txt"
        with open(yt_desc_file, "w", encoding="utf-8") as f:
            f.write(bundle.youtube.description.strip() + "\n")
        files_written["youtube_description"] = str(yt_desc_file)

        # 2. Section 10 Platform Packages (structured JSON)
        ig_json_file = self.pub_dir / "instagram.json"
        with open(ig_json_file, "w", encoding="utf-8") as f:
            json.dump(bundle.instagram.to_platform_package(), f, indent=2, ensure_ascii=False)
        files_written["instagram_json"] = str(ig_json_file)

        tt_json_file = self.pub_dir / "tiktok.json"
        with open(tt_json_file, "w", encoding="utf-8") as f:
            json.dump(bundle.tiktok.to_platform_package(), f, indent=2, ensure_ascii=False)
        files_written["tiktok_json"] = str(tt_json_file)

        yt_json_file = self.pub_dir / "youtube-shorts.json"
        with open(yt_json_file, "w", encoding="utf-8") as f:
            json.dump(bundle.youtube.to_platform_package(), f, indent=2, ensure_ascii=False)
        files_written["youtube_json"] = str(yt_json_file)

        analysis_json_file = self.pub_dir / "caption-analysis.json"
        with open(analysis_json_file, "w", encoding="utf-8") as f:
            json.dump(bundle.to_analysis_dict(), f, indent=2, ensure_ascii=False)
        files_written["caption_analysis_json"] = str(analysis_json_file)

        # 3. Canonical captions.json
        json_data = bundle.to_json_dict()
        captions_json_file = self.pub_dir / "captions.json"
        with open(captions_json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        files_written["captions_json"] = str(captions_json_file)

        # Clean up legacy redundant files
        for leg_name in ["multi_platform_captions.json", "caption_validation_report.json"]:
            leg_path = self.pub_dir / leg_name
            if leg_path.exists():
                try:
                    leg_path.unlink()
                except OSError:
                    pass

        # 4. validation-report.json
        val_report = bundle.validation_report
        val_report_file = self.pub_dir / "validation-report.json"
        with open(val_report_file, "w", encoding="utf-8") as f:
            json.dump(val_report, f, indent=2, ensure_ascii=False)
        files_written["validation_report"] = str(val_report_file)

        return {
            "status": bundle.overall_status,
            "was_cached": was_cached,
            "output_directory": str(self.pub_dir),
            "files": files_written,
            "bundle": bundle
        }


def generate_captions_for_episode(
    episode_slug: str,
    force: bool = False,
    platform: Optional[str] = None
) -> Tuple[bool, Dict[str, Any], List[str]]:
    """Public helper API for pipeline and external integration."""
    try:
        engine = CaptionEngine(episode_slug)
        result = engine.save_deliverables(force=force, platform=platform)
        ok = result["status"] == "READY"
        messages = [
            f"Overall Status: {result['status']} (Cached: {result['was_cached']})",
            f"Output Directory: {result['output_directory']}"
        ]
        for k, v in result["files"].items():
            messages.append(f"Generated {k}: {v}")
        return ok, result, messages
    except Exception as e:
        return False, {}, [f"Caption generation failed: {e}"]
