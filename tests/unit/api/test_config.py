"""Test config endpoint implementation."""

import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


def test_api_config_returns_200_with_required_top_level_keys(tmp_path):
    """Config endpoint returns 200 with game, llm, storage, match keys."""
    # Arrange
    app = create_app(log_dir=str(tmp_path))
    client = TestClient(app)

    # Act
    response = client.get("/api/config")

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Verify all 4 top-level keys are present
    assert "game" in data
    assert "llm" in data
    assert "storage" in data
    assert "match" in data

    # Verify basic structure per ADR-0019 placeholder schema
    assert isinstance(data["game"], dict)
    assert isinstance(data["llm"], dict)
    assert isinstance(data["storage"], dict)
    assert isinstance(data["match"], dict)


def test_api_config_llm_section_has_required_shape():
    """LLM section has providers array and active field."""
    # Arrange
    app = create_app(log_dir="./logs")
    client = TestClient(app)

    # Act
    response = client.get("/api/config")

    # Assert
    assert response.status_code == 200
    data = response.json()

    llm_section = data["llm"]
    assert "providers" in llm_section
    assert isinstance(llm_section["providers"], list)
    assert "active" in llm_section
    # active can be None for placeholder


def test_api_config_storage_section_contains_data_home():
    """Storage section includes data_home path."""
    # Arrange
    test_log_dir = "/tmp/test_logs"
    app = create_app(log_dir=test_log_dir)
    client = TestClient(app)

    # Act
    response = client.get("/api/config")

    # Assert
    assert response.status_code == 200
    data = response.json()

    storage_section = data["storage"]
    assert "data_home" in storage_section
    assert storage_section["data_home"] == test_log_dir


def test_api_config_match_section_has_configs_array():
    """Match section has configs array (empty for placeholder)."""
    # Arrange
    app = create_app(log_dir="./logs")
    client = TestClient(app)

    # Act
    response = client.get("/api/config")

    # Assert
    assert response.status_code == 200
    data = response.json()

    match_section = data["match"]
    assert "configs" in match_section
    assert isinstance(match_section["configs"], list)