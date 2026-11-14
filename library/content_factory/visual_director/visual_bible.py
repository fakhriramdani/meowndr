"""
Episode Visual Bible Generator & State Persistence for @meowndr Papercraft Explainer.
Generates an episode-specific visual contract governing color palettes, lighting,
character wardrobe, environments, camera language, and visual continuity rules.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from .visual_identity import VisualIdentitySystem, ColorPalette
from .cinematography import CinematographyRules


@dataclass
class VisualBible:
    episode_slug: str
    topic: str
    niche: str
    main_visual_concept: str
    metaphor_world: str
    color_palette: Dict[str, Any]
    lighting_direction: str
    character_appearance: Dict[str, Any]
    environments_used: List[Dict[str, Any]]
    camera_language: Dict[str, Any]
    illustration_style: str
    recurring_visual_motifs: List[str]
    visual_continuity_rules: List[str]
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        envs_md = "\n".join([f"- **`{e['id']}`** ({e.get('name', e['id'])}): {e.get('mood', 'Standard mood')}" for e in self.environments_used])
        motifs_md = "\n".join([f"- {m}" for m in self.recurring_visual_motifs])
        rules_md = "\n".join([f"{idx+1}. {r}" for idx, r in enumerate(self.visual_continuity_rules)])
        colors = self.color_palette.get("all_colors", [])
        colors_str = ", ".join([f"`{c}`" for c in colors])

        return f"""# Episode Visual Bible: {self.topic}

**Episode Slug:** `{self.episode_slug}`  
**Niche:** `{self.niche}`  
**Generated At:** `{self.created_at}`  

---

## 1. Main Visual Concept & Metaphor World
- **Visual Concept**: {self.main_visual_concept}
- **Metaphor World**: {self.metaphor_world}
- **Primary Art Style**: {self.illustration_style}

---

## 2. Color Palette & Atmospheric Lighting
- **Palette Name**: {self.color_palette.get('name', 'Custom Palette')}
- **Hex Codes**: {colors_str}
- **Primary**: `{self.color_palette.get('primary')}` | **Secondary**: `{self.color_palette.get('secondary')}` | **Accent**: `{self.color_palette.get('accent')}`
- **Lighting Direction**: {self.lighting_direction}

---

## 3. Character Design Language & Wardrobe
- **Mascot**: `{self.character_appearance.get('name', 'CatScientist')}`
- **Fur Color**: `{self.character_appearance.get('fur_color')}`
- **Wardrobe**: {self.character_appearance.get('wardrobe')}
- **Accessories**: {self.character_appearance.get('accessories')}
- **Expression Rules**: {self.character_appearance.get('expression_rules')}

---

## 4. Environments & Staging Architecture
{envs_md}

- **Floor Line**: `y = {self.camera_language.get('floor_y', 1380)}px`
- **Safe Zones**:
  - Header Banner: `0 - 420px`
  - Active Stage: `420 - 1580px`
  - Captions / UI: `1420 - 1920px`

---

## 5. Recurring Visual Motifs
{motifs_md}

---

