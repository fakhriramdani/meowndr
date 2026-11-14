"""Seam tests for TASK-08: LiveLibraryAdapter contract, zero raw print(), and CLI compatibility."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from studio_api.adapters.pipeline_adapter import LiveLibraryAdapter, PipelinePort


def test_live_library_adapter_satisfies_pipeline_port(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    adapter = LiveLibraryAdapter(repo_root=repo_root, episodes_root=tmp_path)
    assert isinstance(adapter, PipelinePort)


def test_zero_raw_print_calls_in_studio_api() -> None:
    studio_api_dir = Path(__file__).resolve().parent.parent.parent / "studio_api"
    for py_file in studio_api_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        assert "print(" not in content, f"Raw print() found in {py_file}"


def test_cli_status_compatible_with_existing_episode() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    ep_slug = "science-01-manusia-dua-kali-lebih-tinggi"
    if not (repo_root / "episodes" / ep_slug / "content_factory" / "workflow_state.json").exists():
        return
    proc = subprocess.run(
        [sys.executable, "library/content_factory/cli.py", "status", ep_slug],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
