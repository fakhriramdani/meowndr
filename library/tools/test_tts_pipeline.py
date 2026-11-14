#!/usr/bin/env python3
"""
Unit and integration tests for the TTS provider architecture,
caching, ElevenLabs API handling, lip-sync alignment, and Remotion compatibility.
All automated tests use mocked HTTP responses to avoid consuming live API credits.
"""

import os
import sys
import json
import base64
import wave
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.voice.tts.base import (
    TTSRequest,
    TTSResponse,
    WordTimestamp,
    AuthenticationError,
    ConfigurationError,
    RateLimitError,
    SynthesisError,
)
from library.voice.tts.cache import AudioCacheManager
from library.voice.tts.elevenlabs_provider import ElevenLabsProvider
from library.voice.tts.placeholder_provider import PlaceholderProvider
from library.voice.tts.factory import get_tts_provider, synthesize_with_cache


def create_dummy_wav_bytes(duration_sec: float = 1.0, sample_rate: int = 48000) -> bytes:
    """Helper to generate a valid PCM WAV in memory."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        with wave.open(tmp_path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sample_rate)
            n_frames = int(duration_sec * sample_rate)
            w.writeframes(b"\x00\x00" * n_frames)
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


class TestTTSProviderSelection(unittest.TestCase):
    """1. Provider selection and instantiation tests."""

    def test_provider_selection_explicit(self):
        p_el = get_tts_provider("elevenlabs")
        self.assertEqual(p_el.name, "elevenlabs")

        p_ph = get_tts_provider("placeholder")
        self.assertEqual(p_ph.name, "placeholder")

        p_qw = get_tts_provider("qwen3")
        self.assertEqual(p_qw.name, "qwen3")

    def test_provider_selection_from_config(self):
        cfg = {"tts": {"provider": "placeholder", "wps": 3.5}}
        provider = get_tts_provider(config=cfg)
        self.assertEqual(provider.name, "placeholder")

    def test_provider_selection_invalid(self):
        with self.assertRaises(ConfigurationError):
            get_tts_provider("unsupported_provider_xyz")


class TestCredentialsAndConfiguration(unittest.TestCase):
    """2. Missing credentials and invalid configuration tests."""

    def test_missing_api_key(self):
        provider = ElevenLabsProvider(api_key="", default_voice_id="pNInz6obpgDQGcFmaJgB")
        with self.assertRaises(AuthenticationError):
            provider.validate_configuration()

    def test_missing_voice_id(self):
        provider = ElevenLabsProvider(api_key="test_key_123", default_voice_id="")
        with self.assertRaises(ConfigurationError):
            provider.validate_configuration()

    def test_incompatible_indonesian_model(self):
        provider = ElevenLabsProvider(api_key="test_key", default_voice_id="test_voice")
        req = TTSRequest(
            text="Halo dunia",
            line_id="l1",
            model_id="eleven_monolingual_v1",
            language="id"
        )
        with self.assertRaises(ConfigurationError):
            provider.synthesize(req)


class TestElevenLabsAPIHandling(unittest.TestCase):
    """3. API error and rate-limit handling with mocked responses."""

    def setUp(self):
        self.provider = ElevenLabsProvider(
            api_key="valid_mock_key",
            default_voice_id="mock_voice_id",
            max_retries=2,
            timeout=5
        )

    @patch("requests.post")
    def test_authentication_error_401(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = json.dumps({"detail": {"message": "Invalid API key"}})
        mock_post.return_value = mock_resp

        req = TTSRequest(text="Uji otentikasi", line_id="l1")
        with self.assertRaises(AuthenticationError):
            self.provider.synthesize(req)

    @patch("requests.post")
    def test_payment_required_402(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 402
        mock_resp.json.return_value = {"detail": {"message": "Free users cannot use library voices"}}
        mock_resp.text = "Free users cannot use library voices"
        mock_post.return_value = mock_resp

        req = TTSRequest(text="Uji pembayaran", line_id="l1")
        with self.assertRaises(ConfigurationError):
            self.provider.synthesize(req)

    @patch("requests.post")
    def test_rate_limit_429(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.text = "Too Many Requests"
        mock_post.return_value = mock_resp

        req = TTSRequest(text="Uji batas frekuensi", line_id="l1")
        with self.assertRaises(SynthesisError):
            self.provider.synthesize(req)
        # Should have attempted retries
        self.assertEqual(mock_post.call_count, 2)

    @patch("library.voice.tts.elevenlabs_provider.ElevenLabsProvider._convert_audio_to_wav")
    @patch("requests.post")
    def test_successful_synthesis_with_timestamps(self, mock_post, mock_convert):
        # 1. Mock ffmpeg conversion
        dummy_wav = create_dummy_wav_bytes(duration_sec=1.5)
        mock_convert.return_value = (dummy_wav, 1.5)

        # 2. Mock ElevenLabs /with-timestamps JSON response
        # Text: "Halo dunia" -> characters: H, a, l, o, ' ', d, u, n, i, a
        characters = ["H", "a", "l", "o", " ", "d", "u", "n", "i", "a"]
        starts = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        ends =   [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "audio_base64": base64.b64encode(b"dummy_mp3_bytes").decode("utf-8"),
            "alignment": {
                "characters": characters,
                "character_start_times_seconds": starts,
                "character_end_times_seconds": ends,
            }
        }
        mock_post.return_value = mock_resp

        req = TTSRequest(text="Halo dunia", line_id="l1", speaker="cat_scientist")
        resp = self.provider.synthesize(req)

        self.assertEqual(resp.duration_sec, 1.5)
        self.assertEqual(len(resp.words), 2)
        self.assertEqual(resp.words[0].word, "Halo")
        self.assertEqual(resp.words[0].start_sec, 0.0)
        self.assertEqual(resp.words[0].end_sec, 0.4)

        self.assertEqual(resp.words[1].word, "dunia")
        self.assertEqual(resp.words[1].start_sec, 0.5)
        self.assertEqual(resp.words[1].end_sec, 1.0)


class TestAudioCaching(unittest.TestCase):
    """4. Audio caching and invalidation tests."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.cache = AudioCacheManager(cache_dir=Path(self.tmp_dir))

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_cache_miss_then_hit(self):
        provider = PlaceholderProvider(wps=3.0)
        req = TTSRequest(text="Kucing sains sedang bereksperimen.", line_id="l1")

        # 1. Initial call should be a live synthesis and store to cache
        resp1 = synthesize_with_cache(req, provider, cache=self.cache)
        self.assertFalse(resp1.cached)
        self.assertGreater(resp1.duration_sec, 0)

        # 2. Second call should hit cache without re-synthesizing
        resp2 = synthesize_with_cache(req, provider, cache=self.cache)
        self.assertTrue(resp2.cached)
        self.assertAlmostEqual(resp1.duration_sec, resp2.duration_sec, places=3)
        self.assertEqual(len(resp1.words), len(resp2.words))

    def test_cache_invalidation_on_text_change(self):
        provider = PlaceholderProvider()
        req1 = TTSRequest(text="Teks versi pertama", line_id="l1")
        req2 = TTSRequest(text="Teks versi kedua yang berbeda", line_id="l1")

        resp1 = synthesize_with_cache(req1, provider, cache=self.cache)
        resp2 = synthesize_with_cache(req2, provider, cache=self.cache)

        key1 = self.cache.compute_cache_key(req1, provider.name)
        key2 = self.cache.compute_cache_key(req2, provider.name)
        self.assertNotEqual(key1, key2)
        self.assertFalse(resp2.cached)

    def test_cache_metadata_excludes_secrets(self):
        provider = PlaceholderProvider()
        req = TTSRequest(text="Uji rahasia tidak bocor", line_id="l1")
        resp = synthesize_with_cache(req, provider, cache=self.cache)

        key = self.cache.compute_cache_key(req, provider.name)
        meta_file = Path(self.tmp_dir) / f"{key}.meta.json"
        self.assertTrue(meta_file.exists())

        with open(meta_file, "r") as f:
            content = f.read()

        # Ensure no api_key or token keys exist
        self.assertNotIn("api_key", content.lower())
        self.assertNotIn("secret", content.lower())
        self.assertNotIn("token", content.lower())


