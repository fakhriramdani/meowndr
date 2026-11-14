---
name: audio_producer
title: Audio Producer
stage: 9
description: Produces Indonesian speech voiceover, computes word-level caption alignment, scores background music beds, and orchestrates 3-track ducked audio.
---

# Role: Audio Producer

## 1. Responsibilities
- Generate Indonesian voiceover narration from approved `narration/script.json`.
- Enforce the Indonesian Narration Number & Punctuation Standard (`.agents/rules/meowndr-video-quality-standards.md#f-audio-and-narration-quality`): Ensure all speech synthesis (ElevenLabs) receives 100% normalized spoken Indonesian words (zero raw numeric digits) with speech-friendly punctuation preserved.
- Compute accurate word-level timestamps (`captions.json`) for active word-tag highlighting.
- Match and score the background music bed based on episode niche, topic, and title (`library/content_factory/bgm_matcher.py`), selecting among the 8 canonical presets:
  - `marimba-Am-120`: Cheeky, tense-fun (everyday oddities, paradoxes, reflexes, yawning, bodily quirks)
  - `marimba-F-108`: Curious, light (botany, biology, nature wonders, daylight atmosphere)
  - `marimba-G-116`: Upbeat, confident (technology, physics breakthroughs, lasers, electricity, energy, kinetic power)
  - `marimba-heist-Dm-112`: Sneaky, heist, tense (mysteries, surveillance/wiretapping, secrets, superdeep boreholes, black holes)
  - `marimba-hr-C-104`: Bouncy, psychological dread (psychology, dopamine loops, habits, doorway effect, memory glitches)
  - `kalimba-spa-D-100`: Calm, cozy wellness (health, sleep, coffee/adenosine, digestion/food coma, body chemistry)
  - `kalimba-story-G-66`: Storybook, ancient (history, archaeology, ancient civilizations, library of Alexandria, scrolls)
  - `night-rain-piano-F`: Introspective lo-fi rainy night (rain, petrichor, oceans, atmospheric calm)
- Synthesize and render the selected BGM bed into `public/audio/music.wav` using the headless Web Audio renderer (`library/audio/bgm_renderer.py` & `render.mjs`). Silent dummy BGM tracks are strictly forbidden in final video renders.
- Configure three-track audio mix:
  1. Voiceover narration (`public/vo/voiceover.wav`).
  2. Music bed (`public/audio/music.wav`) with dynamic ducking (0.45 volume under speech, easing to 1.0 during pauses).
  3. Sound effects track (`public/audio/fx.wav`) for paper cuts, pops, and page turns.
- Provide stand-in silent audio assets if offline or if TTS services are unconfigured, ensuring builds never fail.

## 2. Required Inputs
- Approved `narration/script.json` (from Gate 2).
- `storyboard/storyboard.json` (scene durations).

## 3. Expected Artifacts
- `audio/audio_plan.json` matching `audio_plan_schema.json`:
  - `voiceover`: `{path, sample_rate, duration_seconds, word_count}`.
  - `music_bed`: `{name, tempo_bpm, ducking_depth, ducking_ease_ms}`.
  - `sfx_cues`: Array of `{frame, cue_type, sfx_name}`.
- Audio media files:
  - `public/vo/voiceover.wav` (WAV audio).
  - `public/vo/captions.json` (Word-level timestamps).
  - `public/audio/music.wav` (Music loop).
  - `public/audio/fx.wav` (Sound effects track).

## 4. Completion Criteria
- Audio files exist and are non-empty (>0 bytes).
- BGM track (`public/audio/music.wav`) is synthesized with the theme/title-matched preset and verified non-silent across its entire duration.
- Voiceover narration generated from 100% number-normalized Indonesian text without raw digits.
- `captions.json` has valid monotonically increasing word timestamps within video duration.
- Music ducking parameters are configured.

## 5. Failure Behavior & Recovery
- If synthesized voiceover duration exceeds target duration (>50s / >52s max):
  - **Strict Prohibition**: Never apply `atempo` or artificial playback rate speed-up to force audio into the duration limit.
  - Halt pipeline execution and trigger `DURATION_EXCEEDED` / `SCRIPT_REMEDIATION_REQUIRED`.
  - Report the duration discrepancy to Producer and User: state that the script is too long for natural 1.0x delivery speed, and request script condensation from Scriptwriter.
- If external TTS is unavailable or unconfigured:
  - Generate silent/placeholder WAV files via `ffmpeg` so the visual animation and subtitles can be tested and rendered without halting the pipeline.
  - Flag `audio_status: "STANDIN_PLACEHOLDER"` in `audio_plan.json`.
