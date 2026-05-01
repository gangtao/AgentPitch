"""
Test suite for Action Resolution Engine Phase 4: Movement compute-all-then-commit + dribble contest.

Implements Story 004 QA test cases per AC-ARE-04 through AC-ARE-06.
Each test verifies that the ARE correctly orchestrates Player Movement System
and Game State Manager through the compute-all-then-commit pattern.
"""

from __future__ import annotations
from unittest.mock import MagicMock, call
import pytest

from src.foundation.action_resolution_engine.engine import ActionResolutionEngine
from src.foundation.action import Move, Hold, Pass, Tackle


@pytest.fixture
def mock_dependencies():
    """Create mocked dependencies for ActionResolutionEngine."""
    gsm = MagicMock()
    pms = MagicMock()
    bps = MagicMock()
    sandbox = MagicMock()
    fallback_handler = MagicMock()

    # Configure GSM seed
    gsm.seed = 12345
    # ADR-0022 amendment d: ARE reads gsm.config.simulation.formation_snap_enabled
    # each tick. Configure the mock to return True (default behavior) so the
    # asserted PMS calls don't have to deal with MagicMock auto-attributes.
    gsm.config.simulation.formation_snap_enabled = True

    return {
        "gsm": gsm,
        "pms": pms,
        "bps": bps,
        "sandbox": sandbox,
        "fallback_handler": fallback_handler
    }


@pytest.fixture
def sample_snap():
    """Sample game state snapshot for testing."""
    return {
        "tick": 50,
        "players": {
            "team_a_0": {
                "player_id": "team_a_0",
                "team": "team_a",
                "position": (10.0, 20.0),
                "dribbling": 10,
                "speed": 15,
                "strength": 12
            },
            "team_a_1": {
                "player_id": "team_a_1",
                "team": "team_a",
                "position": (30.0, 40.0),
                "dribbling": 8,
                "speed": 12,
                "strength": 14
            },
            "team_b_0": {
                "player_id": "team_b_0",
                "team": "team_b",
                "position": (50.0, 30.0),
                "dribbling": 12,
                "speed": 13,
                "strength": 16
            }
        },
        "ball": {
            "carrier_id": None
        }
    }


def test_ac_are_04_compute_all_then_commit_ordering(mock_dependencies, sample_snap):
    """AC-ARE-04: All pms.resolve_movement calls fire before any gsm.apply_move."""
    engine = ActionResolutionEngine(**mock_dependencies)

    # Configure PMS. Per ADR-0022 amendment d (option B), Hold actions are
    # ALSO routed through PMS so the snap can drift idle players. Use a
    # callable side_effect so we can return current_pos for the Hold (no
    # drift → no apply_move call → counts stay at 2 movers).
    def pms_side_effect(pid, action, ps, snap_dict, snap_enabled=True):
        if pid == "team_a_0":
            return ((50.0, 30.0), None)
        if pid == "team_a_1":
            return ((55.0, 35.0), None)
        return (ps["position"], None)  # team_b_0 Hold — no drift
    mock_dependencies["pms"].resolve_movement.side_effect = pms_side_effect

    validated_actions = {
        "team_a_0": Move(dx=1.0, dy=0.0, speed=0.5),
        "team_a_1": Move(dx=0.0, dy=1.0, speed=0.8),
        "team_b_0": Hold(),  # ADR-0022d: NOW routed through PMS for snap-drift check
    }

    # Act
    result = engine._resolve_phase4(validated_actions, sample_snap, 50)

    # Assert: All PMS calls happen before any GSM apply_move calls
    pms_calls = mock_dependencies["pms"].resolve_movement.call_args_list
    gsm_calls = mock_dependencies["gsm"].apply_move.call_args_list

    assert len(pms_calls) == 3  # 2 Moves + 1 Hold (option B routing)
    assert len(gsm_calls) == 2  # Only the 2 movers commit (Hold returned no-drift)

    # Verify the two Move PMS calls were made with the expected arguments
    # (the third call is for the Hold and isn't asserted here — covered by
    # test_hold_routed_through_pms_for_snap_drift).
    move_pms_calls = [
        c for c in pms_calls
        if c[0][1].get("type") == "move"
    ]
    expected_move_pms_calls = [
        call("team_a_0", {"type": "move", "dx": 1.0, "dy": 0.0, "speed": 0.5},
             mock_dependencies["gsm"].build_player_state.return_value, sample_snap,
             snap_enabled=True),
        call("team_a_1", {"type": "move", "dx": 0.0, "dy": 1.0, "speed": 0.8},
             mock_dependencies["gsm"].build_player_state.return_value, sample_snap,
             snap_enabled=True)
    ]
    assert move_pms_calls == expected_move_pms_calls

    # Verify apply_move calls
    expected_gsm_calls = [
        call("team_a_0", (50.0, 30.0)),
        call("team_a_1", (55.0, 35.0))
    ]
    assert gsm_calls == expected_gsm_calls


