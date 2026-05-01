from __future__ import annotations

import pytest
from src.core.player_movement_system import (
    compute_snap_force,
    apply_snap,
    resolve_movement,
    FIELD_WIDTH,
    FIELD_HEIGHT,
    DRIBBLE_RANGE
)


def test_snap_force_cap():
    """AC-1 (Snap force cap — AC-PMS-06): parametrize discipline 1..20; assert all < 1.0. Specific values tested."""
    # Test all values 1-20
    for discipline in range(1, 21):
        snap_force = compute_snap_force(discipline)
        assert snap_force < 1.0, f"discipline={discipline} should produce snap_force < 1.0"

    # Test specific required values (per ADR-0013: divisor=100, cap=0.20)
    assert compute_snap_force(20) == 0.20
    assert compute_snap_force(1) == 0.01
    assert compute_snap_force(16) == 0.16


def test_snap_at_max_discipline():
    """AC-2 (Snap at max discipline): apply_snap with the post-ADR-0013 cap of 0.20.

    Per ADR-0013 (2026-04-22): max snap is now 0.20 (was 0.95). Test exercises
    apply_snap directly with the new cap so the math contract is verified.
    """
    move_result = (80.0, 50.0)
    anchor_pos = (25.0, 20.0)
    snap_force = 0.20

    result = apply_snap(move_result, anchor_pos, snap_force)

    # Expected: (1-0.20)*80 + 0.20*25 = 0.80*80 + 0.20*25 = 64.0 + 5.0 = 69.0
    # Expected: (1-0.20)*50 + 0.20*20 = 0.80*50 + 0.20*20 = 40.0 + 4.0 = 44.0
    assert abs(result[0] - 69.0) < 1e-10
    assert abs(result[1] - 44.0) < 1e-10


def test_snap_on_hold():
    """AC-3 (Snap on Hold — AC-PMS-08): player at (60,40), anchor (25,20), discipline=16, Hold().

    Per ADR-0013: discipline=16 → snap_force=0.16 (was 0.80).
    """
    player_state = {
        "position": (60.0, 40.0),
        "formation_position": (25.0, 20.0),
        "speed": 10,
        "discipline": 16,
        "has_ball": False,
        "team": "team_a",
    }
    action = {"type": "hold"}
    game_state_snapshot = {"players": {}}

    final_pos, dribble_target = resolve_movement("team_a_0", action, player_state, game_state_snapshot)

    # Hold() → move_result = (60, 40) (no movement)
    # snap_force = 0.16
    # final_pos x: 0.84*60 + 0.16*25 = 50.4 + 4.0 = 54.4
    # final_pos y: 0.84*40 + 0.16*20 = 33.6 + 3.2 = 36.8
    assert abs(final_pos[0] - 54.4) < 1e-10
    assert abs(final_pos[1] - 36.8) < 1e-10
    assert dribble_target is None  # Hold doesn't trigger dribble


def test_half_time_anchor_swap():
    """AC-4 (Half-time anchor swap — AC-PMS-09): same player, different formation_position → different final_pos."""
    base_player_state = {
        "position": (50.0, 30.0),
        "speed": 10,
        "discipline": 10,
        "has_ball": False,
        "team": "team_a",
    }
    action = {"type": "hold"}
    game_state_snapshot = {"players": {}}

    # First call with one anchor
    player_state_1 = base_player_state.copy()
    player_state_1["formation_position"] = (8.0, 30.0)
    final_pos_1, _ = resolve_movement("team_a_0", action, player_state_1, game_state_snapshot)

    # Second call with different anchor
    player_state_2 = base_player_state.copy()
    player_state_2["formation_position"] = (92.0, 30.0)
    final_pos_2, _ = resolve_movement("team_a_0", action, player_state_2, game_state_snapshot)

    # Results should differ (proves PMS reads anchor from snapshot)
    assert final_pos_1 != final_pos_2


