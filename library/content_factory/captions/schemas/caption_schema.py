"""
Typed data schemas and contracts for multi-platform caption generation.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import hashlib
import json
import datetime


@dataclass
class CaptionInput:
    """Standardized input payload for multi-platform caption generation."""
    topic: str
    title: str
    script_lines: List[Dict[str, Any]] = field(default_factory=list)
    script_text: str = ""
    hook: str = ""
    cover_title: str = ""
    key_facts: List[str] = field(default_factory=list)
    target_audience: str = "General curious audience (18-35)"
    content_category: str = "science"
    main_keywords: List[str] = field(default_factory=list)
    duration_seconds: float = 45.0
    language: str = "id"
    channel_name: str = "@meowndr"
    slug: str = ""

    def compute_script_hash(self) -> str:
        """Computes SHA-256 hash of script text and title to track modifications."""
        hasher = hashlib.sha256()
        hasher.update(self.title.strip().encode("utf-8"))
        hasher.update(self.topic.strip().encode("utf-8"))
        hasher.update(self.hook.strip().encode("utf-8"))
        hasher.update(self.script_text.strip().encode("utf-8"))
        for line in self.script_lines:
            t = line.get("text", "")
            hasher.update(t.strip().encode("utf-8"))
        return hasher.hexdigest()[:16]


@dataclass
class InstagramCaptionOutput:
    caption: str
    hashtags: List[str]
    character_count: int
    opening_hook: str = ""
    keywords: List[str] = field(default_factory=list)
    CTA: str = ""
    alternative_caption: str = ""
    quality_score: int = 0
    score_breakdown: Dict[str, Any] = field(default_factory=dict)
    status: str = "READY"  # "READY" | "NEEDS_REVIEW"
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "caption": self.caption,
            "opening_hook": self.opening_hook,
            "keywords": self.keywords,
            "hashtags": self.hashtags,
            "CTA": self.CTA,
            "alternative_caption": self.alternative_caption,
            "character_count": self.character_count,
            "quality_score": self.quality_score,
            "score_breakdown": self.score_breakdown,
            "status": self.status,
            "validation_errors": self.validation_errors
        }

    def to_platform_package(self) -> Dict[str, Any]:
        """Section 10 Instagram Reels deliverable package."""
        return {
            "caption": self.caption,
            "opening_hook": self.opening_hook,
            "keywords": self.keywords,
            "hashtags": self.hashtags,
            "CTA": self.CTA,
            "alternative_caption": self.alternative_caption
        }


@dataclass
class TikTokCaptionOutput:
    caption: str
    hashtags: List[str]
    character_count: int
    opening_hook: str = ""
    keywords: List[str] = field(default_factory=list)
    CTA: str = ""
    alternative_caption: str = ""
    quality_score: int = 0
    score_breakdown: Dict[str, Any] = field(default_factory=dict)
    status: str = "READY"  # "READY" | "NEEDS_REVIEW"
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "caption": self.caption,
            "opening_hook": self.opening_hook,
            "keywords": self.keywords,
            "hashtags": self.hashtags,
            "CTA": self.CTA,
            "alternative_caption": self.alternative_caption,
            "character_count": self.character_count,
            "quality_score": self.quality_score,
            "score_breakdown": self.score_breakdown,
            "status": self.status,
            "validation_errors": self.validation_errors
        }

    def to_platform_package(self) -> Dict[str, Any]:
        """Section 10 TikTok deliverable package."""
        return {
            "caption": self.caption,
            "opening_hook": self.opening_hook,
            "keywords": self.keywords,
            "hashtags": self.hashtags,
            "CTA": self.CTA,
            "alternative_caption": self.alternative_caption
        }


@dataclass
class YouTubeCaptionOutput:
    title: str
    description: str
    hashtags: List[str]
    search_keywords: List[str] = field(default_factory=list)
    pinned_comment: str = ""
    alternative_title: str = ""
    title_character_count: int = 0
    description_character_count: int = 0
    quality_score: int = 0
    score_breakdown: Dict[str, Any] = field(default_factory=dict)
    status: str = "READY"  # "READY" | "NEEDS_REVIEW"
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "search_keywords": self.search_keywords,
            "hashtags": self.hashtags,
            "pinned_comment": self.pinned_comment,
            "alternative_title": self.alternative_title,
            "title_character_count": self.title_character_count,
            "description_character_count": self.description_character_count,
            "quality_score": self.quality_score,
            "score_breakdown": self.score_breakdown,
            "status": self.status,
            "validation_errors": self.validation_errors
        }

    def to_platform_package(self) -> Dict[str, Any]:
        """Section 10 YouTube Shorts deliverable package."""
        return {
            "title": self.title,
            "description": self.description,
            "search_keywords": self.search_keywords,
            "hashtags": self.hashtags,
            "pinned_comment": self.pinned_comment,
            "alternative_title": self.alternative_title
        }


@dataclass
class CaptionBundleOutput:
    topic: str
    language: str
    script_hash: str
    instagram: InstagramCaptionOutput
    tiktok: TikTokCaptionOutput
    youtube: YouTubeCaptionOutput
    generated_at: str = ""
    attempt_count: int = 1
    overall_status: str = "READY"  # "READY" | "NEEDS_REVIEW"
    validation_report: Dict[str, Any] = field(default_factory=dict)
    platform_strategy_summary: Dict[str, str] = field(default_factory=dict)
    caption_quality_score: Dict[str, int] = field(default_factory=dict)
    compliance_check: Dict[str, bool] = field(default_factory=dict)
    curiosity_score: Dict[str, int] = field(default_factory=dict)
    keyword_relevance_score: Dict[str, int] = field(default_factory=dict)
    retention_alignment_score: Dict[str, int] = field(default_factory=dict)

    def to_json_dict(self) -> Dict[str, Any]:
        """Matches canonical Phase 9 JSON output format while preserving rich metadata."""
        return {
            "topic": self.topic,
            "language": self.language,
            "script_hash": self.script_hash,
            "generated_at": self.generated_at or datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "platforms": {
                "instagram": self.instagram.to_dict(),
                "tiktok": self.tiktok.to_dict(),
                "youtube": self.youtube.to_dict()
            },
            "analysis": self.to_analysis_dict()
        }

    def to_analysis_dict(self) -> Dict[str, Any]:
        """Section 10 caption-analysis.json deliverable payload."""
        return {
            "platform_strategy_summary": self.platform_strategy_summary,
            "caption_quality_score": self.caption_quality_score,
            "compliance_check": self.compliance_check,
            "curiosity_score": self.curiosity_score,
            "keyword_relevance_score": self.keyword_relevance_score,
            "retention_alignment_score": self.retention_alignment_score
        }
