"""
Audio cache manager for deterministic TTS audio reuse.
Caches synthesized audio and word-level timestamps by a stable hash of
normalized text and synthesis parameters, preventing redundant API calls.
"""

import os
import json
import hashlib
import wave
from pathlib import Path
from typing import Optional, Dict, Any

from .base import TTSRequest, TTSResponse, WordTimestamp


DEFAULT_CACHE_DIR = Path(__file__).resolve().parent.parent.parent.parent / ".cache" / "audio"


class AudioCacheManager:
    """Manages persistent disk caching of synthesized speech."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def compute_cache_key(self, request: TTSRequest, provider_name: str) -> str:
        """
        Computes a deterministic SHA-256 hash from all synthesis parameters.
        Excludes transient tokens, API keys, and file paths.
        """
        key_data = {
            "provider": provider_name.strip().lower(),
            "text": request.normalized_text(),
            "model_id": (request.model_id or "").strip(),
            "voice_id": (request.voice_id or "").strip(),
            "voice_settings": sorted(request.voice_settings.items()) if request.voice_settings else [],
            "language": (request.language or "").strip(),
            "output_format": (request.output_format or "").strip(),
            "speed": request.speed,
        }
        serialized = json.dumps(key_data, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:24]

    def get(self, request: TTSRequest, provider_name: str) -> Optional[TTSResponse]:
        """
        Retrieves a valid cached audio response if it exists and passes integrity checks.
        Returns None if cache misses or validation fails.
        """
        cache_key = self.compute_cache_key(request, provider_name)
        wav_path = self.cache_dir / f"{cache_key}.wav"
        meta_path = self.cache_dir / f"{cache_key}.meta.json"

        if not wav_path.exists() or not meta_path.exists():
            return None

        # Validate file size
        if wav_path.stat().st_size < 44 or meta_path.stat().st_size == 0:
            return None

        try:
            # Validate metadata
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

            # Validate WAV integrity and audio duration
            with wave.open(str(wav_path), "rb") as w:
                nframes = w.getnframes()
                framerate = w.getframerate()
                if framerate <= 0 or nframes <= 0:
                    return None
                actual_duration = nframes / framerate

            # Reconstruct word timestamps
            words = [
                WordTimestamp(word=item["w"], start_sec=item["s"], end_sec=item["e"])
                for item in meta.get("words", [])
            ]

            with open(wav_path, "rb") as f:
                audio_bytes = f.read()

            return TTSResponse(
                audio_bytes=audio_bytes,
                duration_sec=actual_duration,
                words=words,
                provider=meta.get("provider", provider_name),
                model_id=meta.get("model_id", request.model_id or ""),
                voice_id=meta.get("voice_id", request.voice_id or ""),
                sample_rate=meta.get("sample_rate", 48000),
                cached=True,
                metadata=meta.get("extra", {}),
            )
        except Exception:
            # On any corruption or read failure, treat as cache miss
            return None

    def put(self, request: TTSRequest, response: TTSResponse) -> Path:
        """
        Stores synthesized audio and non-secret metadata in the cache.
        Returns the saved WAV path.
        """
        cache_key = self.compute_cache_key(request, response.provider)
        wav_path = self.cache_dir / f"{cache_key}.wav"
        meta_path = self.cache_dir / f"{cache_key}.meta.json"

        # Write WAV audio
        with open(wav_path, "wb") as f:
            f.write(response.audio_bytes)

        # Write safe metadata (strictly without credentials)
        meta = response.to_metadata()
        meta["cache_key"] = cache_key
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return wav_path
