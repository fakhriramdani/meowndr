"""
Story-Driven Visual Analyzer for @meowndr Papercraft Explainer.
Performs 10-step narrative visual analysis for every scene, translating script lines
into art-directed physical papercraft models, cinematic camera choices, and visual metaphors.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from .cinematography import CinematographyRules, CameraShot, CAMERA_SHOT_LIBRARY
from .visual_variety_engine import VisualVarietyEngine, SceneVisualFingerprint


@dataclass
class SceneVisualBrief:
    scene_id: str
    script_text: str
    main_concept: str
    intended_emotion: str
    visual_subject: str
    visual_metaphor: str
    environment_id: str
    camera_shot: CameraShot
    composition_notes: str
    lighting_notes: str
    presenter_action: str
    presenter_state: str
    depth_planes: Dict[str, str] = field(default_factory=dict)


class StoryVisualAnalyzer:
    """Deconstructs narration into rich physical metaphors and cinematic scene briefs."""

    def __init__(self, variety_engine: Optional[VisualVarietyEngine] = None):
        self.variety_engine = variety_engine or VisualVarietyEngine()

    def analyze_scene(
        self,
        scene_id: str,
        script_text: str,
        niche: str,
        default_env: str,
        beat_index: int,
        total_beats: int
    ) -> SceneVisualBrief:
        """Executes 10-step story-driven visual breakdown on a single narration beat."""
        text_lower = script_text.lower()

        # Step 1 & 2: Main concept extraction
        concept = self._extract_concept(script_text)

        # Step 3: Audience emotion determination
        emotion = self._determine_emotion(text_lower, beat_index, total_beats)

        # Step 4 & 5: Visual subject & physical metaphor selection
        subject, metaphor = self._select_metaphor_and_subject(text_lower, concept, niche)

        # Step 6: Environment selection
        env_id = self._select_environment(text_lower, default_env, beat_index)

        # Step 7: Camera shot selection via VisualVarietyEngine
        camera_shot = self.variety_engine.recommend_next_shot(
            scene_purpose=concept,
            beat_index=beat_index,
            total_beats=total_beats
        )

        # Step 8: Composition & safe-zone framing
        presenter_pos = "left" if beat_index % 2 == 0 else "right"
        if camera_shot.code in ("EWS", "BEV", "SYM"):
            presenter_pos = "center"

        composition = (
            f"9:16 vertical frame (1080x1920). Camera shot {camera_shot.name} ({camera_shot.code}). "
            f"Focal subject '{subject}' positioned in Stage Zone (y: 600-1100). "
            f"Presenter Cat Scientist anchored at {presenter_pos} (floor y: 1380). "
            f"Header zone (y < 420) and caption zone (y > 1420) left clean."
        )

        # Step 9: Lighting definition
        lighting = (
            f"Top-left directional paper key light casting soft drop shadows (0px 8px 16px rgba(15,23,42,0.22)). "
            f"Warm highlight rims on upper-left paper cut edges. Ambient mood matching {env_id}."
        )

        # Step 10: Presenter interaction state
        presenter_state, presenter_action = self._determine_presenter_action(emotion, beat_index, total_beats)

        # Record scene in variety history
        fingerprint = SceneVisualFingerprint(
            scene_id=scene_id,
            shot_type=camera_shot.code,
            camera_angle=camera_shot.name,
            environment_id=env_id,
            presenter_state=presenter_state,
            presenter_position=presenter_pos,
            dominant_accent_color="#0284C7",
            focal_subject_type="apparatus" if "gauge" in metaphor or "model" in metaphor else "macro_molecule"
        )
        self.variety_engine.record_scene(fingerprint)

        depth_planes = {
            "background": f"{env_id} room geometry and wall textures at z=0",
            "midground": f"Animated {subject} physical apparatus and Cat Scientist presenter at z=0.5",
            "foreground": f"Ambient paper framing elements at z=1.0 with soft depth-of-field"
        }

        return SceneVisualBrief(
            scene_id=scene_id,
            script_text=script_text,
            main_concept=concept,
            intended_emotion=emotion,
            visual_subject=subject,
            visual_metaphor=metaphor,
            environment_id=env_id,
            camera_shot=camera_shot,
            composition_notes=composition,
            lighting_notes=lighting,
            presenter_action=presenter_action,
            presenter_state=presenter_state,
            depth_planes=depth_planes
        )

    def _extract_concept(self, text: str) -> str:
        words = [w for w in re.findall(r"[a-zA-Z0-9]+", text) if len(w) >= 4]
        stopwords = {"pernah", "tidak", "adalah", "karena", "bahwa", "dengan", "dalam", "untuk", "kamu"}
        filtered = [w for w in words if w.lower() not in stopwords]
        if filtered:
            return " ".join(filtered[:3]).title()
        return "Mekanisme Ilmiah"

    def _determine_emotion(self, text: str, beat_index: int, total_beats: int) -> str:
        if beat_index == 0:
            return "curiosity and hook intrigue"
        if beat_index == total_beats - 1:
            return "satisfying closure and warm community connection"
        if any(w in text for w in ["sakit", "bahaya", "meletup", "panik", "aneh", "rusak"]):
            return "dramatic tension and anomaly surprise"
        if any(w in text for w in ["hebatnya", "luar biasa", "mengalahkan", "rekor", "mencium"]):
            return "scientific awe and revelation"
        return "focused educational insight"

    def _select_metaphor_and_subject(self, text: str, concept: str, niche: str) -> Tuple[str, str]:
        """Maps abstract concepts into physical papercraft models."""
        if "hujan" in text or "tanah" in text or "geosmin" in text or "petrichor" in text:
            return (
                "Porous soil cross-section with micro-cavitation air bubbles and aerosol spray plumes",
                "High-speed physical droplet impact stage with mechanical aerosol spring coils"
            )
        elif "es" in text or "dingin" in text or "membeku" in text or "freeze" in text:
            return (
                "Thermal contraction beaker apparatus with floating faceted ice crystals and rising mercury thermometer",
                "Physical density comparison scale contrasting liquid water molecule lattice with expanded crystal lattice"
            )
        elif "saraf" in text or "otak" in text or "dahi" in text or "palatum" in text:
            return (
                "Stylized papercraft cranial anatomy diorama highlighting glowing trigeminal nerve pathways",
                "Cutout vascular blood vessel dilation model with expanding ruby paper accordion rings"
            )
        elif "oksigen" in text or "serangga" in text or "raksasa" in text:
            return (
                "Atmospheric balance barometer with oversized prehistoric dragonfly paper specimen",
                "Mechanical oxygen molecule gas chamber with pressurized paper bellow pumps"
            )
        elif "sadap" in text or "sinyal" in text or "data" in text or "telepon" in text:
            return (
                "Transparent cross-section mobile device showing intercepting radio wave paper arcs",
                "Cybernetic telecommunications tower diorama with cascading paper packet streams"
            )
        elif "sejarah" in niche or "aleksandria" in text or "kuno" in text:
            return (
                "Layered archival scroll preservation apparatus with illuminated papyrus codex",
                "Architectural library facade with modular parchment scroll shelving dioramas"
            )
        else:
            return (
                f"Bespoke {concept} scientific demonstration model with animated paper gears and indicators",
                f"Physical analog test apparatus with calibrated indicator dials and sliding paper rulers"
            )

    def _select_environment(self, text: str, default_env: str, beat_index: int) -> str:
        if beat_index == 0 and ("hujan" in text or "luar" in text or "kota" in text):
            return "rainy-city-street"
        if "laut" in text or "pantai" in text:
            return "tropical-beach"
        if "gunung" in text or "alam" in text:
            return "mountain-landscape"
        if "sejarah" in text or "buku" in text or "aleksandria" in text:
            return "public-library"
        if "dapur" in text or "makan" in text or "minum" in text:
            return "home-kitchen"
        return default_env or "science-laboratory"

    def _determine_presenter_action(self, emotion: str, beat_index: int, total_beats: int) -> Tuple[str, str]:
        if beat_index == 0:
            return "curious", "Head tilted with paw under chin, peering inquisitively through wire spectacles."
        if beat_index == total_beats - 1:
            return "celebrating", "Both paws raised with eureka smile, celebrating the solved scientific riddle."
        if "tension" in emotion or "surprise" in emotion:
            return "surprised", "Recoil stance with wide spherical eyes and startled ear angle."
        if "awe" in emotion:
            return "pointing", "Arm extended with focused paw pointing directly at the remarkable reading."
        return "explaining", "Upright confident posture with open welcoming gesture introducing the mechanism."
