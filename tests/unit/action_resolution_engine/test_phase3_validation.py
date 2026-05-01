"""Tests for ARE Story 003: Phase 3 — Action validation + normalization."""

from __future__ import annotations
import pytest
from unittest.mock import MagicMock

from src.foundation.action import Move, Pass, Shoot, Tackle, Hold
from src.foundation.action_resolution_engine import ActionResolutionEngine
from src.foundation.sandbox import ExecutionStatus
from src.foundation.sandbox.result import SandboxResult


def _make_snap_with_carrier(carrier_id: str = "team_a_2") -> dict:
    """Create a snapshot with 10 players and specified ball carrier."""
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
        "ball": {"carrier_id": carrier_id},
        "field": {"width": 100.0, "height": 60.0},
    }


@pytest.fixture
def engine_and_deps():
    """Create engine and mocked dependencies for testing."""
    deps = {name: MagicMock() for name in ("gsm", "pms", "bps", "sandbox", "fallback_handler")}
    deps["gsm"].build_tick_snapshot.return_value = _make_snap_with_carrier("team_a_2")

    # Default player state with strength=10
    deps["gsm"].build_player_state.side_effect = lambda pid: {
        "player_id": pid,
        "position": (50.0, 30.0),
        "strength": 10
    }

    # Default to Hold action to avoid validation issues
    deps["sandbox"].execute.return_value = SandboxResult(
        status=ExecutionStatus.SUCCESS,
        action=Hold()
    )
    # PMS default for Phase 4 (Story 004 added)
    deps["pms"].resolve_movement.return_value = ((50.0, 30.0), None)

    engine = ActionResolutionEngine(**deps)
    return engine, deps


def test_ac1_move_speed_clamp_above_one(engine_and_deps):
    """AC-1: Move speed clamping - speed=2.5 clamped to 1.0."""
    engine, deps = engine_and_deps

    # Configure sandbox to return Move with speed > 1.0 for one player
    deps["sandbox"].execute.side_effect = [
        SandboxResult(status=ExecutionStatus.SUCCESS, action=Move(dx=1.0, dy=0.0, speed=2.5))
    ] + [
        SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())
    ] * 9  # Other 9 players get Hold

    records = engine.resolve_tick(0, [])

    # First player should have Move (not substituted to Hold)
    first_pid = list(records.keys())[0]
    assert records[first_pid]["action"] == "Move"
    assert records[first_pid]["result"] == "ok"  # Speed clamping doesn't generate a reason


def test_ac1_move_speed_clamp_below_zero(engine_and_deps):
    """AC-1: Move speed clamping - negative speed clamped to 0.0."""
    engine, deps = engine_and_deps

    # Configure sandbox to return Move with negative speed
    deps["sandbox"].execute.side_effect = [
        SandboxResult(status=ExecutionStatus.SUCCESS, action=Move(dx=1.0, dy=0.0, speed=-0.3))
    ] + [
        SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())
    ] * 9

    records = engine.resolve_tick(0, [])

    # First player should have Hold (substituted due to speed=0.0)
    first_pid = list(records.keys())[0]
    assert records[first_pid]["action"] == "Hold"
    assert records[first_pid]["result"] == "zero_move_substituted"


def test_ac2_move_zero_speed_substitution(engine_and_deps):
    """AC-2: Move zero substitution - speed=0.0 substituted with Hold."""
    engine, deps = engine_and_deps

    deps["sandbox"].execute.side_effect = [
        SandboxResult(status=ExecutionStatus.SUCCESS, action=Move(dx=1.0, dy=0.0, speed=0.0))
    ] + [
        SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())
    ] * 9

    records = engine.resolve_tick(0, [])

    first_pid = list(records.keys())[0]
    assert records[first_pid]["action"] == "Hold"
    assert records[first_pid]["result"] == "zero_move_substituted"


def test_ac2_move_zero_direction_substitution(engine_and_deps):
    """AC-2: Move zero substitution - dx=dy=0 substituted with Hold."""
    engine, deps = engine_and_deps

    deps["sandbox"].execute.side_effect = [
        SandboxResult(status=ExecutionStatus.SUCCESS, action=Move(dx=0.0, dy=0.0, speed=1.0))
    ] + [
        SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())
    ] * 9

    records = engine.resolve_tick(0, [])

    first_pid = list(records.keys())[0]
    assert records[first_pid]["action"] == "Hold"
    assert records[first_pid]["result"] == "zero_move_substituted"


