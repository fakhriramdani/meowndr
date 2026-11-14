"""
Caption Scoring and Quality Assurance System for @meowndr.
Evaluates multi-platform captions against a rigorous 100-point rubric:
  - Hook strength (20 pts)
  - Curiosity and watch intent (20 pts)
  - Platform-specific compliance (20 pts)
  - SEO and keyword relevance (15 pts)
  - Natural language quality (10 pts)
  - Engagement potential (10 pts)
  - Content accuracy (5 pts)
Minimum passing score: 85/100.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .retention_engine import NarrativeDossier, ConsistencyAuditResult, RetentionEngine
from .schemas.caption_schema import CaptionInput


@dataclass
class ScoreBreakdown:
    hook_strength: int = 0             # max 20
    curiosity_watch_intent: int = 0    # max 20
    platform_compliance: int = 0       # max 20
    seo_keyword_relevance: int = 0     # max 15
    natural_language: int = 0          # max 10
    engagement_potential: int = 0      # max 10
    content_accuracy: int = 0          # max 5
    total_score: int = 0               # max 100
    passed: bool = False               # total >= 85
    reasons: List[str] = field(default_factory=list)
    deductions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_score": self.total_score,
            "passed": self.passed,
            "breakdown": {
                "hook_strength": f"{self.hook_strength}/20",
                "curiosity_watch_intent": f"{self.curiosity_watch_intent}/20",
                "platform_compliance": f"{self.platform_compliance}/20",
                "seo_keyword_relevance": f"{self.seo_keyword_relevance}/15",
                "natural_language": f"{self.natural_language}/10",
                "engagement_potential": f"{self.engagement_potential}/10",
                "content_accuracy": f"{self.content_accuracy}/5"
            },
            "reasons": self.reasons,
            "deductions": self.deductions
        }


class CaptionScoringSystem:
    """Automated evaluator scoring captions out of 100 points."""

    PASSING_THRESHOLD = 85

    @classmethod
    def evaluate_instagram(
        cls,
        caption: str,
        input_data: CaptionInput,
        dossier: NarrativeDossier,
        consistency: ConsistencyAuditResult
    ) -> ScoreBreakdown:
        score = ScoreBreakdown()
        text = caption.strip()
        lower = text.lower()
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # 1. Hook Strength (20 pts)
        hook_pts = 0
        first_line = lines[0] if lines else ""
        if len(first_line) >= 15:
            hook_pts += 8
        hook_triggers = [
            "pernah", "kenapa", "mengapa", "tahukah", "rahasia", "fakta", "habis",
            "banyak", "keberadaan", "beda", "gimana", "kalau", "bayangkan",
            "skenario", "sensasi", "aroma", "upaya", "cahaya", "di balik", "ternyata"
        ]
        if any(w in first_line.lower() for w in hook_triggers):
            hook_pts += 6
        if not consistency.verbatim_repetition:
            hook_pts += 6
        else:
            score.deductions.append("Hook verbatim repeats video narration (-6 pts)")
        score.hook_strength = min(20, hook_pts)

        # 2. Curiosity & Watch Intent (20 pts)
        cur_pts = 0
        if consistency.curiosity_preserved:
            cur_pts += 10
        if not consistency.spoiler_detected:
            cur_pts += 10
        else:
            score.deductions.append("Spoiler detected: reveals full ending in caption (-10 pts)")
        score.curiosity_watch_intent = min(20, cur_pts)

        # 3. Platform Compliance (20 pts)
        comp_pts = 0
        c_len = len(text)
        if 100 <= c_len <= 500:
            comp_pts += 10
        elif c_len <= 800:
            comp_pts += 6
        else:
            score.deductions.append(f"Instagram caption length suboptimal: {c_len} chars")

        # Hashtags (3-5)
        tags = re.findall(r"#\w+", text)
        if 3 <= len(tags) <= 5:
            comp_pts += 5
        elif len(tags) > 5:
            score.deductions.append(f"Exceeds max 5 hashtags ({len(tags)} found) (-5 pts)")
        else:
            comp_pts += 2

        # Emojis (0-3)
        emoji_count = len(re.findall(r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\u2300-\u23ff\u2b50]", text))
        if emoji_count <= 3:
            comp_pts += 5
        else:
            score.deductions.append(f"Emoji count exceeds 3 ({emoji_count} found) (-5 pts)")
        score.platform_compliance = min(20, comp_pts)

        # 4. SEO & Keyword Relevance (15 pts)
        seo_pts = 0
        if consistency.keyword_aligned:
            seo_pts += 10
        if tags and not any(t.lower() in {"#fyp", "#viral", "#trend"} for t in tags):
            seo_pts += 5
        score.seo_keyword_relevance = min(15, seo_pts)

        # 5. Natural Language Quality (10 pts)
        nl_pts = 0
        # Check no dangling cuts
        if not text.endswith("...") and not "... 👇" in text:
            nl_pts += 5
        # Paragraph spacing for readability
        if "\n\n" in text:
            nl_pts += 5
        score.natural_language = min(10, nl_pts)

        # 6. Engagement Potential (10 pts)
        eng_pts = 0
        has_save_share = any(w in lower for w in ["simpan", "save", "share", "bagikan", "kirim"])
        if has_save_share:
            eng_pts += 6
        if "?" in text:
            eng_pts += 4
        score.engagement_potential = min(10, eng_pts)

        # 7. Content Accuracy (5 pts)
        acc_pts = 5 if not consistency.contradiction_detected else 0
        score.content_accuracy = acc_pts

        # Total
        score.total_score = (
            score.hook_strength +
            score.curiosity_watch_intent +
            score.platform_compliance +
            score.seo_keyword_relevance +
            score.natural_language +
            score.engagement_potential +
            score.content_accuracy
        )
        score.passed = score.total_score >= cls.PASSING_THRESHOLD
        return score

    @classmethod
    def evaluate_tiktok(
        cls,
        caption: str,
        input_data: CaptionInput,
        dossier: NarrativeDossier,
        consistency: ConsistencyAuditResult
    ) -> ScoreBreakdown:
        score = ScoreBreakdown()
        text = caption.strip()
        lower = text.lower()
        body = text.split("#")[0].strip()

        # 1. Hook Strength (20 pts)
        hook_pts = 0
        hook_prefixes = [
            "pernah", "kenapa", "fakta", "habis", "beda", "gimana", "kalau",
            "bayangkan", "ternyata", "banyak", "aroma", "sensasi", "cahaya",
            "upaya", "keberadaan", "rahasia", "skenario"
        ]
        if any(body.lower().startswith(p) for p in hook_prefixes):
            hook_pts += 10
        if len(body) >= 20:
            hook_pts += 5
        if not consistency.verbatim_repetition:
            hook_pts += 5
        score.hook_strength = min(20, hook_pts)

        # 2. Curiosity & Watch Intent (20 pts)
        cur_pts = 0
        if not consistency.spoiler_detected:
            cur_pts += 10
        if consistency.curiosity_preserved:
            cur_pts += 10
        score.curiosity_watch_intent = min(20, cur_pts)

        # 3. Platform Compliance (20 pts)
        comp_pts = 0
        b_len = len(body)
        if b_len <= 165:
            comp_pts += 10
        elif b_len <= 220:
            comp_pts += 7
        else:
            score.deductions.append(f"TikTok body exceeds 220 chars ({b_len} chars)")

        tags = re.findall(r"#\w+", text)
        if 2 <= len(tags) <= 3:
            comp_pts += 5
        elif len(tags) <= 5:
            comp_pts += 3

        emoji_count = len(re.findall(r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\u2300-\u23ff\u2b50]", text))
        if emoji_count <= 3:
            comp_pts += 5
        score.platform_compliance = min(20, comp_pts)

        # 4. SEO & Keyword Relevance (15 pts)
        seo_pts = 0
        if consistency.keyword_aligned:
            seo_pts += 10
        if tags and not any(t.lower() in {"#fyp", "#viral", "#foryou"} for t in tags):
            seo_pts += 5
        score.seo_keyword_relevance = min(15, seo_pts)

        # 5. Natural Language Quality (10 pts)
        nl_pts = 0
        if not "... 👇" in text and not text.endswith("..."):
            nl_pts += 5
        if not any(slur in lower for slur in ["matamu!", "goblok"]):
            nl_pts += 5
        score.natural_language = min(10, nl_pts)

        # 6. Engagement Potential (10 pts)
        eng_pts = 0
        has_comment = any(w in lower for w in ["komen", "komentar", "tulis", "pendapat", "cerita", "ngalamin"])
        if has_comment:
            eng_pts += 6
        if "?" in text or "👇" in text:
            eng_pts += 4
        score.engagement_potential = min(10, eng_pts)

        # 7. Content Accuracy (5 pts)
        acc_pts = 5 if not consistency.contradiction_detected else 0
        score.content_accuracy = acc_pts

        score.total_score = (
            score.hook_strength +
            score.curiosity_watch_intent +
            score.platform_compliance +
            score.seo_keyword_relevance +
            score.natural_language +
            score.engagement_potential +
            score.content_accuracy
        )
        score.passed = score.total_score >= cls.PASSING_THRESHOLD
        return score

    @classmethod
    def evaluate_youtube(
        cls,
        title: str,
        description: str,
        input_data: CaptionInput,
        dossier: NarrativeDossier,
        consistency: ConsistencyAuditResult
    ) -> ScoreBreakdown:
        score = ScoreBreakdown()
        t = title.strip()
        d = description.strip()
        d_lower = d.lower()

        # 1. Hook Strength (20 pts)
        hook_pts = 0
        if 40 <= len(t) <= 85:
            hook_pts += 10
        elif len(t) <= 100:
            hook_pts += 6
        hook_triggers = {
            "rahasia", "fakta", "kenapa", "mengapa", "bagaimana", "gimana", "misteri",
            "terungkap", "alasan", "sains", "kalau", "apakah", "ternyata", "benarkah",
            "seandainya", "andai", "apa jadinya", "bukan", "tersembunyi"
        }
        if any(w in t.lower() for w in hook_triggers) or "?!" in t or "!?" in t:
            hook_pts += 10
        score.hook_strength = min(20, hook_pts)

        # 2. Curiosity & Watch Intent (20 pts)
        cur_pts = 0
        if not consistency.spoiler_detected:
            cur_pts += 10
        if "?" in t or "?" in d:
            cur_pts += 10
        score.curiosity_watch_intent = min(20, cur_pts)

        # 3. Platform Compliance (20 pts)
        comp_pts = 0
        if 100 <= len(d) <= 500:
            comp_pts += 10
        elif len(d) <= 1000:
            comp_pts += 6

        tags = re.findall(r"#\w+", d)
        if any(t.lower() == "#shorts" for t in tags):
            comp_pts += 5
        if 2 <= len(tags) <= 4:
            comp_pts += 5
        score.platform_compliance = min(20, comp_pts)

        # 4. SEO & Keyword Relevance (15 pts)
        seo_pts = 0
        if consistency.keyword_aligned:
            seo_pts += 8
        kw_pool = list(dossier.searchable_keywords) + list(input_data.main_keywords)
        matched_kw = (
            any(k.lower() in t.lower() for k in kw_pool if len(k) >= 3) or
            any(w in t.lower() for k in kw_pool for w in re.findall(r"[a-zA-Z0-9]+", k.lower()) if len(w) >= 4)
        )
        if matched_kw:
            seo_pts += 7
        score.seo_keyword_relevance = min(15, seo_pts)

        # 5. Natural Language Quality (10 pts)
        nl_pts = 0
        if not "??" in d and not "??" in t:
            nl_pts += 5
        if "\n\n" in d:
            nl_pts += 5
        score.natural_language = min(10, nl_pts)

        # 6. Engagement Potential (10 pts)
        eng_pts = 0
        if any(w in d_lower for w in ["subscribe", "langganan"]):
            eng_pts += 7
        if any(w in d_lower for w in ["kirim", "share", "komen"]):
            eng_pts += 3
        score.engagement_potential = min(10, eng_pts)

        # 7. Content Accuracy (5 pts)
        acc_pts = 5 if not consistency.contradiction_detected else 0
        score.content_accuracy = acc_pts

        score.total_score = (
            score.hook_strength +
            score.curiosity_watch_intent +
            score.platform_compliance +
            score.seo_keyword_relevance +
            score.natural_language +
            score.engagement_potential +
            score.content_accuracy
        )
        score.passed = score.total_score >= cls.PASSING_THRESHOLD
        return score
