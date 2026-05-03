"""Tests for strategy CRUD endpoints (GET /api/strategies/<name>, DELETE /api/strategies/<name>)."""

import tempfile
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from src.api.http_server.app import create_app


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def app_client(temp_dir):
    """Create a test client with temporary data directory."""
    app = create_app(log_dir=temp_dir, seed_defaults=False)
    return TestClient(app)


@pytest.fixture
def sample_strategy_file(temp_dir):
    """Create a sample strategy file for testing."""
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    strategy_content = '''def decide(game_state, player_state, history):
    """Sample strategy for testing."""
    # Simple hold strategy
    return Hold()
'''

    strategy_file = strategies_dir / "test_strategy.py"
    strategy_file.write_text(strategy_content, encoding='utf-8')
    return strategy_file


def test_get_strategy_success(app_client, sample_strategy_file):
    """Test GET /api/strategies/<name> returns strategy source and metadata."""
    response = app_client.get("/api/strategies/test_strategy")

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "test_strategy"
    assert "def decide(game_state, player_state, history):" in data["source"]
    assert data["size_bytes"] > 0
    assert data["line_count"] > 0
    assert "modified_iso" in data
    # ISO format check
    assert "T" in data["modified_iso"]
    assert data["modified_iso"].endswith("Z")


def test_get_strategy_not_found(app_client, temp_dir):
    """Test GET /api/strategies/<missing> returns 404."""
    # Ensure strategies directory exists but is empty
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    response = app_client.get("/api/strategies/nonexistent")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_strategy_invalid_name(app_client, temp_dir):
    """Test GET /api/strategies/<bad..name> returns 400."""
    # Ensure strategies directory exists
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    # Test various invalid name formats that can reach our endpoint
    # Note: Names with '/' will result in 404 because they don't match the route pattern
    # So we focus on names that can reach the endpoint but fail validation
    invalid_names = [
        "bad..name",          # Contains ..
        "bad:name",           # Contains :
        "bad*name",           # Contains *
        "bad?name",           # Contains ?
        "bad\"name",          # Contains "
        "bad<name",           # Contains <
        "bad>name",           # Contains >
        "bad|name",           # Contains |
        "a" * 65,            # Too long (>64 chars)
        "bad name",          # Contains space
    ]

    for invalid_name in invalid_names:
        response = app_client.get(f"/api/strategies/{invalid_name}")
        # These names should either return 400 (invalid format) or 404 (route not found)
        # Both are acceptable since they indicate the name is not valid
        assert response.status_code in [400, 404, 422], f"Name '{invalid_name}' should be rejected"
        if response.status_code == 400:
            assert "Invalid strategy name format" in response.json()["detail"]


def test_get_strategy_path_injection_protection(app_client, temp_dir):
    """Test that path injection attempts are blocked."""
    # Ensure strategies directory exists
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    # Create a file outside the strategies directory that we shouldn't be able to access
    secret_file = temp_dir / "secret.py"
    secret_file.write_text("SECRET_DATA = 'do not access'")

    # Attempt path traversal attacks
    path_injection_attempts = [
        "../secret",
        "..%2fsecret",
        "..%2f..%2fsecret",
        "%2e%2e%2fsecret",
    ]

    for attempt in path_injection_attempts:
        response = app_client.get(f"/api/strategies/{attempt}")
        # Should either be 400 (invalid name) or 404 (not found) - never 200
        assert response.status_code in [400, 404], f"Path injection '{attempt}' should be blocked"

        # Ensure we never get the secret data
        if response.status_code == 200:
            data = response.json()
            assert "SECRET_DATA" not in data.get("source", ""), f"Path injection '{attempt}' leaked data"


def test_delete_strategy_success(app_client, sample_strategy_file):
    """Test DELETE /api/strategies/<name> removes file and returns 204."""
    # Verify file exists
    assert sample_strategy_file.exists()

    response = app_client.delete("/api/strategies/test_strategy")

    assert response.status_code == 204
    assert response.content == b""  # No content for 204

    # Verify file is deleted
    assert not sample_strategy_file.exists()


def test_delete_strategy_not_found(app_client, temp_dir):
    """Test DELETE /api/strategies/<missing> returns 404."""
    # Ensure strategies directory exists but is empty
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    response = app_client.delete("/api/strategies/nonexistent")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_strategy_idempotent(app_client, sample_strategy_file):
    """Test DELETE on already-deleted strategy returns 404 (idempotent behavior)."""
    # Delete once
    response1 = app_client.delete("/api/strategies/test_strategy")
    assert response1.status_code == 204

    # Delete again - should return 404 since file no longer exists
    response2 = app_client.delete("/api/strategies/test_strategy")
    assert response2.status_code == 404


