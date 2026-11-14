#!/usr/bin/env python3
"""Bespoke Animated Papercraft Scene Generator for @meowndr episodes.

Generates 6 Remotion TSX scene components (S01Hook .. S06Outro) with animated
SVG papercraft physical models/instruments tailored to the episode's script beats,
Cat Scientist movement/interaction/lip-sync, and camera orbit/push effects, then
verifies compilation with `npx tsc --noEmit`.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCENE_SLOTS: List[Tuple[str, str, str, str]] = [
    ("S01Hook", "beat_1", "curious", "science-laboratory"),
    ("S02Shockwave", "beat_2", "surprised", "science-laboratory"),
    ("S03Domino", "beat_3", "explaining", "science-laboratory"),
    ("S04ModernReset", "beat_4", "aha", "city-park"),
    ("S05RealityAnchor", "beat_5", "explaining", "science-laboratory"),
    ("S06Outro", "beat_6", "curious", "cozy-bedroom"),
]

VALID_ENVIRONMENTS = {
    "botany-greenhouse",
    "cozy-bedroom",
    "modern-classroom",
    "home-living-room",
    "backyard-garden",
    "public-library",
    "science-laboratory",
    "city-park",
    "home-kitchen",
    "school-science-corner",
    "home-study",
    "mountain-viewpoint",
    "tropical-beach",
    "traditional-indonesian-house",
    "historic-town-street",
    "ancient-temple-ruins",
    "rainy-city-street",
    "underwater-world",
    "space-observatory",
    "home-workshop",
    "city-rooftop",
    "mountain-landscape",
}

LEGACY_TOKENS = (
    "props/everyday",
    "props/aura",
    "TapeBanner",
    "WordTagCaptions",
    "Critter",
    "#E07A5F",
    "#BA563B",
    "#D67354",
)


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _extract_beats(ep_dir: Path) -> List[Dict[str, Any]]:
    raw = _load_json(ep_dir / "narration" / "script.json", [])
    beats = raw if isinstance(raw, list) else raw.get("beats", [])
    return [b for b in beats if isinstance(b, dict)]


def _extract_facts(ep_dir: Path) -> List[str]:
    dossier = _load_json(ep_dir / "research" / "dossier.json", {})
    claims = dossier.get("claims") or dossier.get("verified_facts") or []
    facts: List[str] = []
    for c in claims[:6]:
        if isinstance(c, dict):
            txt = c.get("statement") or c.get("claim") or c.get("fact") or ""
            if txt:
                facts.append(str(txt))
        elif isinstance(c, str):
            facts.append(c)
    return facts


def _safe_env(env: str, fallback: str = "science-laboratory") -> str:
    if env == "science-lab":
        return "science-laboratory"
    return env if env in VALID_ENVIRONMENTS else fallback


def _sanitize_tsx(code: str, scene_id: str, default_env: str) -> str:
    """Clean markdown fences and enforce valid PapercraftSceneShell imports/ID."""
    code = code.strip()
    fence = re.search(r"```(?:tsx|typescript|ts|jsx)?\s*\n(.*?)```", code, re.DOTALL)
    if fence:
        code = fence.group(1).strip()
    for bad in LEGACY_TOKENS:
        if bad in code:
            raise ValueError(f"Legacy token '{bad}' detected in {scene_id}")
    if "PapercraftSceneShell" not in code or "<svg" not in code:
        raise ValueError(f"Missing PapercraftSceneShell or <svg in {scene_id}")
    if f"export const {scene_id}" not in code:
        raise ValueError(f"Missing export const {scene_id}")
    code = code.replace('environment="science-lab"', f'environment="{default_env}"')
    code = code.replace("environment='science-lab'", f"environment='{default_env}'")
    return code + "\n"


def _extract_metric(beat_text: str, default_label: str) -> str:
    nums = re.findall(r"\d+(?:[.,]\d+)?\s*(?:%|kg|g/L|km|m|°C|kali|detik|tahun|juta|persen)?", beat_text)
    if nums:
        return nums[0].strip()[:14]
    return default_label


def _svg_for_scene_slot(idx: int, scene_id: str, metric: str, cx: int) -> str:
    """Return 6 completely distinct animated papercraft SVG apparatuses."""
    if idx == 0:
        # S01Hook: Dual-Chamber Transformation Tank + Dissolving Crystals + Dial
        return f"""
        <g transform={{`translate({cx}, 740) scale(${{pop}})`}} filter="url(#paperShadow{scene_id})">
          <rect x={{-230}} y={{-200}} width={{460}} height={{390}} rx={{28}} fill="#FBF6EC" stroke="#1E293B" strokeWidth={{6}} />
          <rect x={{-195}} y={{-160}} width={{175}} height={{230}} rx={{16}} fill="#0284C7" stroke="#075985" strokeWidth={{4}} />
          <polygon points="-145,-60 -115,-85 -85,-60 -115,-35" fill="#F8FAFC" transform={{`translate(0, ${{wave * 0.6}})`}} />
          <polygon points="-165,10 -135,-15 -105,10 -135,35" fill="#E2E8F0" transform={{`translate(0, ${{-wave * 0.5}})`}} />
          <path d="M -5 -45 L 22 -45 L 22 -65 L 55 -35 L 22 -5 L 22 -25 L -5 -25 Z" fill="#D94E34" transform={{`scale(${{0.9 + pulse * 0.12}})`}} />
          <rect x={{45}} y={{-160}} width={{150}} height={{230}} rx={{16}} fill="#BAE6FD" stroke="#0284C7" strokeWidth={{4}} />
          <path d={{`M 45 ${{-20 + wave}} Q 120 ${{-42 + wave}} 195 ${{-20 + wave}} L 195 70 L 45 70 Z`}} fill="#38BDF8" />
          <rect x={{-195}} y={{95}} width={{390}} height={{66}} rx={{14}} fill="#0F172A" />
          <text x={{0}} y={{138}} textAnchor="middle" fill="#F8FAFC" fontSize={{28}} fontWeight={{900}} fontFamily="sans-serif">{metric}</text>
        </g>"""

    if idx == 1:
        # S02Shockwave: Swelling Osmotic Cell + Expanding Shockwave Rings + Needle Gauge
        return f"""
        <g transform={{`translate({cx}, 740) scale(${{pop}})`}} filter="url(#paperShadow{scene_id})">
          <circle cx={{0}} cy={{-30}} r={{175 + pulse * 35}} fill="none" stroke="#EF4444" strokeWidth={{5}} strokeDasharray="16 12" opacity={{0.55}} />
          <circle cx={{0}} cy={{-30}} r={{130 + pulse * 24}} fill="#FEE2E2" stroke="#DC2626" strokeWidth={{6}} />
          <circle cx={{0}} cy={{-30}} r={{85 + pulse * 28}} fill="#FCA5A5" stroke="#B91C1C" strokeWidth={{5}} />
          <path d={{`M -40 -55 L -5 -30 L -32 -5 L 12 20 M 30 -60 L 10 -22 L 42 5`}} fill="none" stroke="#7F1D1D" strokeWidth={{6}} strokeLinecap="round" opacity={{burst}} />
          <g transform="translate(0, 175)">
            <rect x={{-160}} y={{-36}} width={{320}} height={{72}} rx={{16}} fill="#991B1B" stroke="#450A0A" strokeWidth={{4}} />
            <text x={{0}} y={{10}} textAnchor="middle" fill="#FEF2F2" fontSize={{28}} fontWeight={{900}} fontFamily="sans-serif">{metric}</text>
          </g>
        </g>"""

    if idx == 2:
        # S03Domino: Cascading Domino Blocks + Rising Gas Bubbles + Dropping Bar Meter
        return f"""
        <g transform={{`translate({cx}, 750) scale(${{pop}})`}} filter="url(#paperShadow{scene_id})">
          <rect x={{-230}} y={{-200}} width={{460}} height={{400}} rx={{28}} fill="#FEF3C7" stroke="#92400E" strokeWidth={{6}} />
          {{[-145, -55, 35, 125].map((dx, i) => (
            <g key={{i}} transform={{`translate(${{dx}}, 10) rotate(${{Math.min(72, Math.max(0, (frame - 16 - i * 12) * 3.2))}}, 0, 70)`}}>
              <rect x={{-24}} y={{-90}} width={{48}} height={{160}} rx={{10}} fill="#F59E0B" stroke="#78350F" strokeWidth={{4}} />
              <circle cx={{0}} cy={{-50}} r={{10}} fill="#78350F" />
              <circle cx={{0}} cy={{30}} r={{10}} fill="#78350F" />
            </g>
          ))}}
          <circle cx={{-110}} cy={{-130 + wave}} r={{20}} fill="#10B981" stroke="#065F46" strokeWidth={{3}} />
          <circle cx={{20}} cy={{-150 - wave}} r={{26}} fill="#34D399" stroke="#065F46" strokeWidth={{3}} />
          <circle cx={{130}} cy={{-125 + wave * 0.7}} r={{18}} fill="#6EE7B7" stroke="#065F46" strokeWidth={{3}} />
          <rect x={{-180}} y={{115}} width={{360}} height={{56}} rx={{14}} fill="#1E293B" />
          <rect x={{-170}} y={{125}} width={{Math.max(40, 340 * (1 - burst * 0.5))}} height={{36}} rx={{10}} fill="#10B981" />
          <text x={{0}} y={{152}} textAnchor="middle" fill="#FFFFFF" fontSize={{24}} fontWeight={{900}} fontFamily="sans-serif">{metric}</text>
        </g>"""

    if idx == 3:
        # S04ModernReset: Layered Paper Earth Globe + Rising Thermometer + Storm Cloud
        return f"""
        <g transform={{`translate({cx}, 740) scale(${{pop}})`}} filter="url(#paperShadow{scene_id})">
          <circle cx={{-35}} cy={{0}} r={{165}} fill="#0284C7" stroke="#0F172A" strokeWidth={{6}} />
          <path d="M -115 -65 Q -55 -105 10 -60 Q 45 -20 -5 30 Q -70 50 -120 5 Z" fill="#22C55E" stroke="#15803D" strokeWidth={{4}} />
          <path d="M 35 -10 Q 95 -25 110 35 Q 75 95 20 75 Z" fill="#16A34A" stroke="#15803D" strokeWidth={{4}} />
          <g transform={{`translate(${{wave * 0.8}}, -135)`}}>
            <rect x={{-95}} y={{-32}} width={{190}} height={{54}} rx={{27}} fill="#475569" stroke="#1E293B" strokeWidth={{4}} />
            <polygon points="-15,24 5,24 -12,56 8,56 -24,96 -10,60 -28,60" fill="#FACC15" stroke="#CA8A04" strokeWidth={{2}} />
          </g>
          <g transform="translate(175, -10)">
            <rect x={{-28}} y={{-145}} width={{56}} height={{240}} rx={{28}} fill="#F8FAFC" stroke="#334155" strokeWidth={{5}} />
            <circle cx={{0}} cy={{105}} r={{42}} fill="#DC2626" stroke="#7F1D1D" strokeWidth={{5}} />
            <rect x={{-14}} y={{105 - 190 * burst}} width={{28}} height={{190 * burst}} rx={{14}} fill="#EF4444" />
          </g>
          <rect x={{-165}} y={{185}} width={{260}} height={{54}} rx={{14}} fill="#0F172A" />
          <text x={{-35}} y={{221}} textAnchor="middle" fill="#F8FAFC" fontSize={{25}} fontWeight={{900}} fontFamily="sans-serif">{metric}</text>
        </g>"""

    if idx == 4:
        # S05RealityAnchor: Precision Analog Dial + Rotating Equilibrium Ring
        return f"""
        <g transform={{`translate({cx}, 740) scale(${{pop}})`}} filter="url(#paperShadow{scene_id})">
          <g transform={{`rotate(${{frame * 0.8}})`}}>
            <circle cx={{0}} cy={{-20}} r={{195}} fill="none" stroke="#0EA5E9" strokeWidth={{14}} strokeDasharray="48 24" />
          </g>
          <circle cx={{0}} cy={{-20}} r={{155}} fill="#FBF6EC" stroke="#1E3A8A" strokeWidth={{7}} />
          <path d="M -105 35 A 120 120 0 1 1 105 35" fill="none" stroke="#CBD5E1" strokeWidth={{20}} strokeLinecap="round" />
          <path d="M -35 -135 A 120 120 0 0 1 45 -130" fill="none" stroke="#16A34A" strokeWidth={{20}} strokeLinecap="round" />
          <line
            x1={{0}}
            y1={{-20}}
            x2={{Math.cos((needle - 90) * Math.PI / 180) * 105}}
            y2={{-20 + Math.sin((needle - 90) * Math.PI / 180) * 105}}
            stroke="#DC2626"
            strokeWidth={{9}}
            strokeLinecap="round"
          />
          <circle cx={{0}} cy={{-20}} r={{16}} fill="#0F172A" />
          <rect x={{-130}} y={{62}} width={{260}} height={{58}} rx={{14}} fill="#1E3A8A" />
          <text x={{0}} y={{100}} textAnchor="middle" fill="#FFFFFF" fontSize={{28}} fontWeight={{900}} fontFamily="sans-serif">{metric}</text>
        </g>"""

    # S06Outro: Dilemma Balance Scale + @meowndr CTA Card
    return f"""
        <g transform={{`translate({cx}, 840) scale(${{pop}})`}} filter="url(#paperShadow{scene_id})">
          <rect x={{-14}} y={{0}} width={{28}} height={{220}} rx={{6}} fill="#78350F" />
          <rect x={{-90}} y={{210}} width={{180}} height={{28}} rx={{10}} fill="#92400E" />
          <g transform={{`rotate(${{wave * 0.8}})`}}>
            <rect x={{-210}} y={{-10}} width={{420}} height={{20}} rx={{10}} fill="#F59E0B" stroke="#78350F" strokeWidth={{4}} />
            <g transform="translate(-170, 10)">
              <line x1={{0}} y1={{0}} x2={{-36}} y2={{85}} stroke="#451A03" strokeWidth={{3}} />
              <line x1={{0}} y1={{0}} x2={{36}} y2={{85}} stroke="#451A03" strokeWidth={{3}} />
              <rect x={{-68}} y={{85}} width={{136}} height={{54}} rx={{12}} fill="#0284C7" stroke="#075985" strokeWidth={{4}} />
              <text x={{0}} y={{121}} textAnchor="middle" fill="#FFFFFF" fontSize={{22}} fontWeight={{900}} fontFamily="sans-serif">OPSI A</text>
            </g>
            <g transform="translate(170, 10)">
              <line x1={{0}} y1={{0}} x2={{-36}} y2={{85}} stroke="#451A03" strokeWidth={{3}} />
              <line x1={{0}} y1={{0}} x2={{36}} y2={{85}} stroke="#451A03" strokeWidth={{3}} />
              <rect x={{-68}} y={{85}} width={{136}} height={{54}} rx={{12}} fill="#DC2626" stroke="#7F1D1D" strokeWidth={{4}} />
              <text x={{0}} y={{121}} textAnchor="middle" fill="#FFFFFF" fontSize={{22}} fontWeight={{900}} fontFamily="sans-serif">OPSI B</text>
            </g>
          </g>
        </g>
        <g transform={{`translate({cx}, 560) scale(${{pop}})`}} filter="url(#paperShadow{scene_id})">
          <rect x={{-215}} y={{-62}} width={{430}} height={{116}} rx={{20}} fill="#FBF6EC" stroke="#D94E34" strokeWidth={{5}} />
          <text x={{0}} y={{-10}} textAnchor="middle" fill="#0F172A" fontSize={{28}} fontWeight={{900}} fontFamily="sans-serif">SIMPAN &amp; DISKUSI!</text>
          <text x={{0}} y={{32}} textAnchor="middle" fill="#D94E34" fontSize={{24}} fontWeight={{800}} fontFamily="sans-serif">@meowndr</text>
        </g>"""


def _build_fallback_scene_tsx(
    scene_id: str,
    beat_text: str,
    env: str,
    presenter_x: int,
    presenter_face: int,
    presenter_state: str,
    idx: int,
) -> str:
    """Deterministic distinct animated papercraft SVG scene with Cat Scientist interaction & camera."""
    metric = _extract_metric(beat_text, f"FASE {idx + 1}")
    target_x = 670 if presenter_x < 540 else 410
    start_x = presenter_x - 110 if presenter_x < 540 else presenter_x + 110
    yaw = 7 if idx % 2 == 0 else -7
    push = 1.08 if idx in (0, 1, 4) else 1.05
    inner_svg = _svg_for_scene_slot(idx, scene_id, metric, target_x)

    return f"""import React from 'react';