def test_ac3_pass_power_capped(engine_and_deps):
    """AC-3 (AC-ARE-03): Pass power cap - power > strength gets capped."""
    engine, deps = engine_and_deps

    # Set up carrier with strength=10, Pass with power=15
    deps["gsm"].build_player_state.side_effect = lambda pid: {
        "player_id": pid,
        "position": (50.0, 30.0),
        "strength": 10 if pid == "team_a_2" else 10
    }

    # Configure team_a_2 (carrier) to return Pass with power=15
    def execute_side_effect(pid, *args):
        if pid == "team_a_2":
            return SandboxResult(
                status=ExecutionStatus.SUCCESS,
                action=Pass(target_pos=(60.0, 30.0), power=15)
            )
        else:
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())

    deps["sandbox"].execute.side_effect = execute_side_effect

    records = engine.resolve_tick(0, [])

    carrier_record = records["team_a_2"]
    assert carrier_record["action"] == "Pass"
    assert carrier_record["result"] == "power_capped"
    assert carrier_record["effective_power"] == 10  # Capped to strength


def test_ac4_pass_power_within_cap_unchanged(engine_and_deps):
    """AC-4: Pass power within cap - power=8 from strength=10 unchanged."""
    engine, deps = engine_and_deps

    def execute_side_effect(pid, *args):
        if pid == "team_a_2":
            return SandboxResult(
                status=ExecutionStatus.SUCCESS,
                action=Pass(target_pos=(60.0, 30.0), power=8)
            )
        else:
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())

    deps["sandbox"].execute.side_effect = execute_side_effect

    records = engine.resolve_tick(0, [])

    carrier_record = records["team_a_2"]
    assert carrier_record["action"] == "Pass"
    assert carrier_record["result"] == "ok"  # No power_capped reason
    assert "effective_power" not in carrier_record  # Only added when capped


def test_ac5_pass_power_floored_to_one(engine_and_deps):
    """AC-5: Pass power floored to 1 - power=0 becomes power=1."""
    engine, deps = engine_and_deps

    def execute_side_effect(pid, *args):
        if pid == "team_a_2":
            return SandboxResult(
                status=ExecutionStatus.SUCCESS,
                action=Pass(target_pos=(60.0, 30.0), power=0)
            )
        else:
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())

    deps["sandbox"].execute.side_effect = execute_side_effect

    records = engine.resolve_tick(0, [])

    carrier_record = records["team_a_2"]
    assert carrier_record["action"] == "Pass"
    assert carrier_record["result"] == "ok"


def test_ac6_pass_non_carrier_substituted(engine_and_deps):
    """AC-6 (AC-ARE-09): Pass from non-carrier substituted with Hold."""
    engine, deps = engine_and_deps

    # team_a_2 is carrier, team_a_1 tries to Pass
    def execute_side_effect(pid, *args):
        if pid == "team_a_1":  # Non-carrier
            return SandboxResult(
                status=ExecutionStatus.SUCCESS,
                action=Pass(target_pos=(60.0, 30.0), power=10)
            )
        else:
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())

    deps["sandbox"].execute.side_effect = execute_side_effect

    records = engine.resolve_tick(0, [])

    non_carrier_record = records["team_a_1"]
    assert non_carrier_record["action"] == "Hold"
    assert non_carrier_record["result"] == "not_carrier"


def test_ac7_shoot_non_carrier_substituted(engine_and_deps):
    """AC-7 (AC-ARE-09): Shoot from non-carrier substituted with Hold."""
    engine, deps = engine_and_deps

    def execute_side_effect(pid, *args):
        if pid == "team_a_1":  # Non-carrier
            return SandboxResult(
                status=ExecutionStatus.SUCCESS,
                action=Shoot(angle=0.0, power=10)
            )
        else:
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())

    deps["sandbox"].execute.side_effect = execute_side_effect

    records = engine.resolve_tick(0, [])

    non_carrier_record = records["team_a_1"]
    assert non_carrier_record["action"] == "Hold"
    assert non_carrier_record["result"] == "not_carrier"


def test_ac8_tackle_own_team_substituted(engine_and_deps):
    """AC-8: Tackle own team member substituted with Hold."""
    engine, deps = engine_and_deps

    def execute_side_effect(pid, *args):
        if pid == "team_a_1":
            return SandboxResult(
                status=ExecutionStatus.SUCCESS,
                action=Tackle(target_player_id="team_a_3")  # Same team
            )
        else:
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())

    deps["sandbox"].execute.side_effect = execute_side_effect

    records = engine.resolve_tick(0, [])

    tackler_record = records["team_a_1"]
    assert tackler_record["action"] == "Hold"
    assert tackler_record["result"] == "same_team_tackle"


