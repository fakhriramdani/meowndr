#!/usr/bin/env python3
"""
Automated Google Drive Uploader for @meowndr Papercraft Episodes using rclone.
Coordinates safe, idempotent, non-destructive uploading of:
  - Final rendered video
  - Standalone 16:9 thumbnail and 9:16 opening frame
  - Human-readable narration script (script.md)
  - Platform-specific captions (captions/youtube.md, captions/tiktok.md, captions/instagram.md)
  - Structured production metadata (metadata.json)
  - Research verification notes (research-notes.md)
  - Pre-flight upload checklist (upload-checklist.md)

Destination:
  gdrive:Antigravity/Videos/YYYY-MM-DD_<video-slug>/
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

def _resolve_default_remote() -> str:
    env_remote = os.environ.get("GDRIVE_REMOTE", "").strip()
    if env_remote:
        return env_remote.rstrip(":")
    rclone_bin = shutil.which("rclone")
    if rclone_bin:
        try:
            res = subprocess.run([rclone_bin, "listremotes"], capture_output=True, text=True, timeout=5)
            remotes = [r.strip().rstrip(":") for r in res.stdout.splitlines() if r.strip()]
            if "gdrive-new" in remotes:
                return "gdrive-new"
            if "gdrive-agy" in remotes:
                return "gdrive-agy"
            if remotes:
                return remotes[0]
        except Exception:
            pass
    return "gdrive-new"


DEFAULT_GDRIVE_REMOTE = _resolve_default_remote()
DEFAULT_GDRIVE_BASE_DIR = os.environ.get("GDRIVE_BASE_DIR", "Antigravity/Videos")


class GDriveUploader:
    def __init__(self, episode_slug: str, remote_name: str = DEFAULT_GDRIVE_REMOTE, base_dir: str = DEFAULT_GDRIVE_BASE_DIR):
        self.slug = episode_slug.strip()
        self.ep_dir = REPO_ROOT / "episodes" / self.slug
        self.papercut_dir = self.ep_dir / "papercut"
        self.pub_dir = self.ep_dir / "publishing"
        self.staging_dir = self.pub_dir / "staged_gdrive"

        self.remote_name = remote_name.rstrip(":")
        self.base_dir = base_dir.strip("/")

        self.episode_cfg: Dict[str, Any] = {}
        self.publishing_meta: Dict[str, Any] = {}
        self.video_path: Optional[Path] = None
        self.thumbnail_path: Optional[Path] = None
        self.opening_frame_path: Optional[Path] = None

    def check_rclone_installed(self) -> Tuple[bool, str]:
        """Checks whether rclone is available in PATH."""
        rclone_bin = shutil.which("rclone")
        if not rclone_bin:
            return False, "rclone binary not found in system PATH. Install with: sudo apt-get install rclone or https://rclone.org/install/"
        return True, rclone_bin

    def check_remote_accessible(self) -> Tuple[bool, str]:
        """Verifies that the configured remote is present and reachable."""
        ok, rclone_bin = self.check_rclone_installed()
        if not ok:
            return False, rclone_bin

        try:
            res = subprocess.run([rclone_bin, "listremotes"], capture_output=True, text=True, check=True)
            remotes = [r.strip().rstrip(":") for r in res.stdout.splitlines() if r.strip()]
            if self.remote_name not in remotes:
                return False, f"Remote '{self.remote_name}:' is not configured in rclone. Configured remotes: {remotes}. Run 'rclone config' to set up Google Drive."

            # Test connectivity to remote root (about is a single fast API call)
            test_target = f"{self.remote_name}:"
            conn_res = subprocess.run([rclone_bin, "about", test_target], capture_output=True, text=True, timeout=30)
            if conn_res.returncode != 0:
                conn_res = subprocess.run([rclone_bin, "lsd", test_target], capture_output=True, text=True, timeout=30)
            if conn_res.returncode != 0:
                err_msg = conn_res.stderr.strip() or conn_res.stdout.strip()
                return False, f"Cannot connect to remote '{test_target}': {err_msg}"

            return True, f"Remote '{self.remote_name}:' is accessible."
        except subprocess.TimeoutExpired:
            return False, f"Connection to '{self.remote_name}:' timed out after 30 seconds."
        except Exception as e:
            return False, f"Error checking remote '{self.remote_name}:': {e}"

    def verify_prerequisites(self) -> Tuple[bool, List[str]]:
        """Verifies that rendering has finished, video exists, and all captions exist."""
        errors = []

        if not self.ep_dir.exists():
            return False, [f"Episode directory does not exist: {self.ep_dir}"]

        # 1. episode.json
        ep_json = self.papercut_dir / "episode.json"
        if not ep_json.exists():
            errors.append(f"Missing {ep_json}")
        else:
            try:
                with open(ep_json, "r", encoding="utf-8") as f:
                    self.episode_cfg = json.load(f)
            except Exception as e:
                errors.append(f"Failed to read episode.json: {e}")

        # 2. Check final video render
        out_prefix = self.episode_cfg.get("out", f"episode-{self.slug}")
        expected_video = self.papercut_dir / "out" / f"{out_prefix}.mp4"
        if expected_video.exists() and expected_video.stat().st_size > 1024:
            self.video_path = expected_video
        else:
            # Fallback search in papercut/out/
            mp4_candidates = [p for p in (self.papercut_dir / "out").glob("*.mp4") if p.stat().st_size > 1024]
            if mp4_candidates:
                self.video_path = mp4_candidates[0]
            else:
                errors.append(f"Final rendered video missing or empty in {self.papercut_dir / 'out'}. Render must complete before upload.")

        # 3. Check Publishing Kit / Captions
        required_pub_files = [
            "youtube-shorts.md",
            "tiktok.md",
            "instagram-reels.md",
            "publishing-kit.json"
        ]
        for fname in required_pub_files:
            fpath = self.pub_dir / fname
            if not fpath.exists():
                errors.append(f"Missing required publication deliverable: {fname}. Run publish-kit before uploading.")
            elif fpath.stat().st_size == 0:
                errors.append(f"Publication deliverable is empty: {fname}")

        if (self.pub_dir / "publishing-kit.json").exists():
            try:
                with open(self.pub_dir / "publishing-kit.json", "r", encoding="utf-8") as f:
                    self.publishing_meta = json.load(f)
            except Exception as e:
                errors.append(f"Malformed publishing-kit.json: {e}")

            # Validate publishing kit quality and topic isolation
            try:
                from library.content_factory.publishing_kit_validator import PublishingKitValidator
                validator = PublishingKitValidator(self.slug)
                if not validator.validate():
                    errors.append(f"Publishing kit failed quality validation with {len(validator.errors)} blocking errors. Re-run publish-kit before uploading.")
            except Exception as e:
                errors.append(f"Could not execute publishing kit validation: {e}")

        # 4. Thumbnails (optional but expected)
        thumb_path = self.papercut_dir / "out" / "thumbnail.png"
        if thumb_path.exists():
            self.thumbnail_path = thumb_path
        opening_path = self.papercut_dir / "out" / "opening-frame.png"
        if opening_path.exists():
            self.opening_frame_path = opening_path

        # 5. Remote accessibility check
        remote_ok, remote_msg = self.check_remote_accessible()
        if not remote_ok:
            errors.append(remote_msg)

        return len(errors) == 0, errors

    def _get_target_folder_name(self) -> str:
        """Determines the target folder name in YYYY-MM-DD_slug format."""
        # Try date from publishing-kit.json, then video file mtime, then today
        date_str = ""
        gen_at = self.publishing_meta.get("generated_at")
        if gen_at:
            try:
                dt = datetime.fromisoformat(gen_at.replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d")
            except Exception:
                pass

        if not date_str and self.video_path and self.video_path.exists():
            mtime = self.video_path.stat().st_mtime
            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        return f"{date_str}_{self.slug}"

    def _build_script_markdown(self) -> str:
        """Builds clean, human-readable script.md from narration data."""
        title = self.episode_cfg.get("meta", {}).get("title", self.slug)
        topic = self.episode_cfg.get("meta", {}).get("topic", "")

        script_json_path = self.ep_dir / "narration" / "script.json"
        if not script_json_path.exists():
            script_json_path = self.papercut_dir / "public" / "vo" / "script.json"

        lines = []
        if script_json_path.exists():
            try:
                with open(script_json_path, "r", encoding="utf-8") as f:
                    raw_script = json.load(f)
                for idx, item in enumerate(raw_script, 1):
                    if isinstance(item, dict):
                        line_id = item.get("id", f"line_{idx}")
                        text = item.get("text", "")
                        dur = item.get("target_seconds")
                        dur_str = f" (~{dur}s)" if dur else ""
                        lines.append(f"### {idx}. {line_id.upper()}{dur_str}\n> \"{text}\"\n")
            except Exception:
                pass

        if not lines:
            lines.append("> (Transkrip narasi bersumber dari rekaman voiceover terfinalisasi)\n")

        return f"""# Voiceover Narration Script — {title}

