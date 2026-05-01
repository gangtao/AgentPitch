"""
Tests for MatchLog state machine + finalize() (Story 003).

Tests all 9 acceptance criteria from
production/epics/match-log-system/story-003-state-machine.md.
"""

from __future__ import annotations
import logging
import pytest

from src.core.match_log_system import (
    ActionRecord,
    TickRecord,
    MatchLog,
    MatchAlreadyFinalizedError,
    MatchNotFinalizedError,
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


class TestAC1RecordTickAfterFinalizeRaises:
    """AC-1: record_tick() after finalize() raises MatchAlreadyFinalizedError."""

    def test_record_tick_after_finalize_raises_match_already_finalized_error(self):
        """record_tick should raise MatchAlreadyFinalizedError when called after finalize."""
        ml = MatchLog("test-match")
        ml.finalize({"final_score": {"team_a": 0, "team_b": 0}})
        tr = _create_test_tick_record(tick=0)

        with pytest.raises(MatchAlreadyFinalizedError, match="test-match"):
            ml.record_tick(tr)


class TestAC2RecordFallbackAfterFinalizeRaises:
    """AC-2: record_fallback() after finalize() raises MatchAlreadyFinalizedError."""

    def test_record_fallback_after_finalize_raises_match_already_finalized_error(self):
        """record_fallback should raise MatchAlreadyFinalizedError when called after finalize."""
        ml = MatchLog("test-match")
        ml.finalize({"final_score": {"team_a": 0, "team_b": 0}})
        fb_event = {"type": "timeout", "details": "test"}

        with pytest.raises(MatchAlreadyFinalizedError, match="test-match"):
            ml.record_fallback(fb_event)


class TestAC3RecordPhaseTransitionAfterFinalizeRaises:
    """AC-3: record_phase_transition() after finalize() raises MatchAlreadyFinalizedError."""

    def test_record_phase_transition_after_finalize_raises_match_already_finalized_error(self):
        """record_phase_transition should raise MatchAlreadyFinalizedError when called after finalize."""
        ml = MatchLog("test-match")
        ml.finalize({"final_score": {"team_a": 0, "team_b": 0}})

        with pytest.raises(MatchAlreadyFinalizedError, match="test-match"):
            ml.record_phase_transition(tick=10, old_phase="A", new_phase="B")


class TestAC4GenerateSummaryBeforeFinalizeRaises:
    """AC-4: generate_summary() before finalize() raises MatchNotFinalizedError."""

    def test_generate_summary_before_finalize_raises_match_not_finalized_error(self):
        """generate_summary should raise MatchNotFinalizedError when called before finalize."""
        ml = MatchLog("test-match")

        with pytest.raises(MatchNotFinalizedError, match="call finalize"):
            ml.generate_summary()


class TestAC5EmptyFinalizeSucceeds:
    """AC-5: finalize() called immediately after construction (T==0) succeeds."""

    def test_empty_finalize_succeeds_without_error(self):
        """finalize called on empty MatchLog should succeed without error."""
        ml = MatchLog("test-match")
        final_state = {"score": {"team_a": 0, "team_b": 0}}

        # Should not raise any exception
        ml.finalize(final_state)

        assert ml._state == "FINALIZED"
        assert ml._ticks == []


class TestAC6DoubleFinalizeIsNoOpWithWarning:
    """AC-6: Double-finalize is no-op + WARNING (EC-MLS-12)."""

    def test_double_finalize_logs_warning_and_is_noop(self, caplog):
        """Second call to finalize should be no-op and log WARNING."""
        caplog.set_level(logging.WARNING)
        ml = MatchLog("test-match")

        # Record some ticks first
        for i in range(3):
            tr = _create_test_tick_record(tick=i)
            ml.record_tick(tr)

        final_state = {"final_score": {"team_a": 0, "team_b": 0}}

        # First finalize
        ml.finalize(final_state)
        initial_ticks_len = len(ml._ticks)

        # Second finalize (should be no-op + WARNING)
        ml.finalize(final_state)

        # Verify no exception was raised and state is still FINALIZED
        assert ml._state == "FINALIZED"
        # Verify data is unchanged (no corruption)
        assert len(ml._ticks) == initial_ticks_len == 3

        # Verify WARNING was logged
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert any("FINALIZED" in r.message for r in warnings)


class TestAC7StateTransitionIsOneWay:
    """AC-7: State transition is one-way (no unfinalize method)."""

    def test_state_transition_is_one_way_no_unfinalize_method(self):
        """Verify state transitions only go LIVE → FINALIZED and there's no way back."""
        ml = MatchLog("test-match")

        # Initially LIVE
        assert ml._state == "LIVE"

        # After finalize, FINALIZED
        ml.finalize({"final_score": {"team_a": 0, "team_b": 0}})
        assert ml._state == "FINALIZED"

        # Verify there's no unfinalize method to transition back
        assert not hasattr(MatchLog, "unfinalize")


class TestAC8FinalStateStored:
    """AC-8: finalize(final_state) stores final_state in _final_state."""

    def test_finalize_stores_final_state_in_instance_attribute(self):
        """finalize should store the final_state dict in _final_state."""
        ml = MatchLog("test-match")
        final_state = {"final_score": {"team_a": 2, "team_b": 1}}

        ml.finalize(final_state)

        assert ml._final_state == final_state


class TestAC9CustomExceptionsAreSubclassesOfException:
    """AC-9: Custom exceptions are subclasses of Exception and importable."""

    def test_custom_exceptions_are_subclasses_of_exception(self):
        """Both custom exceptions should be subclasses of Exception."""
        assert issubclass(MatchAlreadyFinalizedError, Exception)
        assert issubclass(MatchNotFinalizedError, Exception)

    def test_custom_exceptions_are_importable_from_module(self):
        """Both custom exceptions should be importable from src.core.match_log_system."""
        # This test passes by the fact that the imports at the top work
        # Additional verification that they're the right types
        assert MatchAlreadyFinalizedError.__name__ == "MatchAlreadyFinalizedError"
        assert MatchNotFinalizedError.__name__ == "MatchNotFinalizedError"