def test_ac9_tackle_unknown_target_substituted(engine_and_deps):
    """AC-9: Tackle unknown target substituted with Hold."""
    engine, deps = engine_and_deps

    def execute_side_effect(pid, *args):
        if pid == "team_a_1":
            return SandboxResult(
                status=ExecutionStatus.SUCCESS,
                action=Tackle(target_player_id="team_z_99")  # Unknown player
            )
        else:
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())

    deps["sandbox"].execute.side_effect = execute_side_effect

    records = engine.resolve_tick(0, [])

    tackler_record = records["team_a_1"]
    assert tackler_record["action"] == "Hold"
    assert tackler_record["result"] == "unknown_target"


def test_ac10_tackle_range_not_checked(engine_and_deps):
    """AC-10: Tackle range NOT checked in Phase 3 - valid opposing target passes."""
    engine, deps = engine_and_deps

    def execute_side_effect(pid, *args):
        if pid == "team_a_1":
            return SandboxResult(
                status=ExecutionStatus.SUCCESS,
                action=Tackle(target_player_id="team_b_2")  # Valid opposing player
            )
        else:
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())

    deps["sandbox"].execute.side_effect = execute_side_effect

    records = engine.resolve_tick(0, [])

    tackler_record = records["team_a_1"]
    assert tackler_record["action"] == "Tackle"  # Not substituted by Phase 3 (range deferred to Phase 6)
    # Phase 6 may resolve to out_of_range / no_op_carrier_changed / failed depending on state;
    # this test only asserts Phase 3 didn't substitute to Hold.


def test_shoot_power_cap_and_effective_power(engine_and_deps):
    """Test Shoot power capping similar to Pass."""
    engine, deps = engine_and_deps

    # Set carrier strength=8, Shoot with power=12
    deps["gsm"].build_player_state.side_effect = lambda pid: {
        "player_id": pid,
        "position": (50.0, 30.0),
        "strength": 8 if pid == "team_a_2" else 10
    }

    def execute_side_effect(pid, *args):
        if pid == "team_a_2":
            return SandboxResult(
                status=ExecutionStatus.SUCCESS,
                action=Shoot(angle=15.0, power=12)
            )
        else:
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())

    deps["sandbox"].execute.side_effect = execute_side_effect

    records = engine.resolve_tick(0, [])

    carrier_record = records["team_a_2"]
    assert carrier_record["action"] == "Shoot"
    assert carrier_record["result"] == "power_capped"
    assert carrier_record["effective_power"] == 8


def test_hold_action_passes_through(engine_and_deps):
    """Test Hold action passes through validation unchanged."""
    engine, deps = engine_and_deps

    # All players return Hold
    deps["sandbox"].execute.return_value = SandboxResult(
        status=ExecutionStatus.SUCCESS,
        action=Hold()
    )

    records = engine.resolve_tick(0, [])

    for record in records.values():
        assert record["action"] == "Hold"
        assert record["result"] == "ok"


def test_mixed_actions_validation(engine_and_deps):
    """Test various actions together to ensure proper validation."""
    engine, deps = engine_and_deps

    def execute_side_effect(pid, *args):
        if pid == "team_a_0":
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Move(dx=1.0, dy=0.0, speed=1.5))  # Clamp speed
        elif pid == "team_a_1":
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Move(dx=0.0, dy=0.0, speed=1.0))  # Zero move
        elif pid == "team_a_2":  # Carrier
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Pass(target_pos=(60.0, 30.0), power=15))  # Power cap
        elif pid == "team_a_3":
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Pass(target_pos=(60.0, 30.0), power=8))   # Non-carrier
        elif pid == "team_b_0":
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Tackle(target_player_id="team_a_2"))  # Valid tackle
        elif pid == "team_b_1":
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Tackle(target_player_id="team_b_2"))  # Same team
        else:
            return SandboxResult(status=ExecutionStatus.SUCCESS, action=Hold())

    deps["sandbox"].execute.side_effect = execute_side_effect

    records = engine.resolve_tick(0, [])

    # Check individual validations
    assert records["team_a_0"]["action"] == "Move"  # Speed clamped but still Move
    assert records["team_a_0"]["result"] == "ok"

    assert records["team_a_1"]["action"] == "Hold"  # Zero move substituted
    assert records["team_a_1"]["result"] == "zero_move_substituted"

    assert records["team_a_2"]["action"] == "Pass"  # Carrier can pass, power capped
    assert records["team_a_2"]["result"] == "power_capped"
    assert records["team_a_2"]["effective_power"] == 10

    assert records["team_a_3"]["action"] == "Hold"  # Non-carrier pass substituted
    assert records["team_a_3"]["result"] == "not_carrier"

    assert records["team_b_0"]["action"] == "Tackle"  # Valid tackle (Phase 3 didn't substitute)
    # Phase 6 may resolve to out_of_range / no_op_carrier_changed; this test only asserts Phase 3 passed it through.

    assert records["team_b_1"]["action"] == "Hold"  # Same team tackle substituted
    assert records["team_b_1"]["result"] == "same_team_tackle"