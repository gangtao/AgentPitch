"""Anthropic provider adapter.

Imports the `anthropic` SDK at module load time. Only loaded when the
registry resolves the `anthropic` provider (lazy via Story 003's
`_adapter_cache`).
"""

from __future__ import annotations

import anthropic

from src.foundation.provider_abstraction.adapters.base import ProviderAdapter


class AnthropicAdapter(ProviderAdapter):
    """Adapter for Anthropic's Messages API.

    Uses `anthropic.AsyncAnthropic(api_key=...).messages.create(...)`.
    Anthropic accepts OpenAI-style user-role messages directly per ADR-0007.
    """

    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        # base_url accepted for interface consistency but ignored - Anthropic has fixed endpoints
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def call(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> tuple[str, int, int]:
        response = await self.client.messages.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = response.content[0].text if response.content else ""
        return (
            text,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )
