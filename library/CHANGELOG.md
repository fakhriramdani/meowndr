# Changelog

## 0.2.0: Episode 10 (Nikola Tesla) Asset Harvest & Kit Hardening

Harvested from `10-whatif-tesla` ("Bagaimana Jika Nikola Tesla Diberikan Dana Tanpa Batas?"):

- **8 Reusable Science Visual Components** (`kit/science/`):
  - `WardenclyffeHookVisual`: 57m papercraft Wardenclyffe wireless power tower with animated knife switch and glowing wireless lightbulb.
  - `NiagaraCleanEnergyVisual`: Hydroelectric water turbine eliminating fossil fuel smokestacks via clean wireless power generation.
  - `SchumannResonanceVisual`: 7.83 Hz electromagnetic cavity resonator between Earth's surface and the ionosphere.
  - `WirelessTransportVisual`: Electric vehicles and electric aviation operating indefinitely without heavy toxic lithium batteries.
  - `MountainDemocratizationVisual`: Ground copper antenna stake delivering clean water pumping to remote mountain villages.
  - `SpaceBeamedPowerVisual`: Planetary wireless beamed power reaching orbital space stations and extraterrestrial settlements.
  - `KardashevCivilizationVisual`: Ascension monument where fossil fuel oil barrels split apart as a clean energy golden lotus blooms.
  - `OutroDiscussionCard`: Floating glowing papercraft Earth globe model with interactive community call-to-action badges.
- **Kit Hardening & Defect Fixes**:
  - `overlays/PapercraftHookTitle.tsx`: Added 3-tier card spacing parameters (`gap: size * 0.28`, `size: 58`, `top: 200`) preventing text overflow and banner overlap.
  - `paper/backdrops.tsx`: Restored `Backdrop` with full-frame asset resolution from `AssetLoader` and dynamic `getEnvironmentLayout`.
  - `scenes/PapercraftSceneShell.tsx`: Restored background layer in default `layerOrder` to eliminate black/empty scenes during custom compositing.
- **Asset Catalog Synchronization**:
  - Registered all 8 new props in `assets/props/` and `assets/library.json` (now 16 registered props).
  - Regenerated `papercut/CATALOG.md` (now 190 kit exports).

## 0.1.0: first public release

What ships.

- Kit (`papercut/kit/`): paper primitives, set builders, a UI kit, a default critter, props sets, `tokens.ts`, local fonts and the `CtaPhoneDM` scene template. `papercut/CATALOG.md` lists every export with its props.
- 24 backdrops (`papercut/public/bg/backdrops/`, `<Backdrop name="..." />`), each with a floor line and a calm band for the banner and captions. The sources of the eight code-drawn ones are in `papercut/backdrops-src/`.
- Camera moves (`paper/camera.tsx`): orbit with depth layers, foreground pass, rack focus, snap zoom, pull-back, freeze frame, dolly zoom, crab track, crane, POV masks, time ramp, dutch tilt, tilt shift, focus pulse, focus hunt and handheld.
- Scene transitions (`paper/transitions.tsx`, `<CutSeries>`): whip, zoom-through, page turn, tear-away, tape pull, stamp cut, infinite zoom, pop-up book, keyhole and burn-away.
- Film-look layers (`paper/look.tsx`): gate weave and flicker, moving felt fibre, lens dirt, lamp flicker, halftone and graph paper.
- Audio: 79 sound effects (one file each), 8 music beds (marimba and kalimba presets plus a rain-and-piano night bed), a Web Audio engine and an offline renderer.
- Tools: scaffold (`new_episode.sh`), kit sync, scene stubs, voiceover and frame-plan builder, SFX cue builder, cached per-scene render, audio mix, QA contact sheets, page capture, catalog generator, harvest report, placeholder narration and a self-test.
- Optional voice pipeline (`voice/`): Qwen3-TTS narration, take picking, pace and loudness pass, word timing, with a setup script.