**Episode Slug**: `{self.slug}`  
**Topic**: {topic}  
**Channel**: `@meowndr`  
**Language**: Indonesian (`id`)  
**Timestamp**: {datetime.now(timezone.utc).isoformat()}  

---

## Complete Narration Breakdown

{''.join(lines)}
---
*Produced by @meowndr Papercraft Content Factory*
"""

    def prepare_staging_directory(self) -> Tuple[bool, Path, List[str]]:
        """
        Organizes deliverables into the exact structure requested:
          staged_gdrive/
            ├── <video_filename>.mp4
            ├── thumbnail.png
            ├── opening-frame.png (if present)
            ├── script.md
            ├── captions/
            │   ├── youtube.md
            │   ├── instagram.md
            │   └── tiktok.md
            ├── metadata.json
            ├── research-notes.md
            └── upload-checklist.md
        """
        if self.staging_dir.exists():
            shutil.rmtree(self.staging_dir)
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        captions_dir = self.staging_dir / "captions"
        captions_dir.mkdir(parents=True, exist_ok=True)

        staged_items = []

        # 1. Video file (preserve actual filename, e.g. episode-05-meowndr.mp4)
        if self.video_path and self.video_path.exists():
            dest_video = self.staging_dir / self.video_path.name
            shutil.copy2(self.video_path, dest_video)
            staged_items.append(dest_video.name)

        # 2. Thumbnail & opening frame
        if self.thumbnail_path and self.thumbnail_path.exists():
            dest_thumb = self.staging_dir / "thumbnail.png"
            shutil.copy2(self.thumbnail_path, dest_thumb)
            staged_items.append(dest_thumb.name)

        if self.opening_frame_path and self.opening_frame_path.exists():
            dest_open = self.staging_dir / "opening-frame.png"
            shutil.copy2(self.opening_frame_path, dest_open)
            staged_items.append(dest_open.name)

        # 3. script.md
        script_md_content = self._build_script_markdown()
        script_md_path = self.staging_dir / "script.md"
        script_md_path.write_text(script_md_content, encoding="utf-8")
        staged_items.append(script_md_path.name)

        # 4. Captions in captions/
        yt_src = self.pub_dir / "youtube-shorts.md"
        if yt_src.exists():
            shutil.copy2(yt_src, captions_dir / "youtube.md")
            staged_items.append("captions/youtube.md")

        ig_src = self.pub_dir / "instagram-reels.md"
        if ig_src.exists():
            shutil.copy2(ig_src, captions_dir / "instagram.md")
            staged_items.append("captions/instagram.md")

        tt_src = self.pub_dir / "tiktok.md"
        if tt_src.exists():
            shutil.copy2(tt_src, captions_dir / "tiktok.md")
            staged_items.append("captions/tiktok.md")

        # Plain text multi-platform caption files
        for txt_name in ["instagram.txt", "tiktok.txt", "youtube_title.txt", "youtube_description.txt"]:
            src = self.pub_dir / txt_name
            # Fallback for legacy filenames
            if not src.exists() and txt_name == "instagram.txt":
                legacy = self.pub_dir / "instagram_caption.txt"
                if legacy.exists():
                    src = legacy
            if not src.exists() and txt_name == "tiktok.txt":
                legacy = self.pub_dir / "tiktok_caption.txt"
                if legacy.exists():
                    src = legacy
            if src.exists():
                shutil.copy2(src, captions_dir / txt_name)
                staged_items.append(f"captions/{txt_name}")

        caps_json = self.pub_dir / "captions.json"
        if not caps_json.exists():
            caps_json = self.pub_dir / "multi_platform_captions.json"
        if caps_json.exists():
            shutil.copy2(caps_json, self.staging_dir / "captions.json")
            staged_items.append("captions.json")

        # 5. metadata.json (standardized from publishing-kit.json)
        pub_kit_path = self.pub_dir / "publishing-kit.json"
        if pub_kit_path.exists():
            shutil.copy2(pub_kit_path, self.staging_dir / "metadata.json")
            staged_items.append("metadata.json")

        # 6. research-notes.md and upload-checklist.md
        res_notes = self.pub_dir / "research-notes.md"
        if res_notes.exists():
            shutil.copy2(res_notes, self.staging_dir / "research-notes.md")
            staged_items.append(res_notes.name)

        up_check = self.pub_dir / "upload-checklist.md"
        if up_check.exists():
            shutil.copy2(up_check, self.staging_dir / "upload-checklist.md")
            staged_items.append(up_check.name)

        # 7. publishing-metadata.md (if present)
        pub_md = self.pub_dir / "publishing-metadata.md"
        if not pub_md.exists():
            pub_md = self.papercut_dir / "out" / "publishing-metadata.md"
        if pub_md.exists():
            shutil.copy2(pub_md, self.staging_dir / "publishing-metadata.md")
            staged_items.append("publishing-metadata.md")

        return True, self.staging_dir, staged_items

    def upload_to_gdrive(self, dry_run: bool = False, force: bool = False) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Executes rclone copy from staging directory to Google Drive.
        Safe, idempotent, non-destructive.
        """
        ok, errors = self.verify_prerequisites()
        if not ok:
            return False, {}, errors

        ok_stage, staging_dir, staged_items = self.prepare_staging_directory()
        if not ok_stage:
            return False, {}, ["Failed to prepare staging directory for upload."]

        folder_name = self._get_target_folder_name()
        remote_dest = f"{self.remote_name}:{self.base_dir}/{folder_name}"

        print(f"  • Google Drive Destination: {remote_dest}")
        print(f"  • Deliverables to upload: {len(staged_items)} files")
        if force:
            print("  • Force flag enabled: Re-transferring all files unconditionally (--ignore-times)")

        if dry_run:
            print("  [DRY-RUN] Simulating rclone copy without transferring bytes...")
            cmd = ["rclone", "copy", str(staging_dir), remote_dest, "--dry-run", "-v"]
        else:
            # Safe non-destructive upload: rclone copy (NEVER rclone sync)
            cmd = [
                "rclone", "copy",
                str(staging_dir),
                remote_dest,
                "--retries", "3",
                "--low-level-retries", "10",
                "--stats-one-line",
                "-v"
            ]
            if force:
                cmd.append("--ignore-times")

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            log_output = res.stderr or res.stdout
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr or e.stdout
            return False, {}, [f"rclone copy failed with exit code {e.returncode}: {err_msg}"]

        if dry_run:
            return True, {
                "status": "DRY_RUN_COMPLETED",
                "folder_name": folder_name,
                "remote_destination": remote_dest,
                "staged_items": staged_items
            }, ["Dry run completed successfully."]

        # Post-upload verification check
        verify_ok, remote_files, verify_errors = self.verify_remote_upload(folder_name)
        if not verify_ok:
            return False, {
                "status": "PARTIAL_OR_FAILED_VERIFICATION",
                "folder_name": folder_name,
                "remote_destination": remote_dest,
                "remote_files": remote_files
            }, verify_errors

        # Save record
        record = {
            "episode_slug": self.slug,
            "episode_title": self.episode_cfg.get("meta", {}).get("title"),
            "channel_name": "@meowndr",
            "google_drive_folder": f"{self.base_dir}/{folder_name}",
            "google_drive_destination": remote_dest,
            "uploaded_files_count": len(remote_files),
            "uploaded_files": remote_files,
            "upload_timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "VERIFIED_UPLOAD_COMPLETED"
        }
        self._save_upload_record(record)
        self._update_workflow_state(record)

        return True, record, [f"Verified {len(remote_files)} files successfully uploaded to {remote_dest}"]

    def verify_remote_upload(self, folder_name: str) -> Tuple[bool, List[Dict[str, Any]], List[str]]:
        """Queries Google Drive using rclone lsjson to verify every file exists and matches size."""
        remote_dest = f"{self.remote_name}:{self.base_dir}/{folder_name}"
        cmd = ["rclone", "lsjson", remote_dest, "-R"]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            files_json = json.loads(res.stdout)
        except Exception as e:
            return False, [], [f"Failed to query remote directory {remote_dest}: {e}"]

        remote_map = {item.get("Path"): item for item in files_json if not item.get("IsDir")}
        missing = []
        verified_items = []

        # Check every staged file against remote
        for local_file in self.staging_dir.rglob("*"):
            if local_file.is_file():
                rel_path = str(local_file.relative_to(self.staging_dir))
                if rel_path not in remote_map:
                    missing.append(f"File missing on Google Drive: {rel_path}")
                else:
                    remote_item = remote_map[rel_path]
                    local_size = local_file.stat().st_size
                    remote_size = remote_item.get("Size", 0)
                    if local_size != remote_size:
                        missing.append(f"Size mismatch for {rel_path}: local={local_size} vs remote={remote_size}")
                    else:
                        verified_items.append({
                            "path": rel_path,
                            "size_bytes": remote_size,
                            "mime_type": remote_item.get("MimeType"),
                            "mod_time": remote_item.get("ModTime"),
                            "id": remote_item.get("ID")
                        })

        if missing:
            return False, verified_items, missing

        return True, verified_items, []

    def _save_upload_record(self, record: Dict[str, Any]):
        """Persists upload record into publishing/upload_record.json."""
        record_path = self.pub_dir / "upload_record.json"
        with open(record_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

    def _update_workflow_state(self, record: Dict[str, Any]):
        """Updates content_factory/workflow_state.json if present."""
        wf_path = self.ep_dir / "content_factory" / "workflow_state.json"
        if wf_path.exists():
            try:
                with open(wf_path, "r", encoding="utf-8") as f:
                    wf = json.load(f)
                wf["gdrive_upload"] = {
                    "status": "COMPLETED",
                    "destination": record.get("google_drive_destination"),
                    "folder": record.get("google_drive_folder"),
                    "uploaded_files_count": record.get("uploaded_files_count"),
                    "uploaded_at": record.get("upload_timestamp")
                }
                wf["last_updated"] = record.get("upload_timestamp")
                with open(wf_path, "w", encoding="utf-8") as f:
                    json.dump(wf, f, indent=2, ensure_ascii=False)
            except Exception:
                pass


def upload_episode_to_gdrive(episode_slug: str, dry_run: bool = False, force: bool = False) -> Tuple[bool, Dict[str, Any], List[str]]:
    """Public functional entrypoint."""
    uploader = GDriveUploader(episode_slug)
    return uploader.upload_to_gdrive(dry_run=dry_run, force=force)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gdrive_uploader.py <episode_slug> [--dry-run] [--force]")
        sys.exit(1)
    slug = sys.argv[1]
    is_dry = "--dry-run" in sys.argv
    is_force = "--force" in sys.argv
    success, res, msgs = upload_episode_to_gdrive(slug, dry_run=is_dry, force=is_force)
    if success:
        print(f"[SUCCESS] Google Drive upload completed for '{slug}':")
        for m in msgs:
            print(f"  - {m}")
        sys.exit(0)
    else:
        print(f"[FAIL] Google Drive upload failed for '{slug}':")
        for m in msgs:
            print(f"  - {m}")
        sys.exit(1)
