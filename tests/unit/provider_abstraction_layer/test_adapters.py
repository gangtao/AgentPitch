"""Tests for PAL Story 002: ProviderAdapter base + OpenAI/Anthropic adapters."""

from __future__ import annotations

import asyncio
import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.foundation.provider_abstraction.adapters.anthropic_adapter import AnthropicAdapter
from src.foundation.provider_abstraction.adapters.base import ProviderAdapter
from src.foundation.provider_abstraction.adapters.openai_adapter import OpenAIAdapter


def _aiorun(coro):
    """Tiny helper since pytest-asyncio is not installed in this project."""
    return asyncio.run(coro)


# Shared message fixture
_MSGS = [{"role": "user", "content": "hi"}]


# ---------------------------------------------------------------------------
# AC-1: OpenAI adapter returns text + token tuple
# ---------------------------------------------------------------------------


class TestAC1OpenAIReturnsTextAndTokens:
    @patch("src.foundation.provider_abstraction.adapters.openai_adapter.openai.AsyncOpenAI")
    def test_returns_text_and_token_tuple(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="hello"))]
        mock_response.usage = MagicMock(prompt_tokens=100, completion_tokens=50)
        mock_client_cls.return_value.chat.completions.create = AsyncMock(return_value=mock_response)

        adapter = OpenAIAdapter(api_key="test-key")
        result = _aiorun(adapter.call(
            model="gpt-4o",
            messages=_MSGS,
            temperature=1.0,
            max_tokens=8192,
        ))
        assert result == ("hello", 100, 50)


# ---------------------------------------------------------------------------
# AC-2: Anthropic adapter returns text + token tuple
# ---------------------------------------------------------------------------


class TestAC2AnthropicReturnsTextAndTokens:
    @patch("src.foundation.provider_abstraction.adapters.anthropic_adapter.anthropic.AsyncAnthropic")
    def test_returns_text_and_token_tuple(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="hello")]
        mock_response.usage = MagicMock(input_tokens=100, output_tokens=50)
        mock_client_cls.return_value.messages.create = AsyncMock(return_value=mock_response)

        adapter = AnthropicAdapter(api_key="test-key")
        result = _aiorun(adapter.call(
            model="claude-opus-4-7",
            messages=_MSGS,
            temperature=1.0,
            max_tokens=8192,
        ))
        assert result == ("hello", 100, 50)


# ---------------------------------------------------------------------------
# AC-3: OpenAI kwargs forwarded
# ---------------------------------------------------------------------------


class TestAC3OpenAIKwargsForwarded:
    @patch("src.foundation.provider_abstraction.adapters.openai_adapter.openai.AsyncOpenAI")
    def test_temperature_and_max_tokens_forwarded(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="x"))]
        mock_response.usage = MagicMock(prompt_tokens=1, completion_tokens=1)
        create_mock = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value.chat.completions.create = create_mock

        adapter = OpenAIAdapter(api_key="k")
        _aiorun(adapter.call(model="gpt-4o", messages=_MSGS, temperature=1.0, max_tokens=8192))

        create_mock.assert_awaited_once()
        kwargs = create_mock.await_args.kwargs
        assert kwargs["model"] == "gpt-4o"
        assert kwargs["temperature"] == 1.0
        # 2026-04-25: adapter now forwards as `max_completion_tokens` (the
        # modern OpenAI parameter; required by gpt-5.x and o1/o3 reasoning
        # models, accepted by older chat models too). Adapter signature
        # still spells the kwarg `max_tokens` for stability — only the SDK
        # call name changed.
        assert kwargs["max_completion_tokens"] == 8192
        assert "max_tokens" not in kwargs


# ---------------------------------------------------------------------------
# AC-4: Anthropic kwargs forwarded
# ---------------------------------------------------------------------------


class TestAC4AnthropicKwargsForwarded:
    @patch("src.foundation.provider_abstraction.adapters.anthropic_adapter.anthropic.AsyncAnthropic")
    def test_temperature_and_max_tokens_forwarded(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="x")]
        mock_response.usage = MagicMock(input_tokens=1, output_tokens=1)
        create_mock = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value.messages.create = create_mock

        adapter = AnthropicAdapter(api_key="k")
        _aiorun(adapter.call(model="claude-opus-4-7", messages=_MSGS, temperature=1.0, max_tokens=8192))

        create_mock.assert_awaited_once()
        kwargs = create_mock.await_args.kwargs
        assert kwargs["model"] == "claude-opus-4-7"
        assert kwargs["temperature"] == 1.0
        assert kwargs["max_tokens"] == 8192


# ---------------------------------------------------------------------------
# AC-5: OpenAI messages list forwarded verbatim
# ---------------------------------------------------------------------------


class TestAC5OpenAIMessagesForwarded:
    @patch("src.foundation.provider_abstraction.adapters.openai_adapter.openai.AsyncOpenAI")
    def test_messages_passed_unchanged(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=""))]
        mock_response.usage = MagicMock(prompt_tokens=0, completion_tokens=0)
        create_mock = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value.chat.completions.create = create_mock

        msgs = [{"role": "user", "content": "test prompt"}]
        adapter = OpenAIAdapter(api_key="k")
        _aiorun(adapter.call(model="gpt-4o", messages=msgs, temperature=1.0, max_tokens=8192))

        assert create_mock.await_args.kwargs["messages"] == msgs


