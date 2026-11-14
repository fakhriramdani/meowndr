#!/usr/bin/env python3
"""
Unit tests for Trend Research and Content Intelligence System (@meowndr).
"""

import os
import sys
import json
import unittest
import tempfile
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.trend_intelligence import (
    MetricCalculator,
    TrendHarvester,
    OpportunityScorer,
    ArtifactExporter,
    TrendValidator,
    run_trend_research_pipeline
)
from library.content_factory.schema_validator import validate_artifact


class TestTrendIntelligence(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_metric_calculator(self):
        # Normal calculation
        rate = MetricCalculator.calculate_engagement_rate(views=1000, likes=100, comments=10, shares=10)
        self.assertEqual(rate, 12.0)

        # Handling missing shares (e.g. YouTube Shorts where share count is private)
        rate_no_shares = MetricCalculator.calculate_engagement_rate(views=1000, likes=50, comments=10, shares=None)
        self.assertEqual(rate_no_shares, 6.0)

        # Zero or None views
        self.assertIsNone(MetricCalculator.calculate_engagement_rate(views=0, likes=10, comments=5, shares=2))
        self.assertIsNone(MetricCalculator.calculate_engagement_rate(views=None, likes=10, comments=5, shares=2))

        # View velocity
        pub_date = "2026-10-31T09:00:00+07:00"
        res_date = "2026-10-31T12:00:00+07:00" # 3 hours later
        velocity = MetricCalculator.calculate_view_velocity(views=3000, pub_date_str=pub_date, research_time_str=res_date)
        self.assertEqual(velocity, 1000.0)

    def test_platform_status_disclosures(self):
        harvester = TrendHarvester()
        statuses = harvester.get_platform_statuses()
        self.assertEqual(len(statuses), 3)

        platforms = [p["platform"] for p in statuses]
        self.assertIn("YouTube Shorts", platforms)
        self.assertIn("TikTok", platforms)
        self.assertIn("Instagram Reels", platforms)

        # Verify limitations are explicitly stated
        for s in statuses:
            self.assertTrue(len(s["limitations"]) > 10)
            self.assertIn("access_mode", s)
            self.assertIn("status", s)

    def test_opportunity_scorer_and_rejection_rules(self):
        sample_trend = {
            "id": "trend-yt-01-return-trip-effect",
            "platform": "youtube_shorts",
            "topic": "The Return Trip Effect",
            "source_url": "https://www.youtube.com/shorts/test",
            "creator_or_channel": "Kok Bisa",
            "publication_date": "2026-10-30T10:00:00+07:00",
            "views": 200000,
            "likes": 20000,
            "comments": 500,
            "shares": 1000,
            "is_measured_metrics": False,
            "research_timestamp": "2026-10-31T10:00:00+07:00",
            "evidence_quality": "high",
            "evidence_notes": "Study on memory interval coding.",
            "niche": "psychology"
        }

        opp = OpportunityScorer.score_topic(sample_trend)
        self.assertEqual(opp["status"], "APPROVED")
        sc = opp["scoring"]
        self.assertGreaterEqual(sc["total_score"], 70.0)
        self.assertLessEqual(sc["total_score"], 100.0)
        self.assertTrue(len(sc["reasoning"]) > 30)

        # Verify video concept structure
        vc = opp["video_concept"]
        self.assertIn("main_question", vc)
        self.assertIn("opening_hook", vc)
        self.assertIn("papercraft_visualizations", vc)
        self.assertIn("cat_scientist_interactions", vc)
        self.assertIn("factual_sources_to_verify", vc)

    def test_schema_conformance_and_artifact_export(self):
        res = run_trend_research_pipeline(date_str="2026-10-31")
        payload = res["payload"]

        # 1. Schema check
        valid, errors = validate_artifact("trend_intelligence", payload)
        self.assertTrue(valid, f"Schema validation errors: {errors}")

        # 2. Validator check
        val_ok, val_errs = TrendValidator.validate(payload)
        self.assertTrue(val_ok, f"TrendValidator errors: {val_errs}")

        # 3. File existence check
        files = res["files"]
        for label, fpath in files.items():
            self.assertTrue(os.path.exists(fpath), f"Expected file {fpath} not found.")
            self.assertGreater(os.path.getsize(fpath), 100, f"File {fpath} is unexpectedly small.")

    def test_rejection_of_corrupt_data(self):
        # Negative views or out-of-bounds score should be caught
        corrupt_payload = {
            "generated_at": "2026-10-31T11:00:00+07:00",
            "research_date": "2026-10-31",
            "target_audience": "Audience",
            "niches_covered": ["science"],
            "platforms_monitored": [
                {
                    "platform": "YouTube Shorts",
                    "access_mode": "api",
                    "status": "OK",
                    "limitations": "None"
                }
            ],
            "raw_trends": [
                {
                    "id": "corrupt-1",
                    "platform": "youtube_shorts",
                    "topic": "Corrupt",
                    "source_url": "invalid-url", # invalid URL
                    "creator_or_channel": "Tester",
                    "views": -500, # negative views
                    "likes": 10,
                    "comments": 2,
                    "shares": 0,
                    "engagement_rate": 150.0, # invalid rate > 100%
                    "view_velocity": -10.0, # negative velocity
                    "is_measured_metrics": True,
                    "research_timestamp": "2026-10-31T11:00:00+07:00",
                    "evidence_quality": "low",
                    "evidence_notes": "note",
                    "niche": "science"
                }
            ],
            "evaluated_opportunities": [],
            "rejected_topics": [],
            "limitations_and_disclosures": {
                "youtube_api_status": "OK",
                "tiktok_api_status": "OK",
                "instagram_api_status": "OK",
                "disclaimer": "test"
            }
        }

        valid, errors = TrendValidator.validate(corrupt_payload)
        self.assertFalse(valid)
        self.assertGreaterEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
