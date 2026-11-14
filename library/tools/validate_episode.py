#!/usr/bin/env python3
"""
Episode Validation Tool for 2D Papercraft Explainer.

Validates:
1. episode.json completeness (meta, environment, scenes, banners, cuts, audio).
2. Registered environment exists in assets/library.json and conforms to schema.
3. Scene TypeScript/TSX files exist and export their respective scene components.
4. Scene durations from plan.json are non-negative, >= 30 frames (1s @ 30fps).
5. Caption and word timings stay within scene and composition bounds.
6. Referenced audio assets (voiceover.wav, music.wav, fx.wav) exist and are non-empty.
7. Zero legacy Papercut references (no legacy prop modules, no legacy Critter,
   no Room color="grey", no legacy colors #E07A5F, #BA563B, #D67354, no legacy overlays).

Usage:
    python3 library/tools/validate_episode.py [episode_path_or_slug] [--strict]
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, List, Any, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
ASSETS_LIB_PATH = os.path.join(REPO_ROOT, "assets", "library.json")

LEGACY_PROP_MODULES = [
    "props/everyday",
    "props/aura",
    "props/cable",
    "props/council",
    "props/crowd",
    "props/gpu",
    "props/leak",
    "props/stage",
    "props/usage",
]

LEGACY_COLOR_PATTERNS = [
    (re.compile(r'["\']#E07A5F["\']', re.IGNORECASE), "Legacy terracotta critter color (#E07A5F)"),
    (re.compile(r'["\']#BA563B["\']', re.IGNORECASE), "Legacy terracotta critter shade (#BA563B)"),
    (re.compile(r'["\']#D67354["\']', re.IGNORECASE), "Legacy default hero color (#D67354)"),
]

LEGACY_OVERLAY_PATTERNS = [
    (re.compile(r'\bimport\s+.*\{[^}]*\bTapeBanner\b[^}]*\}\s+from', re.IGNORECASE), "Legacy TapeBanner component"),
    (re.compile(r'\bimport\s+.*\{[^}]*\bWordTagCaptions\b[^}]*\}\s+from', re.IGNORECASE), "Legacy WordTagCaptions component"),
    (re.compile(r'\bimport\s+.*\{[^}]*\bPill\b[^}]*\}\s+from', re.IGNORECASE), "Legacy generic Pill component"),
    (re.compile(r'\bimport\s+.*\{[^}]*\bCritter\b[^}]*\}\s+from', re.IGNORECASE), "Legacy Critter presenter component"),
    (re.compile(r'<Room\s+color=', re.IGNORECASE), "Legacy <Room color=...> backdrop"),
]


def resolve_episode_papercut_dir(path_or_slug: str) -> str:
    """Resolve an input string to the absolute path of an episode's papercut directory."""
    candidate = os.path.abspath(path_or_slug)
    if os.path.isdir(candidate):
        if os.path.exists(os.path.join(candidate, "episode.json")):
            return candidate
        if os.path.exists(os.path.join(candidate, "papercut", "episode.json")):
            return os.path.join(candidate, "papercut")

    # Try relative to episodes/
    episodes_dir = os.path.join(REPO_ROOT, "episodes")
    sub = os.path.join(episodes_dir, path_or_slug)
    if os.path.isdir(sub):
        if os.path.exists(os.path.join(sub, "episode.json")):
            return sub
        if os.path.exists(os.path.join(sub, "papercut", "episode.json")):
            return os.path.join(sub, "papercut")

    # Try stripping leading 'episodes/' if given
    clean = path_or_slug.strip("/").replace("episodes/", "")
    sub2 = os.path.join(episodes_dir, clean)
    if os.path.isdir(sub2):
        if os.path.exists(os.path.join(sub2, "episode.json")):
            return sub2
        if os.path.exists(os.path.join(sub2, "papercut", "episode.json")):
            return os.path.join(sub2, "papercut")

    return candidate


