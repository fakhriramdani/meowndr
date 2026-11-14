"""
Comprehensive Test Suite for Professional AI Illustration Generation System.
Verifies:
1. Visual Identity & Episode Visual Bible Governance
2. Cinematography & Mobile Safe Zones (14 Camera Shots)
3. Cat Scientist Character Consistency & Invariants
4. Visual Variety Engine & Fatigue Prevention
5. Story-Driven 10-Step Narrative Breakdown
6. 7-Section Structured Prompt Engineering
7. 10-Dimensional Quality Assurance (QA) Engine (Target >= 8.0/10)
8. Multi-Pass Candidate Generation & Selection Performance
9. Five Distinct Scene Types:
   - (1) Emotional Character Close-Up
   - (2) Wide Cinematic Environment
   - (3) Complex Scientific Visualization
   - (4) Symbolic Visual Metaphor
   - (5) Dynamic Action Scene
10. End-to-End Pipeline Integration
"""

import os
import sys
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.visual_director import (
    VisualIdentitySystem,
    ColorPalette,
    CinematographyRules,
    CameraShot,
    CAMERA_SHOT_LIBRARY,
    MascotIdentity,
    CharacterConsistencyEngine,
    VisualVarietyEngine,
    SceneVisualFingerprint,
    StoryVisualAnalyzer,
    SceneVisualBrief,
    VisualBible,
    VisualBibleGenerator,
    PromptEngineer,
    StructuredPrompt,
    IllustrationQAEngine,
    IllustrationQAReport,
    CandidateSelector,
    IllustrationCandidate,
    IllustrationEngine,
    generate_illustrations_for_episode,
)
from library.content_factory.visual_director.illustration_engine import get_png_dimensions


