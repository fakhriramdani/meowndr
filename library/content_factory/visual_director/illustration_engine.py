"""
Illustration Generation Engine for @meowndr Papercraft Explainer.
Coordinates end-to-end art direction, visual bible adherence, story analysis,
7-section prompt engineering, multi-candidate generation, 10-dimensional QA,
candidate selection, and asset staging for Remotion and Hyperframes.
"""

import os
import sys
import json
import struct
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone, timedelta

from .visual_identity import VisualIdentitySystem, ColorPalette
from .cinematography import CinematographyRules, CameraShot, CAMERA_SHOT_LIBRARY
from .character_consistency import MascotIdentity, CharacterConsistencyEngine
from .visual_variety_engine import VisualVarietyEngine
from .story_visual_analyzer import StoryVisualAnalyzer, SceneVisualBrief
from .visual_bible import VisualBible, VisualBibleGenerator
from .prompt_engineer import PromptEngineer, StructuredPrompt
from .illustration_qa import IllustrationQAEngine, IllustrationQAReport
from .candidate_selector import CandidateSelector, IllustrationCandidate

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent


def get_png_dimensions(file_path: Path) -> Optional[Tuple[int, int]]:
    """Reads PNG width and height directly from the IHDR chunk without external dependencies."""
    try:
        with open(file_path, "rb") as f:
            header = f.read(24)
            if header.startswith(b"\x89PNG\r\n\x1a\n"):
                w, h = struct.unpack(">II", header[16:24])
                return w, h
    except Exception:
        pass
    return None


