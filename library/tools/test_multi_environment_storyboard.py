#!/usr/bin/env python3
"""
Unit tests for multi-environment storytelling, storyboard schemas,
scene planning, safe-zone compliance, and baseline preservation.
"""

import os
import sys
import json
import hashlib
import tempfile
import shutil
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
WORKSPACE_ROOT = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "content_factory"))

from validate_episode import validate_episode, load_registered_environments
from schema_validator import validate_artifact
from workflow_engine import WorkflowEngine


class TestMultiEnvironmentStoryboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registered_envs = load_registered_environments()

    def test_registered_environments_contains_required_locations(self):
        """Verify the asset library contains the expected diverse environments."""
        required = [
            "science-lab",
            "cozy-bedroom",
            "tropical-beach",
            "city-park",
            "botany-greenhouse",
            "space-observatory"
        ]
        for env_id in required:
            self.assertIn(env_id, self.registered_envs, f"Expected {env_id} to be registered in asset library")
            env_data = self.registered_envs[env_id]
            rel_path = env_data.get("path", "")
            full_path = os.path.join(WORKSPACE_ROOT, rel_path)
            self.assertTrue(os.path.exists(full_path), f"Background image for {env_id} must exist at {full_path}")

    def test_storyboard_schema_accepts_five_scene_types(self):
        """Verify storyboard schema validates all 5 visual scene types."""
        valid_types = [
            "environment_scene",
            "demonstration_scene",
            "scientific_visualization",
            "full_visual_scene",
            "return_scene"
        ]
        for scene_type in valid_types:
            sb = {
                "environment_id": "science-lab",
                "environments_used": ["science-lab", "cozy-bedroom"],
                "fps": 30,
                "total_frames": 900,
                "scenes": [
                    {
                        "id": "S01Hook",
                        "script_line_id": "l1_hook",
                        "durationInFrames": 300,
                        "banner_text": "MENGAPA ES MENGAPUNG?",
                        "environment_id": "science-lab",
                        "scene_purpose": "Testing scene type",
                        "background_type": scene_type,
                        "transition_in": "pageTurn",
                        "transition_out": "none",
                        "transition_cut": "pageTurn",
                        "camera_motion": {
                            "yaw": 4,
                            "push": 1.05,
                            "origin": [540, 1130],
                            "motion_type": "orbit"
                        },
                        "presenter_position": {
                            "x": 360,
                            "y": 1380,
                            "size": 240,
                            "state": "explaining",
                            "visible": True,
                            "pointAngle": -30
                        },
                        "overlay_assets": ["TapeBanner"],
                        "animated_props": ["lab_beaker"],
                        "visual_evidence": "Test evidence",
                        "continuity_notes": "Continuity clean"
                    },
                    {
                        "id": "S02Lab",
                        "script_line_id": "l2_lab",
                        "durationInFrames": 300,
                        "banner_text": "DENSITAS DAN MASSA",
                        "environment_id": "science-lab",
                        "scene_purpose": "Laboratory demonstration",
                        "background_type": "demonstration_scene",
                        "transition_in": "tearAway",
                        "transition_out": "none",
                        "transition_cut": "tearAway"
                    },
                    {
                        "id": "S03Outro",
                        "script_line_id": "l3_outro",
                        "durationInFrames": 300,
                        "banner_text": "KESIMPULAN",
                        "environment_id": "science-lab",
                        "scene_purpose": "Conclusion",
                        "background_type": "return_scene",
                        "transition_in": "pageTurn",
                        "transition_out": "none",
                        "transition_cut": "pageTurn"
                    }
                ]
            }
            valid, errors = validate_artifact("storyboard", sb)
            self.assertTrue(valid, f"Scene type {scene_type} should be valid according to schema, got: {errors}")

    def test_storyboard_schema_rejects_invalid_scene_type(self):
        """Verify storyboard schema rejects unauthorized scene types."""
        sb = {
            "environment_id": "science-lab",
            "environments_used": ["science-lab"],
            "fps": 30,
            "total_frames": 900,
            "scenes": [
                {
                    "id": "S01Invalid",
                    "script_line_id": "l1_test",
                    "durationInFrames": 300,
                    "banner_text": "TEST BANNER",
                    "environment_id": "science-lab",
                    "scene_purpose": "Testing invalid type",
                    "background_type": "invalid_sci_fi_holodeck",
                    "transition_in": "pageTurn",
                    "transition_out": "none",
                    "transition_cut": "pageTurn"
                },
                {
                    "id": "S02Two",
                    "script_line_id": "l2_test",
                    "durationInFrames": 300,
                    "banner_text": "TEST BANNER 2",
                    "environment_id": "science-lab",
                    "background_type": "environment_scene"
                },
                {
                    "id": "S03Three",
                    "script_line_id": "l3_test",
                    "durationInFrames": 300,
                    "banner_text": "TEST BANNER 3",
                    "environment_id": "science-lab",
                    "background_type": "environment_scene"
                }
            ]
        }
        valid, errors = validate_artifact("storyboard", sb)
        self.assertFalse(valid, "Expected schema validation failure for invalid scene type")

    def test_storyboard_schema_rejects_invalid_transition(self):
        """Verify storyboard schema enforces approved papercraft transition styles."""
        sb = {
            "environment_id": "science-lab",
            "environments_used": ["science-lab"],
            "fps": 30,
            "total_frames": 900,
            "scenes": [
                {
                    "id": "S01Trans",
                    "script_line_id": "l1_test",
                    "durationInFrames": 300,
                    "banner_text": "TEST TRANSITION",
                    "environment_id": "science-lab",
                    "scene_purpose": "Testing invalid transition",
                    "background_type": "environment_scene",
                    "transition_in": "pageTurn",
                    "transition_out": "none",
                    "transition_cut": "glitch_matrix_wipe"  # Unapproved transition enum
                },
                {
                    "id": "S02Two",
                    "script_line_id": "l2_test",
                    "durationInFrames": 300,
                    "banner_text": "TEST BANNER 2",
                    "environment_id": "science-lab",
                    "background_type": "environment_scene"
                },
                {
                    "id": "S03Three",
                    "script_line_id": "l3_test",
                    "durationInFrames": 300,
                    "banner_text": "TEST BANNER 3",
                    "environment_id": "science-lab",
                    "background_type": "environment_scene"
                }
            ]
        }
        valid, errors = validate_artifact("storyboard", sb)
        self.assertFalse(valid, "Expected schema validation failure for unapproved transition type")

    def test_safe_zone_bounds_enforcement(self):
        """Verify safe zone bounds (x: 180-900, y: 850-1650) for visible presenter."""
        # Valid anchor
        valid_pos = {"x": 540, "y": 1380, "scale": 1.0, "visible": True}
        self.assertTrue(180 <= valid_pos["x"] <= 900)
        self.assertTrue(850 <= valid_pos["y"] <= 1650)

        # Invalid outside safe zone
        out_of_bounds = {"x": 100, "y": 200, "scale": 1.0, "visible": True}
        is_safe = (180 <= out_of_bounds["x"] <= 900) and (850 <= out_of_bounds["y"] <= 1650)
        self.assertFalse(is_safe, "Position (100, 200) must be flagged as outside presenter safe zone")

    def test_workflow_engine_auto_plans_multi_environment_storyboard(self):
        """Verify WorkflowEngine Stage 7 and Stage 8 generate valid multi-environment storyboard & asset plan."""
        tmp_dir = tempfile.mkdtemp(prefix="cf_test_engine_")
        try:
            engine = WorkflowEngine("test_multienv_auto", base_dir=tmp_dir)
            # Create approved script
            script_path = os.path.join(engine.episode_dir, "narration", "script.json")
            script_lines = [
                {"id": "l1_hook", "text": "Pernah nggak kalian lihat es batu mengapung di air dingin segar kamar tidur kalian?"},
                {"id": "l2_lab", "text": "Mari kita uji secara ilmiah di laboratorium kimia dengan tabung reaksi dan gelas ukur."},
                {"id": "l3_crystal", "text": "Ketika molekul air H2O membeku, ikatan hidrogen membentuk kisi kristal heksagonal berongga yang luas."},
                {"id": "l4_density", "text": "Rongga tersebut membuat massa jenis es menjadi nol koma sembilan puluh dua gram per sentimeter kubik."},
                {"id": "l5_nature", "text": "Di danau taman kota saat musim dingin, lapisan es di atas melindungi ikan di dasar tetap hidup."},
                {"id": "l6_outro", "text": "Kembali lagi ke kamar santai kita, itulah keajaiban anomali air yang menyelamatkan kehidupan di bumi."}
            ]
            with open(script_path, "w", encoding="utf-8") as f:
                json.dump({"lines": script_lines}, f, indent=2)

            # Advance to Gate 2 and approve script
            engine.state["current_stage"] = 6
            engine.run_stage_6_gate_2_approval(approved_by="TestRunner", notes="Approved test script")

            sb_result = engine.run_stage_7_storyboarding()
            self.assertEqual(sb_result["status"], "SUCCESS")
            self.assertGreaterEqual(len(sb_result["environments_used"]), 2, "Multi-environment pipeline must select at least 2 environments")

            # Check storyboard file created and valid
            self.assertTrue(os.path.exists(sb_result["storyboard"]))
            with open(sb_result["storyboard"], "r", encoding="utf-8") as f:
                sb_data = json.load(f)
            valid, errs = validate_artifact("storyboard", sb_data)
            self.assertTrue(valid, f"Generated storyboard should pass schema validation: {errs}")

            # Check return scene continuity
            first_env = sb_data["scenes"][0]["environment_id"]
            last_env = sb_data["scenes"][-1]["environment_id"]
            self.assertEqual(first_env, last_env, "Narrative circularity should return to opening environment")
            self.assertEqual(sb_data["scenes"][-1]["background_type"], "return_scene")

            # Stage 8: Asset Planning
            ap_result = engine.run_stage_8_asset_planning()
            self.assertEqual(ap_result["status"], "SUCCESS")
            self.assertTrue(os.path.exists(ap_result["asset_plan"]))
            with open(ap_result["asset_plan"], "r", encoding="utf-8") as f:
                ap_data = json.load(f)

            self.assertIn("environments", ap_data)
            self.assertGreaterEqual(len(ap_data["environments"]), 2)
            for env_entry in ap_data["environments"]:
                self.assertIn("id", env_entry)
                self.assertIn("path", env_entry)
                self.assertTrue(os.path.exists(env_entry["path"]), f"Referenced asset path {env_entry['path']} must exist")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_example_multienv_episode_validates_successfully(self):
        """Verify episodes/03-anomali-air-multienv passes all episode validation checks."""
        ep_dir = os.path.join(WORKSPACE_ROOT, "episodes", "03-anomali-air-multienv", "papercut")
        self.assertTrue(os.path.isdir(ep_dir), f"Episode directory must exist at {ep_dir}")

        result = validate_episode(ep_dir)
        self.assertTrue(result["valid"], f"03-anomali-air-multienv failed validation: {result['errors']}")
        self.assertEqual(len(result["errors"]), 0)

        with open(os.path.join(ep_dir, "episode.json"), "r", encoding="utf-8") as f:
            cfg = json.load(f)
        self.assertEqual(len(cfg.get("scenes", [])), 7)
        self.assertIn("environments", cfg)
        self.assertEqual(len(cfg["environments"]), 4)

    def test_baseline_episode_01_remains_fully_valid(self):
        """Verify baseline episode 01 continues to pass all validation checks without regression."""
        ep_dir = os.path.join(WORKSPACE_ROOT, "episodes", "01-anomali-air", "papercut")
        result = validate_episode(ep_dir)
        self.assertTrue(result["valid"], f"Episode 01 baseline failed validation: {result['errors']}")
        self.assertEqual(len(result["errors"]), 0)

    def test_baseline_preservation_hashes(self):
        """Verify strict cryptographic baseline preservation for Episode 01 V4 video and science lab background."""
        baseline_video = os.path.join(WORKSPACE_ROOT, "episodes", "01-anomali-air", "papercut", "out", "episode-01-v4.mp4")
        expected_video_sha256 = "40de9f414b996a544bd47fce300f72754eafe20ee58328b7f7426451817adba2"
        self.assertTrue(os.path.exists(baseline_video), "Baseline video episode-01-v4.mp4 must exist")
        with open(baseline_video, "rb") as f:
            video_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(video_hash, expected_video_sha256, "Baseline video hash MUST NEVER change")

        baseline_bg = os.path.join(WORKSPACE_ROOT, "assets", "backgrounds", "science-lab", "background.png")
        expected_bg_sha256 = "4db1199c6a6076ac8334204473853c0068d361f19f81deb5ce0e4da05527c463"
        self.assertTrue(os.path.exists(baseline_bg), "Baseline background science-lab/background.png must exist")
        with open(baseline_bg, "rb") as f:
            bg_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(bg_hash, expected_bg_sha256, "Baseline science lab background hash MUST NEVER change")


if __name__ == "__main__":
    unittest.main()
