"""
ElevenLabs Text-to-Speech API provider implementation.
Supports the official ElevenLabs /with-timestamps API for synchronized
character-to-word timing alignment, configurable voice models, and audio conversion.
"""

import os
import json
import time
import base64
import tempfile
import subprocess
import wave
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

from .base import (
    TTSProvider,
    TTSRequest,
    TTSResponse,
    WordTimestamp,
    AuthenticationError,
    ConfigurationError,
    RateLimitError,
    SynthesisError,
)

DEFAULT_MODEL_ID = "eleven_multilingual_v2"
# Standard default pre-made voice accessible across all account tiers (including Free tier)
DEFAULT_PREMADE_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam

# Models verified to support multilingual Indonesian speech
INDONESIAN_COMPATIBLE_MODELS = {
    "eleven_multilingual_v2",
    "eleven_flash_v2_5",
    "eleven_turbo_v2_5",
}


def load_env_file_if_needed():
    """Helper to ensure .env variables are loaded if not already in os.environ."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent.parent.parent / ".env",
    ]
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip()
                            if k not in os.environ and v:
                                os.environ[k] = v
            except Exception:
                pass


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs REST API Text-to-Speech implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_voice_id: Optional[str] = None,
        default_model_id: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        load_env_file_if_needed()
        if api_key is None:
            self._api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        else:
            self._api_key = api_key.strip()

        if default_voice_id is None:
            self._default_voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "").strip() or DEFAULT_PREMADE_VOICE_ID
        else:
            self._default_voice_id = default_voice_id.strip()

        if default_model_id is None:
            self._default_model_id = os.environ.get("ELEVENLABS_MODEL_ID", "").strip() or DEFAULT_MODEL_ID
        else:
            self._default_model_id = default_model_id.strip()

        self.timeout = timeout
        self.max_retries = max_retries

    @property
    def name(self) -> str:
        return "elevenlabs"

    def validate_configuration(self) -> None:
        """Validates credentials and core configuration."""
        if not self._api_key:
            raise AuthenticationError(
                "ELEVENLABS_API_KEY is missing or empty. Please set it in your environment or .env file."
            )
        if not self._default_voice_id:
            raise ConfigurationError(
                "ELEVENLABS_VOICE_ID is missing. Please configure a valid voice ID."
            )

    def _validate_model_compatibility(self, model_id: str, language: str) -> None:
        """Checks if the chosen model supports the requested language."""
        if language in ("id", "indonesian") and model_id not in INDONESIAN_COMPATIBLE_MODELS:
            # We warn or allow it if user explicitly configured another v2/v3 model, but reject English-only v1 models
            if "monolingual" in model_id.lower() or model_id == "eleven_monolingual_v1":
                raise ConfigurationError(
                    f"Selected model '{model_id}' does not support Indonesian speech. "
                    f"Use 'eleven_multilingual_v2' or 'eleven_flash_v2_5'."
                )

    def _convert_audio_to_wav(self, raw_audio_bytes: bytes, input_format: str = "mp3") -> tuple[bytes, float]:
        """
        Converts input audio data (MP3 or PCM) into broadcast-grade 48kHz mono WAV
        using ffmpeg, and returns (wav_bytes, duration_seconds).
        """
        with tempfile.NamedTemporaryFile(suffix=f".{input_format}", delete=False) as in_f:
            in_f.write(raw_audio_bytes)
            in_path = in_f.name

        out_path = in_path + ".wav"
        try:
            cmd = [
                "ffmpeg", "-v", "error", "-y",
                "-i", in_path,
                "-ar", "48000",
                "-ac", "1",
                out_path
            ]
            subprocess.run(cmd, check=True)

            with wave.open(out_path, "rb") as w:
                nframes = w.getnframes()
                rate = w.getframerate()
                duration = nframes / rate if rate > 0 else 0.0

            with open(out_path, "rb") as f:
                wav_bytes = f.read()

            return wav_bytes, duration
        finally:
            if os.path.exists(in_path):
                os.remove(in_path)
            if os.path.exists(out_path):
                os.remove(out_path)

    def _parse_character_alignment(self, alignment: Dict[str, Any]) -> List[WordTimestamp]:
        """
        Parses ElevenLabs character-level timestamps and aggregates them into word boundaries.
        Documented Limitation: This derives word boundaries from character alignment,
        not phoneme-level forced alignment.
        """
        characters = alignment.get("characters", [])
        starts = alignment.get("character_start_times_seconds", [])
        ends = alignment.get("character_end_times_seconds", [])

        if not characters or len(characters) != len(starts) or len(characters) != len(ends):
            return []

        words: List[WordTimestamp] = []
        current_word_chars: List[str] = []
        current_start: Optional[float] = None
        current_end: Optional[float] = None

        for ch, s, e in zip(characters, starts, ends):
            if ch.isspace():
                if current_word_chars:
                    word_str = "".join(current_word_chars).strip()
                    if word_str and current_start is not None and current_end is not None:
                        words.append(WordTimestamp(word=word_str, start_sec=current_start, end_sec=current_end))
                    current_word_chars = []
                    current_start = None
                    current_end = None
            else:
                if current_start is None:
                    current_start = s
                current_word_chars.append(ch)
                current_end = e

        # Final word
        if current_word_chars and current_start is not None and current_end is not None:
            word_str = "".join(current_word_chars).strip()
            if word_str:
                words.append(WordTimestamp(word=word_str, start_sec=current_start, end_sec=current_end))

        return words

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        """
        Synthesizes speech using the ElevenLabs API.
        Handles retries, rate limits, and parses timestamps.
        """
        self.validate_configuration()

        voice_id = request.voice_id or self._default_voice_id
        model_id = request.model_id or self._default_model_id
        self._validate_model_compatibility(model_id, request.language)

        voice_settings = {
            "stability": request.voice_settings.get("stability", 0.5),
            "similarity_boost": request.voice_settings.get("similarity_boost", 0.75),
            "style": request.voice_settings.get("style", 0.0),
            "use_speaker_boost": request.voice_settings.get("use_speaker_boost", True),
        }

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
        headers = {
            "xi-api-key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "text": request.normalized_text(),
            "model_id": model_id,
            "voice_settings": voice_settings,
        }

        # Query params
        output_format = request.output_format or "mp3_44100_128"
        params = {"output_format": output_format}

        attempt = 0
        last_error = None

        while attempt < self.max_retries:
            attempt += 1
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    params=params,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    data = response.json()
                    audio_b64 = data.get("audio_base64", "")
                    if not audio_b64:
                        raise SynthesisError("ElevenLabs returned empty audio payload.")

                    raw_audio = base64.b64decode(audio_b64)
                    wav_bytes, actual_duration = self._convert_audio_to_wav(raw_audio, input_format="mp3")

                    alignment = data.get("alignment") or data.get("normalized_alignment") or {}
                    words = self._parse_character_alignment(alignment)

                    # Fallback word timing if alignment was empty for any reason
                    if not words:
                        text_words = request.normalized_text().split()
                        dur_per_word = actual_duration / max(1, len(text_words))
                        t = 0.0
                        for w in text_words:
                            words.append(WordTimestamp(word=w, start_sec=t, end_sec=t + dur_per_word))
                            t += dur_per_word

                    return TTSResponse(
                        audio_bytes=wav_bytes,
                        duration_sec=actual_duration,
                        words=words,
                        provider=self.name,
                        model_id=model_id,
                        voice_id=voice_id,
                        sample_rate=48000,
                        cached=False,
                        metadata={
                            "speaker": request.speaker,
                            "line_id": request.line_id,
                            "language": request.language,
                            "alignment_type": "character_to_word_timestamps",
                        }
                    )

                # Handle specific HTTP error codes
                if response.status_code == 401:
                    raise AuthenticationError(
                        "ElevenLabs API authentication failed (HTTP 401). "
                        "Check that ELEVENLABS_API_KEY is valid and has Text-to-Speech permissions."
                    )
                elif response.status_code == 402:
                    error_msg = ""
                    try:
                        error_msg = response.json().get("detail", {}).get("message", "")
                    except Exception:
                        error_msg = response.text[:200]
                    raise ConfigurationError(
                        f"ElevenLabs payment/credit required (HTTP 402). "
                        f"Selected voice '{voice_id}' or account tier error: {error_msg}"
                    )
                elif response.status_code == 404:
                    raise ConfigurationError(
                        f"ElevenLabs resource not found (HTTP 404). "
                        f"Voice ID '{voice_id}' or Model '{model_id}' does not exist."
                    )
                elif response.status_code == 429:
                    # Rate limit - wait with exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    last_error = RateLimitError(
                        f"ElevenLabs rate limit exceeded (HTTP 429). Attempt {attempt}/{self.max_retries}."
                    )
                    continue
                else:
                    err_text = ""
                    try:
                        err_text = json.dumps(response.json().get("detail", response.text))
                    except Exception:
                        err_text = response.text[:200]
                    raise SynthesisError(
                        f"ElevenLabs API error (HTTP {response.status_code}): {err_text}"
                    )

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_error = e
                time.sleep(1.5 * attempt)
                continue

        raise SynthesisError(f"ElevenLabs request failed after {self.max_retries} attempts: {last_error}")
