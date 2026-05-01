"""Tests for GET /api/matches and DELETE /api/matches/<id> endpoints."""
import json
import shutil
import tempfile
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


@pytest.fixture
def temp_data_home():
    """Create temporary data home directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir).resolve()


@pytest.fixture
def app_with_temp_data(temp_data_home):
    """Create app with temporary data directory."""
    return create_app(log_dir=str(temp_data_home))


@pytest.fixture
def client(app_with_temp_data):
    """Create test client."""
    return TestClient(app_with_temp_data)


@pytest.fixture
def sample_meta():
    """Sample meta.json content."""
    return {
        "match_id": "test_match_001",
        "final_score": {"team_a": 2, "team_b": 1},
        "final_tick": 600,
        "tick_count": 540,
        "teams": {
            "team_a": [
                {"player_id": "team_a_0", "number": 1, "role": "GK"},
                {"player_id": "team_a_1", "number": 2, "role": "DEF"}
            ],
            "team_b": [
                {"player_id": "team_b_0", "number": 1, "role": "GK"},
                {"player_id": "team_b_1", "number": 2, "role": "DEF"}
            ]
        }
    }


def create_match_dir(data_home: Path, match_id: str, meta_content: dict, include_events: bool = True):
    """Helper to create a match directory with meta.json and optionally events.jsonl.

    Per the engine convention, match dirs are named `match_<id>/`.
    """
    match_dir = data_home / "matches" / f"match_{match_id}"
    match_dir.mkdir(parents=True, exist_ok=True)

    # Write meta.json
    meta_path = match_dir / "meta.json"
    with open(meta_path, 'w') as f:
        json.dump(meta_content, f)

    # Write events.jsonl if requested
    if include_events:
        events_path = match_dir / "events.jsonl"
        sample_events = [
            {"tick": 0, "actions": []},
            {"tick": 1, "actions": []},
            {"tick": 2, "actions": []}
        ]
        with open(events_path, 'w') as f:
            for event in sample_events:
                f.write(json.dumps(event) + '\n')


class TestGetMatches:
    """Tests for GET /api/matches endpoint."""

    def test_empty_matches_dir_returns_empty_array(self, client, temp_data_home):
        """GET /api/matches returns empty array when no matches dir exists."""
        response = client.get("/api/matches")
        assert response.status_code == 200
        assert response.json() == []

    def test_no_matches_returns_empty_array(self, client, temp_data_home):
        """GET /api/matches returns empty array when matches dir exists but is empty."""
        matches_dir = temp_data_home / "matches"
        matches_dir.mkdir(parents=True)

        response = client.get("/api/matches")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_matches_sorted_by_mtime_desc(self, client, temp_data_home, sample_meta):
        """GET /api/matches returns matches sorted by mtime descending."""
        # Create first match
        meta1 = sample_meta.copy()
        meta1["match_id"] = "older_match"
        create_match_dir(temp_data_home, "older_match", meta1)

        # Wait a bit to ensure different mtime
        time.sleep(0.01)

        # Create second match (newer)
        meta2 = sample_meta.copy()
        meta2["match_id"] = "newer_match"
        meta2["final_score"] = {"team_a": 3, "team_b": 0}
        create_match_dir(temp_data_home, "newer_match", meta2)

        response = client.get("/api/matches")
        assert response.status_code == 200

        matches = response.json()
        assert len(matches) == 2

        # Should be sorted by mtime desc (newer first)
        assert matches[0]["match_id"] == "newer_match"
        assert matches[1]["match_id"] == "older_match"

        # Check required fields
        for match in matches:
            assert "match_id" in match
            assert "final_score" in match
            assert "date_iso" in match
            assert "config_name" in match
            assert "seed" in match
            assert "duration_sec" in match
            assert "models" in match
            assert "strategies" in match

    def test_skips_in_progress_matches(self, client, temp_data_home, sample_meta):
        """GET /api/matches skips in-progress matches (events.jsonl present, meta.json absent)."""
        matches_dir = temp_data_home / "matches"

        # Create completed match
        create_match_dir(temp_data_home, "completed_match", sample_meta)

        # Create in-progress match (events.jsonl but no meta.json)
        in_progress_dir = matches_dir / "in_progress_match"
        in_progress_dir.mkdir(parents=True)
        events_path = in_progress_dir / "events.jsonl"
        with open(events_path, 'w') as f:
            f.write('{"tick": 0, "actions": []}\n')

        response = client.get("/api/matches")
        assert response.status_code == 200

        matches = response.json()
        assert len(matches) == 1
        assert matches[0]["match_id"] == "test_match_001"

    def test_tolerates_malformed_meta_json(self, client, temp_data_home, sample_meta):
        """GET /api/matches tolerates malformed meta.json (skips and continues)."""
        # Create good match
        create_match_dir(temp_data_home, "good_match", sample_meta)

        # Create match with malformed meta.json
        bad_match_dir = temp_data_home / "matches" / "bad_match"
        bad_match_dir.mkdir(parents=True, exist_ok=True)
        bad_meta_path = bad_match_dir / "meta.json"
        with open(bad_meta_path, 'w') as f:
            f.write("invalid json content")

        response = client.get("/api/matches")
        assert response.status_code == 200

        matches = response.json()
        assert len(matches) == 1
        assert matches[0]["match_id"] == "test_match_001"

    def test_extracts_seed_from_match_id(self, client, temp_data_home):
        """GET /api/matches extracts seed from match_id when present."""
        meta = {
            "match_id": "iter11v4_r6_seed600",
            "final_score": {"team_a": 1, "team_b": 2},
            "final_tick": 300,
            "tick_count": 270,
            "teams": {"team_a": [], "team_b": []}
        }
        create_match_dir(temp_data_home, "iter11v4_r6_seed600", meta)

        response = client.get("/api/matches")
        assert response.status_code == 200

        matches = response.json()
        assert len(matches) == 1
        assert matches[0]["seed"] == 600
        assert matches[0]["config_name"] == "iter11v4_r6"


class TestDeleteMatch:
    """Tests for DELETE /api/matches/<id> endpoint."""

    def test_delete_existing_match_returns_204(self, client, temp_data_home, sample_meta):
        """DELETE /api/matches/<id> removes the dir and returns 204."""
        create_match_dir(temp_data_home, "test_match", sample_meta)

        # Verify match exists
        match_dir = temp_data_home / "matches" / "match_test_match"
        assert match_dir.exists()

        response = client.delete("/api/matches/test_match")
        assert response.status_code == 204

        # Verify match was deleted
        assert not match_dir.exists()

    def test_delete_missing_match_returns_404(self, client, temp_data_home):
        """DELETE /api/matches/<missing> returns 404."""
        response = client.delete("/api/matches/nonexistent_match")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_delete_invalid_match_id_returns_400(self, client):
        """DELETE /api/matches/<bad-id> (invalid format) returns 400."""
        # Test with invalid characters
        response = client.delete("/api/matches/invalid@match#id")
        assert response.status_code == 422  # FastAPI validation error

    def test_delete_match_id_too_long_returns_400(self, client):
        """DELETE /api/matches/<long-id> returns 400 for IDs over 128 chars."""
        long_id = "a" * 129  # 129 characters
        response = client.delete(f"/api/matches/{long_id}")
        assert response.status_code == 422  # FastAPI validation error

    def test_delete_preserves_other_matches(self, client, temp_data_home, sample_meta):
        """DELETE /api/matches/<id> only deletes the specified match."""
        # Create multiple matches
        meta1 = sample_meta.copy()
        meta1["match_id"] = "match_1"
        create_match_dir(temp_data_home, "match_1", meta1)

        meta2 = sample_meta.copy()
        meta2["match_id"] = "match_2"
        create_match_dir(temp_data_home, "match_2", meta2)

        # Delete one match
        response = client.delete("/api/matches/match_1")
        assert response.status_code == 204

        # Verify only the specified match was deleted (engine convention: match_<id>)
        assert not (temp_data_home / "matches" / "match_match_1").exists()
        assert (temp_data_home / "matches" / "match_match_2").exists()

        # Verify the other match is still accessible
        response = client.get("/api/matches")
        matches = response.json()
        assert len(matches) == 1
        assert matches[0]["match_id"] == "match_2"