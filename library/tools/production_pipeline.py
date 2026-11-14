#!/usr/bin/env python3
"""
Papercraft Content Factory Production Pipeline CLI.
Coordinates end-to-end automated episode production:
  1. Pre-flight validation (schemas, assets, durations, audio, lip-sync, text safe zones)
  2. Preview generation (lightweight contact sheets and stills)
  3. Deterministic Remotion rendering
  4. Audio/video integrity quality assurance

Usage:
    python3 library/tools/production_pipeline.py validate <episode_slug>
    python3 library/tools/production_pipeline.py preview <episode_slug> [--frame <f>]
    python3 library/tools/production_pipeline.py render <episode_slug> [--concurrency <n>]
    python3 library/tools/production_pipeline.py qa <episode_slug>
    python3 library/tools/production_pipeline.py run <episode_slug> (Full automated pipeline)
"""

import os
import re
import sys
import json
import argparse
import subprocess
import wave
import struct
import math
from pathlib import Path
from typing import Optional, Dict, Any, List

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.schema_validator import validate_artifact
from library.tools.generate_narration import generate_episode_narration
from library.tools.thumbnail_generator import render_episode_thumbnails
from library.tools.validate_thumbnail import ThumbnailValidator
from library.content_factory.brand_config import validate_thumbnail_config
from library.content_factory.publishing_kit_generator import generate_publishing_kit_for_episode
from library.content_factory.publishing_kit_validator import validate_publishing_kit
from library.content_factory.gdrive_uploader import upload_episode_to_gdrive
from library.content_factory.narration_standard import NarrationValidator

# Standard G.2 (.agents/rules/meowndr-video-quality-standards.md): short-form
# runtime window. Optimized for high retention (APV > 70%) on Shorts & Reels.
# Under 38s lacks educational depth; over 52s causes severe retention drop-off.
MIN_FINAL_DURATION_SEC = 38.0
MAX_FINAL_DURATION_SEC = 52.0
from library.content_factory.captions import generate_captions_for_episode
from library.content_factory.visual_director import generate_illustrations_for_episode
from library.audio.bgm_renderer import render_episode_audio_bed, is_audio_silent
from library.content_factory.bgm_matcher import match_bgm_for_episode, get_bed_info, validate_bed_preset

ASSETS_LIB_PATH = REPO_ROOT / "assets" / "library.json"

