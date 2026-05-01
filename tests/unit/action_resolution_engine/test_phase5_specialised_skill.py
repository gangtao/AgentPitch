"""
Tests for the effective-skill blend in ARE Phase 5 (added 2026-04-23).

Pass deviation is driven by `pass_eff_skill = (2 * passing + skill) / 3`.
Shot angular spread by `shot_eff_skill = (2 * shooting + skill) / 3`.
When the specialised attribute is missing the player dict falls back to
`skill`, so the blend reduces to plain `skill` — pre-existing tests
keep passing unchanged.
"""

from __future__ import annotations
from unittest.mock import MagicMock, patch

import pytest

from src.foundation.action_resolution_engine.engine import ActionResolutionEngine
from src.foundation.action import Pass, Shoot


@pytest.fixture
def mock_dependencies():
    gsm = MagicMock()
    pms = MagicMock()
    bps = MagicMock()
    sandbox = MagicMock()
    fallback_handler = MagicMock()
    gsm.seed = 12345
    return {"gsm": gsm, "pms": pms, "bps": bps,
            "sandbox": sandbox, "fallback_handler": fallback_handler}


def _snap(skill=10, passing=None, shooting=None):
    """Build a minimal snap with one carrier whose attrs we control."""
    p = {
        "player_id": "team_a_0",
        "team": "team_a",
        "position": (50.0, 30.0),
        "skill": skill,
    }
    if passing is not None: p["passing"] = passing
    if shooting is not None: p["shooting"] = shooting
    return {
        "tick": 50,
        "players": {"team_a_0": p},
        "ball": {"carrier_id": "team_a_0"},
        "field": {"team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
                  "goal_top": 35.0, "goal_bottom": 25.0},
    }


def _patch_hash_const(value):
    """Return a hash_01 side_effect that always yields `value`."""
    return lambda *a, **kw: value


def _spread(eff_skill: float) -> float:
    return max(0.0, 1.0 - eff_skill / 20.0) ** 0.7


# -----------------------------------------------------------------------------
# Pass blend
# -----------------------------------------------------------------------------


def test_pass_passing_attr_dominates_skill(mock_dependencies):
    """passing=20, skill=10 → eff = 16.67 → tighter spread than plain skill=10."""
    snap = _snap(skill=10, passing=20)
    engine = ActionResolutionEngine(**mock_dependencies)
    mock_dependencies["gsm"].build_player_state.side_effect = (
        lambda pid: {"has_ball": pid == "team_a_0"}
    )
    actions = {"team_a_0": Pass(target_pos=(60.0, 30.0), power=10)}

    with patch("src.foundation.action_resolution_engine.engine.hash_01") as h:
        # mag draw=0.5, angle draw=0 (so deviation lands along +x)
        h.side_effect = lambda seed, tick, pid, ctx: 0.5 if ctx == "pass_dev_mag" else 0.0
        result = engine._resolve_phase5(actions, snap, 50, "team_a_0")

    eff_skill = (2.0 * 20 + 10) / 3.0     # 16.667
    expected_mag = _spread(eff_skill) * 8.0 * 0.5
    landing = result["team_a_0"]["landing_pos"]
    assert abs(landing[0] - (60.0 + expected_mag)) < 1e-6
    # Sanity: the specialised passer's spread should be MUCH less than
    # what plain skill=10 would produce.
    plain_mag = _spread(10) * 8.0 * 0.5
    assert expected_mag < plain_mag * 0.7  # roughly 1.07 vs 2.50


def test_pass_low_passing_attr_widens_spread(mock_dependencies):
    """passing=1, skill=10 → eff=4 → wider spread than plain skill=10."""
    snap = _snap(skill=10, passing=1)
    engine = ActionResolutionEngine(**mock_dependencies)
    mock_dependencies["gsm"].build_player_state.side_effect = (
        lambda pid: {"has_ball": pid == "team_a_0"}
    )
    actions = {"team_a_0": Pass(target_pos=(60.0, 30.0), power=10)}

    with patch("src.foundation.action_resolution_engine.engine.hash_01") as h:
        h.side_effect = lambda seed, tick, pid, ctx: 0.5 if ctx == "pass_dev_mag" else 0.0
        result = engine._resolve_phase5(actions, snap, 50, "team_a_0")

    eff_skill = (2.0 * 1 + 10) / 3.0   # 4.0
    expected_mag = _spread(eff_skill) * 8.0 * 0.5
    landing = result["team_a_0"]["landing_pos"]
    assert abs(landing[0] - (60.0 + expected_mag)) < 1e-6
    plain_mag = _spread(10) * 8.0 * 0.5
    assert expected_mag > plain_mag