def test_all_pms_calls_use_same_snap(mock_dependencies, sample_snap):
    """All pms.resolve_movement calls use the SAME snap object identity."""
    engine = ActionResolutionEngine(**mock_dependencies)

    # Configure PMS
    mock_dependencies["pms"].resolve_movement.side_effect = [
        ((40.0, 20.0), None),
        ((60.0, 40.0), None)
    ]

    validated_actions = {
        "team_a_0": Move(dx=1.0, dy=0.0, speed=0.5),
        "team_a_1": Move(dx=-1.0, dy=1.0, speed=0.3)
    }

    # Act
    engine._resolve_phase4(validated_actions, sample_snap, 50)

    # Assert: All calls used the same snap object
    pms_calls = mock_dependencies["pms"].resolve_movement.call_args_list
    assert len(pms_calls) == 2

    # Both calls should have received the exact same snap object
    snap_arg_call1 = pms_calls[0][0][3]  # 4th positional arg (snap)
    snap_arg_call2 = pms_calls[1][0][3]
    assert snap_arg_call1 is sample_snap
    assert snap_arg_call2 is sample_snap
    assert snap_arg_call1 is snap_arg_call2


def test_non_move_non_hold_actions_skipped(mock_dependencies, sample_snap):
    """Pass / Shoot / Tackle / Pickup don't trigger PMS calls — those are
    explicit actions that pin the player's location.

    Per ADR-0022 amendment d (option B), Hold IS now routed through PMS
    so the snap can drift idle players toward formation. This test only
    covers the truly non-positional actions.
    """
    engine = ActionResolutionEngine(**mock_dependencies)
    # No Hold here — covered by a separate test below.
    validated_actions = {
        "team_a_1": Pass(target_pos=(70.0, 30.0), power=5),
        "team_b_0": Tackle(target_player_id="team_a_0")
    }

    # Act
    result = engine._resolve_phase4(validated_actions, sample_snap, 50)

    # Assert: No PMS calls for Pass/Tackle
    assert mock_dependencies["pms"].resolve_movement.call_count == 0
    assert mock_dependencies["gsm"].apply_move.call_count == 0
    assert result == set()  # No dribble consumed


def test_hold_routed_through_pms_for_snap_drift(mock_dependencies, sample_snap):
    """Per ADR-0022 amendment d (option B): Hold actions ALSO go through PMS
    so the soft snap can drift idle players toward their dynamic anchor.
    Carriers and snap_disabled players don't get drift (PMS short-circuits)."""
    # Configure PMS to return a drifted position (simulates snap pulling
    # the player slightly toward anchor).
    mock_dependencies["pms"].resolve_movement.return_value = ((9.5, 19.5), None)

    engine = ActionResolutionEngine(**mock_dependencies)
    validated_actions = {"team_a_0": Hold()}

    engine._resolve_phase4(validated_actions, sample_snap, 50)

    # PMS was called once (for the Hold)
    assert mock_dependencies["pms"].resolve_movement.call_count == 1
    # The (drifted) position was committed.
    assert mock_dependencies["gsm"].apply_move.call_count >= 1


