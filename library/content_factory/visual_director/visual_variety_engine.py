"""
Visual Variety Engine for @meowndr Papercraft Explainer.
Tracks episode scene history to prevent visual monotony, enforcing dynamic cinematic
variety across shot types, camera angles, color accents, and staging layouts.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from .cinematography import CAMERA_SHOT_LIBRARY, CameraShot


@dataclass
class SceneVisualFingerprint:
    scene_id: str
    shot_type: str
    camera_angle: str
    environment_id: str
    presenter_state: str
    presenter_position: str  # "left", "center", "right"
    dominant_accent_color: str
    focal_subject_type: str  # "apparatus", "macro_molecule", "environment", "character_reaction"


class VisualVarietyEngine:
    """Maintains scene memory and suggests cinematic variations to avoid visual fatigue."""

    def __init__(self):
        self.history: List[SceneVisualFingerprint] = []

    def record_scene(self, fingerprint: SceneVisualFingerprint):
        self.history.append(fingerprint)

    def get_last_scene(self) -> Optional[SceneVisualFingerprint]:
        return self.history[-1] if self.history else None

    def validate_variety(self, candidate_shot: str, candidate_pos: str, candidate_state: str) -> Tuple[bool, List[str]]:
        """Checks if candidate choice creates monotonous consecutive repetition."""
        warnings = []
        if not self.history:
            return True, warnings

        last = self.history[-1]

        # 1. Consecutive identical shot type check
        if candidate_shot.lower() == last.shot_type.lower():
            warnings.append(
                f"Consecutive identical shot type '{candidate_shot}' detected. "
                f"Alternate camera scale to keep mobile viewer engaged."
            )

        # 2. Consecutive identical presenter position check
        if candidate_pos.lower() == last.presenter_position.lower() and candidate_pos.lower() != "center":
            warnings.append(
                f"Presenter position '{candidate_pos}' repeated consecutively. Shift lateral staging."
            )

        # 3. Consecutive identical presenter state check
        if candidate_state.lower() == last.presenter_state.lower():
            warnings.append(
                f"Presenter emotion '{candidate_state}' repeated consecutively. Vary character reaction."
            )

        return len(warnings) == 0, warnings

    def recommend_next_shot(self, scene_purpose: str, beat_index: int, total_beats: int) -> CameraShot:
        """Selects an optimal, variety-maximizing camera shot based on narrative beat and history."""
        last = self.get_last_scene()
        last_shot = last.shot_type.lower() if last else ""

        # Beat-driven cinematic progression
        if beat_index == 0:
            # Hook: Wide establishing or dramatic Dutch Angle / Medium Wide
            return CAMERA_SHOT_LIBRARY["wide_shot"]
        elif beat_index == 1:
            # Setup / Problem: Medium shot introducing central mechanism
            return CAMERA_SHOT_LIBRARY["medium_shot"]
        elif beat_index == 2:
            # Mechanism / Explanation 1: Extreme Close-Up (macro evidence) or Bird's Eye
            if last_shot != "extreme_close_up":
                return CAMERA_SHOT_LIBRARY["extreme_close_up"]
            return CAMERA_SHOT_LIBRARY["over_the_shoulder"]
        elif beat_index == 3:
            # Climax / High-energy proof: Low Angle or Dutch Angle (anomaly/shock)
            if "anomaly" in scene_purpose.lower() or "shock" in scene_purpose.lower() or "freeze" in scene_purpose.lower():
                return CAMERA_SHOT_LIBRARY["dutch_angle"]
            return CAMERA_SHOT_LIBRARY["low_angle"]
        elif beat_index == total_beats - 1:
            # Outro / CTA: Symmetrical master composition or warm medium close-up
            if last_shot != "symmetrical_composition":
                return CAMERA_SHOT_LIBRARY["symmetrical_composition"]
            return CAMERA_SHOT_LIBRARY["medium_close_up"]
        else:
            # General alternating rotation
            pool = ["medium_shot", "over_the_shoulder", "close_up", "medium_wide_shot", "high_angle"]
            for candidate_key in pool:
                if candidate_key != last_shot:
                    return CAMERA_SHOT_LIBRARY[candidate_key]

        return CAMERA_SHOT_LIBRARY["medium_shot"]