# ---------------------------------------------------------------------------
# AC-6: Anthropic messages list forwarded verbatim
# ---------------------------------------------------------------------------


class TestAC6AnthropicMessagesForwarded:
    @patch("src.foundation.provider_abstraction.adapters.anthropic_adapter.anthropic.AsyncAnthropic")
    def test_messages_passed_unchanged(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="")]
        mock_response.usage = MagicMock(input_tokens=0, output_tokens=0)
        create_mock = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value.messages.create = create_mock

        msgs = [{"role": "user", "content": "test prompt"}]
        adapter = AnthropicAdapter(api_key="k")
        _aiorun(adapter.call(model="claude-opus-4-7", messages=msgs, temperature=1.0, max_tokens=8192))

        assert create_mock.await_args.kwargs["messages"] == msgs


# ---------------------------------------------------------------------------
# AC-7: call() is async (coroutine function)
# ---------------------------------------------------------------------------


class TestAC7CallIsAsync:
    def test_openai_call_is_coroutine_function(self):
        assert inspect.iscoroutinefunction(OpenAIAdapter.call)

    def test_anthropic_call_is_coroutine_function(self):
        assert inspect.iscoroutinefunction(AnthropicAdapter.call)

    def test_base_call_is_coroutine_function(self):
        assert inspect.iscoroutinefunction(ProviderAdapter.call)


# ---------------------------------------------------------------------------
# AC-8: Distinct SDK clients per __init__ (no global state)
# ---------------------------------------------------------------------------


class TestAC8DistinctClientsPerInit:
    @patch("src.foundation.provider_abstraction.adapters.openai_adapter.openai.AsyncOpenAI")
    def test_two_adapters_create_two_clients(self, mock_client_cls):
        OpenAIAdapter(api_key="k1")
        OpenAIAdapter(api_key="k2")
        assert mock_client_cls.call_count == 2
        call_kwargs = [c.kwargs for c in mock_client_cls.call_args_list]
        api_keys = [kw["api_key"] for kw in call_kwargs]
        assert api_keys == ["k1", "k2"]

    @patch("src.foundation.provider_abstraction.adapters.anthropic_adapter.anthropic.AsyncAnthropic")
    def test_two_anthropic_adapters_create_two_clients(self, mock_client_cls):
        AnthropicAdapter(api_key="k1")
        AnthropicAdapter(api_key="k2")
        assert mock_client_cls.call_count == 2


# ---------------------------------------------------------------------------
# AC-9: OpenAI empty content tolerated as empty string
# ---------------------------------------------------------------------------


class TestAC9OpenAIEmptyContentTolerated:
    @patch("src.foundation.provider_abstraction.adapters.openai_adapter.openai.AsyncOpenAI")
    def test_none_content_returns_empty_string(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=None))]
        mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=0)
        mock_client_cls.return_value.chat.completions.create = AsyncMock(return_value=mock_response)

        adapter = OpenAIAdapter(api_key="k")
        result = _aiorun(adapter.call(model="gpt-4o", messages=_MSGS, temperature=1.0, max_tokens=8192))
        assert result == ("", 10, 0)


# ---------------------------------------------------------------------------
# AC-10: SDK exceptions propagate raw (Story 003 wraps them)
# ---------------------------------------------------------------------------


class TestAC10SDKExceptionsPropagateRaw:
    @patch("src.foundation.provider_abstraction.adapters.openai_adapter.openai.AsyncOpenAI")
    def test_openai_runtime_error_propagates(self, mock_client_cls):
        mock_client_cls.return_value.chat.completions.create = AsyncMock(
            side_effect=RuntimeError("simulated SDK failure")
        )
        adapter = OpenAIAdapter(api_key="k")
        with pytest.raises(RuntimeError, match="simulated SDK failure"):
            _aiorun(adapter.call(model="gpt-4o", messages=_MSGS, temperature=1.0, max_tokens=8192))

    @patch("src.foundation.provider_abstraction.adapters.anthropic_adapter.anthropic.AsyncAnthropic")
    def test_anthropic_runtime_error_propagates(self, mock_client_cls):
        mock_client_cls.return_value.messages.create = AsyncMock(
            side_effect=RuntimeError("anthropic boom")
        )
        adapter = AnthropicAdapter(api_key="k")
        with pytest.raises(RuntimeError, match="anthropic boom"):
            _aiorun(adapter.call(model="claude-opus-4-7", messages=_MSGS, temperature=1.0, max_tokens=8192))


# ---------------------------------------------------------------------------
# Bonus: ProviderAdapter base class is abstract — call() raises NotImplementedError
# ---------------------------------------------------------------------------


class TestBaseClassNotImplemented:
    def test_base_call_raises_not_implemented(self):
        adapter = ProviderAdapter()
        with pytest.raises(NotImplementedError):
            _aiorun(adapter.call(model="x", messages=_MSGS, temperature=1.0, max_tokens=1))
