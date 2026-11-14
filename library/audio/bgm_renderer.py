#!/usr/bin/env python3
"""
BGM & SFX Audio Renderer for Papercraft Content Factory (@meowndr).
Renders offline procedural music beds and sound effects using headless Chrome/Puppeteer
and Web Audio API engine (library/audio/render.mjs).

Ensures that every episode has high-quality, non-silent BGM tracks matched
to the episode niche, topic, and title.
"""

import os
import sys
import json
import wave
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LIB_AUDIO = REPO_ROOT / "library" / "audio"
RENDER_MJS = LIB_AUDIO / "render.mjs"
CUES_PY = REPO_ROOT / "library" / "tools" / "cues.py"

from library.content_factory.bgm_matcher import (
    match_bgm_for_episode,
    validate_bed_preset,
    get_bed_info,
    AVAILABLE_BEDS
)


def find_chrome_binary() -> Optional[str]:
    """Find a functional Chrome or Chromium binary on the system."""
    env_chrome = os.environ.get("CHROME_PATH")
    if env_chrome and os.path.exists(env_chrome) and os.access(env_chrome, os.X_OK):
        return env_chrome

    candidates = [
        os.path.expanduser("~/.local/bin/chromium"),
        os.path.expanduser("~/.local/bin/google-chrome"),
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        "/snap/bin/google-chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium"
    ]

    for c in candidates:
        if os.path.exists(c) and os.access(c, os.X_OK):
            return c

    for cmd in ["chromium", "google-chrome", "google-chrome-stable", "chromium-browser"]:
        p = shutil.which(cmd)
        if p and os.path.exists(p) and os.access(p, os.X_OK):
            return p

    for search_root in [REPO_ROOT / "library" / "papercut" / "template" / "node_modules" / ".remotion", REPO_ROOT / "episodes"]:
        if search_root.exists():
            for bin_path in search_root.glob("**/headless_shell"):
                if bin_path.is_file() and os.access(bin_path, os.X_OK):
                    return str(bin_path)

    return None


def is_audio_silent(wav_path: Path, min_duration: float = 5.0) -> Tuple[bool, str]:
    """
    Inspect a WAV file to verify if it is missing, unreadable, too short,
    or contains 100% silent (zero) samples.
    
    Returns:
        (is_silent: bool, reason: str)
    """
    if not wav_path.exists():
        return True, f"File does not exist: {wav_path}"

    if wav_path.stat().st_size < 1000:
        return True, f"File too small ({wav_path.stat().st_size} bytes)"

    try:
        with wave.open(str(wav_path), "rb") as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            
            if framerate == 0 or n_frames == 0:
                return True, "WAV has zero frames or zero framerate"

            duration = n_frames / framerate
            if duration < min_duration:
                return True, f"Duration {duration:.2f}s is less than minimum {min_duration:.2f}s"

            # Scan across the WAV file in chunks so sparse SFX tracks (fx.wav)
            # and full BGM beds (music.wav) are both accurately verified.
            chunk_size = 48000
            has_signal = False
            wf.setpos(0)
            while True:
                frames = wf.readframes(chunk_size)
                if not frames:
                    break
                if any(b != 0 for b in frames):
                    has_signal = True
                    break

            if not has_signal:
                return True, f"Audio stream ({n_frames} frames) is completely zero/silent"

            return False, f"Valid non-silent audio ({duration:.2f}s, {n_channels}ch, {framerate}Hz)"
    except Exception as e:
        return True, f"Failed to parse WAV audio: {e}"


