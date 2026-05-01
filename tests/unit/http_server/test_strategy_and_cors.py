"""Tests for /api/strategy/{team_id} viewer.

Strategy snapshots live in <matches_dir>/match_<id>/strategy_<team>.py
(written by MatchLog.serialize). The endpoint accepts an optional
?match_id=... query param; when omitted, falls back to the most recent
match (in-progress preferred, then latest completed) — same selection
rule as the live-viewer endpoints.
"""
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


def _seed_match(log_dir: Path, match_id: str, *, completed: bool = True) -> Path:
    """Create <log_dir>/matches/match_<id>/ with the sentinel files the
    match-resolver checks for. Returns the match_dir path so the caller
    can drop strategy files alongside.
    """
    match_dir = log_dir / "matches" / f"match_{match_id}"
    match_dir.mkdir(parents=True, exist_ok=True)
    (match_dir / "events.jsonl").write_text("")
    if completed:
        (match_dir / "meta.json").write_text("{}")
    return match_dir


def _write_strategy(match_dir: Path, team_id: str, source: str) -> None:
    (match_dir / f"strategy_{team_id}.py").write_text(source)


def test_strategy_returns_per_match_snapshot_verbatim(tmp_path):
    code = "def decide(s, c, h):\n    return Hold()"
    match_dir = _seed_match(tmp_path, "abc123")
    _write_strategy(match_dir, "team_a", code)

    client = TestClient(create_app(log_dir=str(tmp_path)))
    body = client.get("/api/strategy/team_a").json()

    assert body == {"team_id": "team_a", "source": code, "language": "python"}


def test_strategy_invalid_team_id_returns_422(tmp_path):
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/strategy/team_c")
    assert r.status_code == 422


def test_strategy_missing_match_returns_404(tmp_path):
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/strategy/team_a")
    assert r.status_code == 404
    assert "no_match_found" in str(r.json())


def test_strategy_missing_snapshot_returns_404(tmp_path):
    # Match dir exists but no strategy_team_a.py snapshot inside it.
    _seed_match(tmp_path, "abc123")
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/strategy/team_a")
    assert r.status_code == 404
    assert "resource_not_found" in str(r.json())


def test_strategy_team_b_per_match(tmp_path):
    match_dir = _seed_match(tmp_path, "abc123")
    _write_strategy(match_dir, "team_b", "def decide(s, c, h):\n    pass")
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/strategy/team_b")
    assert r.status_code == 200
    assert r.json()["team_id"] == "team_b"


def test_strategy_explicit_match_id_param(tmp_path):
    """When ?match_id is supplied, viewer returns THAT match's snapshot,
    not the most recent. Regression for the cross-match leak the global
    current.py path used to have.
    """
    older = _seed_match(tmp_path, "older")
    _write_strategy(older, "team_a", "older code")
    newer = _seed_match(tmp_path, "newer")
    _write_strategy(newer, "team_a", "newer code")

    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/strategy/team_a", params={"match_id": "older"})

    assert r.status_code == 200
    assert r.json()["source"] == "older code"


def test_strategy_cors_get_allowed(tmp_path):
    match_dir = _seed_match(tmp_path, "abc123")
    _write_strategy(match_dir, "team_a", "ok")
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get(
        "/api/strategy/team_a",
        headers={"Origin": "http://localhost:8000"},
    )
    assert r.status_code == 200
    assert "access-control-allow-origin" in {k.lower() for k in r.headers}
