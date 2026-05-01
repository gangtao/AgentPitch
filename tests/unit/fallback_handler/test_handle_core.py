"""Tests for Fallback Handler Story 002: handle() core logic."""

from __future__ import annotations

import inspect

import pytest

from src.foundation.action import Hold, Move
from src.foundation.fallback import (
    ExecutionStatus,
    FallbackEvent,
    FallbackHandler,
    FallbackResult,
)
from src.foundation.sandbox.result import SandboxResult


def _make_handler(captured: list = None) -> FallbackHandler:
    """Build a handler whose log_emitter appends to a list (or no emitter)."""
    if captured is None:
        return FallbackHandler()
    return FallbackHandler(log_emitter=captured.append)


def _make_result(status, **overrides) -> SandboxResult:
    base = {
        "status": status,
        "action": None,
        "execution_time_ms": 1.0,
        "error_type": None,
    }
    base.update(overrides)
    return SandboxResult(**base)


# ---------------------------------------------------------------------------
# AC-1: EXCEPTION → fresh Hold()
# ---------------------------------------------------------------------------


class TestAC1ExceptionHold:
    def test_exception_returns_hold_action(self):
        handler = _make_handler()
        sandbox_result = _make_result(
            ExecutionStatus.EXCEPTION, error_type="ValueError", execution_time_ms=1.2
        )
        out = handler.handle(sandbox_result, "team_a_2", "team_a", "openai/gpt-4o", 42)
        assert isinstance(out, FallbackResult)
        assert isinstance(out.action, Hold)
        assert out.action is not None


# ---------------------------------------------------------------------------
# AC-2: TIMEOUT → fresh Hold()
# ---------------------------------------------------------------------------


class TestAC2TimeoutHold:
    def test_timeout_returns_hold(self):
        handler = _make_handler()
        sandbox_result = _make_result(ExecutionStatus.TIMEOUT, execution_time_ms=5.0)
        out = handler.handle(sandbox_result, "team_a_0", "team_a", "openai/gpt-4o", 1)
        assert isinstance(out.action, Hold)


# ---------------------------------------------------------------------------
# AC-3: INVALID_RETURN → fresh Hold()
# ---------------------------------------------------------------------------


class TestAC3InvalidReturnHold:
    def test_invalid_return_returns_hold(self):
        handler = _make_handler()
        sandbox_result = _make_result(ExecutionStatus.INVALID_RETURN, execution_time_ms=0.8)
        out = handler.handle(sandbox_result, "team_a_0", "team_a", "openai/gpt-4o", 1)
        assert isinstance(out.action, Hold)


# ---------------------------------------------------------------------------
# AC-4: DISABLED → reuse SandboxResult.action (identity check)
# ---------------------------------------------------------------------------


class TestAC4DisabledReusesSandboxAction:
    def test_disabled_reuses_action_instance(self):
        handler = _make_handler()
        prefilled = Hold()
        sandbox_result = _make_result(ExecutionStatus.DISABLED, action=prefilled)
        out = handler.handle(sandbox_result, "team_a_0", "team_a", "openai/gpt-4o", 1)
        assert out.action is prefilled  # identity check


# ---------------------------------------------------------------------------
# AC-5: FallbackEvent fields on EXCEPTION
# ---------------------------------------------------------------------------


class TestAC5FallbackEventFieldsOnException:
    def test_event_fields_match_inputs(self):
        captured: list = []
        handler = _make_handler(captured)
        sandbox_result = _make_result(
            ExecutionStatus.EXCEPTION, error_type="ValueError", execution_time_ms=3.7
        )
        handler.handle(sandbox_result, "team_a_2", "team_a", "openai/gpt-4o", 42)

        assert len(captured) == 1
        event = captured[0]
        assert event.event_type == "fallback"
        assert event.failure_status == "EXCEPTION"
        assert event.error_type == "ValueError"
        assert event.execution_time_ms == 3.7
        assert event.substituted_action == "Hold"
        assert event.fallback_substituted is True
        assert event.tick == 42
        assert event.player_id == "team_a_2"
        assert event.team == "team_a"
        assert event.llm_provider == "openai/gpt-4o"


# ---------------------------------------------------------------------------
# AC-6: error_type is None for TIMEOUT and INVALID_RETURN
# ---------------------------------------------------------------------------


class TestAC6ErrorTypeNoneForTimeoutAndInvalidReturn:
    @pytest.mark.parametrize("status", [ExecutionStatus.TIMEOUT, ExecutionStatus.INVALID_RETURN])
    def test_error_type_none_in_event(self, status):
        captured: list = []
        handler = _make_handler(captured)
        sandbox_result = _make_result(status, error_type=None)
        handler.handle(sandbox_result, "team_a_0", "team_a", "openai/gpt-4o", 1)
        assert captured[0].error_type is None


# ---------------------------------------------------------------------------
# AC-7: fallback_substituted always True (AC-FH-11)
# ---------------------------------------------------------------------------


