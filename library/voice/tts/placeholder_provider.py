"""
Placeholder TTS provider.
Generates stand-in audio (silent PCM WAV or macOS say) with paced word timestamps,
ensuring animations, previews, and testing can run offline.
"""

import os
import wave
import tempfile
import subprocess
import shutil
import platform
from typing import Optional, List

from .base import (
    TTSProvider,
    TTSRequest,
    TTSResponse,
    WordTimestamp,
)


class PlaceholderProvider(TTSProvider):
    """Stand-in audio synthesizer with paced word duration estimates."""

    def __init__(self, wps: float = 3.0, sample_rate: int = 48000, use_say: bool = False):
        self.wps = wps
        self.sample_rate = sample_rate
        self.use_say = use_say and platform.system() == "Darwin" and shutil.which("say") is not None

    @property
    def name(self) -> str:
        return "placeholder"

    def validate_configuration(self) -> None:
        """Always valid."""
        pass

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        words_list = request.normalized_text().split()
        if not words_list:
            words_list = ["..."]

        if not self.use_say:
            dur = max(0.5, len(words_list) / self.wps + 0.2)
            n_frames = int(dur * self.sample_rate)
            # Create silent 16-bit mono PCM WAV
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                with wave.open(tmp_path, "wb") as w:
                    w.setnchannels(1)
                    w.setsampwidth(2)
                    w.setframerate(self.sample_rate)
                    w.writeframes(b"\x00\x00" * n_frames)

                with open(tmp_path, "rb") as f:
                    audio_bytes = f.read()
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        else:
            with tempfile.TemporaryDirectory() as tmp_dir:
                aiff_path = os.path.join(tmp_dir, "speech.aiff")
                wav_path = os.path.join(tmp_dir, "speech.wav")
                subprocess.run(["say", "-o", aiff_path, request.normalized_text()], check=True)
                subprocess.run(
                    ["ffmpeg", "-v", "error", "-y", "-i", aiff_path, "-ac", "1", "-ar", str(self.sample_rate), wav_path],
                    check=True
                )
                with wave.open(wav_path, "rb") as w:
                    dur = w.getnframes() / w.getframerate()
                with open(wav_path, "rb") as f:
                    audio_bytes = f.read()

        # Weight-based duration distribution (longer words get proportionately more time)
        weights = [len(w) + 2 for w in words_list]
        total_w = sum(weights)
        t = 0.0
        words: List[WordTimestamp] = []
        body_dur = dur - 0.2 if not self.use_say else dur
        for w, wt in zip(words_list, weights):
            d = body_dur * (wt / total_w)
            words.append(WordTimestamp(word=w, start_sec=round(t, 3), end_sec=round(t + d, 3)))
            t += d

        return TTSResponse(
            audio_bytes=audio_bytes,
            duration_sec=dur,
            words=words,
            provider=self.name,
            model_id="placeholder",
            voice_id="silent",
            sample_rate=self.sample_rate,
            cached=False,
            metadata={"status": "STANDIN_PLACEHOLDER"}
        )
