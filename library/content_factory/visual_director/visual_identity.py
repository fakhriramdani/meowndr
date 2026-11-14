"""
Visual Identity & Master Art Direction Standards for @meowndr Papercraft Explainer.
Defines primary/secondary art styles, color palettes, lighting rules, textures,
character design language, and composition principles.
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class ColorPalette:
    name: str
    primary: str
    secondary: str
    accent: str
    paper_cream: str
    paper_kraft: str
    shadow_tone: str
    all_colors: List[str] = field(default_factory=list)


# Master Niche Color Palettes
NICHE_PALETTES: Dict[str, ColorPalette] = {
    "science": ColorPalette(
        name="Scientific Discovery",
        primary="#0F172A",      # Deep Midnight Slate
        secondary="#0284C7",    # Cerulean Blue
        accent="#06B6D4",       # Electric Cyan
        paper_cream="#FDFBF7",  # Crisp Archival Paper
        paper_kraft="#D5C5B0",  # Cardboard Substrate
        shadow_tone="#090D16",
        all_colors=["#0F172A", "#0284C7", "#06B6D4", "#F59E0B", "#FDFBF7", "#D5C5B0"]
    ),
    "history": ColorPalette(
        name="Ancient Chronicles",
        primary="#7C2D12",      # Burnished Terracotta
        secondary="#B45309",    # Ancient Bronze
        accent="#1E3A8A",       # Lapis Lazuli
        paper_cream="#F5EBE0",  # Ancient Papyrus Parchment
        paper_kraft="#C4B5A5",  # Aged Silt Cardstock
        shadow_tone="#1C100B",
        all_colors=["#7C2D12", "#B45309", "#1E3A8A", "#D97706", "#F5EBE0", "#C4B5A5"]
    ),
    "geography": ColorPalette(
        name="Earth & Ocean Expeditions",
        primary="#166534",      # Deep Forest Green
        secondary="#0D9488",    # Coastal Turquoise
        accent="#FEF08A",       # Sunlight Accent
        paper_cream="#FAF5EE",  # Sandbar Cream
        paper_kraft="#E7D3B6",  # Dunes Kraft
        shadow_tone="#0B1C12",
        all_colors=["#166534", "#0D9488", "#0284C7", "#FEF08A", "#FAF5EE", "#E7D3B6"]
    ),
    "technology": ColorPalette(
        name="Quantum Photonics & Cybernetic Lab",
        primary="#0B0F19",      # Obsidian Carbon
        secondary="#7C3AED",    # Quantum Violet
        accent="#00F0FF",       # Laser Neon Cyan
        paper_cream="#F8FAFC",  # Cleanroom Cellulose
        paper_kraft="#94A3B8",  # Slate Anodized Paper
        shadow_tone="#05070C",
        all_colors=["#0B0F19", "#7C3AED", "#00F0FF", "#10B981", "#F8FAFC", "#94A3B8"]
    ),
    "mystery": ColorPalette(
        name="Nocturnal Cryptic Evidence",
        primary="#1E1B4B",      # Deep Cosmic Indigo
        secondary="#581C87",    # Twilight Velvet
        accent="#F59E0B",       # Glowing Lantern Amber
        paper_cream="#F1F5F9",  # Moonlit Paper
        paper_kraft="#64748B",  # Fog Kraft
        shadow_tone="#0D0B24",
        all_colors=["#1E1B4B", "#581C87", "#F59E0B", "#CBD5E1", "#F1F5F9", "#64748B"]
    ),
    "psychology": ColorPalette(
        name="Cognitive Neuroscience & Mind",
        primary="#1E293B",      # Slate Neural
        secondary="#4338CA",    # Cerebral Indigo
        accent="#F43F5E",       # Synaptic Rose
        paper_cream="#FDFBF7",  # Clean Thinking Cream
        paper_kraft="#CBD5E1",  # Neutral Grey Board
        shadow_tone="#0F172A",
        all_colors=["#1E293B", "#4338CA", "#F43F5E", "#C084FC", "#FDFBF7", "#CBD5E1"]
    )
}


class VisualIdentitySystem:
    """Master Art Direction rules and design specifications."""

    PRIMARY_ART_STYLE = (
        "Artisanal multi-layered 2D construction paper collage with tactile stop-motion aesthetics. "
        "Every element appears physically die-cut or scissor-cut from heavyweight matte paper cardstock (250-300 gsm) "
        "featuring subtle deckle edges, 1px lighter top-left paper fiber rims, and soft, realistic multi-plane drop shadows."
    )

    SECONDARY_INFLUENCES = (
        "Modern Scandinavian educational editorial collage, mid-century architectural blueprints, "
        "Wes Anderson centered and deliberate geometric framing, and tactile stop-motion miniatures."
    )

    LIGHTING_SPECIFICATION = (
        "Directional key light positioned at top-left (angle 45° elevation, 35° azimuth). "
        "Casts gentle, tiered paper drop shadows (rgba(15, 23, 42, 0.22) with 6-12px diffusion). "
        "Zero digital airbrushing or harsh computer-generated gradient fills; shading is constructed exclusively "
        "by stacking darker tone cutout strips beneath lit surfaces."
    )

    TEXTURE_SPECIFICATION = (
        "Subtle fibrous paper grain (10-12% opacity micro-stipple). "
        "Organic paper deckle edges with micro-chatter along cut boundaries. "
        "Matte non-gloss finish; light bounces naturally with diffuse paper reflectivity."
    )

    CHARACTER_DESIGN_LANGUAGE = (
        "Mascot: Cat Scientist. Warm orange silhouette (#EA580C) constructed from clean geometric paper forms. "
        "Wearing circular wire-rim spectacles (#FDFBF7), a crisp white laboratory coat with paper-folded lapels, "
        "and expressive triangular ears. Communicates emotion through oversized eyes, ear rotation, and pose."
    )

    COMPOSITION_PRINCIPLES = (
        "Strict 9:16 vertical canvas (1080x1920). "
        "Three distinct depth planes: Foreground silhouette/framing (z=1.0), Midground focal demonstration (z=0.5), "
        "and Background atmospheric environment (z=0.0). "
        "Header safe zone (y < 420px) and Caption safe zone (y > 1420px) kept visually uncluttered."
    )

    @classmethod
    def get_palette(cls, niche: str) -> ColorPalette:
        return NICHE_PALETTES.get(niche.lower(), NICHE_PALETTES["science"])
