"""PAL `generate()` orchestration — registry, lazy cache, retry/backoff, error normalization.

Single async entry point for all LLM calls. Per ADR-0007.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Optional

from src.foundation.provider_abstraction.adapters.anthropic_adapter import AnthropicAdapter
from src.foundation.provider_abstraction.adapters.base import ProviderAdapter
from src.foundation.provider_abstraction.adapters.gemini_adapter import GeminiAdapter
from src.foundation.provider_abstraction.adapters.openai_adapter import OpenAIAdapter
from src.foundation.provider_abstraction.models import LLMCallError, LLMResponse


# --- Module constants (per GDD §4) ---
PAL_TEMPERATURE: float = 1.0
PAL_MAX_TOKENS: int = 8192
PAL_RETRY_MAX_ATTEMPTS: int = 3
PAL_RETRY_BASE_DELAY_S: float = 1.0


# --- Provider registry (per GDD §1) ---
_ADAPTERS: dict[str, type[ProviderAdapter]] = {
    "openai": OpenAIAdapter,
    "anthropic": AnthropicAdapter,
    "gemini": GeminiAdapter,
}

# --- Type registry for custom providers ---
_TYPE_ADAPTERS: dict[str, type[ProviderAdapter]] = {
    "openai_compatible": OpenAIAdapter,
}


# --- Lazy adapter cache (per GDD §2) ---
# Key is (provider, api_key) so two teams using the same provider with
# different keys each get their own adapter instance.
_adapter_cache: dict[tuple[str, str], ProviderAdapter] = {}


def _reset_adapter_cache() -> None:
    """Test helper — clear the adapter cache between cases."""
    _adapter_cache.clear()


def _get_or_create_adapter(
    provider: str,
    api_key: str,
    *,
    provider_type: str | None = None,
    base_url: str | None = None,
) -> ProviderAdapter:
    """Lazy resolve. Module-level dict is GIL-protected; concurrent writes are
    safe at MVP scale per GDD edge case 5 (no lock needed for 2-provider system).

    Args:
        provider: Provider name (built-in or custom)
        api_key: API key for authentication
        provider_type: Type for custom providers (e.g., "openai_compatible")
        base_url: Custom API endpoint URL for OpenAI-compatible providers
    """
    # Resolve adapter class: check built-in first, then type registry
    adapter_cls = _ADAPTERS.get(provider)
    if adapter_cls is None and provider_type:
        adapter_cls = _TYPE_ADAPTERS.get(provider_type)
    if adapter_cls is None:
        raise KeyError(provider)

    # Cache per (provider, api_key) so different keys for the same provider
    # each get their own adapter instance (avoids silent key discarding).
    cache_key = (provider, api_key)
    if cache_key not in _adapter_cache:
        _adapter_cache[cache_key] = adapter_cls(api_key=api_key, base_url=base_url)
    return _adapter_cache[cache_key]


def _is_retriable(exc: BaseException) -> bool:
    """Classify SDK exceptions per ADR-0007 §Retry policy.

    Retriable: rate-limit (429), 5xx server errors, connection/timeout errors.
    Non-retriable: 401/403 auth, 404 model-not-found, 400 bad-request.
    Unknown / unexpected exceptions: non-retriable (wrapped in attempt 1
    per GDD edge case 7).
    """
    # Lazy-import SDK exception types so PAL works with only one SDK installed.
    try:
        import openai

        if isinstance(exc, (openai.APIConnectionError, openai.APITimeoutError, openai.RateLimitError)):
            return True
        if isinstance(exc, openai.APIStatusError):
            status_code = getattr(exc, "status_code", 0)
            if 500 <= status_code < 600:
                return True
        if isinstance(exc, openai.AuthenticationError):
            return False
    except ImportError:
        pass

    try:
        import anthropic

        if isinstance(exc, (anthropic.APIConnectionError, anthropic.APITimeoutError, anthropic.RateLimitError)):
            return True
        if isinstance(exc, anthropic.APIStatusError):
            status_code = getattr(exc, "status_code", 0)
            if 500 <= status_code < 600:
                return True
        if isinstance(exc, anthropic.AuthenticationError):
            return False
    except ImportError:
        pass

    try:
        from google import genai

        # Gemini exceptions - classify based on HTTP status patterns
        if hasattr(exc, "status_code"):
            status_code = exc.status_code
            if status_code in (429, 503) or 500 <= status_code < 600:
                return True
            if status_code in (401, 403):
                return False
    except ImportError:
        pass

    # Allow tests to inject custom retriable error types via duck-typing
    if getattr(exc, "_pal_retriable", None) is True:
        return True
    if getattr(exc, "_pal_retriable", None) is False:
        return False

    return False


async def generate(
    prompt: str,
    team_id: str,
    config: Any,
    *,
    provider_type: str | None = None,
    base_url: str | None = None,
) -> LLMResponse:
    """Single PAL entry point.

    Reads team's `llm_provider`, `llm_model`, `api_key` from `config.{team_id}`,
    resolves the adapter via `_ADAPTERS` + `_adapter_cache`, calls
    `adapter.call()` up to `PAL_RETRY_MAX_ATTEMPTS` times with `0/1/2`-second
    backoff for retriable errors. Returns `LLMResponse` on success or raises
    `LLMCallError` on failure.

    Args:
        prompt: The prompt text to send to the LLM
        team_id: Team identifier to look up config
        config: Config object with team settings accessible via getattr(config, team_id)
        provider_type: Optional provider type (e.g., "openai_compatible" for custom providers)
        base_url: Optional custom API endpoint URL (for OpenAI-compatible providers)

    Raises:
        LLMCallError: on any failure. `attempt_count` discriminates:
            - `1` = immediate non-retriable (auth, bad model, unrecognized provider, unexpected exc)
            - `PAL_RETRY_MAX_ATTEMPTS` = retriable error exhausted internal retries
    """
    team_cfg = getattr(config, team_id)
    provider = team_cfg.llm_provider
    model = team_cfg.llm_model
    api_key = team_cfg.api_key

    # Resolve adapter (or fail fast on unrecognized provider)
    try:
        adapter = _get_or_create_adapter(
            provider,
            api_key,
            provider_type=provider_type,
            base_url=base_url,
        )
    except KeyError as exc:
        raise LLMCallError(
            provider=provider,
            model=model,
            attempt_count=1,
            cause=exc,
            message=f"Unrecognized provider: {provider!r}",
        ) from exc

    messages = [{"role": "user", "content": prompt}]
    last_exc: Optional[BaseException] = None

    for attempt in range(1, PAL_RETRY_MAX_ATTEMPTS + 1):
        if attempt > 1:
            wait = PAL_RETRY_BASE_DELAY_S * (2 ** (attempt - 2))  # attempt 2 → 1s, 3 → 2s
            await asyncio.sleep(wait)

        start = time.perf_counter()
        try:
            text, input_tokens, output_tokens = await adapter.call(
                model=model,
                messages=messages,
                temperature=PAL_TEMPERATURE,
                max_tokens=PAL_MAX_TOKENS,
            )
        except Exception as exc:  # noqa: BLE001 — last-resort wrapper per GDD edge case 7
            last_exc = exc
            retriable = _is_retriable(exc)
            if retriable and attempt < PAL_RETRY_MAX_ATTEMPTS:
                continue
            # Non-retriable, OR final attempt of a retriable error → raise normalized
            raise LLMCallError(
                provider=provider,
                model=model,
                attempt_count=PAL_RETRY_MAX_ATTEMPTS if retriable else attempt,
                cause=exc,
            ) from exc

        latency_ms = (time.perf_counter() - start) * 1000.0
        return LLMResponse(
            text=text,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            attempt_count=attempt,
        )

    # Defensive — the loop should always either return or raise
    raise LLMCallError(
        provider=provider,
        model=model,
        attempt_count=PAL_RETRY_MAX_ATTEMPTS,
        cause=last_exc,
    )
