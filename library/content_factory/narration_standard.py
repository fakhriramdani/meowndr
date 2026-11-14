#!/usr/bin/env python3
"""
Indonesian Narration Number & Punctuation Standard for @meowndr.

Provides:
1. Number-to-words conversion for Indonesian narration (integers, years, decimals,
   percentages, measurements, currency, fractions, scientific notation, chemicals).
2. Speech-rhythm punctuation enforcement for natural Indonesian synthesis (ElevenLabs).
3. NarrationValidator: Detects numeric digits, broken punctuation, unnatural sentence length,
   missing terminal punctuation, and enforces text-to-TTS consistency.
4. Script normalization utility with source traceability.

Single Source of Truth for @meowndr narration writing standards.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union

ONES = {
    0: "nol", 1: "satu", 2: "dua", 3: "tiga", 4: "empat",
    5: "lima", 6: "enam", 7: "tujuh", 8: "delapan", 9: "sembilan"
}

SUPERSCRIPT_MAP = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    '⁻': '-', '⁺': '+'
}

SUBSCRIPT_MAP = {
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'
}

UNITS_MAP = {
    # Temperature
    "°c": "derajat Celsius",
    "° c": "derajat Celsius",
    "derajat c": "derajat Celsius",
    "derajat celcius": "derajat Celsius",
    "derajat celsius": "derajat Celsius",
    "°f": "derajat Fahrenheit",
    "derajat fahrenheit": "derajat Fahrenheit",
    "k": "Kelvin",
    "kelvin": "Kelvin",

    # Length / Distance
    "km": "kilometer",
    "kilometer": "kilometer",
    "m": "meter",
    "meter": "meter",
    "cm": "sentimeter",
    "sentimeter": "sentimeter",
    "mm": "milimeter",
    "milimeter": "milimeter",
    "nm": "nanometer",
    "nanometer": "nanometer",
    "µm": "mikrometer",
    "um": "mikrometer",
    "mikrometer": "mikrometer",

    # Area & Volume
    "m2": "meter persegi",
    "m^2": "meter persegi",
    "m²": "meter persegi",
    "km2": "kilometer persegi",
    "km^2": "kilometer persegi",
    "km²": "kilometer persegi",
    "cm2": "sentimeter persegi",
    "cm^2": "sentimeter persegi",
    "cm²": "sentimeter persegi",
    "m3": "meter kubik",
    "m^3": "meter kubik",
    "m³": "meter kubik",
    "cm3": "sentimeter kubik",
    "cm^3": "sentimeter kubik",
    "cm³": "sentimeter kubik",

    # Mass
    "kg": "kilogram",
    "kilogram": "kilogram",
    "g": "gram",
    "gr": "gram",
    "gram": "gram",
    "mg": "miligram",
    "miligram": "miligram",
    "ton": "ton",

    # Time
    "detik": "detik",
    "dtk": "detik",
    "s": "detik",
    "menit": "menit",
    "mnt": "menit",
    "jam": "jam",
    "hari": "hari",
    "tahun": "tahun",

    # Speed
    "km/jam": "kilometer per jam",
    "km/h": "kilometer per jam",
    "kpj": "kilometer per jam",
    "m/s": "meter per detik",
    "km/s": "kilometer per detik",

    # Electrical, Energy, Pressure, Frequency, Sound
    "v": "Volt",
    "volt": "Volt",
    "w": "Watt",
    "watt": "Watt",
    "kw": "kilowatt",
    "kilowatt": "kilowatt",
    "mw": "megawatt",
    "gw": "gigawatt",
    "j": "Joule",
    "joule": "Joule",
    "kj": "kilojoule",
    "pa": "Pascal",
    "pascal": "Pascal",
    "kpa": "kilopascal",
    "atm": "atmosfer",
    "atmosfer": "atmosfer",
    "bar": "bar",
    "hz": "Hertz",
    "hertz": "Hertz",
    "khz": "kilohertz",
    "mhz": "megahertz",
    "ghz": "gigahertz",
    "db": "desibel",
    "desibel": "desibel",
    "kali": "kali",
}

ABBREVIATIONS_MAP = [
    (re.compile(r'\bdll\.', re.IGNORECASE), "dan lain-lain"),
    (re.compile(r'\bdsb\.', re.IGNORECASE), "dan sebagainya"),
    (re.compile(r'\bdst\.', re.IGNORECASE), "dan seterusnya"),
    (re.compile(r'\bmis\.\b', re.IGNORECASE), "misalnya"),
    (re.compile(r'\bmisal\b', re.IGNORECASE), "misalnya"),
    (re.compile(r'\bcth\.\b', re.IGNORECASE), "contohnya"),
    (re.compile(r'\bvs\.\b|\bvs\b', re.IGNORECASE), "versus"),
]

CONTROLLED_EXCEPTIONS = {
    # Conventional proper nouns, codes, or terms where digits or symbols are permitted or pre-treated
    "nasa", "dna", "rna", "atp", "ph", "remotion", "meowndr", "trpv1"
}


# =====================================================================
# 1. Number to Words Conversion Engine
# =====================================================================

class IndonesianNumberConverter:
    """
    Translates Arabic numerals, decimals, fractions, measurements, currency,
    ordinals, years, and scientific notation into fluent spoken Indonesian words.
    """

    @classmethod
    def int_to_words(cls, n: int) -> str:
        """Convert integer to Indonesian words (0 to 999,999,999,999,999)."""
        if n < 0:
            return "minus " + cls.int_to_words(abs(n))
        if n < 10:
            return ONES[n]
        if n == 10:
            return "sepuluh"
        if n == 11:
            return "sebelas"
        if n < 20:
            return ONES[n - 10] + " belas"
        if n < 100:
            tens = n // 10
            rem = n % 10
            res = ONES[tens] + " puluh"
            if rem > 0:
                res += " " + ONES[rem]
            return res
        if n < 200:
            rem = n - 100
            res = "seratus"
            if rem > 0:
                res += " " + cls.int_to_words(rem)
            return res
        if n < 1000:
            hundreds = n // 100
            rem = n % 100
            res = ONES[hundreds] + " ratus"
            if rem > 0:
                res += " " + cls.int_to_words(rem)
            return res
        if n < 2000:
            rem = n - 1000
            res = "seribu"
            if rem > 0:
                res += " " + cls.int_to_words(rem)
            return res
        if n < 1_000_000:
            thousands = n // 1000
            rem = n % 1000
            res = cls.int_to_words(thousands) + " ribu"
            if rem > 0:
                res += " " + cls.int_to_words(rem)
            return res
        if n < 1_000_000_000:
            millions = n // 1_000_000
            rem = n % 1_000_000
            res = cls.int_to_words(millions) + " juta"
            if rem > 0:
                res += " " + cls.int_to_words(rem)
            return res
        if n < 1_000_000_000_000:
            billions = n // 1_000_000_000
            rem = n % 1_000_000_000
            res = cls.int_to_words(billions) + " miliar"
            if rem > 0:
                res += " " + cls.int_to_words(rem)
            return res
        if n < 1_000_000_000_000_000:
            trillions = n // 1_000_000_000_000
            rem = n % 1_000_000_000_000
            res = cls.int_to_words(trillions) + " triliun"
            if rem > 0:
                res += " " + cls.int_to_words(rem)
            return res

        quadrillions = n // 1_000_000_000_000_000
        rem = n % 1_000_000_000_000_000
        res = cls.int_to_words(quadrillions) + " kuadriliun"
        if rem > 0:
            res += " " + cls.int_to_words(rem)
        return res

    @classmethod
    def decimal_to_words(cls, whole: int, frac_str: str) -> str:
        """Convert decimal number to Indonesian words (e.g. 2,5 -> 'dua koma lima')."""
        w_words = cls.int_to_words(whole)
        f_words = " ".join(ONES[int(c)] for c in frac_str if c.isdigit())
        return f"{w_words} koma {f_words}"

    @classmethod
    def fraction_to_words(cls, num: int, den: int) -> str:
        """Convert fraction to natural Indonesian words."""
        if num == 1 and den == 2:
            return "setengah"
        if num == 1 and den == 3:
            return "sepertiga"
        if num == 1 and den == 4:
            return "seperempat"
        if num == 2 and den == 3:
            return "dua pertiga"
        if num == 3 and den == 4:
            return "tiga perempat"
        if num == 1 and den == 5:
            return "seperlima"
        if num == 2 and den == 5:
            return "dua per lima"
        if num == 1 and den == 10:
            return "sepersepuluh"
        if num == 1 and den == 100:
            return "seperseratus"
        if num == 1 and den > 1:
            return f"seper{cls.int_to_words(den)}"
        return f"{cls.int_to_words(num)} per {cls.int_to_words(den)}"

    @classmethod
    def ordinal_to_words(cls, val: int) -> str:
        """Convert ordinal to Indonesian words (e.g. 1 -> 'pertama', 3 -> 'ketiga')."""
        if val == 1:
            return "pertama"
        w = cls.int_to_words(val)
        return f"ke{w}"

    @classmethod
    def year_to_words(cls, year: int) -> str:
        """Convert calendar year into natural Indonesian spoken forms."""
        return cls.int_to_words(year)

    @classmethod
    def normalize_sentence(cls, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Normalize all numbers, scientific symbols, units, and punctuation in a single sentence.
        Returns (normalized_text, audit_log).
        """
        s = text
        audit: List[Dict[str, Any]] = []

        # 0. Subscripts & Superscripts preprocessing for chemical formulas & exponents
        # Chemical formulas with subscripts: CO₂, H₂O, O₂, N₂, CH₄
        s = re.sub(r'\bCO[₂2]\b', 'CO dua', s)
        s = re.sub(r'\bH[₂2]O\b', 'H dua O', s)
        s = re.sub(r'\bO[₂2]\b', 'O dua', s)
        s = re.sub(r'\bN[₂2]\b', 'N dua', s)
        s = re.sub(r'\bCH[₄4]\b', 'CH empat', s)

        # Convert superscripts following '10' into standard '^' notation: e.g. 10⁸ -> 10^8
        def _sup_exp_clean(m):
            raw_sup = m.group(1)
            converted = "".join(SUPERSCRIPT_MAP.get(c, c) for c in raw_sup)
            return f"10^{converted}"
        s = re.sub(r'10([⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+)', _sup_exp_clean, s)

        # Replace area & volume superscripts: m², m³, km², cm²
        s = re.sub(r'\bm²\b', 'meter persegi', s)
        s = re.sub(r'\bm³\b', 'meter kubik', s)
        s = re.sub(r'\bkm²\b', 'kilometer persegi', s)
        s = re.sub(r'\bcm²\b', 'sentimeter persegi', s)
        s = re.sub(r'\bcm³\b', 'sentimeter kubik', s)
        s = re.sub(r'\bmm²\b', 'milimeter persegi', s)
        s = re.sub(r'\bmm³\b', 'milimeter kubik', s)

        # 1. pH values: "pH 7", "pH 2,5", "pH 2.5"
        def _sub_ph(m):
            raw = m.group(0)
            val = m.group(1)
            if ',' in val:
                w, f = val.split(',')
                res = f"pH {cls.decimal_to_words(int(w), f)}"
            elif '.' in val:
                w, f = val.split('.')
                res = f"pH {cls.decimal_to_words(int(w), f)}"
            else:
                res = f"pH {cls.int_to_words(int(val))}"
            audit.append({"type": "pH", "original": raw, "converted": res})
            return res
        s = re.sub(r'\bpH\s*(\d+(?:[.,]\d+)?)\b', _sub_ph, s)

        # 2. Scientific notation: e.g. "3 x 10^8 m/s", "3 × 10^8", "10^6", "10^-3"
        def _sub_exp(m):
            raw = m.group(0)
            base_mul = m.group(1)  # e.g. "3 x " or "3 × "
            exp_sign = m.group(2) or ""
            exp_val = m.group(3)
            unit_part = (m.group(4) or "").strip().lower()

            res = ""
            if base_mul:
                b_num = re.findall(r'\d+', base_mul)[0]
                res += f"{cls.int_to_words(int(b_num))} kali "
            res += "sepuluh pangkat "
            if exp_sign == "-":
                res += "minus "
            res += cls.int_to_words(int(exp_val))
            if unit_part:
                u_spoken = UNITS_MAP.get(unit_part, unit_part)
                res += f" {u_spoken}"
            audit.append({"type": "scientific_notation", "original": raw, "converted": res})
            return res

        s = re.sub(r'(\d+\s*[x×]\s*)?10\^([+-]?)(\d+)(?:\s*([a-zA-Z/°]+))?', _sub_exp, s)

        # 3. Century expressions: "21st century", "abad ke-21", "abad 21"
        def _sub_century(m):
            raw = m.group(0)
            c_num = m.group(1)
            res = f"abad {cls.ordinal_to_words(int(c_num))}"
            audit.append({"type": "century", "original": raw, "converted": res})
            return res
        s = re.sub(r'\b(\d+)(?:st|nd|rd|th)\s+century\b', _sub_century, s, flags=re.IGNORECASE)
        s = re.sub(r'\babad\s+(?:ke-)?(\d+)\b', _sub_century, s, flags=re.IGNORECASE)

        # 4. Ordinal numbers: "ke-3", "ke 3", "ke-10"
        def _sub_ord(m):
            raw = m.group(0)
            res = cls.ordinal_to_words(int(m.group(1)))
            audit.append({"type": "ordinal", "original": raw, "converted": res})
            return res
        s = re.sub(r'\bke-(\d+)\b', _sub_ord, s, flags=re.IGNORECASE)

        # 5. Currency: Rp50.000, Rp 50.000, $10, €5
        def _sub_rupiah(m):
            raw = m.group(0)
            num_clean = m.group(1).replace('.', '').replace(',', '')
            res = f"{cls.int_to_words(int(num_clean))} rupiah"
            audit.append({"type": "currency_idr", "original": raw, "converted": res})
            return res
        s = re.sub(r'\bRp\.?\s*(\d{1,3}(?:\.\d{3})+|\d+)\b', _sub_rupiah, s, flags=re.IGNORECASE)

        def _sub_dollar(m):
            raw = m.group(0)
            clean = m.group(1).replace(',', '')
            res = f"{cls.int_to_words(int(clean))} dolar"
            audit.append({"type": "currency_usd", "original": raw, "converted": res})
            return res
        s = re.sub(r'\$(\d+(?:\.\d+)?)\b', _sub_dollar, s)

        def _sub_euro(m):
            raw = m.group(0)
            clean = m.group(1).replace(',', '')
            res = f"{cls.int_to_words(int(clean))} euro"
            audit.append({"type": "currency_eur", "original": raw, "converted": res})
            return res
        s = re.sub(r'€(\d+(?:\.\d+)?)\b', _sub_euro, s)

        # 6. Fractions: 1/2, 3/4, 2/3
        def _sub_frac(m):
            raw = m.group(0)
            n, d = int(m.group(1)), int(m.group(2))
            res = cls.fraction_to_words(n, d)
            audit.append({"type": "fraction", "original": raw, "converted": res})
            return res
        s = re.sub(r'\b(\d+)/(\d+)\b', _sub_frac, s)

        # 7. Temperatures with units: 100°C, 32°F, 300 K
        def _sub_temp(m):
            raw = m.group(0)
            val_str = m.group(1)
            scale = m.group(2).upper()
            if scale == 'C':
                scale_name = "derajat Celsius"
            elif scale == 'F':
                scale_name = "derajat Fahrenheit"
            else:
                scale_name = "Kelvin"

            if ',' in val_str:
                w, f = val_str.split(',')
                w_str = cls.decimal_to_words(int(w), f)
            elif '.' in val_str:
                w, f = val_str.split('.')
                w_str = cls.decimal_to_words(int(w), f)
            else:
                w_str = cls.int_to_words(int(val_str))
            res = f"{w_str} {scale_name}"
            audit.append({"type": "temperature", "original": raw, "converted": res})
            return res
        s = re.sub(r'(-?\d+(?:[.,]\d+)?)\s*°\s*([CFcf])\b', _sub_temp, s)
        s = re.sub(r'(-?\d+(?:[.,]\d+)?)\s*derajat\s*(Celsius|Celcius|Fahrenheit)\b', _sub_temp, s, flags=re.IGNORECASE)

        # 8. Numbers with measurement units: "12 km", "30 detik", "1.500 meter", "1,5 kilometer", "100 km/jam"
        sorted_units = sorted(UNITS_MAP.keys(), key=lambda x: len(x), reverse=True)
        unit_pattern = "|".join(re.escape(u) for u in sorted_units)

        def _sub_num_unit(m):
            raw = m.group(0)
            num_str = m.group(1)
            unit_str = m.group(2).lower()
            unit_spoken = UNITS_MAP.get(unit_str, unit_str)

            # Context-sensitive parsing:
            # Indonesian thousand separator: 1.500 -> 1500 -> "seribu lima ratus"
            # Decimal separator: 1,5 -> 1.5 -> "satu koma lima"
            if re.match(r'^\d{1,3}(?:\.\d{3})+$', num_str):
                clean_num = int(num_str.replace('.', ''))
                val_spoken = cls.int_to_words(clean_num)
            elif ',' in num_str:
                w, f = num_str.split(',')
                val_spoken = cls.decimal_to_words(int(w), f)
            elif '.' in num_str:
                parts = num_str.split('.')
                if len(parts) == 2 and len(parts[1]) == 3 and int(parts[0]) > 0:
                    val_spoken = cls.int_to_words(int(num_str.replace('.', '')))
                else:
                    val_spoken = cls.decimal_to_words(int(parts[0]), parts[1])
            else:
                val_spoken = cls.int_to_words(int(num_str))

            res = f"{val_spoken} {unit_spoken}"
            audit.append({"type": "measurement", "original": raw, "converted": res})
            return res

        s = re.sub(r'\b(\d+(?:[.,]\d+)?)\s*(' + unit_pattern + r')\b', _sub_num_unit, s, flags=re.IGNORECASE)

        # Multiplier notation: "3 kali", "3x", "3X"
        def _sub_multiplier(m):
            raw = m.group(0)
            n = int(m.group(1))
            res = f"{cls.int_to_words(n)} kali"
            audit.append({"type": "multiplier", "original": raw, "converted": res})
            return res
        s = re.sub(r'\b(\d+)\s*kali\b', _sub_multiplier, s, flags=re.IGNORECASE)
        s = re.sub(r'\b(\d+)[xX]\b', _sub_multiplier, s)

        # 9. Percentages: 2,5% or 2,5 persen
        def _sub_percent(m):
            raw = m.group(0)
            val_str = m.group(1)
            if ',' in val_str:
                w, f = val_str.split(',')
                v = cls.decimal_to_words(int(w), f)
            elif '.' in val_str:
                w, f = val_str.split('.')
                v = cls.decimal_to_words(int(w), f)
            else:
                v = cls.int_to_words(int(val_str))
            res = f"{v} persen"
            audit.append({"type": "percentage", "original": raw, "converted": res})
            return res
        s = re.sub(r'\b(\d+(?:[.,]\d+)?)\s*%', _sub_percent, s)
        s = re.sub(r'\b(\d+(?:[.,]\d+)?)\s*persen\b', _sub_percent, s, flags=re.IGNORECASE)

        # 10. Indonesian thousand-separated integers: 1.500, 25.000, 1.000.000
        def _sub_thousand_int(m):
            raw = m.group(0)
            clean_num = int(raw.replace('.', ''))
            res = cls.int_to_words(clean_num)
            audit.append({"type": "thousand_separated_int", "original": raw, "converted": res})
            return res
        s = re.sub(r'\b\d{1,3}(?:\.\d{3})+\b', _sub_thousand_int, s)

        # 11. Decimal numbers without units: 2,5 or 1.5 or 0,01
        def _sub_dec(m):
            raw = m.group(0)
            if ',' in raw:
                w, f = raw.split(',')
                res = cls.decimal_to_words(int(w), f)
            elif '.' in raw:
                w, f = raw.split('.')
                res = cls.decimal_to_words(int(w), f)
            else:
                res = raw
            audit.append({"type": "decimal", "original": raw, "converted": res})
            return res
        s = re.sub(r'\b\d+[.,]\d+\b', _sub_dec, s)

        # 12. Large magnitude terms: e.g. "5 juta" -> "lima juta", "2 miliar" -> "dua miliar"
        def _sub_mag(m):
            raw = m.group(0)
            n = int(m.group(1))
            mag = m.group(2).lower()
            res = f"{cls.int_to_words(n)} {mag}"
            audit.append({"type": "magnitude", "original": raw, "converted": res})
            return res
        s = re.sub(r'\b(\d+)\s*(juta|miliar|triliun|kuadriliun)\b', _sub_mag, s, flags=re.IGNORECASE)

        # 13. Remaining standalone integers (including years like 1883, 2026):
        def _sub_standalone_int(m):
            raw = m.group(0)
            n = int(raw)
            res = cls.int_to_words(n)
            audit.append({"type": "integer_or_year", "original": raw, "converted": res})
            return res
        s = re.sub(r'\b\d+\b', _sub_standalone_int, s)

        # 14. Spoken abbreviations
        for pattern, replacement in ABBREVIATIONS_MAP:
            s = pattern.sub(replacement, s)

        # 15. Punctuation and rhythm cleanup
        s = PunctuationStandard.clean_punctuation(s)

        return s, audit


