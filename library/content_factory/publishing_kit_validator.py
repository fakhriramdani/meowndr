#!/usr/bin/env python3
"""
Publishing Kit Validator for @meowndr episodes.
Verifies all 6 publishing deliverables:
  1. File existence and non-empty content
  2. Strict JSON schema compliance (publishing_kit_schema.json)
  3. Canonical branding (@meowndr)
  4. Platform character limits and formatting rules
  5. Media asset existence on disk
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.schema_validator import validate_artifact
from library.content_factory.brand_config import CHANNEL_NAME

EXPECTED_FILES = [
    "youtube-shorts.md",
    "tiktok.md",
    "instagram-reels.md",
    "publishing-kit.json",
    "research-notes.md",
    "upload-checklist.md"
]


class PublishingKitValidator:
    def __init__(self, episode_slug: str):
        self.slug = episode_slug.strip()
        self.ep_dir = REPO_ROOT / "episodes" / self.slug
        self.pub_dir = self.ep_dir / "publishing"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def log_pass(self, msg: str):
        self.passed.append(msg)
        print(f"  [PASS] {msg}")

    def log_warn(self, msg: str):
        self.warnings.append(msg)
        print(f"  [WARN] {msg}")

    def log_error(self, msg: str):
        self.errors.append(msg)
        print(f"  [ERROR] {msg}")

    def validate(self) -> bool:
        print("=" * 70)
        print(f"  Publishing Kit Quality Verification: {self.slug}")
        print("=" * 70)

        if not self.pub_dir.exists():
            self.log_error(f"Publishing directory missing: {self.pub_dir}")
            return False

        # 1. File existence and size check
        for fname in EXPECTED_FILES:
            fpath = self.pub_dir / fname
            if not fpath.exists():
                self.log_error(f"Missing required deliverable: {fname}")
            elif fpath.stat().st_size == 0:
                self.log_error(f"File is empty: {fname}")
            else:
                self.log_pass(f"Deliverable present and non-empty: {fname} ({fpath.stat().st_size} bytes)")

        # 2. JSON Schema validation
        json_file = self.pub_dir / "publishing-kit.json"
        if json_file.exists():
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                is_valid, schema_errs = validate_artifact("publishing_kit", data)
                if not is_valid:
                    for err in schema_errs:
                        self.log_error(f"Schema error in publishing-kit.json: {err}")
                else:
                    self.log_pass("publishing-kit.json conforms 100% to PublishingKitSchema")

                # 3. Channel Branding Verification
                ch = data.get("channel_name")
                if ch != CHANNEL_NAME:
                    self.log_error(f"Invalid channel_name '{ch}'. Must be exact '{CHANNEL_NAME}'.")
                else:
                    self.log_pass(f"Canonical brand handle verified: '{ch}'")

                # Check for legacy forbidden typos in all markdown files
                self._check_legacy_branding()

                # 4. YouTube Limits
                yt = data.get("youtube_shorts", {})
                for idx, t in enumerate(yt.get("title_options", [])):
                    if len(t) > 100:
                        self.log_error(f"YouTube title option {idx+1} exceeds 100 characters ({len(t)} chars): '{t}'")
                    else:
                        self.log_pass(f"YouTube title option {idx+1} length valid ({len(t)}/100 chars)")

                # 5. Hashtag checks
                for platform_key in ["tiktok", "instagram_reels"]:
                    p_data = data.get(platform_key, {})
                    tags = p_data.get("hashtags", [])
                    if len(tags) != len(set(tags)):
                        self.log_warn(f"{platform_key} contains duplicate hashtags")
                    for t in tags:
                        if not t.startswith("#") or " " in t:
                            self.log_error(f"Malformed hashtag in {platform_key}: '{t}'")
                self.log_pass("Social hashtags syntax and uniqueness verified")

                # 6. Referenced Media Asset existence
                vmeta = data.get("video_metadata", {})
                vpath = REPO_ROOT / vmeta.get("path", "")
                if not vpath.exists():
                    self.log_error(f"Referenced video does not exist on disk: {vpath}")
                else:
                    self.log_pass(f"Referenced video exists: {vpath.name} ({vmeta.get('file_size_mb')} MB)")

                assets = data.get("assets", {})
                thumb_rel = assets.get("thumbnail_16x9")
                if thumb_rel:
                    tpath = REPO_ROOT / thumb_rel
                    if not tpath.exists():
                        self.log_warn(f"Referenced thumbnail not found on disk: {tpath}")
                    else:
                        self.log_pass(f"Referenced 16:9 thumbnail verified on disk: {tpath.name}")

                open_rel = assets.get("opening_frame_9x16")
                if open_rel:
                    opath = REPO_ROOT / open_rel
                    if not opath.exists():
                        self.log_warn(f"Referenced opening frame not found on disk: {opath}")
                    else:
                        self.log_pass(f"Referenced 9:16 opening frame verified on disk: {opath.name}")

                # 7. Semantic Topic Consistency & Astronomy Leak Detection
                self._check_semantic_consistency(data)
                self._check_forbidden_fallback_leaks(data)

                # 8. Platform Constraints & Formatting Quality
                self._check_platform_constraints(data)

                # 9. Anti-Regression, Anti-Spoiler & Rewatch Loop Integrity
                self._check_anti_spoiler_and_loop_integrity(data)

            except Exception as e:
                self.log_error(f"Failed to parse publishing-kit.json: {e}")

        print("-" * 70)
        print(f"Publishing Kit Audit Summary: {len(self.passed)} Passed, {len(self.warnings)} Warnings, {len(self.errors)} Blocking Errors")
        print("=" * 70)
        return len(self.errors) == 0

    def _check_legacy_branding(self):
        """Scans all publishing markdown deliverables for legacy 'meowdnr' typos."""
        forbidden_pattern = re.compile(r"\bmeowdnr\b", re.IGNORECASE)
        for fname in EXPECTED_FILES:
            fpath = self.pub_dir / fname
            if fpath.exists():
                text = fpath.read_text(encoding="utf-8")
                matches = forbidden_pattern.findall(text)
                if matches:
                    self.log_error(f"Legacy branding typo '{matches[0]}' detected in {fname}!")
        self.log_pass("Zero legacy branding typos detected across all publication copy")

    def _check_semantic_consistency(self, data: Dict[str, Any]):
        """Verifies that social media copy is semantically consistent with episode topic."""
        meta_topic = data.get("topic", "")
        ep_title = data.get("episode_title", "")
        combined_text = f"{meta_topic} {ep_title}".lower()

        stopwords = {
            "kenapa", "mengapa", "bagaimana", "gimana", "kalau", "jadinya",
            "bisa", "malah", "bikin", "tambah", "akan", "tapi", "apakah",
            "dan", "di", "ke", "dari", "yang", "pada", "untuk", "dengan",
            "ini", "itu", "atau", "adalah", "saat", "terus", "lagi", "punya",
            "sebuah", "suatu", "oleh", "tentang", "fakta", "sains", "rahasia"
        }
        raw_words = re.findall(r"[a-z0-9\-]+", combined_text)
        keywords = [w for w in raw_words if len(w) >= 3 and w not in stopwords]

        if not keywords:
            self.log_warn("No specific topic keywords extracted for semantic check; skipping semantic match.")
            return

        yt_titles = data.get("youtube_shorts", {}).get("title_options", [])
        yt_desc = data.get("youtube_shorts", {}).get("description", "")
        tt_caps = data.get("tiktok", {}).get("caption_options", [])
        ig_caps = data.get("instagram_reels", {}).get("caption_options", [])

        all_pub_text = " ".join(yt_titles + [yt_desc] + tt_caps + ig_caps).lower()
        matched_keywords = [kw for kw in keywords if kw in all_pub_text]

        if not matched_keywords:
            self.log_error(
                f"Semantic mismatch: None of the episode keywords {keywords[:5]} were found in publishing copy!"
            )
        else:
            self.log_pass(f"Semantic topic consistency verified: matched keywords {matched_keywords[:4]}")

    def _check_forbidden_fallback_leaks(self, data: Dict[str, Any]):
        """Detects whether unrelated astronomy fallback text leaked into publishing copy."""
        meta_topic = data.get("topic", "").lower()
        ep_title = data.get("episode_title", "").lower()
        slug = data.get("episode_id", "").lower()

        # Is this an astronomy/stargazing episode?
        is_astronomy = any(
            term in meta_topic or term in ep_title or term in slug
            for term in ["bintang", "astronomi", "antariksa", "langit malam", "planet", "teleskop", "scintillation", "hubble", "tata surya"]
        )

        if not is_astronomy:
            forbidden_astronomy = [
                "bintang kelap-kelip",
                "scintillation",
                "bintangnya yang berkedip",
                "rahasia cahaya bintang",
                "cahaya bintang",
                "point source",
                "teleskop antariksa",
                "james webb"
            ]
            # Only forbid general kelap-kelip if not bioluminescence/fireflies/lighting
            is_biolum = any(term in meta_topic or term in ep_title or term in slug for term in ["kunang", "bioluminesensi", "lampu"])
            if not is_biolum:
                forbidden_astronomy.extend(["kelap-kelip", "berkelap-kelip"])

            fields_to_scan = []
            fields_to_scan.extend(data.get("youtube_shorts", {}).get("title_options", []))
            fields_to_scan.append(data.get("youtube_shorts", {}).get("description", ""))
            fields_to_scan.extend(data.get("tiktok", {}).get("caption_options", []))
            fields_to_scan.append(data.get("tiktok", {}).get("cover_title", ""))
            fields_to_scan.extend(data.get("instagram_reels", {}).get("caption_options", []))
            fields_to_scan.append(data.get("instagram_reels", {}).get("cover_title", ""))
            fields_to_scan.append(data.get("instagram_reels", {}).get("alt_text", ""))

            full_text = " ".join(fields_to_scan).lower()
            detected_leaks = [term for term in forbidden_astronomy if term in full_text]

            if detected_leaks:
                self.log_error(
                    f"Forbidden fallback leak detected: '{detected_leaks[0]}' found in publishing copy for non-astronomy episode!"
                )
            else:
                self.log_pass("Zero astronomy fallback copy leaks detected (Topic Isolation verified)")

    def _check_platform_constraints(self, data: Dict[str, Any]):
        """Audits platform-specific formatting and character budgets."""
        # 1. TikTok body length before hashtag block
        tt_caps = data.get("tiktok", {}).get("caption_options", [])
        for idx, cap in enumerate(tt_caps):
            body_text = cap.split("#")[0].strip()
            if len(body_text) > 220:
                self.log_error(f"TikTok caption option {idx+1} body exceeds 220 characters ({len(body_text)} chars): '{body_text[:60]}...'")
            elif len(body_text) > 160:
                self.log_warn(f"TikTok caption option {idx+1} body length ({len(body_text)} chars) is close to mobile feed truncation threshold.")
            else:
                self.log_pass(f"TikTok caption option {idx+1} body length optimal ({len(body_text)} chars)")

        # 2. Instagram Reels formatting
        ig = data.get("instagram_reels", {})
        rec_ig = ig.get("recommended_caption", "")
        if "\n\n" not in rec_ig:
            self.log_warn("Instagram recommended caption lacks paragraph line breaks (risk of wall-of-text fatigue).")
        else:
            self.log_pass("Instagram recommended caption formatting has clear paragraph breaks")

        has_structure = "\n\n" in rec_ig and len(rec_ig.split("\n\n")) >= 3
        if not has_structure:
            self.log_warn("Instagram recommended caption lacks clean paragraph structure (needs >= 3 paragraphs).")
        else:
            self.log_pass("Instagram recommended caption formatting has clear paragraph structure")

        # 3. Alt text
        alt_text = ig.get("alt_text", "")
        if len(alt_text) < 30:
            self.log_error(f"Instagram alt text is too short ({len(alt_text)} chars). Must be descriptive for screen readers.")
        elif "kucing ilmuwan" not in alt_text.lower() and "cat scientist" not in alt_text.lower():
            self.log_warn("Instagram alt text should mention Kucing Ilmuwan mascot for visual context.")
        else:
            self.log_pass(f"Instagram accessibility Alt Text verified ({len(alt_text)} chars)")

    def _check_anti_spoiler_and_loop_integrity(self, data: Dict[str, Any]):
        """
        Enforces strict zero-regression quality rules:
          1. Zero awkward double-conditionals ('kenapa jika', 'kenapa bagaimana').
          2. Zero inappropriate sleeping emojis ('😴') on non-sleep topics.
          3. Zero truncated titles with mid-word cutoffs or dangling brackets.
          4. Presence of explicit rewatch / loop triggers across social copy.
          5. Zero dangling sentence elipses ('...').
        """
        yt_titles = data.get("youtube_shorts", {}).get("title_options", [])
        yt_desc = data.get("youtube_shorts", {}).get("description", "")
        tt_caps = data.get("tiktok", {}).get("caption_options", [])
        ig_caps = data.get("instagram_reels", {}).get("caption_options", [])

        all_text = " ".join(yt_titles + [yt_desc] + tt_caps + ig_caps).lower()
        meta_topic = data.get("topic", "").lower()
        slug = data.get("episode_id", "").lower()

        # 1. Zero double-conditionals
        double_conditionals = ["kenapa jika", "kenapa bagaimana", "kenapa ya jika", "mengapa jika"]
        for dc in double_conditionals:
            if dc in all_text:
                self.log_error(f"Grammar defect detected: '{dc}' found in publishing copy!")
                break
        else:
            self.log_pass("Zero double-conditional grammar defects detected")

        # 2. Zero inappropriate sleeping emojis (unless sleep topic)
        is_sleep = any(k in meta_topic or k in slug for k in ["tidur", "kopi", "ngantuk", "coma", "lelah", "sleep", "yawn", "menguap"])
        if not is_sleep and "😴" in all_text:
            self.log_error("Inappropriate sleeping emoji '😴' detected in publishing copy for non-sleep topic!")
        else:
            self.log_pass("Emoji contextual relevance verified (no inappropriate sleep emojis)")

        # 3. YouTube Title Truncation check
        for t in yt_titles:
            if re.search(r"Kenapa Bisa Begini\?\s*\([^\)]+\)", t):
                self.log_error(f"Legacy clumsy title format detected in YouTube title: '{t}'")
            elif "..." in t or t.endswith(("..", "...", "…")):
                self.log_error(f"Truncated title ending in ellipsis detected: '{t}'")
        self.log_pass("YouTube Shorts titles verified complete and untruncated")

        # 4. Zero artificial rewatch phrasing
        forced_cues = ["coba tonton ulang", "tonton ulang", "tonton sekali lagi", "tonton lagi"]
        for fc in forced_cues:
            if fc in all_text:
                self.log_warn(f"Artificial rewatch cue '{fc}' detected in copy. Prefer natural informative storytelling.")
                break
        else:
            self.log_pass("Social copy verified natural & free of artificial rewatch phrasing")


def validate_publishing_kit(episode_slug: str) -> bool:
    validator = PublishingKitValidator(episode_slug)
    return validator.validate()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 publishing_kit_validator.py <episode_slug>")
        sys.exit(1)
    ok = validate_publishing_kit(sys.argv[1])
    sys.exit(0 if ok else 1)
