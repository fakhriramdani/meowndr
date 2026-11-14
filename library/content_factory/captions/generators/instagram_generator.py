"""
Instagram Reels Caption Generator adhering strictly to Platform-Specific Viral Caption & Retention rules:
- Search discoverability & natural keyword placement near opening
- Shares and saves focus
- Curiosity-driven opening without generic intros
- Complementary insight without spoiling the final video revelation
- Clear paragraph breaks, 0-3 emojis
- 3-5 relevant, non-spam hashtags
- Dedicated alternative caption generation
"""

import os
import re
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from .base_generator import BaseCaptionGenerator
from ..hashtag_intelligence import HashtagIntelligence
from ..schemas.caption_schema import CaptionInput, InstagramCaptionOutput
from ..validators.composite_validator import CompositeValidator
from ..retention_engine import RetentionEngine, NarrativeDossier
from ..scoring_system import CaptionScoringSystem


class InstagramCaptionGenerator(BaseCaptionGenerator):
    """Generates retention-optimized, shareable Instagram Reels captions."""

    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        """Loads externalized platform config if present."""
        cfg_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "config" / "platforms" / "instagram.json"
        if cfg_path.exists():
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "platform_recommendations": {
                "recommended_character_range": [100, 500],
                "recommended_hashtags_range": [3, 5]
            }
        }

    @classmethod
    def generate(cls, input_data: CaptionInput, attempt: int = 0) -> str:
        """Backward-compatible helper returning a caption candidate by attempt index."""
        ep_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "episodes" / input_data.slug if input_data.slug else Path(".")
        dossier = RetentionEngine.analyze_episode(ep_dir, input_data.slug)
        variants = ["curiosity_insight", "counter_intuitive", "concise_takeaway"]
        v_type = variants[attempt % len(variants)]
        cap, _, _ = cls.generate_candidate(input_data, dossier, v_type)
        return cap

    @classmethod
    def generate_candidate(
        cls,
        input_data: CaptionInput,
        dossier: NarrativeDossier,
        variant_type: str = "curiosity_insight"
    ) -> Tuple[str, str, str]:
        """
        Synthesizes a specific caption variant.
        Returns (full_caption, opening_hook, cta).
        """
        hashtags = HashtagIntelligence.generate_for_instagram(input_data)
        tags_str = " ".join(hashtags[:5])
        question = cls.get_engagement_question(input_data)
        if not question.endswith("?"):
            question = f"{question}?"

        clean_topic = cls.clean_topic_phrase(input_data.title or input_data.topic)
        statement = cls.generate_informative_statement(input_data, max_chars=260)
        cta = "💡 Simpan postingan ini biar nggak lupa & share ke temanmu!"

        if variant_type == "curiosity_insight":
            # Primary Variant: High-curiosity informative statement + interactive question + Save/Share CTA
            paragraphs = [
                statement,
                f"{question} Tulis di kolom komentar ya! 👇",
                cta,
                tags_str
            ]
        elif variant_type == "counter_intuitive":
            # Alternative Variant 1: Counter-intuitive angle & pattern interrupt
            hook_line = f"Banyak yang mengira rahasia {clean_topic.lower()} itu sederhana, padahal faktanya jauh lebih mengejutkan! ✨"
            paragraphs = [
                hook_line,
                statement,
                f"{question} Tulis di kolom komentar ya! 👇",
                "💡 Simpan postingan ini & share ke temanmu!",
                tags_str
            ]
        else:
            # Alternative Variant 2: Concise informative flow
            paragraphs = [
                statement,
                f"{question} Tulis di kolom komentar ya! 👇",
                cta,
                tags_str
            ]

        caption = "\n\n".join(p.strip() for p in paragraphs if p and p.strip()).strip()

        # Enforce character budget <= 495 chars without breaking sentences or narrative integrity
        if len(caption) > 495:
            # 1. Compact question
            clean_q = re.sub(r"^(kalau skenario ini beneran terjadi,?\s*|kira-kira\s*)", "", question, flags=re.IGNORECASE).strip()
            clean_q = clean_q[0].upper() + clean_q[1:] if clean_q else question
            q_idx = 2 if variant_type == "counter_intuitive" else 1
            paragraphs[q_idx] = f"{clean_q} Komen di bawah ya! 👇"
            caption = "\n\n".join(p.strip() for p in paragraphs if p and p.strip()).strip()

        if len(caption) > 495:
            # 2. Compact CTA
            cta_idx = len(paragraphs) - 2
            paragraphs[cta_idx] = "💡 Simpan postingan ini & share ke temanmu!"
            caption = "\n\n".join(p.strip() for p in paragraphs if p and p.strip()).strip()

        if len(caption) > 495 and len(hashtags) > 3:
            # 3. Compact hashtags (top 3 tags)
            paragraphs[-1] = " ".join(hashtags[:3])
            caption = "\n\n".join(p.strip() for p in paragraphs if p and p.strip()).strip()

        if len(caption) > 495:
            # 4. Streamline statement to compact limit (180 chars) preserving complete sentences
            stmt_idx = 1 if variant_type == "counter_intuitive" else 0
            paragraphs[stmt_idx] = cls.generate_informative_statement(input_data, max_chars=180)
            caption = "\n\n".join(p.strip() for p in paragraphs if p and p.strip()).strip()

        opening_hook = paragraphs[0]
        return caption, opening_hook, cta

    @classmethod
    def generate_validated(cls, input_data: CaptionInput, max_attempts: int = 3) -> InstagramCaptionOutput:
        """
        Generates scored, retention-aligned Instagram Reels package with primary & alternative captions.
        """
        # 1. Extract narrative dossier from episode context
        ep_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "episodes" / input_data.slug if input_data.slug else Path(".")
        dossier = RetentionEngine.analyze_episode(ep_dir, input_data.slug)

        hashtags = HashtagIntelligence.generate_for_instagram(input_data)
        primary_kws = input_data.main_keywords if input_data.main_keywords else dossier.searchable_keywords

        # 2. Generate Primary candidate
        primary_cap, primary_hook, primary_cta = cls.generate_candidate(input_data, dossier, "curiosity_insight")
        consistency_prim = RetentionEngine.audit_consistency(primary_cap, dossier)
        score_prim = CaptionScoringSystem.evaluate_instagram(primary_cap, input_data, dossier, consistency_prim)

        # 3. Generate Alternative candidate
        alt_cap, alt_hook, alt_cta = cls.generate_candidate(input_data, dossier, "counter_intuitive")
        consistency_alt = RetentionEngine.audit_consistency(alt_cap, dossier)
        score_alt = CaptionScoringSystem.evaluate_instagram(alt_cap, input_data, dossier, consistency_alt)

        # 4. Fallback retry if primary score < 85
        best_cap = primary_cap
        best_hook = primary_hook
        best_cta = primary_cta
        best_score = score_prim
        chosen_alt = alt_cap

        if not score_prim.passed and score_alt.total_score > score_prim.total_score:
            # Swap if alternative scored higher
            best_cap, chosen_alt = alt_cap, primary_cap
            best_hook = alt_hook
            best_cta = alt_cta
            best_score = score_alt

        if not best_score.passed and max_attempts > 2:
            # Attempt compact variant
            alt2_cap, alt2_hook, alt2_cta = cls.generate_candidate(input_data, dossier, "concise_takeaway")
            c_audit = RetentionEngine.audit_consistency(alt2_cap, dossier)
            s_audit = CaptionScoringSystem.evaluate_instagram(alt2_cap, input_data, dossier, c_audit)
            if s_audit.total_score > best_score.total_score:
                best_cap = alt2_cap
                best_hook = alt2_hook
                best_cta = alt2_cta
                best_score = s_audit

        # Validate with CompositeValidator for platform hard constraints
        is_valid, errors, warnings = CompositeValidator.validate_instagram_bundle(best_cap, input_data)
        status = "READY" if (best_score.passed and is_valid) else "NEEDS_REVIEW"

        return InstagramCaptionOutput(
            caption=best_cap,
            opening_hook=best_hook,
            keywords=primary_kws[:5],
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
