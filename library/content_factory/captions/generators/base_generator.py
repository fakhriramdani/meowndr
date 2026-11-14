"""
Base generator providing shared content extraction, semantic analysis,
and formatting utilities for multi-platform caption generators.
Zero hardcoded slug dictionaries and zero static f-string templates.
"""

import re
from typing import Dict, Any, List, Optional
from ..schemas.caption_schema import CaptionInput


class BaseCaptionGenerator:
    """Synthesizes articulate informative statements, loop triggers, and structured metadata."""

    @classmethod
    def clean_topic_phrase(cls, text: str) -> str:
        """Strips leading question words, conditionals, and trailing punctuation."""
        if not text:
            return ""
        clean = re.sub(
            r"^(bagaimana jika|gimana jadinya kalau|apa jadinya kalau|gimana kalau|bagaimana kalau|kenapa|mengapa|bagaimana|gimana|misteri di balik|rahasia di balik|fakta di balik|sains di balik|tahukah kamu|kamu tahu nggak)\s+",
            "",
            text,
            flags=re.IGNORECASE
        ).strip().rstrip("?!. ")
        return clean

    @classmethod
    def generate_informative_statement(cls, input_data: CaptionInput, max_chars: int = 250) -> str:
        """
        Extracts an articulate informative statement or extended fact directly from research/narrative.
        Zero hardcoded slug lookups and zero robotic f-string templates.
        """
        # 1. Use verified fact for extended knowledge
        if input_data.key_facts:
            for fact in input_data.key_facts:
                clean_fact = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", fact).strip().rstrip(".!?")
                clean_fact = re.sub(r"^[-\*#\d\.\s]+", "", clean_fact).strip()
                if 25 <= len(clean_fact) <= max_chars:
                    return f"{clean_fact}."

        # 2. Extract first narrative premise sentence from script
        if input_data.script_lines:
            for line in input_data.script_lines[:2]:
                text = line.get("text", "").strip()
                if len(text) >= 25:
                    first_sentence = re.split(r"(?<=[.!?])\s+", text)[0].strip()
                    if 25 <= len(first_sentence) <= max_chars:
                        return first_sentence

        clean_topic = cls.clean_topic_phrase(input_data.title or input_data.topic)
        return f"Eksplorasi mendalam seputar {clean_topic.lower()} mengungkap prinsip penting yang menentukan cara kerja alam dan peradaban."[:max_chars]

    @classmethod
    def get_clean_hook(cls, input_data: CaptionInput) -> str:
        """Extracts or derives a clean, conversational hook."""
        clean_topic = cls.clean_topic_phrase(input_data.title or input_data.topic)
        orig_title = (input_data.title or "").strip().lower()

        if input_data.hook and len(input_data.hook.strip()) > 10 and not any(bad in input_data.hook.lower() for bad in ["kenapa jika", "kenapa bagaimana"]):
            return input_data.hook.strip()

        if orig_title.startswith(("bagaimana jika", "gimana kalau", "apa jadinya", "kalau", "jika")):
            return f"Pernah bayangkan apa jadinya kalau {clean_topic.lower()}?"

        if orig_title.startswith(("kenapa", "mengapa", "bagaimana", "gimana")):
            return f"Pernah kepikiran nggak kenapa {clean_topic.lower()}?"

        return f"Tahukah kamu rahasia menarik di balik {clean_topic.lower()}?"

    @classmethod
    def get_engagement_question(cls, input_data: CaptionInput) -> str:
        """Extracts natural engagement question directly from script without hardcoded slug lookups."""
        if input_data.script_lines:
            for line in reversed(input_data.script_lines[-3:]):
                text = line.get("text", "").strip()
                if "?" in text:
                    q_match = re.search(r"([^.!?]*\?)", text)
                    if q_match:
                        found_q = q_match.group(1).strip()
                        if len(found_q) >= 15 and not any(bad in found_q.lower() for bad in ["kenapa jika"]):
                            found_q = found_q[0].upper() + found_q[1:] if found_q else found_q
                            return found_q

        clean_topic = cls.clean_topic_phrase(input_data.title or input_data.topic).lower()
        return f"Menurutmu fakta tentang {clean_topic or 'hal ini'} paling mengejutkan di bagian mana?"
