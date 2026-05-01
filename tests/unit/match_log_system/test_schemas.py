"""
Tests for MatchLog schemas and construction (Story 001).

Tests all 8 acceptance criteria from
production/epics/match-log-system/story-001-tickrecord-schemas-construction.md.
"""

from __future__ import annotations
import pytest
from dataclasses import FrozenInstanceError

from src.core.match_log_system import (
    ActionRecord,
    TickRecord,
    MatchLog,
    HISTORY_MAX_TICKS,
)


def _create_test_action_record(action: str = "move", details: dict = None) -> ActionRecord:
    """Helper to construct a minimal ActionRecord for tests."""
    return ActionRecord(
        player_id="team_a_0",
        team="team_a",
        action=action,
        result="success",
        details=details if details is not None else {},
    )


def _create_test_tick_record(tick: int = 0, **overrides) -> TickRecord:
    """Helper to construct a minimal TickRecord for tests with sensible defaults."""
    defaults = {
        "tick": tick,
        "ball_position": (50.0, 30.0),
        "ball_possession": None,
        "score": {"team_a": 0, "team_b": 0},
        "player_positions": {f"team_{t}_{i}": [0.0, 0.0] for t in ("a", "b") for i in range(5)},
        "actions": [],
        "is_key_event": False,
        "event_type": None,
    }
    defaults.update(overrides)
    return TickRecord(**defaults)


class TestAC1TickRecordIsFrozen:
    """AC-1: TickRecord cannot be mutated after construction."""

    def test_tick_record_assignment_raises_frozen_instance_error(self):
        """TickRecord.tick assignment should raise FrozenInstanceError."""
        tr = _create_test_tick_record()
        with pytest.raises(FrozenInstanceError):
            tr.tick = 5  # type: ignore[misc]

    def test_tick_record_ball_position_assignment_raises_frozen_instance_error(self):
        """TickRecord.ball_position assignment should raise FrozenInstanceError."""
        tr = _create_test_tick_record()
        with pytest.raises(FrozenInstanceError):
            tr.ball_position = (60.0, 40.0)  # type: ignore[misc]

    def test_tick_record_actions_assignment_raises_frozen_instance_error(self):
        """TickRecord.actions assignment should raise FrozenInstanceError."""
        tr = _create_test_tick_record()
        with pytest.raises(FrozenInstanceError):
            tr.actions = []  # type: ignore[misc]


class TestAC2ActionRecordIsFrozen:
    """AC-2: ActionRecord cannot be mutated after construction."""

    def test_action_record_player_id_assignment_raises_frozen_instance_error(self):
        """ActionRecord.player_id assignment should raise FrozenInstanceError."""
        ar = _create_test_action_record()
        with pytest.raises(FrozenInstanceError):
            ar.player_id = "team_b_0"  # type: ignore[misc]

    def test_action_record_action_assignment_raises_frozen_instance_error(self):
        """ActionRecord.action assignment should raise FrozenInstanceError."""
        ar = _create_test_action_record()
        with pytest.raises(FrozenInstanceError):
            ar.action = "pass"  # type: ignore[misc]

    def test_action_record_details_assignment_raises_frozen_instance_error(self):
        """ActionRecord.details assignment should raise FrozenInstanceError."""
        ar = _create_test_action_record()
        with pytest.raises(FrozenInstanceError):
            ar.details = {"new": "value"}  # type: ignore[misc]


