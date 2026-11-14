#!/usr/bin/env python3
"""
Papercraft Explainer Episode Scaffolding CLI.

Usage:
    python3 library/tools/scaffold_episode.py <slug> "<title>" [options]

Options:
    --topic <topic>         Scientific topic summary (default: inferred from title)
    --env <environment_id>  Environment background ID from asset library (default: science-lab)
    --comp <CompName>       Remotion composition name (default: PascalCase of slug)
    --out <out_prefix>      Output file prefix (default: episode-<slug>)
    --target-sec <sec>      Target duration in seconds (default: 60)
    --force                 Allow scaffolding into existing directory without wiping files

Example:
    python3 library/tools/scaffold_episode.py 02-fotosintesis "Bagaimana Tumbuhan Makan?" \
        --topic "Proses Fotosintesis" --env botany-greenhouse
"""

import os
import sys
import argparse
import json
import shutil
import subprocess
import re
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
LIB_DIR = os.path.join(REPO_ROOT, "library")
TEMPLATE_DIR = os.path.join(LIB_DIR, "papercut", "template")
ASSETS_LIB_PATH = os.path.join(REPO_ROOT, "assets", "library.json")

sys.path.insert(0, str(REPO_ROOT))
from library.content_factory.bgm_matcher import match_bgm_for_episode, validate_bed_preset
from library.platform_utils import copy_tree_merge, link_dir_or_junction, sync_kit


def to_pascal_case(s):
    clean = re.sub(r'[^a-zA-Z0-9]+', ' ', s)
    return ''.join(word.capitalize() for word in clean.split())


