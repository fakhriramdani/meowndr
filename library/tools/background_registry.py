#!/usr/bin/env python3
"""
Centralized Background Registry Engine for @meowndr 2D Papercraft Explainer.

Single source of truth for all background/environment assets across the repository.
Handles:
1. Centralized registry storage at library/backgrounds/registry.json (and assets/backgrounds/registry.json).
2. Dynamic listing with filtering by category, status, and tag.
3. Safe dynamic addition of backgrounds (validates 1080x1920 vertical format, unique ID, generates preview).
4. Safe removal and lifecycle management (disable, archive, remove with episode reference protection).
5. Automatic discovery of unregistered assets, missing files, and duplicate IDs.
6. Comprehensive validation suite for backgrounds and episode references.
7. Downstream synchronization to assets/library.json, assets/backgrounds/index.json,
   AssetLoader.ts, and Remotion public assets.
"""

import os
import sys
import json
import shutil
import struct
import datetime
import subprocess
from typing import Any, Dict, List, Optional, Tuple, Set

# Safe Zones and Resolutions
FRAME_WIDTH = 1080
FRAME_HEIGHT = 1920
VALID_STATUSES = {"active", "disabled", "archived"}
SUPPORTED_FORMATS = {"PNG", "JPEG", "JPG", "WEBP", "SVG"}


def find_repo_root(start_dir: Optional[str] = None) -> str:
    """Finds repository root containing library/ or assets/."""
    curr = os.path.abspath(start_dir or os.getcwd())
    for _ in range(6):
        if os.path.exists(os.path.join(curr, "library", "backgrounds")) or (
            os.path.exists(os.path.join(curr, "assets", "library.json"))
            and os.path.exists(os.path.join(curr, "episodes"))
        ):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return os.path.abspath(start_dir or os.getcwd())


def get_current_iso_timestamp() -> str:
    """Returns ISO 8601 timestamp in Asia/Jakarta (+07:00)."""
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    return now.isoformat(timespec="seconds")


