"""Tests for EL Story 001: static-file invariants."""
from __future__ import annotations
from pathlib import Path

STATIC = Path("src/api/http_server/static")


def test_key_events_fetch():
    js = (STATIC / "app.js").read_text()
    assert "/api/match/key-events" in js


def test_event_log_list_id_present():
    html = (STATIC / "index.html").read_text()
    assert 'id="event-log-list"' in html


def test_event_log_dispatches_tick_selected():
    js = (STATIC / "app.js").read_text()
    assert "eventLog:tickSelected" in js


def test_event_log_subscribes_to_tick_changed():
    js = (STATIC / "app.js").read_text()
    assert "renderer:tickChanged" in js


def test_event_log_sidebar_h2_present():
    html = (STATIC / "index.html").read_text()
    assert 'id="event-log-sidebar"' in html