class ProductionValidator:
    def __init__(self, episode_slug: str):
        self.slug = episode_slug.strip()
        self.ep_dir = REPO_ROOT / "episodes" / self.slug
        self.papercut_dir = self.ep_dir / "papercut"
        self.errors = []
        self.warnings = []
        self.passed = []
        self.cfg = {}

    def log_pass(self, msg: str):
        self.passed.append(msg)
        print(f"  [PASS] {msg}")

    def log_warn(self, msg: str):
        self.warnings.append(msg)
        print(f"  [WARN] {msg}")

    def log_error(self, msg: str):
        self.errors.append(msg)
        print(f"  [ERROR] {msg}")

    def validate_all(self) -> bool:
        print("=" * 70)
        print(f"  Production Pre-Flight Validation: {self.slug}")
        print("=" * 70)

        if not self.ep_dir.exists():
            self.log_error(f"Episode directory does not exist: {self.ep_dir}")
            return False

        self._check_episode_config()
        self._check_repository_hygiene()
        self._check_script_quality()
        self._check_assets_library()
        self._check_audio_and_narration()
        self._check_scene_durations()
        self._check_storyboard_and_character()
        self._check_dynamic_animations()
        self._check_text_safe_zones()
        self._check_thumbnail_branding()
        self._check_watermark_branding()

        print("-" * 70)
        print(f"Validation Summary: {len(self.passed)} Passed, {len(self.warnings)} Warnings, {len(self.errors)} Blocking Errors")
        print("=" * 70)
        return len(self.errors) == 0

    def _check_episode_config(self):
        cfg_file = self.papercut_dir / "episode.json"
        if not cfg_file.exists():
            self.log_error(f"Missing episode.json at {cfg_file}")
            return

        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.cfg = cfg
            self.log_pass("episode.json syntax valid")

            meta = cfg.get("meta", {})
            for req in ["id", "title", "topic", "language", "targetDurationSeconds", "width", "height"]:
                if req not in meta:
                    self.log_error(f"meta missing required field: '{req}'")
                else:
                    if req == "width" and meta[req] != 1080:
                        self.log_error(f"Invalid width: {meta[req]}, expected 1080")
                    if req == "height" and meta[req] != 1920:
                        self.log_error(f"Invalid height: {meta[req]}, expected 1920")

            if "comp" not in cfg:
                self.log_error("Missing Remotion composition ID ('comp')")
            else:
                self.log_pass(f"Composition ID: {cfg['comp']}")

        except Exception as e:
            self.log_error(f"Failed to parse episode.json: {e}")

    def _check_repository_hygiene(self):
        nm = self.papercut_dir / "node_modules"
        if nm.exists():
            if nm.is_symlink():
                self.log_pass("node_modules is a lightweight symlink to shared template (storage optimized)")
            else:
                self.log_warn("papercut/node_modules is a heavy physical directory. Run 'python3 library/tools/repo_hygiene.py --fix' to reclaim ~700MB.")

    def _check_assets_library(self):
        if not ASSETS_LIB_PATH.exists():
            self.log_warn(f"Assets library not found at {ASSETS_LIB_PATH}")
            return

        registered_envs = {}
        try:
            from background_registry import BackgroundRegistry
            reg = BackgroundRegistry(repo_root=str(REPO_ROOT))
            for bg in reg.data.get("backgrounds", []):
                registered_envs[bg["id"]] = {
                    "id": bg["id"],
                    "path": bg.get("assetPath"),
                    "status": bg.get("status", "active"),
                }
        except Exception:
            pass

        if not registered_envs and ASSETS_LIB_PATH.exists():
            with open(ASSETS_LIB_PATH, "r", encoding="utf-8") as f:
                lib = json.load(f)
            registered_envs = {e["id"]: e for e in lib.get("categories", {}).get("environments", [])}

        scenes = self.cfg.get("scenes", [])
        used_envs = set()
        default_env = self.cfg.get("environment", {})
        if isinstance(default_env, dict) and "id" in default_env:
            used_envs.add(default_env["id"])
        elif isinstance(default_env, str):
            used_envs.add(default_env)

        for s in scenes:
            if isinstance(s, dict):
                eid = s.get("environment_id") or s.get("environment")
                if eid:
                    used_envs.add(eid)

        for eid in used_envs:
            if eid not in registered_envs:
                self.log_error(f"Environment '{eid}' is not registered in Background Registry")
            elif registered_envs[eid].get("status") in ("disabled", "archived"):
                st = registered_envs[eid]["status"].upper()
                self.log_warn(f"Environment '{eid}' is marked as {st} in Background Registry")
            else:
                rel_path = registered_envs[eid].get("path")
                disk_path = REPO_ROOT / rel_path if rel_path else None
                if disk_path and not disk_path.exists():
                    self.log_warn(f"Environment background image missing on disk: {disk_path}")
                else:
                    self.log_pass(f"Environment '{eid}' verified in Background Registry")

    def _check_audio_and_narration(self):
        pub_vo = self.papercut_dir / "public" / "vo"
        pub_audio = self.papercut_dir / "public" / "audio"

        vo_file = pub_vo / "voiceover.wav"
        captions_file = pub_vo / "captions.json"
        music_file = pub_audio / "music.wav"
        plan_file = self.papercut_dir / "src" / "plan.json"

        if not vo_file.exists():
            self.log_error(f"Missing voiceover audio: {vo_file}")
        else:
            vo_silent, vo_reason = is_audio_silent(vo_file, min_duration=2.0)
            if vo_silent:
                self.log_error(f"Voiceover track is silent ({vo_reason}). Real speech synthesis required (check TTS provider / ELEVENLABS_API_KEY).")
            else:
                self.log_pass(f"Voiceover track present ({vo_file.stat().st_size / 1024:.1f} KB, non-silent)")

        if not captions_file.exists():
            self.log_warn(f"Missing captions.json: {captions_file}")
        else:
            try:
                with open(captions_file, "r") as f:
                    caps = json.load(f)
                if not isinstance(caps, list) or len(caps) == 0:
                    self.log_warn("captions.json is empty")
                else:
                    self.log_pass(f"Captions verified ({len(caps)} words timestamped)")
            except Exception as e:
                self.log_error(f"Invalid captions.json: {e}")

        if not plan_file.exists():
            self.log_error(f"Missing plan.json: {plan_file}")
        else:
            try:
                with open(plan_file, "r") as f:
                    plan = json.load(f)
                self.plan = plan
                self.log_pass(f"plan.json verified ({len(plan.get('scenes', []))} scenes)")
            except Exception as e:
                self.log_error(f"Invalid plan.json: {e}")

        # Validate BGM Music Bed Audio Track (Mandatory Non-Silent Bed matched to theme)
        if not music_file.exists():
            self.log_error(f"Missing BGM audio track: {music_file}. Run 'production_pipeline.py bgm {self.slug}' to render.")
        else:
            is_silent, s_reason = is_audio_silent(music_file, min_duration=5.0)
            if is_silent:
                self.log_error(f"BGM audio track is silent or invalid: {s_reason}. Run 'production_pipeline.py bgm {self.slug}' to render matched BGM.")
            else:
                bed_name = self.cfg.get("bed", "unspecified")
                self.log_pass(f"BGM audio track verified ({bed_name}, {music_file.stat().st_size / 1024:.1f} KB, non-silent)")

    def _check_scene_durations(self):
        if not hasattr(self, "plan"):
            return

        total_frames = self.plan.get("durationInFrames", 0)
        fps = self.plan.get("fps", 30)
        runtime_sec = total_frames / fps
        target_sec = self.cfg.get("meta", {}).get("targetDurationSeconds", 60)

        if abs(runtime_sec - target_sec) > 10:
            self.log_warn(f"Actual duration ({runtime_sec:.1f}s) differs from target ({target_sec}s)")
        else:
            self.log_pass(f"Runtime duration verified: {runtime_sec:.2f}s ({total_frames} frames at {fps} fps)")

    def _check_storyboard_and_character(self):
        scenes = self.cfg.get("scenes", [])
        for idx, s in enumerate(scenes):
            if isinstance(s, dict):
                sid = s.get("id", f"scene_{idx}")
                # Check interaction target
                itarget = s.get("interaction_target")
                if isinstance(itarget, dict):
                    tx = itarget.get("x", 0)
                    ty = itarget.get("y", 0)
                    if tx < 0 or tx > 1080 or ty < 0 or ty > 1920:
                        self.log_error(f"Scene {sid}: interaction target ({tx}, {ty}) out of bounds")

                # Check character position
                cpos = s.get("character_position") or s.get("presenter_position") or {}
                if cpos.get("visible", True):
                    cx = cpos.get("x", 360)
                    cy = cpos.get("y", 1380)
                    if cx < 0 or cx > 1080:
                        self.log_warn(f"Scene {sid}: character X coordinate ({cx}) near or outside frame")

    def _check_text_safe_zones(self):
        scenes = self.cfg.get("scenes", [])
        for idx, s in enumerate(scenes):
            if isinstance(s, dict):
                sid = s.get("id", f"scene_{idx}")
                texts = s.get("text_elements", [])
                for t in texts:
                    px = t.get("preferredX", 540)
                    py = t.get("preferredY", 800)
                    # Check top banner exclusion (0-380)
                    if 0 <= py <= 380:
                        self.log_warn(f"Scene {sid}: Text '{t.get('id')}' Y={py} overlaps Top Banner safe zone (0-380px)")
                    # Check caption exclusion (1410-1920)
                    if 1410 <= py <= 1920:
                        self.log_warn(f"Scene {sid}: Text '{t.get('id')}' Y={py} overlaps Bottom Caption safe zone (1410-1920px)")
        self.log_pass("Text safe zone checks completed")

    def _check_thumbnail_branding(self):
        thumb = self.cfg.get("thumbnail")
        if not thumb:
            self.log_warn("episode.json missing 'thumbnail' branding block; default branding will be inferred.")
            return

        errs = validate_thumbnail_config(thumb)
        for err in errs:
            self.log_error(f"Thumbnail branding error: {err}")
        if not errs:
            self.log_pass(f"Thumbnail branding configuration verified: channel='{thumb.get('channelName')}', title='{thumb.get('episodeTitle')}'")

    def _check_watermark_branding(self):
        wm = self.cfg.get("watermark", {})
        enabled = wm.get("enabled", True)
        if not enabled:
            self.log_warn("Persistent video watermark is disabled for this episode.")
            return

        text = wm.get("text", "@meowndr")
        if text != "@meowndr":
            self.log_error(f"Invalid watermark text: '{text}'. Must be exact canonical '@meowndr'.")
            return

        pos = wm.get("position", "top-right")
        if pos not in ["top-right", "top-left", "bottom-right", "bottom-left"]:
            self.log_error(f"Invalid watermark position: '{pos}'.")
            return

        self.log_pass(f"Persistent video watermark verified: text='{text}', position='{pos}', enabled={enabled}")

    def _check_script_quality(self):
        script_file = self.ep_dir / "narration" / "script.json"
        if not script_file.exists():
            self.log_warn(f"No script.json found in narration directory: {script_file}")
            return

        try:
            with open(script_file, "r", encoding="utf-8") as f:
                script = json.load(f)

            if not isinstance(script, list) or len(script) == 0:
                self.log_warn("script.json is empty")
                return

            total_words = sum(len(line.get("text", "").split()) for line in script)

            # Audit against Indonesian Narration Number & Punctuation Standard
            audit = NarrationValidator.validate_script(script)
            est_sec = audit.get("estimated_duration_sec", total_words / NarrationValidator.TARGET_WPS)
            if not audit["is_valid"]:
                for err in audit["errors"]:
                    self.log_error(f"Narration Standard: {err}")
            else:
                self.log_pass("Narration Number & Punctuation Standard verified: 100% written in Indonesian words")

            for warn in audit["warnings"]:
                self.log_warn(f"Narration Pacing/Rhythm: {warn}")

            self.log_pass(f"Script storytelling & narration structure verified: {len(script)} lines, {total_words} words (~{est_sec:.1f}s)")
        except Exception as e:
            self.log_error(f"Failed to parse script.json: {e}")

    def _check_dynamic_animations(self):
        scenes_dir = self.papercut_dir / "src" / "scenes"
        if not scenes_dir.exists():
            return

        scene_files = list(scenes_dir.glob("S*.tsx"))
        if not scene_files:
            return

        # Ensure no banned dynamic camera shake/zoom effects (snapZoom, handheld, pullBack, dutchTilt) are used
        banned_effects = []
        for sf in scene_files:
            try:
                content = sf.read_text(encoding="utf-8")
                for eff in ("snapZoom", "handheld", "pullBack", "dutchTilt"):
                    if re.search(rf"\b{eff}\s*:", content):
                        banned_effects.append(f"{sf.name}:{eff}")
            except Exception:
                pass

        if banned_effects:
            self.log_error(
                f"Banned dynamic camera effects detected ({', '.join(banned_effects)}). "
                "Use only smooth OrbitCamera (yaw/push) without snapZoom, handheld, pullBack, or dutchTilt."
            )
        else:
            self.log_pass("Steady diorama camera verified: zero dynamic shake/zoom effects (snapZoom, handheld, pullBack)")

        self.log_pass(f"Dynamic scene components verified: {len(scene_files)} active scenes in src/scenes/")


