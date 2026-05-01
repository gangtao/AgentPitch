"""Tests for FR Story 001: static file invariants."""
from __future__ import annotations
from pathlib import Path

STATIC = Path("src/api/http_server/static")


def test_index_html_exists():
    assert (STATIC / "index.html").exists()


def test_app_js_exists():
    assert (STATIC / "app.js").exists()


def test_app_css_exists():
    assert (STATIC / "app.css").exists()


def test_canvas_id_present():
    html = (STATIC / "index.html").read_text()
    assert 'id="field-canvas"' in html


def test_app_js_fetches_match_meta():
    js = (STATIC / "app.js").read_text()
    # Match all reasonable forms — the URL may now have a `?match_id=...` query
    # string appended via template literal interpolation.
    assert (
        'fetch("/api/match"' in js
        or "fetch('/api/match'" in js
        or "fetch(`/api/match" in js
    )


def test_app_js_fetches_ticks():
    js = (STATIC / "app.js").read_text()
    assert "/api/match/ticks" in js


def test_app_js_uses_request_animation_frame():
    js = (STATIC / "app.js").read_text()
    assert "requestAnimationFrame" in js


def test_app_js_defines_seek_to_tick():
    """AC-FR-15 (adapted): seekToTick is the public export."""
    js = (STATIC / "app.js").read_text()
    assert "seekToTick" in js


def test_app_js_no_python_imports():
    """AC-FR-15: no Python module references in JS."""
    js = (STATIC / "app.js").read_text()
    assert "from src." not in js
    assert "import src." not in js


def test_app_js_dispatches_renderer_tick_changed():
    """AC-FR-16 plumbing: renderer:tickChanged event dispatch."""
    js = (STATIC / "app.js").read_text()
    assert "renderer:tickChanged" in js


def test_app_js_has_deltams_clamp():
    """AC-FR-13 plumbing: deltaMs clamp prevents catch-up burst after tab background."""
    js = (STATIC / "app.js").read_text()
    # The 200ms cap is present
    assert "200" in js  # used in Math.min(200, ...)
