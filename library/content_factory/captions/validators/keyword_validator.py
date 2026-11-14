"""
Keyword validator for multi-platform caption generation.
Verifies natural placement of primary and secondary keywords and flags keyword stuffing.
"""

import re
from typing import List, Tuple, Dict, Any


class KeywordValidator:
    """Validates topic keywords integration and natural language flow."""

    @staticmethod
    def normalize_term(term: str) -> str:
        return re.sub(r"[^\w\s]", "", term).lower().strip()

    @classmethod
    def find_keyword_presence(cls, text: str, keywords: List[str]) -> List[str]:
        """Returns list of keywords that appear in text (case-insensitive, whole or stem match)."""
        text_lower = text.lower()
        matched = []
        for kw in keywords:
            kw_norm = cls.normalize_term(kw)
            if not kw_norm:
                continue
            # Split into individual words if multi-word keyword
            words = [w for w in kw_norm.split() if len(w) >= 3]
            if not words:
                continue
            # If multi-word phrase is directly in text OR major words appear
            if kw_norm in text_lower or any(w in text_lower for w in words):
                matched.append(kw)
        return matched

    @classmethod
    def check_keyword_stuffing(cls, text: str, keyword: str, threshold: int = 3) -> bool:
        """Checks if a single keyword repeats unnaturally often."""
        kw_norm = cls.normalize_term(keyword)
        if not kw_norm:
            return False
        effective_threshold = max(threshold, len(text) // 100)
        count = len(re.findall(rf"\b{re.escape(kw_norm)}\b", text.lower()))
        return count > effective_threshold

    @classmethod
    def validate_keywords(cls, platform: str, text: str, primary_keywords: List[str]) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []

        if not primary_keywords:
            return True, errors, warnings

        matched = cls.find_keyword_presence(text, primary_keywords)
        if not matched:
            warnings.append(
                f"[{platform}] Could not find strong match for primary keywords: {', '.join(primary_keywords[:3])}"
            )

        # Check for stuffing
        for kw in primary_keywords:
            if cls.check_keyword_stuffing(text, kw):
                errors.append(f"[{platform}] Keyword stuffing detected for keyword '{kw}'.")

        return len(errors) == 0, errors, warnings
