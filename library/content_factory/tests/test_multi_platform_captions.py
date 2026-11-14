"""
Unit and integration tests for Automated Multi-Platform Caption Generator.
Covers:
  - CharacterValidator
  - HashtagValidator
  - KeywordValidator
  - ContentValidator
  - HashtagIntelligence
  - Generators (Instagram, TikTok, YouTube Shorts)
  - CaptionEngine (input ingestion, script-hash caching, auto-correction loop, deliverable staging)
  - 5 Real-World Topics (Science, Psychology, History, Facts, Technology)
"""

import os
import sys
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.captions import (
    CaptionEngine,
    generate_captions_for_episode,
    HashtagIntelligence,
    CaptionInput,
    CompositeValidator,
    RetentionEngine,
    CaptionScoringSystem,
    AnalyticsOptimizer
)
from library.content_factory.captions.validators import (
    CharacterValidator,
    HashtagValidator,
    KeywordValidator,
    ContentValidator
)
from library.content_factory.captions.generators import (
    InstagramCaptionGenerator,
    TikTokCaptionGenerator,
    YouTubeCaptionGenerator
)
from library.content_factory.schema_validator import validate_artifact_file


class TestCaptionValidators(unittest.TestCase):
    """Test suite for platform validators."""

    def test_character_validator_instagram(self):
        # Empty caption fails
        ok, errs, _ = CharacterValidator.validate_instagram("")
        self.assertFalse(ok)
        self.assertTrue(any("cannot be empty" in e for e in errs))

        # Too long (> 2200) fails
        long_caption = "a" * 2205
        ok, errs, _ = CharacterValidator.validate_instagram(long_caption)
        self.assertFalse(ok)
        self.assertTrue(any("exceeds hard limit" in e for e in errs))

        # Optimal length passes
        good_caption = "Pernahkah kamu penasaran kenapa es batu mengapung di air? Ternyata ada anomali air! Simpan postingan ini ya! #sains"
        ok, errs, warns = CharacterValidator.validate_instagram(good_caption)
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_character_validator_tiktok(self):
        # Empty fails
        ok, errs, _ = CharacterValidator.validate_tiktok("")
        self.assertFalse(ok)

        # > 2200 fails
        ok, errs, _ = CharacterValidator.validate_tiktok("a" * 2205)
        self.assertFalse(ok)

        # Optimal length passes
        ok, errs, _ = CharacterValidator.validate_tiktok("Kenapa es mengapung? Komen di bawah! #sains #edukasi")
        self.assertTrue(ok)

    def test_character_validator_youtube(self):
        # Title <= 100 chars
        ok, errs, _ = CharacterValidator.validate_youtube_title("Kenapa Es Mengapung? (Misteri Anomali Air) 🔬✨")
        self.assertTrue(ok)

        # Title > 100 fails
        ok, errs, _ = CharacterValidator.validate_youtube_title("x" * 105)
        self.assertFalse(ok)

        # Description <= 5000 chars
        ok, errs, _ = CharacterValidator.validate_youtube_description("Deskripsi video penjelasan sains. Subscribe ya! #Shorts #sains")
        self.assertTrue(ok)

        ok, errs, _ = CharacterValidator.validate_youtube_description("x" * 5005)
        self.assertFalse(ok)

    def test_hashtag_validator_spam_ban(self):
        # Prohibited viral tags
        banned_tags = ["#sains", "#fyp", "#foryou"]
        ok, errs, _ = HashtagValidator.validate_tiktok(banned_tags)
        self.assertFalse(ok)
        self.assertTrue(any("#fyp" in e for e in errs))

        # Deduplication
        dup_tags = ["#sains", "#Sains", "#edukasi"]
        ok, errs, _ = HashtagValidator.validate_instagram(dup_tags)
        self.assertFalse(ok)
        self.assertTrue(any("Duplicate" in e for e in errs))

        # Instagram max 5
        too_many = ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5", "#tag6"]
        ok, errs, _ = HashtagValidator.validate_instagram(too_many)
        self.assertFalse(ok)

    def test_content_validator_rules(self):
        # Instagram missing CTA fails
        no_cta = "Pernahkah kamu penasaran? Ini penjelasannya tentang sains. Apa pendapatmu? ✨ #sains #edukasi #fakta"
        ok, errs, _ = ContentValidator.validate_instagram_content(no_cta)
        self.assertFalse(ok)
        self.assertTrue(any("CTA" in e for e in errs))

        # Instagram with Save CTA passes
        with_cta = "Pernahkah kamu penasaran? Ini penjelasannya tentang sains. Apa pendapatmu? 💡 Simpan postingan ini ya! #sains #edukasi #fakta"
        ok, errs, _ = ContentValidator.validate_instagram_content(with_cta)
        self.assertTrue(ok)

        # Excessive emojis (> 3) fails
        emoji_spam = "Kenapa bisa begini? 🌧️✨🔥🚀 Simpan postingan ini ya!"
        ok, errs, _ = ContentValidator.validate_instagram_content(emoji_spam)
        self.assertFalse(ok)
        self.assertTrue(any("maximum 3 emojis" in e for e in errs))

    def test_keyword_validator(self):
        text = "Penjelasan lengkap tentang fenomena anomali air dan kerapatan es."
        ok, errs, _ = KeywordValidator.validate_keywords("Instagram", text, ["anomali air"])
        self.assertTrue(ok)

        # Keyword stuffing detected
        stuffed = "anomali air adalah anomali air karena anomali air sangat anomali air"
        ok, errs, _ = KeywordValidator.validate_keywords("Instagram", stuffed, ["anomali air"])
        self.assertFalse(ok)
        self.assertTrue(any("stuffing" in e for e in errs))