import {{interpolate, spring, useCurrentFrame, useVideoConfig}} from 'remotion';
import {{PapercraftSceneShell}} from '../lib/scenes';
import {{durOf, wordsOf}} from '../scene';

const ID = '{scene_id}';

export const {scene_id}: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{fps}} = useVideoConfig();
  const dur = durOf(ID);
  const words = wordsOf(ID);

  const pop = spring({{frame: frame - 6, fps, config: {{damping: 13, stiffness: 100}}}});
  const burst = spring({{frame: frame - 24, fps, config: {{damping: 12, stiffness: 90}}}});
  const pulse = Math.sin(frame * 0.14) * 0.5 + 0.5;
  const wave = Math.sin(frame * 0.12) * 10;
  const needle = interpolate(frame, [10, Math.max(40, dur - 15)], [-110, 15], {{
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }});

  return (
    <PapercraftSceneShell
      id={{ID}}
      durationInFrames={{dur}}
      environment="{env}"
      camera={{{{yaw: {yaw}, push: {push}, origin: [{target_x}, 760]}}}}
      presenter={{{{
        x: {presenter_x},
        state: '{presenter_state}',
        face: {presenter_face},
        pointAngle: {presenter_face * -28},
      }}}}
      movement={{{{
        type: 'walk',
        startX: {start_x},
        endX: {presenter_x},
        startFrame: 0,
        duration: 22,
        easing: 'easeOut',
      }}}}
      interaction={{{{
        type: 'point',
        target: {{x: {target_x}, y: 740}},
        startFrame: 24,
        duration: 95,
      }}}}
      dialogue={{{{
        words,
        mode: 'audio_driven',
        speakerId: 'cat_scientist',
        style: 'excited',
      }}}}
      badges={{[]}}
    >
      <svg
        width={{1080}}
        height={{1920}}
        viewBox="0 0 1080 1920"
        style={{{{position: 'absolute', inset: 0, pointerEvents: 'none'}}}}
      >
        <defs>
          <filter id="paperShadow{scene_id}" x="-15%" y="-15%" width="130%" height="130%">
            <feDropShadow dx="0" dy="8" stdDeviation="6" floodColor="#1e293b" floodOpacity="0.28" />
          </filter>
        </defs>
        {inner_svg}
      </svg>
    </PapercraftSceneShell>
  );
}};
"""


def _generate_scenes_with_llm(
    title: str,
    niche: str,
    beats: List[Dict[str, Any]],
    facts: List[str],
    storyboard_scenes: List[Dict[str, Any]],
) -> Dict[str, str]:
    """Generate bespoke animated SVG papercraft TSX per batch so each scene is topic-specific."""
    results: Dict[str, str] = {}
    try:
        from library.content_factory.captions.llm_caption_generator import LLMCaptionGenerator
    except Exception:
        return results

    # Generate in 2 batches of 3 scenes for reliability within timeout
    for batch_start in (0, 3):
        batch_slots = SCENE_SLOTS[batch_start : batch_start + 3]
        slot_specs = []
        for offset, (sid, beat_id, default_state, default_env) in enumerate(batch_slots):
            i = batch_start + offset
            beat = beats[i] if i < len(beats) else (beats[-1] if beats else {})
            sb = storyboard_scenes[i] if i < len(storyboard_scenes) else {}
            env = _safe_env(str(sb.get("environment_id") or default_env), default_env)
            px = 240 if i % 2 == 0 else 820
            tx = 670 if px < 540 else 410
            slot_specs.append({
                "scene_id": sid,
                "beat_id": str(beat.get("id") or beat_id),
                "spoken_text": str(beat.get("spoken_text") or ""),
                "environment": env,
                "presenter_x": px,
                "presenter_face": 1 if i % 2 == 0 else -1,
                "presenter_state": default_state,
                "target_x": tx,
            })

        prompt = (
            f"Kamu adalah Remotion Animation Engineer untuk kanal edukasi papercraft @meowndr.\n"
            f"Judul Episode: {title}\nNiche: {niche}\n"
            f"Fakta Riset: {json.dumps(facts[:4], ensure_ascii=False)}\n"
            f"3 Scene Slots:\n{json.dumps(slot_specs, indent=2, ensure_ascii=False)}\n\n"
            "Buat 3 komponen React Remotion TSX yang BERBEDA SATU SAMA LAIN dan visualisasinya spesifik menggambarkan isi spoken_text.\n"
            "ATURAN WAJIB:\n"
            "1. Import persis:\n"
            "   import React from 'react';\n"
            "   import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';\n"
            "   import {PapercraftSceneShell} from '../lib/scenes';\n"
            "   import {durOf, wordsOf} from '../scene';\n"
            "2. Gunakan `const ID = '<scene_id>';`, `const dur = durOf(ID);`, `const words = wordsOf(ID);`.\n"
            "3. Pada `<PapercraftSceneShell>`, WAJIB sertakan:\n"
            "   - `camera={{yaw: 7, push: 1.07, origin: [target_x, 750]}}`\n"
            "   - `presenter={{x: presenter_x, state: presenter_state, face: presenter_face}}`\n"
            "   - `movement={{type: 'walk', startX: presenter_x - 100, endX: presenter_x, startFrame: 0, duration: 22, easing: 'easeOut'}}`\n"
            "   - `interaction={{type: 'point', target: {x: target_x, y: 740}, startFrame: 24, duration: 90}}`\n"
            "   - `dialogue={{words, mode: 'audio_driven', speakerId: 'cat_scientist', style: 'excited'}}`\n"
            "   - `badges={[]}`\n"
            "4. Di dalam children, render `<svg width={1080} height={1920} viewBox=\"0 0 1080 1920\" style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>` berisi ilustrasi papercraft bertumpuk (`<feDropShadow>`) yang dianimasikan dengan `spring()` dan `interpolate(..., {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})` di sekitar x=target_x, y=460..1120.\n"
            "5. Jangan gunakan badge verbal panjang; cukup angka/satuan ukur singkat. Di S06Outro sertakan '@meowndr'.\n\n"
            "Kembalikan HANYA JSON object dengan key persis nama scene_id di atas."
        )
        try:
            data = LLMCaptionGenerator.call_llm(prompt, timeout_sec=90)
            if isinstance(data, dict):
                for sid, _, _, _ in batch_slots:
                    if sid in data and isinstance(data[sid], str):
                        results[sid] = data[sid]
        except Exception:
            continue

    return results


def ensure_episode_scenes(ep_dir: Path, title: str, niche: str, force: bool = False) -> Dict[str, Any]:
    """Ensure papercut/src/scenes/ has 6 populated animated papercraft TSX scenes."""
    papercut_dir = ep_dir / "papercut"
    scenes_dir = papercut_dir / "src" / "scenes"
    ep_json_path = papercut_dir / "episode.json"
    if not scenes_dir.exists() or not ep_json_path.exists():
        return {"generated": False, "reason": "papercut directory not scaffolded"}

    # Skip if already populated with 6 non-starter scenes unless forced
    existing_s01 = scenes_dir / "S01Hook.tsx"
    if not force and (scenes_dir / "S06Outro.tsx").exists() and existing_s01.exists():
        content = existing_s01.read_text(encoding="utf-8")
        if "<svg" in content and "interaction=" in content:
            return {"generated": False, "reason": "already_populated"}

    beats = _extract_beats(ep_dir)
    facts = _extract_facts(ep_dir)
    sb = _load_json(ep_dir / "storyboard" / "storyboard.json", {})
    sb_scenes = sb.get("scenes", []) if isinstance(sb, dict) else []

    llm_scenes = _generate_scenes_with_llm(title, niche, beats, facts, sb_scenes)
    used_fallback: List[str] = []

    for i, (sid, beat_id, default_state, default_env) in enumerate(SCENE_SLOTS):
        sb_item = sb_scenes[i] if i < len(sb_scenes) else {}
        env = _safe_env(str(sb_item.get("environment_id") or default_env), default_env)
        px = 240 if i % 2 == 0 else 820
        face = 1 if i % 2 == 0 else -1
        beat = beats[i] if i < len(beats) else {}
        beat_text = str(beat.get("spoken_text") or title)

        tsx_code: Optional[str] = None
        if sid in llm_scenes:
            try:
                tsx_code = _sanitize_tsx(llm_scenes[sid], sid, env)
            except Exception:
                tsx_code = None

        if tsx_code is None:
            used_fallback.append(sid)
            tsx_code = _build_fallback_scene_tsx(sid, beat_text, env, px, face, default_state, i)

        (scenes_dir / f"{sid}.tsx").write_text(tsx_code, encoding="utf-8")

    # Remove starter-only files if present
    for old_name in ("S02Concept.tsx", "S03Outro.tsx"):
        old_path = scenes_dir / old_name
        if old_path.exists():
            old_path.unlink()

    # Write src/scenes/index.ts
    banner = re.sub(r"[^A-Za-z0-9 ?!.,:-]", "", title.upper())[:72]
    index_lines = ["import React from 'react';"]
    for sid, _, _, _ in SCENE_SLOTS:
        index_lines.append(f"import {{{sid}}} from './{sid}';")
    index_lines.append("")
    index_lines.append("export type SceneDef = {id: string; component: React.FC; banner: string; band: number};")
    index_lines.append("")
    index_lines.append("export const SCENES: SceneDef[] = [")
    for i, (sid, _, _, _) in enumerate(SCENE_SLOTS):
        b = banner if i == 0 else ""
        index_lines.append(f"  {{id: '{sid}', component: {sid}, banner: '{b}', band: 0.86}},")
    index_lines.append("];")
    (scenes_dir / "index.ts").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    # Update episode.json scenes & banners to match the 6 beat IDs
    ep_data = _load_json(ep_json_path, {})
    beat_ids = [str(b.get("id")) for b in beats if b.get("id")]
    new_scenes = []
    for i, (sid, default_bid, _, _) in enumerate(SCENE_SLOTS):
        bid = beat_ids[i] if i < len(beat_ids) else default_bid
        new_scenes.append([sid, bid, 0])
    ep_data["scenes"] = new_scenes
    ep_data["banners"] = {"S01Hook": banner}
    ep_data["cuts"] = {
        "S03Domino": {"kind": "pageTurn"},
        "S05RealityAnchor": {"kind": "pageTurn"},
    }
    ep_json_path.write_text(json.dumps(ep_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Verify TypeScript compiles; if LLM output has any TS error, replace with deterministic fallback
    tsc = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=str(papercut_dir),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if tsc.returncode != 0:
        for i, (sid, _, default_state, default_env) in enumerate(SCENE_SLOTS):
            if sid not in used_fallback:
                sb_item = sb_scenes[i] if i < len(sb_scenes) else {}
                env = _safe_env(str(sb_item.get("environment_id") or default_env), default_env)
                px = 240 if i % 2 == 0 else 820
                face = 1 if i % 2 == 0 else -1
                beat = beats[i] if i < len(beats) else {}
                beat_text = str(beat.get("spoken_text") or title)
                fallback_tsx = _build_fallback_scene_tsx(sid, beat_text, env, px, face, default_state, i)
                (scenes_dir / f"{sid}.tsx").write_text(fallback_tsx, encoding="utf-8")
                used_fallback.append(sid)

    return {
        "generated": True,
        "scenes": [s[0] for s in SCENE_SLOTS],
        "fallback_scenes": used_fallback,
    }
