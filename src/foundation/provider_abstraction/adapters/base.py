"""Provider Adapter abstract base class.

Subclasses encapsulate one LLM SDK behind a single async `call()` method.
Each adapter MUST return the (text, input_tokens, output_tokens) tuple — the
raw SDK response object never leaves the adapter boundary (per ADR-0007).
"""

from __future__ import annotations


class ProviderAdapter:
    """Abstract base for LLM provider adapters.

    Subclasses MUST:
      - implement `async def call(...)` returning `(text, input_tokens, output_tokens)`
      - construct their SDK client in `__init__` from the api_key argument
      - never leak SDK response objects past the call() boundary

    SDK exceptions are NOT wrapped here — Story 003's `generate()` orchestrator
    classifies exceptions, retries, and wraps in `LLMCallError`.
    """

    async def call(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> tuple[str, int, int]:
        raise NotImplementedError("Subclasses must implement async call()")
