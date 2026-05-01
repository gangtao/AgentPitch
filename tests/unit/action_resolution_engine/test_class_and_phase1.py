"""Test Action Resolution Engine class scaffold and Phase 1 (snapshot collection).

Tests the basic class structure and Phase 1 implementation per Story 001 acceptance criteria.
Verifies dependency injection, statelessness between ticks, snapshot collection invariant,
and placeholder action record generation.
"""

from __future__ import annotations
from unittest.mock import MagicMock
import pytest

from src.foundation.action_resolution_engine import ActionResolutionEngine
from src.foundation.action import Hold
from src.foundation.sandbox import ExecutionStatus
from src.foundation.sandbox.result import SandboxResult


def _make_snap_with_n_players(n: int = 10) -> dict:
    """Helper to create a snapshot with n players for testing."""
    return {
        "players": {
            f"team_{'a' if i < 5 else 'b'}_{i % 5}": {
                "player_id": f"team_{'a' if i < 5 else 'b'}_{i % 5}",
                "team": "team_a" if i < 5 else "team_b"
            }
            for i in range(n)
        },
        "ball": {"carrier_id": None},
        "tick": 0,
        "match_phase": "in_play",
    }


@pytest.fixture
def engine():
    """Create ActionResolutionEngine with mocked dependencies."""
    deps = {name: MagicMock() for name in ("gsm", "pms", "bps", "sandbox", "fallback_handler")}
    deps["gsm"].build_tick_snapshot.return_value = _make_snap_with_n_players(10)

    # Set up sandbox to return SUCCESS with Hold action by default (Phase 2 needs this)
    deps["sandbox"].execute.return_value = SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())
    deps["gsm"].build_player_state.side_effect = lambda pid: {
        "player_id": pid,
        "position": (50.0, 30.0),
        "strength": 10
    }

    # ADR-0022 amendment d (option B): Hold actions now go through PMS for
    # snap-drift. Configure PMS to return the player's current_pos so the
    # engine's no-op short-circuit fires (no apply_move calls). Returning a
    # well-shaped tuple also prevents the MagicMock-default unpacking error.
    deps["pms"].resolve_movement.side_effect = (
        lambda pid, action, ps, snap, snap_enabled=True: (ps["position"], None)
    )

    return ActionResolutionEngine(**deps), deps


def test_init_signature(engine):
    """AC-1: Class signature accepts five injected dependencies and stores as instance attributes."""
    are, deps = engine

    # Verify all dependencies are stored as instance attributes
    assert are.gsm is deps["gsm"]
    assert are.pms is deps["pms"]
    assert are.bps is deps["bps"]
    assert are.sandbox is deps["sandbox"]
    assert are.fallback_handler is deps["fallback_handler"]


def test_stateless_between_ticks(engine):
    """AC-2: No inter-tick state persistence. Tick-local state reset between calls."""
    are, deps = engine

    # Call resolve_tick twice
    are.resolve_tick(0, [])

    # Modify tick-local state to simulate some processing
    are._ball_just_passed = True
    are._last_touching_team = "team_a"
    are._last_ball_action_pid = "team_a_0"

    # Second call should reset tick-local state
    are.resolve_tick(1, [])

    # Verify tick-local state was reset to initial values.
    # _last_ball_action_pid is intentionally PERSISTENT across ticks (used
    # for goal attribution per ADR-0016). Per ADR-0015 amendment
    # (2026-04-22) it no longer blocks pickup — the unified cooldown does.
    # _last_touching_team is ALSO persistent (added 2026-04-23 for FIFA
    # Laws 15-17 OOB restart attribution — needs to outlive the touching
    # tick to be useful when the ball goes OOB many ticks later).
    assert are._ball_just_passed is False
    assert are._last_touching_team == "team_a"  # persisted from before


def test_snapshot_once_invariant(engine):
    """AC-3: gsm.build_tick_snapshot() called exactly once per resolve_tick invocation."""
    are, deps = engine

    # Call resolve_tick once
    are.resolve_tick(5, [])

    # Verify snapshot was called exactly once
    assert deps["gsm"].build_tick_snapshot.call_count == 1


