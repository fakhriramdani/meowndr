#!/usr/bin/env python3
"""
Demonstration script for Papercraft Content Factory.
Generates structured sample configurations and artifacts for two distinct niches:
1. History: 'history-borobudur-stones' ("Rahasia Interlocking Candi Borobudur")
2. Mystery: 'mystery-sailing-stones' ("Misteri Batu Berjalan Death Valley")
Validates all produced artifacts against JSON schemas.
"""

import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

from workflow_engine import WorkflowEngine
from schema_validator import validate_artifact_file


def build_history_sample():
    slug = "history-borobudur-stones"
    topic = "Rahasia Interlocking Candi Borobudur"
    print(f"\n=======================================================")
    print(f">> Building Sample Niche 1: HISTORY ({slug})")
    print(f"=======================================================")

    engine = WorkflowEngine(slug, niche="history", title=topic, on_demand_trends=True)

    # Stage 1: Trend Research (On-demand)
    print("• Stage 1: Trend Research...")
    engine.run_stage_1_trend_research()

    # Stage 2: Fact Research
    print("• Stage 2: Fact Research & Verification...")
    claims = [
        {
            "claim_id": "c1_date_dynasty",
            "statement": "Borobudur dibangun sekitar tahun 750-825 Masehi pada masa pemerintahan Wangsa Syailendra.",
            "explanation": "Catatan prasasti dan analisis gaya arsitektur mengonfirmasi pembangunan era Syailendra di Jawa Tengah.",
            "sources": [
                {"title": "Borobudur Temple Compounds", "url": "https://whc.unesco.org/en/list/592", "publisher": "UNESCO"},
                {"title": "Katalog Sejarah Candi Borobudur", "url": "https://kebudayaan.kemdikbud.go.id/bpcbyogyakarta", "publisher": "Kemendikbudristek RI"}
            ]
        },
        {
            "claim_id": "c2_interlocking_stone",
            "statement": "Struktur 2 juta blok batu andesit disusun tanpa semen, menggunakan sistem sambungan batu interlocking (takikan purus dan ekor burung).",
            "explanation": "Sistem sambungan batu takik kunci memungkinkan struktur fleksibel meredam getaran gempa bumi.",
            "sources": [
                {"title": "Kajian Arsitektur & Rekayasa Gempa Candi Borobudur", "url": "https://konservasiborobudur.kemdikbud.go.id/arsitektur", "publisher": "Balai Konservasi Borobudur"}
            ]
        },
        {
            "claim_id": "c3_volcanic_drainage",
            "statement": "Sistem drainase kuno Borobudur menyalurkan air hujan melalui mulut makara berongga untuk mencegah pelapukan batu.",
            "explanation": "Terdapat 100 pancuran makara yang berfungsi sebagai saluran air hujan tersembunyi.",
            "sources": [
                {"title": "Water Drainage System of Borobudur", "url": "https://whc.unesco.org/en/list/592/documents", "publisher": "UNESCO Conservation Archive"}
            ]
        }
    ]
    engine.run_stage_2_fact_research(topic, claims)

    # Stage 3: Hook Generation
    print("• Stage 3: Hook Generation & Scoring...")
    variants = [
        {
            "id": "v1_paradox",
            "archetype": "paradox",
            "hook_text": "Candi raksasa dua juta batu ini berdiri seribu tahun tanpa semen sama sekali!",
            "cover_lines": [["CANDI", "RAKSASA"], ["TANPA", "SEMEN?"]],
            "hot_words": ["TANPA", "SEMEN?"],
            "curiosity_score": 9.6,
            "clarity_score": 9.2,
            "visual_score": 9.4,
            "composite_score": 9.4
        },
        {
            "id": "v2_high_stakes",
            "archetype": "high_stakes",
            "hook_text": "Bagaimana arsitek kuno Jawa mendesain bangunan tahan gempa seribu tahun lalu?",
            "cover_lines": [["RAHASIA", "KUNO"], ["TAHAN", "GEMPA?"]],
            "hot_words": ["TAHAN", "GEMPA?"],
            "curiosity_score": 8.9,
            "clarity_score": 8.7,
            "visual_score": 8.8,
            "composite_score": 8.8
        },
        {
            "id": "v3_direct_challenge",
            "archetype": "direct_challenge",
            "hook_text": "Rahasia sistem kuncian batu Borobudur yang membuat arsitek dunia terheran-heran.",
            "cover_lines": [["KUNCIAN", "BATU"], ["MISTERI", "BOROBUDUR"]],
            "hot_words": ["KUNCIAN"],
            "curiosity_score": 8.5,
            "clarity_score": 8.4,
            "visual_score": 8.6,
            "composite_score": 8.5
        }
    ]
    engine.run_stage_3_hook_generation(
        topic, variants, "v1_paradox",
        "Cat Historian pulls a glowing papercut interlocking stone puzzle apart and snaps it together."
    )

    # Stage 4: Gate 1 Approval
    print("• Stage 4: Gate 1 Approval (Topic & Hook)...")
    engine.run_stage_4_gate_1_approval(approved_by="Editorial Lead", selected_hook_id="v1_paradox", notes="Excellent curiosity gap and strong historical grounding.")

    # Stage 5: Scriptwriting
    print("• Stage 5: Scriptwriting...")
    script_lines = [
        {
            "id": "l1_hook",
            "text": "Pernahkah kamu penasaran bagaimana Candi Borobudur bisa berdiri kokoh lebih dari seribu tahun padahal dibangun sama sekali tanpa semen perekat?",
            "target_seconds": 12,
            "claim_ref": "c1_date_dynasty"
        },
        {
            "id": "l2_concept",
            "text": "Rahasia besarnya ada pada kecerdasan Wangsa Syailendra yang menyusun lebih dari dua juta balok batu andesit vulkanik seperti permainan puzzle raksasa.",
            "target_seconds": 13,
            "claim_ref": "c2_interlocking_stone"
        },
        {
            "id": "l3_mechanism",
            "text": "Setiap batu dipahat dengan sambungan takik khusus bernama ekor burung sehingga ketika gempa mengguncang bebatuan ini saling mengunci bukan roboh.",
            "target_seconds": 14,
            "claim_ref": "c2_interlocking_stone"
        },
        {
            "id": "l4_drainage",
            "text": "Bahkan air hujan dibuang otomatis lewat seratus patung makara berongga agar batu tidak cepat lapuk oleh lumut tropis.",
            "target_seconds": 11,
            "claim_ref": "c3_volcanic_drainage"
        },
        {
            "id": "l5_outro",
            "text": "Kecerdasan nusantara kuno terbukti melampaui zamannya. Bagikan kisah hebat ini dan ikuti kami untuk rahasia sejarah berikutnya!",
            "target_seconds": 10,
            "claim_ref": "c1_date_dynasty"
        }
    ]
    engine.run_stage_5_scriptwriting(script_lines)

    # Stage 6: Gate 2 Approval
    print("• Stage 6: Gate 2 Approval (Script)...")
    engine.run_stage_6_gate_2_approval(approved_by="Historical Editor", notes="Dialogue verified against conservation records; natural spoken pace.")

    # Stage 7: Storyboarding
    print("• Stage 7: Storyboarding & Scene Timing...")
    scenes = [
        {
            "id": "S01Hook",
            "script_line_id": "l1_hook",
            "durationInFrames": 360,
            "banner_text": "RAHASIA BATU KUNO TANPA SEMEN",
            "transition_cut": "pageTurn",
            "camera": {"yaw": 6, "push": 1.06},
            "presenter": {"state": "curious", "pointAngle": -20}
        },
        {
            "id": "S02Concept",
            "script_line_id": "l2_concept",
            "durationInFrames": 390,
            "banner_text": "DUA JUTA BALOK ANDESIT VULKANIK",
            "transition_cut": "tearAway",
            "camera": {"yaw": -6, "push": 1.08},
            "presenter": {"state": "explaining", "pointAngle": -30}
        },
        {
            "id": "S03Interlocking",
            "script_line_id": "l3_mechanism",
            "durationInFrames": 420,
            "banner_text": "SISTEM TAKIKAN PEREDAM GEMPA",
            "transition_cut": "zoomThrough",
            "camera": {"yaw": 5, "push": 1.10},
            "presenter": {"state": "pointing", "pointAngle": -35}
        },
        {
            "id": "S04Drainage",
            "script_line_id": "l4_drainage",
            "durationInFrames": 330,
            "banner_text": "DRAINASE KUNO MAKARA BERONGGA",
            "transition_cut": "stampCut",
            "camera": {"yaw": -5, "push": 1.06},
            "presenter": {"state": "thinking", "pointAngle": -20}
        },
        {
            "id": "S05Outro",
            "script_line_id": "l5_outro",
            "durationInFrames": 300,
            "banner_text": "IKUTI KISAH SEJARAH BERIKUTNYA",
            "transition_cut": "popUpBook",
            "camera": {"yaw": 4, "push": 1.05},
            "presenter": {"state": "waving", "pointAngle": 0}
        }
    ]
    engine.run_stage_7_storyboarding(scenes, env_id="botany-greenhouse")

    # Stage 8: Asset Planning
    print("• Stage 8: Asset Planning...")
    engine.run_stage_8_asset_planning(env_id="botany-greenhouse")

    # Stage 9: Audio Planning
    print("• Stage 9: Audio Planning...")
    engine.run_stage_9_audio_production(is_placeholder=True)

    # Stage 11: QA Audit
    print("• Stage 11: 4-Dimensional QA Audit...")
    engine.run_stage_11_qa_audit()

    # Stage 12: Gate 3 Approval
    print("• Stage 12: Gate 3 Approval (Final Video Sign-Off)...")
    engine.run_stage_12_gate_3_approval(approved_by="Executive Producer", notes="Release approved for History niche.")

    print(f">> Sample 1 (History) Complete! Final Status: {engine.state['status']}")
    return slug


