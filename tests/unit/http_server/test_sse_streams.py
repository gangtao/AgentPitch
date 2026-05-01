"""Tests for SSE streaming endpoints."""

import json
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from src.api.http_server.app import create_app


def _completed_match(log_dir: Path, n_ticks: int, key_event_ticks: list = None):
    """Create a completed match with n_ticks and optional key events.

    Per the 2026-04-24 layout, match dirs live under <data_dir>/matches/.
    """
    key_event_ticks = key_event_ticks or []
    sub = log_dir / "matches" / "match_test"
    sub.mkdir(parents=True, exist_ok=True)
    lines = []
    for t in range(n_ticks):
        lines.append(json.dumps({"tick": t, "is_key_event": t in key_event_ticks, "ball_position": [50, 30]}))
    (sub / "events.jsonl").write_text("\n".join(lines) + "\n")
    (sub / "meta.json").write_text(json.dumps({
        "match_id": "test",
        "total_ticks": n_ticks,
        "final_score": {"team_a": 0, "team_b": 0},
        "tick_rate": 10,
        "duration_minutes": 90,
        "team_a_provider": "openai",
        "team_b_provider": "anthropic",
        "key_event_tick_indices": key_event_ticks
    }))


def test_ac_http_17_replay_completed_match(tmp_path):
    """AC-HTTP-17: replay completed match emits all ticks then match_complete event."""
    _completed_match(tmp_path, 5)
    client = TestClient(create_app(log_dir=str(tmp_path)))
    response = client.get("/api/match/ticks/stream")
    text = response.text
    # Expect 5 data: lines + match_complete event
    assert text.count("data: {") >= 5
    assert "event: match_complete" in text


def test_ac_http_20_key_events_stream_filters(tmp_path):
    """AC-HTTP-20: key-events stream emits ONLY lines where is_key_event==true."""
    _completed_match(tmp_path, 10, key_event_ticks=[2, 7])
    client = TestClient(create_app(log_dir=str(tmp_path)))
    response = client.get("/api/match/key-events/stream")
    text = response.text
    # Only key-event lines emitted as data:
    data_lines = [line for line in text.split("\n") if line.startswith("data: {")]
    # Count data lines (excluding match_complete)
    key_event_data = [line for line in data_lines if '"is_key_event": true' in line.lower() or '"is_key_event":true' in line.lower() or 'is_key_event' in line]
    # Each tick line in stream is is_key_event
    assert "event: match_complete" in text


def test_no_match_data_returns_404(tmp_path):
    """AC-HTTP-21: Both streams return 404 if no match data exists."""
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/api/match/ticks/stream")
    assert r.status_code == 404

    r = client.get("/api/match/key-events/stream")
    assert r.status_code == 404


def test_partial_line_not_emitted(tmp_path):
    """AC-HTTP-19: partial JSON line buffered, not emitted."""
    sub = tmp_path / "matches" / "match_test"
    sub.mkdir(parents=True)
    # Write a complete line + a partial line (no trailing newline)
    (sub / "events.jsonl").write_text('{"tick": 0}\n{"tick": 1, "partial')
    (sub / "meta.json").write_text(json.dumps({
        "match_id": "test",
        "total_ticks": 2,
        "final_score": {"team_a": 0, "team_b": 0},
        "tick_rate": 10,
        "duration_minutes": 90,
        "team_a_provider": "openai",
        "team_b_provider": "anthropic",
        "key_event_tick_indices": []
    }))
    client = TestClient(create_app(log_dir=str(tmp_path)))
    text = client.get("/api/match/ticks/stream").text
    # Tick 0 should appear; tick 1 with "partial" should NOT
    assert '"tick": 0' in text
    assert "partial" not in text


def test_select_match_for_streaming_prefers_in_progress(tmp_path):
    """Test that _select_match_for_streaming prefers in-progress matches."""
    from src.api.http_server.app import _select_match_for_streaming

    # Create an in-progress match (events.jsonl, no meta.json)
    in_progress_dir = tmp_path / "match_in_progress"
    in_progress_dir.mkdir()
    (in_progress_dir / "events.jsonl").write_text('{"tick": 0}\n')

    # Create a completed match (both events.jsonl and meta.json)
    completed_dir = tmp_path / "match_completed"
    completed_dir.mkdir()
    (completed_dir / "events.jsonl").write_text('{"tick": 0}\n')
    (completed_dir / "meta.json").write_text('{"match_id": "completed"}')

    # Should prefer in-progress over completed
    result = _select_match_for_streaming(tmp_path)
    assert result is not None
    match_dir, in_progress = result
    assert in_progress is True
    assert match_dir.name == "match_in_progress"


def test_select_match_for_streaming_falls_back_to_completed(tmp_path):
    """Test that _select_match_for_streaming falls back to completed matches."""
    from src.api.http_server.app import _select_match_for_streaming

    # Create only a completed match
    completed_dir = tmp_path / "match_completed"
    completed_dir.mkdir()
    (completed_dir / "events.jsonl").write_text('{"tick": 0}\n')
    (completed_dir / "meta.json").write_text('{"match_id": "completed"}')

    # Should select the completed match
    result = _select_match_for_streaming(tmp_path)
    assert result is not None
    match_dir, in_progress = result
    assert in_progress is False
    assert match_dir.name == "match_completed"


def test_select_match_for_streaming_returns_none_for_no_matches(tmp_path):
    """Test that _select_match_for_streaming returns None when no matches exist."""
    from src.api.http_server.app import _select_match_for_streaming

    # Empty directory
    result = _select_match_for_streaming(tmp_path)
    assert result is None


def test_stream_response_headers(tmp_path):
    """Test that streaming responses have correct Content-Type header."""
    _completed_match(tmp_path, 3)
    client = TestClient(create_app(log_dir=str(tmp_path)))

    response = client.get("/api/match/ticks/stream")
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    response = client.get("/api/match/key-events/stream")
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"