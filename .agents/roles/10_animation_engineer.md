---
name: animation_engineer
title: Animation Engineer
stage: 10
description: Implements Remotion scene components, updates timing plans, resolves asset bindings, and renders the final video at 1080×1920 30 fps.
---

# Role: Animation Engineer

## 1. Responsibilities
- Implement TypeScript React scene components in `src/scenes/` (`S01Hook.tsx`, `S02...tsx`) using `PapercraftSceneShell`.
- **Mandatory Visual Animation**: Never render an empty `PapercraftSceneShell` or rely on static text/badges as the primary visual. Every scene must render an animated React/SVG papercraft model with moving parts (`interpolate`, `spring`).
- **Curated On-Screen Text Placement**:
  - Keep `badges={[]}` on `PapercraftSceneShell`. Do NOT add floating narrative explanatory badges repeating what the narrator says.
  - Text inside visual components must be strictly curated: technical apparatus measurements, units, mathematical formulas, and the interactive CTA card.
- Bind `CatScientist` poses, papercraft callout badges (`PapercraftBadge`), and topic demonstrations with active character interaction (look_at, point_at, recoil, celebrate).
- Assemble `src/scenes/index.ts` scene registry with accurate banner texts and caption bands.
- Sync `src/plan.json` scene start frames (`from`) and durations (`durationInFrames`).
- Maintain `episode.json` with typed metadata and environment selection.
- Execute TypeScript compilation (`tsc --noEmit`), ESLint checks, and Remotion video rendering.

## 2. Required Inputs
- `storyboard/storyboard.json`.
- `assets/asset_plan.json`.
- `audio/audio_plan.json`.
- Synchronized papercraft kit in `src/lib/`.

## 3. Expected Artifacts
- Scene components:
  - `src/scenes/S01Hook.tsx`, `S02...tsx`, `S03...tsx`, etc.
  - `src/scenes/index.ts`.
- Configuration files:
  - `src/plan.json`.
  - `episode.json`.
- Rendered video output:
  - `out/<episode-out-name>.mp4` (1080×1920, 30 fps, H.264/AAC).

## 4. Completion Criteria
- Zero TypeScript compilation errors (`tsc --noEmit`).
- Zero ESLint warnings/errors (`npm run lint`).
- Remotion renders output video cleanly without runtime crashes.
- Video duration between 45 and 60 seconds (1350–1800 frames).

## 5. Failure Behavior & Recovery
- If interpolation monotonicity error occurs (`interpolate(f, [a, b])` where `a >= b`):
  - Enforce `const safeEnd = Math.max(startAt + 1, endAt)`.
- If a build fails due to missing packages or node_modules:
  - Symlink from donor node_modules or re-run `npm install --no-audit --no-fund`.
