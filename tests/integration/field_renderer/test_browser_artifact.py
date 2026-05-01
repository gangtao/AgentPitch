"""FR Story 002: Integration smoke — HTTP Server serves the browser artifact correctly."""
from __future__ import annotations
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


def test_root_serves_html_with_canvas(tmp_path):
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/")
    assert r.status_code == 200
    assert "field-canvas" in r.text


def test_app_js_served(tmp_path):
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/static/app.js")
    assert r.status_code == 200
    assert "seekToTick" in r.text


def test_app_css_served(tmp_path):
    client = TestClient(create_app(log_dir=str(tmp_path)))
    r = client.get("/static/app.css")
    assert r.status_code == 200
    assert "field-canvas" in r.text or "code-content" in r.text
