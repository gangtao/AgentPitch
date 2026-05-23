"""Tests for /api/config/teams REST endpoints (Task E2)."""
import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
import yaml

from src.api.http_server.app import create_app


def _valid_team(team_id: str = "red", name: str = "Red Lions") -> dict:
    """Return a minimal valid TeamConfigPayload-shaped dict."""
    return {
        "team_id": team_id,
        "name": name,
        "players": [
            {"role": "GK", "save": 16, "name": "GK"},
            {"role": "DEF"},
            {"role": "DEF"},
            {"role": "MID"},
            {"role": "FWD"},
        ],
    }


@pytest.fixture
def temp_dir():
    """Provide an empty tmp data_home (no configs dir pre-created)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def client(temp_dir):
    """TestClient with seed_defaults=False so we control the data layout."""
    app = create_app(str(temp_dir), seed_defaults=False)
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/config/teams (list)
# ---------------------------------------------------------------------------

def test_list_teams_empty_when_dir_missing(client):
    """GET /api/config/teams returns {"teams": {}} when teams dir absent."""
    resp = client.get("/api/config/teams")
    assert resp.status_code == 200
    assert resp.json() == {"teams": {}}


def test_list_teams_populated(client, temp_dir):
    """GET /api/config/teams returns all teams keyed by slug."""
    teams_dir = temp_dir / "configs" / "teams"
    teams_dir.mkdir(parents=True)

    red = _valid_team("red", "Red Lions")
    blue = _valid_team("blue", "Blue Tigers")
    with open(teams_dir / "red.yaml", "w") as f:
        yaml.safe_dump(red, f)
    with open(teams_dir / "blue.yaml", "w") as f:
        yaml.safe_dump(blue, f)

    resp = client.get("/api/config/teams")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body["teams"].keys()) == {"red", "blue"}
    assert body["teams"]["red"]["name"] == "Red Lions"
    assert body["teams"]["blue"]["name"] == "Blue Tigers"


# ---------------------------------------------------------------------------
# GET /api/config/teams/{slug}
# ---------------------------------------------------------------------------

def test_get_team_happy_path(client, temp_dir):
    teams_dir = temp_dir / "configs" / "teams"
    teams_dir.mkdir(parents=True)
    payload = _valid_team("red", "Red Lions")
    with open(teams_dir / "red.yaml", "w") as f:
        yaml.safe_dump(payload, f)

    resp = client.get("/api/config/teams/red")
    assert resp.status_code == 200
    body = resp.json()
    assert body["team_id"] == "red"
    assert body["name"] == "Red Lions"
    assert len(body["players"]) == 5


def test_get_team_missing_returns_404(client):
    resp = client.get("/api/config/teams/nope")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# PUT /api/config/teams/{slug}
# ---------------------------------------------------------------------------

def test_put_team_creates_new(client, temp_dir):
    resp = client.put("/api/config/teams/red", json=_valid_team("red"))
    assert resp.status_code == 200
    body = resp.json()
    assert body["slug"] == "red"
    assert body["created"] is True
    assert "modified_iso" in body

    # File written
    saved = temp_dir / "configs" / "teams" / "red.yaml"
    assert saved.exists()
    with open(saved) as f:
        on_disk = yaml.safe_load(f)
    assert on_disk["team_id"] == "red"
    assert on_disk["name"] == "Red Lions"


def test_put_team_updates_existing(client, temp_dir):
    # First PUT creates
    resp1 = client.put("/api/config/teams/red", json=_valid_team("red", "Red Lions"))
    assert resp1.status_code == 200
    assert resp1.json()["created"] is True

    # Second PUT updates
    updated = _valid_team("red", "Red Dragons")
    resp2 = client.put("/api/config/teams/red", json=updated)
    assert resp2.status_code == 200
    body = resp2.json()
    assert body["slug"] == "red"
    assert body["created"] is False

    # Disk reflects new name
    saved = temp_dir / "configs" / "teams" / "red.yaml"
    with open(saved) as f:
        on_disk = yaml.safe_load(f)
    assert on_disk["name"] == "Red Dragons"


def test_put_team_400_when_team_id_mismatches_slug(client):
    payload = _valid_team("red", "Red Lions")
    resp = client.put("/api/config/teams/blue", json=payload)
    assert resp.status_code == 400
    assert "team_id" in resp.json()["detail"]


def test_put_team_422_when_too_few_players(client):
    bad = {
        "team_id": "red",
        "name": "Red",
        "players": [
            {"role": "GK", "save": 16},
            {"role": "DEF"},
        ],
    }
    resp = client.put("/api/config/teams/red", json=bad)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /api/config/teams/{slug}
# ---------------------------------------------------------------------------

def test_delete_team_happy_path(client, temp_dir):
    teams_dir = temp_dir / "configs" / "teams"
    teams_dir.mkdir(parents=True)
    with open(teams_dir / "red.yaml", "w") as f:
        yaml.safe_dump(_valid_team("red"), f)

    resp = client.delete("/api/config/teams/red")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"slug": "red", "deleted": True}
    assert not (teams_dir / "red.yaml").exists()


def test_delete_team_missing_returns_404(client):
    resp = client.delete("/api/config/teams/nope")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]


def test_delete_team_409_when_referenced_by_match_config(client, temp_dir):
    """DELETE should refuse with 409 when a match config references this slug."""
    teams_dir = temp_dir / "configs" / "teams"
    teams_dir.mkdir(parents=True)
    with open(teams_dir / "red.yaml", "w") as f:
        yaml.safe_dump(_valid_team("red"), f)

    # Create a match config that references team red
    configs_dir = temp_dir / "configs"
    match_yaml = {
        "team_a": "red",
        "team_b": "blue",
        "match": {"match_id": "example"},
    }
    with open(configs_dir / "example.yaml", "w") as f:
        yaml.safe_dump(match_yaml, f)

    resp = client.delete("/api/config/teams/red")
    assert resp.status_code == 409
    assert "referenced" in resp.json()["detail"]
    assert "example" in resp.json()["detail"]
    # Team file must still exist
    assert (teams_dir / "red.yaml").exists()