class TestProfessionalIllustrationSystem(unittest.TestCase):

    def setUp(self):
        self.output_dir = REPO_ROOT / "library" / "content_factory" / "tests" / "test_visual_output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.engine = IllustrationEngine(repo_root=REPO_ROOT)

    def test_01_visual_identity_and_bible(self):
        """Validates visual identity system and visual bible creation across niches."""
        niches = ["science", "history", "geography", "technology", "mystery", "psychology"]
        for niche in niches:
            palette = VisualIdentitySystem.get_palette(niche)
            self.assertIsNotNone(palette.primary)
            self.assertIsNotNone(palette.secondary)
            self.assertIsNotNone(palette.paper_cream)
            self.assertTrue(palette.primary.startswith("#"))

        bible = VisualBibleGenerator.generate_bible(
            episode_slug="test-quantum-entanglement",
            topic="Keterikatan Kuantum",
            niche="technology",
            script_summary="Partikel terhubung melintasi alam semesta seketika.",
            default_env="science-laboratory"
        )
        self.assertEqual(bible.episode_slug, "test-quantum-entanglement")
        self.assertEqual(bible.niche, "technology")
        self.assertIn("CatScientist", bible.character_appearance["name"])
        self.assertTrue(len(bible.recurring_visual_motifs) >= 3)
        self.assertTrue(len(bible.visual_continuity_rules) >= 4)

        json_path, md_path = VisualBibleGenerator.save_bible(bible, self.output_dir)
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())

    def test_02_cinematography_and_safe_zones(self):
        """Verifies 14-shot camera taxonomy and strict vertical safe zones."""
        distinct_shots = {s.code: s for s in CAMERA_SHOT_LIBRARY.values()}
        self.assertEqual(len(distinct_shots), 14)
        for code, shot in distinct_shots.items():
            self.assertEqual(code, shot.code)
            self.assertTrue(shot.framing_scale > 0)
            self.assertTrue(len(shot.camera_origin) == 2)

        # Check safe zone bounds
        zones = CinematographyRules.SAFE_ZONES
        self.assertEqual(zones["header_banner"], (0, 420))
        self.assertEqual(zones["captions"], (1420, 1920))
        self.assertEqual(zones["stage_action"], (420, 1580))

        # Check presenter position bounds
        p_bounds = CinematographyRules.PRESENTER_BOUNDS
        self.assertEqual(p_bounds["floor_y"], 1380)

    def test_03_character_consistency_invariants(self):
        """Enforces invariant mascot rules: orange fur, white coat, wire spectacles."""
        self.assertEqual(MascotIdentity.FUR_COLOR, "#EA580C")
        self.assertEqual(MascotIdentity.LAB_COAT_COLOR, "#F8FAFC")
        self.assertEqual(MascotIdentity.SPECTACLE_COLOR, "#FDFBF7")

        for state_key in ["curious", "explaining", "pointing", "surprised", "thinking", "celebrating", "waving"]:
            state = MascotIdentity.get_state(state_key)
            self.assertEqual(state.name, state_key)
            prompt_desc = MascotIdentity.get_prompt_description(state_key)
            self.assertIn("#EA580C", prompt_desc)
            self.assertIn("spectacles", prompt_desc)
            self.assertIn("lab coat", prompt_desc)

    def test_04_visual_variety_engine(self):
        """Ensures variety engine avoids consecutive camera, angle, and layout repetition."""
        engine = VisualVarietyEngine()

        # Record first scene: WS on left
        engine.record_scene(SceneVisualFingerprint(
            scene_id="S01",
            shot_type="WS",
            camera_angle="Wide Establishing Shot",
            environment_id="science-laboratory",
            presenter_state="curious",
            presenter_position="left",
            dominant_accent_color="#0284C7",
            focal_subject_type="apparatus"
        ))

        # Check candidate repeating WS on left
        ok, warnings = engine.validate_variety(candidate_shot="WS", candidate_pos="left", candidate_state="curious")
        self.assertFalse(ok)
        self.assertTrue(len(warnings) >= 2)

        # Recommend next shot for beat 1 of 4
        next_shot = engine.recommend_next_shot(scene_purpose="Microscopic explanation", beat_index=1, total_beats=4)
        self.assertNotEqual(next_shot.code, "WS")

    def test_05_story_driven_visual_analyzer(self):
        """Verifies 10-step narrative breakdown translates script into physical models."""
        analyzer = StoryVisualAnalyzer()
        brief = analyzer.analyze_scene(
            scene_id="S02",
            script_text="Ketika suhu melonjak hingga 180 derajat Celsius, batuan granit meleleh liat seperti lilin!",
            niche="science",
            default_env="science-laboratory",
            beat_index=1,
            total_beats=4
        )
        self.assertEqual(brief.scene_id, "S02")
        self.assertIn("background", brief.depth_planes)
        self.assertIn("midground", brief.depth_planes)
        self.assertIn("foreground", brief.depth_planes)
        self.assertTrue(len(brief.visual_subject) > 10)
        self.assertTrue(len(brief.visual_metaphor) > 10)

    def test_06_seven_section_prompt_engineering(self):
        """Validates that PromptEngineer outputs complete 7-section structured prompts."""
        analyzer = StoryVisualAnalyzer()
        brief = analyzer.analyze_scene(
            scene_id="S01",
            script_text="Tahukah kamu, di bawah sana suhu melonjak ekstrem?",
            niche="science",
            default_env="science-laboratory",
            beat_index=0,
            total_beats=4
        )
        bible = VisualBibleGenerator.generate_bible(
            episode_slug="test-ep",
            topic="Test Topic",
            niche="science",
            script_summary="Summary"
        )
        prompt = PromptEngineer.generate_prompt(brief, bible)
        full_text = prompt.build_full_prompt()

        required_sections = [
            "[SUBJECT]:",
            "[SCENE & ENVIRONMENT]:",
            "[COMPOSITION & CINEMATOGRAPHY]:",
            "[LIGHTING & SHADOWS]:",
            "[ART DIRECTION & TEXTURE]:",
            "[TECHNICAL SPECIFICATIONS]:",
            "[NEGATIVE CONSTRAINTS]:"
        ]
        for sec in required_sections:
            self.assertIn(sec, full_text)

        # Check negative prompt coverage
        self.assertIn("photorealistic", full_text)
        self.assertIn("3D CGI", full_text)
        self.assertIn("human presenter", full_text)

    def test_07_ten_dimensional_qa_engine(self):
        """Evaluates 10-dimensional QA auditor, critical thresholds, and scoring."""
        analyzer = StoryVisualAnalyzer()
        brief = analyzer.analyze_scene(
            scene_id="S01",
            script_text="Suhu melonjak drastis pada kedalaman ekstrem.",
            niche="science",
            default_env="science-laboratory",
            beat_index=0,
            total_beats=4
        )
        bible = VisualBibleGenerator.generate_bible("slug", "Topic", "science", "text")

        # Evaluate standard 1080x1920
        report = IllustrationQAEngine.evaluate_illustration(
            image_path="test_image.png",
            brief=brief,
            bible=bible,
            attempt=1,
            image_dimensions=(1080, 1920)
        )
        self.assertGreaterEqual(report.overall_score, 8.0)
        self.assertEqual(report.verdict, "APPROVED")
        self.assertEqual(len(report.dimension_scores), 10)

        # Evaluate non-standard dimensions -> triggers critical flaw
        bad_report = IllustrationQAEngine.evaluate_illustration(
            image_path="test_bad.png",
            brief=brief,
            bible=bible,
            attempt=1,
            image_dimensions=(500, 500)
        )
        self.assertEqual(bad_report.verdict, "RETRY_REQUIRED")
        self.assertTrue(len(bad_report.detected_flaws) > 0)

    def test_08_candidate_selection_performance(self):
        """Tests candidate ranking, winning asset selection, and audit metadata."""
        analyzer = StoryVisualAnalyzer()
        brief = analyzer.analyze_scene("S01", "Text", "science", "science-laboratory", 0, 4)
        bible = VisualBibleGenerator.generate_bible("slug", "Topic", "science", "text")

        rep1 = IllustrationQAEngine.evaluate_illustration("c1.png", brief, bible, attempt=1, image_dimensions=(1080, 1920))
        rep2 = IllustrationQAEngine.evaluate_illustration("c2.png", brief, bible, attempt=1, image_dimensions=(1080, 1920))

        # Artificial tweak to distinguish score
        rep2.overall_score = 9.45

        c1 = IllustrationCandidate("c1", "c1.png", "prompt1", rep1, "now")
        c2 = IllustrationCandidate("c2", "c2.png", "prompt2", rep2, "now")

        winner = CandidateSelector.select_best_candidate([c1, c2])
        self.assertEqual(winner.candidate_id, "c2")
        self.assertTrue(winner.is_selected)
        self.assertFalse(c1.is_selected)

        meta = CandidateSelector.compile_selection_metadata("S01", [c1, c2])
        self.assertEqual(meta["selected_candidate_id"], "c2")
        self.assertEqual(len(meta["candidates_audit"]), 2)

    def test_09_five_distinct_scene_types(self):
        """
        Rigorously verifies 5 distinct visual scene types:
        1. Emotional character close-up (MCU/CU)
        2. Wide cinematic environment (WS/EWS)
        3. Complex scientific visualization (ECU/LA)
        4. Symbolic visual metaphor (SYM/MS)
        5. Dynamic action scene (DA/LA)
        """
        bible = VisualBibleGenerator.generate_bible(
            episode_slug="test-five-scenes",
            topic="Five Distinct Visual Scene Demonstrations",
            niche="science",
            script_summary="Multi-scene benchmark"
        )

        test_cases = [
            {
                "type_name": "1. Emotional Character Close-Up",
                "scene_id": "SCENE_01_EMOTIONAL_CLOSEUP",
                "shot_code": "MCU",
                "presenter_state": "curious",
                "script_text": "Banyak yang mengira lubang ini ditutup karena suara jeritan misterius...",
                "subject": "Cat Scientist mascot in curious realization with wireframe spectacles and tilted ears",
                "metaphor": "Intimate character realization diorama with ambient warm amber lighting",
            },
            {
                "type_name": "2. Wide Cinematic Environment",
                "scene_id": "SCENE_02_WIDE_ENVIRONMENT",
                "shot_code": "WS",
                "presenter_state": "explaining",
                "script_text": "Inilah stasiun pengeboran Kola, proyek ambisius sedalam dua belas kilometer!",
                "subject": "Expansive subterranean geological research station with layered bedrock strata",
                "metaphor": "Monumental cross-section papercraft wall showing Earth crust tier levels",
            },
            {
                "type_name": "3. Complex Scientific Visualization",
                "scene_id": "SCENE_03_COMPLEX_SCIENTIFIC",
                "shot_code": "ECU",
                "presenter_state": "pointing",
                "script_text": "Di kedalaman ekstrem, suhu mencapai 180 derajat Celsius dan tekanan 3000 atmosfer!",
                "subject": "Precision laboratory mercury thermometer with vibrating pressure gauge dials",
                "metaphor": "Calibrated dual physical indicator apparatus with thermal ripple shockwaves",
            },
            {
                "type_name": "4. Symbolic Visual Metaphor",
                "scene_id": "SCENE_04_SYMBOLIC_METAPHOR",
                "shot_code": "SYM",
                "presenter_state": "thinking",
                "script_text": "Batuan granit di bawah sana tidak lagi padat, melainkan melunak liat seperti lilin!",
                "subject": "Hexagonal molecular lattice diorama contrasting rigid granite with plastic deformation",
                "metaphor": "Tiered cardstock melting candle analogy morphing into viscous geological flow",
            },
            {
                "type_name": "5. Dynamic Action Scene",
                "scene_id": "SCENE_05_DYNAMIC_ACTION",
                "shot_code": "DA",
                "presenter_state": "surprised",
                "script_text": "Setiap kali bor ditarik, lubang batuan langsung mengalir menutup kembali dengan cepat!",
                "subject": "High-velocity rotating drill head encountering viscous rock collapse with kinetic particles",
                "metaphor": "Dynamic diagonal energy shockwave with paper particle debris trails and speed lines",
            }
        ]

        for tc in test_cases:
            shot = CinematographyRules.get_shot(tc["shot_code"])
            brief = SceneVisualBrief(
                scene_id=tc["scene_id"],
                script_text=tc["script_text"],
                main_concept=tc["type_name"],
                intended_emotion="scientific awe and intrigue",
                visual_subject=tc["subject"],
                visual_metaphor=tc["metaphor"],
                environment_id="science-laboratory",
                camera_shot=shot,
                composition_notes="Vertical 9:16 frame. Active stage zone respected.",
                lighting_notes="Directional top-left paper shadow casting.",
                presenter_action="Actively interacting with focal subject.",
                presenter_state=tc["presenter_state"],
                depth_planes={
                    "background": "Science lab wall cutouts at z=0",
                    "midground": f"Physical {tc['subject']} at z=0.5",
                    "foreground": "Deckle edge framing cutouts at z=1.0"
                }
            )

            # Generate candidate illustrations
            candidates = self.engine.generate_scene_candidates(
                brief=brief,
                bible=bible,
                output_dir=self.output_dir,
                num_candidates=2,
                max_retries=3
            )
            self.assertEqual(len(candidates), 2)

            # Select best candidate
            winner = CandidateSelector.select_best_candidate(candidates)
            self.assertIsNotNone(winner)
            self.assertEqual(winner.qa_report.verdict, "APPROVED")
            self.assertGreaterEqual(winner.qa_report.overall_score, 8.0)

            # Check that PNG exists and verify dimensions 1080x1920
            png_file = Path(winner.image_path)
            self.assertTrue(png_file.exists())
            dims = get_png_dimensions(png_file)
            self.assertEqual(dims, (1080, 1920))

            print(f"  [PASS] {tc['type_name']} -> Score: {winner.qa_report.overall_score}/10.0, Verdict: {winner.qa_report.verdict}")

    def test_10_end_to_end_episode_generation(self):
        """Tests full episode illustration flow on an existing episode."""
        ok, manifest, msgs = generate_illustrations_for_episode("22-kola-superdeep-borehole", force=True)
        self.assertTrue(ok)
        self.assertGreaterEqual(manifest["average_qa_score"], 8.0)
        self.assertTrue(manifest["all_scenes_approved"])
        self.assertEqual(manifest["total_scenes"], 4)
        for s in manifest["scenes"]:
            self.assertEqual(s["verdict"], "APPROVED")
            self.assertTrue((REPO_ROOT / s["png_path"]).exists())


if __name__ == "__main__":
    unittest.main()