def ensure_cues_json(papercut_dir: Path, target_duration: float = 45.0) -> Path:
    """Ensure tools/cues.json exists for audio rendering."""
    tools_dir = papercut_dir / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    cues_file = tools_dir / "cues.json"
    plan_file = papercut_dir / "src" / "plan.json"

    # Try running cues.py if plan.json is available
    if plan_file.exists() and CUES_PY.exists():
        try:
            res = subprocess.run(
                [sys.executable, str(CUES_PY)],
                cwd=str(papercut_dir),
                capture_output=True,
                text=True
            )
            if res.returncode == 0 and cues_file.exists() and cues_file.stat().st_size > 10:
                return cues_file
        except Exception:
            pass

    # If cues_file doesn't exist or is empty, write a clean fallback cue list
    if not cues_file.exists() or cues_file.stat().st_size == 0:
        dur = target_duration
        if plan_file.exists():
            try:
                with open(plan_file, "r") as pf:
                    pdata = json.load(pf)
                    dur = pdata.get("durationInFrames", dur * 30) / pdata.get("fps", 30)
            except Exception:
                pass

        default_cues = {
            "dur": round(dur, 2),
            "cues": [
                {"t": 0.05, "type": "cut"},
                {"t": max(0.5, round(dur - 2.0, 2)), "type": "outro"}
            ]
        }
        with open(cues_file, "w", encoding="utf-8") as f:
            json.dump(default_cues, f, indent=2)

    return cues_file


