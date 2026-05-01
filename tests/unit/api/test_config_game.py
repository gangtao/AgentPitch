"""Tests for config Game tab API endpoints."""

import json
import os
import tempfile
import yaml
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app
from src.api.http_server.game_config import GameConfig


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def client(temp_log_dir):
    """Create a test client with temporary log directory."""
    app = create_app(str(temp_log_dir))
    return TestClient(app)


def test_put_config_game_valid_body_returns_200(client, temp_log_dir):
    """Test PUT /api/config/game returns 200 on valid body."""
    payload = {
        "tick_rate": 20,
        "duration_minutes": 10,
        "field_width": 120.0,
        "field_height": 80.0
    }

    response = client.put("/api/config/game", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "updated_fields" in data
    assert "timestamp" in data
    assert set(data["updated_fields"]) >= set(payload.keys())


def test_put_config_game_out_of_range_returns_422(client):
    """Test PUT /api/config/game returns 422 on out-of-range values."""
    payload = {
        "tick_rate": 999,  # Max is 60
        "duration_minutes": 5
    }

    response = client.put("/api/config/game", json=payload)

    assert response.status_code == 422
    error_detail = response.json()["detail"]
    # Should contain field path information
    assert any("tick_rate" in str(error) for error in error_detail)


def test_put_config_game_persists_to_disk(client, temp_log_dir):
    """Test PUT /api/config/game persists data to disk."""
    payload = {
        "tick_rate": 15,
        "field_width": 90.0,
        "action_cooldown_ticks": 5
    }

    response = client.put("/api/config/game", json=payload)
    assert response.status_code == 200

    # Check file was written
    config_path = temp_log_dir / "global-defaults.yaml"
    assert config_path.exists()

    # Check contents
    with open(config_path, 'r') as f:
        saved_data = yaml.safe_load(f)

    assert saved_data["tick_rate"] == 15
    assert saved_data["field_width"] == 90.0
    assert saved_data["action_cooldown_ticks"] == 5


def test_get_config_round_trip(client, temp_log_dir):
    """Test round-trip via PUT then GET returns same values."""
    # First, save some values
    payload = {
        "tick_rate": 25,
        "duration_minutes": 8,
        "tackle_range": 2.5,
        "health_max": 150.0
    }

    put_response = client.put("/api/config/game", json=payload)
    assert put_response.status_code == 200

    # Then retrieve via GET /api/config
    get_response = client.get("/api/config")
    assert get_response.status_code == 200

    game_data = get_response.json()["game"]
    assert game_data["tick_rate"] == 25
    assert game_data["duration_minutes"] == 8
    assert game_data["tackle_range"] == 2.5
    assert game_data["health_max"] == 150.0


def test_get_config_returns_defaults_when_no_file(client, temp_log_dir):
    """Test GET /api/config returns defaults when no config file exists."""
    # Ensure no config file exists
    config_path = temp_log_dir / "global-defaults.yaml"
    assert not config_path.exists()

    response = client.get("/api/config")
    assert response.status_code == 200

    game_data = response.json()["game"]
    defaults = GameConfig()

    # Check a few key defaults
    assert game_data["tick_rate"] == defaults.tick_rate
    assert game_data["duration_minutes"] == defaults.duration_minutes
    assert game_data["field_width"] == defaults.field_width


def test_put_config_game_invalid_type_returns_422(client):
    """Test PUT /api/config/game returns 422 on invalid data types."""
    payload = {
        "tick_rate": "not_a_number",
        "duration_minutes": 5
    }

    response = client.put("/api/config/game", json=payload)
    assert response.status_code == 422


def test_put_config_game_partial_update(client, temp_log_dir):
    """Test PUT /api/config/game allows partial updates."""
    # Create initial config
    initial_config = GameConfig()
    config_path = temp_log_dir / "global-defaults.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.safe_dump(initial_config.model_dump(), f)

    # Update only one field
    payload = {"tick_rate": 35}

    response = client.put("/api/config/game", json=payload)
    assert response.status_code == 200

    # Verify the update
    get_response = client.get("/api/config")
    game_data = get_response.json()["game"]
    assert game_data["tick_rate"] == 35
    # Other fields should retain their defaults
    assert game_data["duration_minutes"] == initial_config.duration_minutes