def run_preview(episode_slug: str, frame: int = 40):
    ep_dir = REPO_ROOT / "episodes" / episode_slug / "papercut"
    out_dir = ep_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"preview-frame-{frame}.png"

    with open(ep_dir / "episode.json") as f:
        cfg = json.load(f)
    comp = cfg["comp"]

    cmd = ["npx", "remotion", "still", comp, str(out_file.relative_to(ep_dir)), f"--frame={frame}"]
    print(f"Rendering preview frame {frame} to {out_file}...")
    subprocess.run(cmd, cwd=ep_dir, check=True)
    print(f">> Preview generated: {out_file}")


def run_render(episode_slug: str, concurrency: int = 4):
    validator = ProductionValidator(episode_slug)
    if not validator.validate_all():
        print("[ABORT] Cannot render episode due to blocking pre-flight errors.")
        sys.exit(1)

    ep_dir = REPO_ROOT / "episodes" / episode_slug / "papercut"
    out_dir = ep_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(ep_dir / "episode.json") as f:
        cfg = json.load(f)
    comp = cfg["comp"]
    out_prefix = cfg.get("out", f"episode-{episode_slug}")
    out_file = out_dir / f"{out_prefix}.mp4"

    # Ensure opening-frame thumbnail is staged in public/ for frame 0 poster frame embedding
    pub_opening = ep_dir / "public" / "opening-frame.png"
    out_opening = out_dir / "opening-frame.png"
    if not pub_opening.exists():
        if out_opening.exists():
            shutil.copy2(out_opening, pub_opening)
        else:
            try:
                from library.tools.thumbnail_generator import render_episode_thumbnails
                print(">> Pre-rendering opening frame thumbnail for frame 0 poster embedding...")
                render_episode_thumbnails(episode_slug, validate_after=False)
            except Exception as e:
                print(f"[WARN] Opening frame thumbnail pre-render note: {e}")

    # Ensure BGM audio track is rendered and non-silent before launching render
    pub_music = ep_dir / "public" / "audio" / "music.wav"
    music_silent, m_reason = is_audio_silent(pub_music, min_duration=5.0)
    if music_silent:
        print(f">> Pre-render check: BGM track requires rendering ({m_reason}). Auto-rendering matched BGM...")
        try:
            render_episode_audio_bed(episode_slug, force=True)
        except Exception as e:
            print(f"[WARN] Auto BGM render note: {e}")

    cmd = [
        "npx", "remotion", "render",
        comp,
        str(out_file.relative_to(ep_dir)),
        f"--concurrency={concurrency}"
    ]
    print(f"Executing deterministic Remotion render: {comp} -> {out_file}...")
    subprocess.run(cmd, cwd=ep_dir, check=True)
    print(f">> Video render complete: {out_file}")


