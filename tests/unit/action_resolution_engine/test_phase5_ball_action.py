"""
Test suite for Action Resolution Engine Phase 5: Ball action (Pass + Shoot resolution).

Implements Story 005 QA test cases per AC-ARE-05 through AC-ARE-15.
Each test verifies that the ARE correctly resolves Pass and Shoot actions
for the current ball carrier, updates ball physics state, and sets proper
flags for subsequent phases.
"""

from __future__ import annotations
from unittest.mock import MagicMock, patch
import math
import pytest

from src.foundation.action_resolution_engine.engine import ActionResolutionEngine
from src.foundation.action import Pass, Shoot, Hold, Move


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
                "position": (50.0, 30.0),
                "skill": 16,  # 16/20 = 0.8 pass success probability
            },
            "team_b_0": {
                "player_id": "team_b_0",
                "team": "team_b",
                "position": (25.0, 40.0),
                "skill": 10,  # 10/20 = 0.5 pass success probability
            }
        },
        "ball": {
            "carrier_id": "team_a_0"
        },
        "field": {
            "team_a_goal_x": 0.0,
            "team_b_goal_x": 100.0,
        }
    }


def test_ac_are_05_carrier_only_pass(mock_dependencies, sample_snap):
    """AC-ARE-05: Only current carrier can execute Pass action."""
    engine = ActionResolutionEngine(**mock_dependencies)

    # Configure build_player_state for has_ball checks
    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Pass(target_pos=(60.0, 30.0), power=10),  # Current carrier
        "team_b_0": Pass(target_pos=(30.0, 40.0), power=8),   # Non-carrier
    }

    # Act
    result = engine._resolve_phase5(validated_actions, sample_snap, 50, "team_a_0")

    # Assert: Only carrier's Pass is executed
    assert len(result) == 1
    assert "team_a_0" in result
    assert "team_b_0" not in result
    assert result["team_a_0"]["action"] == "Pass"


def test_ac_are_06_pass_accuracy_formula(mock_dependencies, sample_snap):
    """AC-ARE-06: Pass accuracy uses F2 formula (skill/20)."""
    engine = ActionResolutionEngine(**mock_dependencies)

    # Configure build_player_state
    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Pass(target_pos=(60.0, 30.0), power=10),
    }

    # Mock hash_01 to control accuracy: 0.7 draw vs 0.8 probability = accurate
    with patch('src.foundation.simulation_utils.hash_01') as mock_hash:
        mock_hash.side_effect = lambda seed, tick, pid, context: {
            ("pass_accuracy",): 0.7,  # < 0.8 = accurate
            ("pass_unit",): 0.25,     # angle = 0.25 * 2π = π/2 radians
            ("pass_radius",): 0.4,    # radius = 0.4 * 0.5 = 0.2
        }.get((context,), 0.0)

        # Act
        result = engine._resolve_phase5(validated_actions, sample_snap, 50, "team_a_0")

        # Assert
        assert result["team_a_0"]["result"] == "ok"  # accurate pass


def test_ac_are_07_pass_landing_continuous_deviation(mock_dependencies, sample_snap):
    """AC-ARE-07 (ADR-0018, 2026-04-22): pass landing uses continuous
    skill-based deviation. With skill=16 and pass_max_deviation default
    8.0u, the spread_factor = (1 - 16/20)^0.7 ≈ 0.3247, so max landing
    deviation is 0.3247 * 8.0 ≈ 2.598u. mag_draw=0.5 + ang_draw=0 yields
    a landing 1.299u along +x of the target."""
    engine = ActionResolutionEngine(**mock_dependencies)

    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Pass(target_pos=(60.0, 30.0), power=10),
    }

    with patch('src.foundation.action_resolution_engine.engine.hash_01') as mock_hash:
        mock_hash.side_effect = lambda seed, tick, pid, context: {
            ("pass_dev_mag",):   0.5,  # half of spread max
            ("pass_dev_angle",): 0.0,  # angle 0 → +x
        }.get((context,), 0.0)

        result = engine._resolve_phase5(validated_actions, sample_snap, 50, "team_a_0")

        # spread_factor * pass_max_deviation * mag_draw = 0.3247 * 8.0 * 0.5
        expected_mag = ((1 - 16/20) ** 0.7) * 8.0 * 0.5
        landing = result["team_a_0"]["landing_pos"]
        assert abs(landing[0] - (60.0 + expected_mag)) < 1e-6
        assert abs(landing[1] - 30.0) < 1e-6
        # Pass result is now always "ok" (no binary inaccurate label).
        assert result["team_a_0"]["result"] == "ok"


