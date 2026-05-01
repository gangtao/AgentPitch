"""Smoke tests for the sandbox benchmark module (issue #31).

These confirm the benchmark functions return structurally valid results and that
the game-state fixtures are well-formed. They are NOT performance gates — the
full benchmark is run via `python tests/performance/bench_sandbox.py`.
"""

from __future__ import annotations

import pytest

from tests.performance.bench_sandbox import (
    bench_js,
    bench_python,
    make_game_state,
    make_player_state,
    make_history,
    percentiles,
)


# ── Fixture shape tests ───────────────────────────────────────────────────

def test_make_game_state_has_required_keys():
    gs = make_game_state()
    assert set(gs) >= {"tick", "ball", "players", "field", "score", "half", "match_phase"}
    assert len(gs["players"]) == 10
    assert gs["field"]["width"] == 100.0


def test_make_player_state_has_required_keys():
    ps = make_player_state("team_a_2")
    assert ps["team"] == "team_a"
    assert ps["has_ball"] is True
    assert "cooldown_remaining" in ps


def test_make_history_is_list():
    h = make_history()
    assert isinstance(h, list)
    assert len(h) >= 1


# ── Percentile helper ─────────────────────────────────────────────────────

def test_percentiles_empty_returns_zeros():
    p = percentiles([])
    assert p == {"p50": 0.0, "p95": 0.0, "p99": 0.0, "mean": 0.0}


def test_percentiles_single_value():
    p = percentiles([5.0])
    assert p["p50"] == 5.0
    assert p["p99"] == 5.0


def test_percentiles_sorted_sequence():
    p = percentiles([1.0, 2.0, 3.0, 4.0, 5.0])
    assert p["p50"] == pytest.approx(3.0, abs=0.01)
    assert p["p95"] >= p["p50"]
    assert p["p99"] >= p["p95"]


# ── Python sandbox benchmark returns valid structure ──────────────────────

def test_bench_python_returns_valid_structure():
    result = bench_python(compile_reps=3, execute_reps=5)
    assert "compile" in result
    assert "execute" in result
    assert "hold" in result["compile"]
    assert "realistic" in result["compile"]
    assert "realistic" in result["execute"]
    for key in ("mean", "p50", "p95", "p99"):
        assert key in result["execute"]["realistic"]
        assert result["execute"]["realistic"][key] >= 0.0


# ── JS sandbox benchmark (skips gracefully if quickjs absent) ─────────────

def test_bench_js_returns_valid_structure_or_none():
    result = bench_js(compile_reps=3, execute_reps=5)
    if result is None:
        pytest.skip("quickjs not installed")
    assert "compile" in result
    assert "execute" in result
    assert "json_marshal" in result
    for key in ("mean", "p50", "p95", "p99"):
        assert key in result["execute"]["realistic"]
        assert result["execute"]["realistic"][key] >= 0.0
