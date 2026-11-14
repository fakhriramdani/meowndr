#!/usr/bin/env python3
"""
Unit tests for library/tools/validate_episode.py.
"""

import os
import sys
import shutil
import tempfile
import unittest
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from validate_episode import (
    validate_episode,
    validate_episode_config,
    validate_scene_components,
    validate_plan_and_timing,
    validate_audio_assets,
    scan_for_legacy_leakage,
    load_registered_environments,
)


class TestEpisodeValidator(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="papercraft_test_ep_")
        self.registered_envs = load_registered_environments()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _create_minimal_valid_structure(self, root_dir):
        # episode.json
        cfg = {
            "comp": "EpisodeTest",
            "out": "episode-test",
            "meta": {
                "id": "test-ep",
                "title": "Test Title",
                "topic": "Test Topic",
                "language": "id",
                "targetDurationSeconds": 60,
                "fps": 30,
                "width": 1080,
                "height": 1920
            },
            "environment": {
                "id": "science-lab",
                "floorY": 1380
            },
            "scenes": [
                ["S01Hook", "l1_hook", 0]
            ],
            "banners": {
                "S01Hook": "TEST BANNER"
            }
        }
        with open(os.path.join(root_dir, "episode.json"), "w") as f:
            json.dump(cfg, f)

        # src/scenes/S01Hook.tsx
        scenes_dir = os.path.join(root_dir, "src", "scenes")
        os.makedirs(scenes_dir, exist_ok=True)
        with open(os.path.join(scenes_dir, "S01Hook.tsx"), "w") as f:
            f.write("import React from 'react';\nexport const S01Hook: React.FC = () => <div />;\n")

        with open(os.path.join(scenes_dir, "index.ts"), "w") as f:
            f.write("export {S01Hook} from './S01Hook';\n")

        # src/plan.json
        plan = {
            "fps": 30,
            "durationInFrames": 150,
            "scenes": [
                {
                    "id": "S01Hook",
                    "from": 0,
                    "durationInFrames": 150,
                    "words": [{"text": "Halo", "f": 10}]
                }
            ]
        }
        with open(os.path.join(root_dir, "src", "plan.json"), "w") as f:
            json.dump(plan, f)

        # public/vo/voiceover.wav
        vo_dir = os.path.join(root_dir, "public", "vo")
        os.makedirs(vo_dir, exist_ok=True)
        with open(os.path.join(vo_dir, "voiceover.wav"), "wb") as f:
            f.write(b"RIFFdummydataWAVE")

        audio_dir = os.path.join(root_dir, "public", "audio")
        os.makedirs(audio_dir, exist_ok=True)
        with open(os.path.join(audio_dir, "music.wav"), "wb") as f:
            f.write(b"RIFFdummydataWAVE")

    def test_production_episode_01_valid(self):
        """Episode 01 should pass validation with 0 errors."""
        res = validate_episode("episodes/01-anomali-air/papercut")
        self.assertTrue(res["valid"])
        self.assertEqual(len(res["errors"]), 0)

    def test_minimal_synthetic_valid(self):
        self._create_minimal_valid_structure(self.tmp_dir)
        res = validate_episode(self.tmp_dir)
        self.assertTrue(res["valid"])
        self.assertEqual(len(res["errors"]), 0)

    def test_missing_directory(self):
        res = validate_episode("/path/does/not/exist_12345")
        self.assertFalse(res["valid"])
        self.assertTrue(any("Directory not found" in e for e in res["errors"]))

    def test_missing_episode_json(self):
        res = validate_episode(self.tmp_dir)
        self.assertFalse(res["valid"])
        self.assertTrue(any("Missing configuration file" in e for e in res["errors"]))

    def test_invalid_dimensions(self):
        self._create_minimal_valid_structure(self.tmp_dir)
        with open(os.path.join(self.tmp_dir, "episode.json"), "r") as f:
            cfg = json.load(f)
        cfg["meta"]["width"] = 1920
        cfg["meta"]["height"] = 1080
        with open(os.path.join(self.tmp_dir, "episode.json"), "w") as f:
            json.dump(cfg, f)

        res = validate_episode_config(self.tmp_dir, self.registered_envs)
        self.assertFalse(res["valid"])
        self.assertTrue(any("expected vertical 1080" in e for e in res["errors"]))
        self.assertTrue(any("expected vertical 1920" in e for e in res["errors"]))

    def test_missing_scene_component(self):
        self._create_minimal_valid_structure(self.tmp_dir)
        os.remove(os.path.join(self.tmp_dir, "src", "scenes", "S01Hook.tsx"))

        with open(os.path.join(self.tmp_dir, "episode.json"), "r") as f:
            cfg = json.load(f)
        res = validate_scene_components(self.tmp_dir, cfg)
        self.assertFalse(res["valid"])
        self.assertTrue(any("Scene component file not found" in e for e in res["errors"]))

    def test_short_scene_duration(self):
        self._create_minimal_valid_structure(self.tmp_dir)
        with open(os.path.join(self.tmp_dir, "src", "plan.json"), "w") as f:
            json.dump({
                "fps": 30,
                "durationInFrames": 15,
                "scenes": [{"id": "S01Hook", "from": 0, "durationInFrames": 15}]
            }, f)

        res = validate_plan_and_timing(self.tmp_dir)
        self.assertFalse(res["valid"])
        self.assertTrue(any("less than minimum 1 second" in e for e in res["errors"]))

    def test_missing_audio(self):
        self._create_minimal_valid_structure(self.tmp_dir)
        os.remove(os.path.join(self.tmp_dir, "public", "vo", "voiceover.wav"))

        res = validate_audio_assets(self.tmp_dir)
        self.assertFalse(res["valid"])
        self.assertTrue(any("Missing voiceover audio" in e for e in res["errors"]))

    def test_legacy_leakage_detection(self):
        self._create_minimal_valid_structure(self.tmp_dir)
        # Add legacy prop import to S01Hook
        with open(os.path.join(self.tmp_dir, "src", "scenes", "S01Hook.tsx"), "w") as f:
            f.write("""
import React from 'react';
import {BookStack} from '../props/everyday';
import {Critter} from '../cast/Critter';

export const S01Hook: React.FC = () => (
  <div style={{color: '#E07A5F'}}>
    <Critter />
    <BookStack />
  </div>
);
""")
        res = scan_for_legacy_leakage(self.tmp_dir)
        self.assertFalse(res["valid"])
        self.assertTrue(any("props/everyday" in e for e in res["errors"]))
        self.assertTrue(any("Legacy terracotta" in e for e in res["errors"]))
        self.assertTrue(any("Critter" in e for e in res["errors"]))


if __name__ == "__main__":
    unittest.main()
