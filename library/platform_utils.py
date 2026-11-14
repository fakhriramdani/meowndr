"""Cross-platform utilities for papercraft-open (Linux, macOS, Windows, Docker)."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_lib_dir() -> Path:
    env_lib = os.environ.get("PAPERCUT_LIB")
    if env_lib and Path(env_lib).is_dir():
        return Path(env_lib).resolve()
    return Path(__file__).resolve().parent


def get_config_dir() -> Path:
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "papercraft-open"
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "papercraft-open"
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "papercraft-open"


def get_data_dir() -> Path:
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "papercraft-open"
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "papercraft-open"
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "papercraft-open"


def find_chrome() -> Optional[str]:
    """Locate Chrome or Chromium executable across Windows, macOS, and Linux."""
    env_chrome = os.environ.get("CHROME_PATH")
    if env_chrome and Path(env_chrome).exists():
        return env_chrome

    for cmd in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        found = shutil.which(cmd)
        if found:
            return found

    candidates = []
    system = platform.system()
    if system == "Windows":
        for env_var in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            base = os.environ.get(env_var)
            if base:
                candidates.extend([
                    Path(base) / "Google" / "Chrome" / "Application" / "chrome.exe",
                    Path(base) / "Chromium" / "Application" / "chrome.exe",
                    Path(base) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
                ])
    elif system == "Darwin":
        candidates.extend([
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        ])
    else:
        candidates.extend([
            Path("/usr/bin/google-chrome"),
            Path("/usr/bin/google-chrome-stable"),
            Path("/usr/bin/chromium"),
            Path("/usr/bin/chromium-browser"),
        ])

    for p in candidates:
        if p.exists():
            return str(p)
    return None


def copy_tree_merge(src: Path, dst: Path, ignore_names: Optional[set[str]] = None, overwrite: bool = True) -> None:
    """Pure-Python cross-platform replacement for rsync -a."""
    src = Path(src)
    dst = Path(dst)
    ignore_names = ignore_names or set()
    dst.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in ignore_names]
        rel = Path(root).relative_to(src)
        target_dir = dst / rel
        target_dir.mkdir(parents=True, exist_ok=True)
        for fname in files:
            if fname in ignore_names:
                continue
            s_file = Path(root) / fname
            d_file = target_dir / fname
            if overwrite or not d_file.exists():
                shutil.copy2(s_file, d_file)


def copy_tree_clean(src: Path, dst: Path, ignore_names: Optional[set[str]] = None) -> None:
    """Pure-Python replacement for rsync -a --delete."""
    src = Path(src)
    dst = Path(dst)
    if dst.exists() or dst.is_symlink():
        if dst.is_symlink():
            dst.unlink()
        else:
            shutil.rmtree(dst)
    copy_tree_merge(src, dst, ignore_names=ignore_names, overwrite=True)


def link_or_copy_file(src: Path, dst: Path, relative: bool = True) -> None:
    """Create a symlink if supported by the OS, otherwise fall back to copying."""
    src = Path(src)
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    try:
        target = os.path.relpath(src, dst.parent) if relative else str(src)
        dst.symlink_to(target)
    except OSError:
        shutil.copy2(src, dst)


def link_dir_or_junction(src_dir: Path, dst_dir: Path) -> bool:
    """Link a directory via symlink (POSIX) or NTFS junction (Windows). Returns True if linked."""
    src_dir = Path(src_dir).resolve()
    dst_dir = Path(dst_dir)
    if dst_dir.exists() or dst_dir.is_symlink():
        return True

    if platform.system() == "Windows":
        res = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dst_dir), str(src_dir)],
            capture_output=True,
            text=True,
        )
        return res.returncode == 0

    try:
        rel = os.path.relpath(src_dir, dst_dir.parent)
        dst_dir.symlink_to(rel, target_is_directory=True)
        return True
    except OSError:
        try:
            dst_dir.symlink_to(src_dir, target_is_directory=True)
            return True
        except OSError:
            return False


def sync_kit(project_dir: Path, series_assets_dir: Optional[Path] = None) -> int:
    """Pure-Python cross-platform replacement for library/papercut/sync_kit.sh."""
    lib_papercut = get_lib_dir() / "papercut"
    p = Path(project_dir).resolve()

    src_lib = p / "src" / "lib"
    (p / "public" / "bg" / "backdrops").mkdir(parents=True, exist_ok=True)
    (p / "public" / "bg" / "textures").mkdir(parents=True, exist_ok=True)
    (p / "public" / "assets").mkdir(parents=True, exist_ok=True)
    (p / "public" / "fonts").mkdir(parents=True, exist_ok=True)

    copy_tree_clean(lib_papercut / "kit", src_lib)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    (src_lib / "SYNCED.txt").write_text(
        f"synced from papercut/kit on {stamp}; do not edit here, edit the library and re-sync\n",
        encoding="utf-8",
    )

    grain_src = lib_papercut / "public" / "bg" / "grain.png"
    grain_dst = p / "public" / "bg" / "grain.png"
    if grain_src.exists() and not grain_dst.exists():
        shutil.copy2(grain_src, grain_dst)

    tex_src = lib_papercut / "public" / "bg" / "textures"
    if tex_src.is_dir():
        copy_tree_merge(tex_src, p / "public" / "bg" / "textures", overwrite=True)

    fonts_src = lib_papercut / "public" / "fonts"
    if fonts_src.is_dir():
        copy_tree_merge(fonts_src, p / "public" / "fonts", overwrite=True)

    if series_assets_dir and Path(series_assets_dir).is_dir():
        copy_tree_merge(Path(series_assets_dir).resolve(), p / "public", overwrite=True)

    ts_count = sum(1 for f in src_lib.rglob("*.ts*"))
    print(f"kit -> {src_lib} ({ts_count} files)")
    return ts_count