def test_dribble_uses_post_snap():
    """AC-5 (Dribble uses post-snap — AC-PMS-14): ball carrier snapped → dribble_target=None when far from opponent.

    Per ADR-0013: discipline=20 → snap_force=0.20 (was 0.95). Movement
    follows intent more strongly, but the player is still far from the
    opponent so no dribble.
    """
    player_state = {
        "position": (25.0, 20.0),
        "formation_position": (25.0, 20.0),
        "speed": 2,
        "discipline": 20,  # snap_force = 0.20 per ADR-0013
        "has_ball": True,
        "team": "team_a",
    }
    # Move toward opponent at (40, 20)
    action = {"type": "move", "dx": 1, "dy": 0, "speed": 1.0}

    # Opponent at (40, 20)
    game_state_snapshot = {
        "players": {
            "team_b_0": {"position": (40.0, 20.0), "team": "team_b"}
        }
    }

    final_pos, dribble_target = resolve_movement("team_a_0", action, player_state, game_state_snapshot)

    # Per ADR-0014: move_dist = 1.0 * 2 * 0.05 = 0.1, so move_result = (25.1, 20)
    # Per ADR-0013 amendment (2026-04-22): has_ball=True bypasses snap entirely.
    # Carrier intent is honored, no anchor pull.
    # final_pos = move_result = (25.1, 20.0)
    # Distance from (25.1, 20) to opponent (40, 20) = 14.9 > DRIBBLE_RANGE=1.5
    assert dribble_target is None
    assert abs(final_pos[0] - 25.1) < 0.01


def test_return_type():
    """AC-6 (Return type — AC-PMS-15): returns tuple of (tuple[float, float], str | None)."""
    player_state = {
        "position": (50.0, 30.0),
        "formation_position": (50.0, 30.0),
        "speed": 10,
        "discipline": 10,
        "has_ball": False,
        "team": "team_a",
    }
    action = {"type": "hold"}
    game_state_snapshot = {"players": {}}

    result = resolve_movement("team_a_0", action, player_state, game_state_snapshot)

    # Verify return type structure
    assert isinstance(result, tuple)
    assert len(result) == 2

    final_pos, dribble_target = result
    assert isinstance(final_pos, tuple)
    assert len(final_pos) == 2
    assert isinstance(final_pos[0], float)
    assert isinstance(final_pos[1], float)
    assert dribble_target is None or isinstance(dribble_target, str)


def test_determinism():
    """AC-7 (Determinism — AC-PMS-17): identical inputs → identical outputs."""
    player_state = {
        "position": (50.0, 30.0),
        "formation_position": (40.0, 25.0),
        "speed": 10,
        "discipline": 15,
        "has_ball": True,
        "team": "team_a",
    }
    action = {"type": "move", "dx": 1, "dy": 1, "speed": 0.5}
    game_state_snapshot = {
        "players": {
            "team_b_0": {"position": (60.0, 35.0), "team": "team_b"}
        }
    }

    result_1 = resolve_movement("team_a_0", action, player_state, game_state_snapshot)
    result_2 = resolve_movement("team_a_0", action, player_state, game_state_snapshot)

    assert result_1 == result_2


def test_compute_all_then_commit():
    """AC-8 (Compute-all-then-commit — AC-PMS-16): A's result unaffected by subsequent snapshot mutation."""
    player_state = {
        "position": (50.0, 30.0),
        "formation_position": (50.0, 30.0),
        "speed": 10,
        "discipline": 10,
        "has_ball": False,
        "team": "team_a",
    }
    action = {"type": "move", "dx": 1, "dy": 0, "speed": 0.5}
    game_state_snapshot = {
        "players": {
            "team_a_0": {"position": (50.0, 30.0), "team": "team_a"},
            "team_a_1": {"position": (40.0, 30.0), "team": "team_a"},
        }
    }

    # Player A's resolve_movement call
    result_a = resolve_movement("team_a_0", action, player_state, game_state_snapshot)

    # Simulate commit phase: mutate snapshot's player B position
    game_state_snapshot["players"]["team_a_1"]["position"] = (45.0, 35.0)

    # Per ADR-0014: move_dist = 0.5 * 10 * 0.05 = 0.25, move_result = (50.25, 30)
    # Per ADR-0013 amendment: speed_ratio=0.5 == ACTIVE_SPEED_THRESHOLD,
    # counts as active intent → snap bypassed. final_pos = move_result.
    assert abs(result_a[0][0] - 50.25) < 1e-10
    assert abs(result_a[0][1] - 30.0) < 1e-10


def test_player_at_exact_anchor():
    """AC-9 (EC-PMS-05 player at exact anchor): snap is no-op when player at anchor."""
    player_state = {
        "position": (25.0, 20.0),
        "formation_position": (25.0, 20.0),
        "speed": 10,
        "discipline": 10,
        "has_ball": False,
        "team": "team_a",
    }
    action = {"type": "hold"}
    game_state_snapshot = {"players": {}}

    final_pos, dribble_target = resolve_movement("team_a_0", action, player_state, game_state_snapshot)

    # Player at anchor, Hold action → move_result = anchor, final_pos = anchor
    assert final_pos == (25.0, 20.0)


