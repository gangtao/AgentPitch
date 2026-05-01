"""Story 001 tests — Ball motion (advance_ball_position).

Covers AC-BPS-02, 03, 04, 05, 06, 07, 15 + EC-BPS-01, 10.
"""

from __future__ import annotations

import math

import pytest

from src.core.ball_physics_system import (
    FIELD_HEIGHT,
    FIELD_WIDTH,
    advance_ball_position,
)


# ---------------------------------------------------------------------------
# AC-1: AT_REST no-op (AC-BPS-02)
# ---------------------------------------------------------------------------


def test_at_rest_velocity_zero_returns_unchanged_position():
    pos, vel, oob = advance_ball_position((50.0, 30.0), (0.0, 0.0), None)
    assert pos == (50.0, 30.0)
    assert vel == (0.0, 0.0)
    assert oob is False


# ---------------------------------------------------------------------------
# AC-2: Near-zero velocity guard (AC-BPS-15 / EC-BPS-08)
# ---------------------------------------------------------------------------


def test_near_zero_velocity_treated_as_at_rest():
    pos, vel, oob = advance_ball_position((50.0, 30.0), (1e-9, 1e-9), None)
    assert pos == (50.0, 30.0)
    assert vel == (0.0, 0.0)
    assert oob is False


def test_at_velocity_epsilon_boundary_below_treated_as_at_rest():
    # A velocity whose magnitude is below 1e-6 should be a no-op.
    pos, vel, oob = advance_ball_position((10.0, 10.0), (1e-7, 0.0), None)
    assert pos == (10.0, 10.0)
    assert vel == (0.0, 0.0)
    assert oob is False


# ---------------------------------------------------------------------------
# AC-3: Constant velocity advance (AC-BPS-03)
# ---------------------------------------------------------------------------


def test_constant_velocity_single_tick_advance():
    pos, vel, oob = advance_ball_position((50.0, 30.0), (2.0, 1.0), None)
    assert pos == (52.0, 31.0)
    assert vel == (2.0, 1.0)
    assert oob is False


def test_constant_velocity_three_ticks_total_displacement():
    velocity = (2.0, 1.0)
    pos = (50.0, 30.0)
    for _ in range(3):
        pos, _, _ = advance_ball_position(pos, velocity, None)
    expected_displacement = 3.0 * math.sqrt(2.0 * 2.0 + 1.0 * 1.0)
    actual_displacement = math.sqrt(
        (pos[0] - 50.0) ** 2 + (pos[1] - 30.0) ** 2
    )
    assert actual_displacement == pytest.approx(expected_displacement, abs=1e-9)


# ---------------------------------------------------------------------------
# AC-4: Overshoot snap (AC-BPS-04)
# ---------------------------------------------------------------------------


def test_overshoot_snap_to_landing_zone():
    # First tick: dot > 0, no overshoot, advance normally.
    pos, vel, oob = advance_ball_position(
        (48.0, 30.0), (5.0, 0.0), (50.0, 30.0)
    )
    assert pos == (53.0, 30.0)
    assert vel == (5.0, 0.0)
    assert oob is False

    # Second tick (re-feed): dot <= 0, snap to landing zone, velocity (0, 0).
    pos, vel, oob = advance_ball_position(
        (53.0, 30.0), (5.0, 0.0), (50.0, 30.0)
    )
    assert pos == (50.0, 30.0)
    assert vel == (0.0, 0.0)
    assert oob is False


# ---------------------------------------------------------------------------
# AC-5: Dot=0 trigger (AC-BPS-05)
# ---------------------------------------------------------------------------


def test_dot_product_zero_triggers_snap():
    # Ball at landing zone exactly: to_lz = (0, 0), dot = 0, snap fires.
    pos, vel, oob = advance_ball_position(
        (50.0, 30.0), (5.0, 0.0), (50.0, 30.0)
    )
    assert pos == (50.0, 30.0)
    assert vel == (0.0, 0.0)
    assert oob is False


