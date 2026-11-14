"""
Performance-Based Optimization Loop for Multi-Platform Captions.
Analyzes verified post-publishing platform analytics when available,
identifies high-retention patterns, and generates learning signals
for continuous caption refinement without fabricating metrics.
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class PlatformPerformanceSignal:
    has_analytics: bool = False
    views: int = 0
    watch_time_avg_sec: float = 0.0
    completion_rate_pct: float = 0.0
    engagement_rate_pct: float = 0.0
    shares_count: int = 0
    saves_count: int = 0
    comments_count: int = 0
    top_performing_hook_style: str = "curiosity_question"
    effective_cta_style: str = "save_share"
    recommended_modifications: List[str] = field(default_factory=list)


@dataclass
class OptimizationLoopFeedback:
    episode_slug: str
    available: bool = False
    instagram: PlatformPerformanceSignal = field(default_factory=PlatformPerformanceSignal)
    tiktok: PlatformPerformanceSignal = field(default_factory=PlatformPerformanceSignal)
    youtube: PlatformPerformanceSignal = field(default_factory=PlatformPerformanceSignal)
    key_learnings: List[str] = field(default_factory=list)


class AnalyticsOptimizer:
    """Ingests verified analytics and derives platform-specific optimization cues."""

    @classmethod
    def load_feedback(cls, episode_dir: Path, slug: str) -> OptimizationLoopFeedback:
        """
        Attempts to read real historical or episode-specific analytics.
        Returns a clean zero-fabrication baseline if no analytics file is present.
        """
        ep_dir = Path(episode_dir)
        candidates = [
            ep_dir / "analytics.json",
            ep_dir / "publishing" / "analytics.json",
            ep_dir.parent.parent / "analytics" / f"{slug}.json",
            ep_dir.parent.parent / "analytics" / "channel_performance.json"
        ]

        analytics_file = next((c for c in candidates if c.exists()), None)
        if not analytics_file:
            return OptimizationLoopFeedback(
                episode_slug=slug,
                available=False,
                key_learnings=["No verified historical analytics detected on disk; using baseline empirical creator best practices."]
            )

        try:
            with open(analytics_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            ig_raw = data.get("instagram", {})
            tt_raw = data.get("tiktok", {})
            yt_raw = data.get("youtube", {})

            # Instagram signal
            ig_signal = PlatformPerformanceSignal(
                has_analytics=bool(ig_raw),
                views=ig_raw.get("views", 0),
                watch_time_avg_sec=float(ig_raw.get("avg_watch_time_sec", 0.0)),
                shares_count=ig_raw.get("shares", 0),
                saves_count=ig_raw.get("saves", 0),
                comments_count=ig_raw.get("comments", 0),
                engagement_rate_pct=float(ig_raw.get("engagement_rate_pct", 0.0))
            )
            if ig_signal.saves_count > 50:
                ig_signal.effective_cta_style = "save_reference"
                ig_signal.recommended_modifications.append("High save rate detected: emphasize structured takeaway points in caption body.")

            # TikTok signal
            tt_signal = PlatformPerformanceSignal(
                has_analytics=bool(tt_raw),
                views=tt_raw.get("views", 0),
                watch_time_avg_sec=float(tt_raw.get("avg_watch_time_sec", 0.0)),
                completion_rate_pct=float(tt_raw.get("completion_rate_pct", 0.0)),
                shares_count=tt_raw.get("shares", 0),
                comments_count=tt_raw.get("comments", 0)
            )
            if tt_signal.completion_rate_pct > 65.0:
                tt_signal.top_performing_hook_style = "open_loop_curiosity"
                tt_signal.recommended_modifications.append("Strong completion rate: maintain concise viewport body under 160 chars.")

            # YouTube signal
            yt_signal = PlatformPerformanceSignal(
                has_analytics=bool(yt_raw),
                views=yt_raw.get("views", 0),
                watch_time_avg_sec=float(yt_raw.get("avg_view_duration_sec", 0.0)),
                comments_count=yt_raw.get("comments", 0)
            )

            return OptimizationLoopFeedback(
                episode_slug=slug,
                available=True,
                instagram=ig_signal,
                tiktok=tt_signal,
                youtube=yt_signal,
                key_learnings=[
                    "Actual analytics incorporated into caption generation weighting.",
                    f"Verified Instagram saves: {ig_signal.saves_count}, TikTok completion: {tt_signal.completion_rate_pct}%."
                ]
            )
        except Exception as e:
            return OptimizationLoopFeedback(
                episode_slug=slug,
                available=False,
                key_learnings=[f"Analytics file found but failed to parse ({e}); falling back to standard creator rules."]
            )
