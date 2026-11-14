"""
Composite Validator coordinating all multi-platform checks:
characters, hashtags, keywords, content, and cross-platform uniqueness.
"""

import re
from typing import Dict, Any, Tuple, List, Optional
from .character_validator import CharacterValidator
from .hashtag_validator import HashtagValidator
from .keyword_validator import KeywordValidator
from .content_validator import ContentValidator
from ..schemas.caption_schema import (
    CaptionInput,
    InstagramCaptionOutput,
    TikTokCaptionOutput,
    YouTubeCaptionOutput
)


class CompositeValidator:
    """Orchestrates comprehensive multi-platform caption verification."""

    @staticmethod
    def jaccard_similarity(text1: str, text2: str) -> float:
        """Computes Jaccard word similarity between two texts."""
        w1 = set(re.findall(r"\w+", text1.lower()))
        w2 = set(re.findall(r"\w+", text2.lower()))
        if not w1 or not w2:
            return 0.0
        intersection = len(w1.intersection(w2))
        union = len(w1.union(w2))
        return intersection / union if union > 0 else 0.0

    @classmethod
    def validate_instagram_bundle(cls, caption: str, input_data: CaptionInput) -> Tuple[bool, List[str], List[str]]:
        all_errors = []
        all_warnings = []

        # 1. Character limits
        c_ok, c_err, c_warn = CharacterValidator.validate_instagram(caption)
        all_errors.extend(c_err)
        all_warnings.extend(c_warn)

        # 2. Hashtags
        tags = HashtagValidator.extract_hashtags(caption)
        h_ok, h_err, h_warn = HashtagValidator.validate_instagram(tags)
        all_errors.extend(h_err)
        all_warnings.extend(h_warn)

        # 3. Content rules
        ct_ok, ct_err, ct_warn = ContentValidator.validate_instagram_content(caption)
        all_errors.extend(ct_err)
        all_warnings.extend(ct_warn)

        # 4. Keywords
        k_ok, k_err, k_warn = KeywordValidator.validate_keywords("Instagram", caption, input_data.main_keywords)
        all_errors.extend(k_err)
        all_warnings.extend(k_warn)

        return len(all_errors) == 0, all_errors, all_warnings

    @classmethod
    def validate_tiktok_bundle(cls, caption: str, input_data: CaptionInput) -> Tuple[bool, List[str], List[str]]:
        all_errors = []
        all_warnings = []

        # 1. Character limits
        c_ok, c_err, c_warn = CharacterValidator.validate_tiktok(caption)
        all_errors.extend(c_err)
        all_warnings.extend(c_warn)

        # 2. Hashtags
        tags = HashtagValidator.extract_hashtags(caption)
        h_ok, h_err, h_warn = HashtagValidator.validate_tiktok(tags)
        all_errors.extend(h_err)
        all_warnings.extend(h_warn)

        # 3. Content rules
        ct_ok, ct_err, ct_warn = ContentValidator.validate_tiktok_content(caption)
        all_errors.extend(ct_err)
        all_warnings.extend(ct_warn)

        # 4. Keywords
        k_ok, k_err, k_warn = KeywordValidator.validate_keywords("TikTok", caption, input_data.main_keywords)
        all_errors.extend(k_err)
        all_warnings.extend(k_warn)

        return len(all_errors) == 0, all_errors, all_warnings

    @classmethod
    def validate_youtube_bundle(cls, title: str, description: str, input_data: CaptionInput) -> Tuple[bool, List[str], List[str]]:
        all_errors = []
        all_warnings = []

        # 1. Title character limits
        t_ok, t_err, t_warn = CharacterValidator.validate_youtube_title(title)
        all_errors.extend(t_err)
        all_warnings.extend(t_warn)

        # 2. Description character limits
        d_ok, d_err, d_warn = CharacterValidator.validate_youtube_description(description)
        all_errors.extend(d_err)
        all_warnings.extend(d_warn)

        # 3. Description hashtags
        tags = HashtagValidator.extract_hashtags(description)
        h_ok, h_err, h_warn = HashtagValidator.validate_youtube(tags)
        all_errors.extend(h_err)
        all_warnings.extend(h_warn)

        # 4. Content rules
        ct_ok, ct_err, ct_warn = ContentValidator.validate_youtube_content(title, description)
        all_errors.extend(ct_err)
        all_warnings.extend(ct_warn)

        # 5. Keywords in title and description
        kt_ok, kt_err, kt_warn = KeywordValidator.validate_keywords("YouTube Title", title, input_data.main_keywords)
        all_errors.extend(kt_err)
        all_warnings.extend(kt_warn)

        kd_ok, kd_err, kd_warn = KeywordValidator.validate_keywords("YouTube Description", description, input_data.main_keywords)
        all_errors.extend(kd_err)
        all_warnings.extend(kd_warn)

        return len(all_errors) == 0, all_errors, all_warnings

    @classmethod
    def validate_cross_platform_uniqueness(cls, ig: str, tt: str, yt_desc: str) -> Tuple[bool, List[str], Dict[str, float]]:
        errors = []
        sim_ig_tt = cls.jaccard_similarity(ig, tt)
        sim_ig_yt = cls.jaccard_similarity(ig, yt_desc)
        sim_tt_yt = cls.jaccard_similarity(tt, yt_desc)

        metrics = {
            "similarity_ig_tt": round(sim_ig_tt, 3),
            "similarity_ig_yt": round(sim_ig_yt, 3),
            "similarity_tt_yt": round(sim_tt_yt, 3)
        }

        if sim_ig_tt > 0.85:
            errors.append(f"Instagram and TikTok captions are too similar (Jaccard: {sim_ig_tt:.2f}).")
        if sim_ig_yt > 0.85:
            errors.append(f"Instagram and YouTube descriptions are too similar (Jaccard: {sim_ig_yt:.2f}).")
        if sim_tt_yt > 0.85:
            errors.append(f"TikTok and YouTube descriptions are too similar (Jaccard: {sim_tt_yt:.2f}).")

        return len(errors) == 0, errors, metrics
