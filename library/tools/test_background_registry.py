#!/usr/bin/env python3
"""
Comprehensive Unit & Integration Test Suite for Centralized Background Registry.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from background_registry import (
    BackgroundRegistry,
    read_image_dimensions,
    FRAME_WIDTH,
    FRAME_HEIGHT,
)


class TestBackgroundRegistry(unittest.TestCase):
    def setUp(self):
        # We work with an isolated copy of registry in a temp file or the real repo
        self.repo_root = REPO_ROOT
        self.real_registry = BackgroundRegistry(repo_root=self.repo_root)

    def test_01_loaded_backgrounds_count_and_types(self):
        """Verify the 24 initial backgrounds are loaded with required schema fields."""
        bgs = self.real_registry.list_backgrounds()
        self.assertGreaterEqual(len(bgs), 24, "Registry must contain at least 24 initial backgrounds.")

        required_fields = [
            "id", "name", "category", "description", "assetPath",
            "aspectRatio", "dimensions", "format", "hasTransparency",
            "tags", "status", "floorY", "mood", "createdAt"
        ]
        for b in bgs:
            for field in required_fields:
                self.assertIn(field, b, f"Background '{b.get('id')}' missing required field: {field}")
            self.assertEqual(b["dimensions"]["width"], 1080)
            self.assertEqual(b["dimensions"]["height"], 1920)
            self.assertEqual(b["aspectRatio"], "9:16")
            self.assertTrue(b["exists_on_disk"], f"Background asset must exist on disk: {b['assetPath']}")

    def test_02_listing_filters(self):
        """Verify filtering by category, status, query, and tag."""
        # Category filter
        stem_bgs = self.real_registry.list_backgrounds(category="STEM")
        self.assertTrue(len(stem_bgs) > 0)
        for b in stem_bgs:
            self.assertIn("STEM", b["category"])

        # Status filter
        active_bgs = self.real_registry.list_backgrounds(status="active")
        self.assertEqual(len(active_bgs), len(self.real_registry.data["backgrounds"]))

        # Query filter
        lab_bgs = self.real_registry.list_backgrounds(query="laboratory")
        self.assertTrue(len(lab_bgs) > 0)

        # Tag filter
        indoor_bgs = self.real_registry.list_backgrounds(tag="indoor")
        self.assertTrue(len(indoor_bgs) > 0)

    def test_03_get_background(self):
        """Verify retrieval by ID."""
        bg = self.real_registry.get_background("science-lab")
        self.assertIsNotNone(bg)
        self.assertEqual(bg["id"], "science-lab")
        self.assertEqual(bg["name"], "Science Laboratory")

        none_bg = self.real_registry.get_background("non-existent-id-12345")
        self.assertIsNone(none_bg)

    def test_04_episode_reference_detection(self):
        """Verify that active references in episodes are detected accurately."""
        refs = self.real_registry.find_active_references("science-lab")
        self.assertIn("science-lab", refs)
        episodes_using = [r["episode"] for r in refs["science-lab"]]
        self.assertIn("01-anomali-air", episodes_using)

    def test_05_dimension_reader_validation(self):
        """Verify read_image_dimensions on real background and error on invalid files."""
        img_path = os.path.join(self.repo_root, "assets", "backgrounds", "science-lab", "background.png")
        w, h, fmt = read_image_dimensions(img_path)
        self.assertEqual(w, 1080)
        self.assertEqual(h, 1920)
        self.assertEqual(fmt, "PNG")

        with self.assertRaises(FileNotFoundError):
            read_image_dimensions("/non/existent/path/image.png")

    def test_06_add_background_dimension_rejection(self):
        """Verify that add_background rejects non-1080x1920 images."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create a 500x500 mock image file
            bad_img = os.path.join(temp_dir, "bad.png")
            # Minimal 100x100 PNG header
            import struct
            png_header = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + struct.pack(">II", 500, 500) + b"\x08\x02\x00\x00\x00"
            with open(bad_img, "wb") as f:
                f.write(png_header + b"\x00" * 100)

            with self.assertRaises(ValueError) as ctx:
                self.real_registry.add_background(
                    image_path=bad_img,
                    bg_id="test-bad-dim",
                    name="Test Bad Dim",
                    skip_sync=True,
                )
            self.assertIn("1080x1920", str(ctx.exception))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_07_add_remove_disable_lifecycle(self):
        """Verify full lifecycle: add test background -> disable -> archive -> re-enable -> protected removal -> force removal."""
        temp_dir = tempfile.mkdtemp()
        test_id = "test-automated-env-999"
        try:
            # Create a mock valid 1080x1920 PNG file
            mock_img = os.path.join(temp_dir, "valid.png")
            # Copy real background to serve as mock
            src_sample = os.path.join(self.repo_root, "assets", "backgrounds", "science-lab", "background.png")
            shutil.copy2(src_sample, mock_img)

            # 1. Add background
            res = self.real_registry.add_background(
                image_path=mock_img,
                bg_id=test_id,
                name="Automated Test Environment",
                category="Testing / Quality",
                description="Temporary environment for automated unit testing.",
                tags=["testing", "automated", "qa"],
                skip_preview=True,
                skip_sync=True,
            )
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["id"], test_id)

            # Verify presence in registry
            added = self.real_registry.get_background(test_id)
            self.assertIsNotNone(added)
            self.assertEqual(added["status"], "active")

            # 2. Disable background
            dis_res = self.real_registry.disable_background(test_id, reason="Maintenance testing", skip_sync=True)
            self.assertEqual(dis_res["new_status"], "disabled")
            self.assertEqual(self.real_registry.get_background(test_id)["status"], "disabled")

            # 3. Archive background
            arc_res = self.real_registry.archive_background(test_id, reason="Archival test", skip_sync=True)
            self.assertEqual(arc_res["new_status"], "archived")
            self.assertEqual(self.real_registry.get_background(test_id)["status"], "archived")

            # 4. Re-enable background
            en_res = self.real_registry.enable_background(test_id, skip_sync=True)
            self.assertEqual(en_res["new_status"], "active")
            self.assertEqual(self.real_registry.get_background(test_id)["status"], "active")

            # 5. Remove background (unreferenced, so should succeed without force)
            rem_res = self.real_registry.remove_background(test_id, force=False, delete_asset=True, skip_sync=True)
            self.assertTrue(rem_res["removed_from_registry"])
            self.assertIsNone(self.real_registry.get_background(test_id))

        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            # Ensure test_id is removed if test failed mid-way
            if self.real_registry.get_background(test_id):
                self.real_registry.remove_background(test_id, force=True, delete_asset=True, skip_sync=True)

    def test_08_safe_removal_blocks_referenced_background(self):
        """Verify that attempting to remove an actively referenced background raises ValueError."""
        # science-lab is referenced in 01-anomali-air
        with self.assertRaises(ValueError) as ctx:
            self.real_registry.remove_background("science-lab", force=False, skip_sync=True)
        self.assertIn("Cannot remove background 'science-lab'", str(ctx.exception))
        self.assertIn("01-anomali-air", str(ctx.exception))
        self.assertIn("disable", str(ctx.exception))

    def test_09_discovery_and_diagnostics(self):
        """Verify that discovery accurately detects assets on disk."""
        disc = self.real_registry.discover_backgrounds()
        self.assertEqual(disc["total_registered"], len(self.real_registry.data["backgrounds"]))
        self.assertEqual(len(disc["duplicate_ids"]), 0)
        self.assertEqual(len(disc["missing_on_disk"]), 0)

    def test_10_validation_detects_unregistered_references(self):
        """Verify that validate_registry catches unregistered background references (e.g., physics-lab)."""
        val = self.real_registry.validate_registry(check_episodes=True)
        # mystery-sailing-stones references physics-lab which is currently unregistered
        has_physics_error = any("physics-lab" in err for err in val["errors"])
        self.assertTrue(has_physics_error, "validate_registry must report unregistered 'physics-lab'.")


if __name__ == "__main__":
    unittest.main()
