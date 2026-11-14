#!/usr/bin/env python3
"""
Asset Studio Service Engine for @meowndr 2D Papercraft Explainer.

Provides unified management for:
- Backgrounds & Environments (backed by BackgroundRegistry)
- Characters & Mascot Variants
- Props & Scientific Apparatus
- Foregrounds & Brand Identity Assets
- Asset Collections
- Validation Center & Downstream Synchronization
- Path Traversal & Security Controls
"""

import os
import sys
import json
import shutil
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from background_registry import (
    BackgroundRegistry,
    find_repo_root,
    get_current_iso_timestamp,
    read_image_dimensions,
    FRAME_WIDTH,
    FRAME_HEIGHT,
)


class AssetStudioService:
    """Core backend service powering the @meowndr Asset Studio interface."""

    def __init__(self, repo_root: Optional[str] = None):
        self.root = os.path.abspath(repo_root or find_repo_root())
        self.bg_reg = BackgroundRegistry(repo_root=self.root)
        self.collections_path = os.path.join(self.root, "library", "assets", "collections.json")

    # -------------------------------------------------------------------------
    # Security & Path Resolution
    # -------------------------------------------------------------------------

    def resolve_safe_path(self, rel_or_abs_path: str, allow_create: bool = False) -> str:
        """
        Ensures the path is resolved safely inside allowed repository directories.
        Prevents directory traversal and arbitrary filesystem tampering.
        """
        if not rel_or_abs_path:
            raise ValueError("Path cannot be empty.")

        clean_path = os.path.normpath(
            os.path.join(self.root, rel_or_abs_path) if not os.path.isabs(rel_or_abs_path) else rel_or_abs_path
        )

        allowed_prefixes = [
            os.path.join(self.root, "assets"),
            os.path.join(self.root, "library"),
            os.path.join(self.root, "episodes"),
            "/tmp",
        ]

        if not any(clean_path.startswith(prefix) for prefix in allowed_prefixes):
            raise PermissionError(f"Access denied: Path '{rel_or_abs_path}' is outside approved directories.")

        if ".." in os.path.relpath(clean_path, self.root) and not clean_path.startswith("/tmp"):
            raise PermissionError(f"Path traversal detected: {rel_or_abs_path}")

        return clean_path

    # -------------------------------------------------------------------------
    # Overview & Metrics
    # -------------------------------------------------------------------------

    def get_overview(self) -> Dict[str, Any]:
        """Gathers real-time statistics across all asset categories in the repository."""
        bgs = self.bg_reg.list_backgrounds()
        chars = self.list_characters()
        props = self.list_props()
        other = self.list_other_assets()
        collections = self.list_collections()

        # Discovery & diagnostics
        disc = self.bg_reg.discover_backgrounds()
        val = self.validate_all()

        # Episode references summary
        all_refs = self.bg_reg.find_active_references()
        active_bgs = [b for b in bgs if b.get("status") == "active"]
        disabled_bgs = [b for b in bgs if b.get("status") == "disabled"]
        archived_bgs = [b for b in bgs if b.get("status") == "archived"]

        return {
            "total_assets": len(bgs) + len(chars) + len(props) + len(other.get("foregrounds", [])) + len(other.get("brand", [])),
            "backgrounds": {
                "total": len(bgs),
                "active": len(active_bgs),
                "disabled": len(disabled_bgs),
                "archived": len(archived_bgs),
            },
            "characters": {
                "total": len(chars),
                "variants_total": sum(len(c.get("variants", [])) for c in chars),
                "states_total": sum(len(c.get("states", [])) for c in chars),
            },
            "props": {
                "total": len(props),
            },
            "other_assets": {
                "foregrounds": len(other.get("foregrounds", [])),
                "brand": len(other.get("brand", [])),
            },
            "collections_count": len(collections),
            "diagnostics": {
                "missing_files_count": len(disc.get("missing_on_disk", [])),
                "unregistered_count": len(disc.get("unregistered", [])),
                "validation_errors_count": len(val.get("errors", [])),
                "validation_warnings_count": len(val.get("warnings", [])),
                "health_status": "EXCELLENT" if len(val.get("errors", [])) == 0 else "WARNINGS_FOUND",
            },
            "episode_references_count": sum(len(v) for v in all_refs.values()),
        }

    # -------------------------------------------------------------------------
    # Backgrounds (Delegates to BackgroundRegistry)
    # -------------------------------------------------------------------------

    def list_backgrounds(self, category=None, status=None, query=None, tag=None) -> List[Dict[str, Any]]:
        return self.bg_reg.list_backgrounds(category=category, status=status, query=query, tag=tag, check_exists=True)

    def get_background(self, bg_id: str) -> Optional[Dict[str, Any]]:
        bg = self.bg_reg.get_background(bg_id)
        if bg:
            bg["references"] = self.bg_reg.find_active_references(bg_id).get(bg_id, [])
        return bg

    def add_background(self, image_path: str, **kwargs) -> Dict[str, Any]:
        safe_img = self.resolve_safe_path(image_path)
        return self.bg_reg.add_background(image_path=safe_img, **kwargs)

    def update_background(self, bg_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates editable metadata fields for a background."""
        bgs = self.bg_reg.data.get("backgrounds", [])
        entry = next((b for b in bgs if b.get("id") == bg_id), None)
        if not entry:
            raise KeyError(f"Background '{bg_id}' not found.")

        # Editable fields
        for field in ["name", "description", "category", "tags", "floorY", "mood"]:
            if field in updates:
                entry[field] = updates[field]

        entry["updatedAt"] = get_current_iso_timestamp()
        self.bg_reg.save()
        self.bg_reg.sync_downstream()

        # Update metadata.json on disk if present
        meta_path = os.path.join(self.root, "assets", "backgrounds", bg_id, "metadata.json")
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    disk_meta = json.load(f)
                disk_meta["name"] = entry.get("name")
                disk_meta["description"] = entry.get("description")
                disk_meta["category"] = entry.get("category")
                disk_meta["mood"] = entry.get("mood")
                disk_meta.setdefault("layout", {})["floor_y"] = entry.get("floorY", 1380)
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(disk_meta, f, indent=2)
            except Exception:
                pass

        return {"status": "success", "id": bg_id, "entry": entry}

    def set_background_status(self, bg_id: str, status: str, reason: Optional[str] = None) -> Dict[str, Any]:
        if status == "disabled":
            return self.bg_reg.disable_background(bg_id, reason=reason)
        elif status == "archived":
            return self.bg_reg.archive_background(bg_id, reason=reason)
        elif status == "active":
            return self.bg_reg.enable_background(bg_id)
        else:
            raise ValueError(f"Invalid status '{status}'. Must be active, disabled, or archived.")

    def remove_background(self, bg_id: str, force: bool = False, delete_asset: bool = False) -> Dict[str, Any]:
        return self.bg_reg.remove_background(bg_id, force=force, delete_asset=delete_asset)

    # -------------------------------------------------------------------------
    # Characters Management
    # -------------------------------------------------------------------------

    def list_characters(self) -> List[Dict[str, Any]]:
        """Lists all registered characters, their metadata, states, and avatar variants."""
        chars_dir = os.path.join(self.root, "assets", "characters")
        if not os.path.isdir(chars_dir):
            return []

        results = []
        for c_id in sorted(os.listdir(chars_dir)):
            sub = os.path.join(chars_dir, c_id)
            if not os.path.isdir(sub):
                continue

            meta_file = os.path.join(sub, "metadata.json")
            meta: Dict[str, Any] = {"id": c_id, "name": c_id.replace("-", " ").title()}
            if os.path.isfile(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                except Exception:
                    pass

            # Scan variants / avatars in avatar/ subfolder
            avatar_dir = os.path.join(sub, "avatar")
            variants = []
            if os.path.isdir(avatar_dir):
                for f_name in sorted(os.listdir(avatar_dir)):
                    f_path = os.path.join(avatar_dir, f_name)
                    if os.path.isfile(f_path) and f_name.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".svg")):
                        try:
                            w, h, fmt = read_image_dimensions(f_path)
                        except Exception:
                            w, h, fmt = (1024, 1024, "PNG")
                        var_id = os.path.splitext(f_name)[0]
                        variants.append({
                            "id": var_id,
                            "name": var_id.replace("cat-scientist-avatar-", "").replace("-", " ").title(),
                            "path": os.path.relpath(f_path, self.root),
                            "format": fmt,
                            "dimensions": {"width": w, "height": h},
                            "hasTransparency": "transparent" in f_name.lower() or fmt == "PNG",
                        })

            # Check primary preview
            preview_path = None
            if variants:
                # Prefer primary or transparent
                p_var = next((v for v in variants if "primary" in v["id"]), variants[0])
                preview_path = p_var["path"]

            # Controllable states from style
            states = meta.get("style", {}).get("states", [
                "idle", "talking", "explaining", "pointing", "curious", "excited", "celebrating", "surprised", "thinking", "waving"
            ])

            # Reference tracking in episodes
            all_refs = self.bg_reg.find_active_references()
            refs = all_refs.get(c_id, [])

            results.append({
                "id": c_id,
                "name": meta.get("name", c_id),
                "category": meta.get("category", "characters"),
                "description": meta.get("description", ""),
                "status": meta.get("status", "active"),
                "primary_color": meta.get("style", {}).get("primary_color", "#F97316"),
                "secondary_color": meta.get("style", {}).get("secondary_color", "#FFFDF7"),
                "states": states,
                "dimensions": meta.get("dimensions", {"default_size": 240, "anchor": "ground-feet"}),
                "placement": meta.get("placement", {"requires_floor_y": True}),
                "previewPath": preview_path,
                "variants": variants,
                "references": refs,
                "metadataPath": os.path.relpath(meta_file, self.root) if os.path.isfile(meta_file) else None,
            })

        return results

    def get_character(self, char_id: str) -> Optional[Dict[str, Any]]:
        chars = self.list_characters()
        return next((c for c in chars if c["id"] == char_id), None)

    def update_character(self, char_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates character metadata."""
        char_dir = os.path.join(self.root, "assets", "characters", char_id)
        if not os.path.isdir(char_dir):
            raise KeyError(f"Character '{char_id}' not found.")

        meta_file = os.path.join(char_dir, "metadata.json")
        meta = {}
        if os.path.isfile(meta_file):
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)

        for field in ["name", "description", "status"]:
            if field in updates:
                meta[field] = updates[field]

        if "style" in updates and isinstance(updates["style"], dict):
            meta.setdefault("style", {}).update(updates["style"])

        meta["updated_at"] = get_current_iso_timestamp()

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        # Sync master library.json
        self.sync_character_to_library(char_id, meta)

        return {"status": "success", "id": char_id, "character": meta}

    def add_character_variant(self, char_id: str, variant_id: str, image_source_path: str) -> Dict[str, Any]:
        """Adds a new avatar/expression variant image for a character."""
        char_dir = os.path.join(self.root, "assets", "characters", char_id)
        if not os.path.isdir(char_dir):
            raise KeyError(f"Character '{char_id}' does not exist.")

        safe_src = self.resolve_safe_path(image_source_path)
        if not os.path.isfile(safe_src):
            raise FileNotFoundError(f"Source image '{image_source_path}' not found.")

        avatar_dir = os.path.join(char_dir, "avatar")
        os.makedirs(avatar_dir, exist_ok=True)

        _, ext = os.path.splitext(safe_src)
        dest_filename = f"{char_id}-avatar-{variant_id}{ext}"
        dest_path = os.path.join(avatar_dir, dest_filename)

        shutil.copy2(safe_src, dest_path)
        return {
            "status": "success",
            "character_id": char_id,
            "variant_id": variant_id,
            "path": os.path.relpath(dest_path, self.root),
        }

    def remove_character_variant(self, char_id: str, variant_id: str) -> Dict[str, Any]:
        """Removes a character variant from disk."""
        avatar_dir = os.path.join(self.root, "assets", "characters", char_id, "avatar")
        if not os.path.isdir(avatar_dir):
            raise FileNotFoundError("Avatar directory not found.")

        target = None
        for f in os.listdir(avatar_dir):
            if f.startswith(variant_id) or f.startswith(f"{char_id}-avatar-{variant_id}"):
                target = os.path.join(avatar_dir, f)
                break

        if not target or not os.path.isfile(target):
            raise FileNotFoundError(f"Variant '{variant_id}' not found for character '{char_id}'.")

        os.remove(target)
        return {"status": "success", "character_id": char_id, "variant_id": variant_id}

    def sync_character_to_library(self, char_id: str, meta: Dict[str, Any]):
        """Synchronizes character definitions into assets/library.json."""
        lib_path = os.path.join(self.root, "assets", "library.json")
        if not os.path.isfile(lib_path):
            return

        with open(lib_path, "r", encoding="utf-8") as f:
            lib = json.load(f)

        chars = lib.setdefault("categories", {}).setdefault("characters", [])
        entry = next((c for c in chars if c.get("id") == char_id), None)
        new_item = {
            "id": char_id,
            "name": meta.get("name", char_id),
            "category": "characters",
            "dimensions": meta.get("dimensions", {"default_size": 240, "anchor": "ground-feet"}),
            "metadata_path": f"assets/characters/{char_id}/metadata.json",
        }
        if entry:
            entry.update(new_item)
        else:
            chars.append(new_item)

        with open(lib_path, "w", encoding="utf-8") as f:
            json.dump(lib, f, indent=2)

    # -------------------------------------------------------------------------
    # Props Management
    # -------------------------------------------------------------------------

    def list_props(self) -> List[Dict[str, Any]]:
        """Lists all props registered in assets/props."""
        props_dir = os.path.join(self.root, "assets", "props")
        if not os.path.isdir(props_dir):
            return []

        results = []
        for p_id in sorted(os.listdir(props_dir)):
            sub = os.path.join(props_dir, p_id)
            if not os.path.isdir(sub):
                continue

            meta_file = os.path.join(sub, "metadata.json")
            meta = {"id": p_id, "name": p_id.replace("-", " ").title()}
            if os.path.isfile(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                except Exception:
                    pass

            # Search for visual asset (SVG or PNG if present)
            img_rel = None
            for item in os.listdir(sub):
                if item.lower().endswith((".png", ".svg", ".webp", ".jpg")):
                    img_rel = os.path.relpath(os.path.join(sub, item), self.root)
                    break

            results.append({
                "id": p_id,
                "name": meta.get("name", p_id),
                "category": meta.get("category", "props"),
                "description": meta.get("description", ""),
                "status": meta.get("status", "active"),
                "dimensions": meta.get("dimensions", {"width": 120, "height": 180, "anchor": "bottom-center"}),
                "placement": meta.get("placement", {"supports_floor_mount": True, "supports_hand_held": True}),
                "style": meta.get("style", {}),
                "assetPath": img_rel,
                "metadataPath": os.path.relpath(meta_file, self.root) if os.path.isfile(meta_file) else None,
                "createdAt": meta.get("created_at"),
            })

        return results

    def get_prop(self, prop_id: str) -> Optional[Dict[str, Any]]:
        props = self.list_props()
        return next((p for p in props if p["id"] == prop_id), None)

    def add_prop(
        self,
        prop_id: str,
        name: str,
        description: str = "",
        width: int = 120,
        height: int = 180,
        anchor: str = "bottom-center",
        supports_floor: bool = True,
        supports_hand: bool = True,
        image_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Registers a new prop into assets/props and assets/library.json."""
        clean_id = prop_id.strip().lower()
        prop_dir = os.path.join(self.root, "assets", "props", clean_id)
        if os.path.exists(prop_dir):
            raise FileExistsError(f"Prop '{clean_id}' already exists.")

        os.makedirs(prop_dir, exist_ok=True)
        img_rel = None
        if image_path:
            safe_src = self.resolve_safe_path(image_path)
            _, ext = os.path.splitext(safe_src)
            dest_file = os.path.join(prop_dir, f"prop{ext}")
            shutil.copy2(safe_src, dest_file)
            img_rel = os.path.relpath(dest_file, self.root)

        meta = {
            "id": clean_id,
            "name": name,
            "category": "props",
            "description": description,
            "dimensions": {"width": width, "height": height, "anchor": anchor},
            "placement": {"supports_floor_mount": supports_floor, "supports_hand_held": supports_hand, "default_scale": 1.0},
            "status": "active",
            "created_at": get_current_iso_timestamp(),
        }

        meta_file = os.path.join(prop_dir, "metadata.json")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        # Sync library.json
        lib_path = os.path.join(self.root, "assets", "library.json")
        if os.path.isfile(lib_path):
            with open(lib_path, "r", encoding="utf-8") as f:
                lib = json.load(f)
            lib.setdefault("categories", {}).setdefault("props", []).append({
                "id": clean_id,
                "name": name,
                "category": "props",
                "dimensions": meta["dimensions"],
                "metadata_path": f"assets/props/{clean_id}/metadata.json",
            })
            with open(lib_path, "w", encoding="utf-8") as f:
                json.dump(lib, f, indent=2)

        return {"status": "success", "id": clean_id, "prop": meta}

    def remove_prop(self, prop_id: str, force: bool = False, delete_asset: bool = False) -> Dict[str, Any]:
        """Safely removes a prop with reference checks."""
        prop_dir = os.path.join(self.root, "assets", "props", prop_id)
        if not os.path.isdir(prop_dir):
            raise KeyError(f"Prop '{prop_id}' not found.")

        # Check references in episodes
        all_refs = self.bg_reg.find_active_references()
        refs = all_refs.get(prop_id, [])
        if refs and not force:
            raise ValueError(f"Cannot remove prop '{prop_id}'! Referenced in {len(refs)} episode(s).")

        # Remove from library.json
        lib_path = os.path.join(self.root, "assets", "library.json")
        if os.path.isfile(lib_path):
            with open(lib_path, "r", encoding="utf-8") as f:
                lib = json.load(f)
            props = lib.get("categories", {}).get("props", [])
            lib["categories"]["props"] = [p for p in props if p.get("id") != prop_id]
            with open(lib_path, "w", encoding="utf-8") as f:
                json.dump(lib, f, indent=2)

        deleted_disk = False
        if delete_asset:
            shutil.rmtree(prop_dir)
            deleted_disk = True

        return {"status": "success", "id": prop_id, "deleted_asset": deleted_disk}

    # -------------------------------------------------------------------------
    # Other Assets (Foregrounds & Brand)
    # -------------------------------------------------------------------------

    def list_other_assets(self) -> Dict[str, List[Dict[str, Any]]]:
        """Lists foreground overlays and official brand assets."""
        foregrounds = []
        fg_dir = os.path.join(self.root, "assets", "foregrounds")
        if os.path.isdir(fg_dir):
            for fg_id in sorted(os.listdir(fg_dir)):
                sub = os.path.join(fg_dir, fg_id)
                if not os.path.isdir(sub):
                    continue
                meta_file = os.path.join(sub, "metadata.json")
                meta = {"id": fg_id, "name": fg_id.replace("-", " ").title()}
                if os.path.isfile(meta_file):
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                    except Exception:
                        pass
                foregrounds.append({
                    "id": fg_id,
                    "name": meta.get("name", fg_id),
                    "category": "foregrounds",
                    "description": meta.get("description", ""),
                    "metadataPath": os.path.relpath(meta_file, self.root) if os.path.isfile(meta_file) else None,
                })

        # Brand assets
        brand_assets = []
        brand_dir = os.path.join(self.root, "assets", "brand")
        if os.path.isdir(brand_dir):
            for b_file in sorted(os.listdir(brand_dir)):
                full_path = os.path.join(brand_dir, b_file)
                if os.path.isfile(full_path) and b_file.lower().endswith((".png", ".jpg", ".svg", ".webp")):
                    try:
                        w, h, fmt = read_image_dimensions(full_path)
                    except Exception:
                        w, h, fmt = (1024, 1024, "PNG")
                    b_id = os.path.splitext(b_file)[0]
                    brand_assets.append({
                        "id": b_id,
                        "name": b_id.replace("meowndr-", "").replace("cat-scientist-", "").replace("-", " ").title(),
                        "category": "brand",
                        "path": os.path.relpath(full_path, self.root),
                        "format": fmt,
                        "dimensions": {"width": w, "height": h},
                        "hasTransparency": "transparent" in b_file.lower() or fmt in ("PNG", "SVG"),
                    })

        return {"foregrounds": foregrounds, "brand": brand_assets}

    # -------------------------------------------------------------------------
    # Asset Collections
    # -------------------------------------------------------------------------

    def list_collections(self) -> List[Dict[str, Any]]:
        """Reads collections registry from disk."""
        if not os.path.isfile(self.collections_path):
            return []
        try:
            with open(self.collections_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("collections", [])
        except Exception:
            return []

    def save_collections(self, collections: List[Dict[str, Any]]):
        """Saves collections to disk."""
        data = {
            "version": "1.0.0",
            "updatedAt": get_current_iso_timestamp(),
            "collections": collections,
        }
        os.makedirs(os.path.dirname(self.collections_path), exist_ok=True)
        with open(self.collections_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def create_collection(self, coll_id: str, name: str, description: str = "", category: str = "Curated", asset_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        colls = self.list_collections()
        clean_id = coll_id.strip().lower()
        if any(c["id"] == clean_id for c in colls):
            raise FileExistsError(f"Collection '{clean_id}' already exists.")

        item = {
            "id": clean_id,
            "name": name,
            "description": description,
            "category": category,
            "assetIds": asset_ids or [],
        }
        colls.append(item)
        self.save_collections(colls)
        return {"status": "success", "collection": item}

    def update_collection(self, coll_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        colls = self.list_collections()
        target = next((c for c in colls if c["id"] == coll_id), None)
        if not target:
            raise KeyError(f"Collection '{coll_id}' not found.")

        for field in ["name", "description", "category", "assetIds"]:
            if field in updates:
                target[field] = updates[field]

        self.save_collections(colls)
        return {"status": "success", "collection": target}

    def delete_collection(self, coll_id: str) -> Dict[str, Any]:
        colls = self.list_collections()
        filtered = [c for c in colls if c["id"] != coll_id]
        if len(filtered) == len(colls):
            raise KeyError(f"Collection '{coll_id}' not found.")

        self.save_collections(filtered)
        return {"status": "success", "deleted_id": coll_id}

    # -------------------------------------------------------------------------
    # Comprehensive Validation Center
    # -------------------------------------------------------------------------

    def validate_all(self) -> Dict[str, Any]:
        """Runs validation across all assets (Backgrounds, Characters, Props, Episodes)."""
        issues = []
        errors = []
        warnings = []

        # 1. Backgrounds Validation
        bg_val = self.bg_reg.validate_registry(check_episodes=True)
        for e in bg_val.get("errors", []):
            errors.append(e)
            issues.append({
                "severity": "ERROR",
                "category": "backgrounds",
                "message": e,
                "suggestedAction": "Register the missing background asset in BackgroundRegistry or resolve episode reference."
            })
        for w in bg_val.get("warnings", []):
            warnings.append(w)
            issues.append({
                "severity": "WARNING",
                "category": "backgrounds",
                "message": w,
                "suggestedAction": "Review whether the active episode should switch to an active background."
            })

        # 2. Character Mascots Color & BlendMode Audit
        try:
            from validate_character_color import validate_cat_scientist_component
            cat_tsx = os.path.join(self.root, "library", "papercut", "kit", "cast", "CatScientist.tsx")
            if os.path.isfile(cat_tsx):
                cat_errors = validate_cat_scientist_component(Path(cat_tsx))
                for ce in cat_errors:
                    errors.append(ce)
                    issues.append({
                        "severity": "ERROR",
                        "category": "characters",
                        "message": ce,
                        "suggestedAction": "Ensure CatScientist textures include backgroundBlendMode: 'multiply'."
                    })
        except Exception:
            pass

        # 3. Prop Validation (Check metadata validity)
        props = self.list_props()
        for p in props:
            p_dims = p.get("dimensions", {})
            if not p_dims.get("width") or not p_dims.get("height"):
                w_msg = f"Prop '{p['id']}' missing explicit width/height dimensions."
                warnings.append(w_msg)
                issues.append({
                    "severity": "WARNING",
                    "category": "props",
                    "message": w_msg,
                    "suggestedAction": "Add width and height to prop metadata.json."
                })

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "issues": issues,
            "stats": {
                "total_issues": len(issues),
                "errors_count": len(errors),
                "warnings_count": len(warnings),
            },
        }

    # -------------------------------------------------------------------------
    # Downstream Sync
    # -------------------------------------------------------------------------

    def sync_all(self) -> Dict[str, Any]:
        """Synchronizes all registries downstream."""
        self.bg_reg.sync_downstream()
        return {
            "status": "success",
            "message": "Synchronized Background Registry, AssetLoader.ts, library.json, and public bundles.",
            "synced_at": get_current_iso_timestamp(),
        }