def load_registered_environments() -> Dict[str, Any]:
    """Load valid environment IDs from centralized Background Registry or asset library."""
    envs = {}
    try:
        from background_registry import BackgroundRegistry
        reg = BackgroundRegistry()
        for bg in reg.data.get("backgrounds", []):
            eid = bg.get("id")
            if eid:
                envs[eid] = {
                    "id": eid,
                    "name": bg.get("name"),
                    "status": bg.get("status", "active"),
                    "path": bg.get("assetPath"),
                    "statusReason": bg.get("statusReason"),
                }
        if envs:
            return envs
    except Exception:
        pass

    if os.path.exists(ASSETS_LIB_PATH):
        try:
            with open(ASSETS_LIB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data.get("categories", {}).get("environments", []):
                env_id = item.get("id")
                if env_id:
                    envs[env_id] = item
        except Exception:
            pass
    return envs


def validate_episode_config(ep_dir: str, registered_envs: Dict[str, Any]) -> Dict[str, Any]:
    """Validate episode.json structure, metadata, environment, scenes, and banners."""
    errors = []
    warnings = []
    config_path = os.path.join(ep_dir, "episode.json")

    if not os.path.exists(config_path):
        return {
            "valid": False,
            "errors": [f"Missing configuration file: {config_path}"],
            "warnings": [],
            "config": {}
        }

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Invalid JSON in {config_path}: {e}"],
            "warnings": [],
            "config": {}
        }

    # 1. Top-level attributes
    if "comp" not in config or not str(config["comp"]).strip():
        errors.append("episode.json missing 'comp' composition name")
    if "out" not in config or not str(config["out"]).strip():
        errors.append("episode.json missing 'out' render prefix")

    # 2. Meta block
    meta = config.get("meta")
    if meta is None or not isinstance(meta, dict):
        warnings.append("episode.json missing typed 'meta' block (recommended for production metadata)")
    else:
        for req_field in ["id", "title", "topic"]:
            if req_field not in meta or not str(meta[req_field]).strip():
                errors.append(f"episode.json meta missing required field: '{req_field}'")
        if meta.get("fps") and meta.get("fps") != 30:
            warnings.append(f"meta.fps is {meta.get('fps')}, expected standard 30 fps")
        if meta.get("width") and meta.get("width") != 1080:
            errors.append(f"meta.width is {meta.get('width')}, expected vertical 1080")
        if meta.get("height") and meta.get("height") != 1920:
            errors.append(f"meta.height is {meta.get('height')}, expected vertical 1920")

    # 3. Environment block (single or multi-environment)
    env = config.get("environment")
    if env is not None:
        if isinstance(env, dict):
            env_id = env.get("id")
            if not env_id:
                errors.append("episode.json environment object missing 'id'")
            elif registered_envs and env_id not in registered_envs and env_id not in ("scientific_visualization", "none"):
                warnings.append(f"Environment ID '{env_id}' is not in Background Registry")
            elif registered_envs and registered_envs.get(env_id, {}).get("status") in ("disabled", "archived"):
                st = registered_envs[env_id]["status"].upper()
                warnings.append(f"Environment ID '{env_id}' is marked as {st} in Background Registry")
        elif isinstance(env, str):
            if registered_envs and env not in registered_envs and env not in ("scientific_visualization", "none"):
                warnings.append(f"Environment ID '{env}' is not in Background Registry")
            elif registered_envs and registered_envs.get(env, {}).get("status") in ("disabled", "archived"):
                st = registered_envs[env]["status"].upper()
                warnings.append(f"Environment ID '{env}' is marked as {st} in Background Registry")
    else:
        warnings.append("episode.json missing explicit 'environment' specification (defaults to science-lab)")

    # Multi-environment catalog check
    multi_envs = config.get("environments")
    if multi_envs:
        env_list = list(multi_envs.keys()) if isinstance(multi_envs, dict) else multi_envs
        for e_id in env_list:
            if registered_envs and e_id not in registered_envs and e_id not in ("scientific_visualization", "none"):
                errors.append(f"Declared episode environment '{e_id}' is not registered in Background Registry")
            elif registered_envs and registered_envs.get(e_id, {}).get("status") in ("disabled", "archived"):
                st = registered_envs[e_id]["status"].upper()
                warnings.append(f"Declared episode environment '{e_id}' is marked as {st} in Background Registry")

    # 4. Scenes block
    scenes = config.get("scenes")
    if not scenes or not isinstance(scenes, list) or len(scenes) == 0:
        errors.append("episode.json missing or empty 'scenes' list")
    else:
        scene_ids = []
        seen_environments = []
        valid_background_types = [
            "environment_scene",
            "demonstration_scene",
            "scientific_visualization",
            "full_visual_scene",
            "return_scene"
        ]

        for idx, item in enumerate(scenes):
            s_id = None
            s_env = None
            b_type = None

            if isinstance(item, list) and len(item) >= 1:
                s_id = item[0]
                if len(item) >= 4:
                    s_env = item[3]
            elif isinstance(item, dict) and "id" in item:
                s_id = item["id"]
                s_env = item.get("environment_id") or item.get("environment")
                b_type = item.get("background_type") or item.get("scene_type")

                # Validate background type if declared
                if b_type and b_type not in valid_background_types:
                    errors.append(f"Scene '{s_id}' has invalid background_type '{b_type}'. Allowed: {valid_background_types}")

                # Validate presenter safe zone if presenter position is declared
                pres_pos = item.get("presenter_position") or item.get("presenter")
                if isinstance(pres_pos, dict) and pres_pos.get("visible", True) and b_type != "full_visual_scene":
                    px = pres_pos.get("x")
                    py = pres_pos.get("y")
                    if px is not None and not (180 <= px <= 900):
                        warnings.append(f"Scene '{s_id}' presenter x={px} is outside the safe zone (180-900)")
                    if py is not None and not (850 <= py <= 1650):
                        warnings.append(f"Scene '{s_id}' presenter y={py} is outside the safe zone (850-1650)")

            elif isinstance(item, str):
                s_id = item

            if not s_id:
                errors.append(f"Scene #{idx} in episode.json has no valid scene identifier")
            else:
                scene_ids.append(s_id)

            # Validate scene environment against registered assets
            if s_env and s_env not in ("scientific_visualization", "none"):
                if registered_envs and s_env not in registered_envs:
                    errors.append(f"Scene '{s_id}' references unregistered environment '{s_env}'")
                elif registered_envs and registered_envs.get(s_env, {}).get("status") in ("disabled", "archived"):
                    st = registered_envs[s_env]["status"].upper()
                    warnings.append(f"Scene '{s_id}' references {st} environment '{s_env}'")

                # Continuity check for return_scene: must have been used earlier in the sequence
                if b_type == "return_scene" and s_env not in seen_environments:
                    warnings.append(f"Scene '{s_id}' marked as return_scene for '{s_env}' but environment was not used earlier in the episode")

                seen_environments.append(s_env)

    # 4b. Visual Variety Check (Multi-Environment Standards)
    unique_envs = set(e for e in seen_environments if e)
    target_dur = config.get("meta", {}).get("targetDurationSeconds", 0)
    if (len(scenes) >= 5 or target_dur >= 30) and len(unique_envs) <= 1:
        single_env = list(unique_envs)[0] if unique_envs else config.get("environment", {}).get("id", "unknown")
        warnings.append(
            f"Visual Variety Notice: Episode has {len(scenes)} scenes ({target_dur}s) but uses a single environment '{single_env}' across all scenes. "
            f"Consider diversifying environments (e.g. hook room, lab, outdoor/library) to avoid visual fatigue."
        )

    # 5. Banners block (Dynamic Banner Rule)
    # Rule: Assign headline banner text ONLY to Scene 1 (Hook).
    # Scenes 2+ omit banners to maximize stage breathing room.
    banners = config.get("banners")
    if banners is None or not isinstance(banners, dict):
        warnings.append("episode.json missing 'banners' map")
    elif scenes and isinstance(scenes, list):
        for idx, item in enumerate(scenes):
            s_id = item[0] if isinstance(item, list) and len(item) >= 1 else (item.get("id") if isinstance(item, dict) else item)
            if idx == 0:
                if s_id and not banners.get(s_id):
                    warnings.append(f"Hook Scene 1 '{s_id}' missing headline banner text in episode.json['banners']")
            else:
                # Scenes 2+ should omit banner according to the Dynamic Banner Rule
                if s_id and banners.get(s_id):
                    warnings.append(
                        f"Dynamic Banner Notice: Scene '{s_id}' has banner text '{banners[s_id]}'. "
                        f"Per Dynamic Banner Rule, scenes 2+ should omit top banner for vertical stage breathing room."
                    )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "config": config
    }