def test_dribble_contest_formula(mock_dependencies, sample_snap):
    """Dribble contest formula: attacker_power = (dribbling + speed)/2, prob = attacker_power / (attacker_power + defender.strength)."""
    engine = ActionResolutionEngine(**mock_dependencies)

    # Configure PMS to return a dribble target
    mock_dependencies["pms"].resolve_movement.return_value = ((55.0, 30.0), "team_b_0")

    # Mock hash_01 to return specific value for testing
    import src.foundation.action_resolution_engine.engine as engine_mod
    original_hash_01 = engine_mod.hash_01
    engine_mod.hash_01 = MagicMock(return_value=0.4)

    try:
        validated_actions = {
            "team_a_0": Move(dx=1.0, dy=0.0, speed=0.5)
        }

        # Act
        result = engine._resolve_phase4(validated_actions, sample_snap, 50)

        # Assert: hash_01 called with correct arguments
        engine_mod.hash_01.assert_called_once_with(
            12345, 50, "team_a_0", "team_b_0"  # seed, tick, carrier_id, defender_id
        )

        # Verify dribble contest math:
        # carrier = team_a_0: dribbling=10, speed=15
        # attacker_power = (10 + 15) / 2 = 12.5
        # defender = team_b_0: strength=16
        # prob = 12.5 / (12.5 + 16) = 12.5 / 28.5 ≈ 0.439
        # draw = 0.4 < prob ≈ 0.439 → SUCCESS, no transfer
        assert mock_dependencies["gsm"].transfer_possession.call_count == 0
        assert result == {"team_b_0"}  # Defender consumed by dribble

    finally:
        # Restore original function
        engine_mod.hash_01 = original_hash_01


def test_dribble_contest_fail_transfers_possession(mock_dependencies, sample_snap):
    """When draw >= prob, gsm.transfer_possession(carrier_id, defender_id) is called."""
    engine = ActionResolutionEngine(**mock_dependencies)

    # Configure PMS to return a dribble target
    mock_dependencies["pms"].resolve_movement.return_value = ((55.0, 30.0), "team_b_0")

    # Mock hash_01 to return value that causes failure
    import src.foundation.action_resolution_engine.engine as engine_mod
    original_hash_01 = engine_mod.hash_01
    engine_mod.hash_01 = MagicMock(return_value=0.8)  # High value → fail

    try:
        validated_actions = {
            "team_a_0": Move(dx=1.0, dy=0.0, speed=0.5)
        }

        # Act
        result = engine._resolve_phase4(validated_actions, sample_snap, 50)

        # Assert: transfer_possession called on failure
        mock_dependencies["gsm"].transfer_possession.assert_called_once_with("team_a_0", "team_b_0")
        assert result == {"team_b_0"}  # Defender consumed by dribble

    finally:
        engine_mod.hash_01 = original_hash_01


def test_dribble_contest_success_no_transfer(mock_dependencies, sample_snap):
    """When draw < prob, no transfer_possession call (carrier keeps ball)."""
    engine = ActionResolutionEngine(**mock_dependencies)

    # Configure PMS to return a dribble target
    mock_dependencies["pms"].resolve_movement.return_value = ((55.0, 30.0), "team_b_0")

    # Mock hash_01 to return value that causes success
    import src.foundation.action_resolution_engine.engine as engine_mod
    original_hash_01 = engine_mod.hash_01
    engine_mod.hash_01 = MagicMock(return_value=0.1)  # Low value → success

    try:
        validated_actions = {
            "team_a_0": Move(dx=1.0, dy=0.0, speed=0.5)
        }

        # Act
        result = engine._resolve_phase4(validated_actions, sample_snap, 50)

        # Assert: no transfer_possession call on success
        assert mock_dependencies["gsm"].transfer_possession.call_count == 0
        assert result == {"team_b_0"}  # Defender still consumed by dribble

    finally:
        engine_mod.hash_01 = original_hash_01