def test_resolve_tick_signature(engine):
    """AC-5: resolve_tick signature accepts (tick: int, history: list) and returns dict."""
    are, deps = engine

    # Test with various valid inputs
    result1 = are.resolve_tick(0, [])
    assert isinstance(result1, dict)

    result2 = are.resolve_tick(42, [{"some": "history"}])
    assert isinstance(result2, dict)


def test_returns_10_records_placeholder(engine):
    """AC-4: For 5v5 config (10 players), returns exactly 10 action records."""
    are, deps = engine

    # Call resolve_tick
    records = are.resolve_tick(10, [])

    # Verify 10 records returned
    assert len(records) == 10

    # Verify all player_ids are present as keys
    expected_player_ids = {f"team_{'a' if i < 5 else 'b'}_{i % 5}" for i in range(10)}
    assert set(records.keys()) == expected_player_ids

    # Verify each record has expected placeholder structure
    for player_id, record in records.items():
        assert record["action"] == "Hold"
        assert record["result"] == "ok"
        assert record["tick"] == 10
        assert isinstance(player_id, str)


def test_tick_local_state_init(engine):
    """AC-6: Tick-local state initialized at start of resolve_tick."""
    are, deps = engine

    # Create a custom mock that can capture state during execution
    state_during_snapshot = {}

    def capture_state_during_snapshot():
        # Capture the ARE's tick-local state when snapshot is called
        state_during_snapshot["ball_just_passed"] = are._ball_just_passed
        state_during_snapshot["last_touching_team"] = are._last_touching_team
        state_during_snapshot["last_ball_action_pid"] = are._last_ball_action_pid
        return _make_snap_with_n_players(10)

    deps["gsm"].build_tick_snapshot.side_effect = capture_state_during_snapshot

    # Call resolve_tick
    are.resolve_tick(0, [])

    # Verify initial state was correctly set before snapshot
    assert state_during_snapshot["ball_just_passed"] is False
    assert state_during_snapshot["last_touching_team"] is None
    assert state_during_snapshot["last_ball_action_pid"] is None


def test_no_gsm_mutation_in_phase1(engine):
    """AC-7: Phase 1 is read-only; no GameState mutation methods called."""
    are, deps = engine

    # Call resolve_tick
    are.resolve_tick(0, [])

    # Verify no mutation methods were called on GSM
    deps["gsm"].apply_move.assert_not_called()
    deps["gsm"].transfer_possession.assert_not_called()
    deps["gsm"].update_ball_position.assert_not_called()
    deps["gsm"].update_ball_velocity.assert_not_called()
    deps["gsm"].record_goal.assert_not_called()
    deps["gsm"].set_phase.assert_not_called()
    deps["gsm"].advance_tick.assert_not_called()


def test_importability():
    """AC-8: ActionResolutionEngine can be imported from package."""
    # This test passes if the import in the module header succeeded
    assert ActionResolutionEngine is not None
    assert callable(ActionResolutionEngine)


def test_different_player_counts():
    """Verify the engine works with different numbers of players."""
    # Test with 6 players
    deps = {name: MagicMock() for name in ("gsm", "pms", "bps", "sandbox", "fallback_handler")}
    deps["gsm"].build_tick_snapshot.return_value = _make_snap_with_n_players(6)
    are = ActionResolutionEngine(**deps)

    records = are.resolve_tick(0, [])
    assert len(records) == 6

    # Test with 2 players
    deps["gsm"].build_tick_snapshot.return_value = _make_snap_with_n_players(2)
    records = are.resolve_tick(0, [])
    assert len(records) == 2


def test_multiple_resolve_tick_calls_independent():
    """Verify multiple resolve_tick calls are independent and don't interfere."""
    deps = {name: MagicMock() for name in ("gsm", "pms", "bps", "sandbox", "fallback_handler")}
    deps["gsm"].build_tick_snapshot.return_value = _make_snap_with_n_players(10)
    are = ActionResolutionEngine(**deps)

    # Call multiple times with different tick values
    records1 = are.resolve_tick(5, [])
    records2 = are.resolve_tick(10, [])
    records3 = are.resolve_tick(15, [])

    # Verify each call produced correct tick values in records
    for record in records1.values():
        assert record["tick"] == 5
    for record in records2.values():
        assert record["tick"] == 10
    for record in records3.values():
        assert record["tick"] == 15

    # Verify snapshot was called exactly once per resolve_tick call
    assert deps["gsm"].build_tick_snapshot.call_count == 3