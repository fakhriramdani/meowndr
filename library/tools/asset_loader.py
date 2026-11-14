#!/usr/bin/env python3
"""
Asset loader and validation engine for the 2D papercraft explainer project.
Loads asset library catalogs, individual metadata, and verifies dimensions,
file existence, safe zones, and category layer separation.
"""

import json
import os
import struct
from typing import Any, Dict, List, Optional, Tuple

SAFE_ZONES = {
    "BANNER_TOP_MAX": 420,
    "FLOOR_Y_MIN": 1200,
    "FLOOR_Y_MAX": 1550,
    "FRAME_WIDTH": 1080,
    "FRAME_HEIGHT": 1920,
    "BOTTOM_UI_MIN": 1580,
}


def find_project_root(start_dir: Optional[str] = None) -> str:
    """Finds the root directory of the papercut-explainer project."""
    curr = os.path.abspath(start_dir or os.getcwd())
    while curr != os.path.dirname(curr):
        if os.path.exists(os.path.join(curr, "assets", "library.json")) or os.path.exists(
            os.path.join(curr, "assets", "backgrounds", "index.json")
        ):
            return curr
        if os.path.basename(curr) == "papercut-explainer":
            return curr
        curr = os.path.dirname(curr)
    return os.path.abspath(start_dir or os.getcwd())


def read_image_dimensions(image_path: str) -> Tuple[int, int, str]:
    """
    Reads image dimensions directly from binary headers without external dependencies.
    Supports PNG and JPEG.
    Returns (width, height, format).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file does not exist: {image_path}")

    with open(image_path, "rb") as f:
        head = f.read(32)

        # PNG: 8-byte signature, followed by IHDR chunk (length 4, type 4, width 4, height 4)
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
                # SOF markers: SOF0 (\xff\xc0) to SOF15 (\xff\xcf) except DHT/JPG/DAC
                if marker in [0xFFC0, 0xFFC1, 0xFFC2, 0xFFC3, 0xFFC5, 0xFFC6, 0xFFC7, 0xFFC9, 0xFFCA, 0xFFCB, 0xFFCD, 0xFFCE, 0xFFCF]:
                    f.read(3)  # length (2) + precision (1)
                    height, width = struct.unpack(">HH", f.read(4))
                    return width, height, "JPEG"
                elif marker in [0xFFD9, 0xFFDA]:  # EOI or SOS
                    break
                else:
                    length = struct.unpack(">H", f.read(2))[0]
                    f.seek(length - 2, os.SEEK_CUR)

    raise ValueError(f"Unsupported or unrecognized image header in {image_path}")


def load_library(root_dir: Optional[str] = None) -> Dict[str, Any]:
    """Loads the main asset library index."""
    root = root_dir or find_project_root()
    lib_path = os.path.join(root, "assets", "library.json")
    if os.path.exists(lib_path):
        with open(lib_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Fallback to backgrounds/index.json
    bg_idx_path = os.path.join(root, "assets", "backgrounds", "index.json")
    if os.path.exists(bg_idx_path):
        with open(bg_idx_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "version": data.get("version", "1.0.0"),
                "categories": {
                    "environments": data.get("backgrounds", []),
                    "props": [],
                    "characters": [],
                    "foregrounds": [],
                },
            }

    raise FileNotFoundError(f"No asset library index found under {root}/assets")


def get_environment(env_id: str, root_dir: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves metadata for a specific environment asset."""
    root = root_dir or find_project_root()
    lib = load_library(root)
    envs = lib.get("categories", {}).get("environments", [])
    for env in envs:
        if env.get("id") == env_id:
            # Load full metadata.json if available
            meta_path = env.get("metadata_path")
            if meta_path:
                full_meta_path = os.path.join(root, meta_path)
                if os.path.exists(full_meta_path):
                    with open(full_meta_path, "r", encoding="utf-8") as f:
                        loaded = json.load(f)
                        loaded["path"] = env.get("path") or loaded.get("path")
                        return loaded
            return env
    raise KeyError(f"Environment '{env_id}' not found in library.")


