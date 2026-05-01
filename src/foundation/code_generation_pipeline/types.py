"""CGP exception types — diagnostic envelopes for generation pipeline failures.

Per GDD Rule 6 (exceptions) + ADR-0008 frozen dataclass convention.
These carry immutable post-mortem data for error analysis and retry logic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationFailedError(Exception):
    """LLM strategy code generation failed after exhausting retries.

    Carries diagnostic information for post-mortem analysis and user reporting.
    The `last_failure` field uses the enumerated failure modes from GDD Rule 6.
    """

    team_id: str
    attempts_made: int
    last_failure: str  # One of the GDD Rule 6 literal strings
    cause: Exception | None = None

    def __str__(self) -> str:
        return (
            f"generation failed for {self.team_id} after {self.attempts_made} "
            f"attempt(s): {self.last_failure}"
        )


@dataclass(frozen=True)
class PromptContextOverflowError(Exception):
    """Generated prompt exceeds LLM provider token limits.

    Thrown before attempting LLM call when estimated tokens exceed the
    configured context limit. Prevents wasted API calls and billing charges.
    """

    team_id: str
    estimated_tokens: int
    context_limit: int

    def __str__(self) -> str:
        return (
            f"prompt for {self.team_id} estimated {self.estimated_tokens} tokens "
            f"exceeds limit {self.context_limit}"
        )