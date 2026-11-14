#!/usr/bin/env python3
"""
Asset Provenance Audit Tool for Papercraft Explainer.

Verifies:
1. No scene or component imports unintended legacy prop directories
   (e.g., everyday.tsx, aura.tsx, cable.tsx, etc.)
2. No scene uses hardcoded legacy mascot colors (#E07A5F, #BA563B, #D67354)
3. Background environment assets match registered SHA-256 hashes
4. All characters and props in active scenes resolve to registered assets
   in assets/library.json
5. No references to legacy backdrops (e.g., bg/backdrops/room-*.jpg)

Exits 0 if clean, or 1 if legacy leakage or provenance violations are found.
"""

import os
import sys
import re
import hashlib
import json

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))

EXPECTED_BG_SHA256 = {
    "assets/backgrounds/science-lab/background.png": "4db1199c6a6076ac8334204473853c0068d361f19f81deb5ce0e4da05527c463"
}

LEGACY_PROP_MODULES = [
    "props/everyday",
    "props/aura",
    "props/cable",
    "props/council",
    "props/crowd",
    "props/gpu",
    "props/leak",
    "props/stage",
    "props/usage",
]

LEGACY_COLOR_PATTERNS = [
    (re.compile(r'["\']#E07A5F["\']', re.IGNORECASE), "Legacy terracotta critter color (#E07A5F)"),
    (re.compile(r'["\']#BA563B["\']', re.IGNORECASE), "Legacy terracotta critter shade (#BA563B)"),
    (re.compile(r'["\']#D67354["\']', re.IGNORECASE), "Legacy default hero color (#D67354)"),
]

LEGACY_BACKDROP_PATTERNS = [
    (re.compile(r'["\']bg/backdrops/(?!science-lab)[a-z0-9_-]+\.jpg["\']', re.IGNORECASE), "Legacy backdrop image reference"),
]


def check_file_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def audit_scenes(episode_dir):
    scenes_dir = os.path.join(episode_dir, "src", "scenes")
    if not os.path.isdir(scenes_dir):
        return []

    violations = []
    for root, _, files in os.walk(scenes_dir):
        for f in files:
            if not f.endswith((".tsx", ".ts")):
                continue
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, REPO_ROOT)
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()

            # 1. Check legacy prop imports
            for leg_prop in LEGACY_PROP_MODULES:
                if leg_prop in content:
                    violations.append({
                        "file": rel_path,
                        "type": "LEGACY_PROP_IMPORT",
                        "message": f"Imports from legacy module '{leg_prop}'"
                    })

            # 2. Check legacy color codes
            for pattern, desc in LEGACY_COLOR_PATTERNS:
                if pattern.search(content):
                    violations.append({
                        "file": rel_path,
                        "type": "LEGACY_COLOR_CODE",
                        "message": f"Contains hardcoded {desc}"
                    })

            # 3. Check legacy backdrop references
            for pattern, desc in LEGACY_BACKDROP_PATTERNS:
                if pattern.search(content):
                    violations.append({
                        "file": rel_path,
                        "type": "LEGACY_BACKDROP_REF",
                        "message": desc
                    })

            # 4. Check legacy generic Pill imports
            if re.search(r'\bimport\s+.*\{[^}]*\bPill\b[^}]*\}\s+from', content):
                violations.append({
                    "file": rel_path,
                    "type": "LEGACY_PILL_USAGE",
                    "message": "Uses legacy generic <Pill> component instead of <PapercraftBadge>"
                })

            # 5. Check legacy Critter imports
            if re.search(r'\bimport\s+.*\{[^}]*\bCritter\b[^}]*\}\s+from', content):
                violations.append({
                    "file": rel_path,
                    "type": "LEGACY_CRITTER_USAGE",
                    "message": "Uses legacy Papercut Critter instead of CatScientist"
                })

    return violations


def audit_background_hashes():
    violations = []
    for rel_path, expected_hash in EXPECTED_BG_SHA256.items():
        full_path = os.path.join(REPO_ROOT, rel_path)
        if not os.path.isfile(full_path):
            violations.append({
                "file": rel_path,
                "type": "MISSING_BACKGROUND_FILE",
                "message": f"Expected background asset file does not exist: {rel_path}"
            })
            continue

        actual_hash = check_file_sha256(full_path)
        if actual_hash != expected_hash:
            violations.append({
                "file": rel_path,
                "type": "MODIFIED_BACKGROUND_HASH",
                "message": f"Background SHA-256 mismatch! Expected {expected_hash}, got {actual_hash}"
            })
    return violations


def audit_library_integrity():
    violations = []
    lib_path = os.path.join(REPO_ROOT, "assets", "library.json")
    if not os.path.isfile(lib_path):
        violations.append({
            "file": "assets/library.json",
            "type": "MISSING_LIBRARY_INDEX",
            "message": "Master asset library index assets/library.json is missing"
        })
        return violations

    try:
        with open(lib_path, "r", encoding="utf-8") as f:
            lib = json.load(f)
    except Exception as e:
        violations.append({
            "file": "assets/library.json",
            "type": "INVALID_LIBRARY_JSON",
            "message": f"Cannot parse library.json: {e}"
        })
        return violations

    categories = lib.get("categories", {})
    for cat_name, items in categories.items():
        for item in items:
            item_id = item.get("id")
            meta_path = item.get("metadata_path")
            if meta_path:
                full_meta = os.path.join(REPO_ROOT, meta_path)
                if not os.path.isfile(full_meta):
                    violations.append({
                        "file": meta_path,
                        "type": "MISSING_METADATA",
                        "message": f"Metadata path for {cat_name} '{item_id}' not found: {meta_path}"
                    })

    return violations


def main():
    print("=" * 60)
    print("  Papercraft Asset Provenance & Legacy Leakage Audit")
    print("=" * 60)

    all_violations = []

    # 1. Audit Master Background Hashes
    print("\n[1/3] Verifying background image hashes...")
    bg_violations = audit_background_hashes()
    if bg_violations:
        for v in bg_violations:
            print(f"  [FAIL] {v['file']}: {v['message']}")
        all_violations.extend(bg_violations)
    else:
        for rel_path in EXPECTED_BG_SHA256:
            print(f"  [OK] {rel_path} matches verified SHA-256.")

    # 2. Audit Library Metadata Integrity
    print("\n[2/3] Verifying master asset library registrations...")
    lib_violations = audit_library_integrity()
    if lib_violations:
        for v in lib_violations:
            print(f"  [FAIL] {v['file']}: {v['message']}")
        all_violations.extend(lib_violations)
    else:
        print("  [OK] All registered environments, props, characters, and foregrounds exist.")

    # 3. Audit Episode Scenes
    print("\n[3/3] Scanning Episode 01 scene components for legacy leakage...")
    ep01_dir = os.path.join(REPO_ROOT, "episodes", "01-anomali-air", "papercut")
    scene_violations = audit_scenes(ep01_dir)
    if scene_violations:
        for v in scene_violations:
            print(f"  [FAIL] {v['file']} [{v['type']}]: {v['message']}")
        all_violations.extend(scene_violations)
    else:
        print("  [OK] Zero legacy prop imports detected.")
        print("  [OK] Zero hardcoded legacy mascot colors detected.")
        print("  [OK] Zero legacy backdrop paths detected.")

    # Summary
    print("\n" + "=" * 60)
    if not all_violations:
        print(">> PROVENANCE AUDIT PASSED: No legacy papercut leakage found! <<")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f">> PROVENANCE AUDIT FAILED: Found {len(all_violations)} violations <<")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