class TestAC3PassDetailsSchema:
    """AC-3: Pass action details schema contains exactly required keys (AC-MLS-17)."""

    def test_action_record_pass_details_contains_required_keys(self):
        """Pass action details must contain exactly the 6 required keys."""
        pass_details = {
            "target_pos": [25.0, 30.0],
            "actual_landing_pos": [24.5, 29.8],
            "effective_power": 0.75,
            "on_target": True,
            "ball_control_contest": True,
            "contest_winner": "team_a_1"
        }

        ar = ActionRecord(
            player_id="team_a_0",
            team="team_a",
            action="pass",
            result="success",
            details=pass_details
        )

        expected_keys = {
            "target_pos", "actual_landing_pos", "effective_power",
            "on_target", "ball_control_contest", "contest_winner"
        }
        assert set(ar.details.keys()) == expected_keys

    def test_action_record_pass_details_key_access(self):
        """Pass action details should allow access to specific keys."""
        pass_details = {
            "target_pos": [25.0, 30.0],
            "actual_landing_pos": [24.5, 29.8],
            "effective_power": 0.75,
            "on_target": True,
            "ball_control_contest": True,
            "contest_winner": "team_a_1"
        }

        ar = ActionRecord(
            player_id="team_a_0",
            team="team_a",
            action="pass",
            result="success",
            details=pass_details
        )

        assert ar.details["target_pos"] == [25.0, 30.0]
        assert ar.details["on_target"] is True
        assert ar.details["contest_winner"] == "team_a_1"


class TestAC4HoldDetailsSchema:
    """AC-4: Hold action details schema contains required keys (AC-MLS-17)."""

    def test_action_record_hold_details_contains_required_keys(self):
        """Hold action details must contain exactly the required keys."""
        hold_details = {
            "under_tackle_pressure": True,
            "tackle_contest_result": "hold_maintained"
        }

        ar = ActionRecord(
            player_id="team_a_1",
            team="team_a",
            action="hold",
            result="success",
            details=hold_details
        )

        expected_keys = {"under_tackle_pressure", "tackle_contest_result"}
        assert set(ar.details.keys()) == expected_keys

    def test_action_record_hold_details_key_access(self):
        """Hold action details should allow access to specific keys."""
        hold_details = {
            "under_tackle_pressure": False,
            "tackle_contest_result": "no_pressure"
        }

        ar = ActionRecord(
            player_id="team_a_2",
            team="team_a",
            action="hold",
            result="success",
            details=hold_details
        )

        assert ar.details["under_tackle_pressure"] is False
        assert ar.details["tackle_contest_result"] == "no_pressure"


class TestAC5PlayerPositionsField:
    """AC-5: player_positions field accepts dict structure correctly."""

    def test_tick_record_player_positions_dict_access(self):
        """TickRecord should accept player_positions as dict mapping str → list."""
        player_positions = {
            "team_a_0": [10.0, 20.0],
            "team_a_1": [25.0, 30.0],
            "team_b_0": [90.0, 30.0],
            "team_b_1": [75.0, 25.0]
        }

        tr = _create_test_tick_record(player_positions=player_positions)

        assert tr.player_positions["team_a_0"] == [10.0, 20.0]
        assert tr.player_positions["team_a_1"] == [25.0, 30.0]
        assert tr.player_positions["team_b_0"] == [90.0, 30.0]
        assert tr.player_positions["team_b_1"] == [75.0, 25.0]

    def test_tick_record_player_positions_full_team_structure(self):
        """TickRecord should handle all 10 players in player_positions."""
        player_positions = {}
        for team in ("a", "b"):
            for i in range(5):
                player_id = f"team_{team}_{i}"
                x = 10.0 * i if team == "a" else 100.0 - (10.0 * i)
                y = 30.0
                player_positions[player_id] = [x, y]

        tr = _create_test_tick_record(player_positions=player_positions)

        # Verify all 10 players present
        assert len(tr.player_positions) == 10
        assert tr.player_positions["team_a_0"] == [0.0, 30.0]
        assert tr.player_positions["team_a_4"] == [40.0, 30.0]
        assert tr.player_positions["team_b_0"] == [100.0, 30.0]
        assert tr.player_positions["team_b_4"] == [60.0, 30.0]


