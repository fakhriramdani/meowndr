#!/usr/bin/env python3
"""
test_storyboard_extended_schema.py: Automated QA test for extended storyboard schema
validating character_position, character_movement, interactions, reactions, and text elements.
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from library.content_factory.schema_validator import validate_artifact

def test_extended_storyboard_schema():
    extended_storyboard = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "environment_id": "cozy-bedroom",
        "environments_used": [
            "cozy-bedroom",
            "science-laboratory",
            "modern-classroom",
            "city-park"
        ],
        "fps": 30,
        "total_frames": 1700,
        "scenes": [
            {
                "id": "S01Hook",
                "script_line_id": "l1_hook",
                "durationInFrames": 220,
                "banner_text": "KENAPA ES BATU MENGAPUNG?",
                "environment_id": "cozy-bedroom",
                "scene_purpose": "Domestic bedroom hook with bedside glass of water",
                "background_type": "environment_scene",
                "transition_in": "none",
                "transition_out": "pageTurn",
                "transition_cut": "none",
                "camera_motion": {
                    "yaw": 8,
                    "push": 1.08,
                    "origin": [540, 1180],
                    "motion_type": "orbit"
                },
                "character_position": {
                    "x": 360,
                    "y": 1380,
                    "size": 240,
                    "state": "curious",
                    "face": 1
                },
                "character_movement": {
                    "type": "enter_left",
                    "startFrame": 0,
                    "duration": 30,
                    "easing": "easeOut"
                },
                "interaction_type": "point_at",
                "interaction_target": {"x": 710, "y": 1260},
                "interaction_timing": {"startFrame": 35, "duration": 50},
                "text_elements": [
                    {
                        "id": "hook_badge",
                        "text": "FAKTA ANOMALI #1",
                        "type": "badge",
                        "priority": 1,
                        "preferredX": 750,
                        "preferredY": 900
                    }
                ],
                "continuity_notes": "Cat walks in from left side of bedroom"
            },
            {
                "id": "S02LabReaction",
                "script_line_id": "l2_lab",
                "durationInFrames": 240,
                "banner_text": "MOLEKUL HEKSAGONAL MEMUAI",
                "environment_id": "science-laboratory",
                "scene_purpose": "Molecular lattice expansion and physical reaction",
                "background_type": "scientific_visualization",
                "transition_in": "pageTurn",
                "transition_out": "none",
                "transition_cut": "pageTurn",
                "camera_motion": {
                    "yaw": 2,
                    "push": 1.03,
                    "origin": [540, 1100],
                    "motion_type": "orbit"
                },
                "character_position": {
                    "x": 260,
                    "y": 1400,
                    "size": 220,
                    "state": "explaining",
                    "face": 1
                },
                "character_movement": {
                    "type": "walk",
                    "startX": 180,
                    "endX": 260,
                    "startFrame": 0,
                    "duration": 25
                },
                "reaction_trigger": 45,
                "reaction_animation": "recoil_jump",
                "visualization_event": "expansion",
                "visualization_timing": 45,
                "visualization_bounds": {"x": 460, "y": 600, "width": 560, "height": 580},
                "text_elements": [
                    {
                        "id": "lbl_hydrogen",
                        "text": "IKATAN HIDROGEN",
                        "type": "label",
                        "priority": 2,
                        "preferredX": 600,
                        "preferredY": 540,
                        "targetPoint": {"x": 680, "y": 620}
                    }
                ],
                "continuity_notes": "Recoil jump synchronizes with hexagonal lattice expansion"
            },
            {
                "id": "S03Outro",
                "script_line_id": "l3_outro",
                "durationInFrames": 180,
                "banner_text": "SAINS ANOMALI AIR",
                "environment_id": "cozy-bedroom",
                "scene_purpose": "Takeaway celebration and outro",
                "background_type": "return_scene",
                "transition_in": "hardCut",
                "transition_out": "none",
                "character_position": {
                    "x": 540,
                    "y": 1380,
                    "size": 260,
                    "state": "celebrating",
                    "face": 1
                },
                "interaction_type": "celebrate",
                "continuity_notes": "Return to bedroom, confident gesture"
            }
        ]
    }

    ok, errors = validate_artifact("storyboard", extended_storyboard)

    if not ok:
        print(f"Validation failed with errors: {errors}", file=sys.stderr)
        sys.exit(1)

    print("  [PASS] test_extended_storyboard_schema passed.")


def main():
    print("=================================================================")
    print("  Running Storyboard Extended Schema Validation Test Suite")
    print("=================================================================")
    test_extended_storyboard_schema()
    print(">> Extended Schema validation PASSED successfully!")
    print("=================================================================")


if __name__ == "__main__":
    main()