def render_episode_audio_bed(
    episode_slug: str,
    bed_name: Optional[str] = None,
    force: bool = False
) -> Dict[str, Any]:
    """
    Render or update BGM and SFX audio for an episode.
    
    1. Determines or matches the appropriate BGM bed preset based on niche/title.
    2. Updates episode.json with the matched bed.
    3. Builds tools/cues.json.
    4. Executes library/audio/render.mjs in headless Chrome.
    5. Validates non-silent public/audio/music.wav and fx.wav.
    6. Updates episodes/<slug>/audio/audio_plan.json.
    """
    ep_dir = REPO_ROOT / "episodes" / episode_slug
    papercut_dir = ep_dir / "papercut"
    if not papercut_dir.exists():
        raise FileNotFoundError(f"Papercut directory not found: {papercut_dir}")

    ep_json_path = papercut_dir / "episode.json"
    ep_cfg = {}
    if ep_json_path.exists():
        with open(ep_json_path, "r", encoding="utf-8") as f:
            ep_cfg = json.load(f)

    meta = ep_cfg.get("meta", {})
    title = meta.get("title", episode_slug)
    topic = meta.get("topic", "")
    niche = ep_cfg.get("niche", meta.get("niche", "science"))
    target_dur = float(meta.get("targetDurationSeconds", 45))

    # Read script if available for richer matching
    script_text = ""
    script_path = ep_dir / "narration" / "script.json"
    if script_path.exists():
        try:
            with open(script_path, "r", encoding="utf-8") as sf:
                script_data = json.load(sf)
                if isinstance(script_data, list):
                    script_text = " ".join(line.get("text", "") for line in script_data)
        except Exception:
            pass

    # 1. Determine Bed Preset
    matched_info = None
    if bed_name and validate_bed_preset(bed_name):
        chosen_bed = bed_name
        matched_info = get_bed_info(chosen_bed)
    elif ep_cfg.get("bed") and validate_bed_preset(ep_cfg["bed"]) and not force:
        chosen_bed = ep_cfg["bed"]
        matched_info = get_bed_info(chosen_bed)
    else:
        # Match using intelligent matcher
        match_result = match_bgm_for_episode(
            title=title,
            topic=topic,
            niche=niche,
            script_text=script_text
        )
        chosen_bed = match_result["preset"]
        matched_info = match_result

    # Update episode.json with the matched bed
    ep_cfg["bed"] = chosen_bed
    with open(ep_json_path, "w", encoding="utf-8") as f:
        json.dump(ep_cfg, f, indent=2)

    # 2. Check if existing music.wav is already non-silent and force is not set
    pub_audio = papercut_dir / "public" / "audio"
    pub_audio.mkdir(parents=True, exist_ok=True)
    music_wav = pub_audio / "music.wav"
    fx_wav = pub_audio / "fx.wav"

    if not force:
        music_silent, m_msg = is_audio_silent(music_wav, min_duration=10.0)
        fx_silent, f_msg = is_audio_silent(fx_wav, min_duration=10.0)
        if not music_silent and not fx_silent:
            return {
                "status": "ALREADY_RENDERED",
                "bed": chosen_bed,
                "music_path": str(music_wav),
                "fx_path": str(fx_wav),
                "message": f"Existing non-silent BGM verified: {m_msg}"
            }

    # 3. Ensure Chrome/Chromium is found
    chrome_bin = find_chrome_binary()
    if not chrome_bin:
        raise RuntimeError(
            "No Chrome or Chromium binary found on system. "
            "Please install Chromium or set CHROME_PATH environment variable."
        )

    # 4. Ensure cues.json exists
    cues_file = ensure_cues_json(papercut_dir, target_duration=target_dur)

    # 5. Execute render.mjs via Node.js
    env = os.environ.copy()
    env["CHROME_PATH"] = chrome_bin
    env["PAPERCUT_LIB"] = str(REPO_ROOT / "library")

    cmd = [
        "node",
        str(RENDER_MJS),
        "--cues", str(cues_file.relative_to(papercut_dir)),
        "--bed", chosen_bed,
        "--out", "public/audio"
    ]

    print(f">> Rendering BGM Bed '{chosen_bed}' ({matched_info.get('mood', '')}) via headless Chromium...")
    res = subprocess.run(cmd, cwd=str(papercut_dir), env=env, capture_output=True, text=True)

    if res.returncode != 0:
        err_msg = res.stderr or res.stdout
        raise RuntimeError(f"BGM rendering failed (code {res.returncode}): {err_msg}")

    # 6. Verify rendered files are non-silent
    music_silent, m_msg = is_audio_silent(music_wav, min_duration=5.0)
    if music_silent:
        raise RuntimeError(f"Rendered music.wav failed silence check: {m_msg}")

    fx_silent, f_msg = is_audio_silent(fx_wav, min_duration=5.0)
    if fx_silent:
        print(f"[WARN] Rendered fx.wav note: {f_msg}")

    # 7. Update audio/audio_plan.json
    audio_dir = ep_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    plan_file = audio_dir / "audio_plan.json"

    plan_data = {}
    if plan_file.exists():
        try:
            with open(plan_file, "r", encoding="utf-8") as pf:
                plan_data = json.load(pf)
        except Exception:
            pass

    bpm = matched_info.get("bpm", 120) if matched_info else 120
    plan_data["music_bed"] = {
        "name": chosen_bed,
        "tempo_bpm": bpm,
        "path": "public/audio/music.wav",
        "mood": matched_info.get("mood", "") if matched_info else "",
        "status": "PRODUCED"
    }

    if "ducking" not in plan_data:
        plan_data["ducking"] = {
            "speech_volume": 0.45,
            "silence_volume": 1.0,
            "ease_ms": 400
        }

    with open(plan_file, "w", encoding="utf-8") as pf:
        json.dump(plan_data, pf, indent=2)

    print(f">> BGM '{chosen_bed}' successfully rendered and verified: {music_wav.stat().st_size / 1024:.1f} KB")

    return {
        "status": "SUCCESS",
        "bed": chosen_bed,
        "bpm": bpm,
        "mood": matched_info.get("mood", ""),
        "music_path": str(music_wav),
        "fx_path": str(fx_wav),
        "size_bytes": music_wav.stat().st_size
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 library/audio/bgm_renderer.py <episode_slug> [--bed <name>] [--force]")
        sys.exit(1)

    slug = sys.argv[1]
    bed = None
    force = "--force" in sys.argv

    if "--bed" in sys.argv:
        idx = sys.argv.index("--bed")
        if idx + 1 < len(sys.argv):
            bed = sys.argv[idx + 1]

    try:
        res = render_episode_audio_bed(slug, bed_name=bed, force=force)
        print(f"[OK] {res['status']}: bed '{res['bed']}' -> {res.get('music_path')}")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Failed to render BGM: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
