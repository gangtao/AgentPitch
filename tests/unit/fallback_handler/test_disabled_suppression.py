"""Tests for Fallback Handler Story 003: DISABLED suppression + log resilience + reset_for_match."""

from __future__ import annotations

import pytest

from src.foundation.action import Hold
from src.foundation.fallback import (
    ExecutionStatus,
    FallbackEvent,
    FallbackHandler,
)
from src.foundation.sandbox.result import SandboxResult


def _disabled_result(prefilled_hold: Hold = None) -> SandboxResult:
    return SandboxResult(
        status=ExecutionStatus.DISABLED,
        action=prefilled_hold or Hold(),
        execution_time_ms=0.0,
        error_type=None,
    )


def _exception_result(error_type: str = "ValueError") -> SandboxResult:
    return SandboxResult(
        status=ExecutionStatus.EXCEPTION,
        action=None,
        execution_time_ms=1.0,
        error_type=error_type,
    )


def _timeout_result() -> SandboxResult:
    return SandboxResult(
        status=ExecutionStatus.TIMEOUT,
        action=None,
        execution_time_ms=5.0,
        error_type=None,
    )


# ---------------------------------------------------------------------------
# AC-1: DISABLED logs only on first occurrence per match (AC-FH-07)
# ---------------------------------------------------------------------------


class TestAC1DisabledLogsOnceFirstOccurrence:
    def test_three_consecutive_disabled_emits_once(self):
        captured: list = []
        handler = FallbackHandler(log_emitter=captured.append)

        out_ticks: list = []
        for tick in (1000, 1001, 1002):
            out = handler.handle(_disabled_result(), "team_a_3", "team_a", "openai/gpt-4o", tick)
            out_ticks.append(out)

        # Exactly one event emitted (tick 1000)
        assert len(captured) == 1
        assert captured[0].tick == 1000

        # First call has log_event; subsequent calls do not
        assert out_ticks[0].log_event is not None
        assert out_ticks[1].log_event is None
        assert out_ticks[2].log_event is None

        # Player is in suppression set
        assert "team_a_3" in handler._disabled_logged_set

    def test_action_is_hold_on_all_three_calls(self):
        handler = FallbackHandler()
        for tick in (1000, 1001, 1002):
            out = handler.handle(_disabled_result(), "team_a_3", "team_a", "openai/gpt-4o", tick)
            assert isinstance(out.action, Hold)


# ---------------------------------------------------------------------------
# AC-2: Non-DISABLED does not populate suppression set (AC-FH-08)
# ---------------------------------------------------------------------------


class TestAC2NonDisabledDoesNotPopulateSet:
    def test_exception_then_disabled_emits_disabled_event(self):
        captured: list = []
        handler = FallbackHandler(log_emitter=captured.append)

        # Tick 1: EXCEPTION — should NOT add to disabled set
        handler.handle(_exception_result(), "team_b_1", "team_b", "openai/gpt-4o", 1)
        assert "team_b_1" not in handler._disabled_logged_set

        # Tick 2: DISABLED — first time for this player → emit event
        out = handler.handle(_disabled_result(), "team_b_1", "team_b", "openai/gpt-4o", 2)
        assert out.log_event is not None
        assert "team_b_1" in handler._disabled_logged_set
        # 2 events total (EXCEPTION + DISABLED)
        assert len(captured) == 2

    def test_tick3_disabled_for_same_player_suppressed(self):
        captured: list = []
        handler = FallbackHandler(log_emitter=captured.append)
        handler.handle(_exception_result(), "team_b_1", "team_b", "openai/gpt-4o", 1)
        handler.handle(_disabled_result(), "team_b_1", "team_b", "openai/gpt-4o", 2)
        out3 = handler.handle(_disabled_result(), "team_b_1", "team_b", "openai/gpt-4o", 3)
        assert out3.log_event is None
        assert len(captured) == 2  # EXCEPTION + first DISABLED only


# ---------------------------------------------------------------------------
# AC-3: disabled_logged_set resets between matches (AC-FH-09)
# ---------------------------------------------------------------------------


class TestAC3SuppressionSetResetsBetweenMatches:
    def test_reset_for_match_clears_set(self):
        handler = FallbackHandler()
        handler._disabled_logged_set = {"team_a_2", "team_b_4"}
        handler.reset_for_match()
        assert handler._disabled_logged_set == set()

    def test_post_reset_disabled_emits_fresh_event(self):
        captured: list = []
        handler = FallbackHandler(log_emitter=captured.append)
        # Match 1 — emit one DISABLED event for team_a_2
        handler.handle(_disabled_result(), "team_a_2", "team_a", "openai/gpt-4o", 1000)
        assert len(captured) == 1

        # Reset for match 2
        handler.reset_for_match()

        # Match 2 — first DISABLED for team_a_2 emits again
        handler.handle(_disabled_result(), "team_a_2", "team_a", "openai/gpt-4o", 100)
        assert len(captured) == 2
        assert captured[1].tick == 100


# ---------------------------------------------------------------------------
# AC-4: log emission failure does not raise (AC-FH-10)
# ---------------------------------------------------------------------------


