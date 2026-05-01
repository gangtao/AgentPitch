"""Tests for HTTP Server Story 002: Latest-match scan + GET /api/match."""
import json
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


def _make_match(log_dir: Path, match_id: str, mtime: float, meta: dict):
    """Helper to create a match directory with meta.json and specific mtime.

    Per the 2026-04-24 layout, match dirs live under <data_dir>/matches/.
    """
    sub = log_dir / "matches" / f"match_{match_id}"
    sub.mkdir(parents=True, exist_ok=True)
    meta_path = sub / "meta.json"
    meta_path.write_text(json.dumps(meta))
    os.utime(meta_path, (mtime, mtime))


def _meta_dict():
    """Standard meta.json structure for testing."""
    return {
        "match_id": "20260420_143021",
        "tick_rate": 10,
        "duration_minutes": 90,
        "total_ticks": 54000,
        "final_score": {"team_a": 2, "team_b": 1},
        "team_a_provider": "openai",
        "team_b_provider": "anthropic",
        "key_event_tick_indices": [312, 847],
    }


def test_ac_http_02_empty_log_dir_404(tmp_path):
    """AC-HTTP-02: When log_dir empty/no match dirs/no meta.json, /api/match returns 404."""
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/match")
    assert r.status_code == 404
    assert r.json()["error"] == "no_match_found"


def test_ac_http_03_latest_by_mtime(tmp_path):
    """AC-HTTP-03: When 2+ match dirs exist with meta.json, most recent mtime is selected."""
    _make_match(tmp_path, "20260420_143021", 1000.0, {**_meta_dict(), "match_id": "20260420_143021"})
    _make_match(tmp_path, "20260420_143022", 2000.0, {**_meta_dict(), "match_id": "20260420_143022"})
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/match")
    assert r.status_code == 200
    assert r.json()["match_id"] == "20260420_143022"


def test_ac_http_04_returns_correct_fields(tmp_path):
    """AC-HTTP-04: For valid meta.json, /api/match returns 200 with all required fields."""
    _make_match(tmp_path, "test_match", 1000.0, _meta_dict())
    client = TestClient(create_app(log_dir=str(tmp_path)))
    body = client.get("/api/match").json()
    required_fields = [
        "match_id", "tick_rate", "duration_minutes", "total_ticks",
        "final_score", "team_a_provider", "team_b_provider",
        "key_event_tick_indices", "meta_file_mtime"
    ]
    for key in required_fields:
        assert key in body, f"missing key: {key}"

    # Verify meta_file_mtime is present and is a number
    assert isinstance(body["meta_file_mtime"], (int, float))


def test_no_cache_rescans_per_request(tmp_path):
    """No cache: Adding a new match dir between two requests produces different responses."""
    client = TestClient(create_app(log_dir=str(tmp_path)))
    assert client.get("/api/match").status_code == 404
    _make_match(tmp_path, "first", 1000.0, _meta_dict())
    assert client.get("/api/match").status_code == 200


def test_directories_without_meta_ignored(tmp_path):
    """Directories WITHOUT meta.json are ignored."""
    (tmp_path / "match_no_meta").mkdir()
    client = TestClient(create_app(log_dir=str(tmp_path)))
    assert client.get("/api/match").status_code == 404


def test_mtime_tiebreaker_uses_lexicographic_dir_name(tmp_path):
    """When mtimes are equal, tiebreaker uses lexicographic dir name."""
    # Same mtime, different match IDs - lexicographically later should win
    _make_match(tmp_path, "20260420_143021", 1000.0, {**_meta_dict(), "match_id": "20260420_143021"})
    _make_match(tmp_path, "20260420_143022", 1000.0, {**_meta_dict(), "match_id": "20260420_143022"})
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/match")
    assert r.status_code == 200
    # Should pick the lexicographically later one (match_20260420_143022)
    assert r.json()["match_id"] == "20260420_143022"