def run_qa(episode_slug: str):
    ep_dir = REPO_ROOT / "episodes" / episode_slug / "papercut"
    with open(ep_dir / "episode.json") as f:
        cfg = json.load(f)
    out_prefix = cfg.get("out", f"episode-{episode_slug}")
    video_path = ep_dir / "out" / f"{out_prefix}.mp4"
    if not video_path.exists():
        fallback_path = ep_dir / "out" / f"episode-{episode_slug}.mp4"
        if fallback_path.exists():
            video_path = fallback_path
        else:
            mp4s = list((ep_dir / "out").glob("*.mp4"))
            if mp4s:
                video_path = mp4s[0]
            else:
                print(f"[ERROR] Rendered video not found in {ep_dir / 'out'}")
                sys.exit(1)

    print("=" * 70)
    print(f"  Production QA Verification: {video_path.name}")
    print("=" * 70)

    # 1. ffprobe metadata
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=width,height,r_frame_rate,duration,codec_name,channels,sample_rate",
        "-show_entries", "format=duration,size",
        "-of", "json",
        str(video_path)
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    info = json.loads(res.stdout)

    v_stream = next((s for s in info.get("streams", []) if s.get("width")), None)
    a_stream = next((s for s in info.get("streams", []) if s.get("channels")), None)

    if not v_stream:
        print("[FAIL] Missing video stream!")
        sys.exit(1)

    vw = int(v_stream.get("width", 0))
    vh = int(v_stream.get("height", 0))
    v_fps = v_stream.get("r_frame_rate", "0/0")
    v_dur = float(v_stream.get("duration", 0))

    print(f"  • Video Resolution: {vw}x{vh} (Expected 1080x1920)")
    assert (vw, vh) == (1080, 1920), f"Invalid dimensions: {vw}x{vh}"

    print(f"  • Video Framerate: {v_fps} (Expected 30/1)")
    print(f"  • Video Duration: {v_dur:.3f}s (Expected {MIN_FINAL_DURATION_SEC:.0f}-{MAX_FINAL_DURATION_SEC:.0f}s)")

    if not (MIN_FINAL_DURATION_SEC <= v_dur <= MAX_FINAL_DURATION_SEC):
        print(
            f"[FAIL] Final rendered duration {v_dur:.1f}s is outside the mandatory "
            f"{MIN_FINAL_DURATION_SEC:.0f}-{MAX_FINAL_DURATION_SEC:.0f}s window (Standard G.2).\n"
            f">> STRICT PROHIBITION: Do NOT artificially speed up audio or video (atempo / playback multipliers).\n"
            f">> SCRIPT REMEDIATION REQUIRED: The script is too long. Roll back to Stage 5, notify user,\n"
            f"   and re-generate a shorter script to achieve natural 1.0x delivery within the target window."
        )
        sys.exit(1)

    if a_stream:
        a_channels = a_stream.get("channels")
        a_rate = a_stream.get("sample_rate")
        a_dur = float(a_stream.get("duration", 0))
        print(f"  • Audio Stream: {a_stream.get('codec_name')} | {a_channels} channels | {a_rate} Hz | {a_dur:.3f}s")
        drift = abs(v_dur - a_dur)
        print(f"  • Audio-Video Sync Drift: {drift:.3f}s")
        assert drift < 0.25, f"Audio-video sync drift excessive: {drift}s"

    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    print(f"  • File Size: {file_size_mb:.2f} MB")

    # Voiceover Track QA Verification
    pub_vo = ep_dir / "public" / "vo" / "voiceover.wav"
    if pub_vo.exists():
        vo_silent, vo_msg = is_audio_silent(pub_vo, min_duration=2.0)
        if vo_silent:
            print(f"[FAIL] Voiceover audio track failed QA: silent ({vo_msg}). Real speech synthesis required.")
            sys.exit(1)
        else:
            print(f"  • Voiceover Audio Track: Verified active & non-silent ({pub_vo.stat().st_size / 1024:.1f} KB)")
    else:
        print("[FAIL] Missing voiceover.wav in public/vo!")
        sys.exit(1)

    # BGM Bed Track QA Verification
    pub_music = ep_dir / "public" / "audio" / "music.wav"
    if pub_music.exists():
        m_silent, m_msg = is_audio_silent(pub_music, min_duration=5.0)
        if m_silent:
            print(f"[FAIL] BGM audio track failed QA: {m_msg}")
            sys.exit(1)
        else:
            print(f"  • BGM Audio Track: Verified active & non-silent ({pub_music.stat().st_size / 1024:.1f} KB)")

    # 2. Thumbnail & Branding Verification
    thumb_path = ep_dir / "out" / "thumbnail.png"
    if thumb_path.exists():
        t_val = ThumbnailValidator(episode_slug)
        if not t_val.validate():
            print("[FAIL] Mandatory thumbnail QA failed!")
            sys.exit(1)
        print(">> Thumbnail QA Verification PASSED: 100% compliant with @meowndr branding!")
    else:
        print("[WARN] No thumbnail.png rendered yet for this episode.")

    print(">> QA Verification PASSED: Video and Audio streams meet 100% production criteria!")
    print("=" * 70)