# ---------------------------------------------------------------------------
# AC-6: OOB clamp (AC-BPS-06)
# ---------------------------------------------------------------------------


def test_oob_east_edge_clamps_to_field_width():
    pos, vel, oob = advance_ball_position(
        (98.0, 30.0), (5.0, 0.0), None, field_width=100.0, field_height=60.0
    )
    assert pos == (100.0, 30.0)
    assert vel == (0.0, 0.0)
    assert oob is True


def test_oob_west_edge_clamps_to_zero():
    pos, vel, oob = advance_ball_position(
        (2.0, 30.0), (-5.0, 0.0), None, field_width=100.0, field_height=60.0
    )
    assert pos == (0.0, 30.0)
    assert vel == (0.0, 0.0)
    assert oob is True


def test_oob_south_edge_clamps_to_field_height():
    pos, vel, oob = advance_ball_position(
        (50.0, 58.0), (0.0, 5.0), None, field_width=100.0, field_height=60.0
    )
    assert pos == (50.0, 60.0)
    assert vel == (0.0, 0.0)
    assert oob is True


# ---------------------------------------------------------------------------
# AC-7: OOB priority over overshoot (AC-BPS-07)
# ---------------------------------------------------------------------------


def test_oob_priority_over_overshoot():
    # Landing zone is on-pitch but next_pos goes OOB → OOB wins.
    pos, vel, oob = advance_ball_position(
        (98.0, 30.0), (5.0, 0.0), (99.0, 30.0),
        field_width=100.0, field_height=60.0,
    )
    assert pos == (100.0, 30.0)
    assert vel == (0.0, 0.0)
    assert oob is True
    # Specifically NOT at landing_zone (99, 30).
    assert pos != (99.0, 30.0)


# ---------------------------------------------------------------------------
# AC-8: No landing zone (EC-BPS-01) — shot path
# ---------------------------------------------------------------------------


def test_no_landing_zone_advances_by_velocity_only():
    pos, vel, oob = advance_ball_position((50.0, 30.0), (2.0, 1.0), None)
    assert pos == (52.0, 31.0)
    assert vel == (2.0, 1.0)
    assert oob is False


# ---------------------------------------------------------------------------
# AC-9: Corner OOB (EC-BPS-10) — both axes
# ---------------------------------------------------------------------------


def test_corner_oob_both_axes_clamp_independently():
    pos, vel, oob = advance_ball_position(
        (98.0, 58.0), (5.0, 5.0), None, field_width=100.0, field_height=60.0
    )
    assert pos == (100.0, 60.0)
    assert vel == (0.0, 0.0)
    assert oob is True


# ---------------------------------------------------------------------------
# AC-10: Pure function — no input mutation
# ---------------------------------------------------------------------------


def test_pure_function_no_side_effects():
    initial_pos = (50.0, 30.0)
    initial_vel = (2.0, 1.0)
    initial_lz = (60.0, 30.0)
    advance_ball_position(initial_pos, initial_vel, initial_lz)
    # All inputs are tuples (immutable). Verify they haven't changed.
    assert initial_pos == (50.0, 30.0)
    assert initial_vel == (2.0, 1.0)
    assert initial_lz == (60.0, 30.0)


# ---------------------------------------------------------------------------
# Bonus: default field constants used when not overridden
# ---------------------------------------------------------------------------


def test_default_field_constants_used_when_not_specified():
    # FIELD_WIDTH=100.0, FIELD_HEIGHT=60.0 used by default.
    pos, vel, oob = advance_ball_position(
        (FIELD_WIDTH - 2.0, FIELD_HEIGHT - 2.0), (5.0, 5.0), None
    )
    assert pos == (FIELD_WIDTH, FIELD_HEIGHT)
    assert vel == (0.0, 0.0)
    assert oob is True
