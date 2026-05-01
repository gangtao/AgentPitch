"""
Tests for MatchLog recording API (Story 002).

Tests all 10 acceptance criteria from
production/epics/match-log-system/story-002-recording-api.md.
"""

from __future__ import annotations
import pytest

from src.core.match_log_system import (
    ActionRecord,
    TickRecord,
    MatchLog,
    MatchAlreadyFinalizedError,
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


class TestAC1RecordTickBasic:
    """AC-1: record_tick on LIVE MatchLog increments _ticks."""

    def test_record_tick_increments_ticks_list(self):
        """record_tick(tick_record) on LIVE MatchLog should append to _ticks."""
        ml = MatchLog("test-match")
        tr = _create_test_tick_record(tick=0)

        ml.record_tick(tr)

        assert len(ml._ticks) == 1
        assert ml._ticks[0] is tr


class TestAC2NonMonotonicRaises:
    """AC-2: Non-monotonic tick values raise ValueError."""

    def test_record_tick_repeated_tick_raises_value_error(self):
        """record_tick with same tick as previous should raise ValueError."""
        ml = MatchLog("test-match")
        tr1 = _create_test_tick_record(tick=5)
        tr2 = _create_test_tick_record(tick=5)  # Same tick - should fail

        ml.record_tick(tr1)

        with pytest.raises(ValueError, match="non-monotonic"):
            ml.record_tick(tr2)

    def test_record_tick_less_than_previous_raises_value_error(self):
        """record_tick with tick less than previous should raise ValueError."""
        ml = MatchLog("test-match")
        tr1 = _create_test_tick_record(tick=6)
        tr2 = _create_test_tick_record(tick=4)  # Less than previous - should fail

        ml.record_tick(tr1)

        with pytest.raises(ValueError, match="non-monotonic"):
            ml.record_tick(tr2)


class TestAC3RepeatedTickIsNonMonotonic:
    """AC-3: Repeated tick is non-monotonic (subset of AC-2)."""

    def test_record_tick_exact_repeated_tick_raises_value_error(self):
        """record_tick with exact same tick number should raise ValueError."""
        ml = MatchLog("test-match")
        tr1 = _create_test_tick_record(tick=5)
        tr2 = _create_test_tick_record(tick=5)  # Exact repeat

        ml.record_tick(tr1)

        with pytest.raises(ValueError, match="non-monotonic"):
            ml.record_tick(tr2)


class TestAC4FirstTickCanBeAnyNonNegative:
    """AC-4: First tick can be 0 or any non-negative integer."""

    def test_first_tick_zero_succeeds(self):
        """record_tick(TickRecord(tick=0, ...)) succeeds on empty MatchLog."""
        ml = MatchLog("test-match")
        tr = _create_test_tick_record(tick=0)

        ml.record_tick(tr)

        assert len(ml._ticks) == 1
        assert ml._ticks[0].tick == 0

    def test_first_tick_arbitrary_value_succeeds(self):
        """record_tick(TickRecord(tick=100, ...)) succeeds on empty MatchLog."""
        ml = MatchLog("test-match")
        tr = _create_test_tick_record(tick=100)

        ml.record_tick(tr)

        assert len(ml._ticks) == 1
        assert ml._ticks[0].tick == 100


class TestAC5HistoryDequeUpdated:
    """AC-5: record_tick updates _history_deque correctly."""

    def test_history_deque_contains_newest_entry_after_record_tick(self):
        """After record_tick(tr), _history_deque[-1] should be tr."""
        ml = MatchLog("test-match")
        tr = _create_test_tick_record(tick=0)

        ml.record_tick(tr)

        assert ml._history_deque[-1] is tr

    def test_history_deque_eviction_behavior_after_exceeding_max_ticks(self):
        """After 15 record_tick calls with HISTORY_MAX_TICKS=10, deque should contain exactly 10 entries."""
        ml = MatchLog("test-match")

        # Record 15 ticks (tick=0..14)
        for i in range(15):
            tr = _create_test_tick_record(tick=i)
            ml.record_tick(tr)

        # Should have exactly 10 entries (HISTORY_MAX_TICKS)
        assert len(ml._history_deque) == 10

        # Oldest entry should be tick 5 (15 - 10 = 5)
        assert ml._history_deque[0].tick == 5

        # Newest entry should be tick 14
        assert ml._history_deque[9].tick == 14


class TestAC6RecordFallbackAppends:
    """AC-6: record_fallback appends to _fallback_events."""

    def test_record_fallback_single_append(self):
        """record_fallback(fb_event) should append to _fallback_events."""
        ml = MatchLog("test-match")
        fb_event = {"type": "timeout", "details": "test"}

        ml.record_fallback(fb_event)

        assert ml._fallback_events == [fb_event]

    def test_record_fallback_multiple_appends_accumulate(self):
        """Multiple record_fallback calls should accumulate in order."""
        ml = MatchLog("test-match")
        fb1 = {"type": "timeout", "tick": 5}
        fb2 = {"type": "error", "tick": 10}

        ml.record_fallback(fb1)
        ml.record_fallback(fb2)

        assert ml._fallback_events == [fb1, fb2]


class TestAC7RecordPhaseTransitionAppends:
    """AC-7: record_phase_transition appends to _phase_transitions."""

    def test_record_phase_transition_single_append(self):
        """record_phase_transition should append tuple to _phase_transitions."""
        ml = MatchLog("test-match")

        ml.record_phase_transition(tick=100, old_phase="IN_PLAY", new_phase="GOAL_SCORED")

        assert ml._phase_transitions == [(100, "IN_PLAY", "GOAL_SCORED")]

    def test_record_phase_transition_multiple_appends_accumulate(self):
        """Multiple record_phase_transition calls should accumulate in order."""
        ml = MatchLog("test-match")

        ml.record_phase_transition(tick=50, old_phase="KICK_OFF", new_phase="IN_PLAY")
        ml.record_phase_transition(tick=100, old_phase="IN_PLAY", new_phase="GOAL_SCORED")

        expected = [
            (50, "KICK_OFF", "IN_PLAY"),
            (100, "IN_PLAY", "GOAL_SCORED")
        ]
        assert ml._phase_transitions == expected


class TestAC8OrderIndependence:
    """AC-8: Order independence (EC-MLS-07) - record_fallback before record_tick works."""

    def test_record_fallback_before_record_tick_both_succeed(self):
        """record_fallback(fb) BEFORE record_tick(tr) on same tick should work correctly."""
        ml = MatchLog("test-match")
        fb = {"type": "timeout", "tick": 10}
        tr = _create_test_tick_record(tick=10)

        # Call record_fallback BEFORE record_tick
        ml.record_fallback(fb)
        ml.record_tick(tr)

        # Both should succeed and be recorded
        assert ml._fallback_events == [fb]
        assert ml._ticks == [tr]


class TestAC9KeyEventUpdatesKeyEventsIndex:
    """AC-9: is_key_event=True updates _key_events with index (not tick number)."""

    def test_key_event_flag_updates_key_events_with_index(self):
        """record_tick with is_key_event=True should append index to _key_events."""
        ml = MatchLog("test-match")
        tr = _create_test_tick_record(tick=10, is_key_event=True)

        ml.record_tick(tr)

        # Should contain index 0 (first record), NOT tick number 10
        assert ml._key_events == [0]

    def test_non_key_event_does_not_update_key_events(self):
        """record_tick with is_key_event=False should not update _key_events."""
        ml = MatchLog("test-match")
        tr = _create_test_tick_record(tick=5, is_key_event=False)

        ml.record_tick(tr)

        assert ml._key_events == []


class TestAC10MultipleTicsAccumulate:
    """AC-10: Multiple ticks accumulate correctly."""

    def test_multiple_ticks_accumulate_correctly(self):
        """Record 5 ticks (some key, some not) and verify accumulation."""
        ml = MatchLog("test-match")

        # Record 5 ticks with mixed key_event flags
        ticks_data = [
            (0, True),   # key event at index 0
            (1, False),  # not key
            (2, True),   # key event at index 2
            (3, False),  # not key
            (4, True),   # key event at index 4
        ]

        for tick_num, is_key in ticks_data:
            tr = _create_test_tick_record(tick=tick_num, is_key_event=is_key)
            ml.record_tick(tr)

        # Verify total tick count
        assert len(ml._ticks) == 5

        # Verify _key_events contains only indices of key ticks
        assert ml._key_events == [0, 2, 4]

        # Verify specific tick numbers are correct
        assert ml._ticks[0].tick == 0
        assert ml._ticks[2].tick == 2
        assert ml._ticks[4].tick == 4


class TestFinalizationStateguard:
    """Test that all record_* methods raise MatchAlreadyFinalizedError when state is FINALIZED."""

    def test_record_tick_raises_when_finalized(self):
        """record_tick should raise MatchAlreadyFinalizedError when state is FINALIZED."""
        ml = MatchLog("test-match")
        ml._state = "FINALIZED"  # Manually set to FINALIZED for testing
        tr = _create_test_tick_record(tick=0)

        with pytest.raises(MatchAlreadyFinalizedError, match="test-match"):
            ml.record_tick(tr)

    def test_record_fallback_raises_when_finalized(self):
        """record_fallback should raise MatchAlreadyFinalizedError when state is FINALIZED."""
        ml = MatchLog("test-match")
        ml._state = "FINALIZED"  # Manually set to FINALIZED for testing
        fb = {"type": "timeout"}

        with pytest.raises(MatchAlreadyFinalizedError, match="test-match"):
            ml.record_fallback(fb)

    def test_record_phase_transition_raises_when_finalized(self):
        """record_phase_transition should raise MatchAlreadyFinalizedError when state is FINALIZED."""
        ml = MatchLog("test-match")
        ml._state = "FINALIZED"  # Manually set to FINALIZED for testing

        with pytest.raises(MatchAlreadyFinalizedError, match="test-match"):
            ml.record_phase_transition(tick=10, old_phase="A", new_phase="B")