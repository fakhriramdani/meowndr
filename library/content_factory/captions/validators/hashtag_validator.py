"""
Hashtag validator for Instagram Reels, TikTok, and YouTube Shorts.
Enforces count constraints, syntax, deduplication, and banned generic spam tag rules.
"""

import re
from typing import List, Tuple, Set


class HashtagValidator:
    """Enforces hashtag count, relevance, and generic spam bans."""

    BANNED_SPAM_TAGS = {
        "#fyp", "#foryou", "#foryoupage", "#viral", "#trend", "#trending",
        "#explore", "#likeforlike", "#followforfollow", "#xyzbca"
    }

    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extracts unique hashtags from text maintaining original casing and order."""
        matches = re.findall(r"#([a-zA-Z0-9_]+)", text)
        deduped = []
        seen = set()
        for tag in matches:
            norm = tag.lower()
            if norm not in seen:
                seen.add(norm)
                deduped.append(f"#{tag}")
        return deduped

    @classmethod
    def check_banned_tags(cls, tags: List[str]) -> List[str]:
        """Finds any prohibited viral spam hashtags."""
        violations = []
        for tag in tags:
            if tag.lower() in cls.BANNED_SPAM_TAGS:
                violations.append(tag)
        return violations

    @classmethod
    def validate_instagram(cls, tags: List[str]) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []
        count = len(tags)

        if count == 0:
            errors.append("Instagram caption requires at least 1 relevant hashtag.")
        elif count > 5:
            errors.append(f"Instagram caption exceeds maximum limit of 5 hashtags (found {count}).")
        elif count < 3:
            warnings.append(f"Instagram caption has {count} hashtags (recommended: 3-5).")

        # Banned tags
        banned = cls.check_banned_tags(tags)
        if banned:
            errors.append(f"Instagram caption contains banned generic spam hashtags: {', '.join(banned)}")

        # Deduplication check
        lower_tags = [t.lower() for t in tags]
        if len(lower_tags) != len(set(lower_tags)):
            errors.append("Duplicate hashtags detected in Instagram caption.")

        return len(errors) == 0, errors, warnings

    @classmethod
    def validate_tiktok(cls, tags: List[str]) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []
        count = len(tags)

        if count == 0:
            errors.append("TikTok caption requires at least 1 relevant hashtag.")
        elif count > 5:
            errors.append(f"TikTok caption exceeds recommended maximum of 5 hashtags (found {count}).")
        elif count not in (2, 3):
            warnings.append(f"TikTok caption has {count} hashtags (recommended: 2-3).")

        # Banned tags
        banned = cls.check_banned_tags(tags)
        if banned:
            errors.append(f"TikTok caption contains banned generic spam hashtags: {', '.join(banned)}")

        # Deduplication check
        lower_tags = [t.lower() for t in tags]
        if len(lower_tags) != len(set(lower_tags)):
            errors.append("Duplicate hashtags detected in TikTok caption.")

        return len(errors) == 0, errors, warnings

    @classmethod
    def validate_youtube(cls, tags: List[str]) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []
        count = len(tags)

        if count < 1:
            errors.append("YouTube description requires at least 1 hashtag.")
        elif count > 4:
            errors.append(f"YouTube description has too many hashtags ({count}, recommended 2-3).")
        elif count not in (2, 3):
            warnings.append(f"YouTube description has {count} hashtags (recommended: 2-3).")

        # Banned tags
        banned = cls.check_banned_tags(tags)
        if banned:
            errors.append(f"YouTube description contains banned generic spam hashtags: {', '.join(banned)}")

        # Deduplication check
        lower_tags = [t.lower() for t in tags]
        if len(lower_tags) != len(set(lower_tags)):
            errors.append("Duplicate hashtags detected in YouTube description.")

        return len(errors) == 0, errors, warnings
