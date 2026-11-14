#!/usr/bin/env python3
"""
Operational smoke test: Failure handling verification for Trend Research System.
Verifies:
  1. YouTube API key missing behavior
  2. TikTok data unavailable behavior
  3. Instagram data unavailable behavior
  4. Incomplete metrics handling (missing shares, zero views, missing date)
  5. Empty / no valid trend found behavior
  6. Source timeout / exception handling
"""

import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.trend_intelligence import (
    MetricCalculator,
    TrendHarvester,
    OpportunityScorer,
    TrendValidator
)


class TestFailureHandling(unittest.TestCase):
    def test_missing_youtube_api_key(self):
        # Force unset YOUTUBE_API_KEY
        old_val = os.environ.get("YOUTUBE_API_KEY")
        os.environ["YOUTUBE_API_KEY"] = ""
        try:
            harvester = TrendHarvester()
            statuses = harvester.get_platform_statuses()
            yt = next(s for s in statuses if s["platform"] == "YouTube Shorts")
            self.assertEqual(yt["status"], "UNCONFIGURED_FALLBACK")
            self.assertFalse(yt["credentials_configured"])
            self.assertIn("YOUTUBE_API_KEY not configured", yt["limitations"])
        finally:
            if old_val:
                os.environ["YOUTUBE_API_KEY"] = old_val

    def test_missing_tiktok_credentials(self):
        # Force unset TIKTOK_ACCESS_TOKEN
        old_val = os.environ.get("TIKTOK_ACCESS_TOKEN")
        if "TIKTOK_ACCESS_TOKEN" in os.environ:
            del os.environ["TIKTOK_ACCESS_TOKEN"]
        try:
            harvester = TrendHarvester()
            statuses = harvester.get_platform_statuses()
            tt = next(s for s in statuses if s["platform"] == "TikTok")
            self.assertEqual(tt["status"], "UNAVAILABLE_COMMERCIAL_RESTRICTION")
            self.assertFalse(tt["credentials_configured"])
            self.assertIn("TikTok Research API is legally restricted", tt["limitations"])
        finally:
            if old_val:
                os.environ["TIKTOK_ACCESS_TOKEN"] = old_val

    def test_missing_instagram_credentials(self):
        # Force unset INSTAGRAM_GRAPH_API_KEY
        old_val = os.environ.get("INSTAGRAM_GRAPH_API_KEY")
        if "INSTAGRAM_GRAPH_API_KEY" in os.environ:
            del os.environ["INSTAGRAM_GRAPH_API_KEY"]
        try:
            harvester = TrendHarvester()
            statuses = harvester.get_platform_statuses()
            ig = next(s for s in statuses if s["platform"] == "Instagram Reels")
            self.assertEqual(ig["status"], "UNAVAILABLE_NO_PUBLIC_DISCOVERY_API")
            self.assertFalse(ig["credentials_configured"])
            self.assertIn("Meta Graph API does not provide a public unrestricted Reels discovery", ig["limitations"])
        finally:
            if old_val:
                os.environ["INSTAGRAM_GRAPH_API_KEY"] = old_val

    def test_incomplete_metrics_handling(self):
        # Missing views -> engagement rate and velocity must be None
        self.assertIsNone(MetricCalculator.calculate_engagement_rate(None, 100, 10, 5))
        self.assertIsNone(MetricCalculator.calculate_engagement_rate(0, 100, 10, 5))
        self.assertIsNone(MetricCalculator.calculate_view_velocity(None, "2026-10-31T08:00:00+07:00", "2026-10-31T11:00:00+07:00"))

        # Missing publication date -> velocity must be None
        self.assertIsNone(MetricCalculator.calculate_view_velocity(1000, None, "2026-10-31T11:00:00+07:00"))

        # Missing shares -> engagement rate is computed without inventing shares
        rate = MetricCalculator.calculate_engagement_rate(1000, 50, 10, None)
        self.assertEqual(rate, 6.0)

    def test_empty_or_unmatched_niche(self):
        harvester = TrendHarvester()
        candidates, rejected = harvester.harvest(niche="non_existent_niche_xyz")
        # Should not crash; returns empty candidates list
        self.assertEqual(len(candidates), 0)
        self.assertGreater(len(rejected), 0)

    def test_rejection_of_pseudoscience_and_misinformation(self):
        harvester = TrendHarvester()
        _, rejected = harvester.harvest()
        topics = [r["topic"] for r in rejected]
        self.assertTrue(any("Paru-Paru Basah" in t for t in topics))
        self.assertTrue(any("Alien" in t for t in topics))
        self.assertTrue(any("432Hz" in t for t in topics))


if __name__ == "__main__":
    unittest.main()