def test_pass_no_passing_attr_falls_back_to_skill(mock_dependencies):
    """When passing is missing from the player dict, the blend collapses
    to `skill` — bit-identical to the legacy formula."""
    snap = _snap(skill=10)  # no passing field
    engine = ActionResolutionEngine(**mock_dependencies)
    mock_dependencies["gsm"].build_player_state.side_effect = (
        lambda pid: {"has_ball": pid == "team_a_0"}
    )
    actions = {"team_a_0": Pass(target_pos=(60.0, 30.0), power=10)}

    with patch("src.foundation.action_resolution_engine.engine.hash_01") as h:
        h.side_effect = lambda seed, tick, pid, ctx: 0.5 if ctx == "pass_dev_mag" else 0.0
        result = engine._resolve_phase5(actions, snap, 50, "team_a_0")

    expected_mag = _spread(10) * 8.0 * 0.5
    landing = result["team_a_0"]["landing_pos"]
    assert abs(landing[0] - (60.0 + expected_mag)) < 1e-6


# -----------------------------------------------------------------------------
# Shoot blend
# -----------------------------------------------------------------------------


def test_shoot_shooting_attr_dominates_skill(mock_dependencies):
    """shooting=20, skill=10 → eff=16.67 → angular spread shrinks."""
    snap = _snap(skill=10, shooting=20)
    engine = ActionResolutionEngine(**mock_dependencies)
    mock_dependencies["gsm"].build_player_state.side_effect = (
        lambda pid: {"has_ball": pid == "team_a_0"}
    )
    # angle=0 → straight at goal mouth center; draw=1.0 → max +deviation
    actions = {"team_a_0": Shoot(power=15, angle=0.0)}

    captured = {}
    mock_dependencies["gsm"].update_ball_velocity.side_effect = (
        lambda v: captured.setdefault("vel", v)
    )
    with patch("src.foundation.action_resolution_engine.engine.hash_01") as h:
        h.side_effect = lambda seed, tick, pid, ctx: 1.0 if ctx == "shot_dev_angle" else 0.5
        engine._resolve_phase5(actions, snap, 50, "team_a_0")

    # Sanity: with high shooting, angular deviation is small. Compare against
    # plain skill=10 — the angle off-axis with shooting=20 should be smaller.
    import math
    eff_skill = (2.0 * 20 + 10) / 3.0
    expected_spread = _spread(eff_skill) * 0.30  # default shot_max_angle
    expected_dev = (1.0 - 0.5) * 2.0 * expected_spread
    # Compute angle of resulting velocity vector
    vx, vy = captured["vel"]
    # Base angle = atan2(30 - 30, 100 - 50) = 0 (toward goal center)
    actual_angle = math.atan2(vy, vx)
    assert abs(actual_angle - expected_dev) < 1e-5
    # Plain skill=10 would have a much larger deviation
    plain_dev = (1.0 - 0.5) * 2.0 * _spread(10) * 0.30
    assert abs(actual_angle) < abs(plain_dev) * 0.7


def test_shoot_no_shooting_attr_falls_back_to_skill(mock_dependencies):
    """Missing shooting → blend collapses to plain skill, identical to legacy."""
    snap = _snap(skill=10)
    engine = ActionResolutionEngine(**mock_dependencies)
    mock_dependencies["gsm"].build_player_state.side_effect = (
        lambda pid: {"has_ball": pid == "team_a_0"}
    )
    actions = {"team_a_0": Shoot(power=15, angle=0.0)}

    captured = {}
    mock_dependencies["gsm"].update_ball_velocity.side_effect = (
        lambda v: captured.setdefault("vel", v)
    )
    with patch("src.foundation.action_resolution_engine.engine.hash_01") as h:
        h.side_effect = lambda seed, tick, pid, ctx: 1.0 if ctx == "shot_dev_angle" else 0.5
        engine._resolve_phase5(actions, snap, 50, "team_a_0")

    import math
    expected_dev = (1.0 - 0.5) * 2.0 * _spread(10) * 0.30
    vx, vy = captured["vel"]
    actual_angle = math.atan2(vy, vx)
    assert abs(actual_angle - expected_dev) < 1e-5
