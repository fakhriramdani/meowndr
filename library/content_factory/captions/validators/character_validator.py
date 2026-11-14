"""
Character count validator for Instagram Reels, TikTok, and YouTube Shorts.
Enforces platform hard limits and recommended length targets.
Never allows silent truncation.
"""

from typing import Tuple, List, Dict, Any


class CharacterValidator:
    """Enforces strict platform character limits and optimal ranges."""

    # Instagram Reels
    IG_HARD_LIMIT = 2200
    IG_MIN_RECOMMENDED = 100
    IG_MAX_RECOMMENDED = 500

    # TikTok
    TT_HARD_LIMIT = 2200
    TT_MIN_RECOMMENDED = 50
    TT_MAX_RECOMMENDED = 300

    # YouTube Shorts
    YT_TITLE_HARD_LIMIT = 100
    YT_TITLE_MIN_RECOMMENDED = 40
    YT_TITLE_MAX_RECOMMENDED = 80

    YT_DESC_HARD_LIMIT = 5000
    YT_DESC_MIN_RECOMMENDED = 100
    YT_DESC_MAX_RECOMMENDED = 500

    @classmethod
    def validate_instagram(cls, caption: str) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []
        char_count = len(caption)

        if char_count == 0:
            errors.append("Instagram caption cannot be empty.")
            return False, errors, warnings

        if char_count > cls.IG_HARD_LIMIT:
            errors.append(f"Instagram caption exceeds hard limit of {cls.IG_HARD_LIMIT} chars (current: {char_count}).")
        elif char_count < cls.IG_MIN_RECOMMENDED:
            warnings.append(f"Instagram caption is below recommended minimum {cls.IG_MIN_RECOMMENDED} chars (current: {char_count}).")
        elif char_count > cls.IG_MAX_RECOMMENDED:
            warnings.append(f"Instagram caption is above recommended {cls.IG_MAX_RECOMMENDED} chars (current: {char_count}, hard limit 2200).")

        return len(errors) == 0, errors, warnings

    @classmethod
    def validate_tiktok(cls, caption: str) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []
        char_count = len(caption)

        if char_count == 0:
            errors.append("TikTok caption cannot be empty.")
            return False, errors, warnings

        if char_count > cls.TT_HARD_LIMIT:
            errors.append(f"TikTok caption exceeds hard limit of {cls.TT_HARD_LIMIT} chars (current: {char_count}).")
        elif char_count < cls.TT_MIN_RECOMMENDED:
            warnings.append(f"TikTok caption is below recommended minimum {cls.TT_MIN_RECOMMENDED} chars (current: {char_count}).")
        elif char_count > cls.TT_MAX_RECOMMENDED:
            warnings.append(f"TikTok caption is above recommended {cls.TT_MAX_RECOMMENDED} chars (current: {char_count}, hard limit 2200).")

        return len(errors) == 0, errors, warnings

    @classmethod
    def validate_youtube_title(cls, title: str) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []
        t_len = len(title.strip())

        if t_len == 0:
            errors.append("YouTube Shorts title cannot be empty.")
            return False, errors, warnings

        if t_len > cls.YT_TITLE_HARD_LIMIT:
            errors.append(f"YouTube title exceeds hard limit of {cls.YT_TITLE_HARD_LIMIT} chars (current: {t_len}).")
        elif t_len < cls.YT_TITLE_MIN_RECOMMENDED:
            warnings.append(f"YouTube title is below recommended {cls.YT_TITLE_MIN_RECOMMENDED} chars (current: {t_len}).")
        elif t_len > cls.YT_TITLE_MAX_RECOMMENDED:
            warnings.append(f"YouTube title is above recommended {cls.YT_TITLE_MAX_RECOMMENDED} chars (current: {t_len}, hard limit 100).")

        return len(errors) == 0, errors, warnings

    @classmethod
    def validate_youtube_description(cls, description: str) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []
        d_len = len(description.strip())

        if d_len == 0:
            errors.append("YouTube Shorts description cannot be empty.")
            return False, errors, warnings

        if d_len > cls.YT_DESC_HARD_LIMIT:
            errors.append(f"YouTube description exceeds hard limit of {cls.YT_DESC_HARD_LIMIT} chars (current: {d_len}).")
        elif d_len < cls.YT_DESC_MIN_RECOMMENDED:
            warnings.append(f"YouTube description is below recommended {cls.YT_DESC_MIN_RECOMMENDED} chars (current: {d_len}).")
        elif d_len > cls.YT_DESC_MAX_RECOMMENDED:
            warnings.append(f"YouTube description is above recommended {cls.YT_DESC_MAX_RECOMMENDED} chars (current: {d_len}, hard limit 5000).")

        return len(errors) == 0, errors, warnings
