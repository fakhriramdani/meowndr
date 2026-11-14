#!/usr/bin/env python3
"""
Repository Hygiene & Production Integrity Checker for @meowndr 2D Papercraft Explainer.

Guards against:
1. Heavy physical node_modules in episodes (enforces symlinks to template/node_modules, saving ~18GB).
2. Accidental nested directories (e.g. episodes/episodes).
3. Duplicate episode number prefixes.
4. Unwanted external agent platform files (.claude, .opencode, .rtk, CLAUDE.md).
5. Transient Remotion build and bundle directories (build/, .remotion/).
6. Windows NTFS / WSL Zone.Identifier artifact files.

Usage:
    python3 library/tools/repo_hygiene.py [--fix] [--strict]
"""

import os
import sys
import re
import shutil
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EPISODES_DIR = REPO_ROOT / "episodes"
TEMPLATE_NM = REPO_ROOT / "library" / "papercut" / "template" / "node_modules"


class HygieneChecker:
    def __init__(self, fix: bool = False, strict: bool = False):
        self.fix = fix
        self.strict = strict
        self.issues: List[Tuple[str, str]] = []  # (level, message)

    def log_pass(self, msg: str):
        print(f"  [PASS] {msg}")

    def log_warn(self, msg: str):
        self.issues.append(("WARN", msg))
        print(f"  [WARN] {msg}")

    def log_fail(self, msg: str):
        self.issues.append(("FAIL", msg))
        print(f"  [FAIL] {msg}")

    def check_node_modules_symlinks(self):
        print("\n--- 1. Checking Episode node_modules Symlink Integrity ---")
        if not EPISODES_DIR.exists():
            return

        physical_dirs = []
        broken_links = []
        correct_links = []

        for ep in sorted(EPISODES_DIR.iterdir()):
            if not ep.is_dir() or ep.name == "episodes":
                continue
            nm = ep / "papercut" / "node_modules"
            if not nm.exists() and not nm.is_symlink():
                continue
            if nm.is_symlink():
                target = nm.resolve()
                if not target.exists():
                    broken_links.append((ep.name, nm))
                else:
                    correct_links.append(ep.name)
            elif nm.is_dir():
                physical_dirs.append((ep.name, nm))

        if physical_dirs:
            self.log_fail(f"Found {len(physical_dirs)} physical node_modules folder(s) duplicating ~700MB each!")
            for name, p in physical_dirs:
                print(f"       - {name}: {p}")
                if self.fix:
                    print(f"         -> Fixing: replacing with symlink to template...")
                    shutil.rmtree(p)
                    rel_target = os.path.relpath(TEMPLATE_NM, p.parent)
                    nm.symlink_to(rel_target)
        else:
            self.log_pass(f"All {len(correct_links)} episode node_modules are lightweight symlinks (~15-18 GB saved).")

        if broken_links:
            self.log_warn(f"Found {len(broken_links)} broken node_modules symlink(s).")
            if self.fix:
                for name, p in broken_links:
                    p.unlink(missing_ok=True)
                    rel_target = os.path.relpath(TEMPLATE_NM, p.parent)
                    p.symlink_to(rel_target)
                    print(f"         -> Fixed broken symlink for {name}")

    def check_nested_episode_anomalies(self):
        print("\n--- 2. Checking for Recursive Episode Directory Nesting ---")
        nested = EPISODES_DIR / "episodes"
        if nested.exists():
            self.log_fail(f"Detected invalid recursive directory: {nested}")
            if self.fix:
                print(f"       -> Fixing: removing {nested}...")
                shutil.rmtree(nested)
        else:
            self.log_pass("No nested episodes/episodes directory found.")

    def check_duplicate_episode_numbers(self):
        print("\n--- 3. Checking for Duplicate Episode Number Prefixes ---")
        if not EPISODES_DIR.exists():
            return

        seen_prefixes = {}
        duplicates = []

        for ep in sorted(EPISODES_DIR.iterdir()):
            if not ep.is_dir() or ep.name == "episodes":
                continue
            m = re.match(r'^(\d+)', ep.name)
            if m:
                num = int(m.group(1))
                if num in seen_prefixes:
                    duplicates.append((num, seen_prefixes[num], ep.name))
                else:
                    seen_prefixes[num] = ep.name

        if duplicates:
            for num, first, second in duplicates:
                self.log_warn(f"Duplicate episode number prefix '{num:02d}': '{first}' and '{second}'")
        else:
            self.log_pass("All episode numbers are unique.")

    def check_external_platform_files(self):
        print("\n--- 4. Checking for Foreign Agent Platform Residues ---")
        forbidden = [
            REPO_ROOT / ".claude",
            REPO_ROOT / "CLAUDE.md",
            REPO_ROOT / ".opencode",
            REPO_ROOT / "opencode.jsonc",
            REPO_ROOT / ".rtk",
            REPO_ROOT / "agents",
        ]

        found = [p for p in forbidden if p.exists()]
        if found:
            self.log_fail(f"Found {len(found)} foreign agent platform configuration(s): {[p.name for p in found]}")
            if self.fix:
                for p in found:
                    print(f"       -> Fixing: removing {p}...")
                    if p.is_dir():
                        shutil.rmtree(p)
                    else:
                        p.unlink()
        else:
            self.log_pass("Clean agent platform state: Antigravity is the only active orchestrator.")

    def check_zone_identifier_files(self):
        print("\n--- 5. Checking for Windows Zone.Identifier Junk Files ---")
        zone_files = []
        for p in REPO_ROOT.rglob("*Zone.Identifier"):
            if ".git" not in p.parts:
                zone_files.append(p)

        if zone_files:
            self.log_warn(f"Found {len(zone_files)} Zone.Identifier artifact(s).")
            if self.fix:
                for z in zone_files:
                    z.unlink(missing_ok=True)
                print(f"       -> Fixing: deleted {len(zone_files)} Zone.Identifier file(s).")
        else:
            self.log_pass("No Windows Zone.Identifier artifact files detected.")

    def check_transient_build_dirs(self):
        print("\n--- 6. Checking for Leftover Remotion Build Artifacts ---")
        build_dirs = []
        for ep in EPISODES_DIR.iterdir():
            if not ep.is_dir():
                continue
            b = ep / "papercut" / "build"
            if b.exists() and b.is_dir():
                build_dirs.append(b)
            r = ep / "papercut" / ".remotion"
            if r.exists() and r.is_dir():
                build_dirs.append(r)

        if build_dirs:
            self.log_warn(f"Found {len(build_dirs)} transient build directory/ies consuming extra storage.")
            if self.fix:
                for b in build_dirs:
                    shutil.rmtree(b)
                print(f"       -> Fixing: cleaned {len(build_dirs)} transient build directory/ies.")
        else:
            self.log_pass("No leftover transient build artifacts found.")

    def check_redundant_skills_directory(self):
        print("\n--- 7. Checking for Redundant Root skills/ Directory ---")
        root_skills = REPO_ROOT / "skills"
        if root_skills.exists():
            self.log_fail("Redundant root 'skills/' directory detected! Antigravity loads skills exclusively from '.agents/skills/'.")
            if self.fix:
                shutil.rmtree(root_skills)
                print("       -> Fixing: deleted redundant root 'skills/' directory.")
        else:
            self.log_pass("No redundant root skills/ directory found (.agents/skills/ is single source of truth).")

    def check_duplicate_caption_directories(self):
        print("\n--- 8. Checking for Redundant Caption Subfolders ---")
        found = []
        for ep in EPISODES_DIR.iterdir():
            if not ep.is_dir():
                continue
            sub = ep / "publishing" / "captions"
            if sub.exists():
                found.append(sub)

        out_captions = REPO_ROOT / "output"
        if out_captions.exists():
            for ep_out in out_captions.iterdir():
                if ep_out.is_dir():
                    c_dir = ep_out / "captions"
                    if c_dir.exists():
                        found.append(c_dir)

        if found:
            self.log_fail(f"Found {len(found)} redundant caption subfolder(s) violating single source of truth.")
            if self.fix:
                for d in found:
                    shutil.rmtree(d)
                print(f"       -> Fixing: cleaned {len(found)} redundant caption subfolder(s).")
        else:
            self.log_pass("No duplicate caption subfolders found (episodes/<slug>/publishing/ is canonical).")

    def check_research_directory_hygiene(self):
        print("\n--- 9. Checking Research Directory Cleanliness ---")
        research_dir = REPO_ROOT / "research"
        if not research_dir.exists():
            return

        legacy_files = []
        for item in research_dir.iterdir():
            if item.is_file() and item.name.endswith(".json"):
                legacy_files.append(item)

        if legacy_files:
            self.log_warn(f"Found {len(legacy_files)} legacy/unmanaged JSON file(s) in research root: {[f.name for f in legacy_files]}")
            if self.fix:
                legacy_archive = REPO_ROOT / "archive" / "legacy_trends"
                legacy_archive.mkdir(parents=True, exist_ok=True)
                for f in legacy_files:
                    dest = legacy_archive / f.name
                    shutil.move(str(f), str(dest))
                    print(f"       -> Fixing: moved {f.name} to archive/legacy_trends/")
        else:
            self.log_pass("Research directory is clean (all intelligence housed in dated canonical directories).")

    def check_no_rogue_scripts_in_episodes(self):
        print("\n--- 10. Checking for Rogue Scripts in Episodes ---")
        if not EPISODES_DIR.exists():
            return

        rogue_scripts = []
        for ep in EPISODES_DIR.iterdir():
            if not ep.is_dir():
                continue
            for ext in ("*.py", "*.sh"):
                for p in ep.rglob(ext):
                    # Exclude node_modules if any
                    if "node_modules" not in p.parts:
                        rogue_scripts.append(p)

        if rogue_scripts:
            self.log_fail(f"Found {len(rogue_scripts)} rogue script(s) inside episodes/: {[str(p.relative_to(REPO_ROOT)) for p in rogue_scripts]}")
            if self.fix:
                legacy_voice_archive = REPO_ROOT / "archive" / "legacy_voice"
                legacy_voice_archive.mkdir(parents=True, exist_ok=True)
                for p in rogue_scripts:
                    dest = legacy_voice_archive / f"{p.parent.parent.name}_{p.name}"
                    shutil.move(str(p), str(dest))
                    print(f"       -> Fixing: moved {p.name} to archive/legacy_voice/")
        else:
            self.log_pass("No rogue Python or Shell scripts found inside episodes (tools are centrally located in library/).")

    def check_no_legacy_storyboard_markdown(self):
        print("\n--- 11. Checking for Legacy STORYBOARD.md Files ---")
        if not EPISODES_DIR.exists():
            return

        legacy_sb = []
        for ep in EPISODES_DIR.iterdir():
            if not ep.is_dir():
                continue
            for p in ep.rglob("STORYBOARD.md"):
                if "node_modules" not in p.parts:
                    legacy_sb.append(p)

        if legacy_sb:
            self.log_warn(f"Found {len(legacy_sb)} legacy STORYBOARD.md file(s): {[str(p.relative_to(REPO_ROOT)) for p in legacy_sb]}")
            if self.fix:
                archive_sb = REPO_ROOT / "archive" / "legacy_storyboards"
                archive_sb.mkdir(parents=True, exist_ok=True)
                for p in legacy_sb:
                    dest = archive_sb / f"{p.parent.parent.name}_{p.name}"
                    shutil.move(str(p), str(dest))
                    print(f"       -> Fixing: archived {p.name} to archive/legacy_storyboards/")
        else:
            self.log_pass("No legacy STORYBOARD.md files found (storyboard/storyboard.json is canonical).")

    def check_no_root_output_directory(self):
        print("\n--- 12. Checking for Redundant Root output/ Directory ---")
        root_output = REPO_ROOT / "output"
        if root_output.exists():
            self.log_fail("Detected root 'output/' directory duplicating rendered episode videos and captions!")
            if self.fix:
                shutil.rmtree(root_output)
                print("       -> Fixing: removed redundant root 'output/' directory.")
        else:
            self.log_pass("No duplicate root output/ directory found (episodes/<slug>/papercut/out/ is canonical).")

    def check_no_scratch_test_stills(self):
        print("\n--- 13. Checking for Scratch Test Stills & Inspections ---")
        if not EPISODES_DIR.exists():
            return

        scratch_items = []
        for ep in EPISODES_DIR.iterdir():
            if not ep.is_dir():
                continue
            out_dir = ep / "papercut" / "out"
            if not out_dir.exists():
                continue
            for item in out_dir.iterdir():
                if item.is_file() and (item.name.startswith("test_") or item.name.startswith("still_")):
                    scratch_items.append(item)
                elif item.is_dir() and item.name in ("inspections", "inspections_v2", "inspections_v4", "qa_frames", "stills"):
                    scratch_items.append(item)

        if scratch_items:
            self.log_warn(f"Found {len(scratch_items)} scratch test still(s) or inspection folder(s): {[item.name for item in scratch_items[:5]]}...")
            if self.fix:
                for item in scratch_items:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink(missing_ok=True)
                print(f"       -> Fixing: cleaned {len(scratch_items)} scratch test items.")
        else:
            self.log_pass("No scratch test stills or inspection folders lingering in episodes/*/papercut/out/.")

    def run_all(self) -> bool:
        print("=" * 70)
        print("  Meowndr Repository Hygiene & Production Integrity Audit")
        print("=" * 70)

        self.check_node_modules_symlinks()
        self.check_nested_episode_anomalies()
        self.check_duplicate_episode_numbers()
        self.check_external_platform_files()
        self.check_zone_identifier_files()
        self.check_transient_build_dirs()
        self.check_redundant_skills_directory()
        self.check_duplicate_caption_directories()
        self.check_research_directory_hygiene()
        self.check_no_rogue_scripts_in_episodes()
        self.check_no_legacy_storyboard_markdown()
        self.check_no_root_output_directory()
        self.check_no_scratch_test_stills()

        print("\n" + "=" * 70)
        fails = [msg for lvl, msg in self.issues if lvl == "FAIL"]
        warns = [msg for lvl, msg in self.issues if lvl == "WARN"]

        if fails:
            print(f"[FAILED] Repository hygiene check failed with {len(fails)} blocking issue(s) and {len(warns)} warning(s).")
            return False
        elif warns and self.strict:
            print(f"[FAILED STRICT] Repository hygiene check encountered {len(warns)} warning(s).")
            return False
        else:
            print(f"[PASSED] Repository hygiene check passed successfully ({len(warns)} non-blocking warnings).")
            return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Meowndr Repository Hygiene & Production Integrity Audit")
    parser.add_argument("--fix", action="store_true", help="Automatically fix detected issues")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as errors")
    args = parser.parse_args()

    checker = HygieneChecker(fix=args.fix, strict=args.strict)
    success = checker.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
