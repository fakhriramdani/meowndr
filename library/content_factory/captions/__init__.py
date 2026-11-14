"""
Automated Multi-Platform Caption Generator Module for @meowndr.
"""

from .caption_engine import CaptionEngine, generate_captions_for_episode
from .hashtag_intelligence import HashtagIntelligence
from .retention_engine import RetentionEngine, NarrativeDossier, ConsistencyAuditResult
from .scoring_system import CaptionScoringSystem, ScoreBreakdown
from .analytics_optimizer import AnalyticsOptimizer, OptimizationLoopFeedback
from .schemas.caption_schema import (
    CaptionInput,
    InstagramCaptionOutput,
    TikTokCaptionOutput,
    YouTubeCaptionOutput,
    CaptionBundleOutput
)
from .validators.composite_validator import CompositeValidator

__all__ = [
    "CaptionEngine",
    "generate_captions_for_episode",
    "HashtagIntelligence",
    "RetentionEngine",
    "NarrativeDossier",
    "ConsistencyAuditResult",
    "CaptionScoringSystem",
    "ScoreBreakdown",
    "AnalyticsOptimizer",
    "OptimizationLoopFeedback",
    "CaptionInput",
    "InstagramCaptionOutput",
    "TikTokCaptionOutput",
    "YouTubeCaptionOutput",
    "CaptionBundleOutput",
    "CompositeValidator"
]
