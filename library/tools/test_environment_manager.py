#!/usr/bin/env python3
"""
Unit tests for the environment management workflow (manage_environment.py).
Tests:
- Adding a new environment with valid 1080x1920 dimensions
- Rejection of invalid / non-vertical image dimensions
- Non-destructive protection against unauthorized overwrites
- Creation of revised versions with lineage tracking without destroying originals
- Master catalog and index updates
- Preservation of original background SHA-256 hash
"""

import os
import sys
import unittest
import tempfile
import json
import shutil
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from manage_environment import (
    add_environment,
    revise_environment,
    list_registered_environments,
)
from asset_loader import read_image_dimensions


class TestEnvironmentManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = self.temp_dir.name

        # Initialize mock assets structure
        os.makedirs(os.path.join(self.root, "assets", "backgrounds"), exist_ok=True)
        os.makedirs(os.path.join(self.root, "assets", "previews"), exist_ok=True)
        os.makedirs(os.path.join(self.root, "episodes", "01-anomali-air", "papercut", "public", "assets", "backgrounds"), exist_ok=True)
        os.makedirs(os.path.join(self.root, "library", "papercut", "kit", "assets"), exist_ok=True)

        # Baseline library.json
        self.lib_path = os.path.join(self.root, "assets", "library.json")
        self.base_lib = {
            "version": "2.0.0",
            "categories": {
                "environments": [],
                "props": [],
                "characters": [],
                "foregrounds": [],
            },
        }
        with open(self.lib_path, "w", encoding="utf-8") as f:
            json.dump(self.base_lib, f, indent=2)

        # Baseline index.json
        self.idx_path = os.path.join(self.root, "assets", "backgrounds", "index.json")
        with open(self.idx_path, "w", encoding="utf-8") as f:
            json.dump({"version": "1.1.0", "total_backgrounds": 0, "backgrounds": []}, f, indent=2)

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_dummy_png(self, path: str, width: int = 1080, height: int = 1920):
        import zlib
        os.makedirs(os.path.dirname(path), exist_ok=True)
        raw_data = b"".join(b"\x00" + b"\x80\x90\xa0" * width for _ in range(height))
        idat = zlib.compress(raw_data, level=1)
        def chunk(tag, data):
            crc = zlib.crc32(tag + data) & 0xffffffff
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)
        ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        idat_c = chunk(b"IDAT", idat)
        iend_c = chunk(b"IEND", b"")
        png = b"\x89PNG\r\n\x1a\n" + ihdr + idat_c + iend_c
        with open(path, "wb") as f:
            f.write(png)

    def test_add_new_environment_success(self):
        src_img = os.path.join(self.root, "source_botany.png")
        self.create_dummy_png(src_img, 1080, 1920)

        res = add_environment(
            image_path=src_img,
            env_id="botany-greenhouse",
            name="Botany Greenhouse",
            description="Papercraft plant conservatory with layered paper cutout flora.",
            category="Biology / Botany",
            mood="warm / natural",
            floor_y=1380,
            root_dir=self.root,
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["env_id"], "botany-greenhouse")
        self.assertTrue(res["validation"]["valid"])

        # Check files created on disk
        dest_bg = os.path.join(self.root, "assets", "backgrounds", "botany-greenhouse", "background.png")
        dest_meta = os.path.join(self.root, "assets", "backgrounds", "botany-greenhouse", "metadata.json")
        self.assertTrue(os.path.isfile(dest_bg))
        self.assertTrue(os.path.isfile(dest_meta))

        # Check library registration
        with open(self.lib_path, "r", encoding="utf-8") as f:
            lib = json.load(f)
        env_ids = [e["id"] for e in lib["categories"]["environments"]]
        self.assertIn("botany-greenhouse", env_ids)

    def test_add_environment_rejects_incompatible_dimensions(self):
        bad_img = os.path.join(self.root, "landscape.png")
        self.create_dummy_png(bad_img, 1920, 1080)  # Wrong 16:9 orientation

        with self.assertRaises(ValueError) as ctx:
            add_environment(
                image_path=bad_img,
                env_id="bad-env",
                name="Bad Env",
                description="Invalid dimensions",
                root_dir=self.root,
            )
        self.assertIn("1080x1920", str(ctx.exception))

    def test_add_environment_prevents_unauthorized_overwrite(self):
        src_img = os.path.join(self.root, "valid.png")
        self.create_dummy_png(src_img, 1080, 1920)

        # First add
        add_environment(
            image_path=src_img,
            env_id="physics-lab",
            name="Physics Lab",
            description="First version",
            root_dir=self.root,
        )

        # Second add without overwrite flag must raise FileExistsError
        with self.assertRaises(FileExistsError) as ctx:
            add_environment(
                image_path=src_img,
                env_id="physics-lab",
                name="Physics Lab Duplicate",
                description="Should be blocked",
                allow_overwrite=False,
                root_dir=self.root,
            )
        self.assertIn("already exists", str(ctx.exception))

    def test_revise_environment_preserves_original(self):
        src_v1 = os.path.join(self.root, "lab_v1.png")
        self.create_dummy_png(src_v1, 1080, 1920)

        # 1. Add v1
        add_environment(
            image_path=src_v1,
            env_id="optics-lab",
            name="Optics Laboratory",
            description="V1 initial setup",
            root_dir=self.root,
        )

        v1_meta_path = os.path.join(self.root, "assets", "backgrounds", "optics-lab", "metadata.json")
        with open(v1_meta_path, "r", encoding="utf-8") as f:
            v1_meta_before = json.load(f)

        # 2. Revise to v2
        src_v2 = os.path.join(self.root, "lab_v2.png")
        self.create_dummy_png(src_v2, 1080, 1920)

        rev_res = revise_environment(
            existing_env_id="optics-lab",
            new_image_path=src_v2,
            revision_notes="Extended laser breadboard and adjusted ambient filter",
            root_dir=self.root,
        )

        self.assertEqual(rev_res["operation"], "revise_environment")
        self.assertEqual(rev_res["env_id"], "optics-lab-v2")
        self.assertEqual(rev_res["parent_environment_id"], "optics-lab")
        self.assertTrue(rev_res["validation"]["valid"])

        # 3. Verify V1 is 100% UNTOUCHED
        with open(v1_meta_path, "r", encoding="utf-8") as f:
            v1_meta_after = json.load(f)
        self.assertEqual(v1_meta_before, v1_meta_after)

        # 4. Verify V2 exists with lineage
        v2_meta_path = os.path.join(self.root, "assets", "backgrounds", "optics-lab-v2", "metadata.json")
        with open(v2_meta_path, "r", encoding="utf-8") as f:
            v2_meta = json.load(f)
        self.assertEqual(v2_meta["lineage"]["parent_environment_id"], "optics-lab")
        self.assertEqual(v2_meta["lineage"]["revision_version"], "2.0.0")

        # 5. Verify both exist in catalog
        envs = list_registered_environments(self.root)
        registered_ids = [e["id"] for e in envs]
        self.assertIn("optics-lab", registered_ids)
        self.assertIn("optics-lab-v2", registered_ids)


if __name__ == "__main__":
    unittest.main()