def validate_scene_components(ep_dir: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Verify that every scene file exists and exports a component."""
    errors = []
    warnings = []
    scenes = config.get("scenes", [])
    src_scenes_dir = os.path.join(ep_dir, "src", "scenes")
    scene_component_envs = []

    if not os.path.isdir(src_scenes_dir):
        errors.append(f"Scenes source directory missing: {src_scenes_dir}")
        return {"valid": False, "errors": errors, "warnings": warnings}

    scene_index_path = os.path.join(src_scenes_dir, "index.ts")
    if not os.path.exists(scene_index_path):
        warnings.append("Missing src/scenes/index.ts scene aggregator module")
    else:
        with open(scene_index_path, "r", encoding="utf-8") as f:
            index_content = f.read()

    for item in scenes:
        s_id = item[0] if isinstance(item, list) and len(item) >= 1 else (item.get("id") if isinstance(item, dict) else item)
        if not s_id:
            continue

        tsx_path = os.path.join(src_scenes_dir, f"{s_id}.tsx")
        ts_path = os.path.join(src_scenes_dir, f"{s_id}.ts")
        target_path = tsx_path if os.path.exists(tsx_path) else (ts_path if os.path.exists(ts_path) else None)

        if not target_path:
            errors.append(f"Scene component file not found: {tsx_path}")
            continue

        with open(target_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Check export
        has_named_export = re.search(rf'export\s+(const|function|class)\s+{s_id}\b', code)
        has_default_export = re.search(r'export\s+default\b', code)
        if not (has_named_export or has_default_export):
            errors.append(f"Scene file {os.path.basename(target_path)} does not export '{s_id}' or default component")

        # Track scene environment usage
        env_match = re.search(r'environment\s*=\s*[\'"]([^\'"]+)[\'"]', code)
        if env_match:
            scene_component_envs.append((s_id, env_match.group(1)))

        # Check for verbal narrative badges in PapercraftSceneShell (enforce curated text standard)
        badge_match = re.search(r'badges\s*=\s*\{\[\s*\{[^}]*text\s*:\s*[\'"]([^\'"]+)[\'"]', code)
        if badge_match:
            badge_text = badge_match.group(1)
            if any(term in badge_text.upper() for term in ['?', '!', 'SECEPAT', 'RELATIVITAS', 'KONSEP', 'KOMPRESI', 'BOLA PLASMA', 'TOPIK SAINS']):
                warnings.append(
                    f"Scene {s_id}: Detected verbal narrative badge '{badge_text}'. "
                    "Per @meowndr standards, remove verbal narrative badges repeating voiceover. "
                    "Curate text inside physical apparatus models only."
                )

        # Split-Stage Anti-Overlap Staging Check
        # Check if presenter and a visual component collide near center
        pres_match = re.search(r'presenter\s*=\s*\{([^}]+)\}', code)
        vis_match = re.search(r'<[A-Z][a-zA-Z0-9]*Visual\s+([^/>]+)/?>', code)
        if pres_match and vis_match:
            pres_str = pres_match.group(1)
            vis_str = vis_match.group(1)
            px_m = re.search(r'x\s*:\s*(\d+)', pres_str)
            vx_m = re.search(r'x\s*=\s*\{?(\d+)\}?', vis_str)
            vy_m = re.search(r'y\s*=\s*\{?(\d+)\}?', vis_str)
            scale_m = re.search(r'scale\s*=\s*\{?([0-9.]+)\}?', vis_str)
            if px_m and vx_m:
                px = int(px_m.group(1))
                vx = int(vx_m.group(1))
                vy = int(vy_m.group(1)) if vy_m else 740
                scale = float(scale_m.group(1)) if scale_m else 1.0
                # If presenter is near 340-400 and visual is near 540 with y > 700 and scale > 0.9, high risk of overlap!
                if 320 <= px <= 480 and 480 <= vx <= 600 and vy >= 720 and scale >= 0.95:
                    warnings.append(
                        f"Scene {s_id}: Staging collision risk between presenter (x={px}) and visual apparatus (x={vx}, y={vy}, scale={scale}). "
                        f"Recommend Split-Stage Staging: presenter at x: 250-280 (Stage Left) and visual at x: 680-720, y: 640-660, scale: <= 0.85."
                    )

    if len(scene_component_envs) >= 5:
        unique_component_envs = set(e[1] for e in scene_component_envs)
        if len(unique_component_envs) <= 1:
            warnings.append(
                f"Scene Component Variety: All {len(scene_component_envs)} scene components hardcode the identical environment '{list(unique_component_envs)[0]}'. "
                f"Consider diversifying environments across scenes per narrative beats."
            )

    # Check for Mascot Expression, Physical Mobility, and Prohibited States
    dynamic_action_keywords = {'walking', 'jumping', 'using_phone', 'ducking', 'waving'}
    deprecated_states = {'sitting', 'sleeping'}
    found_states = set()
    has_movement_or_interaction = False

    for item in scenes:
        s_id = item[0] if isinstance(item, list) and len(item) >= 1 else (item.get("id") if isinstance(item, dict) else item)
        if not s_id:
            continue
        target_path = os.path.join(src_scenes_dir, f"{s_id}.tsx")
        if os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as f:
                c = f.read()
            for st in re.findall(r"state\s*:\s*['\"]([a-zA-Z0-9_]+)['\"]", c):
                found_states.add(st)
                if st in deprecated_states:
                    warnings.append(
                        f"Scene {s_id}: Uses deprecated mascot pose '{st}'. "
                        "Per creative standards, replace sitting/sleeping with active mobility (walking, pacing, gesturing)."
                    )
            if 'movement=' in c or 'movements=' in c or 'interaction=' in c or 'interactiveAction=' in c or 'interactiveActions=' in c:
                has_movement_or_interaction = True

    if len(scenes) >= 4:
        dynamic_actions_used = found_states.intersection(dynamic_action_keywords)
        if len(dynamic_actions_used) == 0 and not has_movement_or_interaction:
            warnings.append(
                f"Mascot Dynamics Notice: Episode has {len(scenes)} scenes but uses only basic static states {found_states}. "
                "Include dynamic physical actions (e.g. using_phone, walking, jumping, ducking, waving) "
                "or kinematic movements (walking, pacing, entering) to keep the mascot mobile and expressive."
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_plan_and_timing(ep_dir: str) -> Dict[str, Any]:
    """Validate plan.json durations and caption boundaries."""
    errors = []
    warnings = []
    plan_path = os.path.join(ep_dir, "src", "plan.json")

    if not os.path.exists(plan_path):
        warnings.append(f"plan.json not found at {plan_path} (timing will be calculated at runtime or needs voice build)")
        return {"valid": True, "errors": [], "warnings": warnings, "plan": {}}

    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except Exception as e:
        errors.append(f"Invalid JSON in {plan_path}: {e}")
        return {"valid": False, "errors": errors, "warnings": warnings, "plan": {}}

    total_duration = plan.get("durationInFrames", 0)
    if total_duration <= 0:
        errors.append(f"Total plan durationInFrames ({total_duration}) must be positive")

    fps = plan.get("fps", 30)
    min_scene_frames = int(fps * 1.0)  # at least 1.0 second per scene

    scenes = plan.get("scenes", [])
    if not scenes:
        errors.append("plan.json has no scenes array")
    else:
        calc_cursor = 0
        for s in scenes:
            s_id = s.get("id", "unnamed")
            s_from = s.get("from", 0)
            s_dur = s.get("durationInFrames", 0)

            if s_dur <= 0:
                errors.append(f"Scene '{s_id}' durationInFrames ({s_dur}) must be positive")
            elif s_dur < min_scene_frames:
                errors.append(f"Scene '{s_id}' durationInFrames ({s_dur}) is less than minimum 1 second ({min_scene_frames} frames)")

            if s_from < 0:
                errors.append(f"Scene '{s_id}' start frame 'from' ({s_from}) cannot be negative")

            # Check words inside scene
            words = s.get("words", [])
            for w in words:
                wf = w.get("f", 0)
                if wf < 0:
                    errors.append(f"Word '{w.get('text')}' in scene '{s_id}' has negative frame {wf}")
                elif wf > s_dur + 30:  # allow small tail hold
                    warnings.append(f"Word '{w.get('text')}' frame ({wf}) extends beyond scene '{s_id}' duration ({s_dur})")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "plan": plan
    }


def validate_audio_assets(ep_dir: str) -> Dict[str, Any]:
    """Verify presence of audio files required for rendering."""
    errors = []
    warnings = []

    # Expected standard audio locations
    vo_path = os.path.join(ep_dir, "public", "vo", "voiceover.wav")
    music_path = os.path.join(ep_dir, "public", "audio", "music.wav")
    fx_path = os.path.join(ep_dir, "public", "audio", "fx.wav")

    # voiceover.wav check
    if not os.path.exists(vo_path):
        errors.append(f"Missing voiceover audio: {vo_path}")
    elif os.path.getsize(vo_path) == 0:
        errors.append(f"Voiceover audio file is empty (0 bytes): {vo_path}")
    else:
        try:
            from library.audio.bgm_renderer import is_audio_silent
            from pathlib import Path
            is_silent, s_reason = is_audio_silent(Path(vo_path), min_duration=2.0)
            if is_silent:
                errors.append(f"Voiceover audio appears silent ({s_reason}). Real speech synthesis required (TTS provider).")
        except Exception:
            pass

    # music.wav check
    if not os.path.exists(music_path):
        warnings.append(f"Missing background music: {music_path} (render may be silent or fail if audio track enabled)")
    elif os.path.getsize(music_path) == 0:
        errors.append(f"Background music file is empty (0 bytes): {music_path}")
    else:
        try:
            from library.audio.bgm_renderer import is_audio_silent
            from pathlib import Path
            is_silent, s_reason = is_audio_silent(Path(music_path), min_duration=5.0)
            if is_silent:
                warnings.append(f"Background music appears silent or incomplete ({s_reason}). Run production_pipeline.py bgm to render.")
        except Exception:
            pass

    # fx.wav check
    if not os.path.exists(fx_path):
        warnings.append(f"Missing sound effects audio: {fx_path}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def scan_for_legacy_leakage(ep_dir: str) -> Dict[str, Any]:
    """Scan all episode source code (excluding the synced library under src/lib) for legacy Papercut assets or leakage."""
    errors = []
    src_dir = os.path.join(ep_dir, "src")
    if not os.path.isdir(src_dir):
        return {"valid": True, "errors": [], "warnings": []}

    for root, _, files in os.walk(src_dir):
        for f in files:
            if not f.endswith((".tsx", ".ts")):
                continue
            fpath = os.path.join(root, f)
            rel_path = os.path.relpath(fpath, ep_dir)

            # Skip the shared library directory itself (it contains the legacy kit definitions)
            norm_rel = rel_path.replace("\\", "/")
            if norm_rel.startswith("src/lib/") or norm_rel.startswith("lib/"):
                continue

            try:
                with open(fpath, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except Exception:
                continue

            # 1. Legacy prop imports
            for leg_prop in LEGACY_PROP_MODULES:
                if leg_prop in content:
                    errors.append(f"{rel_path}: Imports legacy prop module '{leg_prop}'")

            # 2. Legacy colors
            for pattern, desc in LEGACY_COLOR_PATTERNS:
                if pattern.search(content):
                    errors.append(f"{rel_path}: Contains {desc}")

            # 3. Legacy overlays & presenter components
            for pattern, desc in LEGACY_OVERLAY_PATTERNS:
                if pattern.search(content):
                    errors.append(f"{rel_path}: Uses {desc}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": []
    }


def validate_camera_effects(ep_dir: str) -> Dict[str, Any]:
    """Verify steady diorama camera (no snapZoom, handheld, pullBack, or dutchTilt)."""
    errors = []
    warnings = []
    scenes_dir = os.path.join(ep_dir, "src", "scenes")
    if not os.path.isdir(scenes_dir):
        return {"valid": True, "errors": [], "warnings": []}

    scene_files = [os.path.join(scenes_dir, f) for f in os.listdir(scenes_dir) if f.startswith("S") and f.endswith(".tsx")]
    if not scene_files:
        return {"valid": True, "errors": [], "warnings": []}

    banned = []
    for sf in sorted(scene_files):
        try:
            with open(sf, "r", encoding="utf-8") as f:
                content = f.read()
            for eff in ("snapZoom", "handheld", "pullBack", "dutchTilt"):
                if re.search(rf"\b{eff}\s*:", content):
                    banned.append(f"{os.path.basename(sf)}:{eff}")
        except Exception:
            pass

    if banned:
        errors.append(
            f"Banned dynamic camera effects found ({', '.join(banned)}). "
            "Do not use snapZoom, handheld, pullBack, or dutchTilt."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_character_identity(ep_dir: str) -> Dict[str, Any]:
    """Validate that CatScientist mascot conforms to the canonical orange-and-cream identity."""
    errors = []
    warnings = []
    cat_component = os.path.join(ep_dir, "src", "lib", "cast", "CatScientist.tsx")
    if os.path.isfile(cat_component):
        with open(cat_component, "r", encoding="utf-8") as f:
            content = f.read()
        grain_count = content.count("backgroundImage: `url(${GRAIN})`")
        blend_count = content.count("backgroundBlendMode: 'multiply'")
        if grain_count > 0 and blend_count < grain_count:
            errors.append(
                f"CatScientist.tsx has {grain_count} GRAIN textures but only {blend_count} 'backgroundBlendMode: multiply'. "
                "This causes white cat regression due to opaque paper texture scan occlusion."
            )
        if "#F97316" not in content:
            errors.append("CatScientist.tsx missing canonical primary orange fur token #F97316.")
        if "#FFFDF7" not in content:
            errors.append("CatScientist.tsx missing canonical secondary cream fur/snout token #FFFDF7.")
        if "#FB7185" not in content:
            errors.append("CatScientist.tsx missing canonical pink accent token #FB7185 (nose/ears).")
        # Check paws / hands have orange fur base and cream tip
        if "Layer 4: Left Arm" in content:
            left_match = re.search(r"Layer 4:\s*Left Arm[\s\S]*?Layer 5:", content)
            if left_match and "#F97316" not in left_match.group(0):
                errors.append("CatScientist.tsx Left hand/paw base must have orange fur (#F97316).")
        if "Layer 6: Right Arm" in content:
            right_match = re.search(r"Layer 6:\s*Right Arm[\s\S]*?</div>\s*</div>\s*\);\s*};", content)
            if right_match and "#F97316" not in right_match.group(0):
                errors.append("CatScientist.tsx Right hand/paw base must have orange fur (#F97316).")
    return {"errors": errors, "warnings": warnings}


def validate_episode(ep_dir_or_slug: str, strict: bool = False) -> Dict[str, Any]:
    """Run full validation suite on an episode."""
    ep_dir = resolve_episode_papercut_dir(ep_dir_or_slug)

    print("=" * 65)
    print(f"  Validating Papercraft Episode at:")
    print(f"  {ep_dir}")
    print("=" * 65)

    if not os.path.isdir(ep_dir):
        return {
            "valid": False,
            "errors": [f"Directory not found: {ep_dir}"],
            "warnings": [],
            "episode_dir": ep_dir
        }

    registered_envs = load_registered_environments()

    all_errors = []
    all_warnings = []

    # 1. Configuration
    print("• Validating episode.json...")
    res_cfg = validate_episode_config(ep_dir, registered_envs)
    all_errors.extend(res_cfg["errors"])
    all_warnings.extend(res_cfg["warnings"])
    config = res_cfg["config"]

    # 2. Scenes
    print("• Validating scene components...")
    res_scenes = validate_scene_components(ep_dir, config)
    all_errors.extend(res_scenes["errors"])
    all_warnings.extend(res_scenes["warnings"])

    # 3. Plan & Durations
    print("• Validating scene plan and durations...")
    res_plan = validate_plan_and_timing(ep_dir)
    all_errors.extend(res_plan["errors"])
    all_warnings.extend(res_plan["warnings"])

    # 4. Audio assets
    print("• Validating audio assets...")
    res_audio = validate_audio_assets(ep_dir)
    all_errors.extend(res_audio["errors"])
    all_warnings.extend(res_audio["warnings"])

    # 5. Legacy Papercut leakage
    print("• Scanning for legacy Papercut references...")
    res_legacy = scan_for_legacy_leakage(ep_dir)
    all_errors.extend(res_legacy["errors"])
    all_warnings.extend(res_legacy["warnings"])

    # 6. Character identity & color integrity
    print("• Validating Cat Scientist character identity & color integrity...")
    res_char = validate_character_identity(ep_dir)
    all_errors.extend(res_char["errors"])
    all_warnings.extend(res_char["warnings"])

    # 7. Dynamic camera variations
    print("• Validating dynamic camera moves & effects...")
    res_cam = validate_camera_effects(ep_dir)
    all_errors.extend(res_cam["errors"])
    all_warnings.extend(res_cam["warnings"])

    is_valid = len(all_errors) == 0 and (not strict or len(all_warnings) == 0)

    print("-" * 65)
    if is_valid:
        print(">> [PASS] Episode passed all validation checks!")
    else:
        print(f">> [FAIL] Episode failed validation with {len(all_errors)} error(s).")

    if all_errors:
        print("\nERRORS:")
        for err in all_errors:
            print(f"  [x] {err}")

    if all_warnings:
        print("\nWARNINGS:")
        for warn in all_warnings:
            print(f"  [!] {warn}")

    print("=" * 65)

    return {
        "valid": is_valid,
        "errors": all_errors,
        "warnings": all_warnings,
        "episode_dir": ep_dir
    }


def main():
    parser = argparse.ArgumentParser(description="Validate a 2D Papercraft Explainer episode")
    parser.add_argument("episode", nargs="?", default="episodes/01-anomali-air/papercut",
                        help="Path or slug to episode directory (default: episodes/01-anomali-air/papercut)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    args = parser.parse_args()
    res = validate_episode(args.episode, strict=args.strict)
    sys.exit(0 if res["valid"] else 1)


if __name__ == "__main__":
    main()
