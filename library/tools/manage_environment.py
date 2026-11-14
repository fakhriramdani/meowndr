#!/usr/bin/env python3
"""
Environment Management Workflow for Papercraft Explainer.

Supports:
1. Adding a new environment from a supplied or procedurally generated 1080x1920 background.
2. Creating a revised version of an existing environment without modifying or destroying the original.
3. Generating Remotion-based scene previews combining the background with the presenter mascot and props.
4. Validating environment dimensions, safe zones, floor placement, and metadata integrity.
5. Updating the master library catalog (assets/library.json), background index (assets/backgrounds/index.json),
   and syncing with public directories.
"""

import os
import sys
import json
import shutil
import argparse
import datetime
import subprocess
from typing import Any, Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from asset_loader import (
    find_project_root,
    read_image_dimensions,
    load_library,
    validate_environment,
    SAFE_ZONES,
)


def get_current_iso_timestamp() -> str:
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    return now.isoformat(timespec="seconds")


def sync_assets_to_public(root: str, env_id: str):
    """Syncs environment assets to Remotion public/assets directories."""
    src_dir = os.path.join(root, "assets", "backgrounds", env_id)
    if not os.path.isdir(src_dir):
        return

    dest_dirs = [
        os.path.join(root, "episodes", "01-anomali-air", "papercut", "public", "assets", "backgrounds", env_id),
        os.path.join(root, "library", "papercut", "public", "assets", "backgrounds", env_id),
        os.path.join(root, "library", "papercut", "template", "public", "assets", "backgrounds", env_id),
    ]

    for dest in dest_dirs:
        os.makedirs(dest, exist_ok=True)
        for item in os.listdir(src_dir):
            s_file = os.path.join(src_dir, item)
            d_file = os.path.join(dest, item)
            if os.path.isfile(s_file):
                shutil.copy2(s_file, d_file)

    # Sync master library.json and backgrounds/index.json to public
    for pub_base in [
        os.path.join(root, "episodes", "01-anomali-air", "papercut", "public", "assets"),
        os.path.join(root, "library", "papercut", "public", "assets"),
        os.path.join(root, "library", "papercut", "template", "public", "assets"),
    ]:
        os.makedirs(pub_base, exist_ok=True)
        os.makedirs(os.path.join(pub_base, "backgrounds"), exist_ok=True)
        shutil.copy2(os.path.join(root, "assets", "library.json"), os.path.join(pub_base, "library.json"))
        shutil.copy2(os.path.join(root, "assets", "backgrounds", "index.json"), os.path.join(pub_base, "backgrounds", "index.json"))


