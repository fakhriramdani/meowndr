"""Seam tests for TASK-02: EpisodeStore, baseline protection, path traversal, and soft-archival."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from studio_api.adapters.fake_adapter import InMemoryFakeAdapter
from studio_api.app import create_app


def _seed_episode(root: Path, slug: str, gate1: str = "APPROVED", gate2: str = "PENDING", stage: int = 6) -> Path:
    ep_dir = root / slug / "content_factory"
    ep_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "episode_id": slug,
        "niche": "science",
        "current_stage": stage,
        "status": "PENDING_USER_APPROVAL",
        "completed_stages": [2, 3, 4, 5],
        "approval_gates": {
            "gate_1_topic_hook": {"status": gate1, "selected_hook_id": "hook-1"},
            "gate_2_script": {"status": gate2},
            "gate_3_final_video": {"status": "PENDING"},
        },
        "artifacts": {},
        "last_updated": "2026-11-14T10:00:00+00:00",
    }
    (ep_dir / "workflow_state.json").write_text(json.dumps(state), encoding="utf-8")
    return ep_dir


def test_history_resume_at_gate2_and_soft_archival(tmp_path: Path) -> None:
    ep_dir = _seed_episode(tmp_path, "ep-paused-g2")
    client = TestClient(create_app(adapter=InMemoryFakeAdapter(tmp_path), episodes_root=tmp_path, require_auth=False))

    detail_res = client.get("/api/episodes/ep-paused-g2")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["gates"]["gate1"] == "APPROVED"
    assert detail["gates"]["gate2"] == "PENDING"
    assert detail["currentStage"] == 6
    assert detail["workflowMode"] == "DirectTopicMode"
    assert detail["ageCategory"] == "Umum"

    arch_res = client.post("/api/episodes/ep-paused-g2/archive", json={"confirmed": True})
    assert arch_res.status_code == 200
    assert arch_res.json()["isArchived"] is True

    default_list = client.get("/api/episodes").json()["episodes"]
    assert all(item["episodeSlug"] != "ep-paused-g2" for item in default_list)

    all_list = client.get("/api/episodes?includeArchived=true").json()["episodes"]
    assert any(item["episodeSlug"] == "ep-paused-g2" for item in all_list)
    assert (ep_dir / "workflow_state.json").exists()


def test_protected_baseline_episode_01_v4_rejects_mutations(tmp_path: Path) -> None:
    _seed_episode(tmp_path, "episode-01-v4", gate1="APPROVED", gate2="APPROVED", stage=12)
    client = TestClient(create_app(adapter=InMemoryFakeAdapter(tmp_path), episodes_root=tmp_path, require_auth=False))

    get_res = client.get("/api/episodes/episode-01-v4")
    assert get_res.status_code == 200
    assert get_res.json()["isBaselineProtected"] is True

    arch_res = client.post("/api/episodes/episode-01-v4/archive", json={"confirmed": True})
    assert arch_res.status_code == 409
    assert arch_res.json()["error"]["code"] == "BASELINE_PROTECTED"


def test_path_traversal_slug_rejected_with_400(tmp_path: Path) -> None:
    client = TestClient(create_app(adapter=InMemoryFakeAdapter(tmp_path), episodes_root=tmp_path, require_auth=False))
    res = client.get("/api/episodes/..%2F..%2Fetc")
    assert res.status_code in (400, 404)
    if res.status_code == 400:
        assert res.json()["error"]["code"] == "VALIDATION_ERROR"

    bad_slug = client.get("/api/episodes/Bad_Slug!")
    assert bad_slug.status_code == 400
    assert bad_slug.json()["error"]["code"] == "VALIDATION_ERROR"
