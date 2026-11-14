"""
Hashtag Intelligence Module for multi-platform short-form video publishing.
Generates platform-tailored, niche-aware, high-relevance hashtags with strict negative filtering.
"""

import re
from typing import List, Dict, Set, Optional
from .schemas.caption_schema import CaptionInput


class HashtagIntelligence:
    """Intelligently synthesizes and filters hashtags based on topic, niche, audience, and platform."""

    BANNED_TAGS = {
        "#fyp", "#foryou", "#foryoupage", "#viral", "#trend", "#trending",
        "#explore", "#likeforlike", "#followforfollow", "#xyzbca"
    }

    INDONESIAN_STOPWORDS: Set[str] = {
        "kenapa", "mengapa", "bagaimana", "gimana", "adalah", "saat", "bisa", "lebih", "dalam", "yang",
        "malah", "bikin", "buat", "kok", "terus", "kalau", "jika", "bila", "tetapi", "tapi",
        "namun", "padahal", "hanya", "cuma", "bukan", "tidak", "nggak", "tiap", "setiap",
        "semua", "seluruh", "antara", "tanpa", "tentang", "seperti", "bagai", "bagaikan",
        "seolah", "ingin", "mau", "sedang", "masih", "telah", "pernah", "sempat", "selalu",
        "sering", "jarang", "banyak", "sedikit", "amat", "sangat", "terlalu", "paling",
        "agak", "cukup", "tentu", "pasti", "mungkin", "kira", "ngira", "boleh", "harus", "wajib",
        "mesti", "dapat", "sanggup", "ada", "yaitu", "yakni", "ialah", "merupakan",
        "begini", "begitu", "demikian", "sini", "situ", "sana", "mana", "siapa", "apa",
        "kapan", "berapa", "saja", "pun", "lah", "kah", "tah", "dong", "deh", "sih",
        "kan", "yuk", "mari", "ayo", "wah", "aduh", "hai", "halo", "dari", "pada",
        "dengan", "untuk", "oleh", "karena", "maka", "jadi", "juga", "kamu", "kita",
        "sudah", "akan", "lalu", "sesudah", "sebelum", "hingga", "sampai", "agar", "supaya",
        "habis", "sehabis", "setelah", "makan", "minum", "kenyang", "lapar", "langsung",
        "berat", "ringan", "tiba", "siang", "malam", "pagi", "sore", "hari", "balik",
        "rahasia", "alasannya", "penasaran", "fakta", "tahu", "tahukah", "tubuh",
        "orang", "waktu", "secara", "coba", "menu", "satu", "dua", "tiga", "mata",
        "matamu", "seberat", "kelopak", "lemas", "pengen", "tidur", "tumbang",
        "triknya", "gampang", "kurangi", "porsi", "jalan", "santai", "menit", "video",
        "pengingat", "besok", "ketiduran", "piring", "sepiring", "nasi", "padang"
    }

    # Niche-to-hashtag mapping for educational categories
    NICHE_TAG_POOLS: Dict[str, List[str]] = {
        "science": ["#sains", "#faktasains", "#belajarsains", "#sainspopuler", "#eksperimen"],
        "history": ["#sejarah", "#sejarahdunia", "#faktasejarah", "#arkeologi", "#kisahsejarah"],
        "geography": ["#geografi", "#bumi", "#alam", "#faktaalam", "#keajaibanalam"],
        "technology": ["#teknologi", "#inovasi", "#sainsteknologi", "#ai", "#gadget"],
        "mystery": ["#misteri", "#faktamisteri", "#misterialam", "#faktaaneh", "#fenomena"],
        "psychology": ["#psikologi", "#otakmanusia", "#faktapsikologi", "#kesehatranmental", "#pikiran"],
        "health": ["#kesehatan", "#faktatubuh", "#biologi", "#tubuhmanusia", "#ilmukesehatan"]
    }

    @classmethod
    def _clean_tag(cls, text: str) -> str:
        """Converts arbitrary text into a clean CamelCase or lowercase hashtag."""
        # Remove accents and non-alphanumeric
        cleaned = re.sub(r"[^\w\s]", "", text)
        words = cleaned.split()
        if not words:
            return ""
        # Filter stopwords
        filtered_words = [w for w in words if w.lower() not in cls.INDONESIAN_STOPWORDS]
        if not filtered_words:
            return ""
        # CamelCase for multi-word or compact
        if len(filtered_words) > 1:
            tag_name = "".join(w.capitalize() for w in filtered_words[:3])
        else:
            tag_name = filtered_words[0].lower()
            if tag_name in cls.INDONESIAN_STOPWORDS or len(tag_name) < 3:
                return ""
        return f"#{tag_name}"

    @classmethod
    def generate_topic_tags(cls, input_data: CaptionInput) -> List[str]:
        """Extracts specific topic hashtags from slug, quotes, key facts, topic, and keywords."""
        topic_tags = []

        def add_tag(candidate: str):
            if not candidate:
                return
            cleaned = cls._clean_tag(candidate) if not candidate.startswith("#") else candidate
            if cleaned and cleaned not in topic_tags and cleaned.lower() not in cls.BANNED_TAGS:
                raw_stem = cleaned.lstrip("#").lower()
                if raw_stem not in cls.INDONESIAN_STOPWORDS and len(raw_stem) >= 3:
                    topic_tags.append(cleaned)

        # 1. From slug (e.g. "26-food-coma" -> #FoodComa, "20-aroma-hujan-petrichor" -> #Petrichor, #AromaHujan)
        if getattr(input_data, "slug", None):
            clean_slug = re.sub(r"^\d+[-_]", "", input_data.slug).strip()
            parts = [p for p in re.split(r"[-_]", clean_slug) if p]
            slug_words = [p for p in parts if p.lower() not in cls.INDONESIAN_STOPWORDS]
            if slug_words:
                add_tag(" ".join(slug_words[:3]))
                for part in slug_words:
                    if len(part) >= 5 and part.lower() not in cls.INDONESIAN_STOPWORDS:
                        add_tag(part)

        # 2. From quoted terms or terms in parentheses (e.g. 'Food Coma', "Rest and Digest")
        full_title_topic = f"{input_data.topic} {input_data.title}"
        quoted_phrases = re.findall(r"['\"]([^'\"]+)['\"]", full_title_topic)
        for qp in quoted_phrases:
            add_tag(qp)

        # 3. From scientific facts & script (specific technical terms)
        combined_text = " ".join(input_data.key_facts) + " " + input_data.script_text
        technical_terms = re.findall(r"\b[A-Z][a-z]{3,}\b", combined_text)
        common_capitalized = {"Pernah", "Banyak", "Begitu", "Nasi", "Tubuh", "Nah", "Biar", "Simpan", "Menu", "Ternyata", "Video", "Kucing"}
        for term in technical_terms:
            if term not in common_capitalized and term.lower() not in cls.INDONESIAN_STOPWORDS:
                add_tag(term)

        # 4. From primary keywords
        for kw in input_data.main_keywords:
            clean_kw = kw.lower().strip()
            if clean_kw in cls.INDONESIAN_STOPWORDS or len(clean_kw) < 4:
                continue
            add_tag(clean_kw)

        # 5. From topic
        if input_data.topic:
            topic_words = [w for w in re.findall(r"[a-zA-Z0-9]+", input_data.topic) if len(w) >= 4]
            filtered_words = [w for w in topic_words if w.lower() not in cls.INDONESIAN_STOPWORDS]
            if filtered_words:
                add_tag(" ".join(filtered_words[:2]))

        return topic_tags

    @classmethod
    def get_niche_tags(cls, niche: str) -> List[str]:
        """Returns relevant niche tags for category."""
        norm_niche = niche.lower().strip()
        # Fallback to science if unknown
        return cls.NICHE_TAG_POOLS.get(norm_niche, cls.NICHE_TAG_POOLS["science"])

    @classmethod
    def generate_for_instagram(cls, input_data: CaptionInput) -> List[str]:
        """Instagram Reels: 3-5 relevant hashtags (max 5)."""
        tags = []
        topic_tags = cls.generate_topic_tags(input_data)
        niche_tags = cls.get_niche_tags(input_data.content_category)

        # 1. Topic tag (1-2)
        for t in topic_tags[:2]:
            if t not in tags:
                tags.append(t)

        # 2. Niche tags
        for nt in niche_tags:
            if len(tags) >= 4:
                break
            if nt not in tags:
                tags.append(nt)

        # 3. Channel tag
        channel_tag = f"#{input_data.channel_name.lstrip('@')}"
        if channel_tag not in tags and len(tags) < 5:
            tags.append(channel_tag)

        # Fallback if too few
        if len(tags) < 3:
            for fallback in ["#faktasains", "#edukasi", "#meowndr"]:
                if fallback not in tags and len(tags) < 5:
                    tags.append(fallback)

        return tags[:5]

    @classmethod
    def generate_for_tiktok(cls, input_data: CaptionInput) -> List[str]:
        """TikTok: 2-3 relevant hashtags (max 4, no #FYP spam)."""
        tags = []
        topic_tags = cls.generate_topic_tags(input_data)
        niche_tags = cls.get_niche_tags(input_data.content_category)

        # 1. Most specific topic tag
        if topic_tags:
            tags.append(topic_tags[0])

        # 2. Educational / curiosity niche tag
        for nt in niche_tags:
            if nt not in tags:
                tags.append(nt)
                break

        # 3. Third tag: facts / education
        general_tags = ["#faktaunik", "#faktasains", "#belajarsains", "#edukasi"]
        for gt in general_tags:
            if len(tags) >= 3:
                break
            if gt not in tags:
                tags.append(gt)

        return tags[:3]

    @classmethod
    def generate_for_youtube(cls, input_data: CaptionInput) -> List[str]:
        """YouTube Shorts: 2-3 hashtags (including #Shorts)."""
        tags = ["#Shorts"]
        topic_tags = cls.generate_topic_tags(input_data)
        niche_tags = cls.get_niche_tags(input_data.content_category)

        # 1. Topic or primary niche tag
        if topic_tags:
            tags.append(topic_tags[0])
        elif niche_tags:
            tags.append(niche_tags[0])

        # 2. General category tag
        for nt in niche_tags:
            if len(tags) >= 3:
                break
            if nt not in tags:
                tags.append(nt)

        if len(tags) < 2:
            tags.append("#FaktaSains")

        return tags[:3]
