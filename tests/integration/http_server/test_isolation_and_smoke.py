"""Integration tests: import isolation + full endpoint smoke test."""
from __future__ import annotations
from pathlib import Path
import json
import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


def test_ac_http_16_import_isolation():
    """Static-source inspection — no simulation modules referenced."""
    server_root = Path("src/api/http_server")
    forbidden_prefixes = ["from src.foundation", "import src.foundation",
                          "from src.core", "import src.core",
                          "from src.orchestration", "import src.orchestration"]
    leaks = []
    for py_file in server_root.rglob("*.py"):
        text = py_file.read_text()
        for prefix in forbidden_prefixes:
            if prefix in text:
                leaks.append(f"{py_file}: {prefix}")
    assert not leaks, f"Import isolation violated: {leaks}"


def test_serve_main_importable():
    """Verify serve_main console script is importable."""
    from src.api.http_server import serve_main
    assert callable(serve_main)


@pytest.fixture
def populated_log_dir(tmp_path, monkeypatch):
    """Create a complete match dir + strategy files + mock static directory."""
    # Create match data (per 2026-04-24 layout: <data_dir>/matches/<match_dir>)
    match = tmp_path / "matches" / "match_test"
    match.mkdir(parents=True)
    (match / "events.jsonl").write_text(
        json.dumps({"tick": 0, "is_key_event": False, "ball_position": [50, 30], "score": {"team_a": 0, "team_b": 0}, "actions": []}) + "\n" +
        json.dumps({"tick": 1, "is_key_event": True, "event_type": "goal", "ball_position": [50, 30], "score": {"team_a": 1, "team_b": 0}, "actions": []}) + "\n"
    )
    (match / "meta.json").write_text(json.dumps({
        "match_id": "test", "tick_rate": 10, "duration_minutes": 90, "total_ticks": 2,
        "final_score": {"team_a": 1, "team_b": 0},
        "team_a_provider": "openai", "team_b_provider": "anthropic",
        "key_event_tick_indices": [1],
    }))

    # Per-match strategy snapshots — written by MatchLog.serialize() in
    # production; the smoke test seeds them inline alongside events.jsonl.
    (match / "strategy_team_a.py").write_text("def decide(s, c, h):\n    return Hold()")
    (match / "strategy_team_b.py").write_text("def decide(s, c, h):\n    return Hold()")

    # Mock static directory to prevent RuntimeError in create_app
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text("<!DOCTYPE html><html><body>Mock Index</body></html>")

    # Patch the _STATIC_DIR constant
    import src.api.http_server.app as app_module
    monkeypatch.setattr(app_module, "_STATIC_DIR", static_dir)

    return tmp_path


def test_full_smoke_all_endpoints(populated_log_dir):
    """Smoke test endpoints per spec: /, /api/health, /api/match, /api/match/ticks, /api/match/key-events, /api/strategy/team_{a,b}, /api/match/ticks/stream."""
    client = TestClient(create_app(log_dir=str(populated_log_dir)))

    # Root endpoint
    root = client.get("/")
    assert root.status_code == 200
    # Note: This returns FileResponse for index.html, so we can't check JSON

    # Health check
    health = client.get("/api/health")
    assert health.status_code == 200
    # Expect new extended format but with backward-compatible "status": "ok"
    health_data = health.json()
    assert health_data["status"] == "ok"  # backward compat
    assert health_data["ok"] is True      # new format
    assert "version" in health_data
    assert "timestamp" in health_data

    # Match metadata
    meta = client.get("/api/match")
    assert meta.status_code == 200
    assert meta.json()["match_id"] == "test"
    assert meta.json()["total_ticks"] == 2
    assert "meta_file_mtime" in meta.json()

    # Ticks (paginated)
    ticks = client.get("/api/match/ticks")
    assert ticks.status_code == 200
    response_data = ticks.json()
    assert response_data["total_ticks"] == 2
    assert len(response_data["ticks"]) == 2
    assert response_data["offset"] == 0
    assert response_data["limit"] == 500

    # Key events
    ke = client.get("/api/match/key-events")
    assert ke.status_code == 200
    ke_data = ke.json()
    assert ke_data["total_key_events"] == 1
    assert len(ke_data["key_events"]) == 1
    assert ke_data["key_events"][0]["is_key_event"] is True

    # Strategy team_a
    s_a = client.get("/api/strategy/team_a")
    assert s_a.status_code == 200
    s_a_data = s_a.json()
    assert s_a_data["team_id"] == "team_a"
    assert "decide" in s_a_data["source"]
    assert "Hold()" in s_a_data["source"]

    # Strategy team_b
    s_b = client.get("/api/strategy/team_b")
    assert s_b.status_code == 200
    s_b_data = s_b.json()
    assert s_b_data["team_id"] == "team_b"
    assert "decide" in s_b_data["source"]

    # Stream (completed match - should return match_complete event)
    stream = client.get("/api/match/ticks/stream")
    assert stream.status_code == 200
    stream_text = stream.text
    assert "match_complete" in stream_text
    assert "data: {" in stream_text  # JSON data events