def test_ac_are_06_dribble_consumed_tracking(mock_dependencies, sample_snap):
    """AC-ARE-06: Defenders consumed by dribble are tracked in returned set."""
    engine = ActionResolutionEngine(**mock_dependencies)

    # Configure multiple dribble contests
    # ADR-0022 amendment d: ARE now passes snap_enabled kwarg to PMS, so the
    # mock side_effect must accept it.
    def pms_side_effect(pid, action, player_state, snap, snap_enabled=True):
        if pid == "team_a_0":
            return ((55.0, 30.0), "team_b_0")
        elif pid == "team_a_1":
            return ((35.0, 45.0), "team_b_0")  # Same defender
        else:
            return ((40.0, 25.0), None)

    mock_dependencies["pms"].resolve_movement.side_effect = pms_side_effect

    # Mock hash_01 for deterministic outcomes
    import src.foundation.action_resolution_engine.engine as engine_mod
    original_hash_01 = engine_mod.hash_01
    engine_mod.hash_01 = MagicMock(return_value=0.5)

    try:
        validated_actions = {
            "team_a_0": Move(dx=1.0, dy=0.0, speed=0.5),
            "team_a_1": Move(dx=0.0, dy=1.0, speed=0.8),
        }

        # Act
        result = engine._resolve_phase4(validated_actions, sample_snap, 50)

        # Assert: dribble_consumed contains defender targeted by dribble
        assert result == {"team_b_0"}
        assert hasattr(engine, "dribble_consumed")
        assert engine.dribble_consumed == {"team_b_0"}

    finally:
        engine_mod.hash_01 = original_hash_01


def test_deterministic_outcomes_same_inputs(mock_dependencies, sample_snap):
    """Calling _resolve_phase4 twice with same inputs produces same dribble outcomes."""
    engine = ActionResolutionEngine(**mock_dependencies)

    # Configure PMS
    mock_dependencies["pms"].resolve_movement.side_effect = [
        ((55.0, 30.0), "team_b_0"),  # First call
        ((55.0, 30.0), "team_b_0"),  # Second call (same output)
    ]

    validated_actions = {
        "team_a_0": Move(dx=1.0, dy=0.0, speed=0.5)
    }

    # Act: call twice
    result1 = engine._resolve_phase4(validated_actions, sample_snap, 50)

    # Reset mocks for second call
    mock_dependencies["gsm"].reset_mock()
    mock_dependencies["pms"].reset_mock()
    mock_dependencies["pms"].resolve_movement.side_effect = [((55.0, 30.0), "team_b_0")]

    result2 = engine._resolve_phase4(validated_actions, sample_snap, 50)

    # Assert: same outcomes (deterministic hash_01)
    assert result1 == result2


def test_no_moves_only_holds_pms_called_for_each_hold(mock_dependencies, sample_snap):
    """Per ADR-0022 amendment d (option B): Hold actions go through PMS so
    snap can drift idle players. With 3 Hold actions and PMS configured to
    return current_pos (no drift — what happens when snap is disabled or
    player is the carrier), apply_move is NOT called (no-op short-circuit).
    """
    # PMS returns the same position it received (no-op — simulates either
    # snap_enabled=False or the player being a carrier, both of which make
    # PMS return final_pos == current_pos).
    def no_drift(pid, action, ps, snapshot, snap_enabled=True):
        return (ps["position"], None)
    mock_dependencies["pms"].resolve_movement.side_effect = no_drift

    engine = ActionResolutionEngine(**mock_dependencies)
    validated_actions = {
        "team_a_0": Hold(),
        "team_a_1": Hold(),
        "team_b_0": Hold()
    }

    # Act
    engine._resolve_phase4(validated_actions, sample_snap, 50)

    # PMS called for each Hold (snap-drift candidate)
    assert mock_dependencies["pms"].resolve_movement.call_count == 3
    # But apply_move was NOT called — final_pos == current_pos for every Hold,
    # so the engine short-circuits the commit (avoids no-op apply_move calls).
    assert mock_dependencies["gsm"].apply_move.call_count == 0
    assert mock_dependencies["gsm"].transfer_possession.call_count == 0