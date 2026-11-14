#!/usr/bin/env python3
"""
Unit tests for BGM Matching, Validation, and Audio Pipeline Integration.
"""

import os
import shutil
import tempfile
import unittest
import wave
import struct
from pathlib import Path

from library.content_factory.bgm_matcher import (
    AVAILABLE_BEDS,
    NICHE_DEFAULT_BEDS,
    match_bgm_for_episode,
    get_bed_info,
    list_available_beds,
    validate_bed_preset,
    BEDS_DIR
)
from library.audio.bgm_renderer import (
    find_chrome_binary,
    is_audio_silent,
    render_episode_audio_bed,
)
from library.content_factory.workflow_engine import WorkflowEngine


class TestBgmSystem(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_bgm_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_all_beds_exist_on_disk(self):
        """Verify all 8 canonical beds have their JSON definitions on disk."""
        self.assertEqual(len(AVAILABLE_BEDS), 8)
        for bed_name, bed_info in AVAILABLE_BEDS.items():
            self.assertTrue(validate_bed_preset(bed_name), f"Bed file missing: {bed_name}")
            bed_path = BEDS_DIR / f"{bed_name}.json"
            self.assertTrue(bed_path.exists())
            self.assertGreater(bed_path.stat().st_size, 100)

    def test_bgm_matcher_themes(self):
        """Verify intelligent matching against distinct thematic topics."""
        cases = [
            # Title, Topic, Niche, Expected Bed
            ("Kenapa Minum Es Bikin Dahi Sakit?", "Brain Freeze Reflex", "science", "marimba-Am-120"),
            ("Fotosintesis & Klorofil Tumbuhan", "Botany Greenhouse", "science", "marimba-F-108"),
            ("Menara Tesla & Listrik Nirkabel", "Nikola Tesla Wardenclyffe", "technology", "marimba-G-116"),
            ("Misteri Penyadapan & Intelijen Spionase", "CIA Telecommunication", "mystery", "marimba-heist-Dm-112"),
            ("Jebakan Dopamin & Kecanduan Scroll Media Sosial", "Dopamine Loop", "psychology", "marimba-hr-C-104"),
            ("Kenapa Pas Masuk Kamar Tiba-tiba Lupa?", "Doorway Effect", "psychology", "marimba-hr-C-104"),
            ("Kenapa Minum Kopi Malah Bikin Ngantuk?", "Adenosine Sleep Dynamics", "science", "kalimba-spa-D-100"),
            ("Tragedi Perpustakaan Aleksandria Kuno", "Ancient Civilizations", "history", "kalimba-story-G-66"),
            ("Kenapa Aroma Hujan Begitu Menenangkan?", "Petrichor Atmospheric Chemistry", "geography", "night-rain-piano-F"),
        ]

        for title, topic, niche, expected in cases:
            res = match_bgm_for_episode(title=title, topic=topic, niche=niche)
            self.assertEqual(
                res["preset"],
                expected,
                f"For '{title}' ({niche}), expected '{expected}' but got '{res['preset']}' (scores: {res['all_scores']})"
            )
            self.assertGreater(res["bpm"], 50)
            self.assertTrue(len(res["match_reason"]) > 0)

    def test_niche_defaults(self):
        """Verify generic topics fall back to niche default beds."""
        for niche, default_bed in NICHE_DEFAULT_BEDS.items():
            res = match_bgm_for_episode(title="Topik Edukasi", topic="Umum", niche=niche)
            self.assertEqual(res["preset"], default_bed, f"Niche '{niche}' default mismatch")

    def test_silence_detection(self):
        """Verify silence detection correctly distinguishes silent vs audio-filled WAVs."""
        # 1. Create a 100% silent WAV
        silent_wav = Path(self.tmp_dir) / "silent.wav"
        with wave.open(str(silent_wav), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            # 6 seconds of zero bytes
            wf.writeframes(b"\x00" * (48000 * 2 * 2 * 6))

        is_silent, msg = is_audio_silent(silent_wav, min_duration=5.0)
        self.assertTrue(is_silent)
        self.assertIn("completely zero/silent", msg)

        # 2. Create a non-silent sinusoidal WAV
        tone_wav = Path(self.tmp_dir) / "tone.wav"
        with wave.open(str(tone_wav), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            # 6 seconds of tone
            samples = bytearray()
            for i in range(48000 * 6):
                val = int(8000 * (1 if (i // 100) % 2 else -1))
                samples.extend(struct.pack("<hh", val, val))
            wf.writeframes(samples)

        is_silent, msg = is_audio_silent(tone_wav, min_duration=5.0)
        self.assertFalse(is_silent)
        self.assertIn("Valid non-silent audio", msg)

    def test_workflow_engine_stage_9_matches_bgm(self):
        """Verify WorkflowEngine Stage 9 uses BGM matcher and records bed in audio_plan.json."""
        engine = WorkflowEngine("test-ep-bgm", niche="technology", base_dir=self.tmp_dir)
        engine.title = "Bagaimana Komputer Kuantum Bekerja?"
        engine.topic = "Quantum Superposition & Qubit Gates"

        res = engine.run_stage_9_audio_production(is_placeholder=True)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["bed"], "marimba-G-116")

        # Verify audio_plan.json
        plan_path = Path(res["audio_plan"])
        self.assertTrue(plan_path.exists())
        import json
        with open(plan_path) as f:
            data = json.load(f)
        self.assertEqual(data["music_bed"]["name"], "marimba-G-116")
        self.assertEqual(data["music_bed"]["tempo_bpm"], 116)


if __name__ == "__main__":
    unittest.main()