def test_ac_are_08_pass_max_deviation_low_skill(mock_dependencies, sample_snap):
    """AC-ARE-08 (ADR-0018, 2026-04-22): low-skill players have wider spread.
    With skill=1, spread_factor = (19/20)^0.7 ≈ 0.928, so max deviation is
    ~7.4u. Verifies the formula behaves correctly at the low-skill extreme.

    Replaces the pre-ADR-0018 "inaccurate at exactly MAX_DEVIATION" test —
    that binary outcome no longer exists."""
    engine = ActionResolutionEngine(**mock_dependencies)

    # Override skill via a patched players dict in the snap.
    snap = {**sample_snap}
    snap["players"] = dict(sample_snap["players"])
    snap["players"]["team_a_0"] = {**sample_snap["players"]["team_a_0"], "skill": 1}

    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Pass(target_pos=(60.0, 30.0), power=10),
    }

    with patch('src.foundation.action_resolution_engine.engine.hash_01') as mock_hash:
        mock_hash.side_effect = lambda seed, tick, pid, context: {
            ("pass_dev_mag",):   1.0,  # max draw → max deviation for this skill
            ("pass_dev_angle",): 0.0,
        }.get((context,), 0.0)

        result = engine._resolve_phase5(validated_actions, snap, 50, "team_a_0")

        expected_mag = ((1 - 1/20) ** 0.7) * 8.0 * 1.0  # ≈ 7.43u
        landing = result["team_a_0"]["landing_pos"]
        assert abs(landing[0] - (60.0 + expected_mag)) < 1e-6
        assert abs(landing[1] - 30.0) < 1e-6
        assert result["team_a_0"]["result"] == "ok"


def test_ac_are_09_ball_velocity_formula(mock_dependencies, sample_snap):
    """AC-ARE-09: Ball velocity calculated correctly from pass direction and power."""
    engine = ActionResolutionEngine(**mock_dependencies)

    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Pass(target_pos=(60.0, 40.0), power=10),  # 10 units right, 10 units up
    }

    with patch('src.foundation.action_resolution_engine.engine.hash_01') as mock_hash:
        mock_hash.side_effect = lambda seed, tick, pid, context: {
            ("pass_accuracy",): 0.7,
            ("pass_unit",): 0.0,      # no deviation
            ("pass_radius",): 0.0,    # landing at exact target
        }.get((context,), 0.0)

        # Act
        engine._resolve_phase5(validated_actions, sample_snap, 50, "team_a_0")

        # Assert: Check update_ball_velocity was called
        mock_dependencies["gsm"].update_ball_velocity.assert_called_once()
        args = mock_dependencies["gsm"].update_ball_velocity.call_args[0][0]

        # Expected: direction from (50,30) to (60,40) = (10,10), normalized to (√2/2, √2/2)
        # Per ADR-0014: BALL_SPEED_PER_POWER = 0.175 (was 0.6).
        # Velocity = (√2/2, √2/2) * 10 * 0.175
        expected_magnitude = 10 * 0.175
        expected_unit_mag = math.sqrt(2) / 2
        expected_velocity = (expected_unit_mag * expected_magnitude, expected_unit_mag * expected_magnitude)

        assert abs(args[0] - expected_velocity[0]) < 1e-6
        assert abs(args[1] - expected_velocity[1]) < 1e-6


def test_ec_are_05_zero_length_pass(mock_dependencies, sample_snap):
    """EC-ARE-05: Zero-length pass uses default direction toward opponent goal."""
    engine = ActionResolutionEngine(**mock_dependencies)

    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    # Pass to same position as passer
    validated_actions = {
        "team_a_0": Pass(target_pos=(50.0, 30.0), power=10),  # Same as passer position
    }

    with patch('src.foundation.action_resolution_engine.engine.hash_01') as mock_hash:
        mock_hash.side_effect = lambda seed, tick, pid, context: {
            ("pass_accuracy",): 0.7,
            ("pass_unit",): 0.0,
            ("pass_radius",): 0.0,
        }.get((context,), 0.0)

        # Act
        engine._resolve_phase5(validated_actions, sample_snap, 50, "team_a_0")

        # Assert: Ball velocity points toward opponent goal (team_b_goal_x = 100.0)
        args = mock_dependencies["gsm"].update_ball_velocity.call_args[0][0]
        # Per ADR-0014: BALL_SPEED_PER_POWER = 0.175. (1,0) * 10 * 0.175 = (1.75, 0.0)
        assert args == (1.75, 0.0)


def test_ac_are_10_pass_gsm_calls(mock_dependencies, sample_snap):
    """AC-ARE-10: Pass calls all required GSM methods in order."""
    engine = ActionResolutionEngine(**mock_dependencies)

    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Pass(target_pos=(60.0, 30.0), power=10),
    }

    with patch('src.foundation.action_resolution_engine.engine.hash_01') as mock_hash:
        mock_hash.side_effect = lambda seed, tick, pid, context: 0.0

        # Act
        engine._resolve_phase5(validated_actions, sample_snap, 50, "team_a_0")

        # Assert: All GSM methods called
        mock_dependencies["gsm"].update_ball_velocity.assert_called_once()
        mock_dependencies["gsm"].set_pass_landing_zone.assert_called_once()
        mock_dependencies["gsm"].transfer_possession.assert_called_once_with("team_a_0", None)