class TestAC4LogEmissionFailureSwallowed:
    def test_runtime_error_in_emitter_swallowed(self):
        def failing_emitter(event: FallbackEvent) -> None:
            raise RuntimeError("simulated match-log outage")

        handler = FallbackHandler(log_emitter=failing_emitter)
        out = handler.handle(_exception_result(), "team_a_0", "team_a", "openai/gpt-4o", 1)
        # No exception propagated
        assert isinstance(out.action, Hold)
        assert out.log_event is None

    def test_keyboard_interrupt_in_emitter_swallowed(self):
        def failing_emitter(event: FallbackEvent) -> None:
            raise KeyboardInterrupt()

        handler = FallbackHandler(log_emitter=failing_emitter)
        out = handler.handle(_exception_result(), "team_a_0", "team_a", "openai/gpt-4o", 1)
        assert out.log_event is None  # No exception propagated

    def test_system_exit_in_emitter_swallowed(self):
        def failing_emitter(event: FallbackEvent) -> None:
            raise SystemExit(1)

        handler = FallbackHandler(log_emitter=failing_emitter)
        out = handler.handle(_exception_result(), "team_a_0", "team_a", "openai/gpt-4o", 1)
        assert out.log_event is None

    def test_disabled_set_still_updated_on_emitter_failure(self):
        def failing_emitter(event: FallbackEvent) -> None:
            raise RuntimeError("boom")

        handler = FallbackHandler(log_emitter=failing_emitter)
        handler.handle(_disabled_result(), "team_a_0", "team_a", "openai/gpt-4o", 1)
        # Even though emitter raised, suppression set was still updated (best-effort signal)
        assert "team_a_0" in handler._disabled_logged_set


# ---------------------------------------------------------------------------
# AC-5: multi-player set hygiene (AC-FH-12 extension)
# ---------------------------------------------------------------------------


class TestAC5MultiPlayerSetHygiene:
    def test_exception_and_timeout_for_two_players_no_suppression(self):
        handler = FallbackHandler()
        handler.handle(_exception_result(), "team_a_0", "team_a", "openai/gpt-4o", 500)
        handler.handle(_timeout_result(), "team_b_0", "team_b", "anthropic/claude", 500)
        assert handler._disabled_logged_set == set()


# ---------------------------------------------------------------------------
# AC-6: suppressed DISABLED still returns reused Hold instance
# ---------------------------------------------------------------------------


class TestAC6SuppressedDisabledReusesHold:
    def test_action_identity_on_both_calls(self):
        handler = FallbackHandler()
        prefilled_1 = Hold()
        prefilled_2 = Hold()

        out1 = handler.handle(_disabled_result(prefilled_1), "team_a_0", "team_a", "openai/gpt-4o", 1)
        out2 = handler.handle(_disabled_result(prefilled_2), "team_a_0", "team_a", "openai/gpt-4o", 2)

        assert out1.action is prefilled_1
        assert out1.log_event is not None
        assert out2.action is prefilled_2
        assert out2.log_event is None  # suppressed


# ---------------------------------------------------------------------------
# AC-7: reset_for_match() is idempotent
# ---------------------------------------------------------------------------


class TestAC7ResetIdempotent:
    def test_two_consecutive_resets(self):
        handler = FallbackHandler()
        handler.reset_for_match()
        handler.reset_for_match()  # no raise
        assert handler._disabled_logged_set == set()


# ---------------------------------------------------------------------------
# AC-8: DISABLED for two different players — both first-time, both emit
# ---------------------------------------------------------------------------


class TestAC8TwoDifferentPlayersBothEmit:
    def test_two_distinct_player_ids_emit_two_events(self):
        captured: list = []
        handler = FallbackHandler(log_emitter=captured.append)
        handler.handle(_disabled_result(), "team_a_0", "team_a", "openai/gpt-4o", 500)
        handler.handle(_disabled_result(), "team_b_0", "team_b", "anthropic/claude", 500)
        assert len(captured) == 2
        assert {captured[0].player_id, captured[1].player_id} == {"team_a_0", "team_b_0"}
        assert {"team_a_0", "team_b_0"}.issubset(handler._disabled_logged_set)


# ---------------------------------------------------------------------------
# AC-9: across-match isolation (full integration sketch)
# ---------------------------------------------------------------------------


class TestAC9AcrossMatchIsolation:
    def test_match1_and_match2_each_emit_once(self):
        captured: list = []
        handler = FallbackHandler(log_emitter=captured.append)

        # Match 1 — tick 1000 emits, tick 1001 suppressed
        handler.handle(_disabled_result(), "team_a_0", "team_a", "openai/gpt-4o", 1000)
        handler.handle(_disabled_result(), "team_a_0", "team_a", "openai/gpt-4o", 1001)
        assert len(captured) == 1

        # Reset for match 2
        handler.reset_for_match()

        # Match 2 — tick 100 emits fresh
        handler.handle(_disabled_result(), "team_a_0", "team_a", "openai/gpt-4o", 100)
        assert len(captured) == 2
        assert captured[0].tick == 1000
        assert captured[1].tick == 100
