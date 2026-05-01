"""EL Story 002: Integration smoke."""
from __future__ import annotations
from fastapi.testclient import TestClient
from src.api.http_server.app import create_app


def test_sidebar_html_present(tmp_path):
    client = TestClient(create_app(log_dir=str(tmp_path)))
    html = client.get("/").text
    assert 'id="event-log-list"' in html
    assert 'id="event-log-sidebar"' in html
