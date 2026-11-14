"""Seam tests for TASK-07: Gate 3 video Range stream, CloudArchive upload, failure preservation & idempotency."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from studio_api.adapters.fake_adapter import InMemoryFakeAdapter
from studio_api.app import create_app


def _advance_to_gate3(client: TestClient) -> str:
    res = client.post(
        "/api/episodes",
        json={
            "workflowMode": "DirectTopicMode",
            "topic": "Bagaimana jika seluruh lautan bumi mengering?",
            "niche": "geography",
            "ageCategory": "Umum",
        },
    )
    slug = res.json()["episode"]["episodeSlug"]
    for jid in [res.json()["jobId"]]:
        for _ in range(40):
            if client.get(f"/api/episodes/{slug}/jobs/{jid}").json()["status"] == "COMPLETED":
                break
            time.sleep(0.01)

    g1 = client.post(f"/api/episodes/{slug}/gates/1/approve", json={"hookId": "hook-1"})
    for _ in range(40):
        if client.get(f"/api/episodes/{slug}/jobs/{g1.json()['jobId']}").json()["status"] == "COMPLETED":
            break
        time.sleep(0.01)

    g2 = client.post(f"/api/episodes/{slug}/gates/2/approve", json={})
    for _ in range(50):
        if client.get(f"/api/episodes/{slug}/jobs/{g2.json()['jobId']}").json()["status"] == "COMPLETED":
            break
        time.sleep(0.01)
    return slug


def test_gate3_range_stream_upload_failure_preservation_and_idempotency(tmp_path: Path) -> None:
    adapter = InMemoryFakeAdapter(tmp_path, simulate_upload_failure=True, stage_delay_sec=0.005)
    client = TestClient(create_app(adapter=adapter, episodes_root=tmp_path, require_auth=False))
    slug = _advance_to_gate3(client)

    media_res = client.get(f"/api/episodes/{slug}/media/video", headers={"Range": "bytes=0-1023"})
    assert media_res.status_code == 206
    assert media_res.headers["Content-Range"].startswith("bytes 0-1023/")
    assert media_res.headers["Content-Type"] == "video/mp4"

    fail_up = client.post(f"/api/episodes/{slug}/gates/3/approve", json={})
    assert fail_up.status_code == 502
    assert fail_up.json()["error"]["code"] == "CLOUD_ARCHIVE_FAILED"
    assert client.get(f"/api/episodes/{slug}").json()["gates"]["gate3"] == "PENDING"

    adapter.simulate_upload_failure = False
    ok_up = client.post(f"/api/episodes/{slug}/gates/3/approve", json={})
    assert ok_up.status_code == 200
    assert ok_up.json()["gdriveDestination"].startswith("gdrive-new:Antigravity/Videos/")
    assert ok_up.json()["episode"]["gates"]["gate3"] == "APPROVED"

    dup_up = client.post(f"/api/episodes/{slug}/gates/3/approve", json={})
    assert dup_up.status_code == 409
    assert dup_up.json()["error"]["code"] == "ALREADY_ARCHIVED"
    assert adapter.upload_count[slug] == 1
