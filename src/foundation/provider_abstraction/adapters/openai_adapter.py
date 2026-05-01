"""OpenAI provider adapter.

Imports the `openai` SDK at module load time. This module is only imported
when the registry resolves the `openai` provider (lazy via Story 003's
`_adapter_cache`), so app boot does not require the SDK on the import path.
"""

from __future__ import annotations

import openai

from src.foundation.provider_abstraction.adapters.base import ProviderAdapter


class OpenAIAdapter(ProviderAdapter):
    """Adapter for OpenAI's chat completions API.

    Uses `openai.AsyncOpenAI(api_key=...).chat.completions.create(...)`.
    Supports custom base_url for OpenAI-compatible APIs (Ollama, vLLM, etc.).
    """

    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = openai.AsyncOpenAI(**kwargs)

    async def call(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> tuple[str, int, int]:
        # `max_completion_tokens` is the modern parameter (required by gpt-5,
        # o1/o3 reasoning models). Older chat models accept it too. The
        # adapter base signature still spells the kwarg `max_tokens` for API
        # stability — only the SDK call site changes here.
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
        )
        # `.message.content` may be None when the model returns no text — coerce to "".
        text = response.choices[0].message.content or ""
        return (text, response.usage.prompt_tokens, response.usage.completion_tokens)
