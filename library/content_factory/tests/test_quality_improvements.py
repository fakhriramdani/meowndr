#!/usr/bin/env python3
"""
Unit tests for Trend Intelligence Quality Improvements (@meowndr).
Verifies:
  1. Fact verification versus trend verification independence.
  2. Missing and estimated metrics classification.
  3. Duplicate topic detection against existing episodes and historical runs.
  4. Single-observation trend classification (preventing false growth claims).
  5. Production feasibility assessment (6-point check & custom asset flag).
  6. Evidence confidence reported independently from opportunity score.
  7. Historical research repeatability comparison across multiple run directories.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.trend_intelligence import (
    EvidenceClassifier,
    DuplicateDetector,
    ProductionFeasibilityEvaluator,
    ResearchRepeatabilityTracker,
    OpportunityScorer,
    TrendValidator
)


class TestTrendIntelligenceQualityImprovements(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.mock_episodes_dir = os.path.join(self.test_dir, "episodes")
        self.mock_research_dir = os.path.join(self.test_dir, "research", "trends")
        os.makedirs(self.mock_episodes_dir, exist_ok=True)
        os.makedirs(self.mock_research_dir, exist_ok=True)

        # Create mock episode in episodes dir
        mock_ep = os.path.join(self.mock_episodes_dir, "04-cacing-cahaya-mata")
        os.makedirs(mock_ep, exist_ok=True)
        with open(os.path.join(mock_ep, "episode.json"), "w", encoding="utf-8") as f:
            json.dump({
                "title": "Misteri Bintik Melayang di Mata (Eye Floaters)",
                "topic": "Penjelasan sains tentang floaters atau muscae volitantes di dalam vitreous humor mata"
            }, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_fact_versus_trend_independence(self):
        """
        Verify that:
          - A factually verified claim is NOT automatically an observed trend.
          - A viral/trending topic is NOT automatically a verified fact.
        """
        # Case A: Scientific fact with primary journal citation but ZERO platform traction (e.g. 50 views)
        fact_not_trend = {
            "id": "trend-sci-niche",
            "platform": "youtube_shorts",
            "topic": "Efek Terowongan Kuantum pada Fusi Matahari",
            "source_url": "https://youtube.com/shorts/quantum-tunneling-raw",
            "creator_or_channel": "Dr. Fisika",
            "views": 50,
            "evidence_notes": "Academic preprint discussion",
            "is_measured_metrics": False
        }
        factual_sources = [{
            "claim": "Quantum tunneling rate in solar core fusion",
            "source_name": "Physical Review Letters (PRL Journal)",
            "url": "https://journals.aps.org/prl/sample"
        }]

        classifs_a = EvidenceClassifier.classify(fact_not_trend, factual_sources)
        self.assertIn("VERIFIED_FACT", classifs_a)
        self.assertNotIn("OBSERVED_TREND", classifs_a)

        # Case B: Viral TikTok trend (5 million views) with sensational myth and NO credible citations
        trend_not_fact = {
            "id": "trend-viral-myth",
            "platform": "tiktok",
            "topic": "Batu Kristal Penyerap Energi Negatif dan Radiasi HP",
            "source_url": "https://tiktok.com/@viral_healer/video/12345",
            "creator_or_channel": "@viral_healer",
            "views": 5000000,
            "evidence_notes": "Viral trend surge across TikTok lifestyle feeds",
            "is_measured_metrics": False
        }
        bogus_sources = [{
            "claim": "Batu kristal menyerap radiasi",
            "source_name": "Blog spiritual online",
            "url": "https://mystic-stones-healing.com/post"
        }]

        classifs_b = EvidenceClassifier.classify(trend_not_fact, bogus_sources)
        self.assertIn("OBSERVED_TREND", classifs_b)
        self.assertNotIn("VERIFIED_FACT", classifs_b)

        # Case C: Valid topic having both verified fact and observed trend
        both_ok = {
            "id": "trend-krakatoa-ok",
            "platform": "instagram_reels",
            "topic": "Gelombang Kejut Krakatau 1883",
            "source_url": "https://instagram.com/reel/krakatau",
            "creator_or_channel": "@geografi_id",
            "views": 500000,
            "evidence_notes": "Viral reels topic verified by Royal Society archives",
            "is_measured_metrics": False
        }
        credible_sources = [{
            "claim": "Atmospheric pressure pulse encircled Earth 4 times",
            "source_name": "Royal Society Report 1888",
            "url": "https://archive.org/details/eruptionkrakato00whipgoog"
        }]
        classifs_c = EvidenceClassifier.classify(both_ok, credible_sources)
        self.assertIn("VERIFIED_FACT", classifs_c)
        self.assertIn("OBSERVED_TREND", classifs_c)

    def test_missing_and_estimated_metrics_classification(self):
        """Verify proper assignment of MEASURED_METRICS vs ESTIMATED_METRICS."""
        # Direct measured metric
        measured_item = {
            "platform": "youtube_shorts",
            "source_url": "https://youtube.com/shorts/test",
            "views": 25000,
            "is_measured_metrics": True
        }
        classifs_m = EvidenceClassifier.classify(measured_item)
        self.assertIn("MEASURED_METRICS", classifs_m)
        self.assertNotIn("ESTIMATED_METRICS", classifs_m)

        # Estimated metric
        estimated_item = {
            "platform": "tiktok",
            "source_url": "https://tiktok.com/@user/video/1",
            "views": 25000,
            "is_measured_metrics": False
        }
        classifs_e = EvidenceClassifier.classify(estimated_item)
        self.assertIn("ESTIMATED_METRICS", classifs_e)
        self.assertNotIn("MEASURED_METRICS", classifs_e)

        # Missing metrics (views is None)
        missing_item = {
            "platform": "instagram_reels",
            "source_url": "https://instagram.com/reel/1",
            "views": None,
            "is_measured_metrics": False
        }
        classifs_none = EvidenceClassifier.classify(missing_item)
        self.assertNotIn("MEASURED_METRICS", classifs_none)
        self.assertNotIn("ESTIMATED_METRICS", classifs_none)

    def test_duplicate_topic_detection(self):
        """Verify detection of existing episodes and distinction between overlap and new angles."""
        detector = DuplicateDetector(
            episodes_dir=self.mock_episodes_dir,
            research_dir=self.mock_research_dir
        )

        # 1. Overlapping topic with existing episode 04-cacing-cahaya-mata
        dup_concept = {"main_question": "Kenapa ada cacing melayang di mata kita?"}
        orig_dup, assess_dup = detector.assess_topic(
            topic_title="Misteri Cacing Melayang di Mata (Eye Floaters)",
            concept=dup_concept,
            raw_trend_id="trend-test-floaters"
        )
        self.assertEqual(assess_dup["similarity_level"], "HIGH")
        self.assertTrue(assess_dup["is_duplicate"])
        self.assertEqual(assess_dup["matched_existing_episode"], "04-cacing-cahaya-mata")
        self.assertEqual(orig_dup["comparison_status"], "POTENTIAL_OVERLAP")
        self.assertTrue(len(assess_dup["new_angle_justification"]) > 10)

        # 2. Distinct new topic
        new_concept = {"main_question": "Kenapa es batu mengapung?"}
        orig_new, assess_new = detector.assess_topic(
            topic_title="Superkonduktor Suhu Kamar LK-99",
            concept=new_concept,
            raw_trend_id="trend-test-lk99"
        )
        self.assertEqual(assess_new["similarity_level"], "NONE")
        self.assertFalse(assess_new["is_duplicate"])
        self.assertIsNone(assess_new["matched_existing_episode"])
        self.assertEqual(orig_new["comparison_status"], "DISTINCT_NEW_TOPIC")

    def test_single_observation_trend_classification(self):
        """
        Verify strict adherence to rule:
        Never infer trend growth from a single observation baseline!
        """
        tracker = ResearchRepeatabilityTracker(research_dir=self.mock_research_dir)

        # Single run observation
        res = tracker.track_opportunity(
            opp_id="opp-single-obs",
            current_date="2026-10-31",
            current_score=88.5,
            current_confidence=82.0,
            current_platform="YouTube Shorts"
        )

        self.assertEqual(res["observation_count"], 1)
        self.assertEqual(res["trend_growth_classification"], "SINGLE_OBSERVATION_BASELINE")
        self.assertIsNone(res["metric_changes"])
        self.assertIsNone(res["score_changes"])
        self.assertIsNone(res["confidence_changes"])
        self.assertIn("cannot be inferred from a single historical observation", res["repeatability_notes"])

        # Test that TrendValidator flags any single-observation record falsely marked as ACCELERATING
        mock_payload = {
            "generated_at": "2026-10-31T12:00:00+07:00",
            "research_date": "2026-10-31",
            "target_audience": "Audience ID",
            "platforms_monitored": [
                {"platform": "YouTube Shorts", "access_mode": "fallback", "status": "ACTIVE", "limitations": "None"}
            ],
            "raw_trends": [{
                "id": "t1", "platform": "YouTube Shorts", "topic": "Topic 1",
                "source_url": "https://youtube.com/1", "creator_or_channel": "Creator",
                "research_timestamp": "2026-10-31T12:00:00+07:00", "evidence_quality": "high"
            }],
            "evaluated_opportunities": [{
                "id": "opp-bad-rep",
                "raw_trend_id": "t1",
                "proposed_title": "Bad Repeatability Opportunity",
                "niche": "science",
                "status": "APPROVED",
                "scoring": {
                    "trend_momentum": 20, "relevance_to_meowndr": 20, "educational_value": 20,
                    "visual_storytelling_potential": 10, "originality_differentiation": 5, "evergreen_value": 5,
                    "total_score": 80.0, "reasoning": "Reasoning over 20 chars long"
                },
                "evidence_confidence": {"confidence_score": 80.0, "confidence_level": "HIGH"},
                "research_repeatability": {
                    "first_observed_date": "2026-10-31",
                    "latest_observed_date": "2026-10-31",
                    "observation_count": 1, # single observation!
                    "trend_growth_classification": "ACCELERATING" # Invalid! Violates rule.
                },
                "video_concept": {
                    "main_question": "Q?", "opening_hook": "Hook!", "educational_explanation": "Exp",
                    "why_interesting_now": "Now", "trend_evidence": "Ev", "papercraft_visualizations": ["vis1"],
                    "cat_scientist_interactions": ["int1"], "suggested_scene_progression": ["s1"],
                    "estimated_duration_seconds": 60, "recommended_platform": "YouTube Shorts",
                    "relevant_keywords": ["k1"], "factual_sources_to_verify": []
                }
            }],
            "rejected_topics": [{"topic": "Myth", "rejection_reason": "False", "disqualification_category": "pseudoscience"}],
            "limitations_and_disclosures": {
                "youtube_api_status": "Status", "tiktok_api_status": "Status", "instagram_api_status": "Status"
            }
        }
        valid, errs = TrendValidator.validate(mock_payload)
        self.assertFalse(valid)
        self.assertTrue(any("violated repeatability rule" in e for e in errs))

    def test_production_feasibility_evaluation(self):
        """Verify 6-point visual production feasibility assessment and custom asset flagging."""
        # Case 1: Simple laboratory concept using existing kit assets
        simple_concept = {
            "estimated_duration_seconds": 55.0,
            "papercraft_visualizations": [
                "Bohlam pijar kertas biasa dengan uap panas",
                "Termometer laboratorium kertas"
            ],
            "cat_scientist_interactions": [
                "Kucing Ilmuwan meniup jarinya yang kepanasan",
                "Memeriksa tabung reaksi kertas dengan kaca pembesar"
            ],
            "suggested_scene_progression": ["Scene 1", "Scene 2", "Scene 3", "Scene 4"],
            "main_question": "Bagaimana kunang-kunang bersinar?"
        }
        feas_simple = ProductionFeasibilityEvaluator.evaluate(simple_concept, "science")
        self.assertEqual(feas_simple["overall_feasibility"], "HIGH")
        self.assertTrue(feas_simple["can_explain_in_30_60s"])
        self.assertTrue(feas_simple["can_represent_in_2d_papercraft"])
        self.assertTrue(feas_simple["cat_scientist_meaningful_interaction"])
        self.assertTrue(feas_simple["strong_visual_progression"])
        self.assertTrue(feas_simple["required_assets_available"])
        self.assertFalse(feas_simple["requires_substantial_custom_assets"])

        # Case 2: Deep-sea submarine concept requiring specialized custom assets
        complex_concept = {
            "estimated_duration_seconds": 65.0,
            "papercraft_visualizations": [
                "Kapal selam submersible kertas",
                "Tangki kaca tekanan tinggi dengan jarum manometer"
            ],
            "cat_scientist_interactions": [
                "Cat Scientist mengenakan helm selam bulat di dalam kapal selam",
                "Menatap bayangan isopod raksasa di jendela observasi"
            ],
            "suggested_scene_progression": ["Scene 1", "Scene 2", "Scene 3", "Scene 4", "Scene 5"],
            "main_question": "Kenapa hewan di palung laut dalam menjadi raksasa?"
        }
        feas_complex = ProductionFeasibilityEvaluator.evaluate(complex_concept, "nature")
        self.assertEqual(feas_complex["overall_feasibility"], "MEDIUM")
        self.assertTrue(feas_complex["requires_substantial_custom_assets"])
        self.assertFalse(feas_complex["required_assets_available"])

    def test_evidence_confidence_separate_from_opportunity_score(self):
        """
        Verify that evidence confidence is reported strictly separate
        from the 0-100 content opportunity score, preserving criteria weights.
        """
        sample_trend = {
            "id": "trend-yt-01-return-trip-effect",
            "platform": "youtube_shorts",
            "topic": "The Return Trip Effect",
            "source_url": "https://www.youtube.com/shorts/test",
            "creator_or_channel": "Kok Bisa",
            "publication_date": "2026-10-30T10:00:00+07:00",
            "views": 485000,
            "likes": 39200,
            "comments": 1420,
            "shares": 8700,
            "is_measured_metrics": False,
            "research_timestamp": "2026-10-31T10:00:00+07:00",
            "evidence_quality": "high",
            "evidence_notes": "Surge in Indonesian edutainment; study by Kyoto University.",
            "niche": "psychology"
        }

        opp = OpportunityScorer.score_topic(sample_trend)

        # 1. Total score is strictly between 0 and 100
        total_score = opp["scoring"]["total_score"]
        self.assertGreaterEqual(total_score, 0.0)
        self.assertLessEqual(total_score, 100.0)

        # 2. Check exact 6 criteria weights sum
        sc = opp["scoring"]
        sum_criteria = (
            sc["trend_momentum"] +
            sc["relevance_to_meowndr"] +
            sc["educational_value"] +
            sc["visual_storytelling_potential"] +
            sc["originality_differentiation"] +
            sc["evergreen_value"]
        )
        self.assertAlmostEqual(total_score, sum_criteria, places=1)

        # 3. Evidence confidence is reported as a separate metric object
        self.assertIn("evidence_confidence", opp)
        conf = opp["evidence_confidence"]
        self.assertIn("confidence_score", conf)
        self.assertIn("confidence_level", conf)
        self.assertIn("rationale", conf)

        # Confidence score should NOT be equal to opportunity score (independent calculation)
        self.assertNotEqual(conf["confidence_score"], total_score)
        self.assertIn(conf["confidence_level"], ["HIGH", "MEDIUM", "LOW"])

    def test_historical_research_repeatability_comparison(self):
        """Verify comparison across multiple research runs and growth classification."""
        tracker = ResearchRepeatabilityTracker(research_dir=self.mock_research_dir)

        # Create Day 1 run (2026-10-25)
        day1_dir = os.path.join(self.mock_research_dir, "2026-10-25")
        os.makedirs(day1_dir, exist_ok=True)
        with open(os.path.join(day1_dir, "trend-data.json"), "w", encoding="utf-8") as f:
            json.dump({
                "evaluated_opportunities": [{
                    "id": "opp-multi-run-test",
                    "scoring": {"total_score": 80.0},
                    "evidence_confidence": {"confidence_score": 70.0},
                    "video_concept": {"recommended_platform": "YouTube Shorts"}
                }]
            }, f)

        # Evaluate Day 2 run (2026-10-31) with accelerating score (delta +8.0)
        res_day2 = tracker.track_opportunity(
            opp_id="opp-multi-run-test",
            current_date="2026-10-31",
            current_score=88.0,
            current_confidence=85.0,
            current_platform="YouTube Shorts"
        )

        self.assertEqual(res_day2["observation_count"], 2)
        self.assertEqual(res_day2["first_observed_date"], "2026-10-25")
        self.assertEqual(res_day2["latest_observed_date"], "2026-10-31")
        self.assertEqual(res_day2["trend_growth_classification"], "ACCELERATING")
        self.assertIsNotNone(res_day2["score_changes"])
        self.assertEqual(res_day2["score_changes"]["score_delta"], 8.0)
        self.assertEqual(res_day2["confidence_changes"]["confidence_delta"], 15.0)


if __name__ == "__main__":
    unittest.main()