class TestAC6MatchLogConstruction:
    """AC-6: MatchLog construction initializes empty internal state correctly."""

    def test_match_log_construction_with_valid_match_id(self):
        """MatchLog construction should initialize all internal state correctly."""
        ml = MatchLog("test-match-01")

        # Verify all initialization requirements from AC-6
        assert ml.match_id == "test-match-01"
        assert ml._ticks == []
        assert ml._key_events == []
        assert len(ml._history_deque) == 0
        assert ml._history_deque.maxlen == HISTORY_MAX_TICKS
        assert ml._fallback_events == []
        assert ml._phase_transitions == []
        assert ml._state == "LIVE"

    def test_match_log_history_deque_maxlen_equals_constant(self):
        """History deque maxlen should equal HISTORY_MAX_TICKS constant."""
        ml = MatchLog("test-match-02")

        assert ml._history_deque.maxlen == HISTORY_MAX_TICKS
        assert HISTORY_MAX_TICKS == 10  # Verify constant value

    def test_match_log_internal_state_types(self):
        """MatchLog internal state should have correct types."""
        ml = MatchLog("test-match-03")

        assert isinstance(ml._ticks, list)
        assert isinstance(ml._key_events, list)
        assert hasattr(ml._history_deque, 'maxlen')  # deque characteristic
        assert isinstance(ml._fallback_events, list)
        assert isinstance(ml._phase_transitions, list)
        assert isinstance(ml._state, str)


class TestAC7PathInjectionGuard:
    """AC-7: match_id with invalid characters raises ValueError at construction (AC-MLS-15)."""

    @pytest.mark.parametrize("invalid_match_id", [
        "../../etc/passwd",
        "/abs/path",
        "name with spaces",
        "name.with.dots",
        "",
    ])
    def test_match_log_invalid_match_id_raises_value_error(self, invalid_match_id):
        """Invalid match_id formats should raise ValueError with descriptive message."""
        with pytest.raises(ValueError, match="invalid characters"):
            MatchLog(invalid_match_id)

    def test_match_log_path_traversal_prevented(self):
        """Path traversal attempts should be blocked."""
        with pytest.raises(ValueError, match="invalid characters"):
            MatchLog("../parent-dir")

        with pytest.raises(ValueError, match="invalid characters"):
            MatchLog("./current-dir")

    def test_match_log_absolute_path_prevented(self):
        """Absolute paths should be blocked."""
        with pytest.raises(ValueError, match="invalid characters"):
            MatchLog("/usr/bin/malicious")

        with pytest.raises(ValueError, match="invalid characters"):
            MatchLog("/home/user/file")

    def test_match_log_special_characters_prevented(self):
        """Special characters beyond alphanumeric, underscore, dash should be blocked."""
        special_chars = ["match@id", "match#id", "match$id", "match%id", "match&id"]
        for invalid_id in special_chars:
            with pytest.raises(ValueError, match="invalid characters"):
                MatchLog(invalid_id)


class TestAC8ValidMatchIdFormats:
    """AC-8: valid match_id formats are accepted without error."""

    @pytest.mark.parametrize("valid_match_id", [
        "test-match-01",
        "match_001",
        "abc",
        "a",
        "123",
    ])
    def test_match_log_valid_match_id_succeeds(self, valid_match_id):
        """Valid match_id formats should be accepted without raising."""
        ml = MatchLog(valid_match_id)
        assert ml.match_id == valid_match_id

    def test_match_log_alphanumeric_combinations_accepted(self):
        """Various alphanumeric combinations should be accepted."""
        valid_ids = [
            "match123",
            "123match",
            "MATCH_ID",
            "match-id-123",
            "a1b2c3",
            "test_match_final_001"
        ]

        for valid_id in valid_ids:
            ml = MatchLog(valid_id)
            assert ml.match_id == valid_id

    def test_match_log_edge_case_single_character_ids(self):
        """Single character IDs should be valid."""
        single_char_ids = ["a", "A", "1", "z", "Z", "9", "_", "-"]

        for char_id in single_char_ids:
            ml = MatchLog(char_id)
            assert ml.match_id == char_id