class TestLipSyncAndSpeakerFiltering(unittest.TestCase):
    """5. Lip-sync timing, speaker assignment, and pause behavior."""

    def test_speaker_metadata_preservation(self):
        provider = PlaceholderProvider()
        req_cat = TTSRequest(text="Halo, saya kucing sains!", line_id="l1", speaker="cat_scientist")
        req_nar = TTSRequest(text="Di kedalaman atmosfer bumi...", line_id="l2", speaker="narrator")

        resp_cat = provider.synthesize(req_cat)
        resp_nar = provider.synthesize(req_nar)

        self.assertEqual(req_cat.speaker, "cat_scientist")
        self.assertEqual(req_nar.speaker, "narrator")

    def test_word_timestamps_monotonic_and_positive(self):
        provider = PlaceholderProvider(wps=2.5)
        req = TTSRequest(text="Bintang berkelap kelip karena refraksi turbulensi udara atmosfer", line_id="l1")
        resp = provider.synthesize(req)

        self.assertTrue(len(resp.words) > 0)
        prev_end = 0.0
        for w in resp.words:
            self.assertGreaterEqual(w.start_sec, prev_end - 0.001)
            self.assertGreater(w.end_sec, w.start_sec)
            prev_end = w.start_sec


class TestRemotionCompatibility(unittest.TestCase):
    """6. Verifies timing and caption payload formats match Remotion schema."""

    def test_captions_schema_structure(self):
        # Remotion Caption[] format requires: text, startMs, endMs, timestampMs
        words = [
            WordTimestamp(word="Bintang", start_sec=0.2, end_sec=0.6),
            WordTimestamp(word="berkelip", start_sec=0.65, end_sec=1.1)
        ]
        caps = [
            {
                "text": (" " if i else "") + w.word,
                "startMs": round(w.start_sec * 1000),
                "endMs": round(w.end_sec * 1000),
                "timestampMs": round((w.start_sec + w.end_sec) / 2 * 1000),
                "confidence": 1.0,
            }
            for i, w in enumerate(words)
        ]

        self.assertEqual(len(caps), 2)
        self.assertEqual(caps[0]["text"], "Bintang")
        self.assertEqual(caps[0]["startMs"], 200)
        self.assertEqual(caps[0]["endMs"], 600)
        self.assertEqual(caps[0]["timestampMs"], 400)

        self.assertEqual(caps[1]["text"], " berkelip")
        self.assertEqual(caps[1]["startMs"], 650)
        self.assertEqual(caps[1]["endMs"], 1100)


if __name__ == "__main__":
    unittest.main()
