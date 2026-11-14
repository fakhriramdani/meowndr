# Canonical Character Specification: Cat Scientist ("Kucing Ilmuwan")

**Single Source of Truth** for the Papercraft Content Factory lead presenter mascot.

---

## 1. Visual Identity & Archetype

The **Cat Scientist** is the brand mascot and narrator across all educational explainers, thumbnails, avatars, and channel branding.
- **Species & Fur Pattern**: Domestic feline with canonical **vibrant orange and cream coat** (bi-color orange tabby / orange-and-cream).
- **Personality**: Curious, intelligent, enthusiastic, approachable, slightly whimsical.
- **Medium**: Handcrafted 2D layered cardstock papercraft with physical paper grain, soft drop shadows, and deckle cut edges.

> [!IMPORTANT]
> **Strict Identity Constraint**: The mascot's fur is **ORANGE (`#F97316`)** with **CREAM (`#FFFDF7`)** muzzle, cheeks, chest, and paws. Under NO circumstances should the cat ever be rendered with white or monochrome fur.

---

## 2. Canonical Color Palette Tokens

| Component | Papercraft Material | Hex Code | Purpose & Application |
|---|---|---|---|
| **Primary Fur** | Warm Tangerine Cardstock | `#F97316` | Head base, plain fur torso, upper arms, feline hand/paw wrists & bases |
| **Fur Shading / Accents** | Burnt Orange Cardstock | `#EA580C` | Outer ears, hind legs, tail base |
| **Secondary Fur (Muzzle/Cheeks/Paws)** | Crisp Cream Cardstock | `#FFFDF7` / `#FFFDF8` | Snout/muzzle, cheek tufts, neck bib, tail tip, paw tips/toes |
| **Inner Ears & Nose** | Blossom Pink Cardstock | `#FB7185` | Triangular inner ear folds, snout paper nose |
| **Whiskers** | Dark Umber Cardstock | `#9A3412` / `#7C2D12` | 3 pairs of fine cut cardstock whiskers |
| **Scientist Spectacles** | Amber Wire Cardstock | `#B45309` | Round intellectual spectacles with bridge and ear pieces |
| **Eye Iris** | Golden Amber Cardstock | `#D97706` | Expressive curious feline pupils |
| **Eye Pupil & Cavity** | Midnight Slate | `#0F172A` | Center pupil with dual white paper catchlights (`#FFFFFF`) |
| **Lab Coat** | Off-White Lab Linen | `#FAF8F5` | Tailored paper lab coat with `#EDE8E1` lapels |
| **Lab Coat Pen** | Deep Teal Paper | `#0D9488` | Signature breast pocket scientific accessory |

---

## 3. Technical Implementation Rules (Web & Remotion)

### The Opaque Grain Bug & CSS Blend Mode Rule
`public/bg/grain.png` is an opaque paper texture scan without transparency.
When applying paper grain to colored elements:

```tsx
// ❌ INCORRECT (Causes White Cat Bug):
// Opaque grain scan completely paints over #F97316 orange background!
<div style={{
  backgroundColor: '#F97316',
  backgroundImage: `url(${GRAIN})`,
  backgroundSize: '360px',
}} />

// ✅ MANDATORY CANONICAL FORM:
// CSS backgroundBlendMode: 'multiply' multiplies paper grain into orange cardstock!
<div style={{
  backgroundColor: '#F97316',
  backgroundImage: `url(${GRAIN})`,
  backgroundSize: '360px',
  backgroundBlendMode: 'multiply',
}} />
```

### Papercraft Layering Order (Z-Index Stack)
1. **Floor Contact Shadow**: Radial or elliptical drop shadow (`rgba(15, 23, 42, 0.35)`).
2. **Layer 1 (Z: 1) — Animated Tail**: `#EA580C` base curve with `#FFFDF7` cream tip and `backgroundBlendMode: 'multiply'`.
3. **Layer 2 (Z: 2) — Hind Legs & Paws**: `#EA580C` planted legs with `#FFFDF7` rounded cream paws.
4. **Layer 3 (Z: 3) — Torso & Lab Coat**: `#FAF8F5` lab coat with `#EDE8E1` lapels, center seam, buttons, and breast pocket with `#0D9488` teal pen. Inner orange fur (`#F97316`) and cream bib (`#FFFDF7`) peeking at the neck.
5. **Layer 4 (Z: 2) — Back Arm & Hand**: Cream lab coat sleeve (`#FAF8F5`) with cuff line (`#EDE8E1`). Emerging feline paw base has vibrant **orange fur (`#F97316`)** with rounded **cream paw tip (`#FFFDF7`)**. Solid white hands are strictly prohibited.
6. **Layer 5 (Z: 5) — Head & Face Assembly**:
   - Outer Ears (`#EA580C`) with Pink Inner Folds (`#FB7185`).
   - Main Orange Head Base (`#F97316`, `backgroundBlendMode: 'multiply'`).
   - Cream Cheek Fur Tufts (`#FFFDF7` polygon cutouts).
   - Cream Snout / Muzzle Cardstock (`#FFFDF7`).
   - Pink Nose (`#FB7185`).
   - Modular Lip-Sync Mouth (`CatScientistMouth.tsx`).
   - Dark Umber Whiskers (`#9A3412`).
   - Amber Cutout Eyes (`#D97706`) with dual catchlights.
   - Amber Wire Spectacles (`#B45309`).
7. **Layer 6 (Z: 6) — Front Gesturing Arm & Lead Paw**: Cream lab coat sleeve (`#FAF8F5`) with cuff seam (`#EDE8E1`). Gesturing feline paw base has vibrant **orange fur (`#F97316`)** with **cream fingertip markings (`#FFFDF7`)**, holding scientific props (magnifier, test tube, pointer). Solid white hands are strictly prohibited.

---

## 4. Visual Generation & Prompting Standards

When generating avatars, thumbnails, or promotional illustrations:
- **Positive Prompt Keywords**: `handcrafted layered 2D papercraft illustration, adorable orange-and-cream cat scientist mascot, vibrant warm orange fur (#F97316), cream-white muzzle and cheeks, pink paper nose, round amber wire-rimmed spectacles, crisp cream paper lab coat with turquoise pocket pen, tactile cardstock textures, subtle drop shadows, clean minimalist cut-paper aesthetic`.
- **Negative Prompt Keywords**: `photorealistic cat, white cat, black cat, grey cat, calico, 3D CGI plastic rendering, glossy reflections, metal textures, hyperrealistic fur fibers, missing glasses, extra ears, deformed paws`.

---

## 5. Automated QA & Verification Gate

Before approving any episode or brand asset:
1. Run character color validation:
   ```bash
   python3 library/tools/validate_character_color.py
   ```
2. Run episode validation:
   ```bash
   python3 library/tools/validate_episode.py episodes/<episode-dir>
   ```
3. Run brand asset audit:
   ```bash
   python3 library/tools/validate_brand_assets.py
   ```

Any violation of color tokens or missing `backgroundBlendMode: 'multiply'` will immediately fail CI/CD and block production release.
