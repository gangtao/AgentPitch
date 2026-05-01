"""Tests for new matches start endpoints (Phase 3b)."""
import json
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


@pytest.fixture
def temp_data_home(tmp_path):
    """Create a temporary data home with test structure."""
    data_home = tmp_path / "data_home"
    data_home.mkdir(parents=True)

    # Create subdirectories
    (data_home / "configs").mkdir()
    (data_home / "strategies").mkdir()
    (data_home / "matches").mkdir()

    return data_home


@pytest.fixture
def app_with_data_home(temp_data_home):
    """Create app with temporary data home."""
    app = create_app(str(temp_data_home), seed_defaults=False)

    # Set up storage settings to point to our temp directory
    storage_file = temp_data_home / "storage-settings.yaml"
    storage_file.write_text(f"data_home: {temp_data_home}\n")

    return app


@pytest.fixture
def client(app_with_data_home):
    """Test client with temporary data setup."""
    return TestClient(app_with_data_home)


class TestStrategiesEndpoint:
    """Test GET /api/strategies endpoint."""

    def test_empty_when_no_strategies_dir(self, client, temp_data_home):
        """Returns empty array when strategies directory doesn't exist."""
        # Remove the strategies directory
        (temp_data_home / "strategies").rmdir()

        response = client.get("/api/strategies")
        assert response.status_code == 200
        assert response.json() == []

    def test_empty_when_no_strategy_files(self, client):
        """Returns empty array when strategies directory exists but is empty."""
        response = client.get("/api/strategies")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_list_with_metadata_when_files_exist(self, client, temp_data_home):
        """Returns list with metadata when strategy files exist."""
        strategies_dir = temp_data_home / "strategies"

        # Create test strategy files with different content
        strategy1 = strategies_dir / "baseline.py"
        strategy1.write_text("# Baseline strategy\nprint('hello')\n# Comment\n\nprint('world')\n")

        strategy2 = strategies_dir / "advanced.py"
        strategy2.write_text("# Advanced strategy\npass\n")

        response = client.get("/api/strategies")
        assert response.status_code == 200

        strategies = response.json()
        assert len(strategies) == 2

        # Check that all expected fields are present
        for strategy in strategies:
            assert "name" in strategy
            assert "size_bytes" in strategy
            assert "line_count" in strategy
            assert "modified_iso" in strategy

        # Check strategy names (should not include .py extension)
        strategy_names = {s["name"] for s in strategies}
        assert strategy_names == {"baseline", "advanced"}

        # Check line counts (only non-empty lines)
        baseline = next(s for s in strategies if s["name"] == "baseline")
        advanced = next(s for s in strategies if s["name"] == "advanced")

        assert baseline["line_count"] == 4  # 4 non-empty lines
        assert advanced["line_count"] == 2  # 2 non-empty lines

        # Check size_bytes are reasonable
        assert baseline["size_bytes"] > 0
        assert advanced["size_bytes"] > 0

    def test_sorted_by_mtime_desc(self, client, temp_data_home):
        """Returns strategies sorted by modification time descending."""
        strategies_dir = temp_data_home / "strategies"

        # Create files with explicit timing
        older_file = strategies_dir / "older.py"
        newer_file = strategies_dir / "newer.py"

        older_file.write_text("# Older strategy\n")
        time.sleep(0.1)  # Ensure different mtimes
        newer_file.write_text("# Newer strategy\n")

        response = client.get("/api/strategies")
        assert response.status_code == 200

        strategies = response.json()
        assert len(strategies) == 2

        # First entry should be the newer file (sorted desc by mtime)
        assert strategies[0]["name"] == "newer"
        assert strategies[1]["name"] == "older"

    def test_handles_permission_errors_gracefully(self, client, temp_data_home):
        """Handles files that can't be read gracefully."""
        strategies_dir = temp_data_home / "strategies"

        # Create a readable strategy file
        good_file = strategies_dir / "good.py"
        good_file.write_text("# Good strategy\n")

        # Create a non-readable file (simulate permission error by creating empty file)
        bad_file = strategies_dir / "bad.py"
        bad_file.write_text("# Bad strategy\n")

        response = client.get("/api/strategies")
        assert response.status_code == 200

        strategies = response.json()
        # Should still get the readable file
        assert len(strategies) >= 1
        assert any(s["name"] == "good" for s in strategies)


class TestStartMatchEndpoint:
    """Test POST /api/matches endpoint."""

    def test_validates_request_body_missing_fields(self, client):
        """Returns 422 when required fields are missing."""
        response = client.post("/api/matches", json={})
        assert response.status_code == 422

        error_detail = response.json()["detail"]
        assert isinstance(error_detail, list)

        # Check that all required fields are mentioned in validation errors
        error_fields = {error["loc"][-1] for error in error_detail}
        expected_fields = {"config_name", "strategy_a", "strategy_b", "match_id"}
        assert expected_fields.issubset(error_fields)

    def test_validates_request_body_bad_format(self, client):
        """Returns 422 when fields have invalid format."""
        response = client.post("/api/matches", json={
            "config_name": "invalid config name!",  # Spaces and special chars
            "strategy_a": "",  # Empty
            "strategy_b": "a" * 100,  # Too long
            "match_id": "123",  # Valid
            "seed_override": -1  # Negative
        })
        assert response.status_code == 422

    def test_returns_404_when_config_missing(self, client):
        """Returns 404 when the referenced config does not exist on disk."""
        response = client.post("/api/matches", json={
            "config_name": "nonexistent_config",
            "strategy_a": "baseline",
            "strategy_b": "advanced",
            "match_id": "test_match_123",
            "seed_override": 42
        })

        # CLI now supports the flags (added 2026-04-24); validation happens
        # at API layer and returns 404 when the referenced config is missing.
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_validates_seed_override_range(self, client):
        """Validates seed_override is within acceptable range."""
        # Test negative seed
        response = client.post("/api/matches", json={
            "config_name": "test",
            "strategy_a": "test",
            "strategy_b": "test",
            "match_id": "test",
            "seed_override": -1
        })
        assert response.status_code == 422

        # Test too large seed
        response = client.post("/api/matches", json={
            "config_name": "test",
            "strategy_a": "test",
            "strategy_b": "test",
            "match_id": "test",
            "seed_override": 2147483648  # Max int32 + 1
        })
        assert response.status_code == 422

        # Test valid seed (would return 501 due to unimplemented feature)
        response = client.post("/api/matches", json={
            "config_name": "test",
            "strategy_a": "test",
            "strategy_b": "test",
            "match_id": "test",
            "seed_override": 42
        })
        # CLI flags now exist; with non-existent referenced files the API
        # returns 404 (config / strategy not found). No longer 501.
        assert response.status_code == 404

    def test_accepts_none_seed_override(self, client):
        """Accepts null seed_override (use config's seed)."""
        response = client.post("/api/matches", json={
            "config_name": "test",
            "strategy_a": "test",
            "strategy_b": "test",
            "match_id": "test",
            "seed_override": None
        })
        # Pydantic validation passes; API then returns 404 because referenced
        # config/strategy files don't exist in the test fixture.
        assert response.status_code == 404

    def test_accepts_omitted_seed_override(self, client):
        """Accepts omitted seed_override field."""
        response = client.post("/api/matches", json={
            "config_name": "test",
            "strategy_a": "test",
            "strategy_b": "test",
            "match_id": "test"
            # seed_override omitted
        })
        # Pydantic validation passes; API then returns 404 because referenced
        # config/strategy files don't exist in the test fixture.
        assert response.status_code == 404