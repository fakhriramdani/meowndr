#!/usr/bin/env python3
"""
Unit and regression tests for the Indonesian Narration Number & Punctuation Standard (@meowndr).
Verifies:
1. Integer conversion (0, 1..19, tens, hundreds, thousands, millions, billions, trillions)
2. Years (1883, 1945, 2014, 2026, 2000)
3. Decimals (Indonesian 'koma' format and international format)
4. Percentages ('persen', '%')
5. Measurements (distance, temperature, speed, mass, time, pressure, energy, frequency, sound)
6. Currency (Rupiah, Dollar, Euro)
7. Fractions (1/2, 1/3, 1/4, 2/3, 3/4, 2/5)
8. Scientific notation (exponents, powers of 10, chemical formulas CO2, H2O)
9. Context-sensitive conversions (1,5 km vs 1.500 m, pH 7, CO2)
10. Speech-rhythm punctuation (commas, periods, question marks, colons, em dashes, ellipses)
11. Script schema compatibility (array and object format, with 'tts' and 'raw_text')
12. ElevenLabs input consistency (digit-free, punctuation preserved, whitespace collapsed)
13. Episode regression validation across existing episode scripts.
"""

import os
import sys
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.narration_standard import (
    IndonesianNumberConverter,
    PunctuationStandard,
    NarrationValidator,
    UNITS_MAP,
)
from library.voice.tts.base import TTSRequest
from library.voice.tts.placeholder_provider import PlaceholderProvider
from library.content_factory.schema_validator import validate_artifact


class TestIndonesianIntegerConversion(unittest.TestCase):
    """1. Integer conversion tests."""

    def test_single_digits(self):
        cases = [
            (0, "nol"),
            (1, "satu"),
            (2, "dua"),
            (3, "tiga"),
            (4, "empat"),
            (5, "lima"),
            (6, "enam"),
            (7, "tujuh"),
            (8, "delapan"),
            (9, "sembilan"),
        ]
        for val, expected in cases:
            self.assertEqual(IndonesianNumberConverter.int_to_words(val), expected)

    def test_teens(self):
        cases = [
            (10, "sepuluh"),
            (11, "sebelas"),
            (12, "dua belas"),
            (13, "tiga belas"),
            (15, "lima belas"),
            (19, "sembilan belas"),
        ]
        for val, expected in cases:
            self.assertEqual(IndonesianNumberConverter.int_to_words(val), expected)

    def test_tens_and_hundreds(self):
        cases = [
            (20, "dua puluh"),
            (21, "dua puluh satu"),
            (30, "tiga puluh"),
            (99, "sembilan puluh sembilan"),
            (100, "seratus"),
            (105, "seratus lima"),
            (111, "seratus sebelas"),
            (150, "seratus lima puluh"),
            (200, "dua ratus"),
            (555, "lima ratus lima puluh lima"),
            (999, "sembilan ratus sembilan puluh sembilan"),
        ]
        for val, expected in cases:
            self.assertEqual(IndonesianNumberConverter.int_to_words(val), expected)

    def test_thousands_and_above(self):
        cases = [
            (1000, "seribu"),
            (1001, "seribu satu"),
            (1500, "seribu lima ratus"),
            (1883, "seribu delapan ratus delapan puluh tiga"),
            (2000, "dua ribu"),
            (10000, "sepuluh ribu"),
            (100000, "seratus ribu"),
            (1000000, "satu juta"),
            (5000000, "lima juta"),
            (1000000000, "satu miliar"),
            (1000000000000, "satu triliun"),
        ]
        for val, expected in cases:
            self.assertEqual(IndonesianNumberConverter.int_to_words(val), expected)

    def test_negative_numbers(self):
        self.assertEqual(IndonesianNumberConverter.int_to_words(-5), "minus lima")
        self.assertEqual(IndonesianNumberConverter.int_to_words(-20), "minus dua puluh")


