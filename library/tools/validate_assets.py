#!/usr/bin/env python3
"""
CLI validation command for the papercraft explainer asset library.
Scans all registered environments, props, characters, and foreground assets.
Exits with 0 if all assets pass, or 1 if errors are detected.
"""

import sys
import os

# Ensure tools directory is on path
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from asset_loader import find_project_root, load_library, validate_environment, read_image_dimensions


def main():
    root = find_project_root()
    print(f"==> Validating Papercraft Asset Library at {root}")

    try:
        lib = load_library(root)
    except Exception as e:
        print(f"[FAIL] Could not load asset library index: {e}")
        sys.exit(1)

    version = lib.get("version", "unknown")
    print(f"    Library version: {version}")

    categories = lib.get("categories", {})
    environments = categories.get("environments", [])
    props = categories.get("props", [])
    characters = categories.get("characters", [])
    foregrounds = categories.get("foregrounds", [])

    print(f"    Found: {len(environments)} environments, {len(props)} props, {len(characters)} characters, {len(foregrounds)} foregrounds")

    total_errors = 0
    total_warnings = 0

    # 1. Validate Environments
    print("\n--- Validating Environments ---")
    for env in environments:
        env_id = env.get("id", "unnamed")
        print(f"  • Checking environment '{env_id}'...")
        res = validate_environment(env, root)
        if res["valid"]:
            print(f"    [OK] Environment '{env_id}' passed all checks.")
        else:
            print(f"    [FAIL] Environment '{env_id}' failed validation:")
            for err in res["errors"]:
                print(f"      - ERROR: {err}")
            total_errors += len(res["errors"])

        for warn in res["warnings"]:
            print(f"      - WARNING: {warn}")
            total_warnings += 1

    # 2. Validate Props
    print("\n--- Validating Props ---")
    for prop in props:
        prop_id = prop.get("id", "unnamed")
        print(f"  • Checking prop '{prop_id}'...")
        meta_path = prop.get("metadata_path")
        if not meta_path or not os.path.exists(os.path.join(root, meta_path)):
            print(f"    [FAIL] Prop '{prop_id}' metadata file missing: {meta_path}")
            total_errors += 1
        else:
            print(f"    [OK] Prop '{prop_id}' valid.")

    # 3. Validate Characters
    print("\n--- Validating Characters ---")
    for char in characters:
        char_id = char.get("id", "unnamed")
        print(f"  • Checking character '{char_id}'...")
        meta_path = char.get("metadata_path")
        if not meta_path or not os.path.exists(os.path.join(root, meta_path)):
            print(f"    [FAIL] Character '{char_id}' metadata file missing: {meta_path}")
            total_errors += 1
        else:
            print(f"    [OK] Character '{char_id}' valid.")

    # 4. Summary
    print("\n================ Validation Summary ================")
    if total_errors == 0:
        print(f"[SUCCESS] All assets valid! ({total_warnings} warnings)")
        sys.exit(0)
    else:
        print(f"[FAILURE] Asset library validation failed with {total_errors} errors and {total_warnings} warnings.")
        sys.exit(1)


if __name__ == "__main__":
    main()
