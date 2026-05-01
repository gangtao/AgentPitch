"""Integration tests for /api/leagues endpoints."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient


def _make_app(tmp_path: Path):
    """Create a test app instance with a temp data dir."""
    import os
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
    from src.api.http_server.app import create_app
    app = create_app(str(tmp_path), seed_defaults=False)
    return app


def _make_strategies(tmp_path: Path, names: list[str]) -> None:
    strategies_dir = tmp_path / "strategies"
    strategies_dir.mkdir(exist_ok=True)
    for name in names:
        (strategies_dir / f"{name}.py").write_text(
            "def decide(state, player_id, team_id): return {'action': 'hold'}",
            encoding="utf-8",
        )


def _make_config(tmp_path: Path, config_name: str = "5v5") -> None:
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir(exist_ok=True)
    (configs_dir / f"{config_name}.yaml").write_text(
        "simulation:\n  players_per_team: 5\n",
        encoding="utf-8",
    )


@pytest.fixture
def client(tmp_path):
    _make_config(tmp_path)
    _make_strategies(tmp_path, ["alpha", "beta", "gamma", "delta"])
    app = _make_app(tmp_path)
    return TestClient(app)


def test_list_leagues_empty_returns_list(client):
    response = client.get("/api/leagues")
    assert response.status_code == 200
    assert response.json() == []


def test_post_league_odd_team_count_returns_422(client):
    payload = {
        "name": "Test League",
        "config_name": "5v5",
        "num_rounds": 1,
        "strategies": ["alpha", "beta", "gamma"],  # 3 = odd
    }
    response = client.post("/api/leagues", json=payload)
    assert response.status_code == 422


def test_post_league_invalid_num_rounds_returns_422(client):
    payload = {
        "name": "Test League",
        "config_name": "5v5",
        "num_rounds": 3,
        "strategies": ["alpha", "beta", "gamma", "delta"],
    }
    response = client.post("/api/leagues", json=payload)
    assert response.status_code == 422


def test_post_league_missing_config_returns_404(client):
    payload = {
        "name": "Test League",
        "config_name": "nonexistent",
        "num_rounds": 1,
        "strategies": ["alpha", "beta", "gamma", "delta"],
    }
    response = client.post("/api/leagues", json=payload)
    assert response.status_code == 404


def test_post_league_valid_returns_201_with_league_id(client):
    payload = {
        "name": "Test League",
        "config_name": "5v5",
        "num_rounds": 1,
        "strategies": ["alpha", "beta", "gamma", "delta"],
    }
    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value.pid = 12345
        response = client.post("/api/leagues", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert "league_id" in body
    assert body["league_id"].startswith("league-")


def test_get_league_not_found_returns_404(client):
    response = client.get("/api/leagues/nonexistent-id")
    assert response.status_code == 404


def test_get_league_returns_league_json(client, tmp_path):
    payload = {
        "name": "My League",
        "config_name": "5v5",
        "num_rounds": 1,
        "strategies": ["alpha", "beta", "gamma", "delta"],
    }
    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value.pid = 12345
        create_resp = client.post("/api/leagues", json=payload)
    assert create_resp.status_code == 201
    league_id = create_resp.json()["league_id"]

    get_resp = client.get(f"/api/leagues/{league_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["league_id"] == league_id
    assert data["name"] == "My League"
    assert "matchdays" in data
    assert "standings" in data


def test_list_leagues_shows_created_league(client):
    payload = {
        "name": "Listed League",
        "config_name": "5v5",
        "num_rounds": 1,
        "strategies": ["alpha", "beta", "gamma", "delta"],
    }
    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value.pid = 12345
        client.post("/api/leagues", json=payload)

    response = client.get("/api/leagues")
    assert response.status_code == 200
    leagues = response.json()
    assert len(leagues) == 1
    assert leagues[0]["name"] == "Listed League"
