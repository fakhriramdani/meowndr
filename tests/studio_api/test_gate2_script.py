"""Seam tests for TASK-05: Gate 2 (Script) 6-beat editor, pacing guard, and condensation."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from studio_api.adapters.fake_adapter import InMemoryFakeAdapter
from studio_api.app import create_app


def _advance_to_gate2(client: TestClient) -> str:
    res = client.post(
        "/api/episodes",
        json={
            "workflowMode": "DirectTopicMode",
            "topic": "Bagaimana jika gravitasi bumi hilang lima detik?",
            "niche": "science",
            "ageCategory": "Umum",
        },
    )
    slug = res.json()["episode"]["episodeSlug"]
    job1 = res.json()["jobId"]
    for _ in range(40):
        if client.get(f"/api/episodes/{slug}/jobs/{job1}").json()["status"] == "COMPLETED":
            break
        time.sleep(0.01)

    g1 = client.post(f"/api/episodes/{slug}/gates/1/approve", json={"hookId": "hook-1"})
    job2 = g1.json()["jobId"]
    for _ in range(40):
        if client.get(f"/api/episodes/{slug}/jobs/{job2}").json()["status"] == "COMPLETED":
            break
        time.sleep(0.01)
    return slug


def test_gate2_rejects_digits_and_pacing_ceiling_and_condenses_to_95_105(tmp_path: Path) -> None:
    client = TestClient(create_app(adapter=InMemoryFakeAdapter(tmp_path, stage_delay_sec=0.005), episodes_root=tmp_path, require_auth=False))
    slug = _advance_to_gate2(client)

    ep = client.get(f"/api/episodes/{slug}").json()
    beats = ep["narrationScript"]["beats"]
    assert ep["narrationScript"]["isCompliant"] is True

    # Inject raw numeric digits
    digit_beats = [dict(b) for b in beats]
    digit_beats[0]["text"] = "Bagaimana jika terjadi dalam 60 detik saja?"
    digit_res = client.put(f"/api/episodes/{slug}/script", json={"beats": digit_beats})
    assert digit_res.status_code == 422
    assert digit_res.json()["error"]["code"] == "SPOKEN_DIGITS_FORBIDDEN"

    # Expand past 50.0s (155 words)
    long_beats = [dict(b) for b in beats]
    long_beats[1]["text"] = " ".join(["oksigen"] * 130)
    long_res = client.put(f"/api/episodes/{slug}/script", json={"beats": long_beats})
    assert long_res.status_code == 422
    assert long_res.json()["error"]["code"] == "PACING_CEILING_EXCEEDED"

    # Condense script
    cond_res = client.post(f"/api/episodes/{slug}/script/condense", json={})
    assert cond_res.status_code == 200
    script = cond_res.json()["script"]
    assert 95 <= script["wordCount"] <= 105
    assert script["hasNumericDigits"] is False
    assert script["isCompliant"] is True
    assert client.get(f"/api/episodes/{slug}").json()["gates"]["gate2"] == "PENDING"

    g2_ok = client.post(f"/api/episodes/{slug}/gates/2/approve", json={})
    assert g2_ok.status_code == 202
    time.sleep(0.1)
