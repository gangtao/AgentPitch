"""Tests for the formation_snap_enabled toggle (ADR-0022 amendment d, 2026-04-25).

When False, PMS skips the snap step entirely — strategy fully owns positioning.
When True (default), behavior matches the existing soft-snap rules from ADR-0013
+ ADR-0022.
"""
from __future__ import annotations

from src.core.player_movement_system import resolve_movement


def _idle_player_state_far_from_anchor():
    """Common fixture: idle player at (60,40), anchor (25,20), discipline=16.
    With snap on, ADR-0013 pulls them ~16% toward the anchor.
    With snap off, they stay put (final_pos = move_result = current_pos).
    """
    return {
        "position": (60.0, 40.0),
        "formation_position": (25.0, 20.0),
        "speed": 10,
        "discipline": 16,
        "has_ball": False,
        "team": "team_a",
    }


def test_snap_disabled_idle_player_stays_put():
    """With snap_enabled=False, an idle (Hold) player at (60,40) stays at
    (60,40) regardless of their formation_position. Strategy owns positioning."""
    player_state = _idle_player_state_far_from_anchor()
    action = {"type": "hold"}
    snapshot = {"players": {}}

    final_pos, _ = resolve_movement(
        "team_a_0", action, player_state, snapshot,
        snap_enabled=False,
    )

    # No snap pull → final_pos == current_pos (Hold means no movement)
    assert final_pos == (60.0, 40.0)


def test_snap_disabled_passive_move_honors_intent_fully():
    """With snap_enabled=False, even a low-speed Move (which would normally
    incur snap pull because speed < ACTIVE_SPEED_THRESHOLD=0.5) honors intent
    fully — no anchor pull at all."""
    player_state = _idle_player_state_far_from_anchor()
    action = {"type": "move", "dx": 1.0, "dy": 0.0, "speed": 0.2}  # passive low-speed
    snapshot = {"players": {}}

    final_pos, _ = resolve_movement(
        "team_a_0", action, player_state, snapshot,
        snap_enabled=False,
    )

    # Expected: small move toward +x with no anchor pull. Compare to
    # snap-enabled equivalent below to confirm the toggle changes behavior.
    expected_move_x = 60.0 + 1.0 * 0.2 * 10 * 0.05  # 60 + 0.1 = 60.1
    assert abs(final_pos[0] - expected_move_x) < 1e-9
    assert abs(final_pos[1] - 40.0) < 1e-9


def test_snap_enabled_default_pulls_idle_player_toward_anchor():
    """Regression guard: snap_enabled defaults to True (preserves existing
    behavior). Idle player at (60,40) with anchor (25,20) discipline=16
    drifts toward anchor by 16%."""
    player_state = _idle_player_state_far_from_anchor()
    action = {"type": "hold"}
    snapshot = {"players": {}}

    final_pos, _ = resolve_movement(
        "team_a_0", action, player_state, snapshot,
        # No snap_enabled kwarg → defaults to True
    )

    # snap_force = 0.16, final = 0.84*current + 0.16*anchor
    expected_x = 0.84 * 60.0 + 0.16 * 25.0
    expected_y = 0.84 * 40.0 + 0.16 * 20.0
    assert abs(final_pos[0] - expected_x) < 1e-9
    assert abs(final_pos[1] - expected_y) < 1e-9


def test_snap_disabled_then_enabled_produce_different_results():
    """The toggle is observably load-bearing: same inputs, different snap
    flag, different output. This is the regression test for the A/B
    testing scenario described in ADR-0022 amendment d."""
    player_state = _idle_player_state_far_from_anchor()
    action = {"type": "hold"}
    snapshot = {"players": {}}

    final_off, _ = resolve_movement(
        "team_a_0", action, player_state, snapshot,
        snap_enabled=False,
    )
    final_on, _ = resolve_movement(
        "team_a_0", action, player_state, snapshot,
        snap_enabled=True,
    )

    assert final_off != final_on


def test_snap_disabled_does_not_affect_carrier_or_active_intent():
    """Carriers and active-intent moves already bypass snap (ADR-0013
    amendment 2026-04-22). The snap_enabled flag is a no-op for them —
    they get the same result either way."""
    # Active-intent Move at speed=1.0 (≥ ACTIVE_SPEED_THRESHOLD)
    player_state = _idle_player_state_far_from_anchor()
    action = {"type": "move", "dx": 1.0, "dy": 0.0, "speed": 1.0}
    snapshot = {"players": {}}

    final_off, _ = resolve_movement(
        "team_a_0", action, player_state, snapshot,
        snap_enabled=False,
    )
    final_on, _ = resolve_movement(
        "team_a_0", action, player_state, snapshot,
        snap_enabled=True,
    )

    # Active intent bypasses snap regardless of toggle — results identical.
    assert final_off == final_on
