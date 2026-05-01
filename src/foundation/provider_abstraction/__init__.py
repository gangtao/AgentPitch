"""Provider Abstraction Layer (PAL) — single async generate() interface for all LLM calls.

Re-exports the public surface defined across this subpackage.
"""

from src.foundation.provider_abstraction.generate import (
    PAL_MAX_TOKENS,
    PAL_RETRY_BASE_DELAY_S,
    PAL_RETRY_MAX_ATTEMPTS,
    PAL_TEMPERATURE,
    generate,
)
from src.foundation.provider_abstraction.models import LLMCallError, LLMResponse

__all__ = [
    "LLMCallError",
    "LLMResponse",
    "generate",
    "PAL_TEMPERATURE",
    "PAL_MAX_TOKENS",
    "PAL_RETRY_MAX_ATTEMPTS",
    "PAL_RETRY_BASE_DELAY_S",
]