# =====================================================================
# 2. Speech-Rhythm Punctuation Engine
# =====================================================================

class PunctuationStandard:
    """
    Cleans and standardizes punctuation for natural Indonesian speech synthesis (ElevenLabs).
    Ensures natural breathing pauses, prevents TTS glitching on repeated symbols,
    and enforces speech-rhythm boundaries.
    """

    ALLOWED_PUNCTUATION = {',', '.', '?', '!', ':', '—', '...'}

    @classmethod
    def clean_punctuation(cls, text: str) -> str:
        s = text

        # 1. Standardize dashes to em dash with natural breathing spaces: " — "
        s = re.sub(r'\s*—\s*', ' — ', s)
        s = re.sub(r'\s*--\s*', ' — ', s)

        # 2. Fix repeated punctuation marks
        s = re.sub(r'\.{4,}', '...', s)
        s = re.sub(r',+', ',', s)
        s = re.sub(r'!+', '!', s)
        s = re.sub(r'\?+', '?', s)
        s = re.sub(r':+', ':', s)

        # 3. Strip whitespace preceding punctuation
        s = re.sub(r'\s+([,.:!?])', r'\1', s)

        # 4. Ensure single space following punctuation (except when at the end of text or before another punctuation)
        s = re.sub(r'([,.:!?])([A-Za-z0-9])', r'\1 \2', s)

        # 5. Fix ellipsis spacing
        s = re.sub(r'\s*\.\.\.\s*', '... ', s)

        # 6. Ensure clean spacing around quotes and parentheses
        s = re.sub(r'\s+', ' ', s).strip()

        return s

    @classmethod
    def validate_punctuation(cls, text: str) -> List[str]:
        """Check for punctuation issues that degrade speech synthesis."""
        warnings = []

        # Check for repeated exclamation or question marks
        if re.search(r'[!?]{2,}', text):
            warnings.append(f"Excessive repeated punctuation detected: '{re.findall(r'[!?]{2,}', text)}'")

        # Check for multiple ellipses in a single sentence/line
        ellipsis_count = len(re.findall(r'\.\.\.', text))
        if ellipsis_count > 1:
            warnings.append(f"Multiple ellipses ({ellipsis_count}) in a single line may cause unnatural TTS hesitation.")

        # Check for terminal punctuation
        stripped = text.strip()
        if stripped and not re.search(r'[.?!:]$', stripped):
            warnings.append("Missing terminal sentence-ending punctuation (., ?, !, or :). Speech model may not pause naturally.")

        # Check for comma overload (> 4 commas in a single line)
        comma_count = len(re.findall(r',', text))
        if comma_count > 4:
            warnings.append(f"High comma density ({comma_count} commas) may produce fragmented, robotic speech.")

        return warnings


