#!/usr/bin/env python3
"""
Re-export BGM Matcher functions for convenience from library.audio.
"""
from library.content_factory.bgm_matcher import (
    AVAILABLE_BEDS,
    NICHE_DEFAULT_BEDS,
    match_bgm_for_episode,
    get_bed_info,
    list_available_beds,
    validate_bed_preset
)

__all__ = [
    "AVAILABLE_BEDS",
    "NICHE_DEFAULT_BEDS",
    "match_bgm_for_episode",
    "get_bed_info",
    "list_available_beds",
    "validate_bed_preset"
]
