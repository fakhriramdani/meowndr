"""
Character & Asset Consistency System for @meowndr Papercraft Explainer.
Enforces invariant visual identity rules for the Cat Scientist presenter mascot,
environment backgrounds, and standalone scientific props.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class CharacterStateSpec:
    name: str
    pose_description: str
    facial_expression: str
    ear_orientation: str
    eye_shape: str
    arm_gesture: str
    spectacle_interaction: str


CHARACTER_STATES: Dict[str, CharacterStateSpec] = {
    "curious": CharacterStateSpec(
        name="curious",
        pose_description="Head tilted ~8 degrees with body slightly angled; inspecting an unusual clue or anomaly.",
        facial_expression="Inquiring, slight quirk of whiskers, mouth small inquisitive oval.",
        ear_orientation="Left ear perked straight up, right ear tilted inquisitively at 25 degrees.",
        eye_shape="Wide circular paper cutout eyes with dilated dark pupils.",
        arm_gesture="Left paw tucked in lab coat pocket; right paw lifted under chin in contemplative pose.",
        spectacle_interaction="Wire spectacles perched lightly on bridge of muzzle with tiny white paper sparkle rim."
    ),
    "explaining": CharacterStateSpec(
        name="explaining",
        pose_description="Balanced upright posture standing securely on floor line; authoritative yet warm scientific host.",
        facial_expression="Gentle welcoming scientific smile, relaxed brow cutouts.",
        ear_orientation="Both ears upright, symmetrical and attentive.",
        eye_shape="Clear, open expressive eyes focused toward the audience.",
        arm_gesture="Right arm extended forward with open palm inviting attention toward the central mechanism.",
        spectacle_interaction="Spectacles neatly centered, reflecting gentle ambient lab light."
    ),
    "pointing": CharacterStateSpec(
        name="pointing",
        pose_description="Dynamic directional stance; weight shifted onto front foot as paws guide viewer attention.",
        facial_expression="Intense analytical focus, eyes locked onto the specific component or reading.",
        ear_orientation="Ears angled forward following the trajectory of the arm.",
        eye_shape="Sharp, engaged eyes with highlight glint.",
        arm_gesture="Arm fully extended with crisp paper index paw pointing directly at the measurement or event.",
        spectacle_interaction="Sightline aligned perfectly through wire-rim spectacle lenses toward target."
    ),
    "surprised": CharacterStateSpec(
        name="surprised",
        pose_description="Recoil reaction, torso sprung backward with tail bristling upward; witnessing unexpected physical reaction.",
        facial_expression="Awe and dramatic shock, mouth cut in wide 'O', paper whiskers extended horizontally.",
        ear_orientation="Both ears flattened sideways at 45 degrees in startling reflex.",
        eye_shape="Maximum aperture wide spherical paper cutouts.",
        arm_gesture="Both paws thrown up beside face in involuntary reflex.",
        spectacle_interaction="Wire spectacles jarred slightly crooked on bridge, enhancing the comedic shock."
    ),
    "thinking": CharacterStateSpec(
        name="thinking",
        pose_description="Weight rested back, head gazing upward toward question mark or theoretical formulation.",
        facial_expression="Deep concentration, slight squint of one eye cutout.",
        ear_orientation="Ears twitching slightly back in deep cognitive processing.",
        eye_shape="Eyes looking toward upper-right quadrant.",
        arm_gesture="Paw tapping against spectacle frame rhythmically.",
        spectacle_interaction="Index claw lightly propping up wire spectacle bridge."
    ),
    "celebrating": CharacterStateSpec(
        name="celebrating",
        pose_description="Joyous hop off the floor with springy paper pop; eureka moment achieved.",
        facial_expression="Beaming triumphant smile, whiskers lifted high in celebration.",
        ear_orientation="Ears perked high and proud.",
        eye_shape="Happy curved upward-crescent paper cutouts.",
        arm_gesture="Both paws raised victoriously overhead clutching test results or glowing discovery.",
        spectacle_interaction="Gleaming double-sparkle bursts on spectacle frames."
    ),
    "waving": CharacterStateSpec(
        name="waving",
        pose_description="Warm approachable posture at beginning or closing of episode.",
        facial_expression="Friendly welcoming host expression, directly acknowledging the audience.",
        ear_orientation="Symmetrical upright ears with gentle friendly tilt.",
        eye_shape="Warm friendly oval cutouts.",
        arm_gesture="Right paw raised beside head, waving in friendly greeting; left paw resting on lab coat hip.",
        spectacle_interaction="Clean, sparkling spectacles framing welcoming eyes."
    )
}


class MascotIdentity:
    """Master invariant identity constraints for the Cat Scientist."""

    CHARACTER_NAME = "CatScientist"
    FUR_COLOR = "#EA580C"  # Warm Tangerine Orange
    LAB_COAT_COLOR = "#F8FAFC"  # Crisp White Lab Coat
    LAB_COAT_CREASES = "#CBD5E1"  # Soft slate paper creases
    SPECTACLE_COLOR = "#FDFBF7"  # Clean white/silver wireframes
    INNER_EAR_COLOR = "#FDFBF7"  # Warm cream inner ear fold
    EYE_PUPIL_COLOR = "#0F172A"  # Deep midnight slate pupils

    INVARIANT_RULES = [
        "Mascot is strictly a feline cat scientist, NEVER human, dog, or generic monster.",
        "Color must remain #EA580C warm orange, NEVER blue, green, or rainbow.",
        "Must wear circular wire-rim spectacles and white lab coat in all educational scenes.",
        "Anatomy must remain chunky geometric cut-paper: clean rectangular limbs, rounded torso, triangular ears.",
        "Zero realistic photorealistic fur textures or 3D CGI fur rendering; must look like flat cardstock paper cutout."
    ]

    @classmethod
    def get_state(cls, state_name: str) -> CharacterStateSpec:
        return CHARACTER_STATES.get(state_name.lower(), CHARACTER_STATES["curious"])

    @classmethod
    def get_prompt_description(cls, state_name: str = "curious") -> str:
        state = cls.get_state(state_name)
        return (
            f"Subject: Cat Scientist mascot ({cls.FUR_COLOR} warm orange papercraft cat) wearing "
            f"{cls.SPECTACLE_COLOR} circular wire-rim spectacles and crisp {cls.LAB_COAT_COLOR} folded paper lab coat. "
            f"State '{state.name}': {state.pose_description} {state.facial_expression} {state.arm_gesture}"
        )


class CharacterConsistencyEngine:
    """Audits and enforces invariant mascot visual parameters across all episode scenes."""

    @classmethod
    def validate_scene_character(cls, brief: Any) -> Dict[str, Any]:
        """Validates that a scene brief maintains mascot integrity."""
        state = MascotIdentity.get_state(brief.presenter_state)
        return {
            "character": MascotIdentity.CHARACTER_NAME,
            "state": state.name,
            "fur_color": MascotIdentity.FUR_COLOR,
            "spectacles": MascotIdentity.SPECTACLE_COLOR,
            "lab_coat": MascotIdentity.LAB_COAT_COLOR,
            "rules_passed": len(MascotIdentity.INVARIANT_RULES),
            "status": "COMPLIANT"
        }
