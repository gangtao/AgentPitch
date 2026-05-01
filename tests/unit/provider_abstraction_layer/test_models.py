"""Tests for PAL Story 001: LLMResponse + LLMCallError data models."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields

import pytest

from src.foundation.provider_abstraction import LLMCallError, LLMResponse


def _make_response(**overrides) -> LLMResponse:
    base = {
        "text": "hello",
        "provider": "openai",
        "model": "gpt-4o",
        "input_tokens": 100,
        "output_tokens": 50,
        "latency_ms": 1234.5,
        "attempt_count": 1,
    }
    base.update(overrides)
    return LLMResponse(**base)


# ---------------------------------------------------------------------------
# AC-1: LLMResponse construction round-trips all 7 fields
# ---------------------------------------------------------------------------


class TestAC1LLMResponseConstruction:
    def test_all_fields_round_trip(self):
        r = _make_response()
        assert r.text == "hello"
        assert r.provider == "openai"
        assert r.model == "gpt-4o"
        assert r.input_tokens == 100
        assert r.output_tokens == 50
        assert r.latency_ms == 1234.5
        assert r.attempt_count == 1

    def test_empty_text_accepted(self):
        r = _make_response(text="")
        assert r.text == ""

    def test_attempt_count_3_accepted(self):
        r = _make_response(attempt_count=3)
        assert r.attempt_count == 3

    def test_tiny_latency_accepted(self):
        r = _make_response(latency_ms=0.001)
        assert r.latency_ms == 0.001


# ---------------------------------------------------------------------------
# AC-2: Frozen — mutation rejected
# ---------------------------------------------------------------------------


class TestAC2LLMResponseFrozen:
    @pytest.mark.parametrize("field_name,new_value", [
        ("text", "modified"),
        ("provider", "anthropic"),
        ("model", "claude-opus-4-7"),
        ("input_tokens", 999),
        ("output_tokens", 999),
        ("latency_ms", 9999.9),
        ("attempt_count", 2),
    ])
    def test_each_field_rejects_mutation(self, field_name, new_value):
        r = _make_response()
        with pytest.raises(FrozenInstanceError):
            setattr(r, field_name, new_value)


# ---------------------------------------------------------------------------
# AC-3: Field count = 7 exactly
# ---------------------------------------------------------------------------


class TestAC3LLMResponseFieldCount:
    def test_exactly_7_fields(self):
        names = {f.name for f in fields(LLMResponse)}
        expected = {
            "text", "provider", "model",
            "input_tokens", "output_tokens",
            "latency_ms", "attempt_count",
        }
        assert names == expected
        assert len(names) == 7


# ---------------------------------------------------------------------------
# AC-4: LLMCallError subclasses Exception
# ---------------------------------------------------------------------------


class TestAC4LLMCallErrorSubclassesException:
    def test_isinstance_exception(self):
        err = LLMCallError("openai", "gpt-4o", 1)
        assert isinstance(err, Exception)

    def test_caught_as_exception(self):
        try:
            raise LLMCallError("openai", "gpt-4o", 1)
        except Exception as caught:
            assert isinstance(caught, LLMCallError)


# ---------------------------------------------------------------------------
# AC-5: LLMCallError fields populated
# ---------------------------------------------------------------------------


class TestAC5LLMCallErrorFields:
    def test_all_fields_round_trip(self):
        original = RuntimeError("boom")
        err = LLMCallError(
            provider="anthropic",
            model="claude-opus-4-7",
            attempt_count=3,
            cause=original,
        )
        assert err.provider == "anthropic"
        assert err.model == "claude-opus-4-7"
        assert err.attempt_count == 3
        assert err.cause is original


# ---------------------------------------------------------------------------
# AC-6: LLMCallError default cause is None
# ---------------------------------------------------------------------------


class TestAC6LLMCallErrorDefaultCause:
    def test_no_cause_passed_returns_none(self):
        err = LLMCallError("openai", "gpt-4o", 1)
        assert err.cause is None


# ---------------------------------------------------------------------------
# AC-7: LLMCallError default message contains diagnostic context
# ---------------------------------------------------------------------------


class TestAC7LLMCallErrorDefaultMessage:
    def test_default_message_contains_provider_model_attempt_count(self):
        err = LLMCallError("openai", "gpt-4o", 2)
        msg = str(err)
        assert "openai" in msg
        assert "gpt-4o" in msg
        assert "2" in msg

    def test_explicit_message_overrides_default(self):
        err = LLMCallError("openai", "gpt-4o", 1, message="custom message")
        assert str(err) == "custom message"


# ---------------------------------------------------------------------------
# AC-8: LLMCallError supports `raise ... from`
# ---------------------------------------------------------------------------


class TestAC8RaiseFromChain:
    def test_cause_chain_preserved(self):
        original = ValueError("bad arg")
        try:
            try:
                raise original
            except ValueError as e:
                raise LLMCallError("openai", "gpt-4o", 1, cause=e) from e
        except LLMCallError as caught:
            assert caught.__cause__ is original
            assert caught.cause is original