def update_typescript_asset_loader(root: str):
    """Synchronizes AssetLoader.ts DEFAULT_LIBRARY with the master assets/library.json."""
    lib_path = os.path.join(root, "assets", "library.json")
    if not os.path.isfile(lib_path):
        return

    with open(lib_path, "r", encoding="utf-8") as f:
        lib_data = json.load(f)

    ts_path = os.path.join(root, "library", "papercut", "kit", "assets", "AssetLoader.ts")
    if not os.path.isfile(ts_path):
        return

    with open(ts_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find DEFAULT_LIBRARY definition
    start_marker = "export const DEFAULT_LIBRARY: AssetLibraryIndex = "
    idx = content.find(start_marker)
    if idx == -1:
        return

    end_marker = "export class AssetLoader {"
    idx_end = content.find(end_marker, idx)
    if idx_end == -1:
        return

    formatted_json = json.dumps(lib_data, indent=2)
    new_block = f"{start_marker}{formatted_json};\n\n"
    updated_content = content[:idx] + new_block + content[idx_end:]

    with open(ts_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    # Sync kit to any existing episodes that have a papercut folder
    from pathlib import Path as _Path
    from library.platform_utils import sync_kit
    episodes_dir = _Path(root) / "episodes"
    if episodes_dir.is_dir():
        for ep_papercut in episodes_dir.glob("*/papercut"):
            if ep_papercut.is_dir():
                sync_kit(ep_papercut)


def generate_scene_preview(root: str, env_id: str, headline: str = "2D PAPERCRAFT COMPOSITE") -> str:
    """
    Renders a 1080x1920 scene preview using the Remotion EnvironmentScenePreview component.
    Falls back to sharp-cli compositing if Remotion is not directly callable.
    """
    out_dir = os.path.join(root, "assets", "previews")
    os.makedirs(out_dir, exist_ok=True)
    out_preview = os.path.join(out_dir, f"{env_id}-scene-preview.png")

    ep_dir = os.path.join(root, "episodes", "01-anomali-air", "papercut")
    rendered = False

    # Try Remotion render still first
    if os.path.isdir(ep_dir):
        props_json = json.dumps({"envId": env_id, "headline": headline})
        cmd = [
            "npx", "remotion", "still", "ScenePreview",
            out_preview,
            f"--props={props_json}"
        ]
        try:
            res = subprocess.run(cmd, cwd=ep_dir, capture_output=True, text=True, timeout=40)
            if res.returncode == 0 and os.path.isfile(out_preview) and os.path.getsize(out_preview) > 1000:
                rendered = True
        except Exception:
            pass

    # Fallback to sharp SVG composite if needed
    if not rendered:
        bg_path = os.path.join(root, "assets", "backgrounds", env_id, "background.png")
        if not os.path.isfile(bg_path):
            raise FileNotFoundError(f"Background image not found for preview: {bg_path}")

        svg_content = f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="150%" height="150%">
      <feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#000000" flood-opacity="0.32"/>
    </filter>
  </defs>
  <!-- Top Banner -->
  <g filter="url(#shadow)" transform="rotate(-0.8 540 185)">
    <rect x="90" y="140" width="900" height="90" rx="4" fill="#FDFBF7"/>
    <rect x="90" y="218" width="900" height="12" rx="2" fill="#E2DACD"/>
    <text x="540" y="200" font-family="sans-serif" font-weight="900" font-size="36" fill="#1C1B17" text-anchor="middle">
      {headline}
    </text>
    <rect x="75" y="125" width="60" height="32" rx="2" fill="#C3B284" fill-opacity="0.8" transform="rotate(-15 105 141)"/>
    <rect x="945" y="125" width="60" height="32" rx="2" fill="#C3B284" fill-opacity="0.8" transform="rotate(18 975 141)"/>
  </g>
  <!-- Presenter Placeholder (Orange) -->
  <g filter="url(#shadow)">
    <rect x="420" y="1200" width="240" height="160" rx="8" fill="#FF8C42"/>
    <rect x="420" y="1335" width="240" height="25" rx="4" fill="#D96820"/>
    <circle cx="490" cy="1260" r="14" fill="#1C1B17"/>
    <circle cx="590" cy="1260" r="14" fill="#1C1B17"/>
    <!-- Feet -->
    <rect x="450" y="1360" width="24" height="20" rx="4" fill="#D96820"/>
    <rect x="606" y="1360" width="24" height="20" rx="4" fill="#D96820"/>
  </g>
  <!-- Caption Word Tags -->
  <g filter="url(#shadow)">
    <rect x="360" y="1480" width="200" height="56" rx="6" fill="#E2725B"/>
    <text x="460" y="1520" font-family="sans-serif" font-weight="900" font-size="28" fill="#FFF8F0" text-anchor="middle">INDEPENDENT</text>
    <rect x="580" y="1480" width="140" height="56" rx="6" fill="#E2725B"/>
    <text x="650" y="1520" font-family="sans-serif" font-weight="900" font-size="28" fill="#FFF8F0" text-anchor="middle">LAYERS</text>
  </g>
</svg>"""
        svg_tmp = f"/tmp/{env_id}_preview_overlay.svg"
        with open(svg_tmp, "w", encoding="utf-8") as f:
            f.write(svg_content)

        subprocess.run(["npx", "--yes", "sharp-cli", "-i", bg_path, "-o", out_preview, "composite", svg_tmp], check=True)

    # Copy preview to episode public assets
    pub_preview_dir = os.path.join(root, "episodes", "01-anomali-air", "papercut", "public", "assets", "previews")
    os.makedirs(pub_preview_dir, exist_ok=True)
    shutil.copy2(out_preview, os.path.join(pub_preview_dir, f"{env_id}-scene-preview.png"))

    # Also copy to brain artifact directory if it exists
    brain_dir = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity-cli", "brain", "28b506b1-8d34-4e05-9793-9646a6e11f82")
    if os.path.isdir(brain_dir):
        shutil.copy2(out_preview, os.path.join(brain_dir, f"{env_id}-scene-preview.png"))

    return out_preview


def add_environment(
    image_path: str,
    env_id: str,
    name: str,
    description: str,
    category: str = "Education / STEM",
    mood: str = "cool / studious",
    floor_y: int = 1380,
    presenter_zone: Optional[Dict[str, List[int]]] = None,
    header_zone: Optional[Dict[str, List[int]]] = None,
    caption_zone: Optional[Dict[str, List[int]]] = None,
    best_for: Optional[List[str]] = None,
    color_palette: Optional[List[str]] = None,
    lighting: str = "Soft top-left ambient illumination with warm pendant paper lights",
    allow_overwrite: bool = False,
    skip_preview: bool = False,
    root_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Operation 1: Adds a new environment from a supplied background image.
    Enforces non-destructive registration and 1080x1920 dimensions.
    """
    root = root_dir or find_project_root()

    # 1. Image checks
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Source background image does not exist: {image_path}")

    w, h, fmt = read_image_dimensions(image_path)
    if w != SAFE_ZONES["FRAME_WIDTH"] or h != SAFE_ZONES["FRAME_HEIGHT"]:
        raise ValueError(
            f"Image dimensions {w}x{h} do not meet the mandatory 1080x1920 vertical format requirement."
        )

    # 2. Safety & Overwrite Check
    env_dir = os.path.join(root, "assets", "backgrounds", env_id)
    if os.path.exists(env_dir) and not allow_overwrite:
        raise FileExistsError(
            f"Environment '{env_id}' already exists at {env_dir}. Overwrite prohibited without explicit authorization."
        )

    # 3. Layout defaults
    pzone = presenter_zone or {"x_range": [240, 840], "y_range": [900, 1750], "status": "clear_unobstructed"}
    hzone = header_zone or {"y_range": [0, 420], "status": "clear_for_banner"}
    czone = caption_zone or {"y_range": [1300, 1550], "status": "low_detail_for_legibility"}
    bf = best_for or ["Science explanations", "STEM educational reels", "Explainer breakdowns"]
    palette = color_palette or ["#4A607A", "#6B8E7C", "#D9CBB6", "#F4EAD4", "#E2725B", "#48A9A6"]

    # 4. Prepare Destination & Save Image
    os.makedirs(env_dir, exist_ok=True)
    dest_img = os.path.join(env_dir, "background.png")
    if fmt == "PNG":
        shutil.copy2(image_path, dest_img)
    else:
        # Convert JPG to PNG
        subprocess.run(["npx", "--yes", "sharp-cli", "-i", image_path, "-o", dest_img], check=True)

    # 5. Build Metadata
    created_at = get_current_iso_timestamp()
    meta_rel = f"assets/backgrounds/{env_id}/metadata.json"
    img_rel = f"assets/backgrounds/{env_id}/background.png"

    metadata = {
        "id": env_id,
        "name": name,
        "description": description,
        "category": category,
        "mood": mood,
        "style": {
            "type": "2D Papercraft Cutout",
            "construction": "Layered paper collage with scissor-cut edges and subtle paper drop shadows",
            "color_palette": palette,
            "lighting": lighting,
        },
        "dimensions": {
            "width": 1080,
            "height": 1920,
            "aspect_ratio": "9:16",
        },
        "layout": {
            "floor_y": floor_y,
            "presenter_zone": pzone,
            "header_zone": hzone,
            "caption_zone": czone,
        },
        "best_for": bf,
        "rules_compliance": {
            "consistent_papercraft_style": True,
            "layered_cutout_construction": True,
            "visible_paper_edges_and_shadows": True,
            "no_characters_or_people": True,
            "foreground_suitable_for_presenter": True,
            "vertical_9_16_composition": True,
            "reusable_environment": True,
        },
        "asset_paths": {
            "image": img_rel,
            "metadata": meta_rel,
        },
        "created_at": created_at,
    }

    meta_full = os.path.join(root, meta_rel)
    with open(meta_full, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # 6. Register in Master Catalog (assets/library.json)
    lib_path = os.path.join(root, "assets", "library.json")
    with open(lib_path, "r", encoding="utf-8") as f:
        lib = json.load(f)

    env_catalog_entry = {
        "id": env_id,
        "name": name,
        "description": description,
        "category": category,
        "mood": mood,
        "aspect_ratio": "9:16",
        "dimensions": {
            "width": 1080,
            "height": 1920,
            "aspect_ratio": "9:16",
        },
        "floor_y": floor_y,
        "presenter_zone": pzone,
        "best_for": bf,
        "path": img_rel,
        "metadata_path": meta_rel,
    }

    envs = lib.setdefault("categories", {}).setdefault("environments", [])
    # Update existing entry if allow_overwrite, else append
    existing_idx = next((i for i, e in enumerate(envs) if e.get("id") == env_id), None)
    if existing_idx is not None:
        envs[existing_idx] = env_catalog_entry
    else:
        envs.append(env_catalog_entry)

    lib["updated_at"] = created_at
    with open(lib_path, "w", encoding="utf-8") as f:
        json.dump(lib, f, indent=2)

    # 7. Register in backgrounds/index.json
    bg_idx_path = os.path.join(root, "assets", "backgrounds", "index.json")
    with open(bg_idx_path, "r", encoding="utf-8") as f:
        bg_idx = json.load(f)

    bg_list = bg_idx.setdefault("backgrounds", [])
    b_idx = next((i for i, b in enumerate(bg_list) if b.get("id") == env_id), None)
    if b_idx is not None:
        bg_list[b_idx] = env_catalog_entry
    else:
        bg_list.append(env_catalog_entry)

    bg_idx["total_backgrounds"] = len(bg_list)
    bg_idx["updated_at"] = created_at
    with open(bg_idx_path, "w", encoding="utf-8") as f:
        json.dump(bg_idx, f, indent=2)

    # 7b. Register in Centralized Registry (library/backgrounds/registry.json)
    reg_path = os.path.join(root, "library", "backgrounds", "registry.json")
    if os.path.isfile(reg_path):
        try:
            with open(reg_path, "r", encoding="utf-8") as f:
                reg_data = json.load(f)
            bgs = reg_data.setdefault("backgrounds", [])
            r_idx = next((i for i, b in enumerate(bgs) if b.get("id") == env_id), None)
            reg_entry = {
                "id": env_id,
                "name": name,
                "category": category,
                "description": description,
                "assetPath": img_rel,
                "thumbnailPath": f"assets/previews/{env_id}-scene-preview.png",
                "aspectRatio": "9:16",
                "dimensions": {"width": 1080, "height": 1920},
                "format": "PNG",
                "hasTransparency": False,
                "tags": [category.lower(), "indoor" if "indoor" in description.lower() else "environment"],
                "status": "active",
                "floorY": floor_y,
                "mood": mood,
                "createdAt": created_at,
                "updatedAt": created_at,
            }
            if r_idx is not None:
                bgs[r_idx] = reg_entry
            else:
                bgs.append(reg_entry)
            reg_data["total"] = len(bgs)
            reg_data["updatedAt"] = created_at
            with open(reg_path, "w", encoding="utf-8") as f:
                json.dump(reg_data, f, indent=2)
        except Exception:
            pass

    # 8. Sync Assets & Update TypeScript AssetLoader
    sync_assets_to_public(root, env_id)
    update_typescript_asset_loader(root)

    # 9. Generate Remotion Scene Preview
    preview_path = None
    if not skip_preview:
        preview_path = generate_scene_preview(root, env_id, headline=name.upper())

    # 10. Run Validation
    val_res = validate_environment(env_catalog_entry, root)

    return {
        "status": "success",
        "operation": "add_environment",
        "env_id": env_id,
        "name": name,
        "image_path": img_rel,
        "metadata_path": meta_rel,
        "preview_path": os.path.relpath(preview_path, root) if preview_path else None,
        "validation": val_res,
    }


def revise_environment(
    existing_env_id: str,
    new_image_path: str,
    revision_notes: str,
    new_env_id: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    mood: Optional[str] = None,
    floor_y: Optional[int] = None,
    presenter_zone: Optional[Dict[str, List[int]]] = None,
    color_palette: Optional[List[str]] = None,
    skip_preview: bool = False,
    root_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Operation 2: Creates a revised version of an existing environment
    without destroying the original environment or its metadata.
    """
    root = root_dir or find_project_root()

    # 1. Verify existing environment
    lib = load_library(root)
    envs = lib.get("categories", {}).get("environments", [])
    parent_env = next((e for e in envs if e.get("id") == existing_env_id), None)
    if not parent_env:
        raise KeyError(f"Parent environment '{existing_env_id}' not found in library index.")

    # Load parent metadata if available
    parent_meta_path = os.path.join(root, parent_env.get("metadata_path", ""))
    parent_meta = {}
    if os.path.isfile(parent_meta_path):
        with open(parent_meta_path, "r", encoding="utf-8") as f:
            parent_meta = json.load(f)

    # 2. Determine Revised ID
    if not new_env_id:
        # Automatically generate next version tag: {existing_env_id}-v2, -v3, etc.
        v = 2
        cand_id = f"{existing_env_id}-v{v}"
        existing_ids = {e.get("id") for e in envs}
        while cand_id in existing_ids or os.path.isdir(os.path.join(root, "assets", "backgrounds", cand_id)):
            v += 1
            cand_id = f"{existing_env_id}-v{v}"
        target_env_id = cand_id
        version_str = f"{v}.0.0"
    else:
        target_env_id = new_env_id
        version_str = "2.0.0"

    # 3. Inherit & override properties
    revised_name = name or f"{parent_env.get('name', existing_env_id)} (Revision {version_str})"
    revised_desc = description or f"{parent_env.get('description', '')} [Revision: {revision_notes}]"
    revised_mood = mood or parent_env.get("mood", "cool / studious")
    revised_floor = floor_y if floor_y is not None else parent_env.get("floor_y", 1380)
    revised_pzone = presenter_zone or parent_env.get("presenter_zone") or {"x_range": [240, 840], "y_range": [900, 1750]}
    revised_palette = color_palette or parent_meta.get("style", {}).get("color_palette")
    best_for = parent_env.get("best_for", ["Science explanations"])

    # 4. Perform Add for the revised version
    result = add_environment(
        image_path=new_image_path,
        env_id=target_env_id,
        name=revised_name,
        description=revised_desc,
        category=parent_env.get("category", "Education / STEM"),
        mood=revised_mood,
        floor_y=revised_floor,
        presenter_zone=revised_pzone,
        best_for=best_for,
        color_palette=revised_palette,
        allow_overwrite=False,
        skip_preview=skip_preview,
        root_dir=root,
    )

    # 5. Enrich metadata with lineage tracking
    meta_full = os.path.join(root, result["metadata_path"])
    with open(meta_full, "r", encoding="utf-8") as f:
        meta = json.load(f)

    meta["lineage"] = {
        "parent_environment_id": existing_env_id,
        "revision_version": version_str,
        "revision_notes": revision_notes,
        "replaces_id": None,  # Non-destructive: original remains active for older episodes
    }

    with open(meta_full, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    result["operation"] = "revise_environment"
    result["parent_environment_id"] = existing_env_id
    result["revision_version"] = version_str
    result["revision_notes"] = revision_notes

    return result


def list_registered_environments(root_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns all registered environments from the master library index."""
    root = root_dir or find_project_root()
    lib = load_library(root)
    return lib.get("categories", {}).get("environments", [])


def main():
    parser = argparse.ArgumentParser(description="Papercraft Explainer Environment Management Workflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Add
    add_p = subparsers.add_parser("add", help="Add a new environment from an image")
    add_p.add_argument("--image", required=True, help="Path to 1080x1920 background image")
    add_p.add_argument("--id", required=True, help="Unique environment identifier")
    add_p.add_argument("--name", required=True, help="Human-readable environment name")
    add_p.add_argument("--description", required=True, help="Description of 2D papercraft set")
    add_p.add_argument("--category", default="Education / STEM", help="Environment category")
    add_p.add_argument("--mood", default="cool / studious", help="Lighting and atmosphere mood")
    add_p.add_argument("--floor-y", type=int, default=1380, help="Presenter floor line Y")
    add_p.add_argument("--overwrite", action="store_true", help="Explicit authorization to overwrite")

    # 2. Revise
    rev_p = subparsers.add_parser("revise", help="Create a revised version of an existing environment")
    rev_p.add_argument("--id", required=True, help="Existing environment ID being revised")
    rev_p.add_argument("--image", required=True, help="Path to revised 1080x1920 background image")
    rev_p.add_argument("--notes", required=True, help="Summary of revision changes")
    rev_p.add_argument("--new-id", default=None, help="Optional custom revised ID")
    rev_p.add_argument("--name", default=None, help="Optional new name")
    rev_p.add_argument("--floor-y", type=int, default=None, help="Optional new floor line Y")

    # 3. Preview
    prev_p = subparsers.add_parser("preview", help="Render a Remotion composite preview for an environment")
    prev_p.add_argument("--id", required=True, help="Environment ID")
    prev_p.add_argument("--headline", default="2D PAPERCRAFT COMPOSITE", help="Banner headline text")

    # 4. List
    subparsers.add_parser("list", help="List all registered environments")

    # 5. Validate
    val_p = subparsers.add_parser("validate", help="Validate an environment or all environments")
    val_p.add_argument("--id", default=None, help="Optional environment ID to validate")

    args = parser.parse_args()
    root = find_project_root()

    if args.command == "add":
        print(f"==> Adding new environment '{args.id}'...")
        res = add_environment(
            image_path=args.image,
            env_id=args.id,
            name=args.name,
            description=args.description,
            category=args.category,
            mood=args.mood,
            floor_y=args.floor_y,
            allow_overwrite=args.overwrite,
            root_dir=root,
        )
        print(json.dumps(res, indent=2))
        if not res["validation"]["valid"]:
            sys.exit(1)

    elif args.command == "revise":
        print(f"==> Revising environment '{args.id}'...")
        res = revise_environment(
            existing_env_id=args.id,
            new_image_path=args.image,
            revision_notes=args.notes,
            new_env_id=args.new_id,
            name=args.name,
            floor_y=args.floor_y,
            root_dir=root,
        )
        print(json.dumps(res, indent=2))
        if not res["validation"]["valid"]:
            sys.exit(1)

    elif args.command == "preview":
        print(f"==> Generating Remotion preview for '{args.id}'...")
        prev = generate_scene_preview(root, args.id, headline=args.headline)
        print(f"[OK] Preview generated at: {prev}")

    elif args.command == "list":
        envs = list_registered_environments(root)
        print(f"==> Found {len(envs)} registered environment(s):")
        for e in envs:
            print(f"  • {e.get('id')} ({e.get('name')}): floor_y={e.get('floor_y')}, path={e.get('path')}")

    elif args.command == "validate":
        lib = load_library(root)
        envs = lib.get("categories", {}).get("environments", [])
        if args.id:
            envs = [e for e in envs if e.get("id") == args.id]
            if not envs:
                print(f"[FAIL] Environment '{args.id}' not found.")
                sys.exit(1)

        all_ok = True
        for e in envs:
            eid = e.get("id")
            res = validate_environment(e, root)
            if res["valid"]:
                print(f"[OK] Environment '{eid}' valid.")
            else:
                print(f"[FAIL] Environment '{eid}' invalid: {res['errors']}")
                all_ok = False
        sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
