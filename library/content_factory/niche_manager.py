#!/usr/bin/env python3
"""
Multi-Niche Manager for Papercraft Content Factory.

Defines thematic profiles, color tokens, visual models, background environments,
and presenter configurations for the 5 supported niches:
1. Science (Chemistry, Physics, Molecular Biology)
2. History (Archaeology, Ancient Civilizations, Historical Mysteries)
3. Geography (World Wonders, Earth Curiosities, Planetary Geography)
4. Technology (Quantum Computing, Photonics, Robotics, AI)
5. Mystery (Evidence-Based Natural Oddities, Cryptic Phenomena)
"""

from typing import Dict, Any, List, Optional

NICHES: Dict[str, Dict[str, Any]] = {
    "science": {
        "id": "science",
        "name": "Sains & Eksplorasi Alam",
        "description": "Speculative What-If scenarios exploring fundamental physics, chemistry, and biology shifts and their downstream cascades.",
        "default_environment": "science-laboratory",
        "allowed_environments": ["science-laboratory", "botany-greenhouse", "physics-lab"],
        "default_floor_y": 1380,
        "color_tokens": {
            "primary": "#0284C7",       # Sky paper blue
            "secondary": "#16A34A",     # Emerald paper green
            "accent": "#E11D48",        # Rose discovery
            "paper_cream": "#FDFBF7",
            "paper_kraft": "#D5C5B0",
            "text_dark": "#1E293B"
        },
        "presenter": {
            "character": "CatScientist",
            "role_title": "Ilmuwan Kucing",
            "default_state": "curious",
            "glasses": True,
            "lab_coat": True
        },
        "reusable_models": [
            "HydrogenLatticeModel",
            "WaterAnomalyGauge",
            "PaperBeakerDemo",
            "ThermalContractionChart",
            "DensityComparisonScale",
            "WinterLakeEcologyDiorama",
            "ScienceSparkleStar"
        ],
        "default_banner_prefix": "",
        "tone": "curious, analytical, wonder-filled, fact-grounded",
        "default_bed": "marimba-F-108",
        "recommended_beds": ["marimba-F-108", "marimba-Am-120", "kalimba-spa-D-100"]
    },
    "history": {
        "id": "history",
        "name": "Sejarah & Peradaban Kuno",
        "description": "Alternative history What-If scenarios investigating pivotal divergence points, lost civilizations, and subsequent era cascades.",
        "default_environment": "botany-greenhouse",
        "allowed_environments": ["botany-greenhouse", "science-lab", "physics-lab"],
        "default_floor_y": 1380,
        "color_tokens": {
            "primary": "#B45309",       # Ancient gold / amber
            "secondary": "#78350F",     # Weathered papyrus brown
            "accent": "#991B1B",        # Ancient terracotta red
            "paper_cream": "#F9F5EB",
            "paper_kraft": "#C8B69B",
            "text_dark": "#1C1917"
        },
        "presenter": {
            "character": "CatScientist",
            "role_title": "Arkeolog Kucing",
            "default_state": "thinking",
            "glasses": True,
            "lab_coat": False
        },
        "reusable_models": [
            "PapercraftTimelineScale",
            "AncientScrollBanner",
            "MonumentReliefCutout",
            "ArchivalMapDiorama"
        ],
        "default_banner_prefix": "",
        "tone": "reverent, intriguing, narrative-rich, archival",
        "default_bed": "kalimba-story-G-66",
        "recommended_beds": ["kalimba-story-G-66", "night-rain-piano-F", "marimba-heist-Dm-112"]
    },
    "geography": {
        "id": "geography",
        "name": "Geografi & Keajaiban Bumi",
        "description": "What-If geological and planetary transformations exploring extreme planetary biomes and downstream evolutionary impacts.",
        "default_environment": "botany-greenhouse",
        "allowed_environments": ["botany-greenhouse", "science-lab", "physics-lab"],
        "default_floor_y": 1380,
        "color_tokens": {
            "primary": "#0D9488",       # Oceanic teal
            "secondary": "#15803D",     # Tropical foliage green
            "accent": "#EA580C",        # Volcanic terracotta
            "paper_cream": "#F8FAFC",
            "paper_kraft": "#CFBEAB",
            "text_dark": "#0F172A"
        },
        "presenter": {
            "character": "CatScientist",
            "role_title": "Penjelajah Geografi",
            "default_state": "pointing",
            "glasses": True,
            "lab_coat": True
        },
        "reusable_models": [
            "TopographicContourMap",
            "ContinentalDriftPlate",
            "ElevationDepthGauge",
            "ClimateCrossSection"
        ],
        "default_banner_prefix": "",
        "tone": "adventurous, breathtaking, earth-scale, precise",
        "default_bed": "marimba-F-108",
        "recommended_beds": ["marimba-F-108", "marimba-G-116", "night-rain-piano-F"]
    },
    "technology": {
        "id": "technology",
        "name": "Teknologi & Komputasi Masa Depan",
        "description": "Future technology and counterfactual computing What-If scenarios exploring technological leaps and their societal ripples.",
        "default_environment": "physics-lab",
        "allowed_environments": ["physics-lab", "optics-lab", "optics-lab-v2", "science-lab"],
        "default_floor_y": 1380,
        "color_tokens": {
            "primary": "#6366F1",       # Indigo quantum
            "secondary": "#06B6D4",     # Data cyan
            "accent": "#F59E0B",        # Energy gold
            "paper_cream": "#F8FAFC",
            "paper_kraft": "#CBD5E1",
            "text_dark": "#0B0F19"
        },
        "presenter": {
            "character": "CatScientist",
            "role_title": "Insinyur Masa Depan",
            "default_state": "explaining",
            "glasses": True,
            "lab_coat": True
        },
        "reusable_models": [
            "OpticsLaserSplitter",
            "QuantumQubitLattice",
            "SiliconWaferLayer",
            "AlgorithmFlowRibbon"
        ],
        "default_banner_prefix": "",
        "tone": "futuristic, precise, cutting-edge, illuminating",
        "default_bed": "marimba-G-116",
        "recommended_beds": ["marimba-G-116", "marimba-heist-Dm-112", "marimba-Am-120"]
    },
    "mystery": {
        "id": "mystery",
        "name": "Misteri & Anomali Berbasis Bukti",
        "description": "Evidence-based What-If inquiries into unexplained physical phenomena, cosmological anomalies, and forensics.",
        "default_environment": "physics-lab",
        "allowed_environments": ["physics-lab", "science-lab", "optics-lab"],
        "default_floor_y": 1380,
        "color_tokens": {
            "primary": "#4338CA",       # Deep investigation indigo
            "secondary": "#B91C1C",     # Evidence red
            "accent": "#FBBF24",        # Flashlight amber
            "paper_cream": "#FAF8F5",
            "paper_kraft": "#BCAB95",
            "text_dark": "#18181B"
        },
        "presenter": {
            "character": "CatScientist",
            "role_title": "Detektif Anomali",
            "default_state": "curious",
            "glasses": True,
            "lab_coat": True
        },
        "reusable_models": [
            "EvidencePinBoard",
            "MagnifyingLensCutout",
            "SpectralAnomalyMeter",
            "MysteryRevelationDial"
        ],
        "default_banner_prefix": "",
        "tone": "suspenseful, inquisitive, evidence-backed, dramatic",
        "default_bed": "marimba-heist-Dm-112",
        "recommended_beds": ["marimba-heist-Dm-112", "night-rain-piano-F", "marimba-Am-120"]
    },
    "psychology": {
        "id": "psychology",
        "name": "Psikologi & Sains Perilaku",
        "description": "Behavioral and cognitive What-If scenarios exploring human perception shifts, altered psychology, and collective civilizational effects.",
        "default_environment": "science-laboratory",
        "allowed_environments": ["science-laboratory", "physics-lab", "botany-greenhouse"],
        "default_floor_y": 1380,
        "color_tokens": {
            "primary": "#8B5CF6",       # Mind violet / synapse purple
            "secondary": "#EC4899",     # Emotional pink / behavioral rose
            "accent": "#F59E0B",        # Dopamine amber / curiosity gold
            "paper_cream": "#FAF8F5",
            "paper_kraft": "#D8CEB9",
            "text_dark": "#1E1B4B"
        },
        "presenter": {
            "character": "CatScientist",
            "role_title": "Psikolog Kucing",
            "default_state": "thinking",
            "glasses": True,
            "lab_coat": True
        },
        "reusable_models": [
            "BrainCrossSectionModel",
            "DopamineSynapseMeter",
            "CognitiveBiasDiorama",
            "AnalogPerceptionDial",
            "ThoughtBubbleArray"
        ],
        "default_banner_prefix": "",
        "tone": "introspective, mind-bending, empathetic, scientifically grounded",
        "default_bed": "marimba-hr-C-104",
        "recommended_beds": ["marimba-hr-C-104", "kalimba-spa-D-100", "marimba-Am-120"]
    }
}


def get_niche_profile(niche_id: str) -> Dict[str, Any]:
    clean_id = niche_id.strip().lower()
    if clean_id not in NICHES:
        raise ValueError(f"Unknown niche '{niche_id}'. Supported niches: {list(NICHES.keys())}")
    return NICHES[clean_id]


def list_supported_niches() -> List[str]:
    return list(NICHES.keys())
