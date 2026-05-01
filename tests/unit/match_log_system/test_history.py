"""
Tests for MatchLog.get_history() API (Story 004).

Tests all 10 acceptance criteria from
production/epics/match-log-system/story-004-get-history-method.md.
"""

from __future__ import annotations
import pytest

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


class TestAC1EmptyDeque:
    """AC-1: Empty deque — AC-MLS-03."""

    def test_get_history_empty_deque_returns_empty_list(self):
        """MatchLog with no ticks should return empty list from get_history()."""
        ml = MatchLog("test-match")

        result = ml.get_history()

        assert result == []


class TestAC2FifteenTicksTenDicts:
    """AC-2: 15 ticks → 10 dicts oldest-first — AC-MLS-04."""

    def test_get_history_fifteen_ticks_returns_ten_dicts_oldest_first(self):
        """After recording 15 ticks with HISTORY_MAX_TICKS=10, get_history() returns exactly 10 dicts."""
        # Verify the default value
        assert HISTORY_MAX_TICKS == 10

        ml = MatchLog("test-match")

        # Record 15 ticks (tick=0..14)
        for i in range(15):
            tr = _create_test_tick_record(tick=i)
            ml.record_tick(tr)

        result = ml.get_history()

        # Should return exactly 10 dicts
        assert len(result) == 10

        # Index 0 has "tick": 5 (oldest in the window)
        assert result[0]["tick"] == 5

        # Index 9 has "tick": 14 (newest in the window)
        assert result[9]["tick"] == 14


class TestAC3ThreeTicksThreeDicts:
    """AC-3: 3 ticks → 3 dicts — AC-MLS-20."""

    def test_get_history_three_ticks_returns_three_dicts(self):
        """With 3 ticks recorded, get_history() should return 3 dicts."""
        ml = MatchLog("test-match")

        # Record 3 ticks
        for i in range(3):
            tr = _create_test_tick_record(tick=i)
            ml.record_tick(tr)

        result = ml.get_history()

        assert len(result) == 3
        assert result[0]["tick"] == 0
        assert result[2]["tick"] == 2


class TestAC4SchemaIsASCIRule7Only:
    """AC-4: Schema is ASCI Rule 7 only — AC-MLS-05."""

    def test_get_history_schema_exact_fields_no_internal_fields(self):
        """get_history() result should only contain ASCI Rule 7 fields, no internal fields."""
        ml = MatchLog("test-match")

        # Create a tick with internal fields that should be excluded
        tr = _create_test_tick_record(
            tick=0,
            ball_possession="team_a",
            is_key_event=True,
            event_type="goal",
            player_positions={"team_a_0": [10.0, 20.0]}
        )
        ml.record_tick(tr)

        result = ml.get_history()

        # Should have exactly the 4 ASCI Rule 7 fields
        assert set(result[0].keys()) == {"tick", "ball_position", "score", "actions"}

        # Verify internal fields are NOT present
        assert "ball_possession" not in result[0]
        assert "is_key_event" not in result[0]
        assert "event_type" not in result[0]
        assert "player_positions" not in result[0]


class TestAC5ActionsSubSchema:
    """AC-5: actions sub-schema."""

    def test_get_history_actions_sub_schema_exact_fields(self):
        """Each actions[i] dict should have exact ASCI Rule 7 action fields."""
        ml = MatchLog("test-match")

        action = _create_test_action_record(action="pass", details={"target": "team_a_1"})
        tr = _create_test_tick_record(tick=0, actions=[action])
        ml.record_tick(tr)

        result = ml.get_history()

        # Should have exactly the 5 action fields
        action_dict = result[0]["actions"][0]
        assert set(action_dict.keys()) == {"player_id", "team", "action", "result", "details"}


class TestAC6BallPositionIsList:
    """AC-6: ball_position is list."""

    def test_get_history_ball_position_is_list_not_tuple(self):
        """ball_position should be converted from tuple to list for JSON-friendliness."""
        ml = MatchLog("test-match")

        tr = _create_test_tick_record(tick=0, ball_position=(75.5, 42.3))
        ml.record_tick(tr)

        result = ml.get_history()

        assert isinstance(result[0]["ball_position"], list)
        assert result[0]["ball_position"] == [75.5, 42.3]


class TestAC7DefensiveCopyScore:
    """AC-7: Defensive copy — score."""

    def test_get_history_defensive_copy_score_mutation_isolated(self):
        """Mutating the returned score dict should not affect the underlying TickRecord."""
        ml = MatchLog("test-match")

        tr = _create_test_tick_record(tick=0, score={"team_a": 2, "team_b": 1})
        ml.record_tick(tr)

        result = ml.get_history()

        # Mutate the returned score
        result[0]["score"]["team_a"] = 99

        # Original TickRecord should be unchanged
        assert ml._ticks[0].score["team_a"] == 2


class TestAC8DefensiveCopyActionDetails:
    """AC-8: Defensive copy — action details."""

    def test_get_history_defensive_copy_action_details_mutation_isolated(self):
        """Mutating the returned action details should not affect the underlying ActionRecord."""
        ml = MatchLog("test-match")

        action = _create_test_action_record(action="move", details={"dx": 5.0, "dy": 3.0})
        tr = _create_test_tick_record(tick=0, actions=[action])
        ml.record_tick(tr)

        result = ml.get_history()

        # Mutate the returned action details
        result[0]["actions"][0]["details"]["dx"] = -999

        # Original ActionRecord should be unchanged
        assert ml._ticks[0].actions[0].details["dx"] == 5.0


class TestAC9AvailableWhenLive:
    """AC-9: Available when LIVE."""

    def test_get_history_available_when_state_is_live(self):
        """get_history() should work when MatchLog state is LIVE."""
        ml = MatchLog("test-match")
        tr = _create_test_tick_record(tick=0)
        ml.record_tick(tr)

        # Verify state is LIVE
        assert ml._state == "LIVE"

        # get_history() should work without exception
        result = ml.get_history()
        assert len(result) == 1
        assert result[0]["tick"] == 0


class TestAC10AvailableWhenFinalized:
    """AC-10: Available when FINALIZED."""

    def test_get_history_available_when_finalized_same_content(self):
        """get_history() should work after finalize() with same content."""
        ml = MatchLog("test-match")
        tr = _create_test_tick_record(tick=0)
        ml.record_tick(tr)

        # Get history while LIVE
        result_live = ml.get_history()

        # Finalize
        ml.finalize(final_state={"team_a": 1, "team_b": 0})

        # Verify state is FINALIZED
        assert ml._state == "FINALIZED"

        # get_history() should still work and return same content
        result_finalized = ml.get_history()

        assert result_live == result_finalized
        assert result_finalized[0]["tick"] == 0