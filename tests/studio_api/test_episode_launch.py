"""Seam tests for TASK-03: TopicResearchMode & DirectTopicMode launch + Pydantic extra='forbid'."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from studio_api.adapters.fake_adapter import InMemoryFakeAdapter
from studio_api.app import create_app


def test_topic_research_mode_returns_five_ranked_cards(tmp_path: Path) -> None:
    client = TestClient(create_app(adapter=InMemoryFakeAdapter(tmp_path), episodes_root=tmp_path, require_auth=False))
    res = client.post("/api/trends/discover", json={"niche": "science", "ageCategory": "Dewasa Muda 18-35"})
    assert res.status_code == 200
    cards = res.json()["opportunities"]
    assert len(cards) == 5
    scores = [c["opportunityScore"] for c in cards]
    assert scores == sorted(scores, reverse=True)
    for c in cards:
        assert len(c["temporalCascade"]) == 6
        assert "Bagaimana jika" in c["premise"]


def test_topic_research_mode_missing_selector_returns_400(tmp_path: Path) -> None:
    client = TestClient(create_app(adapter=InMemoryFakeAdapter(tmp_path), episodes_root=tmp_path, require_auth=False))
    res = client.post("/api/trends/discover", json={"niche": "history", "ageCategory": ""})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "Niche and AgeCategory" in res.json()["error"]["message"]


def test_direct_topic_mode_happy_path_boundary_and_non_what_if_notice(tmp_path: Path) -> None:
    client = TestClient(create_app(adapter=InMemoryFakeAdapter(tmp_path), episodes_root=tmp_path, require_auth=False))

    bad_short = client.post(
        "/api/episodes",
        json={
            "workflowMode": "DirectTopicMode",
            "topic": "Apa",
            "niche": "geography",
            "ageCategory": "Remaja 13-17",
        },
    )
    assert bad_short.status_code == 400
    assert "5 and 200" in bad_short.json()["error"]["message"]

    bad_long = client.post(
        "/api/episodes",
        json={
            "workflowMode": "DirectTopicMode",
            "topic": "x" * 201,
            "niche": "geography",
            "ageCategory": "Remaja 13-17",
        },
    )
    assert bad_long.status_code == 400

    ok_res = client.post(
        "/api/episodes",
        json={
            "workflowMode": "DirectTopicMode",
            "topic": "Sejarah Kerajaan Majapahit",
            "niche": "history",
            "ageCategory": "Umum",
        },
    )
    assert ok_res.status_code == 202
    body = ok_res.json()
    assert "What-If Point of Divergence" in (body["episode"]["nonWhatIfNotice"] or "")
    time.sleep(0.15)


def test_pydantic_extra_forbid_rejects_unexpected_fields(tmp_path: Path) -> None:
    client = TestClient(create_app(adapter=InMemoryFakeAdapter(tmp_path), episodes_root=tmp_path, require_auth=False))
    res = client.post(
        "/api/trends/discover",
        json={"niche": "science", "ageCategory": "Umum", "isBaselineProtected": False},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"
