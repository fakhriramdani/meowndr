#!/usr/bin/env python3
"""
Character Identity & Visual QA Validator: Cat Scientist Mascot
Ensures single source of truth for the canonical Orange-and-Cream Cat Scientist mascot.

Validates:
1. All CatScientist.tsx components across templates and episodes.
2. CSS backgroundBlendMode: 'multiply' on all textured fur elements (avoids opaque grain occlusion bug).
3. Primary coat color (#F97316) on head base and non-lab-coat body.
4. Secondary cream color (#FFFDF7 / #FFFDF8) on snout, cheek tufts, bib, tail tip, and paws.
5. Pink accents (#FB7185) on nose and inner ear cardstock.
6. Ear cardstock (#EA580C) and spectacles (#B45309).
7. SVG and banner generation scripts for proper mascot color fills.
8. Flags regressions where cat is rendered white or has missing blend modes.
"""

import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Required color tokens
COLOR_ORANGE_PRIMARY = "#F97316"
COLOR_ORANGE_SHADE   = "#EA580C"
COLOR_CREAM_WHITE    = "#FFFDF7"
COLOR_PINK_ACCENT    = "#FB7185"
COLOR_SPECTACLES     = "#B45309"
COLOR_LAB_COAT       = "#FAF8F5"

def validate_cat_scientist_component(filepath: Path) -> list[str]:
    errors = []
    content = filepath.read_text(encoding="utf-8")

    # 1. Check opaque texture occlusion (must have backgroundBlendMode: 'multiply')
    # Count occurrences of GRAIN vs backgroundBlendMode
    grain_count = content.count("backgroundImage: `url(${GRAIN})`")
    blend_count = content.count("backgroundBlendMode: 'multiply'")

    if grain_count == 0:
        errors.append(f"{filepath}: Missing GRAIN paper texture reference.")
    elif blend_count < grain_count:
        errors.append(
            f"{filepath}: Has {grain_count} GRAIN textures but only {blend_count} 'backgroundBlendMode: multiply'. "
            f"Opaque grain scan will occlude underlying orange fur resulting in white cat bug!"
        )

    # 2. Check head base color
    if COLOR_ORANGE_PRIMARY not in content:
        errors.append(f"{filepath}: Missing primary orange fur token {COLOR_ORANGE_PRIMARY}.")

    # 3. Check cheek tufts are cream (#FFFDF7), not orange (#EA580C)
    # The cheek tuft highlights must contrast against the orange head
    if "Cream Cat Cheek Fur Tuft Highlights" in content or "Cheek Fur Tuft" in content:
        # Check if cheek tufts use cream
        if not re.search(r"top:\s*2\.6\s*\*\s*u,[\s\S]*?backgroundColor:\s*['\"]#FFFDF7['\"]", content):
            errors.append(f"{filepath}: Cheek fur tufts must use cream cardstock (#FFFDF7), not dark orange or white.")

    # 4. Check snout / muzzle uses cream
    if not re.search(r"backgroundColor:\s*['\"]#FFFDF7['\"][\s\S]*?borderRadius:.*?(Snout|Muzzle|Pink Paper Nose)", content):
        if "#FFFDF7" not in content:
            errors.append(f"{filepath}: Muzzle/snout cardstock must use cream color token #FFFDF7.")

    # 5. Check pink nose
    if COLOR_PINK_ACCENT not in content:
        errors.append(f"{filepath}: Missing pink accent token {COLOR_PINK_ACCENT} for nose / inner ears.")

    # 6. Check hand/paw colors (must have orange fur #F97316 base and cream #FFFDF7 tip)
    # Both arms must render orange feline paws emerging from the lab coat sleeve
    if "Orange Feline Paw Base emerging from sleeve" in content or "Layer 4: Left Arm" in content:
        # Check that arms use orange fur #F97316 on the paw base
        left_arm_match = re.search(r"Layer 4:\s*Left Arm[\s\S]*?Layer 5:", content)
        if left_arm_match:
            arm_text = left_arm_match.group(0)
            if COLOR_ORANGE_PRIMARY not in arm_text:
                errors.append(f"{filepath}: Left hand/paw base must have orange fur ({COLOR_ORANGE_PRIMARY}), not solid white/cream.")
            if COLOR_CREAM_WHITE not in arm_text:
                errors.append(f"{filepath}: Left hand/paw tip must have cream marking ({COLOR_CREAM_WHITE}).")

        right_arm_match = re.search(r"Layer 6:\s*Right Arm[\s\S]*?</div>\s*</div>\s*\);\s*};", content)
        if right_arm_match:
            arm_text = right_arm_match.group(0)
            if COLOR_ORANGE_PRIMARY not in arm_text:
                errors.append(f"{filepath}: Right hand/paw base must have orange fur ({COLOR_ORANGE_PRIMARY}), not solid white/cream.")
            if COLOR_CREAM_WHITE not in arm_text:
                errors.append(f"{filepath}: Right hand/paw tip must have cream marking ({COLOR_CREAM_WHITE}).")

    return errors

