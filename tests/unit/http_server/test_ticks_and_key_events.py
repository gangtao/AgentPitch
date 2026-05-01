"""Tests for /api/match/ticks and /api/match/key-events endpoints."""
import json
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from src.api.http_server.app import create_app


def _make_match_with_ticks(log_dir: Path, n_ticks: int, key_event_ticks: list[int] = None):
    """Helper to create a match directory with events.jsonl and meta.json.

    Per the 2026-04-24 layout, match dirs live under <data_dir>/matches/.
    """
    key_event_ticks = key_event_ticks or []
    sub = log_dir / "matches" / "match_test"
    sub.mkdir(parents=True, exist_ok=True)
    events_path = sub / "events.jsonl"
    lines = []
    for t in range(n_ticks):
        record = {
            "tick": t,
            "is_key_event": t in key_event_ticks,
            "ball_position": [50.0, 30.0],
            "score": {"team_a": 0, "team_b": 0},
            "actions": []
        }
        lines.append(json.dumps(record))
    events_path.write_text("\n".join(lines))
    meta = {
        "match_id": "test",
        "total_ticks": n_ticks,
        "tick_rate": 10,
        "duration_minutes": 90,
        "final_score": {"team_a": 0, "team_b": 0},
        "team_a_provider": "openai",
        "team_b_provider": "anthropic",
        "key_event_tick_indices": key_event_ticks
    }
    (sub / "meta.json").write_text(json.dumps(meta))


def test_ac_http_05_default_first_500(tmp_path):
    """AC-HTTP-05: GET /api/match/ticks (no params) returns first 500 ticks with offset=0, limit=500."""
    _make_match_with_ticks(tmp_path, 1000)
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/match/ticks")
    assert r.status_code == 200
    body = r.json()
    assert body["offset"] == 0
    assert body["limit"] == 500
    assert body["total_ticks"] == 1000
    assert len(body["ticks"]) == 500
    assert body["ticks"][0]["tick"] == 0
    assert body["ticks"][-1]["tick"] == 499


def test_ac_http_06_page_2_offset(tmp_path):
    """AC-HTTP-06: GET /api/match/ticks?offset=500&limit=500 returns ticks 500-999."""
    _make_match_with_ticks(tmp_path, 1000)
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/match/ticks?offset=500&limit=500")
    assert r.status_code == 200
    body = r.json()
    assert body["offset"] == 500
    assert body["limit"] == 500
    assert len(body["ticks"]) == 500
    assert body["ticks"][0]["tick"] == 500
    assert body["ticks"][-1]["tick"] == 999


def test_ac_http_07_offset_at_boundary_empty(tmp_path):
    """AC-HTTP-07: GET /api/match/ticks?offset=500 on a 500-tick match returns 200 with ticks: [], NOT 404."""
    _make_match_with_ticks(tmp_path, 500)
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/match/ticks?offset=500")
    assert r.status_code == 200
    body = r.json()
    assert body["ticks"] == []
    assert body["offset"] == 500
    assert body["limit"] == 500  # Default limit
    assert body["total_ticks"] == 500


def test_ac_http_08_limit_over_max_returns_422(tmp_path):
    """AC-HTTP-08: limit above the max (10000 as of 2026-04-22) returns 422.
    Cap was raised from 500 to 10000 to fit a full match (≥600 ticks) in
    one fetch — front-end couldn't paginate cleanly across half-time gaps."""
    _make_match_with_ticks(tmp_path, 100)
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/match/ticks?limit=10001")
    assert r.status_code == 422


def test_ac_http_09_key_events_filter(tmp_path):
    """AC-HTTP-09: /api/match/key-events returns ONLY ticks with is_key_event==true."""
    _make_match_with_ticks(tmp_path, 100, key_event_ticks=[10, 25, 60])
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/match/key-events")
    assert r.status_code == 200
    body = r.json()
    assert body["total_key_events"] == 3
    assert len(body["key_events"]) == 3
    assert all(t["is_key_event"] is True for t in body["key_events"])
    assert [t["tick"] for t in body["key_events"]] == [10, 25, 60]


def test_ac_http_10_zero_key_events_returns_200_empty(tmp_path):
    """AC-HTTP-10: When no ticks have is_key_event==true, returns 200 with total_key_events: 0, key_events: [], NOT 404."""
    _make_match_with_ticks(tmp_path, 100, key_event_ticks=[])
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/match/key-events")
    assert r.status_code == 200
    assert r.json() == {"total_key_events": 0, "key_events": []}


def test_no_match_404_for_both(tmp_path):
    """Both endpoints return 404 when no match directory exists."""
    client = TestClient(create_app(log_dir=str(tmp_path)))
    assert client.get("/api/match/ticks").status_code == 404
    assert client.get("/api/match/key-events").status_code == 404