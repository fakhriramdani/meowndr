#!/usr/bin/env python3
"""
Papercraft Content Factory: 20 Diverse 2D Papercraft Environments Generator.

Builds, registers, previews, and validates the complete 20-environment collection:
 1. cozy-bedroom
 2. modern-classroom
 3. home-living-room
 4. backyard-garden
 5. public-library
 6. science-laboratory
 7. city-park
 8. home-kitchen
 9. school-science-corner
10. home-study
11. mountain-viewpoint
12. tropical-beach
13. traditional-indonesian-house
14. historic-town-street
15. ancient-temple-ruins
16. rainy-city-street
17. underwater-world
18. space-observatory
19. home-workshop
20. city-rooftop

All environments strictly adhere to:
- 1080x1920 vertical 9:16 canvas
- Layered handcrafted 2D papercraft cutout construction with soft drop shadows
- Clear presenter safe zone: x = 180-900, y = 850-1650 (no props, furniture, or obstructions)
- Presenter floor anchor: x = 540, y = 1380 (clear stage floor)
- Clear header banner zone: y < 420
- Zero baked-in people, characters, animals, logos, or readable text
- Preserving existing project baselines and asset integrity
"""

import os
import sys
import json
import time
import subprocess
import shutil
from typing import Dict, Any, List

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

from env_specs import ENV_SPECS
from manage_environment import add_environment
from asset_loader import validate_environment, read_image_dimensions

BRAIN_DIR = os.path.join(
    os.path.expanduser("~"),
    ".gemini",
    "antigravity-cli",
    "brain",
    "28b506b1-8d34-4e05-9793-9646a6e11f82"
)