def test_delete_strategy_invalid_name(app_client, temp_dir):
    """Test DELETE /api/strategies/<bad..name> returns 400."""
    # Ensure strategies directory exists
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    response = app_client.delete("/api/strategies/bad..name")

    assert response.status_code in [400, 422]
    if response.status_code == 400:
        assert "Invalid strategy name format" in response.json()["detail"]


def test_strategy_line_count_calculation(app_client, temp_dir):
    """Test that line count includes all lines (including blank ones)."""
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    # Create strategy with empty lines
    strategy_content = '''def decide(game_state, player_state, history):
    """Strategy with empty lines."""

    # First line of logic

    # Second line of logic
    return Hold()

'''  # Ends with empty line

    strategy_file = strategies_dir / "line_count_test.py"
    strategy_file.write_text(strategy_content, encoding='utf-8')

    response = app_client.get("/api/strategies/line_count_test")

    assert response.status_code == 200
    data = response.json()

    # Should count all lines including blank ones: 5 non-empty + 3 blank = 8
    assert data["line_count"] == 8


def test_strategy_unicode_content(app_client, temp_dir):
    """Test strategy with unicode content."""
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    # Create strategy with unicode content
    strategy_content = '''def decide(game_state, player_state, history):
    """Stратегия с unicode символами."""
    # Comment with émoji: ⚽
    return Hold()
'''

    strategy_file = strategies_dir / "unicode_test.py"
    strategy_file.write_text(strategy_content, encoding='utf-8')

    response = app_client.get("/api/strategies/unicode_test")

    assert response.status_code == 200
    data = response.json()
    assert "unicode символами" in data["source"]
    assert "émoji: ⚽" in data["source"]


def test_strategies_directory_missing_graceful_404(app_client, temp_dir):
    """Test endpoints handle missing strategies directory gracefully."""
    # Don't create strategies directory at all

    response_get = app_client.get("/api/strategies/any_strategy")
    assert response_get.status_code == 404

    response_delete = app_client.delete("/api/strategies/any_strategy")
    assert response_delete.status_code == 404


def test_put_strategy_new_file_success(app_client, temp_dir):
    """Test PUT /api/strategies/<name> creates a new strategy file."""
    # Ensure strategies directory exists
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    strategy_source = '''def decide(game_state, player_state, history):
    """New strategy for testing."""
    return Hold()
'''

    response = app_client.put("/api/strategies/new_strategy", json={
        "source": strategy_source
    })

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "new_strategy"
    assert "modified_iso" in data
    assert data["size_bytes"] > 0
    assert data["line_count"] == 3  # def, docstring, return

    # Verify file was created
    strategy_file = strategies_dir / "new_strategy.py"
    assert strategy_file.exists()
    assert strategy_file.read_text(encoding='utf-8') == strategy_source


def test_put_strategy_overwrite_existing(app_client, sample_strategy_file):
    """Test PUT /api/strategies/<name> overwrites existing strategy file."""
    original_mtime = sample_strategy_file.stat().st_mtime

    new_source = '''def decide(game_state, player_state, history):
    """Updated strategy."""
    # New logic here
    return Hold()
'''

    response = app_client.put("/api/strategies/test_strategy", json={
        "source": new_source
    })

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "test_strategy"
    assert data["line_count"] == 4

    # Verify file was overwritten
    assert sample_strategy_file.read_text(encoding='utf-8') == new_source

    # Verify modification time changed
    new_mtime = sample_strategy_file.stat().st_mtime
    assert new_mtime > original_mtime


def test_put_strategy_missing_source_field(app_client, temp_dir):
    """Test PUT /api/strategies/<name> with missing source field returns 422."""
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    # Send request without source field
    response = app_client.put("/api/strategies/test_strategy", json={
        "not_source": "some code"
    })

    assert response.status_code == 422
    # Pydantic validation error format
    assert "source" in str(response.json())


def test_put_strategy_empty_source_field(app_client, temp_dir):
    """Test PUT /api/strategies/<name> with empty source field returns 422."""
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    response = app_client.put("/api/strategies/test_strategy", json={
        "source": ""
    })

    assert response.status_code == 422


def test_put_strategy_invalid_name_format(app_client, temp_dir):
    """Test PUT /api/strategies/<bad..name> returns 400."""
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    # Names that survive URL parsing (no `?`, `&`, `#`, `*`, `<`, `>`, `|`, `"`
    # which all get re-interpreted by URL routing or quoted differently). These
    # actually arrive at the handler as the path param and must be rejected.
    invalid_names = [
        "bad..name",
        "bad:name",
        "a" * 65,  # Too long
        "bad name",  # Contains space (URL decodes %20 → space)
    ]

    for invalid_name in invalid_names:
        response = app_client.put(f"/api/strategies/{invalid_name}", json={
            "source": "def decide(): return Hold()"
        })

        # Name validation should catch these
        assert response.status_code in [400, 404, 422], f"Name '{invalid_name}' should be rejected (got {response.status_code})"
        if response.status_code == 400:
            assert "Invalid strategy name format" in response.json()["detail"]


