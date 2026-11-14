"""
Shared Brand Configuration & Constants for Papercraft Content Factory.
Canonical Brand: @meowndr (Exact spelling)
Canonical Mascot: Orange-and-cream Cat Scientist in cream paper lab coat with wire spectacles.
"""

from pathlib import Path
from typing import Dict, Any, List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# 1. Mandatory Brand Constants
CHANNEL_NAME = "@meowndr"
CANONICAL_MASCOT_REL_PATH = "assets/brand/cat-scientist-avatar-transparent.png"
CANONICAL_MASCOT_FULL_PATH = REPO_ROOT / CANONICAL_MASCOT_REL_PATH

# 2. Persistent Video Watermark Configuration
WATERMARK_CONFIG = {
    "enabled": True,
    "text": "@meowndr",
    "position": "top-right",
    "opacity": 0.85,
    "scale": 1.0,
    "safe_margin": {
        "top": 60,
        "right": 50,
        "bottom": 80,
        "left": 50,
    },
}

# 3. Brand Color Palette (Layered Papercraft)
BRAND_PALETTE = {
    "channel_tag_bg": "#0F172A",      # Deep midnight slate cardstock
    "channel_tag_text": "#F8FAFC",    # Crisp cardstock white
    "channel_tag_accent": "#F97316",  # Signature warm orange
    "mascot_orange": "#F97316",       # Primary cat fur
    "mascot_orange_shade": "#EA580C", # Shadowed fur fold
    "mascot_cream": "#FFFDF7",        # Muzzle, chest bib, paws
    "mascot_pink": "#FB7185",         # Nose, inner ear folds
    "mascot_lab_coat": "#FAF8F5",     # Cream paper lab coat
    "mascot_spectacles": "#B45309",   # Bronze/amber wire spectacles
    "mascot_pen_teal": "#0D9488",     # Turquoise pocket pen
    "title_card_bg": "#FFFDF7",       # Warm cream title plaque
    "title_text_primary": "#0F172A",  # Deep navy cardstock letters
    "title_text_hot": "#F59E0B",      # Vibrant amber highlighted keyword
    "hook_pill_bg": "#F59E0B",        # Curiosity hook pill
    "hook_pill_text": "#0F172A",
}

# 4. Standard Dimensions
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720
THUMBNAIL_ASPECT_RATIO = "16:9"

OPENING_FRAME_WIDTH = 1080
OPENING_FRAME_HEIGHT = 1920
OPENING_FRAME_ASPECT_RATIO = "9:16"
OPENING_FRAME_DEFAULT_DURATION_SEC = 1.0
OPENING_FRAME_DEFAULT_DURATION_FRAMES = 30


def get_default_thumbnail_config(episode_meta: Dict[str, Any]) -> Dict[str, Any]:
    """Generates standard compliant thumbnail config from episode metadata."""
    title = episode_meta.get("title", "").strip()
    topic = episode_meta.get("topic", "").strip()
    return {
        "channelName": CHANNEL_NAME,
        "mascotAsset": CANONICAL_MASCOT_REL_PATH,
        "episodeTitle": title,
        "thumbnailHook": f"Fakta Unik {topic}" if topic else "Sains di Balik Fenomena",
        "mainSubject": topic or title,
        "mascotExpression": "curious",
        "layoutPreset": "split-scientist-right",
        "width": THUMBNAIL_WIDTH,
        "height": THUMBNAIL_HEIGHT,
        "openingFrameDurationSeconds": OPENING_FRAME_DEFAULT_DURATION_SEC,
        "openingFrameDurationFrames": OPENING_FRAME_DEFAULT_DURATION_FRAMES,
    }


def validate_thumbnail_config(cfg: Dict[str, Any]) -> List[str]:
    """Validates that a thumbnail config strictly complies with mandatory branding rules."""
    errors = []

    # Check channelName
    ch = cfg.get("channelName")
    if ch != CHANNEL_NAME:
        errors.append(f"Invalid channelName: '{ch}'. Mandatory channel name must be exactly '{CHANNEL_NAME}'.")

    # Check title
    title = cfg.get("episodeTitle")
    if not title or not isinstance(title, str) or not title.strip():
        errors.append("Mandatory 'episodeTitle' is missing or empty.")

    # Check mascot asset
    asset = cfg.get("mascotAsset")
    if not asset or not isinstance(asset, str):
        errors.append("Mandatory 'mascotAsset' reference is missing.")
    else:
        disk_path = REPO_ROOT / asset
        if not disk_path.exists():
            errors.append(f"Mascot asset does not exist on disk: {disk_path}")

    # Check dimensions
    w = cfg.get("width", THUMBNAIL_WIDTH)
    h = cfg.get("height", THUMBNAIL_HEIGHT)
    if (w, h) != (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT):
        errors.append(f"Invalid thumbnail dimensions: {w}x{h}. Expected {THUMBNAIL_WIDTH}x{THUMBNAIL_HEIGHT} (16:9).")

    return errors