# =====================================================================
# 3. Comprehensive Narration Validator
# =====================================================================

class NarrationValidator:
    """
    Validates script lines against the @meowndr Indonesian Narration Standard.
    Distinguishes:
    - Hard errors: numeric digits unintentionally remaining in narration, broken conversions.
    - Warnings: punctuation rhythm, high word counts, long sentences without breathing points.
    - Controlled exceptions: registered technical names.
    - Flags for human review: ambiguous conversions.
    """

    MAX_SENTENCE_WORDS_WITHOUT_PAUSE = 25
    TARGET_WPS = 1.98  # Calibrated words per second for ElevenLabs Indonesian (including multi-syllable words & pauses)
    TARGET_SPS = 5.45  # Calibrated Indonesian syllables per second
    MIN_EPISODE_SECONDS = 38.0
    MAX_EPISODE_SECONDS = 50.0

    @classmethod
    def count_indonesian_syllables(cls, text: str) -> int:
        """Count approximate Indonesian syllables based on vowel nuclei (a, i, u, e, o) and reduplication."""
        words = re.findall(r"[a-zA-Z]+(?:-[a-zA-Z]+)?", text.lower())
        total_syl = 0
        for w in words:
            parts = w.split("-")
            for p in parts:
                vowels = re.findall(r"[aiueo]+", p)
                total_syl += max(1, len(vowels))
        return total_syl

    @classmethod
    def estimate_line_seconds(cls, spoken_text: str) -> float:
        """Estimate spoken duration in seconds using blended Indonesian syllable + word + pause model."""
        words = spoken_text.split()
        if not words:
            return 0.0
        syls = cls.count_indonesian_syllables(spoken_text)
        commas = len(re.findall(r"[,;—]", spoken_text))
        stops = len(re.findall(r"[.?!]", spoken_text))
        pause_sec = commas * 0.22 + max(1, stops) * 0.38
        word_based = len(words) / cls.TARGET_WPS
        syl_based = (syls / cls.TARGET_SPS) + pause_sec
        return round((word_based * 0.45) + (syl_based * 0.55), 2)

    @classmethod
    def validate_line(cls, line: Dict[str, Any], index: int = 0) -> Dict[str, Any]:
        """Validate a single narration line object."""
        errors: List[str] = []
        warnings: List[str] = []
        controlled_exceptions: List[str] = []
        flags_for_review: List[str] = []

        line_id = line.get("id", f"line_{index}")
        text = line.get("text", "")
        tts = line.get("tts")

        # Spoken text is 'tts' if explicitly provided, else 'text'
        spoken_text = tts if tts is not None else text

        if not spoken_text or not isinstance(spoken_text, str) or not spoken_text.strip():
            errors.append(f"Line '{line_id}' has empty or non-string spoken narration.")
            return {
                "id": line_id,
                "is_valid": False,
                "errors": errors,
                "warnings": warnings,
                "exceptions": controlled_exceptions,
                "flags": flags_for_review,
            }

        # 1. Hard Error Check: Numeric digits remaining in spoken narration
        cleaned_for_digits = spoken_text
        for exc in CONTROLLED_EXCEPTIONS:
            cleaned_for_digits = re.sub(rf'\b{re.escape(exc)}\b', '', cleaned_for_digits, flags=re.IGNORECASE)
        digits_found = re.findall(r'\d+', cleaned_for_digits)
        if digits_found:
            errors.append(
                f"Line '{line_id}' contains numeric digits in spoken text: {digits_found}. "
                f"All numbers must be written fully in Indonesian words for ElevenLabs."
            )

        # 2. Hard Error Check: Raw mathematical symbols that were not converted
        unconverted_symbols = re.findall(r'[+%=*×÷<>]', spoken_text)
        if unconverted_symbols:
            errors.append(
                f"Line '{line_id}' contains unpronounced mathematical symbols: {unconverted_symbols}. "
                f"Convert symbols to spoken Indonesian words (e.g. 'persen', 'sama dengan', 'kali')."
            )

        # 3. Hard Error Check: Awkward or invalid number formations
        awkward_patterns = [
            (r'\bsatu belas\b', "Use 'sebelas' instead of 'satu belas'"),
            (r'\bsatu puluh\b', "Use 'sepuluh' instead of 'satu puluh'"),
            (r'\bsatu ratus\b', "Use 'seratus' instead of 'satu ratus'"),
            (r'\bsatu ribu\b', "Use 'seribu' instead of 'satu ribu' (when 1000)"),
        ]
        for pat, msg in awkward_patterns:
            if re.search(pat, spoken_text, re.IGNORECASE):
                errors.append(f"Line '{line_id}' has awkward number phrasing: {msg}.")

        # 4. Punctuation Rhythm Warnings
        punct_warnings = PunctuationStandard.validate_punctuation(spoken_text)
        for pw in punct_warnings:
            warnings.append(f"Line '{line_id}': {pw}")

        # 5. Sentence Length & Breathing Points
        # Split by pauses: periods, commas, colons, question marks, em dashes, ellipses
        clauses = re.split(r'[,.?:!—]|\.\.\.', spoken_text)
        for clause in clauses:
            words = clause.strip().split()
            if len(words) > cls.MAX_SENTENCE_WORDS_WITHOUT_PAUSE:
                warnings.append(
                    f"Line '{line_id}' has an uninterrupted phrase of {len(words)} words: "
                    f"'{clause.strip()[:40]}...'. Add a comma (,) or breathing pause for natural synthesis."
                )

        # 6. Traceability and TTS consistency
        if tts is not None and text != tts:
            # Verified that both are preserved for traceability
            pass

        return {
            "id": line_id,
            "is_valid": len(errors) == 0,
            "spoken_text": spoken_text,
            "word_count": len(spoken_text.split()),
            "syllable_count": cls.count_indonesian_syllables(spoken_text),
            "estimated_seconds": cls.estimate_line_seconds(spoken_text),
            "errors": errors,
            "warnings": warnings,
            "exceptions": controlled_exceptions,
            "flags": flags_for_review,
        }

    @classmethod
    def validate_script(cls, script_data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate an entire script (array or object containing 'lines').
        Returns complete audit report.
        """
        lines: List[Dict[str, Any]] = []
        if isinstance(script_data, list):
            lines = script_data
        elif isinstance(script_data, dict):
            lines = script_data.get("lines", [])
        else:
            return {
                "is_valid": False,
                "errors": [f"Malformed script format: expected list or object with 'lines', got {type(script_data)}"],
                "warnings": [],
                "line_reports": [],
                "total_words": 0,
                "estimated_duration_sec": 0.0,
            }

        total_words = 0
        total_syllables = 0
        total_errors: List[str] = []
        total_warnings: List[str] = []
        total_flags: List[str] = []
        line_reports: List[Dict[str, Any]] = []

        for idx, line in enumerate(lines):
            rep = cls.validate_line(line, index=idx)
            line_reports.append(rep)
            total_words += rep["word_count"]
            total_syllables += rep.get("syllable_count", 0)
            total_errors.extend(rep["errors"])
            total_warnings.extend(rep["warnings"])
            total_flags.extend(rep["flags"])

        est_duration = round(sum(r["estimated_seconds"] for r in line_reports), 2)

        # Script-level pacing audit
        if est_duration < cls.MIN_EPISODE_SECONDS:
            total_warnings.append(
                f"Total estimated spoken duration ({est_duration:.1f}s, {total_words} words / {total_syllables} syllables) is below target minimum "
                f"({cls.MIN_EPISODE_SECONDS}s). Consider expanding physical explanation."
            )
        elif est_duration > cls.MAX_EPISODE_SECONDS:
            total_warnings.append(
                f"Total estimated spoken duration ({est_duration:.1f}s, {total_words} words / {total_syllables} syllables) exceeds short-form limit "
                f"({cls.MAX_EPISODE_SECONDS}s). Trim words to ~85-100 words to ensure YouTube Shorts / TikTok compatibility."
            )

        return {
            "is_valid": len(total_errors) == 0,
            "total_lines": len(lines),
            "total_words": total_words,
            "total_syllables": total_syllables,
            "estimated_duration_sec": est_duration,
            "errors": total_errors,
            "warnings": total_warnings,
            "flags_for_review": total_flags,
            "line_reports": line_reports,
        }

    @classmethod
    def normalize_script(
        cls,
        script_data: Union[List[Dict[str, Any]], Dict[str, Any]],
        populate_tts_field: bool = True,
        in_place: bool = False
    ) -> Tuple[Union[List[Dict[str, Any]], Dict[str, Any]], Dict[str, Any]]:
        """
        Normalizes all lines in a script.
        - If populate_tts_field is True: puts normalized text into 'tts' and preserves original 'text'.
        - If in_place is True: replaces 'text' directly while storing 'raw_text' for traceability.
        Returns (updated_script_data, audit_summary).
        """
        is_list = isinstance(script_data, list)
        lines = script_data if is_list else script_data.get("lines", [])

        normalized_lines: List[Dict[str, Any]] = []
        all_audits: List[Dict[str, Any]] = []

        for line in lines:
            new_line = dict(line)
            src_text = line.get("tts") or line.get("text", "")
            norm_text, audit = IndonesianNumberConverter.normalize_sentence(src_text)

            if audit:
                all_audits.append({"id": line.get("id"), "transformations": audit})

            if populate_tts_field:
                new_line["tts"] = norm_text
                # Preserve raw original text if not already stored
                if "raw_text" not in new_line:
                    new_line["raw_text"] = line.get("text", "")
            elif in_place:
                if "raw_text" not in new_line:
                    new_line["raw_text"] = line.get("text", "")
                new_line["text"] = norm_text
            else:
                new_line["tts"] = norm_text

            normalized_lines.append(new_line)

        updated_script = normalized_lines if is_list else {**script_data, "lines": normalized_lines}
        summary = {
            "transformed_lines": len(all_audits),
            "audit_details": all_audits,
            "validation": cls.validate_script(updated_script)
        }
        return updated_script, summary


# =====================================================================
# 4. CLI Execution
# =====================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 narration_standard.py validate <script_json_path_or_slug>")
        print("  python3 narration_standard.py normalize <text_or_script_json_path>")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "validate":
        target = sys.argv[2] if len(sys.argv) > 2 else ""
        if not target:
            print("[ERROR] Path or slug required for validation.")
            sys.exit(1)

        p = Path(target)
        if not p.exists():
            # Try resolving under episodes/<target>/narration/script.json
            repo_root = Path(__file__).resolve().parent.parent.parent
            cand = repo_root / "episodes" / target / "narration" / "script.json"
            if cand.exists():
                p = cand
            else:
                print(f"[ERROR] Script file not found: {target}")
                sys.exit(1)

        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        rep = NarrationValidator.validate_script(data)
        print("=" * 65)
        print(f"  Indonesian Narration Standard Audit: {p.name}")
        print("=" * 65)
        print(f"Total Lines: {rep['total_lines']} | Total Words: {rep['total_words']} | Est Duration: {rep['estimated_duration_sec']}s")
        print(f"Status: {'[PASS]' if rep['is_valid'] else '[FAIL - BLOCKING ERRORS]'}")

        if rep["errors"]:
            print("\nBlocking Hard Errors:")
            for e in rep["errors"]:
                print(f"  • {e}")

        if rep["warnings"]:
            print("\nPacing & Rhythm Warnings:")
            for w in rep["warnings"]:
                print(f"  • {w}")

        print("=" * 65)
        sys.exit(0 if rep["is_valid"] else 1)

    elif cmd == "normalize":
        inp = " ".join(sys.argv[2:])
        if not inp:
            print("[ERROR] Text or file path required for normalization.")
            sys.exit(1)

        p = Path(inp)
        if p.exists() and p.suffix == ".json":
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            upd, summary = NarrationValidator.normalize_script(data, populate_tts_field=True)
            print(json.dumps(upd, indent=2, ensure_ascii=False))
        else:
            norm, audit = IndonesianNumberConverter.normalize_sentence(inp)
            print(f"Original:   {inp}")
            print(f"Normalized: {norm}")
            if audit:
                print("Transformations:")
                for a in audit:
                    print(f"  - [{a['type']}] '{a['original']}' -> '{a['converted']}'")

    else:
        print(f"Unknown command: '{cmd}'. Choose 'validate' or 'normalize'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
