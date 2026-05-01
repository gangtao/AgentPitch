"""Tests for HTTP Story 001: scaffold + health + static."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(create_app())


def test_ac_http_01_health_always_ok(client):
    """AC-HTTP-01: GET /api/health returns 200 {"status": "ok"} (plus additional fields allowed)."""
    r = client.get("/api/health")
    assert r.status_code == 200
    response_data = r.json()
    assert response_data["status"] == "ok"  # Required field per AC-HTTP-01


def test_ac_http_15_health_content_type(client):
    """AC-HTTP-15: /api/health is application/json."""
    r = client.get("/api/health")
    assert r.headers["content-type"].startswith("application/json")


def test_root_serves_index_html(client):
    """Root endpoint serves index.html as text/html."""
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_serve_main_importable():
    """serve_main is importable from http_server package."""
    from src.api.http_server import serve_main
    assert callable(serve_main)


def test_create_app_returns_fastapi():
    """create_app returns a FastAPI instance."""
    from fastapi import FastAPI
    app = create_app()
    assert isinstance(app, FastAPI)


def test_ac_http_14_missing_static_raises(monkeypatch, tmp_path):
    """AC-HTTP-14: If static/index.html missing at startup → RuntimeError."""
    monkeypatch.setattr("src.api.http_server.app._STATIC_DIR", tmp_path)
    with pytest.raises(RuntimeError, match="static/index.html"):
        create_app()