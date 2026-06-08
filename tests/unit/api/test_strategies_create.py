"""Tests for strategy creation endpoints (Phase 3c)."""
from __future__ import annotations

import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from src.api.http_server.app import create_app


def test_post_strategies_blank_template(tmp_path):
    """POST /api/strategies with no source creates strategy with default template."""
    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    client = TestClient(app)

    response = client.post("/api/strategies", json={
        "name": "test-strategy"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test-strategy"
    assert "modified_iso" in data
    assert data["size_bytes"] > 0
    assert data["line_count"] > 0

    # Check file was created with template
    strategy_file = tmp_path / "strategies" / "test-strategy.py"
    assert strategy_file.exists()
    content = strategy_file.read_text()
    assert "def decide(game_state, player_state, history):" in content
    assert 'return Hold()' in content
    assert '"""Strategy: test-strategy"""' in content


def test_post_strategies_custom_source(tmp_path):
    """POST /api/strategies with custom source uses provided content."""
    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    client = TestClient(app)

    custom_source = '''"""Custom strategy"""
def decide(game_state, player_state, history):
    return Move("forward")
'''

    response = client.post("/api/strategies", json={
        "name": "custom-strategy",
        "source": custom_source
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "custom-strategy"

    # Check file contains custom source
    strategy_file = tmp_path / "strategies" / "custom-strategy.py"
    assert strategy_file.exists()
    content = strategy_file.read_text()
    assert content == custom_source


def test_post_strategies_already_exists(tmp_path):
    """POST /api/strategies returns 409 if strategy already exists."""
    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    client = TestClient(app)

    # Create first strategy
    client.post("/api/strategies", json={"name": "existing"})

    # Try to create same name again
    response = client.post("/api/strategies", json={"name": "existing"})

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_post_strategies_invalid_name(tmp_path):
    """POST /api/strategies validates name format."""
    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    client = TestClient(app)

    # Test invalid characters
    response = client.post("/api/strategies", json={"name": "invalid/name"})
    assert response.status_code == 422

    # Test empty name
    response = client.post("/api/strategies", json={"name": ""})
    assert response.status_code == 422

    # Test too long name
    response = client.post("/api/strategies", json={
        "name": "a" * 65  # Max is 64
    })
    assert response.status_code == 422


def test_post_strategies_creates_directory(tmp_path):
    """POST /api/strategies creates strategies directory if it doesn't exist."""
    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    client = TestClient(app)

    # Strategies dir doesn't exist yet
    assert not (tmp_path / "strategies").exists()

    response = client.post("/api/strategies", json={"name": "first"})

    assert response.status_code == 201
    assert (tmp_path / "strategies").exists()
    assert (tmp_path / "strategies" / "first.py").exists()


def test_post_strategies_generate_requires_provider_and_model(tmp_path):
    """When provider/model are missing the endpoint must reject with 400 — the
    subprocess can't pick a default. (Schema accepts them as optional for
    historical reasons; this is the runtime check.)"""
    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    client = TestClient(app)

    response = client.post("/api/strategies/generate", json={
        "name": "generated-strategy",
        "prompt": "Create a defensive strategy",
        # provider + model omitted
    })

    assert response.status_code == 400
    assert "provider and model are required" in response.json()["detail"]


def test_post_strategies_generate_validates_payload(tmp_path):
    """POST /api/strategies/generate validates required fields.

    Note: `prompt` is OPTIONAL — empty/missing renders the USER INTENT
    fallback ("apply general best practices"). `name` and the runtime
    provider/model check are still required.
    """
    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    client = TestClient(app)

    # Missing name → schema-level 422
    response = client.post("/api/strategies/generate", json={
        "prompt": "Create a strategy"
    })
    assert response.status_code == 422

    # Invalid name format → schema-level 422
    response = client.post("/api/strategies/generate", json={
        "name": "invalid.name",
        "prompt": "Create a strategy",
        "provider": "openai",
        "model": "gpt-4o",
    })
    assert response.status_code == 422

    # Prompt over the schema cap → schema-level 422
    from src.api.http_server.strategy_create_payload import MAX_PROMPT_CHARS
    response = client.post("/api/strategies/generate", json={
        "name": "test",
        "prompt": "x" * (MAX_PROMPT_CHARS + 1),
        "provider": "openai",
        "model": "gpt-4o",
    })
    assert response.status_code == 422


def test_post_strategies_generate_accepts_long_tactical_prompt(tmp_path):
    """A multi-KB tactical profile (e.g. fifa2026/tactices/*.md, ~8-11K chars)
    must pass schema validation. Regression: the old 4096 cap rejected every
    shipped tactical profile with a 422 before the endpoint ran.

    Provider/model are omitted so the request stops at the runtime 400 check
    (provider+model required) — proving the prompt length cleared the schema.
    """
    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    client = TestClient(app)

    response = client.post("/api/strategies/generate", json={
        "name": "mexico",
        "prompt": "x" * 9000,  # larger than the largest tactical profile
    })
    # 400 (not 422) means the 9000-char prompt was accepted by the schema.
    assert response.status_code == 400
    assert "provider and model are required" in response.json()["detail"]


def test_validation_error_body_is_structured_and_logged(tmp_path, caplog):
    """A 422 returns FastAPI's structured detail list AND logs the detail
    server-side so operators can see *what* failed, not just the status line.
    """
    import logging
    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    client = TestClient(app)

    with caplog.at_level(logging.WARNING):
        response = client.post("/api/strategies/generate", json={
            "name": "bad name with spaces",  # fails the name pattern
            "prompt": "Create a strategy",
            "provider": "openai",
            "model": "gpt-4o",
        })

    assert response.status_code == 422
    body = response.json()
    # Detail must remain a structured list of {loc, msg, type} objects.
    assert isinstance(body["detail"], list)
    assert body["detail"], "validation detail list should not be empty"
    assert "msg" in body["detail"][0] and "loc" in body["detail"][0]
    # Backend logged the validation failure with path + detail.
    assert any(
        "/api/strategies/generate" in rec.getMessage()
        for rec in caplog.records
    )


def test_post_strategies_generate_invalid_language(tmp_path):
    """Invalid language value rejected at schema-validation time (422).

    Note: provider field now accepts any string (for custom provider support),
    so we test language field instead which still has Literal validation.
    """
    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    client = TestClient(app)

    response = client.post("/api/strategies/generate", json={
        "name": "test-strategy",
        "prompt": "Create a strategy",
        "provider": "openai",
        "model": "gpt-4o",
        "language": "invalid",
    })
    assert response.status_code == 422


def test_post_strategies_generate_subprocess_failure_returns_502(tmp_path, monkeypatch):
    """If the subprocess prints an `ok: false` JSON line, the endpoint forwards
    it as 502 with the error string. We mock the subprocess to fail with a
    no-key error (cheapest, doesn't touch the network)."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    client = TestClient(app)

    response = client.post("/api/strategies/generate", json={
        "name": "test-strategy",
        "prompt": "Create a strategy",
        "provider": "openai",
        "model": "gpt-4o",
    })
    assert response.status_code == 502
    body = response.json()
    assert body["ok"] is False
    assert "API key" in body["error"]