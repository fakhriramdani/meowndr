#!/usr/bin/env python3
"""
Unit tests for papercraft asset loader and validation logic.
Tests validation of:
- Missing files
- Corrupt / invalid metadata
- Incompatible image dimensions
- Floor line and presenter zone boundaries
- Successful valid assets
"""

import os
import sys
import unittest
import tempfile
import json
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from asset_loader import (
    read_image_dimensions,
    validate_environment,
    validate_presenter_placement,
    SAFE_ZONES,
)


class TestAssetLoader(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_dummy_png(self, path: str, width: int = 1080, height: int = 1920):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Construct minimal valid PNG header with IHDR
        sig = b"\x89PNG\r\n\x1a\n"
        ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        ihdr_chunk = struct.pack(">I", len(ihdr_data)) + b"IHDR" + ihdr_data + b"\x00\x00\x00\x00"
        with open(path, "wb") as f:
            f.write(sig + ihdr_chunk)

    def test_read_image_dimensions_valid_png(self):
        png_path = os.path.join(self.root, "test.png")
        self.create_dummy_png(png_path, 1080, 1920)
        w, h, fmt = read_image_dimensions(png_path)
        self.assertEqual(w, 1080)
        self.assertEqual(h, 1920)
        self.assertEqual(fmt, "PNG")

    def test_missing_image_file_raises_error(self):
        env = {
            "id": "missing-env",
            "name": "Missing Env",
            "dimensions": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
            "floor_y": 1380,
            "presenter_zone": {"x_range": [200, 800], "y_range": [900, 1700]},
            "path": "assets/does_not_exist.png",
        }
        res = validate_environment(env, self.root)
        self.assertFalse(res["valid"])
        self.assertTrue(any("does not exist" in e for e in res["errors"]))

    def test_incompatible_image_dimensions(self):
        png_path = os.path.join(self.root, "bad_dim.png")
        self.create_dummy_png(png_path, 800, 600)  # Landscape / wrong resolution
        env = {
            "id": "bad-dim-env",
            "name": "Bad Dimensions",
            "dimensions": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
            "floor_y": 1380,
            "presenter_zone": {"x_range": [200, 800], "y_range": [900, 1700]},
            "path": "bad_dim.png",
        }
        res = validate_environment(env, self.root)
        self.assertFalse(res["valid"])
        self.assertTrue(any("dimensions (800x600) do not match" in e for e in res["errors"]))

    def test_invalid_metadata_missing_fields(self):
        env = {"id": "incomplete"}
        res = validate_environment(env, self.root)
        self.assertFalse(res["valid"])
        self.assertTrue(any("name" in e for e in res["errors"]))
        self.assertTrue(any("dimensions" in e for e in res["errors"]))
        self.assertTrue(any("floor_y" in e for e in res["errors"]))
        self.assertTrue(any("presenter_zone" in e for e in res["errors"]))

    def test_invalid_presenter_zone_bounds(self):
        png_path = os.path.join(self.root, "ok.png")
        self.create_dummy_png(png_path, 1080, 1920)

        # x_range backwards
        env = {
            "id": "bad-zone",
            "name": "Bad Zone",
            "dimensions": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
            "floor_y": 1380,
            "presenter_zone": {"x_range": [800, 200], "y_range": [900, 1700]},
            "path": "ok.png",
        }
        res = validate_environment(env, self.root)
        self.assertFalse(res["valid"])
        self.assertTrue(any("min_x < max_x" in e for e in res["errors"]))

    def test_floor_y_outside_range(self):
        png_path = os.path.join(self.root, "ok.png")
        self.create_dummy_png(png_path, 1080, 1920)

        # Floor y too high (e.g., 500 near the top)
        env = {
            "id": "bad-floor",
            "name": "Bad Floor",
            "dimensions": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
            "floor_y": 500,
            "presenter_zone": {"x_range": [200, 800], "y_range": [400, 800]},
            "path": "ok.png",
        }
        res = validate_environment(env, self.root)
        self.assertFalse(res["valid"])
        self.assertTrue(any("floor_y (500) is outside valid vertical range" in e for e in res["errors"]))

    def test_validate_presenter_placement(self):
        env = {
            "floor_y": 1380,
            "presenter_zone": {"x_range": [240, 840], "y_range": [900, 1750]},
        }
        # Centered on floor: valid
        valid, reason = validate_presenter_placement(env, 540, 1380)
        self.assertTrue(valid)
        self.assertIsNone(reason)

        # Off floor: invalid
        valid, reason = validate_presenter_placement(env, 540, 1000)
        self.assertFalse(valid)
        self.assertIn("floor_y", reason)

        # Out of bounds horizontal: invalid
        valid, reason = validate_presenter_placement(env, 100, 1380)
        self.assertFalse(valid)
        self.assertIn("horizontal bounds", reason)


if __name__ == "__main__":
    unittest.main()