class TestHashtagIntelligence(unittest.TestCase):
    """Test suite for hashtag synthesis and filtering."""

    def test_niche_hashtag_generation(self):
        inp = CaptionInput(
            topic="Kenapa Es Mengapung di Air",
            title="Misteri Anomali Air",
            content_category="science",
            main_keywords=["anomali air", "es"]
        )

        ig_tags = HashtagIntelligence.generate_for_instagram(inp)
        self.assertLessEqual(len(ig_tags), 5)
        self.assertGreaterEqual(len(ig_tags), 3)
        self.assertFalse(any(t.lower() in HashtagIntelligence.BANNED_TAGS for t in ig_tags))

        tt_tags = HashtagIntelligence.generate_for_tiktok(inp)
        self.assertLessEqual(len(tt_tags), 3)
        self.assertGreaterEqual(len(tt_tags), 2)
        self.assertFalse(any(t.lower() in HashtagIntelligence.BANNED_TAGS for t in tt_tags))

        yt_tags = HashtagIntelligence.generate_for_youtube(inp)
        self.assertIn("#Shorts", yt_tags)
        self.assertLessEqual(len(yt_tags), 3)


class TestCaptionGenerators(unittest.TestCase):
    """Test suite for platform-specific caption synthesis."""

    def setUp(self):
        self.sample_input = CaptionInput(
            topic="Kenapa Es Mengapung di Atas Air?",
            title="Misteri Anomali Air Terungkap",
            script_lines=[
                {"id": "l1", "text": "Pernah kepikiran kenapa es batu mengapung di gelasmu?"},
                {"id": "l2", "text": "Air memuai saat membeku di bawah empat derajat Celsius sehingga kerapatannya berkurang."},
                {"id": "l3", "text": "Keren banget kan? Menurutmu gimana? Tulis di komentar ya!"}
            ],
            hook="Pernah kepikiran kenapa es batu mengapung di gelasmu?",
            content_category="science",
            main_keywords=["anomali air", "es batu"],
            channel_name="@meowndr"
        )

    def test_instagram_generator(self):
        res = InstagramCaptionGenerator.generate_validated(self.sample_input)
        self.assertEqual(res.status, "READY")
        self.assertLessEqual(res.character_count, 500)
        self.assertGreaterEqual(res.character_count, 100)
        self.assertLessEqual(len(res.hashtags), 5)
        self.assertTrue("?" in res.caption)
        self.assertTrue(any(w in res.caption.lower() for w in ["simpan", "save", "bagikan"]))

    def test_tiktok_generator(self):
        res = TikTokCaptionGenerator.generate_validated(self.sample_input)
        self.assertEqual(res.status, "READY")
        self.assertLessEqual(res.character_count, 300)
        self.assertGreaterEqual(res.character_count, 50)
        self.assertLessEqual(len(res.hashtags), 3)
        self.assertTrue(any(w in res.caption.lower() for w in ["komen", "komentar", "menurutmu", "?"]))

    def test_youtube_generator(self):
        res = YouTubeCaptionGenerator.generate_validated(self.sample_input)
        self.assertEqual(res.status, "READY")
        self.assertLessEqual(res.title_character_count, 100)
        self.assertGreaterEqual(res.title_character_count, 40)
        self.assertLessEqual(res.description_character_count, 500)
        self.assertGreaterEqual(res.description_character_count, 100)
        self.assertTrue("subscribe" in res.description.lower())
        self.assertIn("#Shorts", res.hashtags)


