#!/usr/bin/env python3
"""
Narration Audio Generator CLI for Papercraft Content Factory.
Orchestrates speech synthesis across lines using configurable TTS providers
(ElevenLabs, Qwen3, or Placeholder) with persistent caching, word-level alignment,
and automatic timing file generation.

Usage:
    python3 library/tools/generate_narration.py <episode_slug> [--provider elevenlabs] [--force]
"""

import os
import sys
import json
import argparse
import shutil
import wave
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.voice.tts import (
    get_tts_provider,
    synthesize_with_cache,
    AudioCacheManager,
    TTSRequest,
    TTSError,
    ConfigurationError,
    AuthenticationError,
)
from library.content_factory.narration_standard import (
    NarrationValidator,
    IndonesianNumberConverter,
    PunctuationStandard,
)
from library.content_factory.bgm_matcher import (
    match_bgm_for_episode,
    validate_bed_preset,
    get_bed_info,
)
from library.audio.bgm_renderer import render_episode_audio_bed

AUDIO_PLAN_SCHEMA_PATH = REPO_ROOT / "library" / "content_factory" / "schemas" / "audio_plan_schema.json"


def generate_episode_narration(
    episode_slug: str,
    provider_name: str = None,
    force_regenerate: bool = False,
    voice_id: str = None,
    model_id: str = None,
    strict_narration: bool = False,
):
    ep_dir = REPO_ROOT / "episodes" / episode_slug
    if not ep_dir.exists():
        raise FileNotFoundError(f"Episode directory not found: {ep_dir}")

    narration_dir = ep_dir / "narration"
    script_path = narration_dir / "script.json"
    if not script_path.exists():
        raise FileNotFoundError(f"Missing script.json at {script_path}")

    papercut_dir = ep_dir / "papercut"
    ep_cfg_path = papercut_dir / "episode.json"
    ep_cfg = {}
    if ep_cfg_path.exists():
        with open(ep_cfg_path, "r", encoding="utf-8") as f:
            ep_cfg = json.load(f)

    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    # 1. Audit Indonesian Narration Number & Punctuation Standard
    print(">> Auditing script against Indonesian Narration Standard (@meowndr)...")
    narration_audit = NarrationValidator.validate_script(script)
    if narration_audit["errors"]:
        print(f"  [WARN] Script has {len(narration_audit['errors'])} narration standard violations:")
        for err in narration_audit["errors"]:
            print(f"    • {err}")
        if strict_narration:
            raise ValueError(f"Strict narration validation failed with {len(narration_audit['errors'])} blocking error(s).")
    else:
        print("  [PASS] Narration text conforms to Indonesian number & punctuation standards.")

    if narration_audit["warnings"]:
        for warn in narration_audit["warnings"]:
            print(f"  [PACING ADVICE] {warn}")

    # Initialize cache and provider
    cache = AudioCacheManager()
    provider = get_tts_provider(provider_name=provider_name, config=ep_cfg)
    print(f">> Initialized TTS Provider: '{provider.name}'")

    # Validate provider credentials before starting batch
    try:
        provider.validate_configuration()
    except (AuthenticationError, ConfigurationError) as e:
        print(f"[ERROR] Provider configuration check failed: {e}")
        raise

    target_voice_dir = narration_dir / "voice" / "final_narrator"
    target_voice_dir.mkdir(parents=True, exist_ok=True)

    timing_file = narration_dir / ep_cfg.get("timing", "timing_narrator.js")

    order = []
    seg = {}
    speakers = {}
    total_audio_duration = 0.0
    total_words = 0

    cfg_tts = ep_cfg.get("tts", {})
    resolved_voice_id = voice_id or cfg_tts.get("voice_id")
    resolved_model_id = model_id or cfg_tts.get("model_id")

    for line in script:
        line_id = line["id"]
        raw_text = line.get("tts") or line["text"]
        speaker = line.get("speaker", "cat_scientist")
        speakers[line_id] = speaker
        order.append(line_id)

        # Ensure text sent to TTS engine is 100% normalized and speech-rhythm punctuated
        normalized_text, audit = IndonesianNumberConverter.normalize_sentence(raw_text)
        if audit:
            print(f"  [TTS NORMALIZATION] [{line_id}]:")
            for a in audit:
                print(f"    • {a['type']}: '{a['original']}' &rarr; '{a['converted']}'")

        text = normalized_text

        req = TTSRequest(
            text=text,
            line_id=line_id,
            speaker=speaker,
            voice_id=line.get("voice_id") or resolved_voice_id,
            model_id=line.get("model_id") or resolved_model_id,
            voice_settings=line.get("voice_settings") or cfg_tts.get("voice_settings", {}),
            language=line.get("language") or ep_cfg.get("meta", {}).get("language", "id"),
        )

        out_wav_path = target_voice_dir / f"{line_id}.wav"

        # Check if force flag was set to bypass cache
        effective_cache = None if force_regenerate else cache

        print(f"  • Synthesizing [{line_id}] ({speaker}): \"{text[:45]}...\"")
        resp = synthesize_with_cache(req, provider, cache=effective_cache)

        # Write output WAV to final_narrator
        with open(out_wav_path, "wb") as f:
            f.write(resp.audio_bytes)

        rel_wav_path = f"voice/final_narrator/{line_id}.wav"
        seg[line_id] = {
            "dur": round(resp.duration_sec, 3),
            "file": rel_wav_path,
            "speaker": speaker,
            "words": [w.to_dict() for w in resp.words],
        }

        total_audio_duration += resp.duration_sec
        total_words += len(resp.words)
        status_tag = "CACHED" if resp.cached else "GENERATED"
        print(f"    &rarr; [{status_tag}] {resp.duration_sec:.2f}s, {len(resp.words)} words")

    # Write timing_narrator.js
    timing_payload = {
        "provider": provider.name,
        "order": order,
        "seg": seg,
        "speakers": speakers,
    }
    with open(timing_file, "w", encoding="utf-8") as f:
        f.write(f"// Generated by generate_narration.py (provider: {provider.name})\n")
        f.write(f"const VO = {json.dumps(timing_payload, indent=2)};\n")

    print(f">> Wrote timing data to {timing_file}")
    print(f">> Total narration: {total_audio_duration:.2f}s ({total_words} words across {len(script)} lines)")

    # Duration Window Verification (Mandatory Natural Pacing Rule - Zero Speed-Up)
    target_dur = ep_cfg.get("meta", {}).get("targetDurationSeconds", 45)
    max_allowed = min(52.0, target_dur + 5.0) if target_dur else 50.0
    if total_audio_duration > max_allowed:
        print("\n" + "=" * 70)
        print("  [DURATION EXCEEDED & SCRIPT REMEDIATION REQUIRED]")
        print("=" * 70)
        print(f"• Total synthesized voiceover duration: {total_audio_duration:.2f}s")
        print(f"• Target ceiling: {max_allowed:.1f}s (Episode target: {target_dur}s)")
        print(f"• Discrepancy: +{total_audio_duration - max_allowed:.2f}s too long")
        print("----------------------------------------------------------------------")
        print(">> MANDATORY RULE: Artificial speed-up (ffmpeg atempo / playback rate)")
        print("   is STRICTLY PROHIBITED. Narration must remain natural at 1.0x speed.")
        print(">> REQUIRED ACTION: The script is too long. Roll back to Stage 5")
        print("   (Scriptwriting) to condense dialogue and reduce word count")
        print("   (e.g., target 95-105 words) to fit natural 1.0x delivery.")
        print("=" * 70 + "\n")

    # Determine and match BGM bed preset
    meta = ep_cfg.get("meta", {})
    title = meta.get("title", episode_slug)
    topic = meta.get("topic", "")
    niche = ep_cfg.get("niche", meta.get("niche", "science"))
    script_str = " ".join(line.get("text", "") for line in script)

    if ep_cfg.get("bed") and validate_bed_preset(ep_cfg["bed"]):
        chosen_bed = ep_cfg["bed"]
        matched_info = get_bed_info(chosen_bed) or {}
    else:
        bgm_match = match_bgm_for_episode(
            title=title,
            topic=topic,
            niche=niche,
            script_text=script_str
        )
        chosen_bed = bgm_match["preset"]
        matched_info = bgm_match
        ep_cfg["bed"] = chosen_bed
        with open(ep_cfg_file, "w", encoding="utf-8") as f:
            json.dump(ep_cfg, f, indent=2)

    bed_bpm = matched_info.get("bpm", 120)

    # Write audio_plan.json
    audio_dir = ep_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_plan_file = audio_dir / "audio_plan.json"

    audio_plan_data = {
        "voiceover": {
            "path": f"public/vo/voiceover.wav",
            "status": "PRODUCED" if provider.name != "placeholder" else "STANDIN_PLACEHOLDER",
            "provider": provider.name,
            "sample_rate": 48000,
            "word_count": total_words,
            "duration_seconds": round(total_audio_duration, 2),
        },
        "music_bed": {
            "name": chosen_bed,
            "tempo_bpm": bed_bpm,
            "path": "public/audio/music.wav",
        },
        "ducking": {
            "speech_volume": 0.45,
            "silence_volume": 1.0,
            "ease_ms": 400,
        },
        "sfx_cues": [
            {"frame": 0, "cue_type": "paper_cut"},
            {"frame": 90, "cue_type": "page_turn"}
        ]
    }

    with open(audio_plan_file, "w", encoding="utf-8") as f:
        json.dump(audio_plan_data, f, indent=2)
    print(f">> Updated audio plan at {audio_plan_file}")

    # Now execute build_vo.py from papercut_dir to stitch voiceover, captions.json, and plan.json
    print(">> Building voiceover track and scene cuts via build_vo.py...")
    cmd = [sys.executable, str(REPO_ROOT / "library" / "tools" / "build_vo.py")]
    subprocess.run(cmd, cwd=str(papercut_dir), check=True)

    # Synthesize and render matched procedural BGM score for the episode
    print(f">> Synthesizing matched BGM Bed '{chosen_bed}' ({matched_info.get('mood', '')})...")
    try:
        bgm_res = render_episode_audio_bed(episode_slug, bed_name=chosen_bed, force=True)
        print(f">> BGM Bed successfully rendered: {bgm_res.get('music_path')} ({bgm_res.get('size_bytes', 0) / 1024:.1f} KB)")
    except Exception as e:
        print(f"[WARN] Headless BGM render warning: {e}")

    print(">> Narration and Remotion audio assets built successfully!")


def main():
    parser = argparse.ArgumentParser(description="Generate narration audio with TTS providers")
    parser.add_argument("slug", help="Episode slug (e.g. 05-bintang-berkelip)")
    parser.add_argument("--provider", default=None, help="TTS Provider (elevenlabs, qwen3, placeholder)")
    parser.add_argument("--voice-id", default=None, help="ElevenLabs Voice ID")
    parser.add_argument("--model-id", default=None, help="ElevenLabs Model ID")
    parser.add_argument("--force", action="store_true", help="Force regenerate without using cache")
    parser.add_argument("--strict-narration", action="store_true", help="Fail if script has unnormalized digits or violations")
    args = parser.parse_args()

    try:
        generate_episode_narration(
            episode_slug=args.slug,
            provider_name=args.provider,
            force_regenerate=args.force,
            voice_id=args.voice_id,
            model_id=args.model_id,
            strict_narration=args.strict_narration,
        )
    except TTSError as e:
        print(f"\n[FATAL TTS ERROR] {type(e).__name__}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
