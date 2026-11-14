#!/usr/bin/env python3
"""Bespoke Animated Papercraft Scene Generator for @meowndr episodes.

Generates 6 Remotion TSX scene components (S01Hook .. S06Outro) with animated
SVG papercraft physical models/instruments tailored to the episode's script beats,
research dossier, and storyboard, then verifies compilation with `tsc --noEmit`.
"""

from __future__ import annotations

import json
import os
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


def _build_fallback_scene_tsx(
    scene_id: str,
    beat_text: str,
    env: str,
    presenter_x: int,
    presenter_face: int,
    presenter_state: str,
    idx: int,
) -> str:
    """Deterministic animated papercraft SVG apparatus fallback (always compiles)."""
    nums = re.findall(r"\d+(?:[.,]\d+)?\s*(?:%|kg|g/L|km|m|°C|kali|detik|tahun|juta)?", beat_text)
    metric = (nums[0].strip() if nums else f"FASE {idx + 1}")[:14]
    is_outro = scene_id == "S06Outro"
    accent = ["#0284C7", "#DC2626", "#D97706", "#059669", "#2563EB", "#D94E34"][idx % 6]

    if is_outro:
        inner_svg = f"""
        <g transform={{`translate(680, 760) scale(${{pop}})`}} filter="url(#paperShadow{scene_id})">
          <rect x={{-14}} y={{0}} width={{28}} height={{240}} rx={{6}} fill="#78350F" />
          <rect x={{-90}} y={{230}} width={{180}} height={{28}} rx={{10}} fill="#92400E" />
          <g transform={{`rotate(${{wave}})`}}>
            <rect x={{-210}} y={{-10}} width={{420}} height={{20}} rx={{10}} fill="#F59E0B" stroke="#78350F" strokeWidth={{4}} />
            <g transform="translate(-170, 10)">
              <line x1={{0}} y1={{0}} x2={{-36}} y2={{90}} stroke="#451A03" strokeWidth={{3}} />
              <line x1={{0}} y1={{0}} x2={{36}} y2={{90}} stroke="#451A03" strokeWidth={{3}} />
              <rect x={{-64}} y={{90}} width={{128}} height={{54}} rx={{12}} fill="#0284C7" stroke="#075985" strokeWidth={{4}} />
              <text x={{0}} y={{126}} textAnchor="middle" fill="#FFFFFF" fontSize={{24}} fontWeight={{900}} fontFamily="sans-serif">TAWAR</text>
            </g>
            <g transform="translate(170, 10)">
              <line x1={{0}} y1={{0}} x2={{-36}} y2={{90}} stroke="#451A03" strokeWidth={{3}} />
              <line x1={{0}} y1={{0}} x2={{36}} y2={{90}} stroke="#451A03" strokeWidth={{3}} />
              <rect x={{-64}} y={{90}} width={{128}} height={{54}} rx={{12}} fill="#DC2626" stroke="#7F1D1D" strokeWidth={{4}} />
              <text x={{0}} y={{126}} textAnchor="middle" fill="#FFFFFF" fontSize={{24}} fontWeight={{900}} fontFamily="sans-serif">ASIN</text>
            </g>
          </g>
        </g>
        <g transform={{`translate(680, 520) scale(${{pop}})`}} filter="url(#paperShadow{scene_id})">
          <rect x={{-215}} y={{-62}} width={{430}} height={{116}} rx={{20}} fill="#FBF6EC" stroke="#D94E34" strokeWidth={{5}} />
          <text x={{0}} y={{-10}} textAnchor="middle" fill="#0F172A" fontSize={{28}} fontWeight={{900}} fontFamily="sans-serif">SIMPAN &amp; DISKUSI!</text>
          <text x={{0}} y={{32}} textAnchor="middle" fill="#D94E34" fontSize={{24}} fontWeight={{800}} fontFamily="sans-serif">@meowndr</text>
        </g>"""
    else:
        inner_svg = f"""
        <g transform={{`translate(680, 740) scale(${{pop}})`}} filter="url(#paperShadow{scene_id})">
          <rect x={{-230}} y={{-210}} width={{460}} height={{420}} rx={{28}} fill="#FBF6EC" stroke="#334155" strokeWidth={{6}} />
          <rect x={{-190}} y={{-165}} width={{380}} height={{230}} rx={{18}} fill="#E0F2FE" stroke="#0369A1" strokeWidth={{4}} />
          <path
            d={{`M -190 ${{10 + wave}} Q -95 ${{-18 + wave}} 0 ${{10 + wave}} T 190 ${{10 + wave}} L 190 65 L -190 65 Z`}}
            fill="{accent}"
            opacity={{0.85}}
          />
          <circle cx={{-80}} cy={{-65 + wave * 0.6}} r={{22}} fill="#FFFFFF" opacity={{0.7}} />
          <circle cx={{65}} cy={{-35 - wave * 0.5}} r={{16}} fill="#FFFFFF" opacity={{0.65}} />
          <g transform="translate(0, 130)">
            <circle cx={{-110}} cy={{0}} r={{56}} fill="#FEF3C7" stroke="#92400E" strokeWidth={{5}} />
            <line
              x1={{-110}}
              y1={{0}}
              x2={{-110 + Math.cos((needle - 90) * Math.PI / 180) * 38}}
              y2={{Math.sin((needle - 90) * Math.PI / 180) * 38}}
              stroke="#DC2626"
              strokeWidth={{6}}
              strokeLinecap="round"
            />
            <circle cx={{-110}} cy={{0}} r={{8}} fill="#78350F" />
            <rect x={{-20}} y={{-34}} width={{210}} height={{68}} rx={{14}} fill="#0F172A" />
            <text x={{85}} y={{10}} textAnchor="middle" fill="#F8FAFC" fontSize={{28}} fontWeight={{900}} fontFamily="sans-serif">{metric}</text>
          </g>
        </g>"""

    return f"""import React from 'react';
import {{interpolate, spring, useCurrentFrame, useVideoConfig}} from 'remotion';
import {{PapercraftSceneShell}} from '../lib/scenes';
import {{durOf}} from '../scene';

const ID = '{scene_id}';

export const {scene_id}: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{fps}} = useVideoConfig();
  const dur = durOf(ID);

  const pop = spring({{frame: frame - 8, fps, config: {{damping: 13, stiffness: 100}}}});
  const wave = Math.sin(frame * 0.12) * 10;
  const needle = interpolate(frame, [10, Math.max(40, dur - 15)], [-110, 95], {{
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }});

  return (
    <PapercraftSceneShell
      durationInFrames={{dur}}
      environment="{env}"
      camera={{{{yaw: {4 if idx % 2 == 0 else -4}, push: 1.05}}}}
      presenter={{{{
        x: {presenter_x},
        state: '{presenter_state}',
        face: {presenter_face},
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
) -> Optional[Dict[str, str]]:
    """Ask LLM to generate 6 bespoke animated SVG papercraft TSX scene files."""
    try:
        from library.content_factory.captions.llm_caption_generator import LLMCaptionGenerator
    except Exception:
        return None

    slot_specs = []
    for i, (sid, beat_id, default_state, default_env) in enumerate(SCENE_SLOTS):
        beat = beats[i] if i < len(beats) else (beats[-1] if beats else {})
        sb = storyboard_scenes[i] if i < len(storyboard_scenes) else {}
        env = _safe_env(str(sb.get("environment_id") or default_env), default_env)
        slot_specs.append({
            "scene_id": sid,
            "beat_id": str(beat.get("id") or beat_id),
            "spoken_text": str(beat.get("spoken_text") or ""),
            "environment": env,
            "presenter_x": 240 if i % 2 == 0 else 820,
            "presenter_face": 1 if i % 2 == 0 else -1,
            "presenter_state": default_state,
        })

    prompt = (
        f"Kamu adalah Remotion Animation Engineer untuk kanal edukasi papercraft @meowndr.\n"
        f"Judul Episode: {title}\nNiche: {niche}\n"
        f"Fakta Riset: {json.dumps(facts[:4], ensure_ascii=False)}\n"
        f"6 Scene Slots:\n{json.dumps(slot_specs, indent=2, ensure_ascii=False)}\n\n"
        "Buat 6 komponen React Remotion TSX yang BENAR-BENAR BERBEDA dan relevan dengan topik episode di atas.\n"
        "ATURAN KETAT:\n"
        "1. Setiap scene HARUS mengimpor:\n"
        "   import React from 'react';\n"
        "   import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';\n"
        "   import {PapercraftSceneShell} from '../lib/scenes';\n"
        "   import {durOf} from '../scene';\n"
        "2. Setiap scene HARUS memiliki `const ID = '<scene_id>';`, `const dur = durOf(ID);`, dan `export const <scene_id>: React.FC = () => { ... }`.\n"
        "3. Di dalam `<PapercraftSceneShell durationInFrames={dur} environment=\"...\" camera={{yaw: 4, push: 1.05}} presenter={{x: ..., state: '...', face: ...}} badges={[]}>`, render `<svg width={1080} height={1920} viewBox=\"0 0 1080 1920\" style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>` berisi model fisik/instrumen sains papercraft yang dianimasikan dengan `spring()` dan `interpolate(..., {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})` serta `<feDropShadow>`.\n"
        "4. Safe area visual: letakkan ilustrasi SVG di area x=380..980 (jika presenter_x=240) atau x=100..700 (jika presenter_x=820), dan y=420..1180 agar tidak bertabrakan dengan banner atas maupun maskot/subtitle bawah.\n"
        "5. DILARANG pakai badge teks verbal yang mengulang narasi. Hanya angka/satuan ukur/label instrumen singkat, dan di S06Outro sertakan kartu '@meowndr' + animasi timbangan/dilema.\n"
        "6. Pastikan TypeScript valid 100% (jangan pakai properti CSS/SVG yang tidak valid, jangan pakai komponen luar selain yang diimpor di atas).\n\n"
        "Kembalikan HANYA JSON object dengan key persis: "
        '{"S01Hook": "<kode tsx>", "S02Shockwave": "<kode tsx>", "S03Domino": "<kode tsx>", '
        '"S04ModernReset": "<kode tsx>", "S05RealityAnchor": "<kode tsx>", "S06Outro": "<kode tsx>"}'
    )
    try:
        data = LLMCaptionGenerator.call_llm(prompt, timeout_sec=120)
        if isinstance(data, dict) and all(k in data for k, _, _, _ in SCENE_SLOTS):
            return {k: str(data[k]) for k, _, _, _ in SCENE_SLOTS}
    except Exception:
        pass
    return None


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
        if "<svg" in existing_s01.read_text(encoding="utf-8"):
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
        if llm_scenes and sid in llm_scenes:
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
        index_lines.append(f"  {{id: '{sid}', component: {sid}, banner: '{b}', band: 0.77}},")
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