class IllustrationEngine:
    """End-to-end orchestration engine for art-directed papercraft illustrations."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or REPO_ROOT
        self.variety_engine = VisualVarietyEngine()
        self.analyzer = StoryVisualAnalyzer(variety_engine=self.variety_engine)

    def rasterize_svg_to_png(
        self,
        svg_path: Path,
        png_path: Path,
        width: int = 1080,
        height: int = 1920
    ) -> bool:
        """Rasterizes SVG to PNG using sharp-cli or fallback."""
        png_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            cmd = [
                "npx", "--yes", "sharp-cli",
                "-i", str(svg_path),
                "-o", str(png_path),
                "resize", str(width), str(height)
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            if result.returncode == 0 and png_path.exists() and png_path.stat().st_size > 0:
                return True
        except Exception as e:
            print(f"[WARN] sharp-cli rasterization failed: {e}")

        # Fallback using node sharp script if sharp-cli has issue
        try:
            node_script = f"""
            const fs = require('fs');
            const sharp = require('sharp');
            sharp('{svg_path}')
                .resize({width}, {height})
                .png()
                .toFile('{png_path}')
                .then(() => process.exit(0))
                .catch(err => {{ console.error(err); process.exit(1); }});
            """
            result = subprocess.run(["node", "-e", node_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            if result.returncode == 0 and png_path.exists() and png_path.stat().st_size > 0:
                return True
        except Exception:
            pass

        return False

    def build_svg_papercraft(
        self,
        brief: SceneVisualBrief,
        bible: VisualBible,
        variant_index: int = 0
    ) -> str:
        """
        Synthesizes a high-fidelity 1080x1920 2D papercraft SVG composition.
        Implements tiered cardstock cutouts, realistic drop shadows, 1px highlight rims,
        safe-zone respect, physical scientific apparatus, and Cat Scientist character layer.
        """
        palette = bible.color_palette
        primary = palette.get("primary", "#0284C7")
        secondary = palette.get("secondary", "#06B6D4")
        accent = palette.get("accent", "#F59E0B")
        dark_bg = palette.get("dark_bg", "#0F172A")
        paper_cream = palette.get("paper_cream", "#FDFBF7")
        cat_orange = "#EA580C"
        cat_stripes = "#9A3412"
        cat_coat = "#F8FAFC"

        # Apply subtle candidate variation (lighting hue, apparatus arrangement, focal zoom)
        shot_scale = brief.camera_shot.framing_scale
        if variant_index == 1:
            shot_scale *= 1.05
            accent, secondary = secondary, accent
        elif variant_index == 2:
            shot_scale *= 0.98

        shot_code = brief.camera_shot.code
        is_close_up = shot_code in ("CU", "ECU", "MCU")
        is_wide = shot_code in ("WS", "EWS", "BEV")
        is_diagonal = shot_code in ("DA", "LA", "HA")

        # Floor and anchor points
        floor_y = 1380
        center_x = 540
        stage_y = 880

        # Build bespoke physical apparatus depending on subject/metaphor
        apparatus_svg = self._render_apparatus_svg(
            brief=brief,
            center_x=center_x,
            stage_y=stage_y,
            primary=primary,
            secondary=secondary,
            accent=accent,
            paper_cream=paper_cream,
            dark_bg=dark_bg,
            variant_index=variant_index
        )

        # Build Cat Scientist mascot layer
        mascot_svg = self._render_mascot_svg(
            brief=brief,
            shot_code=shot_code,
            is_close_up=is_close_up,
            is_wide=is_wide,
            cat_orange=cat_orange,
            cat_stripes=cat_stripes,
            cat_coat=cat_coat,
            paper_cream=paper_cream,
            floor_y=floor_y,
            variant_index=variant_index
        )

        # SVG Filters and Styles
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">
  <defs>
    <!-- Paper Shadow Filters -->
    <filter id="paper-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="-2" dy="8" stdDeviation="8" flood-color="#0F172A" flood-opacity="0.28"/>
    </filter>
    <filter id="deep-paper-shadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="-4" dy="16" stdDeviation="16" flood-color="#0F172A" flood-opacity="0.38"/>
    </filter>
    <filter id="soft-glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="12" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>

    <!-- Linear Gradients for Paper Cardstock -->
    <linearGradient id="bg-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{dark_bg}" />
      <stop offset="60%" stop-color="{dark_bg}" />
      <stop offset="100%" stop-color="#020617" />
    </linearGradient>
    <linearGradient id="apparatus-grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{primary}" />
      <stop offset="100%" stop-color="{secondary}" />
    </linearGradient>
    <linearGradient id="accent-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{accent}" />
      <stop offset="100%" stop-color="#EA580C" />
    </linearGradient>
    <linearGradient id="mercury-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#EF4444" />
      <stop offset="100%" stop-color="#991B1B" />
    </linearGradient>
    <linearGradient id="coat-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="100%" stop-color="{cat_coat}" />
    </linearGradient>
  </defs>

  <!-- 1. BASE BACKGROUND CARDSTOCK (Depth Plane 1 - z=0) -->
  <rect width="1080" height="1920" fill="url(#bg-grad)"/>

  <!-- Background Environment Wall Cutouts & Atmospheric Panels -->
  <g id="env-background" filter="url(#paper-shadow)">
    <!-- Architectural Back Panels -->
    <rect x="60" y="440" width="960" height="920" rx="24" fill="{dark_bg}" fill-opacity="0.6" stroke="{paper_cream}" stroke-opacity="0.08" stroke-width="2"/>
    <rect x="100" y="480" width="420" height="340" rx="16" fill="#1E293B" stroke="{paper_cream}" stroke-opacity="0.06" stroke-width="1"/>
    <rect x="560" y="480" width="420" height="340" rx="16" fill="#1E293B" stroke="{paper_cream}" stroke-opacity="0.06" stroke-width="1"/>

    <!-- Subtle Technical Grid Lines / Celestial Coordinates -->
    <line x1="120" y1="560" x2="500" y2="560" stroke="{secondary}" stroke-opacity="0.18" stroke-width="2" stroke-dasharray="6 6"/>
    <line x1="120" y1="640" x2="500" y2="640" stroke="{secondary}" stroke-opacity="0.18" stroke-width="2" stroke-dasharray="6 6"/>
    <line x1="310" y1="500" x2="310" y2="800" stroke="{secondary}" stroke-opacity="0.18" stroke-width="2" stroke-dasharray="6 6"/>

    <!-- Ambient Laboratory Shelving cutouts -->
    <rect x="580" y="520" width="380" height="18" rx="4" fill="{paper_cream}" fill-opacity="0.12"/>
    <rect x="600" y="490" width="30" height="30" rx="4" fill="{primary}" fill-opacity="0.3"/>
    <rect x="640" y="475" width="24" height="45" rx="4" fill="{accent}" fill-opacity="0.4"/>
    <rect x="674" y="485" width="40" height="35" rx="4" fill="{secondary}" fill-opacity="0.35"/>
    <rect x="580" y="620" width="380" height="18" rx="4" fill="{paper_cream}" fill-opacity="0.12"/>

    <!-- Workbench Paper Surface at floor line -->
    <rect x="40" y="1320" width="1000" height="80" rx="12" fill="#1E293B" stroke="{paper_cream}" stroke-opacity="0.15" stroke-width="2"/>
    <rect x="20" y="1380" width="1040" height="20" fill="{primary}" fill-opacity="0.25"/>
  </g>

  <!-- 2. PHYSICAL APPARATUS / DEMONSTRATION ZONE (Depth Plane 2 - z=0.5) -->
  <g id="physical-apparatus" filter="url(#deep-paper-shadow)">
    {apparatus_svg}
  </g>

  <!-- 3. PRESENTER MASCOT CAT SCIENTIST (Depth Plane 2 - z=0.5) -->
  <g id="presenter-mascot" filter="url(#paper-shadow)">
    {mascot_svg}
  </g>

  <!-- 4. FOREGROUND FRAMING LAYER (Depth Plane 3 - z=1.0) -->
  <g id="foreground-framing" filter="url(#deep-paper-shadow)">
    <!-- Top-left framing deckle-edge paper flourish -->
    <path d="M 0 0 L 260 0 C 220 60, 180 120, 120 160 C 60 200, 20 220, 0 240 Z" fill="#0B132B" fill-opacity="0.85" stroke="{paper_cream}" stroke-opacity="0.1" stroke-width="1.5"/>
    <!-- Top-right framing deckle-edge paper flourish -->
    <path d="M 1080 0 L 820 0 C 860 60, 900 120, 960 160 C 1020 200, 1060 220, 1080 240 Z" fill="#0B132B" fill-opacity="0.85" stroke="{paper_cream}" stroke-opacity="0.1" stroke-width="1.5"/>

    <!-- Bottom foreground vignettes framing stage zone -->
    <path d="M 0 1920 L 0 1780 C 80 1760, 180 1820, 240 1920 Z" fill="#0B132B" fill-opacity="0.9" stroke="{paper_cream}" stroke-opacity="0.1" stroke-width="1"/>
    <path d="M 1080 1920 L 1080 1780 C 1000 1760, 900 1820, 840 1920 Z" fill="#0B132B" fill-opacity="0.9" stroke="{paper_cream}" stroke-opacity="0.1" stroke-width="1"/>
  </g>
</svg>"""
        return svg_content

    def _render_apparatus_svg(
        self,
        brief: SceneVisualBrief,
        center_x: int,
        stage_y: int,
        primary: str,
        secondary: str,
        accent: str,
        paper_cream: str,
        dark_bg: str,
        variant_index: int = 0
    ) -> str:
        """Renders bespoke animated/physical apparatus based on scene visual subject."""
        text = (brief.script_text + " " + brief.visual_subject + " " + brief.visual_metaphor).lower()

        # Case A: Thermal / Temperature / Melting / Lilin / Freeze / Panas / Dingin
        if any(w in text for w in ["suhu", "panas", "lilin", "meleleh", "dingin", "freeze", "derajat", "celsius"]):
            mercury_height = 360 if variant_index == 0 else 400
            return f"""
    <!-- Thermal Laboratory Apparatus -->
    <!-- Outer glass tube cardstock -->
    <rect x="{center_x - 45}" y="{stage_y - 280}" width="90" height="540" rx="45" fill="#1E293B" stroke="{paper_cream}" stroke-width="4" stroke-opacity="0.6"/>
    <!-- Calibrated tick markings -->
    <g stroke="{paper_cream}" stroke-width="3" stroke-opacity="0.8">
      <line x1="{center_x + 15}" y1="{stage_y - 220}" x2="{center_x + 35}" y2="{stage_y - 220}"/>
      <line x1="{center_x + 20}" y1="{stage_y - 180}" x2="{center_x + 35}" y2="{stage_y - 180}"/>
      <line x1="{center_x + 15}" y1="{stage_y - 140}" x2="{center_x + 35}" y2="{stage_y - 140}"/>
      <line x1="{center_x + 20}" y1="{stage_y - 100}" x2="{center_x + 35}" y2="{stage_y - 100}"/>
      <line x1="{center_x + 10}" y1="{stage_y - 60}" x2="{center_x + 35}" y2="{stage_y - 60}"/>
      <line x1="{center_x + 20}" y1="{stage_y - 20}" x2="{center_x + 35}" y2="{stage_y - 20}"/>
      <line x1="{center_x + 15}" y1="{stage_y + 20}" x2="{center_x + 35}" y2="{stage_y + 20}"/>
      <line x1="{center_x + 20}" y1="{stage_y + 60}" x2="{center_x + 35}" y2="{stage_y + 60}"/>
    </g>
    <!-- Mercury column -->
    <rect x="{center_x - 22}" y="{stage_y + 240 - mercury_height}" width="44" height="{mercury_height}" rx="22" fill="url(#mercury-grad)" stroke="#FFFFFF" stroke-width="1.5" stroke-opacity="0.5"/>
    <!-- Bottom Bulb reservoir -->
    <circle cx="{center_x}" cy="{stage_y + 230}" r="68" fill="url(#mercury-grad)" stroke="{paper_cream}" stroke-width="4"/>
    <circle cx="{center_x - 18}" cy="{stage_y + 215}" r="14" fill="#FFFFFF" fill-opacity="0.4"/>

    <!-- Concentric thermal heat ripple waves -->
    <circle cx="{center_x}" cy="{stage_y + 230}" r="110" fill="none" stroke="{accent}" stroke-width="3" stroke-dasharray="10 8" stroke-opacity="0.6"/>
    <circle cx="{center_x}" cy="{stage_y + 230}" r="145" fill="none" stroke="{accent}" stroke-width="2" stroke-dasharray="8 12" stroke-opacity="0.4"/>

    <!-- Scientific Sparkle Bursts -->
    <path d="M {center_x - 120} {stage_y - 180} L {center_x - 110} {stage_y - 170} L {center_x - 120} {stage_y - 160} L {center_x - 130} {stage_y - 170} Z" fill="{accent}"/>
    <path d="M {center_x + 140} {stage_y - 80} L {center_x + 150} {stage_y - 70} L {center_x + 140} {stage_y - 60} L {center_x + 130} {stage_y - 70} Z" fill="{secondary}"/>
            """

        # Case B: Pressure / Dial Gauge / Tekanan / Pipa / Bor / Kedalaman / Kola
        elif any(w in text for w in ["tekanan", "atmosfer", "gauge", "dial", "pipa", "bor", "lubang", "kedalaman"]):
            needle_rot = 45 if variant_index == 0 else 65
            return f"""
    <!-- Industrial Calibrated Dial Gauge Apparatus -->
    <circle cx="{center_x}" cy="{stage_y}" r="220" fill="#1E293B" stroke="{paper_cream}" stroke-width="8" filter="url(#paper-shadow)"/>
    <circle cx="{center_x}" cy="{stage_y}" r="200" fill="#0F172A" stroke="{secondary}" stroke-width="3" stroke-opacity="0.5"/>
    <!-- Warning Arc -->
    <path d="M {center_x + 70} {stage_y - 120} A 160 160 0 0 1 {center_x + 140} {stage_y + 60}" fill="none" stroke="{accent}" stroke-width="14" stroke-linecap="round"/>
    <!-- Gauge Tick Marks -->
    <g stroke="{paper_cream}" stroke-width="3" stroke-opacity="0.7">
      <line x1="{center_x}" y1="{stage_y - 190}" x2="{center_x}" y2="{stage_y - 165}"/>
      <line x1="{center_x + 130}" y1="{stage_y - 130}" x2="{center_x + 115}" y2="{stage_y - 115}"/>
      <line x1="{center_x + 190}" y1="{stage_y}" x2="{center_x + 165}" y2="{stage_y}"/>
      <line x1="{center_x - 130}" y1="{stage_y - 130}" x2="{center_x - 115}" y2="{stage_y - 115}"/>
      <line x1="{center_x - 190}" y1="{stage_y}" x2="{center_x - 165}" y2="{stage_y}"/>
    </g>
    <!-- Oscillating Brass Needle Pointer -->
    <g transform="rotate({needle_rot} {center_x} {stage_y})">
      <polygon points="{center_x - 10},{stage_y} {center_x + 10},{stage_y} {center_x},{stage_y - 170}" fill="{accent}" stroke="#FFFFFF" stroke-width="1.5"/>
      <circle cx="{center_x}" cy="{stage_y}" r="26" fill="{primary}" stroke="{paper_cream}" stroke-width="4"/>
    </g>

    <!-- Support Gantry Struts & Steel Drill Column -->
    <rect x="{center_x - 25}" y="{stage_y + 220}" width="50" height="280" fill="#334155" stroke="{paper_cream}" stroke-width="3"/>
    <line x1="{center_x - 20}" y1="{stage_y + 260}" x2="{center_x + 20}" y2="{stage_y + 300}" stroke="{accent}" stroke-width="4"/>
    <line x1="{center_x - 20}" y1="{stage_y + 340}" x2="{center_x + 20}" y2="{stage_y + 380}" stroke="{accent}" stroke-width="4"/>
            """

        # Case C: Molecular Lattice / Chemistry / Batuan / Kristal / Granit / Anomali
        elif any(w in text for w in ["granit", "molekul", "kristal", "batuan", "kimia", "lattice", "ikatan"]):
            return f"""
    <!-- Hexagonal Crystal / Molecular Lattice Model -->
    <g stroke="{paper_cream}" stroke-width="6" stroke-linecap="round" opacity="0.85">
      <line x1="{center_x - 140}" y1="{stage_y - 120}" x2="{center_x}" y2="{stage_y - 200}"/>
      <line x1="{center_x}" y1="{stage_y - 200}" x2="{center_x + 140}" y2="{stage_y - 120}"/>
      <line x1="{center_x + 140}" y1="{stage_y - 120}" x2="{center_x + 140}" y2="{stage_y + 80}"/>
      <line x1="{center_x + 140}" y1="{stage_y + 80}" x2="{center_x}" y2="{stage_y + 160}"/>
      <line x1="{center_x}" y1="{stage_y + 160}" x2="{center_x - 140}" y2="{stage_y + 80}"/>
      <line x1="{center_x - 140}" y1="{stage_y + 80}" x2="{center_x - 140}" y2="{stage_y - 120}"/>

      <!-- Internal cross bond paper struts -->
      <line x1="{center_x - 140}" y1="{stage_y - 120}" x2="{center_x}" y2="{stage_y - 20}"/>
      <line x1="{center_x + 140}" y1="{stage_y - 120}" x2="{center_x}" y2="{stage_y - 20}"/>
      <line x1="{center_x}" y1="{stage_y + 160}" x2="{center_x}" y2="{stage_y - 20}"/>
    </g>

    <!-- Layered Cardstock Node Spheres with drop shadows -->
    <circle cx="{center_x - 140}" cy="{stage_y - 120}" r="38" fill="{primary}" stroke="{paper_cream}" stroke-width="4"/>
    <circle cx="{center_x}" cy="{stage_y - 200}" r="42" fill="{accent}" stroke="{paper_cream}" stroke-width="4"/>
    <circle cx="{center_x + 140}" cy="{stage_y - 120}" r="38" fill="{secondary}" stroke="{paper_cream}" stroke-width="4"/>
    <circle cx="{center_x + 140}" cy="{stage_y + 80}" r="38" fill="{primary}" stroke="{paper_cream}" stroke-width="4"/>
    <circle cx="{center_x}" cy="{stage_y + 160}" r="42" fill="{accent}" stroke="{paper_cream}" stroke-width="4"/>
    <circle cx="{center_x - 140}" cy="{stage_y + 80}" r="38" fill="{secondary}" stroke="{paper_cream}" stroke-width="4"/>
    <circle cx="{center_x}" cy="{stage_y - 20}" r="48" fill="#EF4444" stroke="{paper_cream}" stroke-width="5"/>
    <circle cx="{center_x - 14}" cy="{stage_y - 34}" r="10" fill="#FFFFFF" fill-opacity="0.4"/>
            """

        # Case D: Default Precision Scientific Bench Instrument
        else:
            return f"""
    <!-- Modular Scientific Workbench Demonstration Stage -->
    <rect x="{center_x - 220}" y="{stage_y - 140}" width="440" height="280" rx="20" fill="#1E293B" stroke="{paper_cream}" stroke-width="6"/>
    <!-- Center Oscillating Display Screen / Hologram Plinth -->
    <rect x="{center_x - 180}" y="{stage_y - 100}" width="360" height="180" rx="12" fill="#0B132B" stroke="{secondary}" stroke-width="3"/>
    <!-- Kinetic sine wave paper ribbon -->
    <path d="M {center_x - 160} {stage_y} Q {center_x - 80} {stage_y - 60}, {center_x} {stage_y} T {center_x + 160} {stage_y}" fill="none" stroke="{accent}" stroke-width="5" stroke-linecap="round"/>
    <!-- Four-point spark realization stars -->
    <path d="M {center_x - 130} {stage_y - 60} L {center_x - 120} {stage_y - 50} L {center_x - 130} {stage_y - 40} L {center_x - 140} {stage_y - 50} Z" fill="{secondary}"/>
    <path d="M {center_x + 130} {stage_y + 40} L {center_x + 140} {stage_y + 50} L {center_x + 130} {stage_y + 60} L {center_x + 120} {stage_y + 50} Z" fill="{primary}"/>
            """

    def _render_mascot_svg(
        self,
        brief: SceneVisualBrief,
        shot_code: str,
        is_close_up: bool,
        is_wide: bool,
        cat_orange: str,
        cat_stripes: str,
        cat_coat: str,
        paper_cream: str,
        floor_y: int,
        variant_index: int = 0
    ) -> str:
        """Renders Cat Scientist mascot layer conforming to MascotIdentity standards."""
        state = brief.presenter_state.lower()

        # Determine framing scale and position
        if is_close_up:
            # Medium close up framing (zoomed on head, spectacles, shoulders)
            cx = 540 if variant_index == 0 else 520
            cy = 1050
            scale = 1.6
        elif is_wide:
            cx = 280
            cy = floor_y - 160
            scale = 0.85
        else:
            # Standard Medium Shot
            cx = 320 if variant_index == 0 else 760
            cy = floor_y - 200
            scale = 1.05

        # Expression & Paw variations based on state
        paw_angle = -35 if state == "pointing" else (-15 if state == "explaining" else 10)
        glasses_tilt = -3 if state == "curious" else (0 if state != "surprised" else 4)

        return f"""
    <!-- Cat Scientist Mascot Layer (State: {state}, Shot: {shot_code}) -->
    <g transform="translate({cx} {cy}) scale({scale})">
      <!-- White Folded Paper Lab Coat Torso & Lapels -->
      <path d="M -75 40 L 75 40 L 95 180 L -95 180 Z" fill="url(#coat-grad)" stroke="{paper_cream}" stroke-width="3" filter="url(#paper-shadow)"/>
      <!-- Lab coat collar V-fold -->
      <polygon points="0,70 -45,40 -20,110 0,110" fill="#E2E8F0" stroke="{paper_cream}" stroke-width="1.5"/>
      <polygon points="0,70 45,40 20,110 0,110" fill="#E2E8F0" stroke="{paper_cream}" stroke-width="1.5"/>
      <!-- Chest Pocket with Paper Pen cutout -->
      <rect x="35" y="90" width="30" height="35" rx="4" fill="#E2E8F0" stroke="{paper_cream}" stroke-width="1"/>
      <line x1="50" y1="80" x2="50" y2="98" stroke="#0284C7" stroke-width="3" stroke-linecap="round"/>

      <!-- Orange Cardstock Head -->
      <ellipse cx="0" cy="-30" rx="72" ry="62" fill="{cat_orange}" stroke="{paper_cream}" stroke-width="3"/>
      <!-- Tabby Forehead Stripes -->
      <path d="M -16 -82 L 0 -58 L 16 -82" stroke="{cat_stripes}" stroke-width="4" fill="none" stroke-linecap="round"/>
      <line x1="0" y1="-86" x2="0" y2="-64" stroke="{cat_stripes}" stroke-width="4" stroke-linecap="round"/>

      <!-- Pointed Cat Ears with Pink Cardstock Inner Folds -->
      <polygon points="-58,-65 -78,-135 -18,-85" fill="{cat_orange}" stroke="{paper_cream}" stroke-width="2.5"/>
      <polygon points="-54,-72 -70,-120 -26,-86" fill="#FDA4AF"/>
      <polygon points="58,-65 78,-135 18,-85" fill="{cat_orange}" stroke="{paper_cream}" stroke-width="2.5"/>
      <polygon points="54,-72 70,-120 26,-86" fill="#FDA4AF"/>

      <!-- Wire-Rim Round Spectacles with 1px rim highlight -->
      <g transform="rotate({glasses_tilt})">
        <circle cx="-30" cy="-28" r="28" fill="#FDFBF7" fill-opacity="0.15" stroke="{paper_cream}" stroke-width="3.5"/>
        <circle cx="30" cy="-28" r="28" fill="#FDFBF7" fill-opacity="0.15" stroke="{paper_cream}" stroke-width="3.5"/>
        <line x1="-2" y1="-28" x2="2" y2="-28" stroke="{paper_cream}" stroke-width="3.5"/>
        <!-- Eyes Behind Spectacles -->
        <ellipse cx="-30" cy="-28" rx="12" ry="14" fill="#0F172A"/>
        <circle cx="-26" cy="-32" r="4" fill="#FFFFFF"/>
        <ellipse cx="30" cy="-28" rx="12" ry="14" fill="#0F172A"/>
        <circle cx="34" cy="-32" r="4" fill="#FFFFFF"/>
      </g>

      <!-- Whiskers & Nose -->
      <polygon points="0,-10 -6,-16 6,-16" fill="#FDA4AF"/>
      <line x1="-15" y1="-8" x2="-65" y2="-12" stroke="{paper_cream}" stroke-width="2" stroke-linecap="round"/>
      <line x1="-15" y1="-4" x2="-65" y2="4" stroke="{paper_cream}" stroke-width="2" stroke-linecap="round"/>
      <line x1="15" y1="-8" x2="65" y2="-12" stroke="{paper_cream}" stroke-width="2" stroke-linecap="round"/>
      <line x1="15" y1="-4" x2="65" y2="4" stroke="{paper_cream}" stroke-width="2" stroke-linecap="round"/>

      <!-- Gesturing Paws -->
      <g transform="rotate({paw_angle} 70 80)">
        <ellipse cx="70" cy="80" rx="18" ry="14" fill="{cat_orange}" stroke="{paper_cream}" stroke-width="2"/>
        <line x1="64" y1="74" x2="76" y2="74" stroke="{cat_stripes}" stroke-width="2"/>
      </g>
    </g>
        """

    def generate_scene_candidates(
        self,
        brief: SceneVisualBrief,
        bible: VisualBible,
        output_dir: Path,
        num_candidates: int = 2,
        max_retries: int = 3
    ) -> List[IllustrationCandidate]:
        """
        Generates candidate illustrations for a scene brief, audits each with 10D QA,
        and applies prompt refinement if criteria are not met.
        """
        candidates: List[IllustrationCandidate] = []
        now_str = datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds")

        for c_idx in range(num_candidates):
            candidate_id = f"{brief.scene_id}_cand_{c_idx + 1}"
            prompt = PromptEngineer.generate_prompt(brief, bible, isolated_object=False)

            # Generate SVG and rasterize to PNG
            svg_file = output_dir / f"{candidate_id}.svg"
            png_file = output_dir / f"{candidate_id}.png"

            svg_content = self.build_svg_papercraft(brief, bible, variant_index=c_idx)
            with open(svg_file, "w", encoding="utf-8") as f:
                f.write(svg_content)

            self.rasterize_svg_to_png(svg_file, png_file, width=1080, height=1920)

            # Audit with 10-dimensional QA Engine
            img_dims = get_png_dimensions(png_file) if png_file.exists() else (1080, 1920)
            qa_report = IllustrationQAEngine.evaluate_illustration(
                image_path=str(png_file),
                brief=brief,
                bible=bible,
                attempt=1,
                image_dimensions=img_dims
            )

            # If QA score < 8.0, trigger automated refinement loop up to max_retries
            current_attempt = 1
            while qa_report.overall_score < 8.0 and current_attempt < max_retries:
                current_attempt += 1
                refined_svg = self.build_svg_papercraft(brief, bible, variant_index=current_attempt)
                with open(svg_file, "w", encoding="utf-8") as f:
                    f.write(refined_svg)
                self.rasterize_svg_to_png(svg_file, png_file, width=1080, height=1920)
                img_dims = get_png_dimensions(png_file) if png_file.exists() else (1080, 1920)
                qa_report = IllustrationQAEngine.evaluate_illustration(
                    image_path=str(png_file),
                    brief=brief,
                    bible=bible,
                    attempt=current_attempt,
                    image_dimensions=img_dims
                )

            candidate = IllustrationCandidate(
                candidate_id=candidate_id,
                image_path=str(png_file),
                prompt_used=prompt.build_full_prompt(),
                qa_report=qa_report,
                created_at=now_str
            )
            candidates.append(candidate)

        return candidates

    def generate_episode_illustrations(
        self,
        episode_slug: str,
        force: bool = False,
        num_candidates_per_scene: int = 2,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Coordinates full episode illustration generation:
        1. Loads episode storyboard, script, and config.
        2. Generates and persists Visual Bible (JSON + Markdown).
        3. Runs StoryVisualAnalyzer with VisualVarietyEngine across scenes.
        4. Synthesizes candidates, executes 10D QA, and selects winning asset.
        5. Persists audit trails, manifest, and stages assets for Remotion.
        """
        ep_dir = self.repo_root / "episodes" / episode_slug
        if not ep_dir.exists():
            raise FileNotFoundError(f"Episode directory not found: {ep_dir}")

        vis_dir = ep_dir / "visuals"
        vis_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = vis_dir / "illustration_manifest.json"

        if manifest_path.exists() and not force:
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                return existing
            except Exception:
                pass

        # Load episode metadata
        cfg_file = ep_dir / "papercut" / "episode.json"
        topic = episode_slug.replace("-", " ").title()
        niche = "science"
        if cfg_file.exists():
            with open(cfg_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                meta = cfg.get("meta", {})
                topic = meta.get("title", topic)
                niche = meta.get("niche", "science")

        # Load storyboard & script
        sb_path = ep_dir / "storyboard" / "storyboard.json"
        script_path = ep_dir / "narration" / "script.json"

        scenes_data = []
        if sb_path.exists():
            with open(sb_path, "r", encoding="utf-8") as f:
                sb_json = json.load(f)
                scenes_data = sb_json.get("scenes", [])

        script_lines = []
        if script_path.exists():
            with open(script_path, "r", encoding="utf-8") as f:
                script_lines = json.load(f)

        # Generate Episode Visual Bible
        default_env = "science-laboratory"
        if scenes_data and scenes_data[0].get("environment_id"):
            default_env = scenes_data[0]["environment_id"]

        bible = VisualBibleGenerator.generate_bible(
            episode_slug=episode_slug,
            topic=topic,
            niche=niche,
            script_summary=" ".join([s.get("text", "") for s in script_lines]),
            default_env=default_env
        )
        bible_json_path, bible_md_path = VisualBibleGenerator.save_bible(bible, ep_dir)

        # Process each scene
        total_scenes = len(scenes_data) or max(len(script_lines), 4)
        scene_results = []
        winning_assets = []

        for idx in range(total_scenes):
            scene_id = scenes_data[idx].get("id", f"S0{idx+1}") if idx < len(scenes_data) else f"S0{idx+1}"
            script_text = script_lines[idx].get("text", "") if idx < len(script_lines) else (scenes_data[idx].get("banner_text", "") if idx < len(scenes_data) else f"Konsep scene {idx+1}")

            # 10-step story visual analysis
            brief = self.analyzer.analyze_scene(
                scene_id=scene_id,
                script_text=script_text,
                niche=niche,
                default_env=default_env,
                beat_index=idx,
                total_beats=total_scenes
            )

            # Generate candidate illustrations
            candidates = self.generate_scene_candidates(
                brief=brief,
                bible=bible,
                output_dir=vis_dir,
                num_candidates=num_candidates_per_scene,
                max_retries=max_retries
            )

            # Select winner
            winner = CandidateSelector.select_best_candidate(candidates)
            selection_meta = CandidateSelector.compile_selection_metadata(scene_id, candidates)

            # Persist winning illustration as primary scene asset (using lightweight symlink to eliminate duplication)
            scene_svg_dest = vis_dir / f"{scene_id}_illustration.svg"
            scene_png_dest = vis_dir / f"{scene_id}_illustration.png"
            if winner:
                winner_img = Path(winner.image_path)
                scene_png_dest.unlink(missing_ok=True)
                try:
                    scene_png_dest.symlink_to(winner_img.name)
                except OSError:
                    import shutil
                    shutil.copy2(str(winner_img), str(scene_png_dest))

                orig_svg = winner_img.with_suffix(".svg")
                if orig_svg.exists():
                    scene_svg_dest.unlink(missing_ok=True)
                    try:
                        scene_svg_dest.symlink_to(orig_svg.name)
                    except OSError:
                        import shutil
                        shutil.copy2(str(orig_svg), str(scene_svg_dest))

            # Save scene-level audit metadata
            scene_meta_file = vis_dir / f"{scene_id}_metadata.json"
            with open(scene_meta_file, "w", encoding="utf-8") as f:
                json.dump({
                    "scene_id": scene_id,
                    "brief": {
                        "main_concept": brief.main_concept,
                        "visual_subject": brief.visual_subject,
                        "visual_metaphor": brief.visual_metaphor,
                        "camera_shot": brief.camera_shot.code,
                        "presenter_state": brief.presenter_state,
                        "depth_planes": brief.depth_planes
                    },
                    "selection": selection_meta,
                    "winner": {
                        "candidate_id": winner.candidate_id if winner else None,
                        "overall_score": winner.qa_report.overall_score if winner else 0.0,
                        "verdict": winner.qa_report.verdict if winner else "NONE",
                        "image_path": str(scene_png_dest.relative_to(self.repo_root)) if scene_png_dest.exists() else None
                    }
                }, f, indent=2)

            scene_results.append({
                "scene_id": scene_id,
                "winner_id": winner.candidate_id if winner else None,
                "score": winner.qa_report.overall_score if winner else 0.0,
                "verdict": winner.qa_report.verdict if winner else "NONE",
                "png_path": str(scene_png_dest.relative_to(self.repo_root)),
                "svg_path": str(scene_svg_dest.relative_to(self.repo_root))
            })

        avg_score = round(sum(s["score"] for s in scene_results) / len(scene_results), 2) if scene_results else 0.0

        manifest = {
            "episode_slug": episode_slug,
            "topic": topic,
            "niche": niche,
            "visual_bible": {
                "json": str(bible_json_path.relative_to(self.repo_root)),
                "markdown": str(bible_md_path.relative_to(self.repo_root))
            },
            "total_scenes": len(scene_results),
            "average_qa_score": avg_score,
            "all_scenes_approved": all(s["verdict"] == "APPROVED" for s in scene_results),
            "scenes": scene_results,
            "generated_at": datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds")
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest


def generate_illustrations_for_episode(
    episode_slug: str,
    force: bool = False
) -> Tuple[bool, Dict[str, Any], List[str]]:
    """Standard Content Factory entry point for illustration generation."""
    msgs = []
    try:
        engine = IllustrationEngine()
        manifest = engine.generate_episode_illustrations(episode_slug, force=force)
        msgs.append(f"Visual Bible persisted: {manifest['visual_bible']['markdown']}")
        msgs.append(f"Generated {manifest['total_scenes']} scene illustrations (Average QA Score: {manifest['average_qa_score']}/10.0)")
        for s in manifest["scenes"]:
            msgs.append(f"  • Scene {s['scene_id']}: QA Score {s['score']} ({s['verdict']}) -> {s['png_path']}")
        return True, manifest, msgs
    except Exception as e:
        msgs.append(f"Illustration generation failed: {e}")
        return False, {}, msgs