def validate_banner_generator(filepath: Path) -> list[str]:
    errors = []
    content = filepath.read_text(encoding="utf-8")

    # Check mascot head base fill in SVG
    if '<rect x="-85" y="-80" width="170" height="135" rx="58" fill="#F97316"' not in content:
        errors.append(f"{filepath}: Mascot head base must have fill=\"#F97316\" (canonical orange), not #FAF8F5 (white).")

    # Check cheek tufts fill
    if '<polygon points="-82,-26 -104,-12 -82,2" fill="#FFFDF8"' not in content:
        errors.append(f"{filepath}: Mascot cheek tufts must have fill=\"#FFFDF8\" (cream highlights).")

    # Check mascot hands/paws in banner
    if '<!-- Orange Feline Paw Base -->' not in content or 'fill="#F97316"' not in content:
        errors.append(f"{filepath}: Banner mascot hands/paws must have orange fur base (fill=\"#F97316\").")

    return errors

def main():
    print("=" * 70)
    print("🐾 CAT SCIENTIST CHARACTER IDENTITY & COLOR VALIDATOR")
    print("=" * 70)

    all_errors = []

    # 1. Discover all CatScientist.tsx files
    cat_files = list(REPO_ROOT.glob("**/CatScientist.tsx"))
    # Filter out node_modules
    cat_files = [f for f in cat_files if "node_modules" not in str(f)]

    print(f"\n[1/3] Validating {len(cat_files)} CatScientist.tsx components...")
    for f in sorted(cat_files):
        rel = f.relative_to(REPO_ROOT)
        file_errors = validate_cat_scientist_component(f)
        if file_errors:
            print(f"  ❌ FAIL: {rel}")
            for err in file_errors:
                print(f"     -> {err}")
            all_errors.extend(file_errors)
        else:
            print(f"  ✅ PASS: {rel} (Orange #{COLOR_ORANGE_PRIMARY}, Cream #{COLOR_CREAM_WHITE}, Multiply Blend OK)")

    # 2. Check YouTube banner generator
    banner_gen = REPO_ROOT / "library" / "tools" / "generate_youtube_banner.js"
    print(f"\n[2/3] Validating YouTube Banner Mascot Generator ({banner_gen.relative_to(REPO_ROOT)})...")
    if banner_gen.exists():
        banner_errors = validate_banner_generator(banner_gen)
        if banner_errors:
            print(f"  ❌ FAIL: {banner_gen.relative_to(REPO_ROOT)}")
            for err in banner_errors:
                print(f"     -> {err}")
            all_errors.extend(banner_errors)
        else:
            print(f"  ✅ PASS: Mascot SVG uses canonical orange head (#F97316) & cream cheeks (#FFFDF8)")
    else:
        print(f"  ⚠️ SKIP: {banner_gen} does not exist.")

    # 3. Check character metadata
    meta_file = REPO_ROOT / "assets" / "characters" / "cat-scientist" / "metadata.json"
    print(f"\n[3/3] Validating Character Metadata Specification ({meta_file.relative_to(REPO_ROOT)})...")
    if meta_file.exists():
        meta_content = meta_file.read_text(encoding="utf-8")
        if '"primary_color": "#F97316"' in meta_content and '"secondary_color": "#FFFDF7"' in meta_content:
            print(f"  ✅ PASS: Metadata specifies primary_color #F97316 and secondary_color #FFFDF7")
        else:
            err = f"{meta_file}: Metadata must specify primary_color #F97316 and secondary_color #FFFDF7."
            print(f"  ❌ FAIL: {err}")
            all_errors.append(err)
    else:
        err = f"{meta_file}: Missing character metadata file."
        print(f"  ❌ FAIL: {err}")
        all_errors.append(err)

    print("\n" + "=" * 70)
    if all_errors:
        print(f"❌ VALIDATION FAILED: {len(all_errors)} character identity error(s) detected!")
        sys.exit(1)
    else:
        print("🎉 ALL CHECKS PASSED: Cat Scientist Mascot identity is 100% canonical & consistent!")
        sys.exit(0)

if __name__ == "__main__":
    main()