def test_put_strategy_round_trip_get(app_client, temp_dir):
    """Test PUT then GET returns the same source code."""
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    source_code = '''def decide(game_state, player_state, history):
    """Round-trip test strategy."""

    # Test unicode: émoji ⚽
    if player_state["has_ball"]:
        return Pass(target_id="team_a_2")
    else:
        return Run(direction=[1, 0])
'''

    # PUT the strategy
    put_response = app_client.put("/api/strategies/roundtrip_test", json={
        "source": source_code
    })
    assert put_response.status_code == 200

    # GET the strategy back
    get_response = app_client.get("/api/strategies/roundtrip_test")
    assert get_response.status_code == 200

    get_data = get_response.json()
    assert get_data["source"] == source_code
    assert get_data["name"] == "roundtrip_test"


def test_put_strategy_atomic_write_protection(app_client, temp_dir):
    """Test that atomic write leaves no `.tmp` files behind on failure.

    Mocks `os.replace` (the atomic-rename primitive used by
    `src.strategy_library._atomic_write_bytes` per ADR-0023) to fail and
    verifies the original file is untouched and no leftover temp files
    remain.
    """
    from unittest.mock import patch
    import os

    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)

    existing_file = strategies_dir / "existing_strategy.py"
    original_content = "def decide(): return Hold() # original"
    existing_file.write_text(original_content, encoding='utf-8')

    # Patch os.replace globally — strategy_library uses `os.replace(tmp, target)`.
    with patch.object(os, "replace", side_effect=OSError("simulated")):
        response = app_client.put("/api/strategies/existing_strategy", json={
            "source": "def decide(): return Hold() # new"
        })
        assert response.status_code >= 500, (
            f"Expected 5xx on rename failure, got {response.status_code}"
        )

    # Original file unchanged
    assert existing_file.read_text(encoding='utf-8') == original_content
    # No leftover temp files (.py.tmp or .meta.json.tmp)
    assert list(strategies_dir.glob("*.tmp")) == []


def test_put_strategy_creates_strategies_directory(app_client, temp_dir):
    """Test PUT creates strategies directory if it doesn't exist."""
    # Don't create strategies directory
    assert not (temp_dir / "strategies").exists()

    response = app_client.put("/api/strategies/test_strategy", json={
        "source": "def decide(): return Hold()"
    })

    assert response.status_code == 200

    # Verify directory was created
    strategies_dir = temp_dir / "strategies"
    assert strategies_dir.exists()
    assert strategies_dir.is_dir()

    # Verify file was created
    strategy_file = strategies_dir / "test_strategy.py"
    assert strategy_file.exists()

# ──────────────────────────────────────────────────────────────────────────────
# GET /api/strategies/llm-template — raw Jinja2 template for UI inspection
# ──────────────────────────────────────────────────────────────────────────────


def test_get_llm_template_default_returns_generation(app_client):
    """Default mode returns the generation template with content + version."""
    response = app_client.get("/api/strategies/llm-template")
    assert response.status_code == 200

    body = response.json()
    assert body["mode"] == "generation"
    assert body["filename"] == "generation.jinja2"
    assert body["version"]   # parsed from {# version: X #} comment
    assert body["size_bytes"] > 0
    assert "{# version:" in body["content"]
    # Section headers are the stable structural anchors that researchers
    # see when the panel is expanded. Generic v2.0+ template no longer
    # has {{...}} substitutions in generation; evolution still has two.
    assert "=== SECTION 1: CALLBACK CONTRACT ===" in body["content"]


def test_get_llm_template_evolution_mode(app_client):
    """Mode=evolution returns the evolution template."""
    response = app_client.get("/api/strategies/llm-template?mode=evolution")
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "evolution"
    assert body["filename"] == "evolution.jinja2"


def test_get_llm_template_unknown_mode_returns_400(app_client):
    """Mode that isn't generation/evolution → 400, not 500."""
    response = app_client.get("/api/strategies/llm-template?mode=garbage")
    assert response.status_code == 400
    assert "garbage" in response.json()["detail"]


def test_get_llm_template_route_wins_over_name_wildcard(app_client, temp_dir):
    """Regression: /api/strategies/{name} must not catch llm-template.

    A strategy literally named 'llm-template' would conflict — the static
    route is declared first specifically to win this race.
    """
    # Even with a strategy file named "llm-template", the template endpoint wins.
    strategies_dir = temp_dir / "strategies"
    strategies_dir.mkdir(exist_ok=True)
    (strategies_dir / "llm-template.py").write_text("def decide(): return Hold()")

    response = app_client.get("/api/strategies/llm-template")
    assert response.status_code == 200
    assert response.json()["filename"] == "generation.jinja2"