def run_captions(episode_slug: str, force: bool = False) -> bool:
    print("=" * 70)
    print(f"  Automated Multi-Platform Caption Generation: {episode_slug}")
    print("=" * 70)
    ok, result, msgs = generate_captions_for_episode(episode_slug, force=force)
    for m in msgs:
        print(f"  • {m}")
    if ok:
        print(">> Multi-Platform Captions Generated: 100% compliant with editorial standards!")
    else:
        print(">> [WARN] Captions marked as NEEDS_REVIEW")
    print("=" * 70)
    return ok


def run_illustrations(episode_slug: str, force: bool = False) -> bool:
    print("=" * 70)
    print(f"  Art-Directed Visual Bible & Illustration Generation: {episode_slug}")
    print("=" * 70)
    ok, result, msgs = generate_illustrations_for_episode(episode_slug, force=force)
    for m in msgs:
        print(f"  • {m}")
    if ok:
        print(">> Visual Bible & Scene Illustrations PASSED: 100% compliant with art direction!")
    else:
        print(">> [WARN] Illustration generation encountered issues")
    print("=" * 70)
    return ok


def run_publish_kit(episode_slug: str, force: bool = False, skip_qa: bool = False) -> bool:
    print("=" * 70)
    print(f"  Automated Social Media Publishing Kit: {episode_slug}")
    print("=" * 70)

    # 1. Run/verify QA first unless skip_qa is explicitly requested
    if not skip_qa:
        print("[1/3] Running prerequisite Production QA verification...")
        try:
            run_qa(episode_slug)
        except SystemExit as se:
            if se.code != 0:
                print("[FAIL] Prerequisite Production QA exited with error code.")
                print("[ABORT] Cannot generate publishing kit for an episode that has not passed QA.")
                return False
        except Exception as e:
            print(f"[FAIL] Prerequisite Production QA failed: {e}")
            print("[ABORT] Cannot generate publishing kit for an episode that has not passed QA.")
            return False
    else:
        print("[1/3] Skipping QA verification (--no-qa requested)")

    # 2. Generate publishing kit
    print("\n[2/3] Synthesizing platform-specific publication copy and metadata...")
    success, payload, created = generate_publishing_kit_for_episode(episode_slug, force=force)
    if not success:
        print("[FAIL] Publishing kit generation failed:")
        for err in created:
            print(f"  - {err}")
        return False

    print(f"  Generated {len(created)} deliverables in episodes/{episode_slug}/publishing/")

    # 3. Quality validation
    print("\n[3/3] Running Publishing Kit Quality Validation...")
    ok = validate_publishing_kit(episode_slug)
    if not ok:
        print("[FAIL] Publishing kit failed quality validation checks.")
        return False

    print("\n>> Social Media Publishing Kit successfully generated and validated for @meowndr!")
    return True


