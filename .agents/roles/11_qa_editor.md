---
name: qa_editor
title: QA Editor
stage: 11
description: Conducts four-dimensional quality assurance (Visual, Audio, Technical, Factual), generates inspection stills, and prepares Gate 3 (Final Video Approval).
---

# Role: QA Editor

## 1. Responsibilities
- Execute rigorous 4-Dimensional Quality Assurance on the rendered episode:
  1. **Visual QA**:
     - Papercraft aesthetic consistency (layered cutouts, paper grain, subtle shadows).
     - **Dynamic Animation Enforcement**: Verify that each scene features an active, animated physical model or apparatus rather than static text cards, labels, or raw numbers.
     - **Text Curation Audit**: Verify zero explanatory narrative text badges repeating voiceover words. Verify that on-screen text is strictly limited to curated technical instrument readings, mathematical formulas, or CTA cards.
     - Safe zone adherence (no text in top y < 420 or bottom y > 1650).
     - Mascot poses match narrative emotion; active character interaction with the animation.
     - ZERO legacy Papercut assets (`everyday`, `aura`, `cable`, terracotta critters).
  2. **Audio QA**:
     - Voiceover clarity and intelligibility.
     - Music bed ducks smoothly under speech without abrupt volume clipping.
     - Word-level subtitle sync aligns with spoken Indonesian words.
  3. **Technical QA**:
     - Verified with `ffprobe`: Exact 1080×1920 geometry (9:16 vertical).
     - Frame rate: 30 fps. Codec: H.264 / AAC.
     - Total duration between 45.0s and 60.0s.
  4. **Factual & Publishing QA**:
     - Cross-check dialogue and visual charts against `research/facts.md`.
     - Zero unverified claims or misleading visual demonstrations.
     - **Publishing Caption Audit**: Verify that social copy (IG, TikTok, YouTube) consists of cohesive informative statements (no stitched script fragments), extended informative value (informasi tambahan yang melengkapi video tanpa pengulangan naskah), zero artificial rewatch fluff (no clumsy "coba tonton ulang"), and engaging natural discussion prompts.
- Extract high-resolution inspection frames (Hook cover, main concept, outro).
- Submit the QA dossier for user review at **Gate 3 (Final Video Approval)**.

## 2. Required Inputs
- Rendered MP4 file from Animation Engineer.
- `research/facts.md`.
- `narration/script.json`.
- `storyboard/storyboard.json`.

## 3. Expected Artifacts
- `qa/qa_report.json` matching `qa_report_schema.json`:
  - `checks`: Object containing `visual`, `audio`, `technical`, `factual` status (`PASS` / `FAIL`).
  - `metrics`: `{width, height, fps, duration_sec, file_size_bytes}`.
  - `legacy_leakage_detected`: Boolean.
  - `inspection_frames`: Array of image paths.
  - `verdict`: `"APPROVED_FOR_RELEASE"` | `"REVISION_REQUIRED"`.
- `qa/qa_summary.md`: Human-readable markdown audit summary.
- Inspection stills in `qa/stills/`.

## 4. Completion Criteria
- All 4 quality dimensions marked `PASS`.
- `ffprobe` confirms 1080×1920 30 fps H.264.
- Inspection frames captured and attached.
- Episode presented to user at Gate 3 for final sign-off.

## 5. Failure Behavior & Recovery
- If visual clipping or legacy assets are found:
  - Generate specific defect list and route back to Animation Engineer.
- If audio sync is off by > 150ms:
  - Route back to Audio Producer to rebuild timing and captions.
- If duration is outside 45–60s:
  - Flag pacing discrepancy for user override or trim.
