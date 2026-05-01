"""Tests for CGP failure classifier — AC coverage for Story 003."""

from __future__ import annotations

import importlib

import pytest

from src.foundation.code_generation_pipeline.classifier import _classify_failure
from src.foundation.provider_abstraction.models import LLMCallError


class TestClassifyFailure:
    """Test suite for _classify_failure() covering all 9 acceptance criteria."""

    @pytest.mark.parametrize("reason", [
        "empty_response",
        "no_code_block",
        "no_decide_signature",
        "compile_error"
    ])
    def test_string_reasons_are_retriable(self, reason: str) -> None:
        """AC-1: String reasons matching Rule 5 rows 1-4 are retriable."""
        result = _classify_failure(reason)
        assert result == (reason, True)

    def test_llm_call_error_retriable_when_pal_retries_exhausted(self) -> None:
        """AC-2 (AC-CGP-08): LLMCallError with attempt_count == PAL_RETRY_MAX_ATTEMPTS is retriable."""
        # Read PAL_RETRY_MAX_ATTEMPTS at test time to construct the test case
        pal_generate = importlib.import_module("src.foundation.provider_abstraction.generate")
        pal_max_attempts = pal_generate.PAL_RETRY_MAX_ATTEMPTS

        exc = LLMCallError(
            provider="openai",
            model="gpt-4o",
            attempt_count=pal_max_attempts,
            cause=TimeoutError()
        )
        result = _classify_failure(exc)
        assert result == ("llm_call_error", True)

    def test_llm_call_error_non_retriable_when_immediate_failure(self) -> None:
        """AC-3 (AC-CGP-07): LLMCallError with attempt_count=1 is non-retriable (structural config error)."""
        exc = LLMCallError(
            provider="openai",
            model="gpt-4o",
            attempt_count=1,
            cause=ValueError("bad auth")
        )
        result = _classify_failure(exc)
        assert result == ("llm_call_error", False)

    def test_llm_call_error_defensive_mid_value(self) -> None:
        """AC-4: LLMCallError with unexpected mid-value attempt_count is non-retriable (defensive)."""
        exc = LLMCallError(
            provider="openai",
            model="gpt-4o",
            attempt_count=2,
            cause=None
        )
        result = _classify_failure(exc)
        assert result == ("llm_call_error", False)

    def test_pal_retry_max_attempts_read_at_call_time(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AC-5: PAL_RETRY_MAX_ATTEMPTS is read at call time, so monkeypatch propagates."""
        # Monkeypatch PAL_RETRY_MAX_ATTEMPTS to 5
        pal_gen = importlib.import_module("src.foundation.provider_abstraction.generate")
        monkeypatch.setattr(pal_gen, "PAL_RETRY_MAX_ATTEMPTS", 5)

        # Now classifier should treat attempt_count=5 as retriable
        exc_retriable = LLMCallError(provider="o", model="m", attempt_count=5, cause=None)
        assert _classify_failure(exc_retriable) == ("llm_call_error", True)

        # And attempt_count=3 (the previous default) should now be NON-retriable
        exc_non_retriable = LLMCallError(provider="o", model="m", attempt_count=3, cause=None)
        assert _classify_failure(exc_non_retriable) == ("llm_call_error", False)

    def test_unknown_string_reason_preserves_reason_but_not_retriable(self) -> None:
        """AC-6: Unknown string reason returns (reason, False) — preserves for logging."""
        result = _classify_failure("undocumented_reason_str")
        assert result == ("undocumented_reason_str", False)

    def test_truly_unknown_object_returns_unknown_false(self) -> None:
        """AC-7: Random object input returns ("unknown", False)."""
        result = _classify_failure(object())
        assert result == ("unknown", False)

    def test_importability(self) -> None:
        """AC-8: Private helper function is importable via fully qualified path."""
        # This test passing proves the import works (it's used in the test setup)
        assert callable(_classify_failure)
        assert _classify_failure.__name__ == "_classify_failure"

    def test_purity_deterministic_result(self) -> None:
        """AC-9: Function is pure — same input yields same output."""
        # Test with string input
        input_str = "compile_error"
        result1 = _classify_failure(input_str)
        result2 = _classify_failure(input_str)
        assert result1 == result2

        # Test with LLMCallError input
        exc = LLMCallError(provider="test", model="test", attempt_count=1, cause=None)
        result1 = _classify_failure(exc)
        result2 = _classify_failure(exc)
        assert result1 == result2

        # Test with unknown input
        unknown_obj = object()
        result1 = _classify_failure(unknown_obj)
        result2 = _classify_failure(unknown_obj)
        assert result1 == result2

    def test_llm_call_error_getattr_defensive(self) -> None:
        """Additional test: Verify getattr defensive handling works."""
        # Create a mock object that looks like LLMCallError but has no attempt_count
        class MockLLMCallError(LLMCallError):
            def __init__(self) -> None:
                # Don't call super().__init__ to avoid setting attempt_count
                pass

        mock_exc = MockLLMCallError()
        # Remove attempt_count if it exists (defensive)
        if hasattr(mock_exc, 'attempt_count'):
            delattr(mock_exc, 'attempt_count')

        result = _classify_failure(mock_exc)
        # Should default to non-retriable when attempt_count is None
        assert result == ("llm_call_error", False)