def read_image_dimensions(image_path: str) -> Tuple[int, int, str]:
    """
    Reads image dimensions directly from binary headers without external dependencies.
    Supports PNG, JPEG, SVG, WebP.
    Returns (width, height, format).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file does not exist: {image_path}")

    # Check SVG by extension or header
    if image_path.lower().endswith(".svg"):
        try:
            with open(image_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(2048)
                # Parse viewBox="0 0 1080 1920" or width="1080" height="1920"
                import re
                vb = re.search(r'viewBox=["\']\s*0\s+0\s+(\d+)\s+(\d+)\s*["\']', content)
                if vb:
                    return int(vb.group(1)), int(vb.group(2)), "SVG"
                w_m = re.search(r'width=["\'](\d+)(?:px)?["\']', content)
                h_m = re.search(r'height=["\'](\d+)(?:px)?["\']', content)
                if w_m and h_m:
                    return int(w_m.group(1)), int(h_m.group(1)), "SVG"
        except Exception:
            pass
        return FRAME_WIDTH, FRAME_HEIGHT, "SVG"

    with open(image_path, "rb") as f:
        head = f.read(64)

        # PNG: 8-byte signature, followed by IHDR chunk
        if head.startswith(b"\x89PNG\r\n\x1a\n"):
            width, height = struct.unpack(">II", head[16:24])
            return width, height, "PNG"

        # JPEG: \xFF\xD8
        if head.startswith(b"\xff\xd8"):
            f.seek(2)
            while True:
                marker_data = f.read(2)
                if len(marker_data) < 2:
                    break
                marker = struct.unpack(">H", marker_data)[0]
                if marker in [
                    0xFFC0, 0xFFC1, 0xFFC2, 0xFFC3,
                    0xFFC5, 0xFFC6, 0xFFC7, 0xFFC9,
                    0xFFCA, 0xFFCB, 0xFFCD, 0xFFCE, 0xFFCF
                ]:
                    f.read(3)  # length (2) + precision (1)
                    height, width = struct.unpack(">HH", f.read(4))
                    return width, height, "JPEG"
                elif marker in [0xFFD9, 0xFFDA]:
                    break
                else:
                    length = struct.unpack(">H", f.read(2))[0]
                    f.seek(length - 2, os.SEEK_CUR)

        # WebP: RIFF ... WEBP
        if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
            chunk_header = head[12:16]
            if chunk_header == b"VP8 ":
                # Lossy VP8
                width = struct.unpack("<H", head[26:28])[0] & 0x3FFF
                height = struct.unpack("<H", head[28:30])[0] & 0x3FFF
                return width, height, "WEBP"
            elif chunk_header == b"VP8L":
                # Lossless VP8L
                b0, b1, b2, b3 = struct.unpack("BBBB", head[21:25])
                width = 1 + (((b1 & 0x3F) << 8) | b0)
                height = 1 + (((b3 & 0xF) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
                return width, height, "WEBP"
            elif chunk_header == b"VP8X":
                # Extended VP8X
                width = 1 + (head[24] | (head[25] << 8) | (head[26] << 16))
                height = 1 + (head[27] | (head[28] << 8) | (head[29] << 16))
                return width, height, "WEBP"

    raise ValueError(f"Unsupported or unrecognized image header in {image_path}")


class BackgroundRegistry:
    """
    Centralized, dynamic background management system for @meowndr content factory.
    """

    def __init__(self, registry_path: Optional[str] = None, repo_root: Optional[str] = None):
        self.root = os.path.abspath(repo_root or find_repo_root())
        self.registry_path = registry_path or os.path.join(self.root, "library", "backgrounds", "registry.json")
        self.data: Dict[str, Any] = {"version": "1.0.0", "updatedAt": "", "total": 0, "backgrounds": []}
        self.load()

    def load(self) -> Dict[str, Any]:
        """Loads registry data from disk."""
        if os.path.isfile(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"[WARN] Failed to parse registry at {self.registry_path}: {e}", file=sys.stderr)
        elif os.path.isfile(os.path.join(self.root, "assets", "backgrounds", "registry.json")):
            with open(os.path.join(self.root, "assets", "backgrounds", "registry.json"), "r", encoding="utf-8") as f:
                self.data = json.load(f)
        return self.data

    def save(self):
        """Saves registry data to disk and synchronizes the symlink or mirror."""
        self.data["total"] = len(self.data.get("backgrounds", []))
        self.data["updatedAt"] = get_current_iso_timestamp()

        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

        # Mirror or symlink to assets/backgrounds/registry.json
        asset_reg = os.path.join(self.root, "assets", "backgrounds", "registry.json")
        os.makedirs(os.path.dirname(asset_reg), exist_ok=True)
        shutil.copy2(self.registry_path, asset_reg)

    def list_backgrounds(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        query: Optional[str] = None,
        tag: Optional[str] = None,
        check_exists: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Lists backgrounds matching filters.
        """
        results = []
        bgs = self.data.get("backgrounds", [])

        for bg in bgs:
            # Status filter
            if status and bg.get("status", "active").lower() != status.lower():
                continue

            # Category filter
            if category and category.lower() not in bg.get("category", "").lower():
                continue

            # Tag filter
            if tag:
                bg_tags = [t.lower() for t in bg.get("tags", [])]
                if tag.lower() not in bg_tags:
                    continue

            # Text query
            if query:
                q = query.lower()
                id_match = q in bg.get("id", "").lower()
                name_match = q in bg.get("name", "").lower()
                desc_match = q in bg.get("description", "").lower()
                tag_match = any(q in t.lower() for t in bg.get("tags", []))
                if not (id_match or name_match or desc_match or tag_match):
                    continue

            item = dict(bg)
            if check_exists:
                asset_rel = bg.get("assetPath", "")
                full_path = os.path.join(self.root, asset_rel) if not os.path.isabs(asset_rel) else asset_rel
                item["exists_on_disk"] = os.path.isfile(full_path)
            results.append(item)

        return results

    def get_background(self, bg_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves background entry by ID."""
        for bg in self.data.get("backgrounds", []):
            if bg.get("id") == bg_id:
                return dict(bg)
        return None

    def find_active_references(self, bg_id: Optional[str] = None) -> Dict[str, List[Dict[str, str]]]:
        """
        Searches all episode configs and source files for references to background IDs.
        Returns: { bg_id: [ {"episode": ep_slug, "file": rel_path, "context": str} ] }
        """
        refs: Dict[str, List[Dict[str, str]]] = {}
        episodes_dir = os.path.join(self.root, "episodes")
        if not os.path.isdir(episodes_dir):
            return refs

        for ep_slug in sorted(os.listdir(episodes_dir)):
            ep_dir = os.path.join(episodes_dir, ep_slug)
            if not os.path.isdir(ep_dir):
                continue

            # 1. Check episode.json files
            for ep_cfg in [
                os.path.join(ep_dir, "episode.json"),
                os.path.join(ep_dir, "papercut", "episode.json"),
            ]:
                if os.path.isfile(ep_cfg):
                    try:
                        with open(ep_cfg, "r", encoding="utf-8") as f:
                            cfg = json.load(f)
                        rel_f = os.path.relpath(ep_cfg, self.root)
                        env = cfg.get("environment")
                        eid = env.get("id") if isinstance(env, dict) else env
                        if eid and isinstance(eid, str):
                            refs.setdefault(eid, []).append({
                                "episode": ep_slug,
                                "file": rel_f,
                                "context": "episode.json -> environment"
                            })
                        for idx, sc in enumerate(cfg.get("scenes", [])):
                            if isinstance(sc, dict):
                                s_eid = sc.get("environment_id") or sc.get("environment")
                                if s_eid and isinstance(s_eid, str):
                                    refs.setdefault(s_eid, []).append({
                                        "episode": ep_slug,
                                        "file": rel_f,
                                        "context": f"episode.json -> scenes[{idx}]"
                                    })
                    except Exception:
                        pass

            # 2. Check storyboard.json files
            for sb_path in [
                os.path.join(ep_dir, "storyboard", "storyboard.json"),
                os.path.join(ep_dir, "content_factory", "storyboard.json"),
            ]:
                if os.path.isfile(sb_path):
                    try:
                        with open(sb_path, "r", encoding="utf-8") as f:
                            sb = json.load(f)
                        rel_f = os.path.relpath(sb_path, self.root)
                        top_eid = sb.get("environment_id") or sb.get("environment")
                        if isinstance(top_eid, dict):
                            top_eid = top_eid.get("id")
                        if top_eid and isinstance(top_eid, str):
                            refs.setdefault(top_eid, []).append({
                                "episode": ep_slug,
                                "file": rel_f,
                                "context": "storyboard.json -> environment_id"
                            })
                        for idx, sc in enumerate(sb.get("scenes", [])):
                            if isinstance(sc, dict):
                                s_eid = sc.get("environment_id") or sc.get("environment")
                                if s_eid and isinstance(s_eid, str):
                                    refs.setdefault(s_eid, []).append({
                                        "episode": ep_slug,
                                        "file": rel_f,
                                        "context": f"storyboard.json -> scenes[{idx}]"
                                    })
                    except Exception:
                        pass

            # 3. Check asset_plan.json
            ap_path = os.path.join(ep_dir, "assets", "asset_plan.json")
            if os.path.isfile(ap_path):
                try:
                    with open(ap_path, "r", encoding="utf-8") as f:
                        ap = json.load(f)
                    rel_f = os.path.relpath(ap_path, self.root)
                    e = ap.get("environment")
                    if isinstance(e, dict) and e.get("id"):
                        refs.setdefault(e["id"], []).append({
                            "episode": ep_slug,
                            "file": rel_f,
                            "context": "asset_plan.json -> environment.id"
                        })
                    elif isinstance(e, str):
                        refs.setdefault(e, []).append({
                            "episode": ep_slug,
                            "file": rel_f,
                            "context": "asset_plan.json -> environment"
                        })
                    for idx, env_item in enumerate(ap.get("environments", [])):
                        eid = env_item.get("id") if isinstance(env_item, dict) else env_item
                        if eid and isinstance(eid, str):
                            refs.setdefault(eid, []).append({
                                "episode": ep_slug,
                                "file": rel_f,
                                "context": f"asset_plan.json -> environments[{idx}]"
                            })
                except Exception:
                    pass

        if bg_id:
            return {bg_id: refs.get(bg_id, [])}
        return refs

    def add_background(
        self,
        image_path: str,
        bg_id: str,
        name: str,
        category: str = "Education / STEM",
        description: str = "",
        tags: Optional[List[str]] = None,
        status: str = "active",
        floor_y: int = 1380,
        mood: str = "cool / studious",
        has_transparency: bool = False,
        allow_overwrite: bool = False,
        skip_preview: bool = False,
        skip_sync: bool = False,
    ) -> Dict[str, Any]:
        """
        Registers a new background environment.
        Enforces 1080x1920 vertical format and updates downstream assets.
        """
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Source background image does not exist: {image_path}")

        # ID Format Validation
        clean_id = bg_id.strip().lower()
        if not clean_id or not all(c.isalnum() or c in "-_" for c in clean_id):
            raise ValueError(f"Invalid background ID '{bg_id}'. Must be kebab-case alphanumeric.")

        # Dimension and format validation
        w, h, fmt = read_image_dimensions(image_path)
        if w != FRAME_WIDTH or h != FRAME_HEIGHT:
            raise ValueError(
                f"Image dimensions {w}x{h} do not meet mandatory {FRAME_WIDTH}x{FRAME_HEIGHT} vertical requirement."
            )

        if fmt not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format '{fmt}'. Must be one of {SUPPORTED_FORMATS}.")

        # Overwrite Check
        existing = self.get_background(clean_id)
        if existing and not allow_overwrite:
            raise FileExistsError(
                f"Background ID '{clean_id}' is already registered in registry.json. Use allow_overwrite=True to replace."
            )

        # Destination paths
        env_dir = os.path.join(self.root, "assets", "backgrounds", clean_id)
        os.makedirs(env_dir, exist_ok=True)
        dest_img_path = os.path.join(env_dir, "background.png")

        # Copy or convert image
        if fmt == "PNG":
            shutil.copy2(image_path, dest_img_path)
        else:
            try:
                subprocess.run(
                    ["npx", "--yes", "sharp-cli", "-i", image_path, "-o", dest_img_path],
                    check=True,
                    capture_output=True,
                )
            except Exception:
                shutil.copy2(image_path, dest_img_path)

        created_at = existing.get("createdAt") if existing else get_current_iso_timestamp()
        asset_rel = f"assets/backgrounds/{clean_id}/background.png"
        meta_rel = f"assets/backgrounds/{clean_id}/metadata.json"
        thumb_rel = f"assets/previews/{clean_id}-scene-preview.png"

        # Write metadata.json for the background
        metadata = {
            "id": clean_id,
            "name": name,
            "description": description,
            "category": category,
            "mood": mood,
            "style": {
                "type": "2D Papercraft Cutout",
                "construction": "Layered paper collage with scissor-cut edges and subtle paper drop shadows",
                "color_palette": ["#4A607A", "#6B8E7C", "#D9CBB6", "#F4EAD4", "#E2725B", "#48A9A6"],
                "lighting": "Soft top-left ambient illumination with warm pendant paper lights",
            },
            "dimensions": {
                "width": FRAME_WIDTH,
                "height": FRAME_HEIGHT,
                "aspect_ratio": "9:16",
            },
            "layout": {
                "floor_y": floor_y,
                "presenter_zone": {"x_range": [240, 840], "y_range": [900, 1750], "status": "clear_unobstructed"},
                "header_zone": {"y_range": [0, 420], "status": "clear_for_banner"},
                "caption_zone": {"y_range": [1300, 1550], "status": "low_detail_for_legibility"},
            },
            "best_for": [category, "Educational explainer reel"],
            "asset_paths": {
                "image": asset_rel,
                "metadata": meta_rel,
            },
            "created_at": created_at,
        }
        with open(os.path.join(self.root, meta_rel), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        # Generate Preview Thumbnail
        preview_generated = False
        thumb_full = os.path.join(self.root, thumb_rel)
        if not skip_preview:
            try:
                os.makedirs(os.path.dirname(thumb_full), exist_ok=True)
                # Attempt Remotion still or SVG overlay fallback
                from manage_environment import generate_scene_preview
                generate_scene_preview(self.root, clean_id, headline=name.upper())
                preview_generated = os.path.isfile(thumb_full)
            except Exception:
                pass

        if not os.path.isfile(thumb_full):
            thumb_rel = None

        bg_entry = {
            "id": clean_id,
            "name": name,
            "category": category,
            "description": description,
            "assetPath": asset_rel,
            "thumbnailPath": thumb_rel,
            "aspectRatio": "9:16",
            "dimensions": {"width": FRAME_WIDTH, "height": FRAME_HEIGHT},
            "format": "PNG",
            "hasTransparency": has_transparency,
            "tags": tags or [category.lower(), "indoor" if "indoor" in description.lower() else "environment"],
            "status": status if status in VALID_STATUSES else "active",
            "floorY": floor_y,
            "mood": mood,
            "createdAt": created_at,
            "updatedAt": get_current_iso_timestamp(),
        }

        # Update in registry data
        bgs = self.data.setdefault("backgrounds", [])
        idx = next((i for i, b in enumerate(bgs) if b.get("id") == clean_id), None)
        if idx is not None:
            bgs[idx] = bg_entry
        else:
            bgs.append(bg_entry)

        self.save()

        if not skip_sync:
            self.sync_downstream()

        return {
            "status": "success",
            "id": clean_id,
            "entry": bg_entry,
            "preview_generated": preview_generated,
        }

    def disable_background(self, bg_id: str, reason: Optional[str] = None, skip_sync: bool = False) -> Dict[str, Any]:
        """Safely marks a background as disabled without removing it."""
        bgs = self.data.get("backgrounds", [])
        entry = next((b for b in bgs if b.get("id") == bg_id), None)
        if not entry:
            raise KeyError(f"Background ID '{bg_id}' not found in registry.")

        entry["status"] = "disabled"
        entry["statusReason"] = reason or "Disabled by user"
        entry["updatedAt"] = get_current_iso_timestamp()

        self.save()
        if not skip_sync:
            self.sync_downstream()

        return {"status": "success", "id": bg_id, "new_status": "disabled", "reason": reason}

    def archive_background(self, bg_id: str, reason: Optional[str] = None, skip_sync: bool = False) -> Dict[str, Any]:
        """Marks a background as archived."""
        bgs = self.data.get("backgrounds", [])
        entry = next((b for b in bgs if b.get("id") == bg_id), None)
        if not entry:
            raise KeyError(f"Background ID '{bg_id}' not found in registry.")

        entry["status"] = "archived"
        entry["statusReason"] = reason or "Archived by user"
        entry["updatedAt"] = get_current_iso_timestamp()

        self.save()
        if not skip_sync:
            self.sync_downstream()

        return {"status": "success", "id": bg_id, "new_status": "archived", "reason": reason}

    def enable_background(self, bg_id: str, skip_sync: bool = False) -> Dict[str, Any]:
        """Re-enables a disabled or archived background."""
        bgs = self.data.get("backgrounds", [])
        entry = next((b for b in bgs if b.get("id") == bg_id), None)
        if not entry:
            raise KeyError(f"Background ID '{bg_id}' not found in registry.")

        entry["status"] = "active"
        entry.pop("statusReason", None)
        entry["updatedAt"] = get_current_iso_timestamp()

        self.save()
        if not skip_sync:
            self.sync_downstream()

        return {"status": "success", "id": bg_id, "new_status": "active"}

    def remove_background(
        self,
        bg_id: str,
        force: bool = False,
        delete_asset: bool = False,
        skip_sync: bool = False,
    ) -> Dict[str, Any]:
        """
        Safely removes a background from the registry.
        Checks for active episode references before proceeding.
        Never deletes image files on disk unless delete_asset=True.
        """
        bgs = self.data.get("backgrounds", [])
        entry = next((b for b in bgs if b.get("id") == bg_id), None)
        if not entry:
            raise KeyError(f"Background ID '{bg_id}' not found in registry.")

        # Check references
        refs = self.find_active_references(bg_id).get(bg_id, [])
        if refs and not force:
            ep_names = sorted(list({r["episode"] for r in refs}))
            raise ValueError(
                f"Cannot remove background '{bg_id}'! It is currently referenced in {len(refs)} location(s) "
                f"across episode(s): {', '.join(ep_names)}. "
                f"Consider using 'disable {bg_id}' or 'archive {bg_id}', or pass force=True."
            )

        # Remove from backgrounds list
        self.data["backgrounds"] = [b for b in bgs if b.get("id") != bg_id]
        self.save()

        # Delete physical asset only if explicitly requested
        deleted_disk = False
        if delete_asset:
            asset_dir = os.path.join(self.root, "assets", "backgrounds", bg_id)
            if os.path.isdir(asset_dir):
                shutil.rmtree(asset_dir)
                deleted_disk = True
            thumb_path = os.path.join(self.root, "assets", "previews", f"{bg_id}-scene-preview.png")
            if os.path.isfile(thumb_path):
                os.remove(thumb_path)

        if not skip_sync:
            self.sync_downstream()

        return {
            "status": "success",
            "id": bg_id,
            "removed_from_registry": True,
            "deleted_asset_files": deleted_disk,
            "warn_references": refs if force else [],
        }

    def discover_backgrounds(self, scan_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scans disk to identify unregistered assets, missing asset files, and duplicate IDs.
        """
        dirs_to_scan = scan_dirs or [os.path.join(self.root, "assets", "backgrounds")]
        registered_ids = {b.get("id"): b for b in self.data.get("backgrounds", [])}
        registered_paths = {b.get("assetPath") for b in self.data.get("backgrounds", [])}

        unregistered = []
        for sdir in dirs_to_scan:
            if not os.path.isdir(sdir):
                continue
            for item in sorted(os.listdir(sdir)):
                sub = os.path.join(sdir, item)
                if not os.path.isdir(sub):
                    continue

                bg_file = os.path.join(sub, "background.png")
                rel_path = os.path.relpath(bg_file, self.root)

                if os.path.isfile(bg_file) and item not in registered_ids and rel_path not in registered_paths:
                    w, h, fmt = read_image_dimensions(bg_file)
                    unregistered.append({
                        "id": item,
                        "diskPath": rel_path,
                        "dimensions": {"width": w, "height": h},
                        "format": fmt,
                        "isCompliant": (w == FRAME_WIDTH and h == FRAME_HEIGHT),
                    })

        # Check missing on disk
        missing_on_disk = []
        for bg in self.data.get("backgrounds", []):
            rel = bg.get("assetPath", "")
            full = os.path.join(self.root, rel) if not os.path.isabs(rel) else rel
            if not os.path.isfile(full):
                missing_on_disk.append({
                    "id": bg.get("id"),
                    "name": bg.get("name"),
                    "expectedPath": rel,
                    "status": bg.get("status"),
                })

        # Check duplicate IDs in registry
        seen_ids = set()
        duplicates = []
        for bg in self.data.get("backgrounds", []):
            bid = bg.get("id")
            if bid in seen_ids:
                duplicates.append(bid)
            seen_ids.add(bid)

        return {
            "total_registered": len(self.data.get("backgrounds", [])),
            "unregistered": unregistered,
            "missing_on_disk": missing_on_disk,
            "duplicate_ids": duplicates,
        }

    def validate_registry(self, check_episodes: bool = True) -> Dict[str, Any]:
        """
        Validates the background registry and cross-checks episode references.
        """
        errors = []
        warnings = []
        bgs = self.data.get("backgrounds", [])
        seen_ids = set()

        for idx, bg in enumerate(bgs):
            bg_id = bg.get("id")
            if not bg_id:
                errors.append(f"Entry #{idx} is missing mandatory 'id'.")
                continue

            if bg_id in seen_ids:
                errors.append(f"Duplicate background ID detected: '{bg_id}'.")
            seen_ids.add(bg_id)

            # Check status
            st = bg.get("status", "active")
            if st not in VALID_STATUSES:
                errors.append(f"Background '{bg_id}' has invalid status '{st}'. Allowed: {VALID_STATUSES}.")

            # Check asset file
            asset_rel = bg.get("assetPath")
            if not asset_rel:
                errors.append(f"Background '{bg_id}' is missing 'assetPath'.")
            else:
                full_path = os.path.join(self.root, asset_rel) if not os.path.isabs(asset_rel) else asset_rel
                if not os.path.isfile(full_path):
                    errors.append(f"Background '{bg_id}' asset file does not exist on disk: {asset_rel}")
                else:
                    try:
                        w, h, fmt = read_image_dimensions(full_path)
                        if w != FRAME_WIDTH or h != FRAME_HEIGHT:
                            errors.append(
                                f"Background '{bg_id}' dimensions {w}x{h} do not match vertical {FRAME_WIDTH}x{FRAME_HEIGHT}."
                            )
                    except Exception as e:
                        errors.append(f"Background '{bg_id}' corrupted image header: {e}")

            # Check thumbnail
            thumb_rel = bg.get("thumbnailPath")
            if thumb_rel:
                full_thumb = os.path.join(self.root, thumb_rel) if not os.path.isabs(thumb_rel) else thumb_rel
                if not os.path.isfile(full_thumb):
                    warnings.append(f"Background '{bg_id}' thumbnail not found on disk: {thumb_rel}")

        # Check episodes cross-reference
        if check_episodes:
            refs = self.find_active_references()
            registered_map = {b["id"]: b for b in bgs}

            for eid, ref_list in refs.items():
                if eid in ("scientific_visualization", "none"):
                    continue

                if eid not in registered_map:
                    ep_names = sorted(list({r["episode"] for r in ref_list}))
                    errors.append(
                        f"Unregistered background '{eid}' referenced in episode(s): {', '.join(ep_names)}."
                    )
                else:
                    bg_obj = registered_map[eid]
                    bg_st = bg_obj.get("status", "active")
                    if bg_st != "active":
                        ep_names = sorted(list({r["episode"] for r in ref_list}))
                        warnings.append(
                            f"{bg_st.capitalize()} background '{eid}' is referenced by active episode(s): {', '.join(ep_names)}."
                        )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "stats": {
                "total_backgrounds": len(bgs),
                "active_count": len([b for b in bgs if b.get("status", "active") == "active"]),
                "disabled_count": len([b for b in bgs if b.get("status") == "disabled"]),
                "archived_count": len([b for b in bgs if b.get("status") == "archived"]),
            },
        }

    def sync_downstream(self):
        """
        Synchronizes active backgrounds to:
        1. assets/library.json
        2. assets/backgrounds/index.json
        3. library/papercut/kit/assets/AssetLoader.ts
        4. Remotion public assets directories
        """
        # 1. Update assets/backgrounds/index.json
        index_path = os.path.join(self.root, "assets", "backgrounds", "index.json")
        index_entries = []
        for bg in self.data.get("backgrounds", []):
            bg_id = bg["id"]
            index_entries.append({
                "id": bg_id,
                "name": bg.get("name", bg_id),
                "description": bg.get("description", ""),
                "category": bg.get("category", "General"),
                "mood": bg.get("mood", "cool / studious"),
                "aspect_ratio": bg.get("aspectRatio", "9:16"),
                "dimensions": bg.get("dimensions", {"width": FRAME_WIDTH, "height": FRAME_HEIGHT, "aspect_ratio": "9:16"}),
                "floor_y": bg.get("floorY", 1380),
                "presenter_zone": {"x_range": [240, 840], "y_range": [900, 1750], "status": "clear_unobstructed"},
                "best_for": bg.get("tags", ["Science explanations"]),
                "path": bg.get("assetPath", f"assets/backgrounds/{bg_id}/background.png"),
                "metadata_path": f"assets/backgrounds/{bg_id}/metadata.json",
                "status": bg.get("status", "active"),
            })

        idx_data = {
            "version": "1.2.0",
            "total_backgrounds": len(index_entries),
            "updated_at": get_current_iso_timestamp(),
            "backgrounds": index_entries,
        }
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(idx_data, f, indent=2)

        # 2. Update assets/library.json
        lib_path = os.path.join(self.root, "assets", "library.json")
        lib = {}
        if os.path.isfile(lib_path):
            with open(lib_path, "r", encoding="utf-8") as f:
                lib = json.load(f)

        # In library.json, only expose active backgrounds for rendering/production
        active_entries = [e for e in index_entries if e.get("status") == "active"]
        lib.setdefault("categories", {})["environments"] = active_entries
        lib["updated_at"] = get_current_iso_timestamp()

        with open(lib_path, "w", encoding="utf-8") as f:
            json.dump(lib, f, indent=2)

        # 3. Update TypeScript AssetLoader
        from manage_environment import update_typescript_asset_loader, sync_assets_to_public
        update_typescript_asset_loader(self.root)

        # 4. Sync public assets for each background
        for bg in self.data.get("backgrounds", []):
            sync_assets_to_public(self.root, bg["id"])


# Module-level convenience functions
_default_registry = None

def get_registry(repo_root: Optional[str] = None) -> BackgroundRegistry:
    global _default_registry
    if _default_registry is None or repo_root is not None:
        _default_registry = BackgroundRegistry(repo_root=repo_root)
    return _default_registry
