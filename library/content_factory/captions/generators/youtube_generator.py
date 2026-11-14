"""
YouTube Shorts Metadata Generator adhering strictly to Platform-Specific Viral Caption & Retention rules:
- Dedicated Shorts Title (reason to watch, primary searchable keyword, no caps spam, 0-2 emojis)
- Dedicated Alternative Title
- Informative Description (overview without spoiling ending, Subscribe CTA)
- shorts_hashtags (2-3 relevant tags including #Shorts)
- shorts_search_keywords (high-intent SEO terms)
- shorts_pinned_comment (community engagement trigger)
- 100-pt rubric evaluation & scoring
"""

import os
import re
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from .base_generator import BaseCaptionGenerator
from ..hashtag_intelligence import HashtagIntelligence
from ..schemas.caption_schema import CaptionInput, YouTubeCaptionOutput
from ..validators.composite_validator import CompositeValidator
from ..retention_engine import RetentionEngine, NarrativeDossier
from ..scoring_system import CaptionScoringSystem


class YouTubeCaptionGenerator(BaseCaptionGenerator):
    """Generates SEO-optimized YouTube Shorts Title, Description, Keywords, and Pinned Comment."""

    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        """Loads externalized platform config if present."""
        cfg_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "config" / "platforms" / "youtube-shorts.json"
        if cfg_path.exists():
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "platform_recommendations": {
                "recommended_title_range": [40, 80],
                "recommended_description_range": [100, 500]
            }
        }

    @classmethod
    def generate_all_title_candidates(cls, input_data: CaptionInput, dossier: NarrativeDossier) -> List[str]:
        """
        Synthesizes multiple diverse title candidates optimized for YouTube Shorts click-through.
        Avoids awkward brackets, truncations, and artificial filler prefixes.
        """
        clean_title = input_data.title.strip().rstrip("?!. ")
        clean_topic = cls.clean_topic_phrase(clean_title)
        slug = (input_data.slug or "").lower().strip()

        t_candidates = []

        # 2. Cover title if available & punchy
        if input_data.cover_title and len(input_data.cover_title) >= 10:
            cov = input_data.cover_title.strip()
            cov_clean = re.sub(r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\u2300-\u23ff\u2b50?!. ]+$", "", cov).strip()
            if 40 <= len(cov_clean) <= 75:
                t_candidates.append(f"{cov_clean} 🔬")
            elif len(cov_clean) < 40 and clean_topic:
                t_candidates.append(f"{cov_clean}: Rahasia {clean_topic[:35]}! 🔬")

        # 3. Direct title candidate with proper emoji
        if 40 <= len(clean_title) <= 80:
            candidate_base = clean_title if any(e in clean_title for e in ["🔬", "🧠", "✨", "❗", "🚢", "☄️"]) else f"{clean_title} 🔬"
            t_candidates.append(candidate_base)

        # 4. Clean Curiosity Question (No ugly brackets!)
        if clean_title.lower().startswith(("bagaimana jika", "gimana kalau", "apa jadinya", "kalau", "jika")):
            t_candidates.append(f"Gimana Jadinya Kalau {clean_topic[:48]}?! 🔬")
        else:
            t_candidates.append(f"Kenapa Bisa Begini? Rahasia {clean_topic[:45]}! 🔬")
            t_candidates.append(f"Misteri {clean_topic[:45]} Terungkap! 🔬")

        # 5. Surprising Discovery Angle
        t_candidates.append(f"Fakta di Balik {clean_topic[:45]} yang Jarang Diketahui! 🔬")

        # Deduplicate preserving order
        seen = set()
        deduped = []
        for c in t_candidates:
            clean_c = c.strip()[:95]
            if clean_c and clean_c not in seen:
                seen.add(clean_c)
                deduped.append(clean_c)
        return deduped

    @classmethod
    def generate_title(cls, input_data: CaptionInput, attempt: int = 0) -> str:
        """Backward-compatible helper returning a title candidate by attempt index."""
        ep_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "episodes" / input_data.slug if input_data.slug else Path(".")
        dossier = RetentionEngine.analyze_episode(ep_dir, input_data.slug)
        candidates = cls.generate_all_title_candidates(input_data, dossier)
        if candidates:
            idx = attempt % len(candidates)
            return candidates[idx]
        return f"Misteri {input_data.title[:45]} Terungkap! 🔬"

    @classmethod
    def generate_titles(cls, input_data: CaptionInput, dossier: NarrativeDossier) -> Tuple[str, str]:
        """
        Synthesizes (primary_title, alternative_title) optimized for YouTube Shorts click-through.
        """
        candidates = cls.generate_all_title_candidates(input_data, dossier)
        primary = candidates[0] if candidates else f"Misteri {input_data.title[:45]} Terungkap! 🔬"
        alternative = candidates[1] if len(candidates) > 1 else f"Rahasia Sains: {input_data.title[:45]}?! 🔬"
        return primary, alternative

    @classmethod
    def generate_description(cls, input_data: CaptionInput, dossier: NarrativeDossier, attempt: int = 0) -> str:
        """Synthesizes YouTube Shorts description (100-500 chars)."""
        hashtags = HashtagIntelligence.generate_for_youtube(input_data)
        tags_str = " ".join(hashtags[:3])
        cta = (
            f"🔔 Subscribe {input_data.channel_name} untuk fakta sains & sejarah seru setiap minggu, "
            f"dan share ke temanmu!"
        )

        statement = cls.generate_informative_statement(input_data, max_chars=280 if attempt == 0 else 200)

        paragraphs = [
            statement,
            cta,
            tags_str
        ]

        desc = "\n\n".join(p.strip() for p in paragraphs if p.strip()).strip()
        if len(desc) > 490:
            statement_compact = cls.generate_informative_statement(input_data, max_chars=200)
            paragraphs = [
                statement_compact,
                cta,
                tags_str
            ]
            desc = "\n\n".join(p.strip() for p in paragraphs if p.strip()).strip()

        return desc

    @classmethod
    def generate_pinned_comment(cls, input_data: CaptionInput, dossier: NarrativeDossier) -> str:
        """Generates community discussion prompt for pinned comment."""
        clean_topic = re.sub(r"^(kenapa|mengapa|bagaimana|gimana)\s+", "", input_data.title or input_data.topic, flags=re.IGNORECASE).strip()
        question = cls.get_engagement_question(input_data)
        if question and len(question) > 15:
            return f"{question} Tulis pendapatmu di kolom komentar ya! 👇🐱"
        return f"Menu atau fakta apa seputar {clean_topic.lower()} yang paling mengejutkan buat kamu? Tulis di kolom komentar! 👇🐱"

    @classmethod
    def generate_search_keywords(cls, input_data: CaptionInput, dossier: NarrativeDossier) -> List[str]:
        """Derives 8-12 high-intent search keywords for YouTube indexing."""
        clean_topic = re.sub(r"[:\?!]", "", input_data.topic or input_data.title).lower().strip()
        clean_core = re.sub(r"^(sains di balik|rahasia di balik|fakta di balik|misteri di balik|kenapa|mengapa|bagaimana|gimana)\s+", "", clean_topic, flags=re.IGNORECASE).strip()
        words = [w for w in re.findall(r"[a-zA-Z0-9]+", clean_core) if len(w) >= 3 and w not in {"dan", "yang", "saat", "pada", "pasca", "buat", "bisa", "kita"}]
        
        keywords = [clean_topic]
        if clean_core and clean_core != clean_topic:
            keywords.append(clean_core)
        if len(words) >= 2:
            keywords.append(f"{words[0]} {words[1]}")
            if len(words) >= 3:
                keywords.append(f"{words[0]} {words[1]} {words[2]}")
        
        core_phrase = " ".join(words[:2]) if len(words) >= 2 else (words[0] if words else clean_core)
        keywords.extend([
            f"sains {core_phrase}",
            f"rahasia {core_phrase}",
            f"edukasi {input_data.content_category}",
            "meowndr",
            "fakta sains",
            "edukasi sains",
            "animasi papercraft",
            "sains populer"
        ])

        seen = set()
        deduped = []
        for kw in keywords:
            norm = kw.strip().lower()
            if norm and norm not in seen:
                seen.add(norm)
                deduped.append(kw.strip())
        return deduped[:12]

    @classmethod
    def generate_validated(cls, input_data: CaptionInput, max_attempts: int = 3) -> YouTubeCaptionOutput:
        """
        Generates scored, retention-aligned YouTube Shorts metadata package.
        """
        ep_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "episodes" / input_data.slug if input_data.slug else Path(".")
        dossier = RetentionEngine.analyze_episode(ep_dir, input_data.slug)

        candidates = cls.generate_all_title_candidates(input_data, dossier)
        description = cls.generate_description(input_data, dossier, attempt=0)
        hashtags = HashtagIntelligence.generate_for_youtube(input_data)
        search_kws = cls.generate_search_keywords(input_data, dossier)
        pinned_comment = cls.generate_pinned_comment(input_data, dossier)

        consistency = RetentionEngine.audit_consistency(description, dossier)

        # Score and rank all title candidates
        scored_titles = []
        for cand in candidates:
            sc = CaptionScoringSystem.evaluate_youtube(cand, description, input_data, dossier, consistency)
            scored_titles.append((sc.total_score, sc, cand))

        scored_titles.sort(key=lambda x: x[0], reverse=True)
        best_score_val, score, primary_title = scored_titles[0]
        alt_title = scored_titles[1][2] if len(scored_titles) > 1 else candidates[-1]

        # Retry loop if score < 85 or length invalid
        if (not score.passed or len(description) > 500) and max_attempts > 1:
            desc_retry = cls.generate_description(input_data, dossier, attempt=1)
            c_retry = RetentionEngine.audit_consistency(desc_retry, dossier)
            s_retry = CaptionScoringSystem.evaluate_youtube(primary_title, desc_retry, input_data, dossier, c_retry)
            if s_retry.total_score >= score.total_score:
                description = desc_retry
                score = s_retry

        is_valid, errors, warnings = CompositeValidator.validate_youtube_bundle(
            primary_title, description, input_data
        )
        status = "READY" if (score.passed and is_valid and len(description) <= 500) else "NEEDS_REVIEW"

        return YouTubeCaptionOutput(
            title=primary_title,
            description=description,
            hashtags=hashtags,
            search_keywords=search_kws,
            pinned_comment=pinned_comment,
            alternative_title=alt_title,
            title_character_count=len(primary_title),
            description_character_count=len(description),
            quality_score=score.total_score,
            score_breakdown=score.to_dict(),
            status=status,
            validation_errors=errors,
            validation_warnings=warnings
        )
