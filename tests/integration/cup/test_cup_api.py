"""Integration tests for Strategy Cup API endpoints.

Covers GET/POST/DELETE /api/cups and supporting helpers.
All filesystem I/O uses pytest tmp_path; subprocess spawning is mocked.
"""
from __future__ import annotations

import json
import unittest.mock
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


# ───────────────────────────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────────────────────────

@pytest.fixture
def data_home(tmp_path: Path) -> Path:
    """Minimal data-home directory with required subdirectories."""
    dh = tmp_path / "data"
    (dh / "configs").mkdir(parents=True)
    (dh / "strategies").mkdir(parents=True)
    (dh / "matches").mkdir(parents=True)
    (dh / "cups").mkdir(parents=True)
    return dh


@pytest.fixture
def app(data_home: Path):
    """FastAPI app wired to the temp data_home."""
    return create_app(str(data_home), seed_defaults=False)


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


# ───────────────────────────────────────────────────────────────────
# Test: GET /api/cups on empty dir returns []
# ───────────────────────────────────────────────────────────────────

def test_get_cups_empty_returns_list(client):
    """GET /api/cups on an empty cups dir returns an empty JSON list."""
    # Act
    response = client.get("/api/cups")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


# ───────────────────────────────────────────────────────────────────
# Test: GET /api/cups/{cup_id} — not found returns 404
# ───────────────────────────────────────────────────────────────────

def test_get_cup_not_found_returns_404(client):
    """GET /api/cups/nonexistent returns 404."""
    # Act
    response = client.get("/api/cups/nonexistent-cup-id")

    # Assert
    assert response.status_code == 404


# ───────────────────────────────────────────────────────────────────
# Test: DELETE /api/cups/{cup_id} — not found returns 404
# ───────────────────────────────────────────────────────────────────

def test_delete_cup_not_found_returns_404(client):
    """DELETE /api/cups/nonexistent returns 404."""
    # Act
    response = client.delete("/api/cups/nonexistent-cup-id")

    # Assert
    assert response.status_code == 404


# ───────────────────────────────────────────────────────────────────
# Test: POST /api/cups — missing config returns 422 or 404
# ───────────────────────────────────────────────────────────────────

def test_post_cup_missing_config_returns_422_or_404(client, data_home: Path):
    """POST /api/cups with nonexistent config_name returns 404 (after validation passes)."""
    # Arrange — seed 4 strategy files so strategy validation passes
    strategies_dir = data_home / "strategies"
    strategy_names = ["alpha", "beta", "gamma", "delta"]
    for name in strategy_names:
        (strategies_dir / f"{name}.py").write_text(
            "def decide(s, c, h):\n    return Hold()", encoding="utf-8"
        )

    payload = {
        "name": "Test Cup",
        "config_name": "nonexistent-config",
        "bracket_size": 4,
        "strategies": strategy_names,
    }

    # Act
    response = client.post("/api/cups", json=payload)

    # Assert — config does not exist; validation passes but file lookup returns 404
    assert response.status_code == 404


# ───────────────────────────────────────────────────────────────────
# Test: POST /api/cups — strategy count mismatch returns 422
# ───────────────────────────────────────────────────────────────────

def test_post_cup_strategy_count_mismatch_returns_422(client, data_home: Path):
    """POST /api/cups where len(strategies) != bracket_size returns 422."""
    # Arrange — create a valid config
    config_path = data_home / "configs" / "5v5.yaml"
    config_path.write_text("match:\n  tick_rate: 10\n  duration_minutes: 5\n", encoding="utf-8")

    # Provide only 3 strategies for bracket_size=4 — mismatch
    payload = {
        "name": "Mismatched Cup",
        "config_name": "5v5",
        "bracket_size": 4,
        "strategies": ["alpha", "beta", "gamma"],  # 3 instead of 4
    }

    # Act
    response = client.post("/api/cups", json=payload)

    # Assert — Pydantic model_validator catches count mismatch at body parse time
    assert response.status_code == 422


# ───────────────────────────────────────────────────────────────────
# Test: POST /api/cups — happy path creates cup dir and returns cup_id
# ───────────────────────────────────────────────────────────────────

def test_post_cup_creates_cup_json(data_home: Path):
    """POST /api/cups with valid payload creates cup dir and returns cup_id."""
    # Arrange
    app = create_app(str(data_home), seed_defaults=False)
    client = TestClient(app)

    # Write a minimal 5v5.yaml config
    (data_home / "configs" / "5v5.yaml").write_text(
        "match:\n  tick_rate: 10\n  duration_minutes: 2\n", encoding="utf-8"
    )

    # Write 4 strategy files
    for name in ["alpha", "beta", "gamma", "delta"]:
        (data_home / "strategies" / f"{name}.py").write_text(
            "def decide(s, c, h):\n    return Hold()", encoding="utf-8"
        )

    payload = {
        "name": "Test Cup",
        "config_name": "5v5",
        "bracket_size": 4,
        "strategies": ["alpha", "beta", "gamma", "delta"],
    }

    # Act — mock subprocess.Popen to avoid actually running the cup
    with unittest.mock.patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value = unittest.mock.MagicMock(pid=12345)
        response = client.post("/api/cups", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "cup_id" in data

    # Verify cup.json was created on disk
    cup_id = data["cup_id"]
    cup_json_path = data_home / "cups" / f"cup_{cup_id}" / "cup.json"
    assert cup_json_path.exists()


# ───────────────────────────────────────────────────────────────────
# Test: GET /api/cups/{cup_id} — detail returns cup.json content
# ───────────────────────────────────────────────────────────────────

def test_get_cup_detail_returns_cup_data(data_home: Path):
    """GET /api/cups/{cup_id} returns the cup.json contents for an existing cup."""
    # Arrange — manually create a cup dir with cup.json
    cup_id = "cup-20260429-abc123"
    cup_d = data_home / "cups" / f"cup_{cup_id}"
    cup_d.mkdir(parents=True)
    cup_json = {
        "cup_id": cup_id,
        "name": "Spring Cup",
        "status": "completed",
        "bracket_size": 4,
        "teams": [],
        "rounds": [],
    }
    (cup_d / "cup.json").write_text(json.dumps(cup_json), encoding="utf-8")

    app = create_app(str(data_home), seed_defaults=False)
    client = TestClient(app)

    # Act
    response = client.get(f"/api/cups/{cup_id}")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["cup_id"] == cup_id
    assert body["name"] == "Spring Cup"
    assert body["status"] == "completed"