def render_silhouette_preview(bg_path: str, out_path: str, env_name: str, floor_y: int = 1380):
    """
    Renders an engineering verification preview with safe zone overlays,
    floor guideline, and the Cat Scientist mascot silhouette at (x=540, y=floor_y).
    """
    svg_overlay = f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="sil-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>
    </filter>
  </defs>

  <!-- Header Banner Safe Zone (y < 420) -->
  <rect x="20" y="20" width="1040" height="380" rx="8" fill="none" stroke="#3B82F6" stroke-width="3" stroke-dasharray="10 8" opacity="0.65"/>
  <rect x="30" y="30" width="220" height="34" rx="4" fill="#3B82F6" opacity="0.9"/>
  <text x="140" y="53" font-family="sans-serif" font-weight="bold" font-size="16" fill="#FFFFFF" text-anchor="middle">HEADER BANNER ZONE</text>

  <!-- Presenter Safe Zone (x: 180-900, y: 850-1650) -->
  <rect x="180" y="850" width="720" height="800" rx="12" fill="#10B981" fill-opacity="0.08" stroke="#10B981" stroke-width="3" stroke-dasharray="12 8"/>
  <rect x="190" y="860" width="250" height="34" rx="4" fill="#10B981" opacity="0.9"/>
  <text x="315" y="883" font-family="sans-serif" font-weight="bold" font-size="16" fill="#FFFFFF" text-anchor="middle">PRESENTER SAFE ZONE</text>

  <!-- Floor Line Guideline -->
  <line x1="0" y1="{floor_y}" x2="1080" y2="{floor_y}" stroke="#EF4444" stroke-width="2" stroke-dasharray="6 6" opacity="0.75"/>
  <rect x="20" y="{floor_y - 28}" width="160" height="24" rx="4" fill="#EF4444" opacity="0.85"/>
  <text x="100" y="{floor_y - 12}" font-family="sans-serif" font-weight="bold" font-size="13" fill="#FFFFFF" text-anchor="middle">FLOOR Y = {floor_y}</text>

  <!-- Presenter Character Silhouette (Cat Scientist silhouette) anchored at x=540, y=floor_y -->
  <g filter="url(#sil-shadow)" transform="translate(540, {floor_y})">
    <ellipse cx="0" cy="8" rx="110" ry="22" fill="#000000" opacity="0.25"/>
    <path d="M 60 -40 Q 120 -80 110 -130 Q 100 -160 85 -145 Q 90 -110 50 -60 Z" fill="#F97316"/>
    <path d="M -80 -20 Q -90 -160 -60 -210 L 60 -210 Q 90 -160 80 -20 Z" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="3"/>
    <path d="M 0 -210 L -25 -110 L 0 -110 L 25 -110 Z" fill="#E2E8F0"/>
    <circle cx="0" cy="-80" r="5" fill="#94A3B8"/>
    <circle cx="0" cy="-50" r="5" fill="#94A3B8"/>
    <ellipse cx="-40" cy="-10" rx="20" ry="12" fill="#EA580C"/>
    <ellipse cx="40" cy="-10" rx="20" ry="12" fill="#EA580C"/>
    <circle cx="0" cy="-280" r="75" fill="#F97316"/>
    <ellipse cx="-35" cy="-265" rx="30" ry="20" fill="#FFF7ED"/>
    <ellipse cx="35" cy="-265" rx="30" ry="20" fill="#FFF7ED"/>
    <polygon points="-55,-325 -75,-395 -15,-345" fill="#EA580C"/>
    <polygon points="-50,-330 -68,-380 -22,-345" fill="#FDBA74"/>
    <polygon points="55,-325 75,-395 15,-345" fill="#EA580C"/>
    <polygon points="50,-330 68,-380 22,-345" fill="#FDBA74"/>
    <circle cx="-25" cy="-285" r="24" fill="none" stroke="#0F172A" stroke-width="4"/>
    <circle cx="25" cy="-285" r="24" fill="none" stroke="#0F172A" stroke-width="4"/>
    <line x1="-1" y1="-285" x2="1" y2="-285" stroke="#0F172A" stroke-width="4"/>
    <ellipse cx="-25" cy="-285" rx="14" ry="16" fill="#0F172A"/>
    <ellipse cx="25" cy="-285" rx="14" ry="16" fill="#0F172A"/>
    <circle cx="-21" cy="-290" r="5" fill="#FFFFFF"/>
    <circle cx="29" cy="-290" r="5" fill="#FFFFFF"/>
    <polygon points="-5,-268 5,-268 0,-262" fill="#F43F5E"/>
    <path d="M -8 -258 Q 0 -252 8 -258" fill="none" stroke="#0F172A" stroke-width="2.5"/>
    <circle cx="0" cy="0" r="16" fill="none" stroke="#EF4444" stroke-width="3"/>
    <line x1="-24" y1="0" x2="24" y2="0" stroke="#EF4444" stroke-width="3"/>
    <line x1="0" y1="-24" x2="0" y2="24" stroke="#EF4444" stroke-width="3"/>
  </g>

  <rect x="540" y="320" width="560" height="48" rx="6" fill="#0F172A" opacity="0.85" transform="translate(-280, 0)"/>
  <text x="540" y="352" font-family="sans-serif" font-weight="900" font-size="20" fill="#FFFFFF" text-anchor="middle">{env_name.upper()} COMPOSITION CHECK</text>