def build_mystery_sample():
    slug = "mystery-sailing-stones"
    topic = "Misteri Batu Berjalan Racetrack Playa"
    print(f"\n=======================================================")
    print(f">> Building Sample Niche 2: EVIDENCE-BASED MYSTERY ({slug})")
    print(f"=======================================================")

    engine = WorkflowEngine(slug, niche="mystery", title=topic, on_demand_trends=False)

    # Stage 2: Fact Research
    print("• Stage 2: Fact Research & Verification...")
    claims = [
        {
            "claim_id": "c1_death_valley_phenomenon",
            "statement": "Di dasar danau kering Racetrack Playa (Death Valley), bebatuan seberat ratusan kilogram berpindah sendiri meninggalkan jejak panjang di lumpur.",
            "explanation": "Fenomena ini membingungkan para peneliti selama hampir satu abad sejak dekade 1940-an.",
            "sources": [
                {"title": "The Mystery of Death Valley's Moving Rocks Solved", "url": "https://scripps.ucsd.edu/news/mystery-death-valleys-moving-rocks-solved", "publisher": "Scripps Institution of Oceanography"},
                {"title": "Death Valley Sailing Stones", "url": "https://earthobservatory.nasa.gov/images/84377", "publisher": "NASA Earth Observatory"}
            ]
        },
        {
            "claim_id": "c2_ice_wind_mechanism",
            "statement": "Pada 2014, tim peneliti membuktikan batu bergerak akibat kombinasi lapisan es jendela setipis beberapa milimeter dan hembusan angin sepoi-sepoi.",
            "explanation": "Lapisan es transparan tipis mengapungkan batu sedikit di atas lumpur licin, sehingga dorongan angin ringan mampu menggesernya perlahan.",
            "sources": [
                {"title": "Sliding Rocks on Racetrack Playa, Death Valley National Park: First Observation of Rocks in Motion", "url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0105948", "publisher": "PLOS ONE Research"}
            ]
        }
    ]
    engine.run_stage_2_fact_research(topic, claims)

    # Stage 3: Hook Generation
    print("• Stage 3: Hook Generation & Scoring...")
    variants = [
        {
            "id": "v1_sensory_mystery",
            "archetype": "sensory_mystery",
            "hook_text": "Batu seberat ratusan kilo ini berjalan sendiri di gurun tanpa disentuh siapa pun!",
            "cover_lines": [["BATU", "BERJALAN"], ["SENDIRI?"]],
            "hot_words": ["BATU", "BERJALAN"],
            "curiosity_score": 9.7,
            "clarity_score": 9.4,
            "visual_score": 9.5,
            "composite_score": 9.5
        },
        {
            "id": "v2_counter_intuitive",
            "archetype": "counter_intuitive",
            "hook_text": "Kamu kira ini fenomena gaib? Sains membuktikan pelakunya lapisan es setipis kaca!",
            "cover_lines": [["BUKAN", "GAIB"], ["PELAKUNYA", "ES?"]],
            "hot_words": ["PELAKUNYA", "ES?"],
            "curiosity_score": 9.1,
            "clarity_score": 9.0,
            "visual_score": 9.1,
            "composite_score": 9.1
        },
        {
            "id": "v3_direct_challenge",
            "archetype": "direct_challenge",
            "hook_text": "Misteri satu abad terpecahkan: bagaimana batu gurun bisa meninggalkan jejak ratusan meter?",
            "cover_lines": [["MISTERI", "ABAD"], ["JEJAK", "GURUN"]],
            "hot_words": ["MISTERI"],
            "curiosity_score": 8.7,
            "clarity_score": 8.5,
            "visual_score": 8.8,
            "composite_score": 8.7
        }
    ]
    engine.run_stage_3_hook_generation(
        topic, variants, "v1_sensory_mystery",
        "Cat Detective illuminates a sliding desert boulder leaving a long textured trail on cracked earth."
    )

    # Stage 4: Gate 1 Approval
    print("• Stage 4: Gate 1 Approval (Topic & Hook)...")
    engine.run_stage_4_gate_1_approval(approved_by="Editorial Lead", selected_hook_id="v1_sensory_mystery", notes="Incredible mystery payoff with peer-reviewed scientific resolution.")

    # Stage 5: Scriptwriting
    print("• Stage 5: Scriptwriting...")
    script_lines = [
        {
            "id": "l1_hook",
            "text": "Bayangkan batu seberat ratusan kilogram yang tiba-tiba berpindah tempat di tengah gurun gersang meninggalkan jejak panjang misterius di atas tanah.",
            "target_seconds": 12,
            "claim_ref": "c1_death_valley_phenomenon"
        },
        {
            "id": "l2_concept",
            "text": "Selama hampir satu abad fenomena batu berlayar di Death Valley ini dianggap misteri gaib atau kekuatan magnet bumi yang tak kasat mata.",
            "target_seconds": 13,
            "claim_ref": "c1_death_valley_phenomenon"
        },
        {
            "id": "l3_mechanism",
            "text": "Namun pada tahun 2014 kamera peneliti menangkap rahasianya: saat malam dingin genangan air membeku menjadi lempengan es tipis seperti jendela kaca.",
            "target_seconds": 14,
            "claim_ref": "c2_ice_wind_mechanism"
        },
        {
            "id": "l4_explanation",
            "text": "Ketika matahari terbit es mencair dan hembusan angin sepoi-sepoi mendorong lempeng es menggeser batu besar itu dengan sangat mulus di atas lumpur.",
            "target_seconds": 13,
            "claim_ref": "c2_ice_wind_mechanism"
        },
        {
            "id": "l5_outro",
            "text": "Terkadang misteri paling rumit di dunia punya penjelasan sains yang sangat indah. Suka misteri sains nyata? Ikuti kami untuk fakta berikutnya!",
            "target_seconds": 11,
            "claim_ref": "c2_ice_wind_mechanism"
        }
    ]
    engine.run_stage_5_scriptwriting(script_lines)

    # Stage 6: Gate 2 Approval
    print("• Stage 6: Gate 2 Approval (Script)...")
    engine.run_stage_6_gate_2_approval(approved_by="Science Editor", notes="PLOS ONE 2014 study accurately explained in conversational Indonesian.")

    # Stage 7: Storyboarding
    print("• Stage 7: Storyboarding & Scene Timing...")
    scenes = [
        {
            "id": "S01Hook",
            "script_line_id": "l1_hook",
            "durationInFrames": 360,
            "banner_text": "MISTERI BATU BERGERAK SENDIRI",
            "transition_cut": "pageTurn",
            "camera": {"yaw": 6, "push": 1.07},
            "presenter": {"state": "curious", "pointAngle": -20}
        },
        {
            "id": "S02MysteryHistory",
            "script_line_id": "l2_concept",
            "durationInFrames": 390,
            "banner_text": "SATU ABAD TEKA-TEKI GURUN",
            "transition_cut": "tearAway",
            "camera": {"yaw": -6, "push": 1.08},
            "presenter": {"state": "thinking", "pointAngle": -25}
        },
        {
            "id": "S03IceLattice",
            "script_line_id": "l3_mechanism",
            "durationInFrames": 420,
            "banner_text": "LEMPENGAN ES TIPIS JENDELA",
            "transition_cut": "zoomThrough",
            "camera": {"yaw": 5, "push": 1.10},
            "presenter": {"state": "explaining", "pointAngle": -30}
        },
        {
            "id": "S04WindPush",
            "script_line_id": "l4_explanation",
            "durationInFrames": 390,
            "banner_text": "DORONGAN ANGIN DI ATAS LUMPUR",
            "transition_cut": "stampCut",
            "camera": {"yaw": -5, "push": 1.06},
            "presenter": {"state": "pointing", "pointAngle": -35}
        },
        {
            "id": "S05Outro",
            "script_line_id": "l5_outro",
            "durationInFrames": 330,
            "banner_text": "SAINS DI BALIK MISTERI DUNIA",
            "transition_cut": "popUpBook",
            "camera": {"yaw": 4, "push": 1.05},
            "presenter": {"state": "waving", "pointAngle": 0}
        }
    ]
    engine.run_stage_7_storyboarding(scenes, env_id="physics-lab")

    # Stage 8: Asset Planning
    print("• Stage 8: Asset Planning...")
    engine.run_stage_8_asset_planning(env_id="physics-lab")

    # Stage 9: Audio Planning
    print("• Stage 9: Audio Planning...")
    engine.run_stage_9_audio_production(is_placeholder=True)

    # Stage 11: QA Audit
    print("• Stage 11: 4-Dimensional QA Audit...")
    engine.run_stage_11_qa_audit()

    # Stage 12: Gate 3 Approval
    print("• Stage 12: Gate 3 Approval (Final Video Sign-Off)...")
    engine.run_stage_12_gate_3_approval(approved_by="Executive Producer", notes="Release approved for Mystery niche.")

    print(f">> Sample 2 (Mystery) Complete! Final Status: {engine.state['status']}")
    return slug


