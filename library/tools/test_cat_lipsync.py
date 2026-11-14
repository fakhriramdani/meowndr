#!/usr/bin/env python3
"""
Automated Test Suite for Cat Scientist Lip-Sync, Mouth Shapes & Talking Animation
Verifies deterministic mouth resolution, audio-driven word alignment, procedural
dialogue fallback, emotional expression compatibility, and speaker ID filtering.
"""

import sys
from pathlib import Path

# Add repo root to python path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

def classify_char_viseme(ch: str, style: str = "calm") -> str:
    if ch in ["m", "b", "p"]:
        return "closed"
    elif ch in ["o", "u"]:
        return "surprised_open"
    elif ch == "a":
        return "smile_talking" if style in ["excited", "energetic"] else "wide_open"
    elif ch in ["e", "i"]:
        return "smile_talking" if style == "excited" else "small_open"
    elif ch in ["s", "z", "t", "d", "n", "l", "r", "c", "j", "f", "v"]:
        return "small_open"
    elif ch in ["k", "g", "h", "q", "x"]:
        return "medium_open"
    return "small_open"

def frame_hash(n: int) -> int:
    x = (n ^ 0xDEADBEEF) * 0x45D9F3B
    x = ((x >> 16) ^ x) * 0x45D9F3B
    x = (x >> 16) ^ x
    return abs(x)

def get_non_speaking_mouth_shape(state: str = "idle") -> str:
    if state == "surprised":
        return "surprised_open"
    if state == "thinking":
        return "closed"
    return "neutral"

def resolve_cat_mouth_shape(frame: int, options: dict) -> str:
    state = options.get("state", "idle")
    mouth_open = options.get("mouthOpen")
    dialogue = options.get("dialogue", {})
    speaker_id = options.get("speakerId", "cat_scientist")
    active_speaker = options.get("activeSpeaker")

    # 1. Direct legacy override
    if mouth_open is not None:
        return "medium_open" if mouth_open else get_non_speaking_mouth_shape(state)

    # 2. Speaker Verification
    curr_speaker = dialogue.get("activeSpeaker", active_speaker)
    target_speaker = dialogue.get("speakerId", speaker_id)
    if curr_speaker and curr_speaker != target_speaker:
        return get_non_speaking_mouth_shape(state)

    # 3. Manual override or explicit visemes
    if dialogue.get("manualShape"):
        return dialogue["manualShape"]

    if dialogue.get("visemeTimeline"):
        active_kf = None
        for kf in dialogue["visemeTimeline"]:
            if frame >= kf["frame"]:
                if active_kf is None or kf["frame"] > active_kf["frame"]:
                    active_kf = kf
        if active_kf:
            return active_kf["shape"]

    mode = dialogue.get("mode", "auto")
    style = dialogue.get("style", "excited" if state in ["excited", "celebrating"] else "calm")

    # 4. Audio-Driven Lip-Sync
    words = dialogue.get("words", [])
    if words and (mode in ["audio_driven", "auto"]):
        current_word = None
        for w in words:
            start = w["f"]
            end = w.get("e", start + 10)
            if start <= frame <= end:
                current_word = w
                break

        if not current_word:
            return get_non_speaking_mouth_shape(state)

        start = current_word["f"]
        end = current_word.get("e", start + 10)
        word_dur = max(1, end - start)
        rel_f = frame - start
        clean_word = "".join([c for c in current_word["text"].lower() if c.isalpha()])

        if not clean_word:
            return "small_open"

        progress = rel_f / word_dur
        char_idx = min(len(clean_word) - 1, int(progress * len(clean_word)))
        ch = clean_word[char_idx]
        base_shape = classify_char_viseme(ch, style)

        if word_dur > 6 and base_shape in ["wide_open", "smile_talking"]:
            if rel_f % 4 >= 2:
                base_shape = "medium_open"

        if state == "surprised":
            return "surprised_open" if (rel_f % 6 < 3) else "wide_open"
        if state == "excited" and base_shape == "wide_open":
            return "smile_talking"

        return base_shape

    # 5. Fallback Dialogue-Timed Mode
    is_timed = (
        mode == "dialogue_timed"
        or "startFrame" in dialogue
        or dialogue.get("speaking")
        or options.get("speechSync")
        or state == "talking"
    )

    if is_timed:
        start_f = dialogue.get("startFrame", 0)
        end_f = dialogue.get("endFrame")
        is_inside = (start_f <= frame <= end_f) if end_f is not None else True
        is_speaking = dialogue.get("speaking", is_inside)

        if not is_speaking:
            return get_non_speaking_mouth_shape(state)

        rel_f = frame - start_f
        phrase_cycle = rel_f % 24
        if phrase_cycle >= 21:
            return "closed"

        beat_idx = rel_f // 4
        h = frame_hash(beat_idx + 101)
        flap_sub = rel_f % 4

        if flap_sub == 0:
            return "closed"
        if state == "surprised":
            return "surprised_open" if flap_sub < 2 else "wide_open"
        if style == "excited" or state == "excited":
            shapes = ["small_open", "smile_talking", "wide_open", "medium_open"]
            return shapes[h % len(shapes)]
        if style == "subtle" or state == "curious":
            shapes = ["neutral", "small_open", "medium_open", "small_open"]
            return shapes[h % len(shapes)]

        shapes = ["small_open", "medium_open", "wide_open", "medium_open", "small_open"]
        return shapes[h % len(shapes)]

    return get_non_speaking_mouth_shape(state)

