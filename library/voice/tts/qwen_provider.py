"""
Qwen3-TTS local neural voice provider.
Wraps the repository's local Qwen3-TTS engine (library/voice/narrate.py).
"""

import os
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Optional

from .base import (
    TTSProvider,
    TTSRequest,
    TTSResponse,
    WordTimestamp,
    ConfigurationError,
    SynthesisError,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Qwen3Provider(TTSProvider):
    """Local Qwen3-TTS neural voice synthesis provider."""

    def __init__(self, python_bin: Optional[str] = None):
        self.python_bin = python_bin or os.environ.get("QWEN_TTS_PY", "python3")

    @property
    def name(self) -> str:
        return "qwen3"

    def validate_configuration(self) -> None:
        """Checks if Qwen3-TTS environment is operational."""
        # Test if qwen_tts is importable in the configured python interpreter
        cmd = [self.python_bin, "-c", "import qwen_tts; import torch"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode != 0:
                raise ConfigurationError(
                    f"Qwen3-TTS is not available in Python interpreter '{self.python_bin}'. "
                    f"Run 'library/voice/setup_tts.sh' or select 'elevenlabs' as provider."
                )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to verify Qwen3-TTS: {e}. Run 'library/voice/setup_tts.sh'."
            )

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        self.validate_configuration()

        # Generate take using narrate.py or subprocess
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            out_wav = tmp_path / f"{request.line_id}_0.wav"

            # Execute generation
            # If Qwen3 is installed, run generation script
            narrate_script = REPO_ROOT / "library" / "voice" / "narrate.py"
            if not narrate_script.exists():
                raise SynthesisError(f"Missing narrate.py at {narrate_script}")

            # Prepare temporary voice.json and script.json
            voice_cfg = {
                "speaker": request.voice_id or "Ryan",
                "language": request.language or "Indonesian",
                "takes_per_line": 1,
            }
            script_cfg = [{"id": request.line_id, "text": request.normalized_text(), "speaker": request.speaker}]

            v_path = tmp_path / "voice.json"
            s_path = tmp_path / "script.json"
            with open(v_path, "w") as f:
                json.dump(voice_cfg, f)
            with open(s_path, "w") as f:
                json.dump(script_cfg, f)

            cmd = [self.python_bin, str(narrate_script), str(v_path), str(s_path), str(tmp_path)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0 or not out_wav.exists():
                raise SynthesisError(f"Qwen3-TTS synthesis failed: {proc.stderr}")

            with open(out_wav, "rb") as f:
                wav_bytes = f.read()

            with wave.open(str(out_wav), "rb") as w:
                dur = w.getnframes() / w.getframerate()

            # Word timing via word count approximation unless ASR is run
            words_list = request.normalized_text().split()
            w_dur = dur / max(1, len(words_list))
            words = [
                WordTimestamp(word=w, start_sec=i * w_dur, end_sec=(i + 1) * w_dur)
                for i, w in enumerate(words_list)
            ]

            return TTSResponse(
                audio_bytes=wav_bytes,
                duration_sec=dur,
                words=words,
                provider=self.name,
                model_id="qwen3-tts",
                voice_id=request.voice_id or "Ryan",
                sample_rate=48000,
                cached=False,
            )
