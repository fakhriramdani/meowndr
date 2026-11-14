"""
Professional Image Prompt Engineering Layer for @meowndr Papercraft Explainer.
Constructs rigorous 7-section structured prompts for cinematic 2D papercraft illustrations.
Enforces zero vague templates and strict negative constraints.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .story_visual_analyzer import SceneVisualBrief
from .visual_bible import VisualBible
from .visual_identity import VisualIdentitySystem
from .character_consistency import MascotIdentity


@dataclass
class StructuredPrompt:
    scene_id: str
    subject_section: str
    scene_section: str
    composition_section: str
    lighting_section: str
    art_direction_section: str
    technical_section: str
    negative_section: str

    def build_full_prompt(self) -> str:
        """Combines all 7 structured sections into a comprehensive art-directed prompt."""
        return (
            f"[SUBJECT]: {self.subject_section}\n\n"
            f"[SCENE & ENVIRONMENT]: {self.scene_section}\n\n"
            f"[COMPOSITION & CINEMATOGRAPHY]: {self.composition_section}\n\n"
            f"[LIGHTING & SHADOWS]: {self.lighting_section}\n\n"
            f"[ART DIRECTION & TEXTURE]: {self.art_direction_section}\n\n"
            f"[TECHNICAL SPECIFICATIONS]: {self.technical_section}\n\n"
            f"[NEGATIVE CONSTRAINTS]: {self.negative_section}"
        )


class PromptEngineer:
    """Transforms scene briefs and visual bibles into cinematic structured prompts."""

    STANDARD_NEGATIVE_PROMPT = (
        "photorealistic, 3D CGI rendering, glossy plastic, raytracing, smooth airbrushed gradient, "
        "distorted anatomy, extra limbs, deformed paws, human presenter, human face, realistic fur, "
        "baked-in text, typography, letters, words, subtitles, numbers, watermark, artist signature, "
        "low resolution, blurry cutouts, pixelated edges, cluttered trash, random floating decor, "
        "awkward framing, subject cropped out of safe zone, flat single-layer graphic."
    )

    @classmethod
    def generate_prompt(
        cls,
        brief: SceneVisualBrief,
        bible: VisualBible,
        isolated_object: bool = False
    ) -> StructuredPrompt:
        """Generates a complete 7-section structured prompt."""
        shot = brief.camera_shot

        # 1. Subject
        char_desc = MascotIdentity.get_prompt_description(brief.presenter_state)
        subject = (
            f"{brief.visual_subject}. "
            f"Embodied through: {brief.visual_metaphor}. "
            f"Accompanied by presenter: {char_desc}. Presenter is {brief.presenter_action}."
        )
        if isolated_object:
            subject = f"Isolated scientific papercraft prop: {brief.visual_subject}. Clean die-cut silhouette."

        # 2. Scene
        scene = (
            f"Setting: {brief.environment_id.replace('-', ' ').title()} environment. "
            f"{brief.depth_planes.get('background', 'Architectural paper wall with atmospheric depth')}. "
            f"Atmospheric mood reflecting {brief.intended_emotion}. "
            f"Supporting elements: {brief.depth_planes.get('midground', 'Supporting lab instruments')}."
        )
        if isolated_object:
            scene = "Pure transparent background with zero environment clutter or baked room artifacts."

        # 3. Composition
        composition = (
            f"Camera framing: {shot.name} ({shot.code}), scale factor {shot.framing_scale}x. "
            f"Camera perspective: {shot.description}. "
            f"Vertical 9:16 mobile canvas. Focal point centered in Stage Action Zone (y: 600-1100px). "
            f"Header Banner Zone (top 420px) and Caption Zone (bottom 500px) kept strictly uncluttered. "
            f"Clear depth separation across three paper z-planes: foreground framing, midground demonstration, background wall."
        )

        # 4. Lighting
        lighting = (
            "Directional key light from top-left (angle 45°). "
            "Casts realistic tiered paper drop shadows (rgba(15,23,42,0.24) with soft 8-16px edge blur) "
            "between stacked cardstock layers. Highlights along upper-left paper cut contours with 1px lighter rim. "
            "Warm ambient fill light; zero harsh black voids or blown-out highlights."
        )

        # 5. Art Direction
        palette_colors = bible.color_palette.get("all_colors", ["#0F172A", "#0284C7", "#06B6D4", "#FDFBF7"])
        palette_str = ", ".join(palette_colors[:5])
        art_direction = (
            f"Art Style: {bible.illustration_style}. "
            f"Material: Heavyweight 280gsm matte textured construction paper collage. "
            f"Textures: Visible 10% organic cellulose paper grain and micro-deckle scissor edges. "
            f"Shading constructed strictly from tiered cut paper strips in darker tones, never blended gradients. "
            f"Color Harmony: Coordinated palette [{palette_str}]. One dominant warm orange accent (#EA580C) on mascot."
        )

        # 6. Technical Requirements
        technical = (
            "Canvas Dimensions: 1080x1920 pixels (9:16 vertical vertical video standard). "
            "Asset Format: High-fidelity PNG with 24-bit RGB (RGBA with alpha transparency for isolated props). "
            "Compositional Safe Zones strictly observed. Mobile legibility verified: main subject instantly readable at 2-inch phone preview."
        )

        # 7. Negative Constraints
        negative = cls.STANDARD_NEGATIVE_PROMPT

        return StructuredPrompt(
            scene_id=brief.scene_id,
            subject_section=subject,
            scene_section=scene,
            composition_section=composition,
            lighting_section=lighting,
            art_direction_section=art_direction,
            technical_section=technical,
            negative_section=negative
        )