</svg>"""

    svg_tmp = f"/tmp/{os.path.basename(out_path)}.svg"
    with open(svg_tmp, "w", encoding="utf-8") as f:
        f.write(svg_overlay)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    subprocess.run(["npx", "--yes", "sharp-cli", "-i", bg_path, "-o", out_path, "composite", svg_tmp], check=True, capture_output=True)
    if os.path.exists(svg_tmp):
        os.remove(svg_tmp)


def generate_all_environments():
    print("=" * 80)
    print("PAPERCRAFT CONTENT FACTORY: 20-ENVIRONMENT GENERATION SUITE")
    print("=" * 80)

    results = []
    start_all = time.time()

    for idx, spec in enumerate(ENV_SPECS, 1):
        env_id = spec["id"]
        name = spec["name"]
        print(f"\n[{idx:02d}/20] Processing '{env_id}' ({name})...")

        # 1. Check if already exists in assets/backgrounds
        env_dir = os.path.join(REPO_ROOT, "assets", "backgrounds", env_id)
        if os.path.isdir(env_dir):
            print(f"  [WARN] Environment directory '{env_id}' already exists at {env_dir}.")

        # 2. Render SVG artwork to 1080x1920 PNG
        t0 = time.time()
        svg_code = spec["svg"]()
        svg_tmp = f"/tmp/{env_id}.svg"
        png_tmp = f"/tmp/{env_id}.png"

        with open(svg_tmp, "w", encoding="utf-8") as f:
            f.write(svg_code)

        subprocess.run(
            ["npx", "--yes", "sharp-cli", "-i", svg_tmp, "-o", png_tmp],
            check=True,
            capture_output=True,
        )

        w, h, fmt = read_image_dimensions(png_tmp)
        if w != 1080 or h != 1920:
            raise ValueError(f"Rendered PNG {env_id} is {w}x{h}, expected 1080x1920!")

        print(f"  - Rendered 1080x1920 PNG ({time.time() - t0:.2f}s)")

        # 3. Register Environment in Asset Library via add_environment
        t1 = time.time()
        reg_result = add_environment(
            image_path=png_tmp,
            env_id=env_id,
            name=name,
            description=spec["description"],
            category=spec["category"],
            mood=spec["mood"],
            floor_y=1380,
            presenter_zone={"x_range": [180, 900], "y_range": [850, 1650], "status": "clear_unobstructed"},
            header_zone={"y_range": [0, 420], "status": "clear_for_banner"},
            caption_zone={"y_range": [1300, 1550], "status": "low_detail_for_legibility"},
            best_for=spec.get("best_for"),
            color_palette=spec.get("palette"),
            lighting=spec.get("lighting", "Soft ambient lighting"),
            allow_overwrite=True,
            root_dir=REPO_ROOT,
        )
        print(f"  - Registered in asset library & rendered scene preview ({time.time() - t1:.2f}s)")

        bg_dest = os.path.join(REPO_ROOT, "assets", "backgrounds", env_id, "background.png")
        meta_dest = os.path.join(REPO_ROOT, "assets", "backgrounds", env_id, "metadata.json")
        scene_preview = os.path.join(REPO_ROOT, "assets", "previews", f"{env_id}-scene-preview.png")

        # 4. Render Presenter Silhouette Verification Preview
        t2 = time.time()
        sil_preview = os.path.join(REPO_ROOT, "assets", "previews", f"{env_id}-silhouette-preview.png")
        render_silhouette_preview(bg_dest, sil_preview, name, floor_y=1380)
        print(f"  - Rendered silhouette verification preview ({time.time() - t2:.2f}s)")

        # 5. Copy Previews to Brain Artifacts Directory
        if os.path.isdir(BRAIN_DIR):
            shutil.copy2(scene_preview, os.path.join(BRAIN_DIR, f"{env_id}-scene-preview.png"))
            shutil.copy2(sil_preview, os.path.join(BRAIN_DIR, f"{env_id}-silhouette-preview.png"))

        # 6. Validate Environment Integrity
        val_result = reg_result.get("validation")
        if not val_result or not val_result["valid"]:
            print(f"  [ERROR] Validation failed for {env_id}: {val_result.get('errors') if val_result else 'None'}")
            raise RuntimeError(f"Validation failed for {env_id}")
        else:
            print("  - Validation passed: dimensions 1080x1920, zones clear, metadata valid.")

        results.append({
            "id": env_id,
            "name": name,
            "category": spec["category"],
            "mood": spec["mood"],
            "background": bg_dest,
            "metadata": meta_dest,
            "scene_preview": scene_preview,
            "sil_preview": sil_preview,
            "valid": val_result["valid"],
        })

        # Cleanup tmp files
        if os.path.exists(svg_tmp):
            os.remove(svg_tmp)
        if os.path.exists(png_tmp):
            os.remove(png_tmp)

    total_time = time.time() - start_all
    print("\n" + "=" * 80)
    print(f"ALL 20 ENVIRONMENTS GENERATED, REGISTERED & VALIDATED IN {total_time:.1f}s")
    print("=" * 80)

    # Print Table
    print(f"{'#':<3} | {'ID':<28} | {'Category':<24} | {'Status':<8}")
    print("-" * 80)
    for idx, r in enumerate(results, 1):
        status = "PASS" if r["valid"] else "FAIL"
        print(f"{idx:<3} | {r['id']:<28} | {r['category']:<24} | {status:<8}")

    return results


if __name__ == "__main__":
    generate_all_environments()
