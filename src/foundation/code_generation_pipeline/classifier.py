"""CGP failure classifier — collapses GDD Rule 5 retry-policy table into one decision."""

from __future__ import annotations
import importlib

# Failure reasons that are always retriable (string-based, from extraction step)
_RETRIABLE_REASONS = frozenset({
    "empty_response",
    "no_code_block",
    "no_decide_signature",
    "compile_error",
})


def _classify_failure(exc_or_reason: object) -> tuple[str, bool]:
    """GDD Rule 5 — return (failure_reason_string, retriable_flag).

    Inputs:
        - A reason string from the extraction/compile step → look up in _RETRIABLE_REASONS.
        - An LLMCallError instance → discriminate via `attempt_count` vs PAL_RETRY_MAX_ATTEMPTS.
        - Anything else → ("unknown", False) defensively.

    Reads PAL_RETRY_MAX_ATTEMPTS at call time via importlib so monkeypatch propagates.
    """
    if isinstance(exc_or_reason, str):
        if exc_or_reason in _RETRIABLE_REASONS:
            return (exc_or_reason, True)
        return (exc_or_reason, False)

    pal_models = importlib.import_module("src.foundation.provider_abstraction.models")
    pal_generate = importlib.import_module("src.foundation.provider_abstraction.generate")
    LLMCallError = pal_models.LLMCallError
    pal_max_attempts = pal_generate.PAL_RETRY_MAX_ATTEMPTS

    if isinstance(exc_or_reason, LLMCallError):
        attempt_count = getattr(exc_or_reason, "attempt_count", None)
        if attempt_count == pal_max_attempts:
            return ("llm_call_error", True)
        return ("llm_call_error", False)

    return ("unknown", False)