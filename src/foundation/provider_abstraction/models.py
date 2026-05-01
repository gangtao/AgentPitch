"""Provider Abstraction Layer (PAL) — data models.

`LLMResponse` is the immutable shape of a successful PAL call result.
`LLMCallError` is the single normalized exception PAL raises; its
`attempt_count` field is the retry discriminator CGP/PMEP branch on per
the Feature-layer control manifest rules.

Per ADR-0007.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LLMResponse:
    """Immutable response from a successful LLM call routed through PAL.

    All SDK-specific response objects are converted into this shape before
    leaving PAL. Callers must not depend on SDK response types.

    Attributes:
        text: The generated text (model output, post-extraction).
        provider: One of "openai" / "anthropic".
        model: Provider-specific model identifier (e.g. "gpt-4o").
        input_tokens: Prompt token count from SDK usage report.
        output_tokens: Generated token count from SDK usage report.
        latency_ms: Wall-clock duration of the SDK call in milliseconds.
        attempt_count: 1 = first try; 2-3 = required retries (max =
            PAL_RETRY_MAX_ATTEMPTS).
    """

    text: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    attempt_count: int


class LLMCallError(Exception):
    """Single normalized PAL exception type.

    Wraps any SDK-specific exception via the `cause` field. Callers MUST NOT
    catch SDK-specific exceptions — `attempt_count` is the discriminator
    CGP/PMEP use to decide retriable vs non-retriable per the Feature-layer
    control manifest:

      - `attempt_count == 1`: non-retriable (auth, bad model, unrecognized
        provider, unexpected exc) — PAL gave up immediately.
      - `attempt_count == PAL_RETRY_MAX_ATTEMPTS` (3 by default): a retriable
        error exhausted PAL's internal retry loop.
    """

    def __init__(
        self,
        provider: str,
        model: str,
        attempt_count: int,
        cause: Optional[Exception] = None,
        message: str = "",
    ) -> None:
        self.provider = provider
        self.model = model
        self.attempt_count = attempt_count
        self.cause = cause
        super().__init__(
            message
            or f"LLM call failed: provider={provider} model={model} attempt_count={attempt_count}"
        )
