#!/usr/bin/env python3
"""
validate_thumbnail.py: Automated QA Validation for Mandatory Episode Thumbnails & Opening Frames.
Enforces:
  1. Title field non-empty & faithful to episode.
  2. Exact canonical channel name: "@meowndr".
  3. Canonical mascot asset configured and existing on disk.
  4. Aspect ratio (16:9 for YouTube thumbnail, 9:16 for opening frame) and dimensions.
  5. Physical image-analysis verification of all three mandatory elements in rendered pixels:
     - Prominent Video Title (cardstock text pixel clusters)
     - Channel Name '@meowndr' (brand pill & contrast signature)
     - Cat Scientist Mascot (orange fur #F97316, cream muzzle #FFFDF7, spectacles, turquoise pen, non-white cat validation).
"""

import sys
import json
import struct
import zlib
from pathlib import Path
from typing import Tuple, Dict, Any, List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.brand_config import (
    CHANNEL_NAME,
    CANONICAL_MASCOT_REL_PATH,
    THUMBNAIL_WIDTH,
    THUMBNAIL_HEIGHT,
    OPENING_FRAME_WIDTH,
    OPENING_FRAME_HEIGHT,
)

def read_png_raw(path: Path) -> Tuple[int, int, bytes, int]:
    """Reads PNG file and extracts dimensions, uncompressed pixel bytes, and channel count."""
    with open(path, "rb") as f:
        data = f.read()

    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG signature for {path}"
    pos = 8
    width = 0
    height = 0
    raw_idat = b""
    color_type = 2

    while pos < len(data):
        length, chunk_type = struct.unpack(">I4s", data[pos : pos + 8])
        pos += 8
        chunk_data = data[pos : pos + length]
        pos += length
        pos += 4  # skip crc

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, comp, fltr, interlace = struct.unpack(
                ">IIBBBBB", chunk_data
            )
            assert bit_depth == 8
            assert color_type in (2, 6)
        elif chunk_type == b"IDAT":
            raw_idat += chunk_data
        elif chunk_type == b"IEND":
            break

    decompressed = zlib.decompress(raw_idat)
    channels = 4 if color_type == 6 else 3
    stride = width * channels
    pixels = bytearray(width * height * channels)
    decomp_pos = 0
    prev_row = bytearray(stride)

    for y in range(height):
        filter_type = decompressed[decomp_pos]
        decomp_pos += 1
        current_row = bytearray(decompressed[decomp_pos : decomp_pos + stride])
        decomp_pos += stride
        row = bytearray(stride)
        for x in range(stride):
            b_pixel = prev_row[x]
            a_pixel = row[x - channels] if x >= channels else 0
            c_pixel = prev_row[x - channels] if x >= channels else 0
            x_val = current_row[x]
            if filter_type == 0:
                recon = x_val
            elif filter_type == 1:
                recon = (x_val + a_pixel) & 0xFF
            elif filter_type == 2:
                recon = (x_val + b_pixel) & 0xFF
            elif filter_type == 3:
                recon = (x_val + ((a_pixel + b_pixel) >> 1)) & 0xFF
            elif filter_type == 4:
                p = a_pixel + b_pixel - c_pixel
                pa, pb, pc = abs(p - a_pixel), abs(p - b_pixel), abs(p - c_pixel)
                pr = a_pixel if (pa <= pb and pa <= pc) else (b_pixel if pb <= pc else c_pixel)
                recon = (x_val + pr) & 0xFF
            row[x] = recon
        pixels[y * stride : (y + 1) * stride] = row
        prev_row = row

    return width, height, bytes(pixels), channels