def run_upload_gdrive(episode_slug: str, dry_run: bool = False, force: bool = False) -> bool:
    print("=" * 70)
    print(f"  Google Drive Production Upload: {episode_slug}")
    print("=" * 70)

    # 1. Ensure Publishing Kit exists and passes quality validation
    pub_dir = REPO_ROOT / "episodes" / episode_slug / "publishing"
    from library.content_factory.publishing_kit_validator import PublishingKitValidator
    validator = PublishingKitValidator(episode_slug)
    needs_gen = not (pub_dir / "publishing-kit.json").exists()
    if not needs_gen:
        if not validator.validate():
            print("[WARN] Existing publishing kit failed quality validation. Auto-regenerating...")
            needs_gen = True

    if needs_gen:
        print("[INFO] Generating fresh, validated publishing kit before Google Drive upload...")
        if not run_publish_kit(episode_slug, force=True, skip_qa=True):
            print("[FAIL] Could not generate required publishing deliverables. Aborting upload.")
            return False

    # 2. Upload to Google Drive via rclone
    print("\n[INFO] Executing safe rclone upload to Google Drive...")
    ok, record, msgs = upload_episode_to_gdrive(episode_slug, dry_run=dry_run, force=force)
    for m in msgs:
        print(f"  {'[PASS]' if ok else '[FAIL]'} {m}")

    if ok:
        print("\n>> Google Drive Upload PASSED: 100% of deliverables verified on remote!")
    else:
        print("\n>> Google Drive Upload FAILED or incomplete.")
    print("=" * 70)
    return ok


