"""Tests for match config API endpoints."""
import json
import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
import yaml

from src.api.http_server.app import create_app


def _seed_team_yaml(teams_dir: Path, slug: str, display_name: str) -> None:
    """Write a minimal valid team YAML so match configs can reference it."""
    teams_dir.mkdir(parents=True, exist_ok=True)
    team_doc = {
        "team_id": slug,
        "name": display_name,
        "players": [
            {"role": "GK",  "save": 16},
            {"role": "DEF"},
            {"role": "DEF"},
            {"role": "MID"},
            {"role": "FWD"},
        ],
    }
    with open(teams_dir / f"{slug}.yaml", "w") as f:
        yaml.safe_dump(team_doc, f, default_flow_style=False)


@pytest.fixture
def temp_dir():
    """Create a temporary directory with sample configs and seeded team files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)

        # Create configs subdirectory
        configs_dir = temp_path / "configs"
        configs_dir.mkdir()

        # Seed team YAMLs referenced by the sample match configs (and by
        # subsequent PUT tests). The PUT handler validates that referenced
        # team slugs exist on disk before saving, so tests must seed first.
        teams_dir = configs_dir / "teams"
        _seed_team_yaml(teams_dir, "red", "Red Lions")
        _seed_team_yaml(teams_dir, "blue", "Blue Wolves")

        # Create sample match configs (now slug-based, not inline rosters)
        sample_config_1 = {
            "match": {
                "seed": 42,
                "tick_rate": 10,
                "duration_minutes": 5,
                "field_width": 100.0,
                "field_height": 60.0,
                "match_id": "test_match_1"
            },
            "simulation": {
                "goal_reset_ticks": 30,
                "half_time_pause_ticks": 60,
                "action_cooldown_ticks": 10
            },
            "output": {
                "log_dir": "./playtest/logs"
            },
            "team_a": "red",
            "team_b": "blue",
        }

        sample_config_2 = {
            "match": {
                "seed": 123,
                "tick_rate": 30,
                "duration_minutes": 10,
                "field_width": 120.0,
                "field_height": 80.0,
                "match_id": "test_match_2"
            },
            "simulation": {
                "goal_reset_ticks": 45,
                "half_time_pause_ticks": 90,
                "action_cooldown_ticks": 15
            },
            "output": {
                "log_dir": "./playtest/logs"
            },
            "team_a": "red",
            "team_b": "blue",
        }

        # Write configs to files (with different mtimes)
        config1_path = configs_dir / "match_5v5.yaml"
        config2_path = configs_dir / "match_3v3.yaml"

        with open(config1_path, 'w') as f:
            yaml.safe_dump(sample_config_1, f, default_flow_style=False)

        with open(config2_path, 'w') as f:
            yaml.safe_dump(sample_config_2, f, default_flow_style=False)

        yield temp_path


@pytest.fixture
def client(temp_dir):
    """Create test client with temporary directory."""
    app = create_app(str(temp_dir), seed_defaults=False)
    return TestClient(app)


def test_get_match_configs_list(client, temp_dir):
    """Test GET /api/config/match returns sorted list."""
    response = client.get("/api/config/match")
    assert response.status_code == 200

    configs = response.json()
    assert isinstance(configs, list)
    assert len(configs) == 2

    # Check structure
    config = configs[0]
    assert "name" in config
    assert "modified_iso" in config
    assert "summary" in config

    # Check summary structure
    summary = config["summary"]
    assert "tick_rate" in summary
    assert "duration_min" in summary
    assert "field_w" in summary
    assert "field_h" in summary
    assert "formation" in summary
    assert "players_per_team" in summary

    # Formation should have team_a and team_b
    assert "team_a" in summary["formation"]
    assert "team_b" in summary["formation"]


def test_get_match_config_single(client, temp_dir):
    """Test GET /api/config/match/<name> returns full payload."""
    response = client.get("/api/config/match/match_5v5")
    assert response.status_code == 200

    config = response.json()

    # Check main sections
    assert "match" in config
    assert "simulation" in config
    assert "output" in config
    assert "team_a" in config
    assert "team_b" in config

    # Check match section
    match_section = config["match"]
    assert match_section["seed"] == 42
    assert match_section["tick_rate"] == 10
    assert match_section["duration_minutes"] == 5
    assert match_section["field_width"] == 100.0
    assert match_section["field_height"] == 60.0
    assert match_section["match_id"] == "test_match_1"

    # Teams are slug strings, not inline rosters.
    assert config["team_a"] == "red"
    assert config["team_b"] == "blue"


def test_get_match_config_not_found(client, temp_dir):
    """Test GET /api/config/match/<missing> returns 404."""
    response = client.get("/api/config/match/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_put_match_config_new(client, temp_dir):
    """Test PUT /api/config/match/<new> creates new config."""
    new_config = {
        "match": {
            "seed": 999,
            "tick_rate": 20,
            "duration_minutes": 3,
            "field_width": 80.0,
            "field_height": 50.0,
            "match_id": "new_match"
        },
        "simulation": {
            "goal_reset_ticks": 25,
            "half_time_pause_ticks": 50,
            "action_cooldown_ticks": 8
        },
        "output": {
            "log_dir": "./test/logs"
        },
        "team_a": "red",
        "team_b": "blue",
    }

    response = client.put("/api/config/match/new_match", json=new_config)
    assert response.status_code == 200

    result = response.json()
    assert result["name"] == "new_match"
    assert result["created"] is True
    assert "modified_iso" in result

    # Verify file was created
    config_path = temp_dir / "configs" / "new_match.yaml"
    assert config_path.exists()

    # Verify content
    with open(config_path, 'r') as f:
        saved_data = yaml.safe_load(f)
    assert saved_data["match"]["seed"] == 999
    assert saved_data["team_a"] == "red"
    assert saved_data["team_b"] == "blue"


def test_put_match_config_update_existing(client, temp_dir):
    """Test PUT /api/config/match/<existing> overwrites."""
    updated_config = {
        "match": {
            "seed": 777,
            "tick_rate": 15,
            "duration_minutes": 7,
            "field_width": 90.0,
            "field_height": 55.0,
            "match_id": "updated_match"
        },
        "simulation": {
            "goal_reset_ticks": 35,
            "half_time_pause_ticks": 70,
            "action_cooldown_ticks": 12
        },
        "output": {
            "log_dir": "./updated/logs"
        },
        "team_a": "red",
        "team_b": "blue",
    }

    response = client.put("/api/config/match/match_5v5", json=updated_config)
    assert response.status_code == 200

    result = response.json()
    assert result["name"] == "match_5v5"
    assert result["created"] is False  # Existing file

    # Verify content was updated
    config_path = temp_dir / "configs" / "match_5v5.yaml"
    with open(config_path, 'r') as f:
        saved_data = yaml.safe_load(f)
    assert saved_data["match"]["seed"] == 777


def test_put_match_config_with_llm_provider_field_forbidden(client, temp_dir):
    """Test PUT /api/config/match/<name> with llm_provider field returns 422."""
    invalid_config = {
        "match": {
            "seed": 999,
            "tick_rate": 20,
            "duration_minutes": 3,
            "field_width": 80.0,
            "field_height": 50.0,
            "match_id": "invalid_match"
        },
        "simulation": {
            "goal_reset_ticks": 25,
            "half_time_pause_ticks": 50,
            "action_cooldown_ticks": 8
        },
        "output": {
            "log_dir": "./test/logs"
        },
        "team_a": "red",
        "team_b": "blue",
        "llm_provider": "openai"  # This should be rejected
    }

    response = client.put("/api/config/match/invalid", json=invalid_config)
    assert response.status_code == 422
    # FastAPI 422 returns a list of error dicts under "detail"
    errors = response.json()["detail"]
    assert any(
        ("extra" in err.get("msg", "").lower())
        or ("forbidden" in err.get("msg", "").lower())
        or ("not permitted" in err.get("msg", "").lower())
        or "llm_provider" in str(err.get("loc", []))
        for err in errors
    )


def test_put_match_config_invalid_name(client, temp_dir):
    """Test PUT /api/config/match/<bad-name> returns 422."""
    valid_config = {
        "match": {
            "seed": 999,
            "tick_rate": 20,
            "duration_minutes": 3,
            "field_width": 80.0,
            "field_height": 50.0,
            "match_id": "test"
        },
        "simulation": {},
        "output": {"log_dir": "./test"},
        "team_a": "red",
        "team_b": "blue",
    }

    # Test with invalid characters — `..` rejected by name regex (422).
    response = client.put("/api/config/match/bad..name", json=valid_config)
    assert response.status_code == 422

    # `/` in the name causes a route mismatch — FastAPI returns 404 (no
    # route at /api/config/match/bad/name). Either rejection mode is
    # acceptable; both prevent the bad write.
    response = client.put("/api/config/match/bad/name", json=valid_config)
    assert response.status_code in (404, 422)


def test_delete_match_config(client, temp_dir):
    """Test DELETE /api/config/match/<name> removes file."""
    # Verify file exists first
    config_path = temp_dir / "configs" / "match_5v5.yaml"
    assert config_path.exists()

    response = client.delete("/api/config/match/match_5v5")
    assert response.status_code == 204

    # Verify file was removed
    assert not config_path.exists()


def test_delete_match_config_idempotent(client, temp_dir):
    """Test DELETE /api/config/match/<name> is idempotent (returns 204 even if file already gone)."""
    # Delete non-existent file
    response = client.delete("/api/config/match/nonexistent")
    assert response.status_code == 204

    # Delete same file twice
    response1 = client.delete("/api/config/match/match_3v3")
    assert response1.status_code == 204

    response2 = client.delete("/api/config/match/match_3v3")
    assert response2.status_code == 204


def test_get_api_config_includes_match_configs(client, temp_dir):
    """Test GET /api/config includes match.configs array."""
    response = client.get("/api/config")
    assert response.status_code == 200

    data = response.json()
    assert "match" in data
    assert "configs" in data["match"]

    configs = data["match"]["configs"]
    assert isinstance(configs, list)
    assert len(configs) == 2

    # Should be same format as GET /api/config/match
    config = configs[0]
    assert "name" in config
    assert "modified_iso" in config
    assert "summary" in config


def test_put_match_config_auto_fills_output_when_omitted(client, temp_dir):
    """PUT auto-fills the `output` block when the UI omits it. The UI never
    edits output (the API always passes --log-dir to the CLI) but the engine's
    MatchConfig requires it, so the API writes a deterministic placeholder so
    the saved YAML stays loadable by direct CLI users.
    """
    # Arrange — minimal payload with NO `output` and NO `simulation` (Optional).
    payload = {
        "match": {
            "seed": 1, "tick_rate": 10, "duration_minutes": 5,
            "field_width": 100.0, "field_height": 60.0, "match_id": "no_output",
        },
        "team_a": "red",
        "team_b": "blue",
    }

    # Act
    resp = client.put("/api/config/match/no_output", json=payload)
    assert resp.status_code == 200, resp.text

    # Assert — saved YAML carries an `output.log_dir` even though the UI sent none.
    saved_path = temp_dir / "configs" / "no_output.yaml"
    with open(saved_path, "r") as f:
        on_disk = yaml.safe_load(f)
    assert "output" in on_disk, "API must auto-fill output so engine load_config() succeeds"
    assert "log_dir" in on_disk["output"]
    assert isinstance(on_disk["output"]["log_dir"], str)
    assert on_disk["output"]["log_dir"]  # non-empty
    # `simulation` was also omitted — exclude_none must keep it out of the YAML.
    assert "simulation" not in on_disk, (
        "Omitted simulation block must not be persisted (it is overlaid from "
        "global-defaults.yaml at match-start time)"
    )


def test_put_match_config_with_team_slugs(client, temp_dir):
    """Happy path: PUT with valid team slugs that exist on disk."""
    body = {
        "match": {
            "seed": 42, "tick_rate": 10, "duration_minutes": 5,
            "field_width": 60.0, "field_height": 40.0,
        },
        "team_a": "red",
        "team_b": "blue",
    }
    response = client.put("/api/config/match/test5v5", json=body)
    assert response.status_code == 200, response.text

    # Saved YAML stores slug strings, not inline rosters.
    saved_path = temp_dir / "configs" / "test5v5.yaml"
    with open(saved_path, "r") as f:
        on_disk = yaml.safe_load(f)
    assert on_disk["team_a"] == "red"
    assert on_disk["team_b"] == "blue"
    # Neither value should be a dict / contain a nested players list.
    assert isinstance(on_disk["team_a"], str)
    assert isinstance(on_disk["team_b"], str)


def test_put_match_config_rejects_missing_team_slug(client, temp_dir):
    """422 when a team slug does not exist on disk."""
    body = {
        "match": {
            "seed": 42, "tick_rate": 10, "duration_minutes": 5,
            "field_width": 60.0, "field_height": 40.0,
        },
        "team_a": "red",
        "team_b": "doesnotexist",
    }
    response = client.put("/api/config/match/test_missing", json=body)
    assert response.status_code == 422
    detail = response.json()["detail"]
    # The handler raises HTTPException with a plain string detail (not a list).
    assert "team_b" in detail
    assert "doesnotexist" in detail

    # File must NOT have been created.
    assert not (temp_dir / "configs" / "test_missing.yaml").exists()


def test_put_match_config_rejects_uppercase_team_slug(client, temp_dir):
    """422 when a team slug contains uppercase characters (pydantic regex)."""
    body = {
        "match": {
            "seed": 42, "tick_rate": 10, "duration_minutes": 5,
            "field_width": 60.0, "field_height": 40.0,
        },
        "team_a": "Red",  # uppercase — must be rejected
        "team_b": "blue",
    }
    response = client.put("/api/config/match/test_upper", json=body)
    assert response.status_code == 422
    errors = response.json()["detail"]
    # Pydantic 422 returns a list of {"loc": [...], "msg": ...} entries
    assert any("team_a" in str(err.get("loc", [])) for err in errors)