def validate_environment(env: Dict[str, Any], root_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Validates environment metadata and file consistency.
    Returns {"valid": bool, "errors": List[str], "warnings": List[str]}
    """
    errors: List[str] = []
    warnings: List[str] = []
    root = root_dir or find_project_root()

    env_id = env.get("id")
    if not env_id or not isinstance(env_id, str):
        errors.append("Missing or invalid 'id' field.")

    if not env.get("name") or not isinstance(env.get("name"), str):
        errors.append("Missing or invalid 'name' field.")

    # Dimensions
    dim = env.get("dimensions", {})
    if not dim:
        errors.append("Missing 'dimensions' block.")
    else:
        w = dim.get("width")
        h = dim.get("height")
        aspect = dim.get("aspect_ratio") or env.get("aspect_ratio")

        if w != SAFE_ZONES["FRAME_WIDTH"]:
            errors.append(f"Width must be {SAFE_ZONES['FRAME_WIDTH']}px (got {w}).")
        if h != SAFE_ZONES["FRAME_HEIGHT"]:
            errors.append(f"Height must be {SAFE_ZONES['FRAME_HEIGHT']}px (got {h}).")
        if aspect != "9:16":
            errors.append(f"Aspect ratio must be '9:16' (got '{aspect}').")

    # Floor Y
    floor_y = env.get("floor_y")
    if floor_y is None and "layout" in env:
        floor_y = env["layout"].get("floor_y")

    if floor_y is None or not isinstance(floor_y, (int, float)):
        errors.append("Missing or invalid 'floor_y'.")
    elif floor_y < SAFE_ZONES["FLOOR_Y_MIN"] or floor_y > SAFE_ZONES["FLOOR_Y_MAX"]:
        errors.append(
            f"floor_y ({floor_y}) is outside valid vertical range [{SAFE_ZONES['FLOOR_Y_MIN']}, {SAFE_ZONES['FLOOR_Y_MAX']}]."
        )

    # Presenter Zone
    pzone = env.get("presenter_zone")
    if not pzone and "layout" in env:
        pzone = env["layout"].get("presenter_zone")

    if not pzone:
        errors.append("Missing 'presenter_zone' configuration.")
    else:
        x_range = pzone.get("x_range")
        y_range = pzone.get("y_range")

        if not isinstance(x_range, list) or len(x_range) != 2 or x_range[0] >= x_range[1]:
            errors.append("presenter_zone.x_range must be [min_x, max_x] with min_x < max_x.")
        else:
            if x_range[0] < 0 or x_range[1] > SAFE_ZONES["FRAME_WIDTH"]:
                errors.append(f"presenter_zone.x_range [{x_range[0]}, {x_range[1]}] exceeds frame width.")

        if not isinstance(y_range, list) or len(y_range) != 2 or y_range[0] >= y_range[1]:
            errors.append("presenter_zone.y_range must be [min_y, max_y] with min_y < max_y.")
        else:
            if y_range[0] < SAFE_ZONES["BANNER_TOP_MAX"]:
                warnings.append(
                    f"Presenter zone top ({y_range[0]}) encroaches on header banner safe area (< {SAFE_ZONES['BANNER_TOP_MAX']})."
                )
            if floor_y is not None and (floor_y < y_range[0] or floor_y > y_range[1]):
                errors.append(f"floor_y ({floor_y}) is outside presenter_zone y_range [{y_range[0]}, {y_range[1]}].")

    # Image file check
    rel_path = env.get("path")
    if not rel_path and "asset_paths" in env:
        rel_path = env["asset_paths"].get("image")

    if not rel_path:
        errors.append("Missing asset image path.")
    else:
        full_img_path = os.path.join(root, rel_path) if not os.path.isabs(rel_path) else rel_path
        if not os.path.exists(full_img_path):
            errors.append(f"Asset image file does not exist: {full_img_path}")
        else:
            try:
                actual_w, actual_h, fmt = read_image_dimensions(full_img_path)
                if actual_w != SAFE_ZONES["FRAME_WIDTH"] or actual_h != SAFE_ZONES["FRAME_HEIGHT"]:
                    errors.append(
                        f"Actual image dimensions ({actual_w}x{actual_h}) do not match required 9:16 vertical resolution ({SAFE_ZONES['FRAME_WIDTH']}x{SAFE_ZONES['FRAME_HEIGHT']})."
                    )
            except Exception as e:
                errors.append(f"Failed to inspect image header: {e}")

    # Cross-category pollution check
    desc = (env.get("description") or "").lower()
    if any(k in desc for k in ["with presenter standing", "including critter", "human figure baked"]):
        errors.append("Environment description indicates character figures baked in; violation of layer separation.")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_presenter_placement(env: Dict[str, Any], x: int, y: int) -> Tuple[bool, Optional[str]]:
    """Validates if presenter feet coordinate (x, y) is positioned accurately."""
    floor_y = env.get("floor_y")
    if floor_y is None and "layout" in env:
        floor_y = env["layout"].get("floor_y")

    if floor_y is None:
        return False, "Environment has no floor_y defined."

    if abs(y - floor_y) > 40:
        return False, f"Presenter feet y ({y}) must be on floor_y ({floor_y} ± 40px tolerance)."

    pzone = env.get("presenter_zone") or (env.get("layout", {}).get("presenter_zone"))
    if not pzone:
        return False, "Environment has no presenter_zone defined."

    min_x, max_x = pzone["x_range"]
    if x < min_x or x > max_x:
        return False, f"Presenter x ({x}) must be within presenter_zone horizontal bounds [{min_x}, {max_x}]."

    return True, None
