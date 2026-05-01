from __future__ import annotations

import pytest
from src.core.player_movement_system import compute_move_result


def test_speed_constraint_enforced():
    """AC-1 (Speed constraint — AC-PMS-01): per ADR-0014, speed=10, ratio=1.0 → 0.5 units/tick (5 m/s)."""
    current_pos = (50.0, 30.0)
    action = {"type": "move", "dx": 1, "dy": 0, "speed": 1.0}
    player_speed = 10

    result = compute_move_result(current_pos, action, player_speed)

    # move_dist = 1.0 * 10 * 0.05 = 0.5
    assert result == (50.5, 30.0)


def test_speed_ratio_clamping():
    """AC-2 (speed_ratio clamping — AC-PMS-02): speed=1.0 and speed=1.5 both produce same result."""
    current_pos = (50.0, 30.0)
    action_normal = {"type": "move", "dx": 1, "dy": 0, "speed": 1.0}
    action_over = {"type": "move", "dx": 1, "dy": 0, "speed": 1.5}
    player_speed = 10

    result_normal = compute_move_result(current_pos, action_normal, player_speed)
    result_over = compute_move_result(current_pos, action_over, player_speed)

    # Both → move_dist = 0.5 (per ADR-0014)
    assert result_normal == result_over == (50.5, 30.0)


def test_boundary_clamp():
    """AC-3 (Boundary clamp — AC-PMS-03): Player near edge, full-speed inward → clamped to bounds.

    Per ADR-0014: max move_dist = speed*0.05 = 1.0 unit at speed=20 ratio=1.0.
    Start at (0.5, 30.0) so move(-1) attempts to go to -0.5 → clamped to 0.0.
    """
    current_pos = (0.5, 30.0)
    action = {"type": "move", "dx": -1, "dy": 0, "speed": 1.0}
    player_speed = 20

    result = compute_move_result(current_pos, action, player_speed)

    # move_dist = 1.0; raw new_x = 0.5 + (-1) * 1.0 = -0.5, clamped to 0.0
    assert result == (0.0, 30.0)


def test_direction_only_normalization():
    """AC-4 (Direction-only — AC-PMS-04): (dx=3,dy=4) and (dx=300,dy=400) produce identical results."""
    current_pos = (50.0, 30.0)
    action_small = {"type": "move", "dx": 3, "dy": 4, "speed": 0.5}
    action_large = {"type": "move", "dx": 300, "dy": 400, "speed": 0.5}
    player_speed = 10

    result_small = compute_move_result(current_pos, action_small, player_speed)
    result_large = compute_move_result(current_pos, action_large, player_speed)

    # normalize(3,4) = (0.6, 0.8); move_dist = 0.5 * 10 * 0.05 = 0.25
    # result = (50 + 0.6*0.25, 30 + 0.8*0.25) = (50.15, 30.20)
    expected = (50.15, 30.20)
    assert result_small == expected
    assert result_large == expected


def test_hold_passthrough():
    """AC-5 (Hold() pass-through — AC-PMS-05): Hold action → current_pos unchanged."""
    current_pos = (40.0, 25.0)
    action = {"type": "hold"}
    player_speed = 10

    result = compute_move_result(current_pos, action, player_speed)

    assert result == (40.0, 25.0)


def test_near_zero_direction():
    """AC-6 (EC-01 near-zero direction): dx=0, dy=0 or below epsilon → no movement."""
    current_pos = (40.0, 25.0)
    player_speed = 10

    # Test with zero direction
    action_zero = {"type": "move", "dx": 0.0, "dy": 0.0, "speed": 1.0}
    result_zero = compute_move_result(current_pos, action_zero, player_speed)
    assert result_zero == current_pos

    # Test with below epsilon direction
    action_tiny = {"type": "move", "dx": 1e-9, "dy": 1e-9, "speed": 1.0}
    result_tiny = compute_move_result(current_pos, action_tiny, player_speed)
    assert result_tiny == current_pos


def test_negative_speed_ratio_clamped():
    """AC-7 (Negative speed_ratio clamped to 0): speed=-0.5 → no movement."""
    current_pos = (40.0, 25.0)
    action = {"type": "move", "dx": 1, "dy": 0, "speed": -0.5}
    player_speed = 10

    result = compute_move_result(current_pos, action, player_speed)

    # speed_ratio clamped to 0.0, move_dist = 0, result = current_pos
    assert result == current_pos


def test_multi_side_boundary_clamp():
    """AC-8 (Boundary clamp on multiple sides): Player near corner, full-speed outward → clamped to bounds.

    Per ADR-0014: max move_dist = 1.0 at speed=20 ratio=1.0. Start at (99.5, 59.5)
    so move(1,1) → (~100.2, ~60.2), clamped to (100.0, 60.0).
    """
    current_pos = (99.5, 59.5)
    action = {"type": "move", "dx": 1, "dy": 1, "speed": 1.0}
    player_speed = 20

    result = compute_move_result(current_pos, action, player_speed)

    # normalize(1,1) ≈ (0.707, 0.707); move_dist = 1.0 (per ADR-0014)
    # raw ≈ (99.5 + 0.707, 59.5 + 0.707) = (100.21, 60.21), clamped to (100.0, 60.0)
    assert result == (100.0, 60.0)


def test_empty_action_treated_as_hold():
    """AC-9 (Action without "type" key treated as Hold): empty dict → current_pos unchanged."""
    current_pos = (40.0, 25.0)
    action = {}  # Empty dict — defensive default
    player_speed = 10

    result = compute_move_result(current_pos, action, player_speed)

    assert result == current_pos


def test_pure_function_no_mutation():
    """AC-10 (Pure function — no input mutation): action dict unchanged after call."""
    current_pos = (50.0, 30.0)
    action = {"type": "move", "dx": 1, "dy": 0, "speed": 1.0}
    action_original = action.copy()
    player_speed = 10

    compute_move_result(current_pos, action, player_speed)

    assert action == action_original  # Verify no mutation occurred