class TestCaptionEngineIntegration(unittest.TestCase):
    """Integration test suite across 5 diverse topics."""

    TOPICS = [
        ("science", "20-aroma-hujan-petrichor"),
        ("psychology", "07-brain-freeze"),
        ("history", "15-perpustakaan-aleksandria"),
        ("interesting_facts", "16-oksigen-2x-lipat"),
        ("technology", "18-teknologi-penyadapan")
    ]

    def test_all_five_topics(self):
        for niche, slug in self.TOPICS:
            with self.subTest(niche=niche, slug=slug):
                ok, result, msgs = generate_captions_for_episode(slug, force=True)
                self.assertTrue(ok, f"Failed generation for {slug}")
                self.assertEqual(result["status"], "READY")

                bundle = result["bundle"]
                # 1. Instagram
                self.assertEqual(bundle.instagram.status, "READY")
                self.assertLessEqual(bundle.instagram.character_count, 500)
                self.assertGreaterEqual(bundle.instagram.character_count, 100)
                self.assertLessEqual(len(bundle.instagram.hashtags), 5)

                # 2. TikTok
                self.assertEqual(bundle.tiktok.status, "READY")
                self.assertLessEqual(bundle.tiktok.character_count, 300)
                self.assertGreaterEqual(bundle.tiktok.character_count, 50)
                self.assertLessEqual(len(bundle.tiktok.hashtags), 3)

                # 3. YouTube Shorts
                self.assertEqual(bundle.youtube.status, "READY")
                self.assertLessEqual(bundle.youtube.title_character_count, 100)
                self.assertLessEqual(bundle.youtube.description_character_count, 500)
                self.assertIn("#Shorts", bundle.youtube.hashtags)

                # Verify files exist on disk
                for f_name, f_path in result["files"].items():
                    self.assertTrue(os.path.exists(f_path), f"File {f_path} missing")

                # Verify captions.json against schema
                json_path = result["files"]["captions_json"]
                s_ok, s_errs = validate_artifact_file("captions", json_path)
                self.assertTrue(s_ok, f"Schema validation error in {json_path}: {s_errs}")

    def test_caching_and_regeneration(self):
        slug = "20-aroma-hujan-petrichor"
        # 1. Force generate
        engine = CaptionEngine(slug)
        b1, cached1 = engine.generate_captions(force=True)
        engine.save_deliverables(force=True)
        self.assertFalse(cached1)

        # 2. Second run without force should hit cache
        b2, cached2 = engine.generate_captions(force=False)
        self.assertTrue(cached2)
        self.assertEqual(b1.script_hash, b2.script_hash)
        self.assertEqual(b1.instagram.caption, b2.instagram.caption)


