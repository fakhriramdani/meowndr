"""
Visual Director & Professional Illustration System for @meowndr Papercraft Explainer.
Automates visual art direction, cinematography, visual bible governance,
story-driven visual analysis, structured prompt engineering, 10D QA,
candidate selection, and asset generation.
"""

from .visual_identity import VisualIdentitySystem, ColorPalette
from .cinematography import CinematographyRules, CameraShot, CAMERA_SHOT_LIBRARY
from .character_consistency import MascotIdentity, CharacterConsistencyEngine
from .visual_variety_engine import VisualVarietyEngine, SceneVisualFingerprint
from .story_visual_analyzer import StoryVisualAnalyzer, SceneVisualBrief
from .visual_bible import VisualBible, VisualBibleGenerator
from .prompt_engineer import PromptEngineer, StructuredPrompt
from .illustration_qa import IllustrationQAEngine, IllustrationQAReport, QADimensionScore
from .candidate_selector import CandidateSelector, IllustrationCandidate
from .illustration_engine import IllustrationEngine, generate_illustrations_for_episode

__all__ = [
    "VisualIdentitySystem",
    "ColorPalette",
    "CinematographyRules",
    "CameraShot",
    "CAMERA_SHOT_LIBRARY",
    "MascotIdentity",
    "CharacterConsistencyEngine",
    "VisualVarietyEngine",
    "SceneVisualFingerprint",
    "StoryVisualAnalyzer",
    "SceneVisualBrief",
    "VisualBible",
    "VisualBibleGenerator",
    "PromptEngineer",
    "StructuredPrompt",
    "IllustrationQAEngine",
    "IllustrationQAReport",
    "QADimensionScore",
    "CandidateSelector",
    "IllustrationCandidate",
    "IllustrationEngine",
    "generate_illustrations_for_episode",
]
