"""Server-side NarrationScript pacing and numeric-digit validator."""

from __future__ import annotations

import re

from studio_api.schemas import NarrationScriptState, ScriptBeat

_DIGIT_RE = re.compile(r"[0-9]")
_WORD_RE = re.compile(r"\S+")
WORDS_PER_SEC_1X = 2.65
MAX_DURATION_SEC = 50.0


def analyze_narration_beats(
    beats: list[ScriptBeat],
    measured_audio_duration_sec: float | None = None,
) -> NarrationScriptState:
    """Validate 6-beat Indonesian narration script for 1.0x pacing and zero spoken digits."""
    spoken_text = " ".join(beat.text.strip() for beat in beats if beat.text.strip()).strip()
    words = _WORD_RE.findall(spoken_text)
    word_count = len(words)
    estimated_duration_sec = round(word_count / WORDS_PER_SEC_1X, 1) if word_count > 0 else 0.0
    has_numeric_digits = bool(_DIGIT_RE.search(spoken_text))

    violations: list[str] = []
    if has_numeric_digits:
        violations.append(
            "Spoken NarrationScript must contain 0 numeric digits (spell out numbers in Indonesian)."
        )
    if word_count == 0:
        violations.append("NarrationScript cannot be empty; target 110-135 words (95-105 condensed).")
    if estimated_duration_sec > MAX_DURATION_SEC:
        violations.append(
            f"Estimated 1.0x duration ({estimated_duration_sec:.1f}s) exceeds the 50.0s ceiling; "
            "condense script to 95-105 words. Audio speed-up is prohibited."
        )
    if measured_audio_duration_sec is not None and measured_audio_duration_sec > MAX_DURATION_SEC:
        violations.append(
            f"Audio duration {measured_audio_duration_sec:.1f}s exceeds 50.0s target at 1.0x pace; "
            "artificial speed-up prohibited."
        )

    is_compliant = len(violations) == 0
    return NarrationScriptState(
        beats=beats,
        wordCount=word_count,
        estimatedDurationSec=estimated_duration_sec,
        measuredAudioDurationSec=measured_audio_duration_sec,
        hasNumericDigits=has_numeric_digits,
        isCompliant=is_compliant,
        violations=violations,
    )
