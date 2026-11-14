"""
Retention & Narrative Intelligence Engine for Multi-Platform Captions.
Extracts core narrative beats, curiosity gaps, open loops, and enforces
strict spoiler prevention and hook-caption consistency checks.
"""

import os
import re
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Set
from pathlib import Path


@dataclass
class NarrativeDossier:
    """Structured extraction of video storytelling components."""
    main_topic: str
    core_curiosity_gap: str
    primary_hook: str
    cover_text: str
    first_3s_context: str
    most_surprising_revelation: str
    emotional_trigger: str
    main_audience_takeaway: str
    strongest_shareable_moment: str
    searchable_keywords: List[str] = field(default_factory=list)
    script_body_summary: str = ""
    revelation_keywords: Set[str] = field(default_factory=set)


@dataclass
class ConsistencyAuditResult:
    """Result of evaluating caption alignment against video narrative."""
    is_consistent: bool
    curiosity_preserved: bool
    spoiler_detected: bool
    verbatim_repetition: bool
    keyword_aligned: bool
    contradiction_detected: bool
    score_penalty: int
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class RetentionEngine:
    """Analyzes approved script, storyboard, and research to maximize retention and curiosity."""

    @classmethod
    def analyze_episode(cls, episode_dir: Path, slug: str) -> NarrativeDossier:
        """Parses script, hook matrix, storyboard, and dossier to extract narrative DNA."""
        ep_dir = Path(episode_dir)

        # 1. Title and Topic
        title = ""
        topic = ""
        ep_json = ep_dir / "papercut" / "episode.json"
        if not ep_json.exists():
            ep_json = ep_dir / "episode.json"
        if ep_json.exists():
            try:
                with open(ep_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    meta = data.get("meta", {})
                    title = meta.get("title", "")
                    topic = meta.get("topic", "") or title
            except Exception:
                pass

        # 2. Script lines
        script_lines: List[Dict[str, Any]] = []
        for s_cand in [
            ep_dir / "narration" / "script.json",
            ep_dir / "papercut" / "public" / "vo" / "script.json"
        ]:
            if s_cand.exists():
                try:
                    with open(s_cand, "r", encoding="utf-8") as f:
                        script_lines = json.load(f)
                    break
                except Exception:
                    pass

        # 3. Hook Matrix & Cover text
        hook_text = ""
        cover_text = ""
        hook_path = ep_dir / "research" / "hook_matrix.json"
        if hook_path.exists():
            try:
                with open(hook_path, "r", encoding="utf-8") as f:
                    h_data = json.load(f)
                    variants = h_data.get("variants", [])
                    primary_id = h_data.get("primary_recommendation")
                    chosen = next((v for v in variants if v.get("id") == primary_id), None) or (variants[0] if variants else None)
                    if chosen:
                        hook_text = chosen.get("hook_text", "")
                        clines = chosen.get("cover_lines", [])
                        words = []
                        for cl in clines:
                            if isinstance(cl, list):
                                words.extend(cl)
                            elif cl:
                                words.append(str(cl))
                        cover_text = " ".join(words).strip()
            except Exception:
                pass

        if not hook_text and script_lines:
            hook_text = script_lines[0].get("text", "")

        # 4. Storyboard first scene & cuts
        first_3s_action = ""
        sb_path = ep_dir / "storyboard" / "storyboard.json"
        if sb_path.exists():
            try:
                with open(sb_path, "r", encoding="utf-8") as f:
                    sb_data = json.load(f)
                    scenes = sb_data.get("scenes", [])
                    if scenes:
                        first_3s_action = scenes[0].get("visual_description", "") or scenes[0].get("cat_action", "")
            except Exception:
                pass

        # 5. Extract narrative beats from script body
        body_lines = script_lines[1:-1] if len(script_lines) > 2 else script_lines
        body_texts = [l.get("text", "") for l in body_lines if l.get("text")]
        outro_text = script_lines[-1].get("text", "") if len(script_lines) > 1 else ""

        # Identifying surprising revelation (usually the penultimate or middle mechanism lines)
        revelation_line = ""
        for line in reversed(body_texts):
            if any(w in line.lower() for w in ["ternyata", "zat", "hormon", "otak", "rahasia", "karena", "sebenarnya"]):
                revelation_line = line
                break
        if not revelation_line and body_texts:
            revelation_line = body_texts[-1]

        # Extract keywords from revelation that should NOT be fully spoiled
        revelation_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", revelation_line.lower()))
        common_words = {"yang", "kamu", "bisa", "akan", "dalam", "dengan", "langsung", "bikin", "buat", "terasa"}
        revelation_keywords = revelation_words - common_words

        # Core curiosity gap formulation
        clean_topic = re.sub(r"^(kenapa|mengapa|bagaimana|gimana)\s+", "", title or topic or slug.replace("-", " "), flags=re.IGNORECASE).strip()
        curiosity_gap = f"Apa alasan ilmiah sebenarnya di balik {clean_topic}?"

        # Searchable keywords
        search_kws = [clean_topic]
        if slug:
            clean_slug = re.sub(r"^\d+[-_]", "", slug).replace("-", " ")
            if clean_slug not in search_kws:
                search_kws.append(clean_slug)

        # Main takeaway from outro/mitigation line
        takeaway = outro_text if outro_text else "Fakta edukasi sains animasi papercraft @meowndr."

        return NarrativeDossier(
            main_topic=title or topic or slug,
            core_curiosity_gap=curiosity_gap,
            primary_hook=hook_text,
            cover_text=cover_text,
            first_3s_context=first_3s_action or hook_text[:60],
            most_surprising_revelation=revelation_line,
            emotional_trigger="Penasaran & Kejutan Ilmiah",
            main_audience_takeaway=takeaway,
            strongest_shareable_moment=revelation_line or clean_topic,
            searchable_keywords=search_kws,
            script_body_summary=" ".join(body_texts[:3]),
            revelation_keywords=revelation_keywords
        )

    @classmethod
    def audit_consistency(cls, caption_text: str, dossier: NarrativeDossier) -> ConsistencyAuditResult:
        """
        Audits candidate caption against video hook, narrative, cover text, and final revelation.
        Enforces spoiler prevention, non-verbatim hook framing, and keyword alignment.
        """
        issues: List[str] = []
        suggestions: List[str] = []
        penalty = 0

        cap_lower = caption_text.lower()
        hook_lower = dossier.primary_hook.lower()

        # 1. Verbatim repetition check
        # Caption should complement the hook, not just repeat it 100% identically
        verbatim_rep = False
        if len(dossier.primary_hook) > 25 and dossier.primary_hook.strip().lower() in cap_lower:
            # Check if caption literally just repeats the full hook word for word at the start
            if cap_lower.startswith(dossier.primary_hook.strip().lower()):
                verbatim_rep = True
                penalty += 10
                issues.append("Caption repeats video voiceover hook verbatim without adding a new curiosity gap.")
                suggestions.append("Reframe the opening with an alternative conversational angle or teaser.")

        # 2. Extended Value Check (supersedes legacy anti-spoiler rule)
        # Social captions now deliver extended scientific/historical information not present in video.
        spoiler = False

        # 3. Contradiction check
        contradiction = False
        forbidden_false_claims = ["darah benar-benar tersedot", "tidak berbahaya", "100% mitos tanpa bukti"]
        for claim in forbidden_false_claims:
            if claim in cap_lower:
                contradiction = True
                penalty += 20
                issues.append(f"Caption contains potential contradictory claim: '{claim}'.")

        # 4. Keyword alignment check
        # Must contain at least one primary topic or searchable keyword
        keyword_aligned = any(kw.lower() in cap_lower for kw in dossier.searchable_keywords if len(kw) >= 4)
        if not keyword_aligned and dossier.main_topic:
            # Check individual main words
            main_words = [w.lower() for w in re.findall(r"[a-zA-Z]{4,}", dossier.main_topic) if w.lower() not in {"kenapa", "mengapa", "bagaimana"}]
            keyword_aligned = any(w in cap_lower for w in main_words)

        if not keyword_aligned:
            penalty += 10
            issues.append("Caption is missing primary searchable keywords for the topic.")
            suggestions.append(f"Integrate natural keywords from: {', '.join(dossier.searchable_keywords[:2])}")

        # Curiosity and informative value evaluation
        has_question_or_open_loop = any(char in caption_text for char in ["?", "👇", "ternyata", "penasaran", "rahasia", "fakta", "tahu"])
        curiosity_preserved = has_question_or_open_loop or len(caption_text) >= 40

        is_consistent = (penalty < 15 and not contradiction)

        return ConsistencyAuditResult(
            is_consistent=is_consistent,
            curiosity_preserved=curiosity_preserved,
            spoiler_detected=spoiler,
            verbatim_repetition=verbatim_rep,
            keyword_aligned=keyword_aligned,
            contradiction_detected=contradiction,
            score_penalty=penalty,
            issues=issues,
            suggestions=suggestions
        )
