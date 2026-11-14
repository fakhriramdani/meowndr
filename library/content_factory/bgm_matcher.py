#!/usr/bin/env python3
"""
BGM Matcher for Papercraft Content Factory (@meowndr).
Intelligently matches video themes, niches, titles, and scripts
with optimal background music (BGM) beds from the papercut audio library.

Available Beds:
1. marimba-Am-120: Cheeky, tense-fun (everyday oddities, paradoxes, reflexes)
2. marimba-F-108: Curious, light (botany, biology, daylight nature wonders)
3. marimba-G-116: Upbeat, confident (technology, physics, lasers, electricity, energy)
4. marimba-heist-Dm-112: Sneaky, tense mystery (espionage, secrets, boreholes, black holes)
5. marimba-hr-C-104: Bouncy, psychological dread (dopamine, habits, memory glitches, doorways)
6. kalimba-spa-D-100: Calm, cozy wellness (health, sleep, coffee, digestion, tears, body)
7. kalimba-story-G-66: Storybook, ancient, bedtime (history, archaeology, ancient scrolls/libraries)
8. night-rain-piano-F: Lo-fi rainy night, introspective (rain, petrichor, oceans, atmospheric calm)
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BEDS_DIR = REPO_ROOT / "library" / "audio" / "beds"

# Canonical BGM Bed Definitions & Thematic Profiles
AVAILABLE_BEDS: Dict[str, Dict[str, Any]] = {
    "marimba-Am-120": {
        "name": "marimba-Am-120",
        "bpm": 120,
        "mood": "cheeky, tense-fun",
        "instrument": "marimba",
        "file": "marimba-Am-120.json",
        "primary_niche": "science",
        "suitable_niches": ["science", "mystery", "psychology"],
        "keywords": [
            "paradoks", "aneh", "beku", "otak", "freeze", "menguap", "cegukan",
            "kucing", "refleks", "unik", "lucu", "trik", "makanan", "pedas", "lidah",
            "sensasi", "menular", "kejanggalan", "everyday", "fun", "bizarre",
            "geli", "kaget", "bingung", "saraf", "reaksi", "tubuh"
        ],
        "description": "Cheeky minor marimba with hand claps, ideal for fast everyday bodily paradoxes, witty questions, and playful science oddities."
    },
    "marimba-F-108": {
        "name": "marimba-F-108",
        "bpm": 108,
        "mood": "curious, light",
        "instrument": "marimba",
        "file": "marimba-F-108.json",
        "primary_niche": "science",
        "suitable_niches": ["science", "geography", "history"],
        "keywords": [
            "daun", "tumbuhan", "tanaman", "fotosintesis", "serangga", "cahaya",
            "bunga", "hewan", "alam", "biologi", "matahari", "ekosistem", "hutan",
            "oksigen", "langit", "warna", "atmosfer", "senja", "pelangi", "bumi",
            "greenhouse", "klorofil", "akar", "botani", "fauna", "flora"
        ],
        "description": "Bright, gentle marimba pop, perfect for botany, nature curiosity, light biology, and daylight atmospheric wonders."
    },
    "marimba-G-116": {
        "name": "marimba-G-116",
        "bpm": 116,
        "mood": "upbeat, confident",
        "instrument": "marimba",
        "file": "marimba-G-116.json",
        "primary_niche": "technology",
        "suitable_niches": ["technology", "science", "geography"],
        "keywords": [
            "teknologi", "komputer", "robot", "listrik", "tesla", "menara", "energi",
            "ai", "laser", "kuantum", "kecepatan", "cahaya", "jarum", "petir",
            "fisika", "reaktor", "nuklir", "satelit", "roket", "antariksa", "mesin",
            "relativitas", "partikel", "daya", "voltase", "magnet", "foton"
        ],
        "description": "Upbeat, energetic marimba groove with soft claps, tailored for technology, physics breakthroughs, high energy, and kinetic phenomena."
    },
    "marimba-heist-Dm-112": {
        "name": "marimba-heist-Dm-112",
        "bpm": 112,
        "mood": "sneaky, heist, tense",
        "instrument": "marimba",
        "file": "marimba-heist-Dm-112.json",
        "primary_niche": "mystery",
        "suitable_niches": ["mystery", "technology", "geography"],
        "keywords": [
            "misteri", "rahasia", "sadap", "penyadapan", "spy", "intelijen", "cia",
            "kgb", "lubang", "borehole", "kola", "black hole", "lubang hitam",
            "konspirasi", "anomali", "tersembunyi", "kriptik", "bawah tanah",
            "kedalaman", "gelap", "bahaya", "investigasi", "spionase", "kebocoran"
        ],
        "description": "Tense and sneaky minor marimba with finger snaps, crafted for mysteries, surveillance, deep subterranean boreholes, and cryptic phenomena."
    },
    "marimba-hr-C-104": {
        "name": "marimba-hr-C-104",
        "bpm": 104,
        "mood": "cheesy, corporate, warm, bouncy, wink of dread",
        "instrument": "marimba",
        "file": "marimba-hr-C-104.json",
        "primary_niche": "psychology",
        "suitable_niches": ["psychology", "science"],
        "keywords": [
            "psikologi", "dopamin", "dopamine", "kebiasaan", "habit", "scroll",
            "media sosial", "kamar", "lupa", "pintu", "doorway effect", "otak",
            "memori", "bias", "kognitif", "perilaku", "fokus", "prokrastinasi",
            "kecanduan", "jebakan", "sosial", "kantor", "psikis", "atensi"
        ],
        "description": "Bouncy corporate marimba with a wink of psychological dread, ideal for cognitive biases, dopamine loops, and memory quirks."
    },
    "kalimba-spa-D-100": {
        "name": "kalimba-spa-D-100",
        "bpm": 100,
        "mood": "calm, cozy, wellness",
        "instrument": "kalimba",
        "file": "kalimba-spa-D-100.json",
        "primary_niche": "science",
        "suitable_niches": ["science", "psychology"],
        "keywords": [
            "kesehatan", "kopi", "ngantuk", "tidur", "adenosin", "makan", "kenyang",
            "food coma", "lemas", "bawang", "nangis", "air mata", "relaksasi",
            "tubuh", "darah", "jantung", "pencernaan", "spa", "hangat", "wellness",
            "tenang", "mata", "nutrisi", "istirahat", "lambung"
        ],
        "description": "Warm kalimba with finger snaps and water plips, ideal for human biology, sleep, coffee, digestion, and soothing bodily processes."
    },
    "kalimba-story-G-66": {
        "name": "kalimba-story-G-66",
        "bpm": 66,
        "mood": "calm, tender, storybook, bedtime",
        "instrument": "kalimba",
        "file": "kalimba-story-G-66.json",
        "primary_niche": "history",
        "suitable_niches": ["history", "geography"],
        "keywords": [
            "sejarah", "kuno", "peradaban", "aleksandria", "perpustakaan", "buku",
            "arsip", "arkeologi", "candi", "piramida", "kerajaan", "zaman",
            "masa lalu", "legenda", "manuskrip", "dongeng", "bintang", "asal usul",
            "bangsa", "artefak", "prasasti", "evolusi", "purba"
        ],
        "description": "Lyrical storybook kalimba with warm pad and sparkle, perfect for ancient history, lost civilization, and archival deep dives."
    },
    "night-rain-piano-F": {
        "name": "night-rain-piano-F",
        "bpm": 62,
        "mood": "gloomy-but-warm, intimate, lo-fi rainy night",
        "instrument": "piano & rain",
        "file": "night-rain-piano-F.json",
        "primary_niche": "geography",
        "suitable_niches": ["geography", "mystery", "science"],
        "keywords": [
            "hujan", "rain", "petrichor", "aroma hujan", "bau tanah", "malam",
            "badai", "rintik", "melankolis", "sunyi", "tetesan"
        ],
        "description": "Intimate felt piano over real ambient rain on glass, crafted for petrichor, rainy weather science, deep oceans, and quiet mysteries."
    }
}

# Niche Default Fallback Bed
NICHE_DEFAULT_BEDS: Dict[str, str] = {
    "science": "marimba-F-108",
    "history": "kalimba-story-G-66",
    "geography": "marimba-F-108",
    "technology": "marimba-G-116",
    "mystery": "marimba-heist-Dm-112",
    "psychology": "marimba-hr-C-104"
}


def _normalize_text(text: str) -> str:
    """Normalize text into lowercase alphanumeric space-delimited tokens."""
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def match_bgm_for_episode(
    title: str,
    topic: str = "",
    niche: str = "science",
    script_text: str = ""
) -> Dict[str, Any]:
    """
    Intelligently select the best matching BGM bed preset based on
    episode title, topic, niche, and optional voiceover script content.

    Returns:
        Dict with keys:
            - preset: Canonical preset name (e.g. 'marimba-heist-Dm-112')
            - bpm: Tempo in BPM
            - mood: Descriptive mood
            - instrument: Primary instrument family
            - score: Match relevance score
            - match_reason: Human-readable rationale
            - all_scores: Diagnostic scores across all 8 beds
    """
    clean_niche = niche.strip().lower() if niche else "science"
    norm_title = _normalize_text(title)
    norm_topic = _normalize_text(topic)
    norm_script = _normalize_text(script_text)

    scores: Dict[str, float] = {}
    matched_reasons: Dict[str, List[str]] = {}

    for bed_name, bed_info in AVAILABLE_BEDS.items():
        score = 0.0
        reasons = []

        # 1. Niche Affinity
        if bed_info["primary_niche"] == clean_niche:
            score += 4.0
            reasons.append(f"Primary niche '{clean_niche}' match (+4.0)")
        elif clean_niche in bed_info["suitable_niches"]:
            score += 2.0
            reasons.append(f"Suitable for niche '{clean_niche}' (+2.0)")

        # 2. Keyword Matching in Title (Heavy Weight: 3.5 per match)
        title_hits = []
        for kw in bed_info["keywords"]:
            # Check whole word match or phrase match
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, norm_title):
                score += 3.5
                title_hits.append(kw)
        if title_hits:
            reasons.append(f"Title keywords: {title_hits} (+{len(title_hits) * 3.5:.1f})")

        # 3. Keyword Matching in Topic (Medium Weight: 2.5 per match)
        topic_hits = []
        for kw in bed_info["keywords"]:
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, norm_topic):
                score += 2.5
                topic_hits.append(kw)
        if topic_hits:
            reasons.append(f"Topic keywords: {topic_hits} (+{len(topic_hits) * 2.5:.1f})")

        # 4. Keyword Matching in Narration Script (Light Weight: 0.5 per match, max 3.0)
        if norm_script:
            script_hits = []
            for kw in bed_info["keywords"]:
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, norm_script):
                    script_hits.append(kw)
            if script_hits:
                script_bonus = min(3.0, len(script_hits) * 0.5)
                score += script_bonus
                reasons.append(f"Script keywords: {script_hits[:4]} (+{script_bonus:.1f})")

        scores[bed_name] = round(score, 2)
        matched_reasons[bed_name] = reasons

    # Select candidate with the highest score
    sorted_candidates = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best_bed_name, best_score = sorted_candidates[0]

    # If top score is very weak (<= 4.0, only niche default with no keywords),
    # ensure niche default is respected
    if best_score <= 4.0 and clean_niche in NICHE_DEFAULT_BEDS:
        default_bed = NICHE_DEFAULT_BEDS[clean_niche]
        if default_bed in AVAILABLE_BEDS:
            best_bed_name = default_bed
            best_score = scores.get(best_bed_name, 4.0)

    chosen = AVAILABLE_BEDS[best_bed_name]
    summary_reason = "; ".join(matched_reasons.get(best_bed_name, []))
    if not summary_reason:
        summary_reason = f"Default bed for niche '{clean_niche}'"

    return {
        "preset": chosen["name"],
        "bpm": chosen["bpm"],
        "mood": chosen["mood"],
        "instrument": chosen["instrument"],
        "score": best_score,
        "match_reason": summary_reason,
        "description": chosen["description"],
        "all_scores": scores
    }


def get_bed_info(bed_name: str) -> Optional[Dict[str, Any]]:
    """Get metadata for a specific BGM bed preset."""
    clean_name = bed_name.strip()
    if clean_name.endswith(".json"):
        clean_name = clean_name[:-5]
    return AVAILABLE_BEDS.get(clean_name)


def list_available_beds() -> List[Dict[str, Any]]:
    """List all supported BGM beds with metadata."""
    return list(AVAILABLE_BEDS.values())


def validate_bed_preset(bed_name: str) -> bool:
    """Verify that a bed preset name exists in the audio library beds directory."""
    clean_name = bed_name.strip()
    if clean_name.endswith(".json"):
        clean_name = clean_name[:-5]
    if clean_name not in AVAILABLE_BEDS:
        return False
    bed_path = BEDS_DIR / f"{clean_name}.json"
    return bed_path.exists()