def test_max_snap_still_produces_visible_move():
    """AC-10 (EC-PMS-12): active Move bypasses snap entirely per ADR-0013 amendment.

    Per ADR-0013 amendment (2026-04-22): a Move with speed_ratio >=
    ACTIVE_SPEED_THRESHOLD (0.5) bypasses snap regardless of discipline.
    So max discipline=20 is irrelevant when intent is active.
    """
    player_state = {
        "position": (8.0, 30.0),
        "formation_position": (8.0, 30.0),
        "speed": 8,
        "discipline": 20,  # snap_force=0.20 — irrelevant for active Move
        "has_ball": False,
        "team": "team_a",
    }
    action = {"type": "move", "dx": 1, "dy": 0, "speed": 1.0}  # active
    game_state_snapshot = {"players": {}}

    final_pos, dribble_target = resolve_movement("team_a_0", action, player_state, game_state_snapshot)

    # move_result = (8.0 + 1.0 * 8 * 0.05, 30) = (8.4, 30). Snap bypassed.
    assert abs(final_pos[0] - 8.4) < 1e-10
    assert final_pos[1] == 30.0


def test_pure_function_no_mutation():
    """AC-11 (Pure function — no input mutation): inputs unchanged after call."""
    original_action = {"type": "move", "dx": 1, "dy": 0, "speed": 0.5}
    original_player_state = {
        "position": (50.0, 30.0),
        "formation_position": (40.0, 25.0),
        "speed": 10,
        "discipline": 10,
        "has_ball": False,
        "team": "team_a",
    }
    original_snapshot = {
        "players": {
            "team_b_0": {"position": (60.0, 35.0), "team": "team_b"}
        }
    }

    # Make copies to verify no mutation
    action = original_action.copy()
    player_state = original_player_state.copy()
    game_state_snapshot = {
        "players": {k: v.copy() for k, v in original_snapshot["players"].items()}
    }

    resolve_movement("team_a_0", action, player_state, game_state_snapshot)

    # Verify no mutation occurred
    assert action == original_action
    assert player_state == original_player_state
    assert game_state_snapshot == original_snapshot


def test_compose_with_movement_formula():
    """AC-12 (Compose with movement formula — round-trip): integration test of movement + snap.

    Per ADR-0013: discipline=10 → snap_force=0.10 (was 0.50).
    """
    player_state = {
        "position": (50.0, 30.0),
        "formation_position": (50.0, 30.0),
        "speed": 10,
        "discipline": 10,  # snap_force = 0.10 per ADR-0013
        "has_ball": False,
        "team": "team_a",
    }
    action = {"type": "move", "dx": 1, "dy": 0, "speed": 1.0}
    game_state_snapshot = {"players": {}}

    final_pos, dribble_target = resolve_movement("team_a_0", action, player_state, game_state_snapshot)

    # Per ADR-0014: move_dist = 1.0 * 10 * 0.05 = 0.5, move_result = (50.5, 30)
    # Per ADR-0013 amendment: active Move (speed=1.0 >= 0.5) bypasses snap.
    assert abs(final_pos[0] - 50.5) < 1e-10
    assert abs(final_pos[1] - 30.0) < 1e-10
    assert dribble_target is None


def test_compose_with_dribble():
    """AC-13 (Compose with dribble — round-trip): ball carrier triggers dribble within range.

    Per ADR-0013 amendment (2026-04-22): has_ball=True bypasses snap.
    Carrier moves to exactly move_result position with no anchor pull.
    """
    player_state = {
        "position": (30.0, 30.0),
        "formation_position": (30.0, 30.0),
        "speed": 20,  # max speed → 1.0 unit/tick at full ratio
        "discipline": 1,  # snap_force=0.01 — irrelevant for carrier
        "has_ball": True,
        "team": "team_a",
    }
    action = {"type": "move", "dx": 1, "dy": 0, "speed": 1.0}

    # Opponent within DRIBBLE_RANGE=1.5 of carrier's final position
    game_state_snapshot = {
        "players": {
            "team_b_0": {"position": (32.0, 30.0), "team": "team_b"}
        }
    }

    final_pos, dribble_target = resolve_movement("team_a_0", action, player_state, game_state_snapshot)

    # Per ADR-0014: move_dist = 1.0 * 20 * 0.05 = 1.0
    # Carrier bypasses snap → final_pos = move_result = (31, 30)
    # Distance from (31, 30) to opponent (32, 30) = 1.0 < DRIBBLE_RANGE=1.5
    assert dribble_target == "team_b_0"
    assert abs(final_pos[0] - 31.0) < 0.01