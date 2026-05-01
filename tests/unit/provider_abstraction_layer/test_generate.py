"""Tests for PAL Story 003: generate() orchestration."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

import importlib

from src.foundation.provider_abstraction import (
    LLMCallError,
    LLMResponse,
    PAL_MAX_TOKENS,
    PAL_RETRY_BASE_DELAY_S,
    PAL_RETRY_MAX_ATTEMPTS,
    PAL_TEMPERATURE,
    generate,
)
from src.foundation.provider_abstraction.adapters.base import ProviderAdapter

# `generate` is re-exported as a function from the package, shadowing the
# submodule of the same name. Load the submodule explicitly via importlib to
# access module-level state (_ADAPTERS, _adapter_cache, _reset_adapter_cache).
gen_module = importlib.import_module("src.foundation.provider_abstraction.generate")


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _aiorun(coro):
    return asyncio.run(coro)


def _make_config(provider: str = "openai", model: str = "gpt-4o", api_key: str = "k") -> SimpleNamespace:
    """Minimal MatchConfig stub — avoids cross-epic test dependency on Pydantic models."""
    team = SimpleNamespace(llm_provider=provider, llm_model=model, api_key=api_key)
    return SimpleNamespace(team_a=team, team_b=team)


class FakeRetriableError(Exception):
    """Test-only exception that PAL classifies as retriable via _pal_retriable=True."""
    _pal_retriable = True


class FakeNonRetriableError(Exception):
    """Test-only exception that PAL classifies as non-retriable via _pal_retriable=False."""
    _pal_retriable = False


class FakeAdapter(ProviderAdapter):
    """Adapter that runs through scripted outcomes (one entry per attempt).

    Each entry is either:
      - a 3-tuple (text, input_tokens, output_tokens) → returned
      - an Exception instance → raised
    """

    def __init__(self, api_key: str, base_url: str | None = None, scripted_outcomes: list = None):
        self.api_key = api_key
        self.base_url = base_url
        self.scripted_outcomes = scripted_outcomes or []
        self.call_count = 0
        self.call_args_list: list[dict] = []

    async def call(self, model, messages, temperature, max_tokens):
        idx = self.call_count
        self.call_count += 1
        self.call_args_list.append({
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        })
        if idx >= len(self.scripted_outcomes):
            raise IndexError(f"No scripted outcome for attempt {self.call_count}")
        outcome = self.scripted_outcomes[idx]
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


@pytest.fixture(autouse=True)
def _reset_adapter_cache():
    """Reset module-level cache before AND after each test (no leakage between tests)."""
    gen_module._reset_adapter_cache()
    yield
    gen_module._reset_adapter_cache()


def _install_fake_adapter(monkeypatch, scripted_outcomes: list, provider: str = "openai") -> type:
    """Install a FakeAdapter subclass into the PAL registry. Returns the class
    so tests can inspect its `last_instance.call_count` etc."""
    instances: list[FakeAdapter] = []

    class TrackedFakeAdapter(FakeAdapter):
        def __init__(self, api_key: str, base_url: str | None = None):
            super().__init__(api_key, base_url=base_url, scripted_outcomes=list(scripted_outcomes))
            instances.append(self)

    TrackedFakeAdapter.instances = instances  # type: ignore[attr-defined]
    monkeypatch.setitem(gen_module._ADAPTERS, provider, TrackedFakeAdapter)
    return TrackedFakeAdapter


# ---------------------------------------------------------------------------
# AC-1 + AC-2 + AC-3 + AC-4: success first try
# ---------------------------------------------------------------------------


class TestAC1SuccessFirstTry:
    def test_returns_llmresponse_with_text(self, monkeypatch):
        _install_fake_adapter(monkeypatch, [("hello", 100, 50)])
        result = _aiorun(generate("prompt", "team_a", _make_config()))
        assert isinstance(result, LLMResponse)
        assert result.text == "hello"

    def test_response_provider_model_from_config(self, monkeypatch):
        _install_fake_adapter(monkeypatch, [("ok", 1, 1)], provider="anthropic")
        cfg = _make_config(provider="anthropic", model="claude-opus-4-7")
        result = _aiorun(generate("prompt", "team_a", cfg))
        assert result.provider == "anthropic"
        assert result.model == "claude-opus-4-7"

    def test_token_counts_forwarded(self, monkeypatch):
        _install_fake_adapter(monkeypatch, [("ok", 100, 50)])
        result = _aiorun(generate("prompt", "team_a", _make_config()))
        assert result.input_tokens == 100
        assert result.output_tokens == 50

    def test_latency_ms_positive(self, monkeypatch):
        _install_fake_adapter(monkeypatch, [("ok", 1, 1)])
        result = _aiorun(generate("prompt", "team_a", _make_config()))
        assert result.latency_ms >= 0  # very fast in tests but never negative

    def test_attempt_count_1_on_first_try(self, monkeypatch):
        _install_fake_adapter(monkeypatch, [("ok", 1, 1)])
        result = _aiorun(generate("prompt", "team_a", _make_config()))
        assert result.attempt_count == 1


# ---------------------------------------------------------------------------
# AC-5: attempt_count tracking on retries
# ---------------------------------------------------------------------------


class TestAC5AttemptCountTracking:
    def test_one_retry_then_success_attempt_count_2(self, monkeypatch):
        _install_fake_adapter(monkeypatch, [FakeRetriableError("rate limited"), ("ok", 1, 1)])
        with patch.object(gen_module.asyncio, "sleep", AsyncMock()) as sleep_mock:
            result = _aiorun(generate("prompt", "team_a", _make_config()))
        assert result.attempt_count == 2
        sleep_mock.assert_awaited_once_with(1)

    def test_two_retries_then_success_attempt_count_3(self, monkeypatch):
        _install_fake_adapter(monkeypatch, [
            FakeRetriableError("r1"),
            FakeRetriableError("r2"),
            ("ok", 1, 1),
        ])
        with patch.object(gen_module.asyncio, "sleep", AsyncMock()) as sleep_mock:
            result = _aiorun(generate("prompt", "team_a", _make_config()))
        assert result.attempt_count == 3
        # Two backoff sleeps: 1s before attempt 2, 2s before attempt 3
        sleep_args = [c.args[0] for c in sleep_mock.await_args_list]
        assert sleep_args == [1, 2]


# ---------------------------------------------------------------------------
# AC-6: unrecognized provider
# ---------------------------------------------------------------------------


class TestAC6UnrecognizedProvider:
    def test_gemini_provider_raises_immediately(self):
        cfg = _make_config(provider="gemini")
        with pytest.raises(LLMCallError) as exc_info:
            _aiorun(generate("prompt", "team_a", cfg))
        assert exc_info.value.attempt_count == 1
        assert exc_info.value.provider == "gemini"

    def test_no_adapter_constructed_on_bad_provider(self, monkeypatch):
        constructor_calls = []
        original_init = gen_module._ADAPTERS["openai"].__init__

        def spy_init(self, api_key):
            constructor_calls.append(api_key)
            original_init(self, api_key)

        monkeypatch.setattr(gen_module._ADAPTERS["openai"], "__init__", spy_init)
        cfg = _make_config(provider="gemini")
        with pytest.raises(LLMCallError):
            _aiorun(generate("prompt", "team_a", cfg))
        assert constructor_calls == []  # no openai adapter constructed


# ---------------------------------------------------------------------------
# AC-7: non-retriable error on attempt 1
# ---------------------------------------------------------------------------


class TestAC7NonRetriableAttempt1:
    def test_non_retriable_raises_after_one_call(self, monkeypatch):
        TrackedAdapter = _install_fake_adapter(monkeypatch, [FakeNonRetriableError("auth")])
        with patch.object(gen_module.asyncio, "sleep", AsyncMock()) as sleep_mock:
            with pytest.raises(LLMCallError) as exc_info:
                _aiorun(generate("prompt", "team_a", _make_config()))
        assert exc_info.value.attempt_count == 1
        assert TrackedAdapter.instances[0].call_count == 1
        sleep_mock.assert_not_awaited()


# ---------------------------------------------------------------------------
# AC-8: retriable exhausted (3 attempts) → LLMCallError(attempt_count=3)
# ---------------------------------------------------------------------------


class TestAC8RetriableExhausted:
    def test_three_retriable_failures_raises_attempt_3(self, monkeypatch):
        TrackedAdapter = _install_fake_adapter(monkeypatch, [
            FakeRetriableError("r1"),
            FakeRetriableError("r2"),
            FakeRetriableError("r3"),
        ])
        with patch.object(gen_module.asyncio, "sleep", AsyncMock()) as sleep_mock:
            with pytest.raises(LLMCallError) as exc_info:
                _aiorun(generate("prompt", "team_a", _make_config()))
        assert exc_info.value.attempt_count == 3
        assert TrackedAdapter.instances[0].call_count == 3
        # Two sleeps: before attempts 2 and 3 only — no third sleep before raise
        sleep_args = [c.args[0] for c in sleep_mock.await_args_list]
        assert sleep_args == [1, 2]


# ---------------------------------------------------------------------------
# AC-9: one retriable then success — covered by AC-5b
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# AC-10: cause chained
# ---------------------------------------------------------------------------


class TestAC10CauseChained:
    def test_non_retriable_cause_preserved(self, monkeypatch):
        original = FakeNonRetriableError("auth fail")
        _install_fake_adapter(monkeypatch, [original])
        with pytest.raises(LLMCallError) as exc_info:
            _aiorun(generate("prompt", "team_a", _make_config()))
        assert exc_info.value.cause is original
        assert exc_info.value.__cause__ is original

    def test_retriable_exhausted_cause_is_last_exception(self, monkeypatch):
        last_exc = FakeRetriableError("r3")
        _install_fake_adapter(monkeypatch, [
            FakeRetriableError("r1"), FakeRetriableError("r2"), last_exc,
        ])
        with patch.object(gen_module.asyncio, "sleep", AsyncMock()):
            with pytest.raises(LLMCallError) as exc_info:
                _aiorun(generate("prompt", "team_a", _make_config()))
        assert exc_info.value.cause is last_exc


# ---------------------------------------------------------------------------
# AC-11: lazy cache reused for same provider
# ---------------------------------------------------------------------------


class TestAC11LazyCacheReused:
    def test_two_calls_same_provider_construct_adapter_once(self, monkeypatch):
        TrackedAdapter = _install_fake_adapter(monkeypatch, [("ok", 1, 1)])
        # First call creates instance
        _aiorun(generate("prompt", "team_a", _make_config()))
        # Second call must reuse — extend the cached adapter's outcome list
        TrackedAdapter.instances[0].scripted_outcomes.append(("ok2", 2, 2))
        _aiorun(generate("prompt", "team_a", _make_config()))
        assert len(TrackedAdapter.instances) == 1


# ---------------------------------------------------------------------------
# AC-12: cache shared across teams
# ---------------------------------------------------------------------------


class TestAC12CacheSharedAcrossTeams:
    def test_team_a_and_team_b_use_same_adapter_instance(self, monkeypatch):
        TrackedAdapter = _install_fake_adapter(monkeypatch, [("ok-a", 1, 1)])
        # Call team_a → constructs the (only) adapter
        _aiorun(generate("prompt", "team_a", _make_config()))
        TrackedAdapter.instances[0].scripted_outcomes.append(("ok-b", 1, 1))
        _aiorun(generate("prompt", "team_b", _make_config()))
        # Same instance reused
        assert len(TrackedAdapter.instances) == 1


# ---------------------------------------------------------------------------
# AC-13: concurrent gather works
# ---------------------------------------------------------------------------


class TestAC13ConcurrentGather:
    def test_gather_two_teams_succeeds(self, monkeypatch):
        # Pre-load the cache by installing a fake; both calls share the instance
        TrackedAdapter = _install_fake_adapter(monkeypatch, [
            ("ok-1", 1, 1), ("ok-2", 1, 1),
        ])

        async def both():
            return await asyncio.gather(
                generate("p1", "team_a", _make_config()),
                generate("p2", "team_b", _make_config()),
            )

        results = asyncio.run(both())
        assert len(results) == 2
        assert all(isinstance(r, LLMResponse) for r in results)
        # Cache contains exactly one entry per unique provider
        assert len(gen_module._adapter_cache) == 1


# ---------------------------------------------------------------------------
# AC-14: empty completion does not raise
# ---------------------------------------------------------------------------


class TestAC14EmptyCompletionNotRaised:
    def test_empty_text_returned_as_llmresponse(self, monkeypatch):
        _install_fake_adapter(monkeypatch, [("", 50, 0)])
        result = _aiorun(generate("prompt", "team_a", _make_config()))
        assert result.text == ""
        assert result.input_tokens == 50
        assert result.output_tokens == 0
        assert result.attempt_count == 1


# ---------------------------------------------------------------------------
# AC-15: unexpected exception wrapped (attempt_count=1)
# ---------------------------------------------------------------------------


class TestAC15UnexpectedExceptionWrapped:
    def test_runtime_error_wrapped_attempt_1(self, monkeypatch):
        original = RuntimeError("unexpected")
        TrackedAdapter = _install_fake_adapter(monkeypatch, [original])
        with pytest.raises(LLMCallError) as exc_info:
            _aiorun(generate("prompt", "team_a", _make_config()))
        assert exc_info.value.attempt_count == 1
        assert exc_info.value.cause is original
        assert TrackedAdapter.instances[0].call_count == 1


# ---------------------------------------------------------------------------
# AC-16: PAL_MAX_TOKENS=8192 forwarded
# ---------------------------------------------------------------------------


class TestAC16MaxTokensForwarded:
    def test_max_tokens_8192_in_call_kwargs(self, monkeypatch):
        TrackedAdapter = _install_fake_adapter(monkeypatch, [("ok", 1, 1)])
        _aiorun(generate("prompt", "team_a", _make_config()))
        assert TrackedAdapter.instances[0].call_args_list[0]["max_tokens"] == 8192


# ---------------------------------------------------------------------------
# AC-17: PAL_TEMPERATURE=1.0 forwarded
# ---------------------------------------------------------------------------


class TestAC17TemperatureForwarded:
    def test_temperature_1_0_in_call_kwargs(self, monkeypatch):
        TrackedAdapter = _install_fake_adapter(monkeypatch, [("ok", 1, 1)])
        _aiorun(generate("prompt", "team_a", _make_config()))
        assert TrackedAdapter.instances[0].call_args_list[0]["temperature"] == 1.0


# ---------------------------------------------------------------------------
# AC-EXTRA-1: messages format is single user-role message
# ---------------------------------------------------------------------------


class TestACExtra1MessagesFormat:
    def test_single_user_role_message_no_system_role(self, monkeypatch):
        TrackedAdapter = _install_fake_adapter(monkeypatch, [("ok", 1, 1)])
        _aiorun(generate("the-prompt", "team_a", _make_config()))
        msgs = TrackedAdapter.instances[0].call_args_list[0]["messages"]
        assert msgs == [{"role": "user", "content": "the-prompt"}]


# ---------------------------------------------------------------------------
# AC-EXTRA-2: no time.sleep blocking call
# ---------------------------------------------------------------------------


class TestACExtra2NoBlockingSleep:
    def test_time_sleep_never_called(self, monkeypatch):
        _install_fake_adapter(monkeypatch, [
            FakeRetriableError("r1"), FakeRetriableError("r2"), ("ok", 1, 1),
        ])

        # Patch time.sleep to raise — if any sync sleep is called, this fails
        def raise_on_blocking(*a, **kw):
            raise AssertionError("PAL must use asyncio.sleep, not time.sleep")

        monkeypatch.setattr(gen_module.time, "sleep", raise_on_blocking, raising=False)
        with patch.object(gen_module.asyncio, "sleep", AsyncMock()):
            result = _aiorun(generate("prompt", "team_a", _make_config()))
        assert result.attempt_count == 3


# ---------------------------------------------------------------------------
# AC-EXTRA-3: module constants present with expected values
# ---------------------------------------------------------------------------


class TestACExtra3ModuleConstants:
    def test_pal_temperature(self):
        assert PAL_TEMPERATURE == 1.0

    def test_pal_max_tokens(self):
        assert PAL_MAX_TOKENS == 8192

    def test_pal_retry_max_attempts(self):
        assert PAL_RETRY_MAX_ATTEMPTS == 3

    def test_pal_retry_base_delay(self):
        assert PAL_RETRY_BASE_DELAY_S == 1.0