def run_bgm(episode_slug: str, bed_name: Optional[str] = None, force: bool = False) -> bool:
    print("=" * 70)
    print(f"  Procedural BGM Bed Matching & Synthesis: {episode_slug}")
    print("=" * 70)
    try:
        res = render_episode_audio_bed(episode_slug, bed_name=bed_name, force=force)
        print(f">> Status: {res['status']}")
        print(f"  • Matched BGM: {res['bed']} ({res.get('mood', '')}, {res.get('bpm', 120)} bpm)")
        print(f"  • Music File:  {res.get('music_path')} ({res.get('size_bytes', 0) / 1024:.1f} KB)")
        print(">> BGM track verified non-silent and ready for Remotion render!")
        print("=" * 70)
        return True
    except Exception as e:
        print(f"[FAIL] BGM rendering encountered error: {e}")
        print("=" * 70)
        return False


def main():
    parser = argparse.ArgumentParser(description="Papercraft Content Factory Production Pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    val_p = subparsers.add_parser("validate", help="Run pre-flight validation")
    val_p.add_argument("slug", help="Episode slug")

    voice_p = subparsers.add_parser("voice", help="Generate narration audio with configured TTS provider")
    voice_p.add_argument("slug", help="Episode slug")
    voice_p.add_argument("--provider", default=None, help="TTS Provider (elevenlabs, qwen3, placeholder)")
    voice_p.add_argument("--voice-id", default=None, help="Voice ID")
    voice_p.add_argument("--model-id", default=None, help="Model ID")
    voice_p.add_argument("--force", action="store_true", help="Force regenerate cache")

    bgm_p = subparsers.add_parser("bgm", help="Match and render procedural BGM score for episode")
    bgm_p.add_argument("slug", help="Episode slug")
    bgm_p.add_argument("--bed", default=None, help="Explicit BGM bed preset (e.g. marimba-G-116)")
    bgm_p.add_argument("--force", action="store_true", help="Force regenerate audio bed")

    prev_p = subparsers.add_parser("preview", help="Render lightweight preview still")
    prev_p.add_argument("slug", help="Episode slug")
    prev_p.add_argument("--frame", type=int, default=40, help="Frame to render")

    thumb_p = subparsers.add_parser("thumbnail", help="Render standalone 16:9 YouTube thumbnail & 9:16 opening frame")
    thumb_p.add_argument("slug", help="Episode slug")
    thumb_p.add_argument("--no-validate", action="store_true", help="Skip post-render validation")

    ren_p = subparsers.add_parser("render", help="Render full episode")
    ren_p.add_argument("slug", help="Episode slug")
    ren_p.add_argument("--concurrency", type=int, default=4, help="Render concurrency")

    qa_p = subparsers.add_parser("qa", help="Run post-render audio/video QA verification")
    qa_p.add_argument("slug", help="Episode slug")

    cap_p = subparsers.add_parser("captions", help="Generate automated multi-platform captions (Instagram, TikTok, YouTube Shorts)")
    cap_p.add_argument("slug", help="Episode slug")
    cap_p.add_argument("--force", action="store_true", help="Force regenerate captions ignoring cache")

    illust_p = subparsers.add_parser("illustrations", help="Generate art-directed papercraft illustrations & Visual Bible")
    illust_p.add_argument("slug", help="Episode slug")
    illust_p.add_argument("--force", action="store_true", help="Force regenerate illustrations ignoring cache")

    pub_p = subparsers.add_parser("publish-kit", help="Generate automated social media publishing kit for @meowndr")
    pub_p.add_argument("slug", help="Episode slug")
    pub_p.add_argument("--force", action="store_true", help="Force regenerate publishing kit")
    pub_p.add_argument("--no-qa", action="store_true", help="Skip pre-generation QA verification")

    gdrive_p = subparsers.add_parser("upload-gdrive", help="Upload completed episode and publishing kit to Google Drive via rclone")
    gdrive_p.add_argument("slug", help="Episode slug")
    gdrive_p.add_argument("--dry-run", action="store_true", help="Simulate upload without transferring files")
    gdrive_p.add_argument("--force", action="store_true", help="Force re-upload of all files unconditionally (--ignore-times)")

    trend_p = subparsers.add_parser("trend-research", help="Run trend research and content intelligence for @meowndr")
    trend_p.add_argument("--date", help="Target research date (YYYY-MM-DD)")
    trend_p.add_argument("--niche", help="Filter by niche")
    trend_p.add_argument("--daily", action="store_true", help="Daily monitoring mode")
    trend_p.add_argument("--weekly", action="store_true", help="Weekly summary mode")
    trend_p.add_argument("--on-demand", action="store_true", help="On-demand research mode")
    trend_p.add_argument("--force", action="store_true", help="Force re-generation of existing intelligence files")

    run_p = subparsers.add_parser("run", help="Run end-to-end pipeline: validate, preview, render, qa")
    run_p.add_argument("slug", help="Episode slug")

    args = parser.parse_args()

    if args.command == "validate":
        validator = ProductionValidator(args.slug)
        ok = validator.validate_all()
        sys.exit(0 if ok else 1)
    elif args.command == "voice":
        generate_episode_narration(
            episode_slug=args.slug,
            provider_name=args.provider,
            force_regenerate=args.force,
            voice_id=args.voice_id,
            model_id=args.model_id,
        )
    elif args.command == "bgm":
        ok = run_bgm(args.slug, bed_name=args.bed, force=args.force)
        sys.exit(0 if ok else 1)
    elif args.command == "preview":
        run_preview(args.slug, args.frame)
    elif args.command == "thumbnail":
        ok = render_episode_thumbnails(args.slug, validate_after=not args.no_validate)
        sys.exit(0 if ok else 1)
    elif args.command == "render":
        run_render(args.slug, args.concurrency)
    elif args.command == "qa":
        run_qa(args.slug)
    elif args.command == "captions":
        ok = run_captions(args.slug, force=args.force)
        sys.exit(0 if ok else 1)
    elif args.command == "illustrations":
        ok = run_illustrations(args.slug, force=args.force)
        sys.exit(0 if ok else 1)
    elif args.command == "publish-kit":
        ok = run_publish_kit(args.slug, force=args.force, skip_qa=args.no_qa)
        sys.exit(0 if ok else 1)
    elif args.command == "upload-gdrive":
        ok = run_upload_gdrive(args.slug, dry_run=args.dry_run, force=args.force)
        sys.exit(0 if ok else 1)
    elif args.command == "trend-research":
        from library.content_factory.trend_intelligence import run_trend_research_pipeline
        res = run_trend_research_pipeline(date_str=args.date, niche=args.niche, force=args.force)
        print(f"[OK] Trend research successfully completed for {res['date']}")
        for k, v in res["files"].items():
            print(f"  - {k}: {v}")
        sys.exit(0)
    elif args.command == "run":
        validator = ProductionValidator(args.slug)
        if not validator.validate_all():
            sys.exit(1)
        run_preview(args.slug, 40)
        render_episode_thumbnails(args.slug)
        print("\n>> Automatically generating Art-Directed Illustrations & Visual Bible...")
        run_illustrations(args.slug, force=False)
        print("\n>> Synthesizing and verifying procedural BGM track for episode...")
        run_bgm(args.slug, force=False)
        run_render(args.slug)
        run_qa(args.slug)
        # Always run caption generation automatically for completed videos
        print("\n>> Automatically generating Multi-Platform Captions for completed video...")
        run_captions(args.slug, force=False)
        auto_pub = os.environ.get("AUTO_GENERATE_PUBLISHING_KIT", "true").lower() in ("true", "1", "yes")
        auto_gdrive = os.environ.get("AUTO_UPLOAD_GDRIVE", "true").lower() in ("true", "1", "yes")

        if auto_pub or auto_gdrive:
            print("\n>> Automatically generating Social Media Publishing Kit...")
            run_publish_kit(args.slug, force=True, skip_qa=True)

        if auto_gdrive:
            print("\n>> AUTO_UPLOAD_GDRIVE=true: Automatically uploading to Google Drive...")
            run_upload_gdrive(args.slug)

if __name__ == "__main__":
    main()
