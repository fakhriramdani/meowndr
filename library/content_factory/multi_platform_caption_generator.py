#!/usr/bin/env python3
"""
Multi-Platform Caption Generator & Quality Assurance System for @meowndr.
Unified wrapper over library.content_factory.captions engine.
Generates platform-tailored, validated captions for:
  1. Instagram Reels (100-500 chars recommended, <= 5 hashtags, Save/Share CTA)
  2. TikTok (50-300 chars recommended, 2-3 hashtags, Comment CTA)
  3. YouTube Shorts (Title <= 100 chars, Description <= 5000 chars, 2-3 hashtags, Subscribe CTA)

Outputs:
  - output/<slug>/captions/instagram.txt
  - output/<slug>/captions/tiktok.txt
  - output/<slug>/captions/youtube.txt
  - output/<slug>/captions/captions.json
  - output/<slug>/captions/validation-report.json
And mirrors to:
  - episodes/<slug>/publishing/
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.captions import (
    CaptionEngine,
    generate_captions_for_episode,
    CompositeValidator,
    HashtagIntelligence
)
from library.content_factory.captions.validators import (
    CharacterValidator,
    HashtagValidator,
    ContentValidator,
    KeywordValidator
)


class CaptionValidator:
    """Backward-compatible pre-save Quality Assurance validator for multi-platform captions."""

    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        return HashtagValidator.extract_hashtags(text)

    @staticmethod
    def count_emojis(text: str) -> int:
        return ContentValidator.count_emojis(text)

    @staticmethod
    def jaccard_similarity(text1: str, text2: str) -> float:
        return CompositeValidator.jaccard_similarity(text1, text2)

    @classmethod
    def validate_instagram(cls, caption: str) -> Tuple[bool, List[str]]:
        c_ok, c_err, _ = CharacterValidator.validate_instagram(caption)
        tags = HashtagValidator.extract_hashtags(caption)
        h_ok, h_err, _ = HashtagValidator.validate_instagram(tags)
        ct_ok, ct_err, _ = ContentValidator.validate_instagram_content(caption)
        all_errs = c_err + h_err + ct_err
        return len(all_errs) == 0, all_errs

    @classmethod
    def validate_tiktok(cls, caption: str) -> Tuple[bool, List[str]]:
        c_ok, c_err, _ = CharacterValidator.validate_tiktok(caption)
        tags = HashtagValidator.extract_hashtags(caption)
        h_ok, h_err, _ = HashtagValidator.validate_tiktok(tags)
        ct_ok, ct_err, _ = ContentValidator.validate_tiktok_content(caption)
        all_errs = c_err + h_err + ct_err
        return len(all_errs) == 0, all_errs

    @classmethod
    def validate_youtube(cls, title: str, description: str) -> Tuple[bool, List[str]]:
        t_ok, t_err, _ = CharacterValidator.validate_youtube_title(title)
        d_ok, d_err, _ = CharacterValidator.validate_youtube_description(description)
        tags = HashtagValidator.extract_hashtags(description)
        h_ok, h_err, _ = HashtagValidator.validate_youtube(tags)
        ct_ok, ct_err, _ = ContentValidator.validate_youtube_content(title, description)
        all_errs = t_err + d_err + h_err + ct_err
        return len(all_errs) == 0, all_errs

    @classmethod
    def validate_cross_platform(cls, ig: str, tt: str, yt_desc: str) -> Tuple[bool, List[str]]:
        ok, errs, _ = CompositeValidator.validate_cross_platform_uniqueness(ig, tt, yt_desc)
        return ok, errs


class MultiPlatformCaptionGenerator:
    """Automated multi-platform caption generator with self-healing QA retry loop."""

    def __init__(self, episode_slug: str, output_dir: Optional[Path] = None):
        self.slug = episode_slug.strip()
        self.engine = CaptionEngine(self.slug)
        self.output_dir = output_dir or self.engine.pub_dir

    def generate_and_validate(self, max_retries: int = 3, force: bool = False) -> Dict[str, Any]:
        """Coordinates caption synthesis with automatic self-healing QA retry loop."""
        bundle, was_cached = self.engine.generate_captions(force=force, max_attempts=max_retries)
        json_dict = bundle.to_json_dict()

        # Build response compatible with existing expectations
        compat_result = {
            "status": "VALIDATED" if bundle.overall_status == "READY" else "NEEDS_REVIEW",
            "attempt": bundle.attempt_count,
            "was_cached": was_cached,
            "topic": bundle.topic,
            "language": bundle.language,
            "script_hash": bundle.script_hash,
            "instagram": {
                "caption": bundle.instagram.caption,
                "character_count": bundle.instagram.character_count,
                "hashtags": bundle.instagram.hashtags,
                "validation_status": "PASS" if bundle.instagram.status == "READY" else "FAIL",
                "target_range": "100-500 characters",
                "cta_type": "Save / Share CTA",
                "errors": bundle.instagram.validation_errors,
            },
            "tiktok": {
                "caption": bundle.tiktok.caption,
                "character_count": bundle.tiktok.character_count,
                "hashtags": bundle.tiktok.hashtags,
                "validation_status": "PASS" if bundle.tiktok.status == "READY" else "FAIL",
                "target_range": "50-300 characters",
                "cta_type": "Comment Interaction CTA",
                "errors": bundle.tiktok.validation_errors,
            },
            "youtube": {
                "title": bundle.youtube.title,
                "title_length": bundle.youtube.title_character_count,
                "description": bundle.youtube.description,
                "description_length": bundle.youtube.description_character_count,
                "hashtags": bundle.youtube.hashtags,
                "validation_status": "PASS" if bundle.youtube.status == "READY" else "FAIL",
                "target_range": "Title <= 100, Desc 100-500 characters",
                "cta_type": "Subscribe CTA",
                "errors": bundle.youtube.validation_errors,
            },
            "cross_platform_uniqueness": bundle.validation_report.get("cross_platform_uniqueness", {
                "status": "PASS",
                "errors": []
            }),
            "platforms": json_dict.get("platforms", {})
        }
        return compat_result

    def save_deliverables(self, force: bool = False) -> Dict[str, str]:
        """Saves individual text files and structured JSON output."""
        res = self.engine.save_deliverables(force=force)
        return {
            "instagram_caption": res["files"]["instagram"],
            "tiktok_caption": res["files"]["tiktok"],
            "youtube_title": str(self.engine.pub_dir / "youtube_title.txt"),
            "youtube_description": str(self.engine.pub_dir / "youtube_description.txt"),
            "youtube_combined": res["files"]["youtube"],
            "captions_json": res["files"]["captions_json"],
            "validation_report": res["files"]["validation_report"],
            "structured_json": str(self.engine.pub_dir / "captions.json")
        }


def main():
    parser = argparse.ArgumentParser(description="Multi-Platform Caption Generator for @meowndr")
    parser.add_argument("slug", help="Episode slug (e.g. 20-aroma-hujan-petrichor)")
    parser.add_argument("--out-dir", default=None, help="Custom output directory")
    parser.add_argument("--force", action="store_true", help="Force regenerate captions ignoring cache")
    parser.add_argument("--json", action="store_true", help="Print structured JSON to stdout")
    args = parser.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else None
    gen = MultiPlatformCaptionGenerator(args.slug, output_dir=out_dir)
    res = gen.generate_and_validate(force=args.force)
    saved = gen.save_deliverables(force=args.force)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("=" * 70)
        print(f"  Multi-Platform Captions Generated: {args.slug}")
        print("=" * 70)
        print(f"• Overall Status:     {res['status']} (Attempt {res.get('attempt', 1)}, Cached: {res.get('was_cached', False)})")
        print(f"• Instagram Reels:    {res['instagram']['character_count']} chars, {len(res['instagram']['hashtags'])} tags [{res['instagram']['validation_status']}]")
        print(f"• TikTok:             {res['tiktok']['character_count']} chars, {len(res['tiktok']['hashtags'])} tags [{res['tiktok']['validation_status']}]")
        print(f"• YouTube Title:      {res['youtube']['title_length']} chars [{res['youtube']['validation_status']}]")
        print(f"• YouTube Desc:       {res['youtube']['description_length']} chars, {len(res['youtube']['hashtags'])} tags [{res['youtube']['validation_status']}]")
        print("-" * 70)
        print("Files Generated:")
        for k, v in saved.items():
            print(f"  - {k}: {v}")
        print("=" * 70)


if __name__ == "__main__":
    main()
