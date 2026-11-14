"""Seam tests for TASK-04: Gate 1 (Topic & Hook) approval and bypass prevention."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from studio_api.adapters.fake_adapter import InMemoryFakeAdapter
from studio_api.app import create_app


def _launch_and_wait_for_gate1(client: TestClient) -> str:
    res = client.post(
        "/api/episodes",
        json={
            "workflowMode": "DirectTopicMode",
            "topic": "Bagaimana jika oksigen bumi naik dua kali lipat?",
            "niche": "science",
            "ageCategory": "Umum",
        },
    )
    assert res.status_code == 202
    slug = res.json()["episode"]["episodeSlug"]
    job_id = res.json()["jobId"]
    for _ in range(40):
        st = client.get(f"/api/episodes/{slug}/jobs/{job_id}").json()
        if st["status"] == "COMPLETED":
            break
        time.sleep(0.02)
    return slug


def test_gate1_requires_hook_selection_and_blocks_gate2_bypass(tmp_path: Path) -> None:
    client = TestClient(create_app(adapter=InMemoryFakeAdapter(tmp_path, stage_delay_sec=0.005), episodes_root=tmp_path, require_auth=False))
    slug = _launch_and_wait_for_gate1(client)

    bypass = client.post(f"/api/episodes/{slug}/gates/2/approve", json={})
    assert bypass.status_code == 409
    assert bypass.json()["error"]["code"] == "GATE_BYPASS_BLOCKED"

    missing_hook = client.post(f"/api/episodes/{slug}/gates/1/approve", json={"hookId": ""})
    assert missing_hook.status_code == 400
    assert "Select 1 of the 5 HookVariant" in missing_hook.json()["error"]["message"]

    ok_g1 = client.post(f"/api/episodes/{slug}/gates/1/approve", json={"hookId": "hook-2"})
    assert ok_g1.status_code == 202
    assert ok_g1.json()["episode"]["gates"]["gate1"] == "APPROVED"
    assert ok_g1.json()["episode"]["selectedHookId"] == "hook-2"
    time.sleep(0.05)