class TestYearsConversion(unittest.TestCase):
    """2. Historical and modern calendar years conversion."""

    def test_years(self):
        cases = [
            ("1883", "seribu delapan ratus delapan puluh tiga"),
            ("1945", "seribu sembilan ratus empat puluh lima"),
            ("2000", "dua ribu"),
            ("2014", "dua ribu empat belas"),
            ("2024", "dua ribu dua puluh empat"),
            ("2026", "dua ribu dua puluh enam"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(f"Tahun {val}")
            self.assertEqual(norm, f"Tahun {expected}")


class TestDecimalsAndFractions(unittest.TestCase):
    """3. Decimal and fraction conversion tests."""

    def test_decimals(self):
        cases = [
            ("2,5", "dua koma lima"),
            ("0,5", "nol koma lima"),
            ("0,01", "nol koma nol satu"),
            ("3,14", "tiga koma satu empat"),
            ("1.5", "satu koma lima"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(val)
            self.assertEqual(norm, expected)

    def test_fractions(self):
        cases = [
            ("1/2", "setengah"),
            ("1/3", "sepertiga"),
            ("1/4", "seperempat"),
            ("2/3", "dua pertiga"),
            ("3/4", "tiga perempat"),
            ("2/5", "dua per lima"),
            ("1/10", "sepersepuluh"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(f"Porsinya {val} bagian.")
            self.assertEqual(norm, f"Porsinya {expected} bagian.")


class TestPercentagesAndCurrency(unittest.TestCase):
    """4. Percentage and currency conversion tests."""

    def test_percentages(self):
        cases = [
            ("2,5 persen", "dua koma lima persen"),
            ("2,5%", "dua koma lima persen"),
            ("100%", "seratus persen"),
            ("9 persen", "sembilan persen"),
            ("0,1%", "nol koma satu persen"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(val)
            self.assertEqual(norm, expected)

    def test_currency(self):
        cases = [
            ("Rp50.000", "lima puluh ribu rupiah"),
            ("Rp 50.000", "lima puluh ribu rupiah"),
            ("Rp. 100.000", "seratus ribu rupiah"),
            ("$10", "sepuluh dolar"),
            ("€5", "lima euro"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(val)
            self.assertEqual(norm, expected)


class TestMeasurementsAndUnits(unittest.TestCase):
    """5. Physical measurements and scientific units."""

    def test_distance(self):
        cases = [
            ("12 km", "dua belas kilometer"),
            ("1.500 meter", "seribu lima ratus meter"),
            ("1,5 kilometer", "satu koma lima kilometer"),
            ("10 cm", "sepuluh sentimeter"),
            ("5 mm", "lima milimeter"),
            ("100 nm", "seratus nanometer"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(val)
            self.assertEqual(norm, expected)

    def test_temperature(self):
        cases = [
            ("100°C", "seratus derajat Celsius"),
            ("100 °C", "seratus derajat Celsius"),
            ("32°F", "tiga puluh dua derajat Fahrenheit"),
            ("300 K", "tiga ratus Kelvin"),
            ("0°C", "nol derajat Celsius"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(val)
            self.assertEqual(norm, expected)

    def test_time_and_speed(self):
        cases = [
            ("30 detik", "tiga puluh detik"),
            ("15 menit", "lima belas menit"),
            ("2 jam", "dua jam"),
            ("100 km/jam", "seratus kilometer per jam"),
            ("30 m/s", "tiga puluh meter per detik"),
            ("300.000 km/s", "tiga ratus ribu kilometer per detik"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(val)
            self.assertEqual(norm, expected)

    def test_mass_and_energy(self):
        cases = [
            ("5 kg", "lima kilogram"),
            ("500 gram", "lima ratus gram"),
            ("10 mg", "sepuluh miligram"),
            ("2 ton", "dua ton"),
            ("100 V", "seratus Volt"),
            ("50 W", "lima puluh Watt"),
            ("10 kW", "sepuluh kilowatt"),
            ("100 J", "seratus Joule"),
            ("1000 Pa", "seribu Pascal"),
            ("1 atm", "satu atmosfer"),
            ("60 Hz", "enam puluh Hertz"),
            ("2,4 GHz", "dua koma empat gigahertz"),
            ("80 dB", "delapan puluh desibel"),
            ("3 kali", "tiga kali"),
            ("3x", "tiga kali"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(val)
            self.assertEqual(norm, expected)


class TestScientificNotationAndFormulas(unittest.TestCase):
    """6. Scientific powers, exponents, chemical formulas."""

    def test_scientific_notation(self):
        cases = [
            ("3 x 10^8 m/s", "tiga kali sepuluh pangkat delapan meter per detik"),
            ("3 × 10⁸ m/s", "tiga kali sepuluh pangkat delapan meter per detik"),
            ("10^6", "sepuluh pangkat enam"),
            ("10^-3", "sepuluh pangkat minus tiga"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(val)
            self.assertEqual(norm, expected)

    def test_chemical_formulas(self):
        cases = [
            ("CO₂", "CO dua"),
            ("CO2", "CO dua"),
            ("H₂O", "H dua O"),
            ("H2O", "H dua O"),
            ("O₂", "O dua"),
            ("O2", "O dua"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(f"Molekul {val}")
            self.assertEqual(norm, f"Molekul {expected}")

    def test_ph_values(self):
        cases = [
            ("pH 7", "pH tujuh"),
            ("pH 2,5", "pH dua koma lima"),
            ("pH 2.5", "pH dua koma lima"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(val)
            self.assertEqual(norm, expected)


class TestContextSensitiveNumberConversion(unittest.TestCase):
    """7. Context-sensitive distinction: 1,5 km vs 1.500 m, ordinals, centuries."""

    def test_thousand_separator_vs_decimal(self):
        # Indonesian thousand separator: 1.500 meter -> 1500 -> seribu lima ratus meter
        norm1, _ = IndonesianNumberConverter.normalize_sentence("Jaraknya 1.500 meter.")
        self.assertEqual(norm1, "Jaraknya seribu lima ratus meter.")

        # Decimal: 1,5 kilometer -> satu koma lima kilometer
        norm2, _ = IndonesianNumberConverter.normalize_sentence("Jaraknya 1,5 kilometer.")
        self.assertEqual(norm2, "Jaraknya satu koma lima kilometer.")

    def test_ordinals_and_centuries(self):
        cases = [
            ("ke-3", "ketiga"),
            ("ke-21", "kedua puluh satu"),
            ("abad ke-21", "abad kedua puluh satu"),
            ("21st century", "abad kedua puluh satu"),
            ("abad 21", "abad kedua puluh satu"),
        ]
        for val, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(val)
            self.assertEqual(norm, expected)


class TestSpeechRhythmPunctuation(unittest.TestCase):
    """8. Punctuation cleaning, rhythm, and validation."""

    def test_clean_punctuation(self):
        cases = [
            ("Halo,, teman-teman!!", "Halo, teman-teman!"),
            ("Tunggu...... apa itu???", "Tunggu... apa itu?"),
            ("Kecepatan mencapai 100 km/jam--sangat cepat!", "Kecepatan mencapai seratus kilometer per jam — sangat cepat!"),
            ("Satu , dua , dan tiga .", "Satu, dua, dan tiga."),
        ]
        for inp, expected in cases:
            norm, _ = IndonesianNumberConverter.normalize_sentence(inp)
            self.assertEqual(norm, expected)

    def test_validate_punctuation_warnings(self):
        warnings = PunctuationStandard.validate_punctuation("Teks tanpa titik di akhir")
        self.assertTrue(any("Missing terminal" in w for w in warnings))

        warnings_rep = PunctuationStandard.validate_punctuation("Keren banget kan???!!")
        self.assertTrue(any("Excessive repeated" in w for w in warnings_rep))

        warnings_ell = PunctuationStandard.validate_punctuation("Satu... dua... tiga... empat...")
        self.assertTrue(any("Multiple ellipses" in w for w in warnings_ell))


class TestNarrationValidator(unittest.TestCase):
    """9. NarrationValidator tests for hard errors, warnings, and compliance."""

    def test_hard_error_on_digits(self):
        line = {"id": "l1", "text": "Suhu mencapai 100°C di tahun 1883."}
        rep = NarrationValidator.validate_line(line)
        self.assertFalse(rep["is_valid"])
        self.assertTrue(len(rep["errors"]) > 0)
        self.assertTrue(any("numeric digits" in e for e in rep["errors"]))

    def test_pass_on_normalized_text(self):
        line = {
            "id": "l1",
            "text": "Suhu mencapai seratus derajat Celsius pada tahun seribu delapan ratus delapan puluh tiga."
        }
        rep = NarrationValidator.validate_line(line)
        self.assertTrue(rep["is_valid"])
        self.assertEqual(len(rep["errors"]), 0)

    def test_support_tts_field(self):
        # When 'text' has digits for display but 'tts' has normalized Indonesian words
        line = {
            "id": "l1",
            "text": "Suhu mencapai 100°C di tahun 1883.",
            "tts": "Suhu mencapai seratus derajat Celsius di tahun seribu delapan ratus delapan puluh tiga."
        }
        rep = NarrationValidator.validate_line(line)
        self.assertTrue(rep["is_valid"])
        self.assertEqual(len(rep["errors"]), 0)

    def test_normalize_script_preserves_traceability(self):
        raw_script = [
            {"id": "l1", "text": "Pada kedalaman 12 km, suhu mencapai 100°C."},
            {"id": "l2", "text": "Volume air mengembang 9% saat membeku."},
            {"id": "l3", "text": "Keren kan? Ikuti kami untuk fakta sains seru berikutnya!"}
        ]
        upd, summary = NarrationValidator.normalize_script(raw_script, populate_tts_field=True)
        self.assertEqual(len(upd), 3)
        # Original 'text' preserved
        self.assertEqual(upd[0]["text"], "Pada kedalaman 12 km, suhu mencapai 100°C.")
        # 'tts' normalized
        self.assertEqual(upd[0]["tts"], "Pada kedalaman dua belas kilometer, suhu mencapai seratus derajat Celsius.")
        self.assertEqual(upd[1]["tts"], "Volume air mengembang sembilan persen saat membeku.")
        # Audit details captured
        self.assertEqual(summary["transformed_lines"], 2)
        # Final validation passes
        self.assertTrue(summary["validation"]["is_valid"])


class TestScriptSchemaCompatibility(unittest.TestCase):
    """10. Formal JSON Schema validation for script artifacts."""

    def test_array_format_with_tts_and_metadata(self):
        script_array = [
            {
                "id": "l1_hook",
                "text": "Suhu mencapai 100°C.",
                "tts": "Suhu mencapai seratus derajat Celsius.",
                "raw_text": "Suhu mencapai 100°C.",
                "speaker": "cat_scientist",
                "target_seconds": 6.0,
                "claim_ref": "c1",
                "validation_status": "NORMALIZED"
            },
            {
                "id": "l2_concept",
                "text": "Normalnya molekul bergerak lebih lambat.",
                "target_seconds": 7.0
            },
            {
                "id": "l3_outro",
                "text": "Keren kan? Ikuti kami!",
                "target_seconds": 5.0
            }
        ]
        valid, errs = validate_artifact("script", script_array)
        self.assertTrue(valid, f"Schema validation failed: {errs}")

    def test_object_format_with_lines(self):
        script_obj = {
            "language": "id",
            "total_word_count": 140,
            "estimated_duration_sec": 51.0,
            "normalization_status": "COMPLIANT",
            "lines": [
                {"id": "l1", "text": "Baris pertama narasi."},
                {"id": "l2", "text": "Baris kedua penjelasan sains."},
                {"id": "l3", "text": "Baris ketiga penutup video."}
            ]
        }
        valid, errs = validate_artifact("script", script_obj)
        self.assertTrue(valid, f"Schema validation failed: {errs}")


class TestElevenLabsInputConsistency(unittest.TestCase):
    """11. TTS request normalization and punctuation preservation."""

    def test_tts_request_preserves_speech_punctuation(self):
        text = "Ternyata, suhunya mencapai seratus derajat Celsius — luar biasa!"
        req = TTSRequest(text=text, line_id="l1")
        norm = req.normalized_text()

        # Ensure commas and em dashes are preserved
        self.assertIn(",", norm)
        self.assertIn("—", norm)
        self.assertNotIn("100", norm)
        # Ensure whitespace is clean
        self.assertEqual(norm, "Ternyata, suhunya mencapai seratus derajat Celsius — luar biasa!")

    def test_placeholder_tts_synthesizes_normalized_words(self):
        provider = PlaceholderProvider(wps=2.75)
        text = "Suhu seratus derajat Celsius pada kedalaman dua belas kilometer."
        req = TTSRequest(text=text, line_id="l1")
        resp = provider.synthesize(req)

        self.assertGreater(resp.duration_sec, 2.0)
        self.assertEqual(len(resp.words), len(text.split()))
        words_text = [w.word for w in resp.words]
        self.assertIn("seratus", words_text)
        self.assertIn("Celsius", words_text)
        self.assertIn("kilometer.", words_text)


class TestExistingEpisodesValidation(unittest.TestCase):
    """12. Validates existing repository episode scripts against narration standard."""

    def test_canonical_episode_01(self):
        ep_path = REPO_ROOT / "episodes" / "01-anomali-air" / "narration" / "script.json"
        if ep_path.exists():
            with open(ep_path, "r", encoding="utf-8") as f:
                script = json.load(f)
            rep = NarrationValidator.validate_script(script)
            self.assertTrue(rep["is_valid"], f"01-anomali-air failed narration standard: {rep['errors']}")
            self.assertEqual(len(rep["errors"]), 0)

    def test_canonical_episode_05(self):
        ep_path = REPO_ROOT / "episodes" / "05-bintang-berkelip" / "narration" / "script.json"
        if ep_path.exists():
            with open(ep_path, "r", encoding="utf-8") as f:
                script = json.load(f)
            rep = NarrationValidator.validate_script(script)
            self.assertTrue(rep["is_valid"], f"05-bintang-berkelip failed narration standard: {rep['errors']}")
            self.assertEqual(len(rep["errors"]), 0)


if __name__ == "__main__":
    unittest.main()