def test_ac_are_11_ball_just_passed_flag(mock_dependencies, sample_snap):
    """AC-ARE-11: _ball_just_passed flag set after Pass."""
    engine = ActionResolutionEngine(**mock_dependencies)

    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Pass(target_pos=(60.0, 30.0), power=10),
    }

    with patch('src.foundation.action_resolution_engine.engine.hash_01') as mock_hash:
        mock_hash.side_effect = lambda seed, tick, pid, context: 0.0

        # Act
        engine._resolve_phase5(validated_actions, sample_snap, 50, "team_a_0")

        # Assert: Flag is set
        assert engine._ball_just_passed is True
        assert engine._last_touching_team == "team_a"
        assert engine._last_ball_action_pid == "team_a_0"


def test_ac_are_12_shoot_trajectory(mock_dependencies, sample_snap):
    """AC-ARE-12 (ADR-0018, 2026-04-22): Shoot velocity = base direction
    (toward goal mouth center) + angle offset (degrees) + skill deviation.

    With hash_01 mocked to 0.5 the skill_deviation is exactly zero, so the
    test isolates the base+intent contribution.

    team_a_0 at (50, 30); team_a opp_goal_x=100, goal_y=30 (defaults).
    base_angle = atan2(0, 50) = 0. angle=90° → +π/2 rad. final = π/2.
    Velocity = (cos π/2, sin π/2) * 10 * 0.175 = (0, 1.75).
    """
    engine = ActionResolutionEngine(**mock_dependencies)

    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Shoot(angle=90.0, power=10),  # 90° offset from base
    }

    with patch('src.foundation.action_resolution_engine.engine.hash_01') as mock_hash:
        mock_hash.return_value = 0.5  # any draw → skill_deviation = 0
        engine._resolve_phase5(validated_actions, sample_snap, 50, "team_a_0")

    args = mock_dependencies["gsm"].update_ball_velocity.call_args[0][0]
    expected_velocity = (0.0, 1.75)
    assert abs(args[0] - expected_velocity[0]) < 1e-6
    assert abs(args[1] - expected_velocity[1]) < 1e-6


def test_ac_are_13_shoot_landing_zone_none(mock_dependencies, sample_snap):
    """AC-ARE-13: Shoot sets landing_zone to None."""
    engine = ActionResolutionEngine(**mock_dependencies)

    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Shoot(angle=0.0, power=10),
    }

    # Act
    engine._resolve_phase5(validated_actions, sample_snap, 50, "team_a_0")

    # Assert: set_pass_landing_zone called with None
    mock_dependencies["gsm"].set_pass_landing_zone.assert_called_once_with(None)


def test_ac_are_14_shoot_transfer_possession(mock_dependencies, sample_snap):
    """AC-ARE-14: Shoot transfers possession to None."""
    engine = ActionResolutionEngine(**mock_dependencies)

    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Shoot(angle=0.0, power=10),
    }

    # Act
    engine._resolve_phase5(validated_actions, sample_snap, 50, "team_a_0")

    # Assert: transfer_possession called correctly
    mock_dependencies["gsm"].transfer_possession.assert_called_once_with("team_a_0", None)
    # Flags are set correctly
    assert engine._ball_just_passed is True
    assert engine._last_touching_team == "team_a"
    assert engine._last_ball_action_pid == "team_a_0"


def test_ac_are_15_no_carrier_no_action(mock_dependencies, sample_snap):
    """AC-ARE-15: No ball action when no carrier."""
    engine = ActionResolutionEngine(**mock_dependencies)

    def mock_build_player_state(pid):
        return {"has_ball": False}  # No one has ball
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Pass(target_pos=(60.0, 30.0), power=10),
    }

    # Act
    result = engine._resolve_phase5(validated_actions, sample_snap, 50, None)  # No carrier

    # Assert: No action taken
    assert result == {}
    mock_dependencies["gsm"].update_ball_velocity.assert_not_called()
    mock_dependencies["gsm"].set_pass_landing_zone.assert_not_called()
    mock_dependencies["gsm"].transfer_possession.assert_not_called()


def test_non_ball_action_ignored(mock_dependencies, sample_snap):
    """Non-Pass/Shoot actions are ignored in Phase 5."""
    engine = ActionResolutionEngine(**mock_dependencies)

    def mock_build_player_state(pid):
        return {"has_ball": pid == "team_a_0"}
    mock_dependencies["gsm"].build_player_state.side_effect = mock_build_player_state

    validated_actions = {
        "team_a_0": Hold(),  # Carrier with non-ball action
    }

    # Act
    result = engine._resolve_phase5(validated_actions, sample_snap, 50, "team_a_0")

    # Assert: No action taken
    assert result == {}