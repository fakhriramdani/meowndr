#!/usr/bin/env python3
"""
Unified cross-platform CLI for papercraft-open (Linux, macOS, Windows, Docker).

Usage:
    papercraft doctor
    papercraft setup
    papercraft new-episode <slug> "<title>" [--topic ...] [--env ...]
    papercraft sync-kit <project_dir> [assets_dir]
    papercraft factory <init|status|approve|reject|validate|niches|trends> ...
    papercraft pipeline <validate|preview|bgm|render|qa|publish-kit|upload-gdrive|trend-research|run> ...
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from library.platform_utils import find_chrome, get_config_dir, get_repo_root, sync_kit


def _run_python_script(script_rel: str, argv: list[str]) -> int:
    root = get_repo_root()
    script = root / script_rel
    env = os.environ.copy()
    env.setdefault("PAPERCUT_LIB", str(root / "library"))
    prev_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{root}{os.pathsep}{prev_pp}" if prev_pp else str(root)
    proc = subprocess.run([sys.executable, str(script), *argv], cwd=str(root), env=env)
    return proc.returncode


def cmd_doctor() -> int:
    root = get_repo_root()
    print("=" * 60)
    print(f"  papercraft-open Doctor ({platform.system()} {platform.machine()})")
    print("=" * 60)
    print(f"• Repo Root:   {root}")
    print(f"• Config Dir:  {get_config_dir()}")
    print(f"• Python:      {sys.version.split()[0]} ({sys.executable})")

    checks = {
        "node": shutil.which("node"),
        "npm": shutil.which("npm.cmd" if os.name == "nt" else "npm"),
        "ffmpeg": shutil.which("ffmpeg"),
        "rclone": shutil.which("rclone"),
        "chrome": find_chrome(),
    }
    for name, path in checks.items():
        status = f"[OK] {path}" if path else "[MISSING]"
        print(f"• {name:<11}  {status}")

    tpl_nm = root / "library" / "papercut" / "template" / "node_modules"
    print(f"• template nm: {'[OK]' if tpl_nm.is_dir() else '[NOT INSTALLED - run: papercraft setup]'}")
    env_file = root / ".env"
    print(f"• .env file:   {'[OK]' if env_file.exists() else '[MISSING - copy from .env.example]'}")
    print("=" * 60)
    return 0


def cmd_setup() -> int:
    root = get_repo_root()
    env_file = root / ".env"
    env_example = root / ".env.example"
    if not env_file.exists() and env_example.exists():
        shutil.copy2(env_example, env_file)
        print(f"• Created {env_file} from .env.example")

    (root / "episodes").mkdir(exist_ok=True)
    (root / "out").mkdir(exist_ok=True)

    tpl_dir = root / "library" / "papercut" / "template"
    npm_cmd = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if npm_cmd and (tpl_dir / "package.json").exists():
        print(f"• Installing Remotion template dependencies in {tpl_dir}...")
        subprocess.run([npm_cmd, "ci", "--no-audit", "--no-fund"], cwd=str(tpl_dir), check=True)
    else:
        print("[WARN] npm not found; skipping Remotion template npm install.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__.strip())
        return 0

    sub = args[0]
    rest = args[1:]

    if sub == "doctor":
        return cmd_doctor()
    if sub == "setup":
        return cmd_setup()
    if sub == "new-episode":
        return _run_python_script("library/tools/scaffold_episode.py", rest)
    if sub == "sync-kit":
        if not rest:
            print("Usage: papercraft sync-kit <project_dir> [series_assets_dir]", file=sys.stderr)
            return 2
        sync_kit(Path(rest[0]), Path(rest[1]) if len(rest) > 1 else None)
        return 0
    if sub == "factory":
        return _run_python_script("library/content_factory/cli.py", rest)
    if sub == "pipeline":
        return _run_python_script("library/tools/production_pipeline.py", rest)

    print(f"Unknown subcommand: {sub}\n", file=sys.stderr)
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
