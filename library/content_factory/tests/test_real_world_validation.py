#!/usr/bin/env python3
"""
Controlled Real-World Validation Suite for Trend Research & Content Intelligence System (@meowndr).
Evaluates 5 critical real-world scenarios:
  1. Historical/scientific event with strong documented evidence (Krakatau 1883 shockwaves)
  2. Scientific/engineering exploration (Kola Superdeep Borehole)
  3. Psychology phenomenon (The Return Trip Effect)
  4. Viral misinformation (Health myth / Sensational claim with high virality but false science)
  5. Low-virality scientific discovery (Peer-reviewed breakthrough with minimal social media traction)
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


class TestRealWorldValidation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.mock_episodes_dir = os.path.join(self.test_dir, "episodes")
        self.mock_research_dir = os.path.join(self.test_dir, "research", "trends")
        os.makedirs(self.mock_episodes_dir, exist_ok=True)
        os.makedirs(self.mock_research_dir, exist_ok=True)

        # Setup mock episodes
        ep1 = os.path.join(self.mock_episodes_dir, "06-petir-zigzag")
        os.makedirs(ep1, exist_ok=True)
        with open(os.path.join(ep1, "episode.json"), "w", encoding="utf-8") as f:
            json.dump({
                "title": "Kenapa Petir Bergerak Zig-zag?",
                "topic": "Ionisasi muatan listrik awan dan pembentukan stepped leader di atmosfer"
            }, f)

        ep2 = os.path.join(self.mock_episodes_dir, "04-cacing-cahaya-mata")
        os.makedirs(ep2, exist_ok=True)
        with open(os.path.join(ep2, "episode.json"), "w", encoding="utf-8") as f:
            json.dump({
                "title": "Misteri Bintik Melayang di Mata (Eye Floaters)",
                "topic": "Muscae volitantes dan bayangan sel mikroskopis di cairan vitreous humor mata"
            }, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_scenario_1_krakatoa_historical_geophysics(self):
        """Scenario 1: Historical/scientific event with strong documented evidence."""
        raw = {
            "id": "trend-reels-03-krakatoa-shockwave",
            "platform": "instagram_reels",
            "topic": "Gelombang Kejut Krakatau 1883: Dentuman yang Mengelilingi Planet Bumi 4 Kali",
            "source_url": "https://www.instagram.com/reel/C8kL90_geografi_id/",
            "creator_or_channel": "@geografi_nusantara / Barograf Dunia",
            "publication_date": "2026-10-27T10:00:00+07:00",
            "views": 612000,
            "likes": 54100,
            "comments": 2130,
            "shares": 14900,
            "is_measured_metrics": False,
            "research_timestamp": "2026-10-31T12:00:00+07:00",
            "evidence_quality": "high",
            "evidence_notes": "Historical barograph data verified by Royal Society archives (1888) and BMKG vulcanology records.",
            "niche": "geography"
        }

        tracker = ResearchRepeatabilityTracker(research_dir=self.mock_research_dir)
        opp = OpportunityScorer.score_topic(raw, history_tracker=tracker)
        classifs = opp["evidence_classifications"]
        conf = opp["evidence_confidence"]
        sc = opp["scoring"]
        feas = opp["visual_production_feasibility"]
        rep = opp["research_repeatability"]

        # Evidence classification
        self.assertIn("VERIFIED_FACT", classifs)
        self.assertIn("OBSERVED_TREND", classifs)
        self.assertIn("ESTIMATED_METRICS", classifs)
        self.assertNotIn("MEASURED_METRICS", classifs) # Honest fallback
        self.assertNotIn("INSUFFICIENT_EVIDENCE", classifs)

        # Confidence vs Opportunity score independence
        self.assertEqual(conf["confidence_level"], "HIGH")
        self.assertEqual(conf["confidence_score"], 90.0)
        self.assertEqual(sc["total_score"], 95.5)
        self.assertNotEqual(conf["confidence_score"], sc["total_score"])

        # Feasibility with custom asset effort warning (NOT rejected)
        self.assertEqual(feas["overall_feasibility"], "MEDIUM")
        self.assertTrue(feas["requires_substantial_custom_assets"]) # 1883 London barograph drum warning
        self.assertFalse(feas["required_assets_available"])
        self.assertEqual(opp["status"], "APPROVED") # Custom asset is an effort warning, not rejection

        # Repeatability
        self.assertEqual(rep["observation_count"], 1)
        self.assertEqual(rep["trend_growth_classification"], "SINGLE_OBSERVATION_BASELINE")
        self.assertIsNone(rep["metric_changes"])

    def test_scenario_2_kola_superdeep_borehole_exploration(self):
        """Scenario 2: Scientific/engineering exploration with geothermal rheology limits."""
        raw = {
            "id": "trend-yt-07-kola-superdeep",
            "platform": "youtube_shorts",
            "topic": "Kola Superdeep Borehole: Kenapa Manusia Menyerah Mengebor Perut Bumi di 12 Km?",
            "source_url": "https://www.youtube.com/shorts/kola-superdeep-borehole-mystery-id",
            "creator_or_channel": "Sains Populer / Kok Bisa (#faktaunik #misteribumi)",
            "publication_date": "2026-10-29T11:00:00+07:00",
            "views": 395000,
            "likes": 34200,
            "comments": 1280,
            "shares": 5600,
            "is_measured_metrics": False,
            "research_timestamp": "2026-10-31T12:00:00+07:00",
            "evidence_quality": "high",
            "evidence_notes": "Verified by ICDP and USGS geothermal investigations.",
            "niche": "mystery"
        }

        tracker = ResearchRepeatabilityTracker(research_dir=self.mock_research_dir)
        opp = OpportunityScorer.score_topic(raw, history_tracker=tracker)
        classifs = opp["evidence_classifications"]
        conf = opp["evidence_confidence"]
        sc = opp["scoring"]
        feas = opp["visual_production_feasibility"]
        risk = opp["misleading_simplification_risk"]

        self.assertIn("VERIFIED_FACT", classifs)
        self.assertIn("OBSERVED_TREND", classifs)
        self.assertEqual(conf["confidence_level"], "HIGH")
        self.assertEqual(sc["total_score"], 93.0)

        # Misleading simplification risk must address the 1989 Well to Hell hoax
        self.assertEqual(risk["risk_level"], "HIGH")
        self.assertIn("screaming souls", risk["safeguard_instructions"].lower())

        # Feasibility custom asset effort warning
        self.assertTrue(feas["requires_substantial_custom_assets"])
        self.assertEqual(feas["overall_feasibility"], "MEDIUM")
        self.assertEqual(opp["status"], "APPROVED")

    def test_scenario_3_return_trip_effect_psychology(self):
        """Scenario 3: Psychology phenomenon (everyday paradox with cognitive neuroscience)."""
        raw = {
            "id": "trend-yt-01-return-trip-effect",
            "platform": "youtube_shorts",
            "topic": "The Return Trip Effect: Kenapa Perjalanan Pulang Terasa Jauh Lebih Cepat?",
            "source_url": "https://www.youtube.com/shorts/return-trip-psychology-id",
            "creator_or_channel": "Kok Bisa? / Hujan Tanda Tanya",
            "publication_date": "2026-10-28T14:30:00+07:00",
            "views": 485000,
            "likes": 39200,
            "comments": 1420,
            "shares": 8700,
            "is_measured_metrics": False,
            "research_timestamp": "2026-10-31T12:00:00+07:00",
            "evidence_quality": "high",
            "evidence_notes": "Verified by cognitive neuroscience studies (Kyoto Univ & Tilburg PLOS ONE 2015).",
            "niche": "psychology"
        }

        tracker = ResearchRepeatabilityTracker(research_dir=self.mock_research_dir)
        opp = OpportunityScorer.score_topic(raw, history_tracker=tracker)
        classifs = opp["evidence_classifications"]
        conf = opp["evidence_confidence"]
        feas = opp["visual_production_feasibility"]
        dup = opp["duplicate_assessment"]

        self.assertIn("VERIFIED_FACT", classifs)
        self.assertIn("OBSERVED_TREND", classifs)
        self.assertEqual(conf["confidence_level"], "HIGH")

        # Standard kit assets sufficient -> High feasibility, no custom asset flag
        self.assertEqual(feas["overall_feasibility"], "HIGH")
        self.assertFalse(feas["requires_substantial_custom_assets"])
        self.assertTrue(feas["required_assets_available"])

        # Brain/neurology theme has moderate semantic overlap with 07-brain-freeze ('otak', 'sains', 'cepat'),
        # but qualifies with a justified new angle (cognitive temporal compression vs cranial neuralgia)
        self.assertEqual(dup["similarity_level"], "MODERATE")
        self.assertEqual(dup["matched_existing_episode"], "07-brain-freeze")
        self.assertFalse(dup["is_duplicate"])
        self.assertIn("07-brain-freeze", dup["new_angle_justification"])

    def test_scenario_4_viral_misinformation(self):
        """Scenario 4: Popular myth with high virality but disproven/weak science."""
        raw_myth = {
            "id": "trend-myth-paru-paru-basah",
            "platform": "tiktok",
            "topic": "Mandi Malam Menyebabkan Paru-Paru Basah",
            "source_url": "https://www.tiktok.com/tag/mitosataufakta/video/sample1",
            "creator_or_channel": "@viral_kesehatan_mitos",
            "views": 3800000,
            "likes": 290000,
            "comments": 8500,
            "shares": 45000,
            "is_measured_metrics": False,
            "research_timestamp": "2026-10-31T12:00:00+07:00",
            "evidence_quality": "low",
            "evidence_notes": "Massive viral engagement on TikTok Indonesia; scientifically disproven by pulmonology research (infections cause pneumonia, not bath water temperature).",
            "niche": "health_myth"
        }
        bogus_sources = [
            {"claim": "Air mandi dingin menyerap lewat kulit masuk pleura", "source_name": "Blog gaya hidup viral", "url": "https://mitos-sehat.org"}
        ]

        classifs = EvidenceClassifier.classify(raw_myth, bogus_sources)
        conf = EvidenceClassifier.calculate_evidence_confidence(classifs, bogus_sources, raw_myth)

        # High virality generates OBSERVED_TREND
        self.assertIn("OBSERVED_TREND", classifs)
        # But lack of scientific evidence blocks VERIFIED_FACT
        self.assertNotIn("VERIFIED_FACT", classifs)
        self.assertIn("INSUFFICIENT_EVIDENCE", classifs)

        # Evidence confidence must be severely degraded
        self.assertEqual(conf["confidence_level"], "LOW")
        self.assertLess(conf["confidence_score"], 40.0)

    def test_scenario_5_low_virality_scientific_discovery(self):
        """Scenario 5: Legitimate scientific discovery with strong evidence but low social media traction."""
        raw_niche = {
            "id": "trend-sci-quantum-fusion",
            "platform": "youtube_shorts",
            "topic": "Efek Terowongan Kuantum pada Fusi Inti Matahari",
            "source_url": "https://www.youtube.com/shorts/solar-quantum-tunneling-raw",
            "creator_or_channel": "Dr. Fisika Teori (Niche Academic Channel)",
            "views": 150,
            "likes": 14,
            "comments": 2,
            "shares": 0,
            "is_measured_metrics": False,
            "research_timestamp": "2026-10-31T12:00:00+07:00",
            "evidence_quality": "high",
            "evidence_notes": "Authoritative paper published in Physical Review Letters explaining barrier penetration in proton-proton chain.",
            "niche": "science"
        }
        authoritative_sources = [
            {
                "claim": "Proton-proton fusion in the Sun relies on quantum barrier tunneling to overcome Coulomb barrier at 15 million Kelvin.",
                "source_name": "Physical Review Letters (Nuclear Astrophysics)",
                "url": "https://journals.aps.org/prl/solar-tunneling"
            }
        ]

        classifs = EvidenceClassifier.classify(raw_niche, authoritative_sources)
        conf = EvidenceClassifier.calculate_evidence_confidence(classifs, authoritative_sources, raw_niche)
        opp = OpportunityScorer.score_topic(raw_niche)

        # Verified fact present due to PRL journal
        self.assertIn("VERIFIED_FACT", classifs)
        # Observed trend ABSENT due to low views (150 views)
        self.assertNotIn("OBSERVED_TREND", classifs)

        # Factual confidence is medium/high (75.0%)
        self.assertEqual(conf["confidence_score"], 75.0)

        # But opportunity is logged in BACKLOG (not APPROVED) to preserve production slots for trending topics
        self.assertEqual(opp["status"], "BACKLOG")
        self.assertLess(opp["scoring"]["total_score"], 80.0)

    def test_semantic_duplicate_detection_and_justified_new_angles(self):
        """Verify semantic similarity detection against existing episodes and distinct angle qualification."""
        detector = DuplicateDetector(episodes_dir=self.mock_episodes_dir, research_dir=self.mock_research_dir)

        # Case A: High semantic overlap with existing episode 04-cacing-cahaya-mata
        concept_overlap = {
            "main_question": "Kenapa ada cacing atau benang melayang di pandangan mata?",
            "relevant_keywords": ["floaters", "cacing cahaya mata", "vitreous humor", "mata"]
        }
        orig_a, dup_a = detector.assess_topic(
            topic_title="Misteri Cacing Melayang di Mata (Eye Floaters)",
            concept=concept_overlap,
            raw_trend_id="trend-dup-floaters"
        )
        self.assertEqual(dup_a["similarity_level"], "HIGH")
        self.assertTrue(dup_a["is_duplicate"])
        self.assertEqual(dup_a["matched_existing_episode"], "04-cacing-cahaya-mata")
        self.assertEqual(orig_a["comparison_status"], "POTENTIAL_OVERLAP")

        # Case B: Related theme on atmospheric physics with justified new angle (Krakatoa shockwave vs lightning)
        concept_krakatoa = {
            "main_question": "Bagaimana letusan Krakatau 1883 menghasilkan dentuman yang mengitari bumi 4 kali?",
            "relevant_keywords": ["krakatau 1883", "gelombang kejut", "barograf", "sejarah indonesia"]
        }
        orig_b, dup_b = detector.assess_topic(
            topic_title="Gelombang Kejut Krakatau 1883",
            concept=concept_krakatoa,
            raw_trend_id="trend-reels-03-krakatoa-shockwave"
        )
        # Distinct angle justified: tropospheric acoustic-gravity shockwaves vs thunderstorm stepped leaders
        self.assertFalse(dup_b["is_duplicate"])
        self.assertIn("06-petir-zigzag", dup_b["new_angle_justification"])

    def test_repeatability_rules_and_longitudinal_tracking(self):
        """Verify single observation baseline enforcement and longitudinal comparison across runs."""
        tracker = ResearchRepeatabilityTracker(research_dir=self.mock_research_dir)

        # Run 1: Baseline observation
        res_run1 = tracker.track_opportunity(
            opp_id="opp-repeat-test",
            current_date="2026-10-25",
            current_score=85.0,
            current_confidence=80.0,
            current_platform="YouTube Shorts"
        )
        self.assertEqual(res_run1["observation_count"], 1)
        self.assertEqual(res_run1["trend_growth_classification"], "SINGLE_OBSERVATION_BASELINE")
        self.assertIsNone(res_run1["metric_changes"])
        self.assertIsNone(res_run1["score_changes"])

        # Create historical run directory for 2026-10-25
        run1_dir = os.path.join(self.mock_research_dir, "2026-10-25")
        os.makedirs(run1_dir, exist_ok=True)
        with open(os.path.join(run1_dir, "trend-data.json"), "w", encoding="utf-8") as f:
            json.dump({
                "evaluated_opportunities": [{
                    "id": "opp-repeat-test",
                    "scoring": {"total_score": 85.0},
                    "evidence_confidence": {"confidence_score": 80.0},
                    "video_concept": {"recommended_platform": "YouTube Shorts"}
                }]
            }, f)

        # Run 2: Multi-run tracking (2026-10-31) with accelerating score (+7.0)
        res_run2 = tracker.track_opportunity(
            opp_id="opp-repeat-test",
            current_date="2026-10-31",
            current_score=92.0,
            current_confidence=85.0,
            current_platform="YouTube Shorts"
        )
        self.assertEqual(res_run2["observation_count"], 2)
        self.assertEqual(res_run2["trend_growth_classification"], "ACCELERATING")
        self.assertEqual(res_run2["score_changes"]["score_delta"], 7.0)
        self.assertEqual(res_run2["confidence_changes"]["confidence_delta"], 5.0)


if __name__ == "__main__":
    unittest.main()
