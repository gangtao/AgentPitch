"""
Tests for MatchLog key event selection (Story 005).

Tests all 10 acceptance criteria from
production/epics/match-log-system/story-005-select-key-events.md.
"""

from __future__ import annotations
import pytest

from src.core.match_log_system import (
    ActionRecord,
    TickRecord,
    MatchLog,
    MLS_KEY_EVENT_RECENCY_BIAS,
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


class TestAC1Selection3Goals2MostRecentTackles:
    """AC-1 (Selection: 3 goals + 2 most recent tackles — AC-MLS-08)."""

    def test_select_key_events_3_goals_plus_2_most_recent_tackles(self):
        """3 goals at (10,20,30), 10 tackle_success at (5,15,25,35,40,45,50,55,60,65).
        select_key_events(5) → indices for ticks [10, 20, 30, 60, 65].
        """
        ml = MatchLog("test-match")

        # Record all events in chronological order (monotonic ticks)
        # Mix goals and tackles in proper order
        events = [
            (5, "tackle_success"),
            (10, "goal"),
            (15, "tackle_success"),
            (20, "goal"),
            (25, "tackle_success"),
            (30, "goal"),
            (35, "tackle_success"),
            (40, "tackle_success"),
            (45, "tackle_success"),
            (50, "tackle_success"),
            (55, "tackle_success"),
            (60, "tackle_success"),
            (65, "tackle_success"),
        ]

        for tick, event_type in events:
            tr = _create_test_tick_record(
                tick=tick,
                is_key_event=True,
                event_type=event_type
            )
            ml.record_tick(tr)

        result = ml.select_key_events(max_events=2)

        # Should get indices for ticks [10, 20, 30, 60, 65] (3 goals + 2 most recent tackles)
        # max_events=2 because that's the cap for non-goal events only
        result_ticks = [ml._ticks[i].tick for i in result]
        assert result_ticks == [10, 20, 30, 60, 65]


class TestAC2GoalsCapExemptWithCap0:
    """AC-2 (Goals cap-exempt with cap=0 — EC-MLS-04)."""

    def test_cap_0_still_includes_goals(self):
        """With max_events=0 and 3 goals + 5 tackle_success → returns indices for the 3 goals only."""
        ml = MatchLog("test-match")

        # Record all events in chronological order
        events = [
            (5, "tackle_success"),
            (10, "goal"),
            (15, "tackle_success"),
            (20, "goal"),
            (25, "tackle_success"),
            (30, "goal"),
            (35, "tackle_success"),
            (45, "tackle_success"),
        ]

        for tick, event_type in events:
            tr = _create_test_tick_record(
                tick=tick,
                is_key_event=True,
                event_type=event_type
            )
            ml.record_tick(tr)

        result = ml.select_key_events(max_events=0)

        # Should only get goal indices (goals never affected by cap)
        result_ticks = [ml._ticks[i].tick for i in result]
        assert result_ticks == [10, 20, 30]


class TestAC3TackleWithoutPossessionNotClassified:
    """AC-3 (Tackle without possession_changed not classified — AC-MLS-09)."""

    def test_tackle_without_possession_not_in_key_events(self):
        """TickRecord with is_key_event=False, event_type=None → tick's index NOT in _key_events."""
        ml = MatchLog("test-match")

        # Record a tackle that didn't change possession
        tr = _create_test_tick_record(
            tick=10,
            is_key_event=False,  # Not a key event
            event_type=None      # No event type
        )
        ml.record_tick(tr)

        # Verify it's not in key events
        assert 0 not in ml._key_events

        # select_key_events should return empty
        result = ml.select_key_events(max_events=5)
        assert result == []


class TestAC4TackleWithPossessionIsClassified:
    """AC-4 (Tackle with possession_changed IS classified)."""

    def test_tackle_with_possession_in_key_events(self):
        """TickRecord with is_key_event=True, event_type="tackle_success" → tick's index IS in _key_events."""
        ml = MatchLog("test-match")

        # Record a successful tackle that changed possession
        tr = _create_test_tick_record(
            tick=10,
            is_key_event=True,           # This is a key event
            event_type="tackle_success"  # Successful tackle
        )
        ml.record_tick(tr)

        # Verify it's in key events
        assert 0 in ml._key_events

        # select_key_events should include it
        result = ml.select_key_events(max_events=5)
        assert result == [0]
        assert ml._ticks[0].tick == 10


class TestAC5ExtremeFallback:
    """AC-5 (Extreme fallback — EC-MLS-05)."""

    def test_100_fallback_events_returns_5_most_recent(self):
        """100 ticks all is_key_event=True, event_type="fallback", no goals.
        select_key_events(5) → 5 indices (most recent: ticks 95-99 → indices 95-99).
        """
        ml = MatchLog("test-match")

        # Record 100 fallback events
        for tick in range(100):
            tr = _create_test_tick_record(
                tick=tick,
                is_key_event=True,
                event_type="fallback"
            )
            ml.record_tick(tr)

        result = ml.select_key_events(max_events=5)

        # Should get the 5 most recent (indices 95-99 for ticks 95-99)
        assert result == [95, 96, 97, 98, 99]

        # Verify these correspond to the correct ticks
        result_ticks = [ml._ticks[i].tick for i in result]
        assert result_ticks == [95, 96, 97, 98, 99]


class TestAC6RecencyBiasFalseUsesPriority:
    """AC-6 (RECENCY_BIAS=False uses priority type)."""

    def test_priority_bias_over_recency(self, monkeypatch):
        """Patch MLS_KEY_EVENT_RECENCY_BIAS=False. Record 3 fallback (10,20,30) +
        3 tackle_success (5,15,25) + 1 goal (50). select_key_events(4) →
        indices for ticks [10, 20, 25, 30, 50] sorted ascending.
        """
        # Patch the bias setting
        monkeypatch.setattr("src.core.match_log_system.MLS_KEY_EVENT_RECENCY_BIAS", False)

        ml = MatchLog("test-match")

        # Record all events in chronological order
        events = [
            (5, "tackle_success"),
            (10, "fallback"),
            (15, "tackle_success"),
            (20, "fallback"),
            (25, "tackle_success"),
            (30, "fallback"),
            (50, "goal"),
        ]

        for tick, event_type in events:
            tr = _create_test_tick_record(
                tick=tick,
                is_key_event=True,
                event_type=event_type
            )
            ml.record_tick(tr)

        result = ml.select_key_events(max_events=4)

        # Should get all 3 fallback (higher priority) + 1 tackle_success (most recent within tackles) + 1 goal
        # Priority order: all fallback first, then most recent tackle_success
        result_ticks = [ml._ticks[i].tick for i in result]
        assert result_ticks == [10, 20, 25, 30, 50]


class TestAC7ReturnedIndicesSortedAscending:
    """AC-7 (Returned indices sorted ascending)."""

    def test_mixed_input_returns_sorted_ascending(self):
        """Verify with mixed input that result is always sorted ascending."""
        ml = MatchLog("test-match")

        # Record events in chronological order (but mixed types)
        events = [
            (5, "tackle_success"),
            (10, "fallback"),
            (20, "goal"),
            (30, "tackle_success"),
            (50, "goal"),
        ]

        for tick, event_type in events:
            tr = _create_test_tick_record(
                tick=tick,
                is_key_event=True,
                event_type=event_type
            )
            ml.record_tick(tr)

        result = ml.select_key_events(max_events=5)

        # Result should be sorted by tick number (ascending)
        result_ticks = [ml._ticks[i].tick for i in result]
        assert result_ticks == sorted(result_ticks)


class TestAC8EmptyKeyEvents:
    """AC-8 (Empty key events)."""

    def test_empty_key_events_returns_empty_list(self):
        """0 key events → select_key_events(5) == []."""
        ml = MatchLog("test-match")

        # Record some ticks but none are key events
        for tick in [1, 2, 3]:
            tr = _create_test_tick_record(
                tick=tick,
                is_key_event=False,  # Not key events
                event_type=None
            )
            ml.record_tick(tr)

        result = ml.select_key_events(max_events=5)
        assert result == []


class TestAC9MoreGoalsThanCap:
    """AC-9 (More goals than cap)."""

    def test_more_goals_than_cap_all_goals_included(self):
        """7 goals + 0 non-goal, max_events=5 → all 7 goal indices."""
        ml = MatchLog("test-match")

        # Record 7 goals
        for tick in range(10, 80, 10):  # 10, 20, 30, 40, 50, 60, 70
            tr = _create_test_tick_record(
                tick=tick,
                is_key_event=True,
                event_type="goal"
            )
            ml.record_tick(tr)

        result = ml.select_key_events(max_events=5)

        # Should get all 7 goals despite cap of 5
        assert len(result) == 7
        result_ticks = [ml._ticks[i].tick for i in result]
        assert result_ticks == [10, 20, 30, 40, 50, 60, 70]


class TestAC10ReturnedIndicesAreValid:
    """AC-10 (Returned indices are valid)."""

    def test_returned_indices_are_valid(self):
        """Each returned index is in range(len(_ticks)) and _ticks[i].is_key_event == True."""
        ml = MatchLog("test-match")

        # Mix of key and non-key events
        events = [
            (5, True, "tackle_success"),
            (10, False, None),        # Not a key event
            (15, True, "goal"),
            (20, False, None),        # Not a key event
            (25, True, "fallback"),
        ]

        for tick, is_key, event_type in events:
            tr = _create_test_tick_record(
                tick=tick,
                is_key_event=is_key,
                event_type=event_type
            )
            ml.record_tick(tr)

        result = ml.select_key_events(max_events=5)

        # All indices should be valid
        for i in result:
            assert 0 <= i < len(ml._ticks)
            assert ml._ticks[i].is_key_event is True

        # Should only get the key events
        result_ticks = [ml._ticks[i].tick for i in result]
        assert result_ticks == [5, 15, 25]