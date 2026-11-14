"""
Cinematography & Camera Shot Taxonomy for 9:16 Vertical Papercraft Video.
Defines 14 distinct shot types, vertical mobile safe zones, depth layering planes,
and camera positioning rules.
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field


@dataclass
class CameraShot:
    code: str
    name: str
    description: str
    narrative_purpose: str
    framing_scale: float
    camera_origin: Tuple[int, int]
    camera_yaw: float
    camera_push: float
    depth_planes: List[str]


CAMERA_SHOT_LIBRARY: Dict[str, CameraShot] = {
    "extreme_wide_shot": CameraShot(
        code="EWS",
        name="Extreme Wide Shot",
        description="Expansive macroscopic perspective showing colossal environment with presenter miniature.",
        narrative_purpose="Establishing massive scale, celestial systems, weather phenomena, or ancient landscape.",
        framing_scale=0.75,
        camera_origin=(540, 960),
        camera_yaw=1.0,
        camera_push=1.02,
        depth_planes=["vast_background", "horizon", "tiny_midground"]
    ),
    "wide_shot": CameraShot(
        code="WS",
        name="Wide Shot",
        description="Full environmental stage with presenter and primary physical apparatus in clear context.",
        narrative_purpose="Standard establishment of scene space, multi-component demonstrations, and lab workbench.",
        framing_scale=1.0,
        camera_origin=(540, 1130),
        camera_yaw=4.0,
        camera_push=1.05,
        depth_planes=["background_room", "workbench_midground", "mascot"]
    ),
    "medium_wide_shot": CameraShot(
        code="MWS",
        name="Medium Wide Shot",
        description="Presenter visible from knees up; apparatus fills dominant center stage.",
        narrative_purpose="Transitioning from room establishment to active experimental interaction.",
        framing_scale=1.12,
        camera_origin=(540, 1100),
        camera_yaw=3.0,
        camera_push=1.04,
        depth_planes=["defocused_background", "active_apparatus", "presenter"]
    ),
    "medium_shot": CameraShot(
        code="MS",
        name="Medium Shot",
        description="Presenter from waist up, perfectly balanced beside central papercraft mechanism.",
        narrative_purpose="Core explanatory beats; presenter points directly at physical model components.",
        framing_scale=1.25,
        camera_origin=(500, 1150),
        camera_yaw=3.5,
        camera_push=1.05,
        depth_planes=["subtle_vignette_bg", "focal_mechanism", "presenter_half_body"]
    ),
    "medium_close_up": CameraShot(
        code="MCU",
        name="Medium Close-Up",
        description="Presenter from chest up with wire spectacles prominent, secondary prop behind.",
        narrative_purpose="Emotional curiosity, eureka realization, or direct conversational dialogue to viewer.",
        framing_scale=1.45,
        camera_origin=(460, 1200),
        camera_yaw=2.0,
        camera_push=1.06,
        depth_planes=["blurred_lab_bg", "reaction_mascot", "ambient_sparkles"]
    ),
    "close_up": CameraShot(
        code="CU",
        name="Close-Up",
        description="Tight focus on character facial reaction or focal experimental component.",
        narrative_purpose="Highlighting dramatic reaction (shock, intense concentration) or intricate prop details.",
        framing_scale=1.8,
        camera_origin=(540, 1220),
        camera_yaw=1.5,
        camera_push=1.07,
        depth_planes=["deep_depth_of_field", "focal_subject"]
    ),
    "extreme_close_up": CameraShot(
        code="ECU",
        name="Extreme Close-Up (Macro)",
        description="Microscopic/macro view: needle vibrating on dial, single droplet impact, molecular bond.",
        narrative_purpose="Revealing invisible scientific mechanisms, micro-reactions, or precise physical evidence.",
        framing_scale=2.4,
        camera_origin=(540, 780),
        camera_yaw=0.5,
        camera_push=1.08,
        depth_planes=["macro_specimen", "micro_texture_paper_grains"]
    ),
    "over_the_shoulder": CameraShot(
        code="OTS",
        name="Over-the-Shoulder",
        description="Looking past presenter's paper coat shoulder toward the apparatus or discovery.",
        narrative_purpose="Inviting the audience into the researcher's perspective, observing an unfolding reaction.",
        framing_scale=1.35,
        camera_origin=(520, 1180),
        camera_yaw=5.0,
        camera_push=1.05,
        depth_planes=["foreground_shoulder_cutout", "target_apparatus", "distant_wall"]
    ),
    "low_angle": CameraShot(
        code="LA",
        name="Low-Angle Shot",
        description="Camera tilted upward from floor level, looking up at imposing towering phenomenon.",
        narrative_purpose="Emphasizing monumental power, massive atmospheric pressure, lightning, or giant structures.",
        framing_scale=1.2,
        camera_origin=(540, 1420),
        camera_yaw=6.0,
        camera_push=1.07,
        depth_planes=["floor_paper_foreground", "towering_reaction", "high_ceiling"]
    ),
    "high_angle": CameraShot(
        code="HA",
        name="High-Angle Shot",
        description="Camera elevated and looking downward onto the laboratory table or terrain.",
        narrative_purpose="Providing analytical overview of complex experimental layout or vulnerable situation.",
        framing_scale=1.15,
        camera_origin=(540, 850),
        camera_yaw=2.0,
        camera_push=1.04,
        depth_planes=["table_surface_grid", "apparatus_overview", "floor_shadows"]
    ),
    "birds_eye_view": CameraShot(
        code="BEV",
        name="Bird's-Eye View (Blueprint)",
        description="Orthographic top-down plan view directly perpendicular to the staging surface.",
        narrative_purpose="Mapping schematic paths, electron circuits, anatomical routes, or geographic tracks.",
        framing_scale=1.0,
        camera_origin=(540, 960),
        camera_yaw=0.0,
        camera_push=1.03,
        depth_planes=["blueprint_grid", "flat_paper_cutouts", "overhead_drop_shadows"]
    ),
    "dutch_angle": CameraShot(
        code="DA",
        name="Dutch Angle (Tilted)",
        description="Camera dynamically canted (7° to 12° tilt) to induce cognitive disorientation.",
        narrative_purpose="Dramatic anomaly, sudden brain freeze pain, paradoxical scientific result, or hazard.",
        framing_scale=1.3,
        camera_origin=(540, 1100),
        camera_yaw=-8.0,
        camera_push=1.06,
        depth_planes=["canted_background", "destabilized_subject", "tension_lines"]
    ),
    "pov_shot": CameraShot(
        code="POV",
        name="Point of View (First-Person)",
        description="Looking directly through character wire spectacles, circular microscope bezel, or telescope lens.",
        narrative_purpose="Direct first-person discovery, placing viewer in the shoes of the scientist making a breakthrough.",
        framing_scale=1.6,
        camera_origin=(540, 960),
        camera_yaw=0.0,
        camera_push=1.05,
        depth_planes=["bezel_mask_foreground", "magnified_specimen", "ambient_reticle"]
    ),
    "symmetrical_composition": CameraShot(
        code="SYM",
        name="Symmetrical Master Composition",
        description="Strictly centered, balanced Wes Anderson-style framing with dual comparative elements.",
        narrative_purpose="Authoritative proof beat, balanced comparison (cold vs hot, before vs after), iconic finale.",
        framing_scale=1.05,
        camera_origin=(540, 1080),
        camera_yaw=0.0,
        camera_push=1.04,
        depth_planes=["centered_symmetry_axis", "dual_comparative_models", "grounded_presenter"]
    )
}


class CinematographyRules:
    """Safe zones and compositional boundaries for 1080x1920 9:16 vertical video."""

    WIDTH = 1080
    HEIGHT = 1920

    # Vertical safe boundaries
    BANNER_ZONE = (0, 420)
    STAGE_ACTION_ZONE = (420, 1580)
    CAPTION_ZONE = (1420, 1920)

    SAFE_ZONES = {
        "header_banner": (0, 420),
        "stage_action": (420, 1580),
        "captions": (1420, 1920)
    }

    # Presenter standard placement
    PRESENTER_FLOOR_Y = 1380
    PRESENTER_X_RANGE = (240, 840)

    PRESENTER_BOUNDS = {
        "floor_y": 1380,
        "x_range": (240, 840)
    }

    @classmethod
    def get_shot(cls, shot_code_or_name: str) -> CameraShot:
        key = shot_code_or_name.lower().replace("-", "_").replace(" ", "_")
        for k, shot in CAMERA_SHOT_LIBRARY.items():
            if key in (k, shot.code.lower(), shot.name.lower()):
                return shot
        # Default fallback
        return CAMERA_SHOT_LIBRARY["wide_shot"]


# Also register uppercase shot codes directly for ergonomic dictionary access
for _shot in list(CAMERA_SHOT_LIBRARY.values()):
    CAMERA_SHOT_LIBRARY[_shot.code] = _shot
