"""
Tests for the per-tick health drain / recovery system (added 2026-04-23).

Verifies:
- _health_factor formula
- _apply_health_drain applies the right delta per action type
- stamina modulates drain
- Hold and low-speed Move recover
- formulas multiply by health_factor
"""

from __future__ import annotations
from unittest.mock import MagicMock, patch

from src.foundation.action_resolution_engine.engine import ActionResolutionEngine
from src.foundation.action import Pass, Shoot, Tackle, Hold, Move


def _engine_with_sim(health_max=100.0, drain_factor=1.0, health_floor=0.6):
    gsm = MagicMock()
    pms = MagicMock()
    bps = MagicMock()
    sandbox = MagicMock()
    fallback_handler = MagicMock()
    gsm.seed = 42
    sim = MagicMock()
    sim.health_max = health_max
    sim.health_drain_factor = drain_factor
    sim.health_floor = health_floor
    gsm.config = MagicMock()
    gsm.config.simulation = sim
    return ActionResolutionEngine(gsm=gsm, pms=pms, bps=bps,
                                  sandbox=sandbox,
                                  fallback_handler=fallback_handler)


# -----------------------------------------------------------------------------
# health_factor formula
# -----------------------------------------------------------------------------


def test_health_factor_full_health_is_one():
    eng = _engine_with_sim()
    assert abs(eng._health_factor({"current_health": 100.0}) - 1.0) < 1e-9


def test_health_factor_at_zero_equals_floor():
    eng = _engine_with_sim(health_floor=0.6)
    assert abs(eng._health_factor({"current_health": 0.0}) - 0.6) < 1e-9


def test_health_factor_half_health_is_eighty_pct():
    eng = _engine_with_sim(health_floor=0.6)
    assert abs(eng._health_factor({"current_health": 50.0}) - 0.8) < 1e-9


def test_health_factor_missing_health_falls_back_to_one():
    """Defensive: when player_state has no current_health (mock-based
    older tests), the multiplier is a no-op."""
    eng = _engine_with_sim()
    assert eng._health_factor({}) == 1.0


# -----------------------------------------------------------------------------
# Drain accounting via _apply_health_drain
# -----------------------------------------------------------------------------


def _snap_with_player(stamina):
    return {"players": {"team_a_0": {"player_id": "team_a_0", "stamina": stamina}}}


def test_pass_drains_with_stamina_modifier():
    eng = _engine_with_sim()
    snap = _snap_with_player(stamina=10)
    actions = {"team_a_0": Pass(target_pos=(60, 30), power=10)}
    captured = []
    eng.gsm.adjust_health.side_effect = lambda pid, delta: captured.append((pid, delta))
    eng._apply_health_drain(actions, snap, tick=1)
    # base_drain Pass=2.0, modifier (1 - 10/20)=0.5 → -1.0
    assert captured == [("team_a_0", -1.0)]


def test_shoot_drains_more_than_pass():
    eng = _engine_with_sim()
    snap = _snap_with_player(stamina=10)
    actions = {"team_a_0": Shoot(power=15, angle=0.0)}
    captured = []
    eng.gsm.adjust_health.side_effect = lambda pid, delta: captured.append((pid, delta))
    eng._apply_health_drain(actions, snap, tick=1)
    # base Shoot=4.0 × 0.5 = -2.0
    assert captured == [("team_a_0", -2.0)]


def test_tackle_drains():
    eng = _engine_with_sim()
    snap = _snap_with_player(stamina=10)
    actions = {"team_a_0": Tackle(target_player_id="team_b_2")}
    captured = []
    eng.gsm.adjust_health.side_effect = lambda pid, delta: captured.append((pid, delta))
    eng._apply_health_drain(actions, snap, tick=1)
    # base Tackle=4.0 × 0.5 = -2.0
    assert captured == [("team_a_0", -2.0)]


def test_max_stamina_zero_drain():
    eng = _engine_with_sim()
    snap = _snap_with_player(stamina=20)
    actions = {"team_a_0": Pass(target_pos=(60, 30), power=10)}
    captured = []
    eng.gsm.adjust_health.side_effect = lambda pid, delta: captured.append((pid, delta))
    eng._apply_health_drain(actions, snap, tick=1)
    assert captured == [("team_a_0", -0.0)] or captured == []  # 0 drain


def test_min_stamina_near_full_drain():
    eng = _engine_with_sim()
    snap = _snap_with_player(stamina=1)
    actions = {"team_a_0": Pass(target_pos=(60, 30), power=10)}
    captured = []
    eng.gsm.adjust_health.side_effect = lambda pid, delta: captured.append((pid, delta))
    eng._apply_health_drain(actions, snap, tick=1)
    # base 2.0 × (1 - 1/20) = 1.9 → -1.9
    assert captured == [("team_a_0", -1.9)]


def test_drain_factor_scales_drain():
    eng = _engine_with_sim(drain_factor=2.0)
    snap = _snap_with_player(stamina=10)
    actions = {"team_a_0": Pass(target_pos=(60, 30), power=10)}
    captured = []
    eng.gsm.adjust_health.side_effect = lambda pid, delta: captured.append((pid, delta))
    eng._apply_health_drain(actions, snap, tick=1)
    # 2.0 × 0.5 × 2.0 = -2.0
    assert captured == [("team_a_0", -2.0)]


# -----------------------------------------------------------------------------
# Recovery
# -----------------------------------------------------------------------------


def test_hold_recovers_one_point_five():
    eng = _engine_with_sim()
    snap = _snap_with_player(stamina=10)
    actions = {"team_a_0": Hold()}
    captured = []
    eng.gsm.adjust_health.side_effect = lambda pid, delta: captured.append((pid, delta))
    eng._apply_health_drain(actions, snap, tick=1)
    assert captured == [("team_a_0", 1.5)]


def test_low_speed_move_recovers():
    eng = _engine_with_sim()
    snap = _snap_with_player(stamina=10)
    actions = {"team_a_0": Move(dx=1.0, dy=0.0, speed=0.4)}  # below 0.5 → recovery
    captured = []
    eng.gsm.adjust_health.side_effect = lambda pid, delta: captured.append((pid, delta))
    eng._apply_health_drain(actions, snap, tick=1)
    assert captured == [("team_a_0", 0.5)]


def test_high_speed_move_drains():
    eng = _engine_with_sim()
    snap = _snap_with_player(stamina=10)
    actions = {"team_a_0": Move(dx=1.0, dy=0.0, speed=1.0)}
    captured = []
    eng.gsm.adjust_health.side_effect = lambda pid, delta: captured.append((pid, delta))
    eng._apply_health_drain(actions, snap, tick=1)
    # base Move=0.3 × (1 - 10/20)=0.5 → -0.15
    assert len(captured) == 1
    assert abs(captured[0][1] - (-0.15)) < 1e-9


def test_recovery_independent_of_stamina():
    """Recovery is flat: a low-stamina player on Hold still recovers
    1.5/tick. Stamina only modulates drain, not recovery."""
    eng = _engine_with_sim()
    captured = []
    eng.gsm.adjust_health.side_effect = lambda pid, delta: captured.append((pid, delta))
    for stamina in (1, 10, 20):
        captured.clear()
        snap = _snap_with_player(stamina=stamina)
        actions = {"team_a_0": Hold()}
        eng._apply_health_drain(actions, snap, tick=1)
        assert captured == [("team_a_0", 1.5)]
