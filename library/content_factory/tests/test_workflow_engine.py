#!/usr/bin/env python3
"""
Unit tests for Papercraft Content Factory Workflow Engine and Schemas.
"""

import os
import sys
import shutil
import tempfile
import unittest
import json

HERE = os.path.dirname(os.path.abspath(__file__))
CF_DIR = os.path.dirname(HERE)
sys.path.insert(0, CF_DIR)

from workflow_engine import WorkflowEngine
from schema_validator import validate_artifact
from niche_manager import get_niche_profile, list_supported_niches


class TestWorkflowEngine(unittest.TestCase):
    def setUp(self):
        self.tmp_episodes = tempfile.mkdtemp(prefix="cf_test_ep_")
        self.slug = "test-history-temple"

    def tearDown(self):
        shutil.rmtree(self.tmp_episodes, ignore_errors=True)

    def test_schema_validator_dossier(self):
        valid_dossier = {
            "topic": "Candi Borobudur",
            "niche": "history",
            "verification_status": "VERIFIED",
            "generated_at": "2026-10-29T03:00:00+07:00",
            "claims": [
                {
                    "claim_id": "claim_1",
                    "statement": "Borobudur dibangun sekitar abad ke-8 dan ke-9 Masehi.",
                    "explanation": "Dibangun pada masa Wangsa Syailendra.",
                    "sources": [{"title": "UNESCO World Heritage", "url": "https://whc.unesco.org/en/list/592"}]
                },
                {
                    "claim_id": "claim_2",
                    "statement": "Struktur disusun tanpa semen menggunakan sistem interlocking batu vulkanik.",
                    "sources": [{"title": "Kemendikbud Balai Konservasi Borobudur", "url": "https://konservasiborobudur.kemdikbud.go.id"}]
                }
            ]
        }
        valid, errs = validate_artifact("dossier", valid_dossier)
        self.assertTrue(valid, f"Validation failed with: {errs}")

        # Invalid (missing claims)
        invalid_dossier = dict(valid_dossier)
        del invalid_dossier["claims"]
        valid, errs = validate_artifact("dossier", invalid_dossier)
        self.assertFalse(valid)

    def test_schema_validator_hook_matrix(self):
        valid_hooks = {
            "topic": "Borobudur",
            "niche": "history",
            "primary_recommendation": "v1",
            "visual_hook_concept": "Cat Historian zooms in on interlocking stone puzzle.",
            "variants": [
                {
                    "id": "v1",
                    "archetype": "paradox",
                    "hook_text": "Candi raksasa ini berdiri seribu tahun tanpa semen!",
                    "cover_lines": [["CANDI", "RAKSASA"], ["TANPA", "SEMEN?"]],
                    "hot_words": ["TANPA", "SEMEN?"],
                    "curiosity_score": 9.5,
                    "clarity_score": 9.0,
                    "visual_score": 9.2,
                    "composite_score": 9.3
                },
                {
                    "id": "v2",
                    "archetype": "high_stakes",
                    "hook_text": "Bagaimana batu seberat jutaan ton bisa saling mengunci?",
                    "cover_lines": [["JUTAAN", "TON"], ["SALING", "MENGUNCI?"]],
                    "hot_words": ["MENGUNCI?"],
                    "curiosity_score": 8.8,
                    "clarity_score": 8.5,
                    "visual_score": 8.9,
                    "composite_score": 8.7
                },
                {
                    "id": "v3",
                    "archetype": "direct_challenge",
                    "hook_text": "Teknik rahasia kuno yang bahkan arsitek modern kagumi.",
                    "cover_lines": [["RAHASIA", "KUNO"], ["ARSITEK", "DUNIA"]],
                    "hot_words": ["RAHASIA"],
                    "curiosity_score": 8.2,
                    "clarity_score": 8.0,
                    "visual_score": 8.5,
                    "composite_score": 8.2
                }
            ]
        }
        valid, errs = validate_artifact("hook_matrix", valid_hooks)
        self.assertTrue(valid, f"Validation failed with: {errs}")

    def test_niche_profiles(self):
        niches = list_supported_niches()
        self.assertIn("science", niches)
        self.assertIn("history", niches)
        self.assertIn("geography", niches)
        self.assertIn("technology", niches)
        self.assertIn("mystery", niches)

        for n in niches:
            prof = get_niche_profile(n)
            self.assertIn("default_environment", prof)
            self.assertIn("color_tokens", prof)
            self.assertIn("presenter", prof)

    def test_workflow_halt_at_gate_1(self):
        engine = WorkflowEngine("test-niche-gate1", niche="history", base_dir=self.tmp_episodes)
        # Run stage 2 (fact research)
        claims = [
            {"claim_id": "c1", "statement": "Fakta sejarah teruji satu.", "sources": [{"title": "Src 1", "url": "https://example.com"}]},
            {"claim_id": "c2", "statement": "Fakta sejarah teruji dua.", "sources": [{"title": "Src 2", "url": "https://example.com"}]}
        ]
        engine.run_stage_2_fact_research("Sejarah Kuno", claims)

        # Run stage 3 (hook generation)
        variants = [
            {"id": "v1", "archetype": "paradox", "hook_text": "Hook 1 test", "cover_lines": [["H1"]], "hot_words": ["H1"], "composite_score": 9.0},
            {"id": "v2", "archetype": "high_stakes", "hook_text": "Hook 2 test", "cover_lines": [["H2"]], "hot_words": ["H2"], "composite_score": 8.5},
            {"id": "v3", "archetype": "direct_challenge", "hook_text": "Hook 3 test", "cover_lines": [["H3"]], "hot_words": ["H3"], "composite_score": 8.0}
        ]
        res = engine.run_stage_3_hook_generation("Sejarah Kuno", variants, "v1", "Cat visual concept")
        self.assertEqual(res["next"], "GATE_1_APPROVAL")
        self.assertEqual(engine.state["current_stage"], 4)
        self.assertEqual(engine.state["status"], "PENDING_USER_APPROVAL")

        # Attempting Stage 5 without Gate 1 approval must raise an error
        with self.assertRaises(RuntimeError):
            engine.run_stage_5_scriptwriting([{"id": "l1", "text": "Tes skrip", "target_seconds": 5}])

    def test_workflow_approval_gate_progression(self):
        engine = WorkflowEngine("test-niche-full", niche="technology", title="Komputasi Kuantum", base_dir=self.tmp_episodes)

        # 1. Fact research
        claims = [
            {"claim_id": "c1", "statement": "Qubit memanfaatkan superposisi kuantum.", "sources": [{"title": "Nature Physics", "url": "https://nature.com"}]},
            {"claim_id": "c2", "statement": "Komputer kuantum memproses kemungkinan secara eksponensial.", "sources": [{"title": "IEEE", "url": "https://ieee.org"}]}
        ]
        engine.run_stage_2_fact_research("Komputasi Kuantum", claims)

        # 2. Hook generation
        variants = [
            {"id": "v1", "archetype": "paradox", "hook_text": "Satu partikel bisa ada di dua tempat sekaligus!", "cover_lines": [["SATU", "PARTIKEL"], ["DUA", "TEMPAT?"]], "hot_words": ["PARTIKEL"], "composite_score": 9.5},
            {"id": "v2", "archetype": "high_stakes", "hook_text": "Kenapa komputer kuantum bisa memecahkan enkripsi?", "cover_lines": [["KOMPUTER", "KUANTUM"]], "hot_words": ["KUANTUM"], "composite_score": 8.9},
            {"id": "v3", "archetype": "sensory_mystery", "hook_text": "Apa yang terjadi di dalam superkonduktor dingin?", "cover_lines": [["RAHASIA", "DINGIN"]], "hot_words": ["DINGIN"], "composite_score": 8.4}
        ]
        engine.run_stage_3_hook_generation("Komputasi Kuantum", variants, "v1", "Cat in physics lab pointing at laser")

        # 3. Gate 1 Approval
        res_g1 = engine.run_stage_4_gate_1_approval(approved_by="Auditor", selected_hook_id="v1", notes="Hook approved")
        self.assertEqual(res_g1["status"], "APPROVED")
        self.assertEqual(engine.state["current_stage"], 5)

        # 4. Scriptwriting
        script_lines = [
            {
                "id": "l1_hook",
                "text": "Pernahkah kamu membayangkan sebuah koin berputar kencang di atas meja yang seolah-olah berada di kedua sisi sekaligus secara bersamaan?",
                "target_seconds": 10,
                "claim_ref": "c1"
            },
            {
                "id": "l2_concept",
                "text": "Di dunia fisika kuantum inilah yang disebut superposisi kuantum di mana sebuah partikel atau qubit bisa berada di banyak kondisi sebelum diukur.",
                "target_seconds": 12,
                "claim_ref": "c1"
            },
            {
                "id": "l3_mechanism",
                "text": "Dengan sifat ajaib ini komputer kuantum mampu memproses jutaan kalkulasi rumit secara serentak membuka batas baru kecerdasan dan enkripsi masa depan.",
                "target_seconds": 12,
                "claim_ref": "c2"
            },
            {
                "id": "l4_outro",
                "text": "Teknologi kuantum perlahan mengubah dunia kita dari laboratorium ke masa depan. Ikuti terus untuk eksplorasi rahasia teknologi berikutnya bersama kami!",
                "target_seconds": 10,
                "claim_ref": "c2"
            }
        ]
        res_s = engine.run_stage_5_scriptwriting(script_lines)
        self.assertEqual(res_s["next"], "GATE_2_APPROVAL")
        self.assertEqual(engine.state["current_stage"], 6)

        # 5. Gate 2 Approval
        res_g2 = engine.run_stage_6_gate_2_approval(approved_by="Auditor", notes="Script approved")
        self.assertEqual(res_g2["status"], "APPROVED")
        self.assertEqual(engine.state["current_stage"], 7)

        # 6. Storyboarding
        scenes = [
            {
                "id": "S01Hook",
                "script_line_id": "l1_hook",
                "durationInFrames": 300,
                "banner_text": "MISTERI SUPERPOSISI KUANTUM",
                "transition_cut": "pageTurn",
                "camera": {"yaw": 6, "push": 1.06},
                "presenter": {"state": "curious", "pointAngle": -20}
            },
            {
                "id": "S02Concept",
                "script_line_id": "l2_concept",
                "durationInFrames": 450,
                "banner_text": "RAHASIA KEKUATAN QUBIT",
                "transition_cut": "tearAway",
                "camera": {"yaw": -6, "push": 1.08},
                "presenter": {"state": "explaining", "pointAngle": -30}
            },
            {
                "id": "S03Mechanism",
                "script_line_id": "l3_mechanism",
                "durationInFrames": 450,
                "banner_text": "JUTAAN PERHITUNGAN SERENTAK",
                "transition_cut": "zoomThrough",
                "camera": {"yaw": 4, "push": 1.10},
                "presenter": {"state": "pointing", "pointAngle": -25}
            },
            {
                "id": "S04Outro",
                "script_line_id": "l4_outro",
                "durationInFrames": 300,
                "banner_text": "FOLLOW UNTUK SAINS BERIKUTNYA",
                "transition_cut": "popUpBook",
                "camera": {"yaw": 4, "push": 1.05},
                "presenter": {"state": "waving", "pointAngle": 0}
            }
        ]
        res_sb = engine.run_stage_7_storyboarding(scenes, env_id="physics-lab")
        self.assertEqual(res_sb["status"], "SUCCESS")
        self.assertEqual(engine.state["current_stage"], 8)

        # 7. Asset Planning
        res_ap = engine.run_stage_8_asset_planning(env_id="physics-lab")
        self.assertEqual(res_ap["status"], "SUCCESS")
        self.assertEqual(engine.state["current_stage"], 9)

        # 8. Audio Planning
        res_aud = engine.run_stage_9_audio_production(is_placeholder=True)
        self.assertEqual(res_aud["status"], "SUCCESS")
        self.assertEqual(engine.state["current_stage"], 10)

        # 9. QA Audit
        res_qa = engine.run_stage_11_qa_audit()
        self.assertEqual(res_qa["status"], "SUCCESS")
        self.assertEqual(engine.state["current_stage"], 12)
        self.assertEqual(engine.state["status"], "PENDING_USER_APPROVAL")

        # 10. Gate 3 Approval
        res_g3 = engine.run_stage_12_gate_3_approval(approved_by="Auditor", notes="Final release approved")
        self.assertEqual(res_g3["status"], "COMPLETED")
        self.assertEqual(engine.state["status"], "COMPLETED")

    def test_resume_preserves_completed_state(self):
        slug = "test-resume-episode"
        engine1 = WorkflowEngine(slug, niche="geography", base_dir=self.tmp_episodes)
        claims = [
            {"claim_id": "c1", "statement": "Danau Toba adalah kaldera supervulkan terbesar di dunia.", "sources": [{"title": "USGS", "url": "https://usgs.gov"}]},
            {"claim_id": "c2", "statement": "Letusan 74.000 tahun lalu mempengaruhi iklim global.", "sources": [{"title": "Nature", "url": "https://nature.com"}]}
        ]
        engine1.run_stage_2_fact_research("Kaldera Danau Toba", claims)

        # Load new engine instance for same slug
        engine2 = WorkflowEngine(slug, base_dir=self.tmp_episodes)
        self.assertEqual(engine2.state["current_stage"], 3)
        self.assertIn(2, engine2.state["completed_stages"])
        self.assertIn("dossier", engine2.state["artifacts"])


if __name__ == "__main__":
    unittest.main()
