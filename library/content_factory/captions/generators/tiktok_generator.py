"""
TikTok Caption Generator adhering strictly to Platform-Specific Viral Caption & Retention rules:
- High-energy, immediate curiosity opening
- TikTok SEO search intent integration
- Viewport readability (body text <= 165 chars, hard ceiling 220 chars)
- Fresh curiosity angle without repeating video hook verbatim
- Conversational comment/interaction CTA
- 2-3 specific, non-spam hashtags
- Generates primary & alternative caption packages with 100-pt scoring
"""

import os
import re
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from .base_generator import BaseCaptionGenerator
from ..hashtag_intelligence import HashtagIntelligence
from ..schemas.caption_schema import CaptionInput, TikTokCaptionOutput
from ..validators.composite_validator import CompositeValidator
from ..retention_engine import RetentionEngine, NarrativeDossier
from ..scoring_system import CaptionScoringSystem


class TikTokCaptionGenerator(BaseCaptionGenerator):
    """Generates punchy, search-optimized, retention-driven TikTok captions."""

    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        """Loads externalized platform config if present."""
        cfg_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "config" / "platforms" / "tiktok.json"
        if cfg_path.exists():
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "platform_recommendations": {
                "recommended_character_range": [50, 300],
                "target_body_length_before_truncation": 160
            }
        }

    @classmethod
    def generate(cls, input_data: CaptionInput, attempt: int = 0) -> str:
        """Backward-compatible helper returning a caption candidate by attempt index."""
        ep_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "episodes" / input_data.slug if input_data.slug else Path(".")
        dossier = RetentionEngine.analyze_episode(ep_dir, input_data.slug)
        variants = ["curiosity_hook", "surprising_fact", "open_loop"]
        v_type = variants[attempt % len(variants)]
        cap, _, _ = cls.generate_candidate(input_data, dossier, v_type)
        return cap

    @classmethod
    def generate_candidate(
        cls,
        input_data: CaptionInput,
        dossier: NarrativeDossier,
        variant_type: str = "curiosity_loop"
    ) -> Tuple[str, str, str]:
        """
        Synthesizes a punchy TikTok caption (body <= 160 chars recommended, hard limit 220).
        Returns (full_caption, opening_hook, cta).
        """
        hashtags = HashtagIntelligence.generate_for_tiktok(input_data)
        tags_str = " ".join(hashtags[:3])

        hook_text = cls.get_clean_hook(input_data)
        question = cls.get_engagement_question(input_data)
        
        if variant_type == "curiosity_loop":
            statement = f"{hook_text} {question}"
            cta = "Komen di bawah ya! 👇"
        elif variant_type == "open_loop":
            statement = f"{hook_text}"
            cta = "Tulis pendapatmu di komen ya! 👇"
        else:
            statement = f"{question}"
            cta = "Komen di bawah ya! 👇"

        has_comment_cta = any(w in statement.lower() for w in ["komen", "komentar", "tulis"])
        if not has_comment_cta:
            body = f"{statement} {cta}"
        else:
            body = statement
        body = re.sub(r"\s+", " ", body).strip()

        # Enforce mobile feed truncation ceiling (body <= 160) to prevent UI truncation warnings
        if len(body) > 160:
            target_cut = 160 - len(cta) - 2
            prefix_part = statement[:target_cut].rsplit(" ", 1)[0].rstrip(" ,.-?!")
            body = f"{prefix_part}! {cta}"

        if len(body) > 215:
            body = body[:210].rsplit(" ", 1)[0].rstrip(" ,;:") + "! 👇"

        caption = f"{body} {tags_str}".strip()
        opening_hook = statement[:45]
        return caption, opening_hook, cta

    @classmethod
    def generate_validated(cls, input_data: CaptionInput, max_attempts: int = 3) -> TikTokCaptionOutput:
        """
        Generates scored, retention-aligned TikTok package with primary & alternative captions.
        """
        ep_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "episodes" / input_data.slug if input_data.slug else Path(".")
        dossier = RetentionEngine.analyze_episode(ep_dir, input_data.slug)

        hashtags = HashtagIntelligence.generate_for_tiktok(input_data)
        primary_kws = input_data.main_keywords if input_data.main_keywords else dossier.searchable_keywords

        # 1. Primary candidate
        primary_cap, primary_hook, primary_cta = cls.generate_candidate(input_data, dossier, "curiosity_loop")
        consistency_prim = RetentionEngine.audit_consistency(primary_cap, dossier)
        score_prim = CaptionScoringSystem.evaluate_tiktok(primary_cap, input_data, dossier, consistency_prim)

        # 2. Alternative candidate
        alt_cap, alt_hook, alt_cta = cls.generate_candidate(input_data, dossier, "open_loop")
        consistency_alt = RetentionEngine.audit_consistency(alt_cap, dossier)
        score_alt = CaptionScoringSystem.evaluate_tiktok(alt_cap, input_data, dossier, consistency_alt)

        # 3. Best selection based on quality score
        best_cap = primary_cap
        best_hook = primary_hook
        best_cta = primary_cta
        best_score = score_prim
        chosen_alt = alt_cap

        if not score_prim.passed and score_alt.total_score > score_prim.total_score:
            best_cap, chosen_alt = alt_cap, primary_cap
            best_hook = alt_hook
            best_cta = alt_cta
            best_score = score_alt

        if not best_score.passed and max_attempts > 2:
            alt2_cap, alt2_hook, alt2_cta = cls.generate_candidate(input_data, dossier, "fact_trigger")
            c_audit = RetentionEngine.audit_consistency(alt2_cap, dossier)
            s_audit = CaptionScoringSystem.evaluate_tiktok(alt2_cap, input_data, dossier, c_audit)
            if s_audit.total_score > best_score.total_score:
                best_cap = alt2_cap
                best_hook = alt2_hook
                best_cta = alt2_cta
                best_score = s_audit

        # Hard constraints validation
        is_valid, errors, warnings = CompositeValidator.validate_tiktok_bundle(best_cap, input_data)
        status = "READY" if (best_score.passed and is_valid) else "NEEDS_REVIEW"

        return TikTokCaptionOutput(
            caption=best_cap,
            opening_hook=best_hook,
            keywords=primary_kws[:3],
            hashtags=hashtags,
            CTA=best_cta,
            alternative_caption=chosen_alt,
            character_count=len(best_cap),
            quality_score=best_score.total_score,
            score_breakdown=best_score.to_dict(),
            status=status,
            validation_errors=errors,
            validation_warnings=warnings
        )