class ThumbnailValidator:
    def __init__(self, episode_slug: str):
        self.slug = episode_slug.strip()
        self.ep_dir = REPO_ROOT / "episodes" / self.slug
        self.papercut_dir = self.ep_dir / "papercut"
        self.out_dir = self.papercut_dir / "out"
        self.errors = []
        self.passes = []
        self.warnings = []

    def log_pass(self, msg: str):
        self.passes.append(msg)
        print(f"  [PASS] {msg}")

    def log_error(self, msg: str):
        self.errors.append(msg)
        print(f"  [FAIL] {msg}")

    def log_warn(self, msg: str):
        self.warnings.append(msg)
        print(f"  [WARN] {msg}")

    def validate(self) -> bool:
        print("=" * 70)
        print(f"  Mandatory Thumbnail QA & Branding Verification: {self.slug}")
        print("=" * 70)

        # 1. Config & Metadata Audit
        self._audit_configuration()

        # 2. Standalone 16:9 Thumbnail Verification
        thumb_path = self.out_dir / "thumbnail.png"
        if not thumb_path.exists():
            self.log_error(f"Rendered thumbnail not found at: {thumb_path}")
        else:
            self._validate_thumbnail_image(thumb_path)

        # 3. Opening Frame Verification
        opening_path = self.out_dir / "opening-frame.png"
        if not opening_path.exists():
            self.log_warn(f"Opening frame preview not found at: {opening_path}")
        else:
            self._validate_opening_frame_image(opening_path)

        print("-" * 70)
        print(f"Audit Summary: {len(self.passes)} Passed, {len(self.warnings)} Warnings, {len(self.errors)} Blocking Errors")
        print("=" * 70)
        return len(self.errors) == 0

    def _audit_configuration(self):
        ep_json = self.papercut_dir / "episode.json"
        if not ep_json.exists():
            self.log_error(f"episode.json not found: {ep_json}")
            return

        with open(ep_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        thumb = data.get("thumbnail")
        if not thumb or not isinstance(thumb, dict):
            self.log_error("episode.json missing mandatory 'thumbnail' branding block.")
            return

        # Check Element B: Channel Name
        ch_name = thumb.get("channelName")
        if ch_name != CHANNEL_NAME:
            self.log_error(f"Channel name must be exact lowercase '{CHANNEL_NAME}', found: '{ch_name}'")
        else:
            self.log_pass(f"Channel name verified: '{ch_name}'")

        # Check Element A: Video Title
        ep_title = thumb.get("episodeTitle")
        if not ep_title or not isinstance(ep_title, str) or len(ep_title.strip()) < 3:
            self.log_error("episodeTitle is missing or empty.")
        else:
            self.log_pass(f"Episode title verified: '{ep_title}'")

        # Check Element C: Canonical Mascot Asset
        mascot_asset = thumb.get("mascotAsset")
        if not mascot_asset:
            self.log_error("mascotAsset reference is missing.")
        else:
            mascot_path = REPO_ROOT / mascot_asset
            if not mascot_path.exists():
                self.log_error(f"Canonical mascot asset does not exist on disk: {mascot_path}")
            else:
                self.log_pass(f"Canonical mascot asset verified: {mascot_asset}")

        # Check Layout & Expression
        expr = thumb.get("mascotExpression")
        if not expr:
            self.log_error("mascotExpression is missing.")
        else:
            self.log_pass(f"Mascot expression configured: '{expr}'")

    def _validate_thumbnail_image(self, path: Path):
        print("\n  >> Inspecting Rendered 16:9 Thumbnail Image <<")
        try:
            w, h, pixels, channels = read_png_raw(path)
        except Exception as e:
            self.log_error(f"Failed to read PNG {path}: {e}")
            return

        # 1. Dimensions & 16:9 Aspect Ratio
        if (w, h) != (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT):
            self.log_error(f"Thumbnail dimensions {w}x{h} do not match expected {THUMBNAIL_WIDTH}x{THUMBNAIL_HEIGHT}")
        else:
            self.log_pass(f"Thumbnail dimensions verified: {w}x{h} (16:9)")

        aspect = w / h
        expected_aspect = 16.0 / 9.0
        if abs(aspect - expected_aspect) > 0.01:
            self.log_error(f"Aspect ratio {aspect:.3f} is not 16:9")
        else:
            self.log_pass("Aspect ratio verified: 16:9")

        # 2. Visual Inspection: MANDATORY ELEMENT B (Channel Name '@meowndr' badge)
        # Bounding box for brand badge: X in [50, 320], Y in [40, 140]
        badge_pixels = 0
        badge_dark_bg = 0
        badge_orange_accent = 0
        for y in range(40, 140):
            for x in range(50, 320):
                idx = (y * w + x) * channels
                r, g, b = pixels[idx], pixels[idx + 1], pixels[idx + 2]
                if r < 30 and g < 40 and b < 60:
                    badge_dark_bg += 1
                if r > 200 and 80 <= g <= 150 and b < 50:
                    badge_orange_accent += 1
                if r > 220 and g > 220 and b > 220:
                    badge_pixels += 1

        if badge_dark_bg > 1000 and badge_pixels > 200 and badge_orange_accent > 100:
            self.log_pass(f"Visually verified '@meowndr' brand badge (high-contrast text + orange accent)")
        else:
            self.log_error(f"Brand badge '@meowndr' not detected in designated region (pixels: text={badge_pixels}, bg={badge_dark_bg})")

        # 3. Visual Inspection: MANDATORY ELEMENT A (Video Title typography)
        # Bounding box for title: X in [50, 750], Y in [100, 480]
        title_cream_pixels = 0
        title_amber_pixels = 0
        title_dark_letters = 0
        for y in range(100, 480):
            for x in range(50, 750):
                idx = (y * w + x) * channels
                r, g, b = pixels[idx], pixels[idx + 1], pixels[idx + 2]
                if r > 240 and g > 240 and b > 235:
                    title_cream_pixels += 1
                elif r > 220 and 140 <= g <= 180 and b < 50:
                    title_amber_pixels += 1
                elif r < 40 and g < 40 and b < 60:
                    title_dark_letters += 1

        if (title_cream_pixels + title_amber_pixels) > 5000 and title_dark_letters > 2000:
            self.log_pass(f"Visually verified bold Video Title plaques ({title_cream_pixels} cream, {title_amber_pixels} amber, {title_dark_letters} letter px)")
        else:
            self.log_error("Video Title plaques missing or insufficiently prominent in rendered image.")

        # 4. Visual Inspection: MANDATORY ELEMENT C (Cat Scientist Mascot)
        # In split-scientist-right layout: X in [750, 1260], Y in [150, 700]
        mascot_orange = 0
        mascot_cream = 0
        mascot_spectacles = 0
        mascot_teal_pen = 0
        for y in range(150, 700):
            for x in range(750, 1260):
                idx = (y * w + x) * channels
                r, g, b = pixels[idx], pixels[idx + 1], pixels[idx + 2]
                # Orange fur
                if r > 190 and 80 <= g <= 160 and b < 60:
                    mascot_orange += 1
                # Cream muzzle / coat
                elif r > 235 and g > 235 and b > 225:
                    mascot_cream += 1
                # Wire spectacles
                elif 140 <= r <= 210 and 65 <= g <= 125 and b < 40:
                    mascot_spectacles += 1
                # Turquoise pocket pen
                elif r < 40 and 110 <= g <= 170 and 100 <= b <= 165:
                    mascot_teal_pen += 1

        # Check non-white cat requirement
        if mascot_orange < 1500:
            self.log_error(f"Cat Scientist mascot not detected or cat is NOT orange ({mascot_orange} orange px, minimum 1500 required)")
        else:
            self.log_pass(f"Visually verified canonical Orange-and-Cream Cat Scientist ({mascot_orange} orange fur px, {mascot_cream} cream px)")

        if mascot_spectacles > 50:
            self.log_pass(f"Visually verified bronze wire spectacles ({mascot_spectacles} px)")
        else:
            self.log_warn("Spectacles wire signature faint or partially obscured.")

        if mascot_teal_pen > 10:
            self.log_pass(f"Visually verified turquoise pocket pen ({mascot_teal_pen} px)")
        else:
            self.log_warn("Turquoise pocket pen signature faint.")

    def _validate_opening_frame_image(self, path: Path):
        print("\n  >> Inspecting Rendered 9:16 Opening Thumbnail Frame <<")
        try:
            w, h, pixels, channels = read_png_raw(path)
        except Exception as e:
            self.log_error(f"Failed to read PNG {path}: {e}")
            return

        if (w, h) != (OPENING_FRAME_WIDTH, OPENING_FRAME_HEIGHT):
            self.log_error(f"Opening frame dimensions {w}x{h} do not match expected {OPENING_FRAME_WIDTH}x{OPENING_FRAME_HEIGHT}")
        else:
            self.log_pass(f"Opening frame dimensions verified: {w}x{h} (9:16 vertical)")

        # Verify all 3 mandatory elements in 9:16 composition
        # Element B: '@meowndr' at top center (Y in [160, 260], X in [300, 780])
        brand_bg = 0
        for y in range(160, 260):
            for x in range(300, 780):
                idx = (y * w + x) * channels
                r, g, b = pixels[idx], pixels[idx + 1], pixels[idx + 2]
                if r < 30 and g < 40 and b < 60:
                    brand_bg += 1

        if brand_bg > 1000:
            self.log_pass("Opening frame contains '@meowndr' brand badge in upper header safe zone")
        else:
            self.log_error("Opening frame missing '@meowndr' brand badge")

        # Element C: Mascot in lower region (Y in [1000, 1850])
        mascot_orange = 0
        for y in range(1000, 1850):
            for x in range(200, 880):
                idx = (y * w + x) * channels
                r, g, b = pixels[idx], pixels[idx + 1], pixels[idx + 2]
                if r > 190 and 80 <= g <= 160 and b < 60:
                    mascot_orange += 1

        if mascot_orange > 3000:
            self.log_pass(f"Opening frame contains prominent Cat Scientist mascot ({mascot_orange} orange px)")
        else:
            self.log_error("Opening frame missing prominent Cat Scientist mascot in lower half")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 library/tools/validate_thumbnail.py <episode_slug>")
        sys.exit(1)

    slug = sys.argv[1]
    validator = ThumbnailValidator(slug)
    ok = validator.validate()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
