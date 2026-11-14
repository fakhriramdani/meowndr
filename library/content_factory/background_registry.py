"""
Background Registry Interface for Papercraft Content Factory.
Re-exports BackgroundRegistry and convenience functions.
"""

import sys
import os
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(os.path.dirname(HERE), "tools")
TARGET_PATH = os.path.join(TOOLS_DIR, "background_registry.py")

spec = importlib.util.spec_from_file_location("tools_background_registry", TARGET_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BackgroundRegistry = mod.BackgroundRegistry
get_registry = mod.get_registry
read_image_dimensions = mod.read_image_dimensions
find_repo_root = mod.find_repo_root
FRAME_WIDTH = mod.FRAME_WIDTH
FRAME_HEIGHT = mod.FRAME_HEIGHT
VALID_STATUSES = mod.VALID_STATUSES
SUPPORTED_FORMATS = mod.SUPPORTED_FORMATS

__all__ = [
    "BackgroundRegistry",
    "get_registry",
    "read_image_dimensions",
    "find_repo_root",
    "FRAME_WIDTH",
    "FRAME_HEIGHT",
    "VALID_STATUSES",
    "SUPPORTED_FORMATS",
]
