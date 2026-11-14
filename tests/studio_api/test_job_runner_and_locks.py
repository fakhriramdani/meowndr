"""Seam tests for TASK-06: BackgroundJobRunner, SSE stream, locks, pacing remediation, and retry."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from studio_api.adapters.fake_adapter import InMemoryFakeAdapter
from studio_api.app import create_app
from studio_api.errors import AppError
from studio_api.job_runner import EpisodeLockManager


def _prepare_at_gate2(client: TestClient) -> str:
    res = client.post(
        "/api/episodes",
        json={
            "workflowMode": "DirectTopicMode",
            "topic": "Bagaimana jika bulan menghilang malam ini?",
            "niche": "science",
            "ageCategory": "Umum",
        },
    )
    slug = res.json()["episode"]["episodeSlug"]
    j1 = res.json()["jobId"]
    for _ in range(40):
        if client.get(f"/api/episodes/{slug}/jobs/{j1}").json()["status"] == "COMPLETED":
            break
        time.sleep(0.01)
    g1 = client.post(f"/api/episodes/{slug}/gates/1/approve", json={"hookId": "hook-1"})
    j2 = g1.json()["jobId"]
    for _ in range(40):
        if client.get(f"/api/episodes/{slug}/jobs/{j2}").json()["status"] == "COMPLETED":
            break
        time.sleep(0.01)
    return slug


def test_lock_manager_rejects_concurrent_acquisition() -> None:
    locks = EpisodeLockManager()
    locks.acquire("ep-test", "render_pipeline")
    assert locks.is_locked("ep-test") is True
    try:
        locks.acquire("ep-test", "gate_3_upload")
        assert False, "Expected AppError 409 EPISODE_LOCKED"
    except AppError as exc:
        assert exc.status_code == 409
        assert exc.code == "EPISODE_LOCKED"
    finally:
        locks.release("ep-test")


def test_stages_7_to_11_sse_stream_has_unbuffered_header(tmp_path: Path) -> None:
    adapter = InMemoryFakeAdapter(tmp_path, stage_delay_sec=0.005)
    client = TestClient(create_app(adapter=adapter, episodes_root=tmp_path, require_auth=False))
    slug = _prepare_at_gate2(client)

    g2 = client.post(f"/api/episodes/{slug}/gates/2/approve", json={})
    assert g2.status_code == 202
    job_id = g2.json()["jobId"]

    with client.stream("GET", f"/api/episodes/{slug}/jobs/{job_id}/events") as sse:
        assert sse.status_code == 200
        assert sse.headers.get("X-Accel-Buffering") == "no"
        body = "".join(sse.iter_text())
    assert '"stage": 7' in body
    assert '"stage": 11' in body
    assert '"status": "COMPLETED"' in body


def test_stage9_pacing_overflow_routes_back_to_gate2(tmp_path: Path) -> None:
    adapter = InMemoryFakeAdapter(tmp_path, simulate_pacing_failure=True, stage_delay_sec=0.005)
    client = TestClient(create_app(adapter=adapter, episodes_root=tmp_path, require_auth=False))
    slug = _prepare_at_gate2(client)

    g2 = client.post(f"/api/episodes/{slug}/gates/2/approve", json={})
    job_id = g2.json()["jobId"]
    for _ in range(50):
        st = client.get(f"/api/episodes/{slug}/jobs/{job_id}").json()
        if st["status"] == "PACING_REMEDIATION":
            break
        time.sleep(0.01)
    assert st["status"] == "PACING_REMEDIATION"
    assert st["measuredDurationSec"] == 54.2
    assert st["gate"] == 2

    ep = client.get(f"/api/episodes/{slug}").json()
    assert ep["gates"]["gate2"] == "PENDING"
    assert 95 <= ep["narrationScript"]["wordCount"] <= 105


def test_stage8_failure_and_retry_resumes_without_rerunning_completed_stages(tmp_path: Path) -> None:
    adapter = InMemoryFakeAdapter(tmp_path, simulate_stage_failure_at=8, stage_delay_sec=0.005)
    client = TestClient(create_app(adapter=adapter, episodes_root=tmp_path, require_auth=False))
    slug = _prepare_at_gate2(client)

    g2 = client.post(f"/api/episodes/{slug}/gates/2/approve", json={})
    job_id = g2.json()["jobId"]
    for _ in range(50):
        st = client.get(f"/api/episodes/{slug}/jobs/{job_id}").json()
        if st["status"] == "FAILED":
            break
        time.sleep(0.01)
    assert st["status"] == "FAILED"
    assert adapter.executed_stages[slug] == [7, 8]

    adapter.simulate_stage_failure_at = None
    retry = client.post(f"/api/episodes/{slug}/stages/8/retry", json={})
    assert retry.status_code == 202
    retry_job = retry.json()["jobId"]
    for _ in range(50):
        st2 = client.get(f"/api/episodes/{slug}/jobs/{retry_job}").json()
        if st2["status"] == "COMPLETED":
            break
        time.sleep(0.01)
    assert st2["status"] == "COMPLETED"
    assert adapter.executed_stages[slug] == [7, 8, 8, 9, 10, 11]


def test_audit_failure_blocks_gate3(tmp_path: Path) -> None:
    adapter = InMemoryFakeAdapter(tmp_path, simulate_audit_failure=True, stage_delay_sec=0.005)
    client = TestClient(create_app(adapter=adapter, episodes_root=tmp_path, require_auth=False))
    slug = _prepare_at_gate2(client)

    g2 = client.post(f"/api/episodes/{slug}/gates/2/approve", json={})
    job_id = g2.json()["jobId"]
    for _ in range(50):
        st = client.get(f"/api/episodes/{slug}/jobs/{job_id}").json()
        if st["status"] == "FAILED":
            break
        time.sleep(0.01)
    assert st["status"] == "FAILED"

    g3 = client.post(f"/api/episodes/{slug}/gates/3/approve", json={})
    assert g3.status_code == 409
    assert g3.json()["error"]["code"] == "AUDIT_NOT_PASSED"
