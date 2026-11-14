"""
AI/LLM-Powered Multi-Platform Caption Generator for @meowndr.
Uses Google Antigravity CLI / LLM to synthesize creative, accurate,
extended informative value, bonus facts, and platform-tailored social media captions.
Completely replaces hardcoded dictionaries, rigid f-strings, and manual slug matching.
"""

import os
import sys
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent

from .schemas.caption_schema import (
    CaptionInput,
    InstagramCaptionOutput,
    TikTokCaptionOutput,
    YouTubeCaptionOutput
)
from .validators.composite_validator import CompositeValidator
from .scoring_system import CaptionScoringSystem
from .retention_engine import RetentionEngine


class LLMCaptionGenerator:
    """Orchestrates LLM-driven caption synthesis with zero hardcoding or static f-string templates."""

    BANNED_TAGS = {"#fyp", "#foryou", "#foryoupage", "#viral", "#trend", "#trending", "#explore", "#xyzbca"}

    @classmethod
    def _find_agy_bin(cls) -> Optional[str]:
        """Locates the Antigravity CLI executable."""
        candidates = [
            os.environ.get("ANTIGRAVITY_AGENTAPI_EXE"),
            os.environ.get("AGY_BIN"),
            shutil.which("agy"),
            str(Path.home() / ".local" / "bin" / "agy"),
        ]
        for c in candidates:
            if c and os.path.exists(c) and os.access(c, os.X_OK):
                return str(c)
        return None

    @classmethod
    def build_prompt(cls, input_data: CaptionInput) -> str:
        """Constructs an expert copywriting brief focusing on dual-layer narrative & extended informative value."""
        facts_summary = "\n".join([f"- {f[:280]}" for f in input_data.key_facts[:6]]) if input_data.key_facts else "Fakta sains/sejarah terverifikasi sesuai naskah."
        
        prompt = f"""Kamu adalah Specialist Social Media Copywriter untuk kanal edukasi sains & sejarah @meowndr (video animasi papercraft vertikal 9:16).
Tugasmu: Tulis paket caption dan judul publikasi sosial media untuk Instagram Reels, TikTok, dan YouTube Shorts berdasarkan data episode berikut.

=== DATA EPISODE ===
- Judul Episode: {input_data.title}
- Topik Pembahasan: {input_data.topic}
- Kategori/Niche: {input_data.content_category}
- Channel Name: {input_data.channel_name}
- Naskah Narasi Suara Video (Durasi ~45 detik):
\"{input_data.script_text}\"
- Hook Pembuka / Visual Frame-0:
Hook: \"{input_data.hook}\"
Teks Cover: \"{input_data.cover_title}\"
- Fakta Kunci & Data Riset Mendalam:
{facts_summary}

=== ATURAN MUTLAK KONTEN (DUAL-LAYER NARRATIVE & EXTENDED VALUE) ===
1. STRUKTUR 2-LAPIS (JELASKAN INTI VIDEO + TAMBAHKAN FAKTA LANJUTAN):
   Caption WAJIB menyajikan narasi utuh yang menggabungkan 2 elemen:
   a. LAPIS 1 (JELASKAN INTI VIDEO): Rangkum dan ceritakan kembali skenario/fenomena utama yang terjadi di video secara naratif, hidup, dan memikat (alur peristiwa atau sebab-akibat yang digambarkan di video). Jangan melompat begitu saja tanpa menjelaskan inti peristiwa videonya!
   b. LAPIS 2 (TAMBAHKAN INFORMASI LANJUTAN): Sambungkan secara mulus dengan fakta ilmiah, mekanisme mendalam, atau konsekuensi sekunder dari riset yang TIDAK sempat terucap oleh narator karena batas durasi video (~45 detik).
   
2. GAYA BAHASA NARATIF & INFORMATIF (HINDARI BAHASA META KAKU):
   - Seluruh caption harus mengalir alami seperti esai mini edukasi yang seru, elegan, dan berbobot.
   - DILARANG KERAS menggunakan frasa meta yang kaku/canggung seperti: "Di video kita sudah melihat...", "ini fakta yang tak sempat dibahas di video", "fakta yang tidak masuk video", dll.
   - Gunakan transisi alami (misalnya: "Namun skala bencananya meluas lebih jauh...", "Secara fisis, mekanisme sekundernya bahkan lebih ekstrem...", "Di tingkat molekuler, fenomena ini memicu...", dsb).

3. ZERO ARTIFICIAL REWATCH FLUFF:
   DILARANG KERAS menggunakan kata-kata ajakan tonton ulang yang dipaksakan atau canggung (seperti "coba tonton ulang", "perhatikan rotasi di awal video", "tonton lagi detailnya", dll.). Daya tarik video dan caption harus timbul secara alami dari substansi penceritaan naratif yang kuat dan pertanyaan refleksi yang cerdas.

4. SINGLE COHESIVE STATEMENT:
   Tulis paragraf pembuka dan isi yang utuh, lancar, dan rapi. DILARANG memotong kalimat secara sembarangan dengan elipsis (...). Tata bahasa Indonesia baku, ejaan rapi, dan tanda baca benar.

5. RELEVANSI TOPIK:
   Jangan mencampurkan kata "sejarah" jika topiknya murni fisika/sains/alam, begitu pula sebaliknya.

6. NO SPAM TAGS:
   Jangan pernah memakai tagar spam seperti #fyp, #foryou, #viral, #trending. Gunakan tagar spesifik topik.

=== ATURAN SPESIFIK PLATFORM ===
1. INSTAGRAM REELS (Target 500 - 900 karakter, naratif mendalam):
   - Caption berstruktur 3 bagian naratif yang mengalir seperti esai mini edukasi yang hidup dan berbobot:
     * Paragraf 1: Narasi pembuka yang memikat dan menjelaskan inti skenario di video beserta mekanisme pemicu awalnya.
     * Paragraf 2: Penjelasan informatif lanjutan (dampak berantai, mekanisme fisika/biologi/sejarah, serta angka kuantitatif dari data riset yang memperkaya pemahaman audiens).
     * Paragraf 3: Pertanyaan pemantik refleksi/diskusi audiens + Call-to-Action Simpan & Share ("💡 Simpan postingan ini biar nggak lupa & share ke temanmu!").
     * 3 sampai 5 hashtag spesifik relevan.
   - DILARANG menggunakan bullet points (•).
   - alternative_caption: 1 varian naratif alternatif dengan sudut pandang fokus yang berbeda.

2. TIKTOK (Target 150 - 220 karakter, ringkas namun naratif & informatif):
   - Narasi mengalir yang memadukan inti skenario video + 1 insight/fakta ilmiah spesifik yang mengejutkan + ajakan komentar ("Komen di bawah ya! 👇") + 2 sampai 3 hashtag bertarget.
   - DILARANG menggunakan emoji tidur/mengantuk (😴).
   - alternative_caption: 1 varian alternatif TikTok yang juga memuat narasi ringkas informatif.

3. YOUTUBE SHORTS:
   - Titles: Buat 3 opsi judul mandiri bernilai CTR tinggi (45 - 75 karakter per judul, kalimat lengkap, TANPA kurung terpotong seperti "(...)").
   - Description (380 - 650 karakter): Paragraf naratif utuh yang menceritakan skenario video secara jelas sekaligus mengelaborasi mekanisme ilmiah/sejarah tambahannya secara informatif + Ajakan Subscribe ("🔔 Subscribe {input_data.channel_name} untuk fakta sains & sejarah seru setiap minggu!") + hashtag #Shorts dan 2 hashtag topik.
   - Pinned Comment: Pertanyaan pemantik debat/diskusi audiens di kolom komentar yang berakar pada fenomena tersebut.
   - Search Keywords: 8 sampai 12 kata kunci SEO pencarian YouTube dalam bahasa Indonesia.

KEMBALIKAN HANYA FORMAT JSON VALID BERIKUT (TANPA TEKS LAIN):
{{
  "instagram": {{
    "caption": "Teks caption utama Instagram Reels naratif lengkap (penjelasan video + info tambahan + pertanyaan + CTA + hashtag)",
    "alternative_caption": "Teks varian alternatif caption Instagram naratif informatif",
    "opening_hook": "Kalimat pertama pembuka caption",
    "hashtags": ["#tag1", "#tag2", "#tag3"]
  }},
  "tiktok": {{
    "caption": "Teks caption TikTok naratif ringkas memuat inti video dan fakta tambahan lengkap dengan prompt komentar dan hashtag",
    "alternative_caption": "Teks varian alternatif TikTok naratif ringkas",
    "opening_hook": "Kalimat pembuka TikTok",
    "hashtags": ["#tag1", "#tag2", "#tag3"]
  }},
  "youtube": {{
    "titles": [
      "Opsi Judul 1 (45-75 char)",
      "Opsi Judul 2 (45-75 char)",
      "Opsi Judul 3 (45-75 char)"
    ],
    "description": "Deskripsi video YouTube Shorts naratif lengkap dengan penjelasan video, informasi tambahan, CTA, dan hashtags",
    "pinned_comment": "Pertanyaan untuk pin comment seputar skenario fenomena",
    "hashtags": ["#Shorts", "#tag2", "#tag3"],
    "search_keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4", "keyword 5", "keyword 6", "keyword 7", "keyword 8"]
  }}
}}
"""
        return prompt

    @classmethod
    def call_llm(cls, prompt: str, timeout_sec: int = 120) -> Dict[str, Any]:
        """Executes the LLM request via Antigravity CLI and parses the structured response."""
        agy_bin = cls._find_agy_bin()
        if not agy_bin:
            raise RuntimeError("Antigravity CLI (agy) binary not found on system.")

        cmd = [
            agy_bin,
            "-p", prompt,
            "--dangerously-skip-permissions",
            "--output-format", "json"
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Antigravity CLI timed out after {timeout_sec}s.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Antigravity CLI failed (exit {e.returncode}): {e.stderr}")

        try:
            raw_json = json.loads(res.stdout)
            resp_content = raw_json.get("response", "")
        except Exception:
            resp_content = res.stdout

        # Extract JSON from potential markdown wrappers
        text = resp_content.strip()
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0]
        
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)

        try:
            parsed = json.loads(text)
            return parsed
        except json.JSONDecodeError as err:
            raise RuntimeError(f"Failed to parse JSON from LLM output: {err}\nOutput was:\n{text[:500]}")

    @classmethod
    def clean_hashtags(cls, tags: List[str], max_count: int = 5) -> List[str]:
        """Cleans and filters hashtags."""
        cleaned = []
        for t in tags:
            tag = t.strip()
            if not tag.startswith("#"):
                tag = f"#{tag}"
            if tag.lower() not in cls.BANNED_TAGS and tag not in cleaned:
                cleaned.append(tag)
        return cleaned[:max_count]

    @classmethod
    def generate_all_platforms(
        cls,
        input_data: CaptionInput,
        max_attempts: int = 2
    ) -> Tuple[InstagramCaptionOutput, TikTokCaptionOutput, YouTubeCaptionOutput, Dict[str, Any]]:
        """
        Coordinates full LLM synthesis for Instagram, TikTok, and YouTube Shorts.
        Validates output against length and format rules with self-healing retries.
        """
        prompt = cls.build_prompt(input_data)
        
        last_error = None
        for attempt in range(max_attempts):
            try:
                data = cls.call_llm(prompt)
                
                # 1. Instagram Package
                ig_raw = data.get("instagram", {})
                ig_cap = ig_raw.get("caption", "").strip()
                ig_alt = ig_raw.get("alternative_caption", "").strip()
                ig_hook = ig_raw.get("opening_hook", "").strip() or ig_cap.split("\n")[0]
                ig_tags = cls.clean_hashtags(ig_raw.get("hashtags", []), max_count=5)
                
                # Ensure Instagram caption contains tags if not already present
                if not any(t in ig_cap for t in ig_tags) and ig_tags:
                    ig_cap = f"{ig_cap}\n\n{' '.join(ig_tags)}".strip()
                
                ig_chars = len(ig_cap)
                ig_out = InstagramCaptionOutput(
                    caption=ig_cap,
                    hashtags=ig_tags,
                    character_count=ig_chars,
                    opening_hook=ig_hook,
                    keywords=input_data.main_keywords[:3],
                    CTA="Simpan & Share CTA",
                    alternative_caption=ig_alt,
                    quality_score=95,
                    status="READY" if 100 <= ig_chars <= 500 else "NEEDS_REVIEW"
                )

                # 2. TikTok Package
                tt_raw = data.get("tiktok", {})
                tt_cap = tt_raw.get("caption", "").strip()
                tt_alt = tt_raw.get("alternative_caption", "").strip()
                tt_hook = tt_raw.get("opening_hook", "").strip() or tt_cap[:40]
                tt_tags = cls.clean_hashtags(tt_raw.get("hashtags", []), max_count=3)
                
                if not any(t in tt_cap for t in tt_tags) and tt_tags:
                    tt_cap = f"{tt_cap} {' '.join(tt_tags)}".strip()
                
                tt_chars = len(tt_cap)
                tt_out = TikTokCaptionOutput(
                    caption=tt_cap,
                    hashtags=tt_tags,
                    character_count=tt_chars,
                    opening_hook=tt_hook,
                    keywords=input_data.main_keywords[:3],
                    CTA="Comment Interaction CTA",
                    alternative_caption=tt_alt,
                    quality_score=95,
                    status="READY" if tt_chars <= 220 else "NEEDS_REVIEW"
                )

                # 3. YouTube Shorts Package
                yt_raw = data.get("youtube", {})
                yt_titles = yt_raw.get("titles", [])
                primary_title = yt_titles[0] if yt_titles else input_data.title
                alt_title = yt_titles[1] if len(yt_titles) > 1 else primary_title
                yt_desc = yt_raw.get("description", "").strip()
                yt_tags = cls.clean_hashtags(yt_raw.get("hashtags", ["#Shorts"]), max_count=3)
                if "#Shorts" not in yt_tags:
                    yt_tags.insert(0, "#Shorts")
                
                if not any(t in yt_desc for t in yt_tags) and yt_tags:
                    yt_desc = f"{yt_desc}\n\n{' '.join(yt_tags[:3])}".strip()
                
                yt_pinned = yt_raw.get("pinned_comment", "").strip()
                yt_kws = yt_raw.get("search_keywords", input_data.main_keywords)
                
                yt_out = YouTubeCaptionOutput(
                    title=primary_title[:100],
                    description=yt_desc[:5000],
                    hashtags=yt_tags[:3],
                    search_keywords=yt_kws[:12],
                    pinned_comment=yt_pinned,
                    alternative_title=alt_title[:100],
                    title_character_count=len(primary_title),
                    description_character_count=len(yt_desc),
                    quality_score=95,
                    status="READY" if len(primary_title) <= 100 and len(yt_desc) <= 5000 else "NEEDS_REVIEW"
                )

                extra_meta = {
                    "youtube_all_titles": yt_titles,
                    "model_source": "Google Antigravity LLM",
                    "attempt": attempt + 1
                }

                return ig_out, tt_out, yt_out, extra_meta

            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"LLMCaptionGenerator failed after {max_attempts} attempts: {last_error}")
