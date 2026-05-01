"""Tests for ARE Story 002: Phase 2 callback invocation + fallback routing."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from src.foundation.action import Hold, Move
from src.foundation.action_resolution_engine import ActionResolutionEngine
from src.foundation.sandbox import ExecutionStatus
from src.foundation.sandbox.result import SandboxResult
from src.foundation.fallback.types import FallbackResult


def _make_snap_10():
    """Create a snapshot with 10 players for testing."""
    return {
        "players": {
            f"team_a_{i}": {
                "player_id": f"team_a_{i}",
                "team": "team_a",
                "role": "MID"
            }
            for i in range(5)
        } | {
            f"team_b_{i}": {
                "player_id": f"team_b_{i}",
                "team": "team_b",
                "role": "MID"
            }
            for i in range(5)
        },
        "ball": {"carrier_id": "team_a_2"},
        "field": {"width": 100.0, "height": 60.0},
    }


@pytest.fixture
def engine_and_deps():
    """Create engine and mocked dependencies for testing."""
    deps = {name: MagicMock() for name in ("gsm", "pms", "bps", "sandbox", "fallback_handler")}
    deps["gsm"].build_tick_snapshot.return_value = _make_snap_10()
    deps["gsm"].build_player_state.side_effect = lambda pid: {
        "player_id": pid,
        "position": (50.0, 30.0),
        "strength": 10
    }
    # SUCCESS by default
    deps["sandbox"].execute.return_value = SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())
    # PMS returns a default tuple so Phase 4 (added in Story 004) doesn't blow up
    deps["pms"].resolve_movement.return_value = ((50.0, 30.0), None)
    engine = ActionResolutionEngine(**deps)
    return engine, deps


def test_ac1_all_10_players_invoked(engine_and_deps):
    """AC-1: All 10 players invoked - sandbox.execute called exactly 10 times."""
    engine, deps = engine_and_deps
    engine.resolve_tick(tick=0, history=[])
    assert deps["sandbox"].execute.call_count == 10


def test_ac2_game_state_has_my_player_id_and_my_team(engine_and_deps):
    """AC-2: Each game_state has my_player_id and my_team matching the player."""
    engine, deps = engine_and_deps
    engine.resolve_tick(tick=0, history=[])

    for call in deps["sandbox"].execute.call_args_list:
        args = call.args
        pid = args[0]
        gs = args[1]
        assert gs["my_player_id"] == pid
        expected_team = "team_a" if pid.startswith("team_a") else "team_b"
        assert gs["my_team"] == expected_team


def test_ac3_player_state_built_per_player(engine_and_deps):
    """AC-3: player_state from build_player_state - called for each player."""
    engine, deps = engine_and_deps
    engine.resolve_tick(tick=0, history=[])
    # Phase 2 calls build_player_state once per player; later phases (4/6/7) may also call.
    # AC-3 only requires the per-callback call exists — assert at least 10.
    assert deps["gsm"].build_player_state.call_count >= 10


def test_ac4_success_routes_to_action(engine_and_deps):
    """AC-4: SUCCESS status routes directly to the returned action."""
    engine, deps = engine_and_deps
    move = Move(dx=1.0, dy=0.0, speed=0.5)
    deps["sandbox"].execute.return_value = SandboxResult(status=ExecutionStatus.SUCCESS, action=move)
    records = engine.resolve_tick(tick=0, history=[])

    # All 10 records should be Move
    for rec in records.values():
        assert rec["action"] == "Move"
    # fallback never called
    deps["fallback_handler"].handle.assert_not_called()


def test_ac5_non_success_routes_to_fallback(engine_and_deps):
    """AC-5: Non-SUCCESS status routes to fallback handler."""
    engine, deps = engine_and_deps
    deps["sandbox"].execute.return_value = SandboxResult(status=ExecutionStatus.EXCEPTION, error_type="ValueError")
    deps["fallback_handler"].handle.return_value = FallbackResult(action=Hold(), log_event=None)
    records = engine.resolve_tick(tick=0, history=[])

    assert deps["fallback_handler"].handle.call_count == 10
    for rec in records.values():
        assert rec["action"] == "Hold"


def test_ac6_collect_all_before_advance(engine_and_deps):
    """AC-6: Phase 2 collects all actions before any phase advances."""
    engine, deps = engine_and_deps
    # All 10 sandbox.execute calls happen before resolve_tick returns
    engine.resolve_tick(tick=0, history=[])
    # Just confirm it runs to completion with 10 sandbox calls
    assert deps["sandbox"].execute.call_count == 10


def test_ac7_all_fallback_no_raise(engine_and_deps):
    """AC-7: AC-ARE-14 plumbing - all 10 callbacks failing must not crash."""
    engine, deps = engine_and_deps
    deps["sandbox"].execute.return_value = SandboxResult(status=ExecutionStatus.EXCEPTION, error_type="RuntimeError")
    deps["fallback_handler"].handle.return_value = FallbackResult(action=Hold(), log_event=None)

    # Should not raise
    records = engine.resolve_tick(tick=0, history=[])
    assert len(records) == 10


def test_ac8_provider_arg_to_fallback(engine_and_deps):
    """AC-8: Provider arg from snapshot teams dict (currently defaults to 'unknown')."""
    engine, deps = engine_and_deps
    deps["sandbox"].execute.return_value = SandboxResult(status=ExecutionStatus.EXCEPTION, error_type="X")
    deps["fallback_handler"].handle.return_value = FallbackResult(action=Hold(), log_event=None)
    engine.resolve_tick(tick=0, history=[])

    # Inspect each fallback.handle call's args
    for call in deps["fallback_handler"].handle.call_args_list:
        args = call.args
        # Signature: handle(result, player_id, team, provider, tick)
        provider = args[3]  # provider argument
        assert provider == "unknown"  # Current default implementation


def test_mixed_success_and_failure(engine_and_deps):
    """Test mix of successful and failed callbacks."""
    engine, deps = engine_and_deps

    # First 5 succeed, next 5 fail
    def execute_side_effect(pid, *args):
        if pid.startswith("team_a"):
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Move(dx=1.0, dy=0.0, speed=0.5))
        else:
            return SandboxResult(status=ExecutionStatus.TIMEOUT, error_type=None)

    deps["sandbox"].execute.side_effect = execute_side_effect
    deps["fallback_handler"].handle.return_value = FallbackResult(action=Hold(), log_event=None)

    records = engine.resolve_tick(tick=0, history=[])

    # Check team_a got Move, team_b got Hold
    for pid, record in records.items():
        if pid.startswith("team_a"):
            assert record["action"] == "Move"
        else:
            assert record["action"] == "Hold"

    # fallback called 5 times (for team_b)
    assert deps["fallback_handler"].handle.call_count == 5


def test_sandbox_context_preserved(engine_and_deps):
    """Test that sandbox.execute is called with correct args."""
    engine, deps = engine_and_deps
    engine.resolve_tick(tick=123, history=["prev_tick"])

    # Verify all calls have correct structure
    for call in deps["sandbox"].execute.call_args_list:
        pid, game_state, player_state, history = call.args

        # Verify game_state contains snapshot data plus injected fields
        assert "players" in game_state
        assert "ball" in game_state
        assert "field" in game_state
        assert game_state["my_player_id"] == pid

        # Verify player_state is from build_player_state
        assert player_state["player_id"] == pid

        # Verify history passed through
        assert history == ["prev_tick"]