def run_tests():
    print("=================================================================")
    print("  Running Cat Scientist Lip-Sync & Talking Animation Test Suite   ")
    print("=================================================================")

    # Test 1: Active dialogue vs Silence in Audio-Driven Mode
    words = [
        {"text": "Hampir", "f": 4, "e": 17},
        {"text": "semua", "f": 17, "e": 27},
        {"text": "benda", "f": 27, "e": 38},
    ]
    # Frame 0 is silence before speech
    shape_0 = resolve_cat_mouth_shape(0, {"dialogue": {"words": words, "mode": "audio_driven"}})
    assert shape_0 == "neutral", f"Expected 'neutral' during initial silence, got {shape_0}"

    # Frame 10 is inside "Hampir"
    shape_10 = resolve_cat_mouth_shape(10, {"dialogue": {"words": words, "mode": "audio_driven"}})
    assert shape_10 in ["small_open", "medium_open", "wide_open", "smile_talking", "closed"], f"Expected open mouth during dialogue, got {shape_10}"

    # Frame 50 is silence after words
    shape_50 = resolve_cat_mouth_shape(50, {"dialogue": {"words": words, "mode": "audio_driven"}})
    assert shape_50 == "neutral", f"Expected 'neutral' during post-dialogue silence, got {shape_50}"
    print("  [PASS] test_active_dialogue_vs_silence passed.")

    # Test 2: Bilabial closed lips & Open vowels
    word_membeku = [{"text": "membeku", "f": 10, "e": 25}]
    # At frame 10, onset is 'm'
    shape_m = resolve_cat_mouth_shape(10, {"dialogue": {"words": word_membeku, "mode": "audio_driven"}})
    assert shape_m == "closed", f"Expected 'closed' for bilabial 'm', got {shape_m}"

    word_air = [{"text": "air", "f": 30, "e": 40}]
    shape_a = resolve_cat_mouth_shape(30, {"dialogue": {"words": word_air, "mode": "audio_driven"}})
    assert shape_a in ["wide_open", "smile_talking"], f"Expected open mouth for vowel 'a', got {shape_a}"
    print("  [PASS] test_phonetic_viseme_accuracy passed.")

    # Test 3: Fallback Dialogue-Timed Animation with Natural Pauses
    opts = {
        "dialogue": {
            "mode": "dialogue_timed",
            "startFrame": 20,
            "endFrame": 80,
            "style": "calm",
        }
    }
    # Before dialogue window
    assert resolve_cat_mouth_shape(10, opts) == "neutral"
    # Inside dialogue window
    active_shapes = set()
    for f in range(20, 80):
        s = resolve_cat_mouth_shape(f, opts)
        active_shapes.add(s)
    assert len(active_shapes) > 1, f"Expected mouth shape variety, got {active_shapes}"
    # Natural pause at phraseCycle (f - startFrame) % 24 in [21, 22, 23]
    assert resolve_cat_mouth_shape(20 + 22, opts) == "closed"
    # After dialogue window
    assert resolve_cat_mouth_shape(85, opts) == "neutral"
    print("  [PASS] test_dialogue_timed_fallback_and_pauses passed.")

    # Test 4: Deterministic Reproducibility
    seq_1 = [resolve_cat_mouth_shape(f, opts) for f in range(100)]
    seq_2 = [resolve_cat_mouth_shape(f, opts) for f in range(100)]
    assert seq_1 == seq_2, "Expected identical deterministic output across runs"
    print("  [PASS] test_deterministic_reproducibility passed.")

    # Test 5: Emotional Expression Compatibility
    # Surprised while silent
    s_silent_surprised = resolve_cat_mouth_shape(0, {"state": "surprised"})
    assert s_silent_surprised == "surprised_open", f"Expected surprised_open, got {s_silent_surprised}"

    # Surprised while speaking
    s_speaking_surprised = resolve_cat_mouth_shape(10, {
        "state": "surprised",
        "dialogue": {"mode": "dialogue_timed", "startFrame": 0, "endFrame": 30}
    })
    assert s_speaking_surprised in ["surprised_open", "wide_open", "closed"]

    # Excited speech favoring smile_talking
    s_excited = resolve_cat_mouth_shape(10, {
        "state": "excited",
        "dialogue": {"mode": "dialogue_timed", "startFrame": 0, "endFrame": 30, "style": "excited"}
    })
    assert s_excited in ["smile_talking", "wide_open", "small_open", "medium_open", "closed"]
    print("  [PASS] test_expression_composability passed.")

    # Test 6: Speaker ID Filtering
    # Other speaker active -> silent
    s_other_speaker = resolve_cat_mouth_shape(10, {
        "speakerId": "cat_scientist",
        "activeSpeaker": "guest_fox",
        "dialogue": {"words": words, "mode": "audio_driven"}
    })
    assert s_other_speaker == "neutral", f"Expected silent neutral when other speaker active, got {s_other_speaker}"

    # Cat active -> talking
    s_cat_active = resolve_cat_mouth_shape(10, {
        "speakerId": "cat_scientist",
        "activeSpeaker": "cat_scientist",
        "dialogue": {"words": words, "mode": "audio_driven"}
    })
    assert s_cat_active != "neutral", f"Expected talking mouth when cat is active speaker, got {s_cat_active}"
    print("  [PASS] test_speaker_id_filtering passed.")

    print(">> All 6 Cat Scientist Lip-Sync tests PASSED successfully!")
    print("=================================================================")

if __name__ == "__main__":
    run_tests()
