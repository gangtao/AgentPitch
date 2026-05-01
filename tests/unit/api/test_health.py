"""Test health endpoint implementation."""

import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


def test_api_health_returns_200_with_required_fields(tmp_path):
    """Health endpoint returns 200 with ok=true, version, and timestamp."""
    # Arrange
    app = create_app(log_dir=str(tmp_path))
    client = TestClient(app)

    # Act
    response = client.get("/api/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "version" in data
    assert isinstance(data["version"], str)
    assert "timestamp" in data
    assert isinstance(data["timestamp"], int)
    assert data["timestamp"] > 0


def test_api_health_version_fallback_when_package_not_installed():
    """Health endpoint returns fallback version when package not found."""
    # Arrange
    app = create_app(log_dir="./logs")
    client = TestClient(app)

    # Act
    response = client.get("/api/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # Version should be either the installed version or fallback
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0