def validate_all_sample_artifacts(slug: str):
    print(f"\n--- Validating Artifact Schemas for '{slug}' ---")
    ep_dir = os.path.join(REPO_ROOT, "episodes", slug)
    state_file = os.path.join(ep_dir, "content_factory", "workflow_state.json")
    with open(state_file) as f:
        state = json.load(f)

    type_map = {
        "dossier": "dossier",
        "hook_matrix": "hook_matrix",
        "script": "script",
        "storyboard": "storyboard",
        "asset_plan": "asset_plan",
        "audio_plan": "audio_plan",
        "qa_report": "qa_report"
    }

    errors = 0
    for key, rel_path in state.get("artifacts", {}).items():
        art_type = type_map.get(key)
        if not art_type:
            continue
        full_path = os.path.join(REPO_ROOT, rel_path)
        valid, errs = validate_artifact_file(art_type, full_path)
        if valid:
            print(f"  [PASS] {key} -> {rel_path}")
        else:
            print(f"  [FAIL] {key} -> {rel_path}: {errs}")
            errors += 1

    return errors == 0


def main():
    s1 = build_history_sample()
    v1 = validate_all_sample_artifacts(s1)

    s2 = build_mystery_sample()
    v2 = validate_all_sample_artifacts(s2)

    print("\n" + "=" * 65)
    if v1 and v2:
        print(">> DEMONSTRATION SUCCEEDED: All multi-niche samples passed schema validation!")
    else:
        print(">> DEMONSTRATION FAILED: Validation errors detected.")
        sys.exit(1)
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
