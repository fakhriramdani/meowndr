#!/usr/bin/env python3
"""
Unit tests for GDriveUploader and Google Drive upload integration.
"""

import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.gdrive_uploader import GDriveUploader


class TestGDriveUploader(unittest.TestCase):
    def setUp(self):
        self.uploader_ep05 = GDriveUploader("05-bintang-berkelip")
        self.uploader_ep06 = GDriveUploader("06-petir-zigzag")
        self.uploader_invalid = GDriveUploader("nonexistent-episode")

    def test_rclone_installed(self):
        ok, rclone_bin = self.uploader_ep05.check_rclone_installed()
        self.assertTrue(ok, "rclone binary must be installed and found in PATH")
        self.assertTrue(Path(rclone_bin).exists())

    def test_remote_accessible(self):
        ok, msg = self.uploader_ep05.check_remote_accessible()
        self.assertTrue(ok, f"gdrive remote should be accessible: {msg}")

    def test_invalid_remote_fails_gracefully(self):
        bad_uploader = GDriveUploader("05-bintang-berkelip", remote_name="nonexistent_remote_xyz")
        ok, msg = bad_uploader.check_remote_accessible()
        self.assertFalse(ok)
        self.assertIn("not configured in rclone", msg)

    def test_prerequisites_valid_episode(self):
        ok, errors = self.uploader_ep05.verify_prerequisites()
        self.assertTrue(ok, f"Prerequisites should pass for 05-bintang-berkelip: {errors}")
        self.assertIsNotNone(self.uploader_ep05.video_path)
        self.assertTrue(self.uploader_ep05.video_path.exists())

    def test_prerequisites_missing_episode(self):
        ok, errors = self.uploader_invalid.verify_prerequisites()
        self.assertFalse(ok)
        self.assertTrue(any("does not exist" in e for e in errors))

    def test_staging_directory_structure(self):
        ok, errors = self.uploader_ep05.verify_prerequisites()
        self.assertTrue(ok)
        ok_stage, stage_dir, items = self.uploader_ep05.prepare_staging_directory()
        self.assertTrue(ok_stage)
        self.assertTrue(stage_dir.exists())

        # Verify required deliverables exist in staging
        self.assertTrue((stage_dir / "thumbnail.png").exists())
        self.assertTrue((stage_dir / "script.md").exists())
        self.assertTrue((stage_dir / "metadata.json").exists())
        self.assertTrue((stage_dir / "captions" / "youtube.md").exists())
        self.assertTrue((stage_dir / "captions" / "tiktok.md").exists())
        self.assertTrue((stage_dir / "captions" / "instagram.md").exists())

    def test_dry_run_upload(self):
        ok, record, msgs = self.uploader_ep05.upload_to_gdrive(dry_run=True)
        self.assertTrue(ok)
        self.assertEqual(record.get("status"), "DRY_RUN_COMPLETED")
        self.assertIn(f"{self.uploader_ep05.remote_name}:Antigravity/Videos/", record.get("remote_destination", ""))

    def test_target_folder_name_format(self):
        folder_name = self.uploader_ep05._get_target_folder_name()
        # Expect YYYY-MM-DD_slug
        import re
        self.assertTrue(re.match(r"^\d{4}-\d{2}-\d{2}_05-bintang-berkelip$", folder_name))


if __name__ == "__main__":
    unittest.main()
