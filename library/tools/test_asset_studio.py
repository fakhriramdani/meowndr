#!/usr/bin/env python3
"""
Comprehensive Unit & Integration Test Suite for @meowndr Asset Studio.
"""

import os
import sys
import json
import shutil
import tempfile
import threading
import urllib.request
import unittest
from http.server import HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from asset_studio_service import AssetStudioService
from asset_studio_server import AssetStudioHandler


class TestAssetStudioService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = REPO_ROOT
        cls.service = AssetStudioService(repo_root=cls.repo_root)

    def test_01_overview_metrics(self):
        """Verify overview statistics accurately count all real project assets."""
        ov = self.service.get_overview()
        self.assertIn("total_assets", ov)
        self.assertGreaterEqual(ov["total_assets"], 60)
        self.assertEqual(ov["backgrounds"]["total"], 24)
        self.assertEqual(ov["backgrounds"]["active"], 24)
        self.assertEqual(ov["characters"]["total"], 2)
        self.assertEqual(ov["props"]["total"], 16)
        self.assertGreaterEqual(ov["other_assets"]["brand"], 10)
        self.assertGreaterEqual(ov["collections_count"], 5)
        self.assertIn("diagnostics", ov)
        self.assertIn("episode_references_count", ov)

    def test_02_background_listing_and_filtering(self):
        """Verify background listing and filtering by category and status."""
        all_bgs = self.service.list_backgrounds()
        self.assertEqual(len(all_bgs), 24)

        stem_bgs = self.service.list_backgrounds(category="STEM")
        self.assertTrue(len(stem_bgs) > 0)
        for b in stem_bgs:
            self.assertIn("STEM", b["category"])

        active_bgs = self.service.list_backgrounds(status="active")
        self.assertEqual(len(active_bgs), 24)

    def test_03_background_metadata_update(self):
        """Verify editing metadata updates the registry and preserves disk consistency."""
        target_id = "science-lab"
        orig = self.service.get_background(target_id)
        orig_desc = orig.get("description")

        try:
            new_desc = orig_desc + " [Verified by Asset Studio QA]"
            res = self.service.update_background(target_id, {"description": new_desc, "mood": "studious & vibrant"})
            self.assertEqual(res["status"], "success")

            updated = self.service.get_background(target_id)
            self.assertEqual(updated["description"], new_desc)
            self.assertEqual(updated["mood"], "studious & vibrant")
        finally:
            # Restore original
            self.service.update_background(target_id, {"description": orig_desc, "mood": orig.get("mood", "cool / studious")})

    def test_04_character_listing_and_avatar_variants(self):
        """Verify character details, avatar variants, and controllable states."""
        chars = self.service.list_characters()
        self.assertEqual(len(chars), 2)

        cat = next((c for c in chars if c["id"] == "cat-scientist"), None)
        self.assertIsNotNone(cat)
        self.assertEqual(cat["name"], "Cat Scientist Mascot")
        self.assertEqual(cat["primary_color"], "#F97316")
        self.assertGreaterEqual(len(cat["variants"]), 4)
        self.assertIn("idle", cat["states"])
        self.assertIn("explaining", cat["states"])

    def test_05_character_variant_crud(self):
        """Verify adding and removing a character variant."""
        temp_dir = tempfile.mkdtemp()
        test_var_id = "test-custom-pose"
        try:
            # Create mock variant image
            src_avatar = os.path.join(self.repo_root, "assets", "brand", "cat-scientist-avatar-primary.png")
            mock_img = os.path.join(temp_dir, "custom_pose.png")
            shutil.copy2(src_avatar, mock_img)

            # Add variant
            res = self.service.add_character_variant("cat-scientist", test_var_id, mock_img)
            self.assertEqual(res["status"], "success")

            # Verify it shows up in character variants
            cat = self.service.get_character("cat-scientist")
            var_ids = [v["id"] for v in cat["variants"]]
            self.assertTrue(any(test_var_id in vid for vid in var_ids))

            # Remove variant
            rem_res = self.service.remove_character_variant("cat-scientist", test_var_id)
            self.assertEqual(rem_res["status"], "success")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_06_prop_crud_and_metadata(self):
        """Verify prop addition, listing, and safe deletion."""
        test_prop_id = "test-studio-spectrometer"
        try:
            res = self.service.add_prop(
                prop_id=test_prop_id,
                name="Papercraft Spectrometer",
                description="Diffraction prism spectrometer for optical analysis.",
                width=160,
                height=140,
                anchor="bottom-center",
                supports_floor=True,
                supports_hand=True,
            )
            self.assertEqual(res["status"], "success")

            # Check presence
            p = self.service.get_prop(test_prop_id)
            self.assertIsNotNone(p)
            self.assertEqual(p["name"], "Papercraft Spectrometer")

            # Delete prop
            del_res = self.service.remove_prop(test_prop_id, force=False, delete_asset=True)
            self.assertEqual(del_res["status"], "success")
            self.assertIsNone(self.service.get_prop(test_prop_id))
        finally:
            p_dir = os.path.join(self.repo_root, "assets", "props", test_prop_id)
            if os.path.isdir(p_dir):
                shutil.rmtree(p_dir, ignore_errors=True)

    def test_07_collections_crud(self):
        """Verify collection creation, updating, and deletion."""
        test_coll_id = "test-studio-collection"
        try:
            res = self.service.create_collection(
                coll_id=test_coll_id,
                name="Test Studio Collection",
                description="Temporary collection for testing.",
                category="Testing",
                asset_ids=["science-lab", "cat-scientist"],
            )
            self.assertEqual(res["status"], "success")

            # Verify presence
            colls = self.service.list_collections()
            target = next((c for c in colls if c["id"] == test_coll_id), None)
            self.assertIsNotNone(target)
            self.assertEqual(len(target["assetIds"]), 2)

            # Update
            upd = self.service.update_collection(test_coll_id, {"description": "Updated description"})
            self.assertEqual(upd["collection"]["description"], "Updated description")

            # Delete
            del_res = self.service.delete_collection(test_coll_id)
            self.assertEqual(del_res["status"], "success")
        finally:
            colls = self.service.list_collections()
            if any(c["id"] == test_coll_id for c in colls):
                self.service.delete_collection(test_coll_id)

    def test_08_path_traversal_protection(self):
        """Verify resolve_safe_path prevents path traversal attacks."""
        with self.assertRaises(PermissionError):
            self.service.resolve_safe_path("../../../etc/passwd")

        with self.assertRaises(PermissionError):
            self.service.resolve_safe_path("/etc/shadow")

        # Allowed paths should succeed
        safe = self.service.resolve_safe_path("assets/backgrounds/science-lab/background.png")
        self.assertTrue(os.path.isfile(safe))

    def test_09_safe_deletion_blocking(self):
        """Verify that attempting to remove an asset referenced in episodes raises ValueError."""
        # science-lab is used in 01-anomali-air
        with self.assertRaises(ValueError) as ctx:
            self.service.remove_background("science-lab", force=False)
        self.assertIn("Cannot remove background 'science-lab'", str(ctx.exception))
        self.assertIn("01-anomali-air", str(ctx.exception))

    def test_10_validation_diagnostics(self):
        """Verify comprehensive validation catches issues across assets."""
        val = self.service.validate_all()
        self.assertIn("is_valid", val)
        self.assertIn("issues", val)
        self.assertIn("stats", val)
        self.assertGreaterEqual(val["stats"]["total_issues"], 1)


class TestAssetStudioHttpServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = REPO_ROOT
        # Pick an ephemeral test port
        cls.port = 4567
        cls.server = HTTPServer(("127.0.0.1", cls.port), AssetStudioHandler)
        cls.server.repo_root = cls.repo_root
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_11_http_overview_endpoint(self):
        """Verify GET /api/overview returns 200 with valid JSON structure."""
        url = f"http://127.0.0.1:{self.port}/api/overview"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("total_assets", data)
            self.assertEqual(data["backgrounds"]["total"], 24)

    def test_12_http_backgrounds_endpoint(self):
        """Verify GET /api/backgrounds returns 200 and list of backgrounds."""
        url = f"http://127.0.0.1:{self.port}/api/backgrounds"
        with urllib.request.urlopen(url, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(len(data), 24)

    def test_13_http_static_ui_serving(self):
        """Verify UI files (index.html, app.css, app.js) are served properly."""
        for path, mime in [
            ("/", "text/html"),
            ("/app.css", "text/css"),
            ("/app.js", "application/javascript"),
        ]:
            url = f"http://127.0.0.1:{self.port}{path}"
            with urllib.request.urlopen(url, timeout=3) as resp:
                self.assertEqual(resp.status, 200)
                content_type = resp.headers.get("Content-Type", "")
                self.assertIn(mime, content_type)
                body = resp.read()
                self.assertGreater(len(body), 50)

    def test_14_http_static_asset_serving_and_security(self):
        """Verify image asset serving and 403 on traversal attempt."""
        # Valid asset
        url = f"http://127.0.0.1:{self.port}/assets/backgrounds/science-lab/background.png"
        with urllib.request.urlopen(url, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get("Content-Type"), "image/png")
            content = resp.read()
            self.assertTrue(content.startswith(b"\x89PNG"))

        # Traversal attempt
        bad_url = f"http://127.0.0.1:{self.port}/assets/../../../../etc/passwd"
        try:
            urllib.request.urlopen(bad_url, timeout=3)
            self.fail("Traversal attempt should return 403/404.")
        except urllib.error.HTTPError as e:
            self.assertIn(e.code, (403, 404))


if __name__ == "__main__":
    unittest.main()
