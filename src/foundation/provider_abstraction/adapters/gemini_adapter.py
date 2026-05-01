"""Google Gemini provider adapter.

Imports the `google-genai` SDK at module load time. This module is only imported
when the registry resolves the `gemini` provider (lazy via Story 003's
`_adapter_cache`), so app boot does not require the SDK on the import path.
"""

from __future__ import annotations

from google import genai
from google.genai import types

from src.foundation.provider_abstraction.adapters.base import ProviderAdapter


class GeminiAdapter(ProviderAdapter):
    """Adapter for Google Gemini's generative AI API.

    Uses `google.genai.Client(api_key=...).aio.models.generate_content(...)`.
    Converts OpenAI-style messages to Gemini's contents format.
    """

    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        # base_url accepted for interface consistency but ignored - Gemini has fixed endpoints
        self.client = genai.Client(api_key=api_key)

    async def call(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> tuple[str, int, int]:
        # Convert OpenAI-style messages to Gemini contents format
        # OpenAI uses role: "user"/"assistant", Gemini uses role: "user"/"model"
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            content_text = msg.get("content") or ""
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=content_text)]
                )
            )

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        response = await self.client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

        # Extract text, coerce None to ""
        text = response.text or ""

        # Extract token counts from usage metadata (may be None on filtered responses).
        input_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
        output_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0

        return (text, input_tokens, output_tokens)
