"""
Content and editorial standard validator for multi-platform captions.
Verifies hooks, engagement prompts, CTAs, tone, emoji limits, and grounding.
"""

import re
from typing import List, Tuple, Dict, Any


class ContentValidator:
    """Validates platform-specific editorial standards and narrative components."""

    EMOJI_PATTERN = re.compile(
        r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\u2300-\u23ff\u2b50]",
        flags=re.UNICODE
    )

    @classmethod
    def count_emojis(cls, text: str) -> int:
        """Counts emojis in text."""
        return len(cls.EMOJI_PATTERN.findall(text))

    @classmethod
    def validate_instagram_content(cls, caption: str) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []
        lower = caption.lower()

        # 1. Opening hook check (first line / paragraph should not start with CTA)
        first_line = caption.strip().split("\n")[0]
        if len(first_line) < 15:
            errors.append("Instagram opening line is too short to be an effective hook.")

        # 2. Paragraph break check (Instagram captions need clean readability)
        if "\n" not in caption.strip() and len(caption) > 150:
            warnings.append("Instagram caption should use short paragraphs separated by line breaks.")

        # 3. Question / Engagement prompt
        if "?" not in caption:
            errors.append("Instagram caption must include an engaging question or discussion prompt ('?').")

        # 4. CTA check (Save, Share, or Follow)
        has_save = any(w in lower for w in ["simpan", "save"])
        has_share = any(w in lower for w in ["share", "bagikan"])
        has_follow = any(w in lower for w in ["follow", "ikuti"])
        if not (has_save or has_share or has_follow):
            errors.append("Instagram caption must include a Save, Share, or Follow CTA.")

        # 5. Emoji count check (0-3 recommended, error if > 3)
        emoji_count = cls.count_emojis(caption)
        if emoji_count > 3:
            errors.append(f"Instagram caption exceeds maximum 3 emojis (found {emoji_count}).")

        # 6. Excessively promotional tone check
        spam_words = ["diskon", "promo", "beli sekarang", "order sekarang", "link di bio murah"]
        if any(w in lower for w in spam_words):
            errors.append("Instagram caption contains prohibited overly promotional language.")

        return len(errors) == 0, errors, warnings

    @classmethod
    def validate_tiktok_content(cls, caption: str) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []
        lower = caption.lower()

        # 1. Hook / curiosity trigger check
        first_line = caption.strip().split("\n")[0]
        if len(first_line) < 10:
            errors.append("TikTok opening hook is too short.")

        # 2. Engagement question or CTA
        has_question = "?" in caption
        has_comment_cta = any(w in lower for w in ["komen", "komentar", "menurutmu", "pendapatmu", "ceritain", "tulis"])
        if not (has_question or has_comment_cta):
            errors.append("TikTok caption must include an engagement question or comment CTA.")

        # 3. Emoji count check (0-3 emojis)
        emoji_count = cls.count_emojis(caption)
        if emoji_count > 3:
            errors.append(f"TikTok caption exceeds maximum 3 emojis (found {emoji_count}).")

        # 4. Excessively formal language check
        overly_formal = ["dengan demikian", "maka dari itu", "sebagaimana kita ketahui bersama", "oleh karena itu"]
        if any(f in lower for f in overly_formal):
            warnings.append("TikTok caption contains overly formal phrasing; keep it conversational.")

        return len(errors) == 0, errors, warnings

    @classmethod
    def validate_youtube_content(cls, title: str, description: str) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []
        t_lower = title.lower()
        d_lower = description.lower()

        # 1. Title emoji check (0-2 emojis)
        title_emojis = cls.count_emojis(title)
        if title_emojis > 2:
            errors.append(f"YouTube title exceeds maximum 2 emojis (found {title_emojis}).")

        # 2. Description emoji check (0-3 emojis)
        desc_emojis = cls.count_emojis(description)
        if desc_emojis > 3:
            errors.append(f"YouTube description exceeds maximum 3 emojis (found {desc_emojis}).")

        # 3. Misleading clickbait check in title
        spam_caps = ["GILA LUAR BIASA BANGET", "JANGAN DITONTON KALAU", "MUSTAHIL BANGET"]
        if any(c.lower() in t_lower for c in spam_caps):
            warnings.append("YouTube title contains potentially sensationalist clickbait phrasing.")

        # 4. Subscribe CTA in description
        has_subscribe = any(w in d_lower for w in ["subscribe", "langganan"])
        if not has_subscribe:
            errors.append("YouTube description must include a Subscribe CTA.")

        return len(errors) == 0, errors, warnings
