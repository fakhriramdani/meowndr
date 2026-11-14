#!/usr/bin/env python3
"""
thumbnail_generator.py: Standalone & Pipeline Thumbnail Renderer for Papercraft Episodes.
Generates:
  1. Standalone YouTube 16:9 thumbnail (1280x720) -> out/thumbnail.png
  2. Opening Thumbnail Frame 9:16 preview (1080x1920) -> out/opening-frame.png
Runs automated physical validation against mandatory branding rules.
"""

import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.tools.validate_thumbnail import ThumbnailValidator
from library.content_factory.brand_config import get_default_thumbnail_config

def render_episode_thumbnails(episode_slug: str, validate_after: bool = True) -> bool:
    ep_dir = REPO_ROOT / "episodes" / episode_slug / "papercut"
    out_dir = ep_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    ep_json_path = ep_dir / "episode.json"
    if not ep_json_path.exists():
        print(f"[ERROR] episode.json not found at {ep_json_path}")
        return False

    with open(ep_json_path, "r", encoding="utf-8") as f:
        ep_data = json.load(f)

    # Ensure thumbnail block exists
    if "thumbnail" not in ep_data:
        print("[INFO] Adding default thumbnail configuration to episode.json...")
        ep_data["thumbnail"] = get_default_thumbnail_config(ep_data.get("meta", {}))
        with open(ep_json_path, "w", encoding="utf-8") as f:
            json.dump(ep_data, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print(f"  Rendering Thumbnails for Episode: {episode_slug}")
    print("=" * 70)

    # 1. Render 16:9 YouTube Thumbnail (Composition: Thumbnail)
    thumb_out = out_dir / "thumbnail.png"
    rel_thumb_out = thumb_out.relative_to(ep_dir)
    print(f"Rendering 16:9 YouTube Thumbnail (1280x720) -> {thumb_out}...")
    cmd_thumb = [
        "npx", "remotion", "still",
        "Thumbnail",
        str(rel_thumb_out),
        "--frame=0"
    ]
    subprocess.run(cmd_thumb, cwd=ep_dir, check=True)
    print(f">> 16:9 Thumbnail rendered successfully: {thumb_out}")

    # 2. Render 9:16 Opening Thumbnail Frame (Composition: OpeningFrame)
    opening_out = out_dir / "opening-frame.png"
    rel_opening_out = opening_out.relative_to(ep_dir)
    print(f"Rendering 9:16 Opening Thumbnail Frame (1080x1920) -> {opening_out}...")
    cmd_open = [
        "npx", "remotion", "still",
        "OpeningFrame",
        str(rel_opening_out),
        "--frame=0"
    ]
    subprocess.run(cmd_open, cwd=ep_dir, check=True)
    print(f">> 9:16 Opening Frame rendered successfully: {opening_out}")

    # Ensure opening-frame is staged in public/ for frame 0 poster thumbnail embedding in video
    pub_opening = ep_dir / "public" / "opening-frame.png"
    pub_opening.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(opening_out, pub_opening)

    # 3. Automated Validation
    if validate_after:
        validator = ThumbnailValidator(episode_slug)
        ok = validator.validate()
        return ok

    return True

def main():
    parser = argparse.ArgumentParser(description="Papercraft Episode Thumbnail Generator")
    parser.add_argument("slug", help="Episode slug (e.g. 05-bintang-berkelip)")
    parser.add_argument("--no-validate", action="store_true", help="Skip post-render validation")
    args = parser.parse_args()

    success = render_episode_thumbnails(args.slug, validate_after=not args.no_validate)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