class TestThirteenProductionCriteria(unittest.TestCase):
    """
    Verification suite covering all 13 production criteria from the platform-specific
    viral caption & retention engine specification.
    """

    @classmethod
    def setUpClass(cls):
        cls.sample_input = CaptionInput(
            topic="Kenapa Es Mengapung di Atas Air?",
            title="Misteri Anomali Air Terungkap",
            script_lines=[
                {"id": "l1", "text": "Pernah kepikiran kenapa es batu mengapung di gelasmu?"},
                {"id": "l2", "text": "Air memuai saat membeku di bawah empat derajat Celsius sehingga kerapatannya berkurang."},
                {"id": "l3", "text": "Keren banget kan? Menurutmu gimana? Tulis di komentar ya!"}
            ],
            hook="Pernah kepikiran kenapa es batu mengapung di gelasmu?",
            cover_title="ES MENUMPUK DI ATAS AIR?!",
            content_category="science",
            main_keywords=["anomali air", "es batu"],
            channel_name="@meowndr",
            slug="07-brain-freeze"
        )
        cls.ep_dir = Path(REPO_ROOT) / "episodes" / "07-brain-freeze"
        cls.dossier = RetentionEngine.analyze_episode(cls.ep_dir, "07-brain-freeze")

    def test_01_instagram_caption_rules(self):
        res = InstagramCaptionGenerator.generate_validated(self.sample_input)
        self.assertEqual(res.status, "READY")
        self.assertTrue(100 <= res.character_count <= 500)
        self.assertTrue(3 <= len(res.hashtags) <= 5)
        self.assertTrue(any(cta_word in res.caption.lower() for cta_word in ["simpan", "save", "share", "bagikan"]))
        self.assertIsNotNone(res.alternative_caption)
        self.assertGreater(len(res.alternative_caption), 50)
        self.assertGreaterEqual(res.quality_score, 85)

    def test_02_tiktok_caption_rules(self):
        res = TikTokCaptionGenerator.generate_validated(self.sample_input)
        self.assertEqual(res.status, "READY")
        body = res.caption.split("#")[0].strip()
        self.assertLessEqual(len(body), 220)
        self.assertTrue(2 <= len(res.hashtags) <= 3)
        self.assertTrue(any(cta_word in body.lower() for cta_word in ["komen", "komentar", "tulis", "ngalamin", "menurutmu"]))
        self.assertIsNotNone(res.alternative_caption)
        self.assertGreaterEqual(res.quality_score, 85)

    def test_03_youtube_shorts_caption_rules(self):
        res = YouTubeCaptionGenerator.generate_validated(self.sample_input)
        self.assertEqual(res.status, "READY")
        self.assertTrue(100 <= res.description_character_count <= 500)
        self.assertIn("#Shorts", res.hashtags)
        self.assertTrue("subscribe" in res.description.lower())
        self.assertTrue(len(res.search_keywords) >= 8)
        self.assertIsNotNone(res.pinned_comment)
        self.assertGreater(len(res.pinned_comment), 15)

    def test_04_youtube_shorts_dedicated_title_generation(self):
        res = YouTubeCaptionGenerator.generate_validated(self.sample_input)
        self.assertTrue(40 <= res.title_character_count <= 100)
        self.assertIsNotNone(res.alternative_title)
        self.assertNotEqual(res.title, res.alternative_title)
        self.assertGreaterEqual(res.quality_score, 85)

    def test_05_retention_alignment(self):
        self.assertTrue(len(self.dossier.main_topic) > 0)
        self.assertTrue(len(self.dossier.primary_hook) > 0)
        self.assertTrue(len(self.dossier.searchable_keywords) > 0)
        self.assertTrue(len(self.dossier.revelation_keywords) > 0)

    def test_06_curiosity_preservation(self):
        audit = RetentionEngine.audit_consistency(
            "Pernah kepikiran kenapa es batu bisa mengapung di air? Ada rahasia fisikanya!",
            self.dossier
        )
        self.assertTrue(audit.curiosity_preserved)
        self.assertFalse(audit.spoiler_detected)

    def test_07_consistency_checks(self):
        audit = RetentionEngine.audit_consistency(
            "Penjelasan sains tentang kenapa es batu mengapung dan anomali air.",
            self.dossier
        )
        self.assertTrue(audit.is_consistent)

    def test_08_redundancy_checks(self):
        verbatim_caption = f"{self.dossier.primary_hook} {self.dossier.primary_hook}"
        audit = RetentionEngine.audit_consistency(verbatim_caption, self.dossier)
        self.assertTrue(audit.verbatim_repetition)

    def test_09_extended_information_supported(self):
        if self.dossier.most_surprising_revelation:
            extended_cap = f"Fakta tambahan yang tidak sempat masuk video: {self.dossier.most_surprising_revelation}. Fakta sains ini sangat penting!"
            audit = RetentionEngine.audit_consistency(extended_cap, self.dossier)
            self.assertFalse(audit.spoiler_detected)
            self.assertTrue(audit.is_consistent)

    def test_10_hashtag_selection_and_filtering(self):
        inp = CaptionInput(
            topic="Uji Coba Sains",
            title="Sains Keren",
            content_category="science",
            main_keywords=["sains", "fisika"]
        )
        ig_tags = HashtagIntelligence.generate_for_instagram(inp)
        tt_tags = HashtagIntelligence.generate_for_tiktok(inp)
        yt_tags = HashtagIntelligence.generate_for_youtube(inp)

        for tag_set in [ig_tags, tt_tags, yt_tags]:
            self.assertFalse(any(t.lower() in HashtagIntelligence.BANNED_TAGS for t in tag_set))

    def test_11_scoring_logic(self):
        audit = RetentionEngine.audit_consistency("Caption edukasi singkat.", self.dossier)
        score = CaptionScoringSystem.evaluate_instagram("Caption edukasi singkat.", self.sample_input, self.dossier, audit)
        self.assertIsInstance(score.total_score, (int, float))
        score_dict = score.to_dict()
        self.assertIn("hook_strength", score_dict["breakdown"])
        self.assertIn("curiosity_watch_intent", score_dict["breakdown"])
        self.assertIn("platform_compliance", score_dict["breakdown"])

    def test_12_fallback_mechanisms(self):
        # Generator handles empty hook and empty keywords without crashing
        sparse_input = CaptionInput(
            topic="Topik Sederhana",
            title="Judul Sederhana",
            content_category="science"
        )
        res_ig = InstagramCaptionGenerator.generate_validated(sparse_input)
        res_tt = TikTokCaptionGenerator.generate_validated(sparse_input)
        res_yt = YouTubeCaptionGenerator.generate_validated(sparse_input)
        self.assertIsNotNone(res_ig.caption)
        self.assertIsNotNone(res_tt.caption)
        self.assertIsNotNone(res_yt.title)

    def test_13_independent_single_platform_regeneration(self):
        engine = CaptionEngine("07-brain-freeze")
        full_bundle, _ = engine.generate_captions(force=True)

        # Regenerate only TikTok
        tt_bundle, _ = engine.generate_captions(platform="tiktok", force=True)
        self.assertEqual(full_bundle.instagram.caption, tt_bundle.instagram.caption)
        self.assertEqual(full_bundle.youtube.title, tt_bundle.youtube.title)
        self.assertEqual(tt_bundle.tiktok.status, "READY")

    def test_14_zero_double_conditionals_and_sleep_emojis(self):
        """Guarantees no double-conditional grammar ('kenapa jika') and no sleep emojis on non-sleep topics."""
        for slug in ["31-majapahit-poros-maritim", "32-meteor-dinosaurus-meleset"]:
            engine = CaptionEngine(slug)
            bundle, _ = engine.generate_captions(force=True)
            all_text = f"{bundle.instagram.caption} {bundle.tiktok.caption} {bundle.youtube.title} {bundle.youtube.description}".lower()
            self.assertNotIn("kenapa jika", all_text)
            self.assertNotIn("kenapa bagaimana", all_text)
            self.assertNotIn("kenapa ya jika", all_text)
            self.assertNotIn("😴", all_text)

    def test_15_organic_informative_statement_integrity(self):
        """Guarantees captions feature clean, high-retention informative statements without artificial rewatch fluff."""
        for slug in ["31-majapahit-poros-maritim", "32-meteor-dinosaurus-meleset"]:
            engine = CaptionEngine(slug)
            bundle, _ = engine.generate_captions(force=True)
            all_text = f"{bundle.instagram.caption} {bundle.tiktok.caption} {bundle.youtube.description}".lower()
            # Must not contain forced/clumsy rewatch phrasing
            for awkward_phrase in ["coba tonton ulang", "tonton ulang", "tonton sekali lagi"]:
                self.assertNotIn(awkward_phrase, all_text)
            # Must contain substantive informative statements
            self.assertGreater(len(bundle.instagram.caption), 100)
            self.assertGreater(len(bundle.youtube.description), 100)
            self.assertGreater(len(bundle.tiktok.caption), 40)

    def test_16_zero_truncated_title_brackets(self):
        """Guarantees YouTube titles never use clumsy truncated bracket format."""
        for slug in ["31-majapahit-poros-maritim", "32-meteor-dinosaurus-meleset"]:
            engine = CaptionEngine(slug)
            bundle, _ = engine.generate_captions(force=True)
            self.assertFalse("Kenapa Bisa Begini? (" in bundle.youtube.title)
            self.assertFalse(bundle.youtube.title.endswith("... 🔬"))
            self.assertFalse(bundle.youtube.title.endswith("...)"))


if __name__ == "__main__":
    unittest.main()