class TestAC7FallbackSubstitutedAlwaysTrue:
    @pytest.mark.parametrize("status", [
        ExecutionStatus.EXCEPTION,
        ExecutionStatus.TIMEOUT,
        ExecutionStatus.INVALID_RETURN,
        ExecutionStatus.DISABLED,
    ])
    def test_event_fallback_substituted_is_true(self, status):
        captured: list = []
        handler = _make_handler(captured)
        sandbox_result = _make_result(
            status, action=Hold() if status is ExecutionStatus.DISABLED else None
        )
        handler.handle(sandbox_result, "team_a_0", "team_a", "openai/gpt-4o", 1)
        assert captured[0].fallback_substituted is True


# ---------------------------------------------------------------------------
# AC-8: multi-player independence
# ---------------------------------------------------------------------------


class TestAC8MultiPlayerIndependence:
    def test_two_players_produce_distinct_events(self):
        captured: list = []
        handler = _make_handler(captured)
        result_a = _make_result(ExecutionStatus.EXCEPTION, error_type="ValueError")
        result_b = _make_result(ExecutionStatus.TIMEOUT)

        out_a = handler.handle(result_a, "team_a_3", "team_a", "openai/gpt-4o", 500)
        out_b = handler.handle(result_b, "team_b_1", "team_b", "anthropic/claude", 500)

        assert isinstance(out_a.action, Hold)
        assert isinstance(out_b.action, Hold)
        assert len(captured) == 2
        assert captured[0].player_id == "team_a_3"
        assert captured[0].team == "team_a"
        assert captured[1].player_id == "team_b_1"
        assert captured[1].team == "team_b"


# ---------------------------------------------------------------------------
# AC-9: llm_provider defaults to "unknown" (AC-FH-13)
# ---------------------------------------------------------------------------


class TestAC9LlmProviderDefault:
    @pytest.mark.parametrize("missing", [None, ""])
    def test_missing_provider_becomes_unknown(self, missing):
        captured: list = []
        handler = _make_handler(captured)
        sandbox_result = _make_result(ExecutionStatus.EXCEPTION, error_type="ValueError")
        handler.handle(sandbox_result, "team_a_0", "team_a", missing, 1)
        assert captured[0].llm_provider == "unknown"

    def test_real_provider_passes_through(self):
        captured: list = []
        handler = _make_handler(captured)
        sandbox_result = _make_result(ExecutionStatus.EXCEPTION, error_type="ValueError")
        handler.handle(sandbox_result, "team_a_0", "team_a", "anthropic/claude-opus-4-7", 1)
        assert captured[0].llm_provider == "anthropic/claude-opus-4-7"


# ---------------------------------------------------------------------------
# AC-10: handle() signature (TR-FH-001)
# ---------------------------------------------------------------------------


class TestAC10HandleSignature:
    def test_signature_parameters(self):
        sig = inspect.signature(FallbackHandler.handle)
        params = list(sig.parameters.keys())
        # excluding self
        assert params[1:] == ["result", "player_id", "team", "llm_provider", "tick"]


# ---------------------------------------------------------------------------
# AC-11: statelessness (TR-FH-005, partial — Story 003 covers DISABLED suppression)
# ---------------------------------------------------------------------------


class TestAC11StatelessnessPartial:
    def test_two_identical_calls_produce_equal_events(self):
        handler = _make_handler()
        sandbox_result = _make_result(ExecutionStatus.EXCEPTION, error_type="ValueError")
        out1 = handler.handle(sandbox_result, "team_a_0", "team_a", "openai/gpt-4o", 1)
        out2 = handler.handle(sandbox_result, "team_a_0", "team_a", "openai/gpt-4o", 1)
        # FallbackEvent is frozen + value-equal — direct dataclass __eq__
        assert out1.log_event == out2.log_event
        # Action class matches — fresh Hold instance each call by design
        assert isinstance(out1.action, Hold) and isinstance(out2.action, Hold)


# ---------------------------------------------------------------------------
# AC-12: failure_status uses enum NAME (uppercase string)
# ---------------------------------------------------------------------------


class TestAC12FailureStatusUsesEnumName:
    @pytest.mark.parametrize("status,expected_name", [
        (ExecutionStatus.EXCEPTION, "EXCEPTION"),
        (ExecutionStatus.TIMEOUT, "TIMEOUT"),
        (ExecutionStatus.INVALID_RETURN, "INVALID_RETURN"),
        (ExecutionStatus.DISABLED, "DISABLED"),
        (ExecutionStatus.COMPILE_ERROR, "COMPILE_ERROR"),
    ])
    def test_failure_status_is_enum_name(self, status, expected_name):
        captured: list = []
        handler = _make_handler(captured)
        sandbox_result = _make_result(
            status, action=Hold() if status is ExecutionStatus.DISABLED else None
        )
        handler.handle(sandbox_result, "team_a_0", "team_a", "openai/gpt-4o", 1)
        assert captured[0].failure_status == expected_name


# ---------------------------------------------------------------------------
# Bonus: returns FallbackResult, not None
# ---------------------------------------------------------------------------


class TestBonusReturnType:
    def test_returns_fallback_result(self):
        handler = _make_handler()
        sandbox_result = _make_result(ExecutionStatus.EXCEPTION, error_type="ValueError")
        out = handler.handle(sandbox_result, "team_a_0", "team_a", "openai/gpt-4o", 1)
        assert isinstance(out, FallbackResult)
        assert isinstance(out.log_event, FallbackEvent)