## 6. Strict Visual Continuity Rules
{rules_md}
"""


class VisualBibleGenerator:
    """Creates and persists episode-level visual bibles."""

    @classmethod
    def generate_bible(
        cls,
        episode_slug: str,
        topic: str,
        niche: str,
        script_summary: str,
        default_env: str = "science-laboratory"
    ) -> VisualBible:
        import datetime
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
        palette = VisualIdentitySystem.get_palette(niche)

        # Metaphor world formulation
        if "hujan" in topic.lower() or "petrichor" in topic.lower():
            concept = "Microscopic Cavitation & Natural Aerosol Dynamics"
            metaphor = "Rain-slicked urban asphalt contrasting with subterranean soil microbial laboratory."
            motifs = [
                "Layered paper raindrop impact crowns with expanding splash droplets",
                "Perforated soil aeration cross-sections with floating microscopic aerosol curls",
                "Dial indicator aroma concentration gauges with oscillating needles",
                "Four-point papercut science sparkle bursts (#06B6D4)"
            ]
        elif "freeze" in topic.lower() or "es" in topic.lower():
            concept = "Cranial Vascular Constriction & Thermal Defense Reflex"
            metaphor = "Home kitchen beverage table transitioning into stylized cranial neurology diorama."
            motifs = [
                "Rising red mercury thermometer tube with thermal wave ripples",
                "Expanding and contracting accordion paper blood vessel rings",
                "Glowing trigeminal nerve paper filaments pulsing with alert signals",
                "Faceted icy paper snowflake crystal lattices"
            ]
        elif "aleksandria" in topic.lower() or "sejarah" in niche.lower():
            concept = "Ancient Archival Preservation & Loss of Global Knowledge"
            metaphor = "Colonnaded classical papyrus hall with modular rolling scroll shelving."
            motifs = [
                "Tiered papyrus parchment scrolls with deckle scissor edges",
                "Cast shadow architectural archways with ambient sunlight beams",
                "Ancient astrolabe brass paper cutout rings and celestial star maps"
            ]
        elif "oksigen" in topic.lower():
            concept = "Atmospheric Partial Pressure & Prehistoric Gigantism"
            metaphor = "Barometric pressure chamber with calibrated twin atmospheric balance scales."
            motifs = [
                "Giant Carboniferous dragonfly paper model with translucent layered wings",
                "Pressurized glass jar bellow pumps with rising gas particle cutouts",
                "Atmospheric oxygen percentage dial scale (21% vs 42%)"
            ]
        elif "sadap" in topic.lower() or "teknologi" in niche.lower():
            concept = "Electromagnetic Packet Interception & Mobile Privacy Architecture"
            metaphor = "Deconstructed smartphone glass schematic with cellular antenna relay tower."
            motifs = [
                "Concentric paper radio wave transmission rings with signal degradation dashes",
                "Encrypted binary data paper tape scrolling through paper logic gates",
                "Glowing padlock security indicator flipping from locked amber to alert red"
            ]
        else:
            concept = f"Physical Mechanical Demonstration of {topic}"
            metaphor = "Classic educational workbench with modular test apparatus and calibrated dials."
            motifs = [
                "Die-cut measurement indicators with high-contrast tick marks",
                "Tactile papercraft gear assemblies and mechanical levers",
                "Four-point paper sparkle bursts celebrating scientific realization"
            ]

        continuity_rules = [
            "100% adherence to digital cut-paper collage aesthetic; zero 3D CGI or raw pixel textures.",
            "Never display raw numbers or claims as plain text; always embody measurements through animated apparatus.",
            "Cat Scientist mascot must maintain #EA580C warm orange fur, wire spectacles, and white lab coat.",
            "Maintain consistent floor_y = 1380 anchor across all laboratory and environmental staging.",
            "Preserve vertical safe zones: banner top 420px, captions bottom 500px, stage central 1160px."
        ]

        environments_used = [
            {"id": default_env, "name": default_env.replace("-", " ").title(), "mood": "Primary narrative set"},
        ]

        return VisualBible(
            episode_slug=episode_slug,
            topic=topic,
            niche=niche,
            main_visual_concept=concept,
            metaphor_world=metaphor,
            color_palette=asdict(palette),
            lighting_direction=VisualIdentitySystem.LIGHTING_SPECIFICATION,
            character_appearance={
                "name": "CatScientist",
                "fur_color": "#EA580C",
                "wardrobe": "Crisp white paper lab coat with folded lapels (#F8FAFC)",
                "accessories": "Circular wire-rim spectacles (#FDFBF7)",
                "expression_rules": "Always actively looking at or interacting with central apparatus; never idle."
            },
            environments_used=environments_used,
            camera_language={
                "aspect_ratio": "9:16 (1080x1920)",
                "floor_y": 1380,
                "banner_safe_zone": [0, 420],
                "caption_safe_zone": [1420, 1920],
                "stage_zone": [420, 1580]
            },
            illustration_style=VisualIdentitySystem.PRIMARY_ART_STYLE,
            recurring_visual_motifs=motifs,
            visual_continuity_rules=continuity_rules,
            created_at=now
        )

    @classmethod
    def save_bible(cls, bible: VisualBible, episode_dir: Path) -> Tuple[Path, Path]:
        """Saves JSON and Markdown visual bible files."""
        vis_dir = episode_dir / "visuals"
        vis_dir.mkdir(parents=True, exist_ok=True)

        json_path = vis_dir / "visual_bible.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(bible.to_dict(), f, indent=2, ensure_ascii=False)

        md_path = vis_dir / "visual_bible.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(bible.to_markdown())

        return json_path, md_path