def get_environment_floor_y(env_id):
    try:
        with open(ASSETS_LIB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for env in data.get("categories", {}).get("environments", []):
            if env.get("id") == env_id:
                return env.get("floor_y", 1380)
    except Exception:
        pass
    return 1380


def scaffold_episode(slug, title, topic=None, env_id="science-laboratory", comp_name=None, out_prefix=None, target_sec=60, force=False, niche="science", bed_preset=None):
    if not topic:
        topic = title

    clean_slug = re.sub(r'[^a-zA-Z0-9_-]', '', slug).strip()
    if not clean_slug or clean_slug == "episodes":
        print(f"[ERROR] Invalid episode slug: '{slug}'. Cannot use reserved name 'episodes'.")
        sys.exit(1)

    # Validate numeric prefix to prevent duplicate episode numbers
    num_match = re.match(r'^(\d+)', clean_slug)
    if num_match:
        ep_num = num_match.group(1)
        episodes_root = os.path.join(REPO_ROOT, "episodes")
        if os.path.isdir(episodes_root):
            for existing in os.listdir(episodes_root):
                if existing != clean_slug and re.match(rf'^{ep_num}[-_]', existing):
                    print(f"[ERROR] Episode number '{ep_num}' is already used by existing episode: 'episodes/{existing}'.")
                    print("Choose a unique sequential episode number to avoid collisions.")
                    sys.exit(1)

    if not comp_name:
        # e.g. 02-fotosintesis -> Episode02
        match = re.match(r'^(\d+)', clean_slug)
        if match:
            comp_name = f"Episode{int(match.group(1)):02d}"
        else:
            comp_name = f"Episode{to_pascal_case(clean_slug)}"

    if not out_prefix:
        out_prefix = f"episode-{clean_slug}"

    episode_dir = os.path.join(REPO_ROOT, "episodes", clean_slug)
    papercut_dir = os.path.join(episode_dir, "papercut")

    print("=" * 65)
    print(f"  Scaffolding 2D Papercraft Explainer: {slug}")
    print("=" * 65)

    if os.path.exists(papercut_dir) and not force:
        if os.path.exists(os.path.join(papercut_dir, "src", "Root.tsx")):
            print(f"[ERROR] Destination already scaffolded: {papercut_dir}")
            print("Use --force if you intentionally wish to refresh the template scaffolding.")
            sys.exit(1)

    # 1. Create directory hierarchy
    research_dir = os.path.join(episode_dir, "research")
    narration_dir = os.path.join(episode_dir, "narration")
    voice_dir = os.path.join(narration_dir, "voice")

    os.makedirs(research_dir, exist_ok=True)
    os.makedirs(narration_dir, exist_ok=True)
    os.makedirs(voice_dir, exist_ok=True)
    os.makedirs(papercut_dir, exist_ok=True)

    # 2. Research & Script starter files
    facts_file = os.path.join(research_dir, "facts.md")
    if not os.path.exists(facts_file):
        with open(facts_file, "w", encoding="utf-8") as f:
            f.write(f"""# Research Notes: {title}

## Scientific Topic
**{topic}**

## Core Scientific Claims & Sources
1. [Claim 1: Core mechanism to be explained]
2. [Claim 2: Why it matters ecologically / physically]
3. [Source URLs & references]

## Visual Concept & Demonstration Ideas
- Hook demonstration:
- Main scientific demonstration:
- Takeaway summary:
""")

    script_file = os.path.join(narration_dir, "script.json")
    if not os.path.exists(script_file):
        starter_script = [
            {"id": "l1_hook", "text": f"Pernahkah kamu penasaran, {title.lower()}"},
            {"id": "l2_concept", "text": f"Secara sains, {topic.lower()} memiliki mekanisme yang menakjubkan."},
            {"id": "l3_outro", "text": "Sains itu seru dan dekat dengan kita. Ikuti untuk sains berikutnya!"}
        ]
        with open(script_file, "w", encoding="utf-8") as f:
            json.dump(starter_script, f, indent=2, ensure_ascii=False)

    # 3. Copy base template (pure-Python cross-platform, ignoring node_modules and build artifacts)
    print("• Copying template infrastructure...")
    copy_tree_merge(
        Path(TEMPLATE_DIR),
        Path(papercut_dir),
        ignore_names={"node_modules", "build", ".remotion", "out"},
        overwrite=False,
    )

    # 4. Link or install node_modules (symlink on POSIX, NTFS junction on Windows, else npm install)
    nm_dest = os.path.join(papercut_dir, "node_modules")
    if not os.path.exists(nm_dest) and not os.path.islink(nm_dest):
        template_nm = os.path.join(TEMPLATE_DIR, "node_modules")
        if os.path.isdir(template_nm) and link_dir_or_junction(Path(template_nm), Path(nm_dest)):
            print(f"• Linked node_modules from shared template ({template_nm})")
        else:
            npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
            print("• Running npm install in episode directory...")
            subprocess.run([npm_cmd, "install", "--no-audit", "--no-fund"], cwd=papercut_dir, check=True)

    # 5. Sync shared kit (CatScientist, Overlays, Science Models, etc.)
    print("• Syncing shared papercraft kit...")
    sync_kit(Path(papercut_dir))

    # 5b. Sync registered asset library into public/assets/
    root_assets = os.path.join(REPO_ROOT, "assets")
    if os.path.isdir(root_assets):
        print("• Syncing registered asset library into public/assets/...")
        copy_tree_merge(Path(root_assets), Path(papercut_dir) / "public" / "assets", overwrite=True)

    # 6. Customize episode.json with typed configuration
    floor_y = get_environment_floor_y(env_id)
    ep_config_path = os.path.join(papercut_dir, "episode.json")

    # Split title for hook
    title_words = [w.upper() for w in re.sub(r'[^a-zA-Z0-9\s]', '', title).split()]
    half = max(1, len(title_words) // 2)
    hook_lines = [title_words[:half], title_words[half:]]
    hot_words = title_words[half:] if title_words[half:] else title_words[:1]

    # Match BGM Bed to episode theme, niche, and title
    if bed_preset and validate_bed_preset(bed_preset):
        chosen_bed = bed_preset
        bgm_match = {"preset": chosen_bed, "bpm": 120, "mood": "user selected", "match_reason": "explicit override"}
    else:
        bgm_match = match_bgm_for_episode(title=title, topic=topic, niche=niche)
        chosen_bed = bgm_match["preset"]

    ep_config = {
        "comp": comp_name,
        "out": out_prefix,
        "meta": {
            "id": clean_slug,
            "title": title,
            "topic": topic,
            "language": "id",
            "targetDurationSeconds": target_sec,
            "fps": 30,
            "width": 1080,
            "height": 1920,
            "niche": niche
        },
        "environment": {
            "id": env_id,
            "floorY": floor_y
        },
        "niche": niche,
        "bed": chosen_bed,
        "narration": "../narration",
        "timing": "timing_narrator.js",
        "fps": 30,
        "start": 0.15,
        "gap": 0.1,
        "hold": 0.8,
        "hook": {
            "lines": hook_lines,
            "hot": hot_words,
            "hold": 1.8
        },
        "cta": {
            "heading": "SUKA & BAGIKAN!",
            "handle": "@meowndr"
        },
        "scenes": [
            ["S01Hook", "l1_hook", 0],
            ["S02Concept", "l2_concept", 0],
            ["S03Outro", "l3_outro", 0]
        ],
        "banners": {
            "S01Hook": f"{title.upper()}",
            "S02Concept": "",
            "S03Outro": ""
        },
        "cuts": {
            "S02Concept": {"kind": "pageTurn"},
            "S03Outro": {"kind": "popUpBook"}
        }
    }

    with open(ep_config_path, "w", encoding="utf-8") as f:
        json.dump(ep_config, f, indent=2, ensure_ascii=False)

    # 7. Generate starter scene files using CatScientist and PapercraftSceneShell
    scenes_src_dir = os.path.join(papercut_dir, "src", "scenes")
    os.makedirs(scenes_src_dir, exist_ok=True)

    # S01Hook starter
    s01_path = os.path.join(scenes_src_dir, "S01Hook.tsx")
    if not os.path.exists(s01_path):
        with open(s01_path, "w", encoding="utf-8") as f:
            f.write(f"""import React from 'react';
import {{PapercraftSceneShell}} from '../lib/scenes';
import {{PapercraftBadge}} from '../lib/overlays';
import {{durOf}} from '../scene';

const ID = 'S01Hook';

/**
 * S01Hook: Starter Hook Scene.
 * Uses approved Cat Scientist mascot and '{env_id}' background.
 */
export const S01Hook: React.FC = () => {{
  const dur = durOf(ID);

  return (
    <PapercraftSceneShell
      durationInFrames={{dur}}
      environment="{env_id}"
      camera={{{{yaw: 6, push: 1.06}}}}
      presenter={{{{
        x: 360,
        state: 'curious',
        face: 1,
      }}}}
      badges={{[]}}
    >
      {{/* Slot for bespoke animated physical papercraft apparatus (e.g. models, dials, instruments) - NO verbal explanatory text badges */}}
    </PapercraftSceneShell>
  );
}};
""")

    # S02Concept starter
    s02_path = os.path.join(scenes_src_dir, "S02Concept.tsx")
    if not os.path.exists(s02_path):
        with open(s02_path, "w", encoding="utf-8") as f:
            f.write(f"""import React from 'react';
import {{PapercraftSceneShell}} from '../lib/scenes';
import {{durOf}} from '../scene';

const ID = 'S02Concept';

/**
 * S02Concept: Scientific Explanation Scene.
 * Demonstrates the core concept with Cat Scientist in explaining state.
 */
export const S02Concept: React.FC = () => {{
  const dur = durOf(ID);

  return (
    <PapercraftSceneShell
      durationInFrames={{dur}}
      environment="{env_id}"
      camera={{{{yaw: -6, push: 1.07}}}}
      presenter={{{{
        x: 320,
        state: 'explaining',
        pointAngle: -35,
        face: 1,
      }}}}
      badges={{[]}}
    >
      {{/* Scientific visualization slot - bespoke physical papercraft model */}}
    </PapercraftSceneShell>
  );
}};
""")

    # S03Outro starter
    s03_path = os.path.join(scenes_src_dir, "S03Outro.tsx")
    if not os.path.exists(s03_path):
        with open(s03_path, "w", encoding="utf-8") as f:
            f.write(f"""import React from 'react';
import {{PapercraftSceneShell}} from '../lib/scenes';
import {{PapercraftCtaCard}} from '../lib/overlays';
import {{PopIn}} from '../lib/paper/kit';
import {{durOf}} from '../scene';

const ID = 'S03Outro';

/**
 * S03Outro: Friendly Outro & Social CTA Scene.
 */
export const S03Outro: React.FC = () => {{
  const dur = durOf(ID);

  return (
    <PapercraftSceneShell
      durationInFrames={{dur}}
      environment="{env_id}"
      camera={{{{yaw: 4, push: 1.05}}}}
      presenter={{{{
        x: 360,
        state: 'waving',
        face: 1,
      }}}}
    >
      {{/* Multi-layered papercraft CTA card */}}
      <PopIn at={{15}}>
        <PapercraftCtaCard x={{720}} y={{760}} scale={{0.95}} />
      </PopIn>
    </PapercraftSceneShell>
  );
}};
""")

    # Write scenes/index.ts
    scenes_idx_path = os.path.join(scenes_src_dir, "index.ts")
    with open(scenes_idx_path, "w", encoding="utf-8") as f:
        f.write(f"""import React from 'react';
import {{S01Hook}} from './S01Hook';
import {{S02Concept}} from './S02Concept';
import {{S03Outro}} from './S03Outro';

export type SceneDef = {{id: string; component: React.FC; banner: string; band: number}};

export const SCENES: SceneDef[] = [
  {{id: 'S01Hook', component: S01Hook, banner: '{ep_config["banners"]["S01Hook"]}', band: 0.77}},
  {{id: 'S02Concept', component: S02Concept, banner: '', band: 0.77}},
  {{id: 'S03Outro', component: S03Outro, banner: '', band: 0.77}},
];
""")

    # 8. Starter plan.json with valid default scene timings
    plan_path = os.path.join(papercut_dir, "src", "plan.json")
    starter_plan = {
        "fps": 30,
        "durationInFrames": 450,
        "hook": {
            "lines": hook_lines,
            "hot": hot_words,
            "outAt": 54
        },
        "scenes": [
            {
                "id": "S01Hook",
                "from": 0,
                "durationInFrames": 150,
                "words": [{"text": "Pernahkah", "f": 10}, {"text": "kamu", "f": 25}, {"text": "penasaran", "f": 40}]
            },
            {
                "id": "S02Concept",
                "from": 150,
                "durationInFrames": 180,
                "words": [{"text": "Secara", "f": 15}, {"text": "sains", "f": 35}, {"text": "bekerja", "f": 60}]
            },
            {
                "id": "S03Outro",
                "from": 330,
                "durationInFrames": 120,
                "words": [{"text": "Sains", "f": 10}, {"text": "itu", "f": 25}, {"text": "seru", "f": 45}]
            }
        ]
    }
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(starter_plan, f, indent=1)

    # 9. Starter silent audio assets so preview works out of the box
    os.makedirs(os.path.join(papercut_dir, "public", "vo"), exist_ok=True)
    os.makedirs(os.path.join(papercut_dir, "public", "audio"), exist_ok=True)

    silent_wav_files = [
        os.path.join(papercut_dir, "public", "vo", "voiceover.wav"),
        os.path.join(papercut_dir, "public", "audio", "music.wav"),
        os.path.join(papercut_dir, "public", "audio", "fx.wav")
    ]
    for wav_file in silent_wav_files:
        if not os.path.exists(wav_file):
            subprocess.run([
                "ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-t", "15.0", wav_file
            ], check=True)

    starter_captions = [
        {"text": "Pernahkah", "startMs": 300, "endMs": 700, "timestampMs": 500, "confidence": 1},
        {"text": "kamu", "startMs": 750, "endMs": 1100, "timestampMs": 925, "confidence": 1},
        {"text": "penasaran", "startMs": 1150, "endMs": 1800, "timestampMs": 1475, "confidence": 1},
    ]
    with open(os.path.join(papercut_dir, "public", "vo", "captions.json"), "w", encoding="utf-8") as f:
        json.dump(starter_captions, f, indent=2)

    # 10. Summary Report
    print("\n" + "=" * 65)
    print(f">> SCAFFOLD SUCCESSFUL: {clean_slug}")
    print("=" * 65)
    print(f"• Location:      episodes/{clean_slug}/papercut")
    print(f"• Niche:         {niche}")
    print(f"• Composition:   {comp_name}")
    print(f"• Environment:   {env_id} (floorY: {floor_y})")
    print(f"• Matched BGM:   {chosen_bed} ({bgm_match.get('mood', '')}, {bgm_match.get('bpm', 120)} bpm)")
    print(f"  Match Reason:  {bgm_match.get('match_reason', '')}")
    print(f"• Output target: out/{out_prefix}.mp4")
    print("\n[Commands]")
    print(f"  1. Validate:   python3 library/tools/validate_episode.py episodes/{clean_slug}/papercut")
    print(f"  2. Preview:    cd episodes/{clean_slug}/papercut && npx remotion preview")
    print(f"  3. Render:     cd episodes/{clean_slug}/papercut && npx remotion render {comp_name} out/{out_prefix}.mp4")
    print("\n[Creator Checklist]")
    print("  [ ] Write factual claims in research/facts.md")
    print("  [ ] Polish dialogue script in narration/script.json")
    print("  [ ] Generate narration audio with local TTS into narration/voice/")
    print("  [ ] Run python3 library/tools/build_vo.py to update plan.json and captions")
    print("  [ ] Customize S01Hook, S02Concept, S03Outro with topic papercraft models")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new 2D Papercraft Explainer episode")
    parser.add_argument("slug", help="Episode folder slug (e.g. 02-fotosintesis)")
    parser.add_argument("title", help="Episode title in Indonesian (e.g. 'Bagaimana Tumbuhan Makan?')")
    parser.add_argument("--topic", help="Scientific topic description")
    parser.add_argument("--niche", default="science", help="Content niche (science, history, geography, technology, mystery, psychology)")
    parser.add_argument("--bed", default=None, help="Explicit BGM bed override (e.g. marimba-G-116)")
    parser.add_argument("--env", default="science-laboratory", help="Environment background ID (default: science-laboratory)")
    parser.add_argument("--comp", help="Remotion composition ID (default: EpisodeNN)")
    parser.add_argument("--out", help="Output file prefix (default: episode-<slug>)")
    parser.add_argument("--target-sec", type=int, default=60, help="Target duration in seconds (default: 60)")
    parser.add_argument("--force", action="store_true", help="Allow scaffolding into existing directory")

    args = parser.parse_args()
    scaffold_episode(
        slug=args.slug,
        title=args.title,
        topic=args.topic,
        env_id=args.env,
        comp_name=args.comp,
        out_prefix=args.out,
        target_sec=args.target_sec,
        force=args.force,
        niche=args.niche,
        bed_preset=args.bed
    )


if __name__ == "__main__":
    main()
