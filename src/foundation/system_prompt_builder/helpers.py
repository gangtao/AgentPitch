"""SPB helpers — token estimation + tuning constants.

Per ADR-0007 conventions: module-level constants with `SPB_` prefix; pure
functions; no I/O beyond the read-only template cache from Story 002.

Note: `_build_team_context` was removed in 2026-04-25 — generation v2.4
and evolution v2.0 dropped all per-team Jinja substitutions, so the
team_context dict is no longer consumed by either template.
"""

from __future__ import annotations

import logging
import math

_log = logging.getLogger(__name__)


# Tuning knobs (per GDD Tuning Knobs section)
SPB_WARN_TOKEN_THRESHOLD: int = 12000
SPB_MAX_KEY_EVENTS: int = 5
SPB_TOKEN_CHARS_RATIO: float = 3.5


def estimate_tokens(text: str) -> int:
    """SPB Formula 1 — approximate token count for a rendered prompt.

    Uses chars-per-token ratio (3.5 default) — accurate ±15% for English +
    Python prompt content per the GDD.
    """
    return math.ceil(len(text) / SPB_TOKEN_CHARS_RATIO)


def warn_if_over_threshold(estimated: int) -> None:
    """Emit a WARNING log entry if `estimated` strictly exceeds the threshold.

    Soft signal only — CGP/PMEP own the hard `CGP_CONTEXT_LIMIT_TOKENS=16000`
    ceiling (per ADR-0007). This warning fires earlier (at 12000 default) so
    researchers see the prompt approaching the limit before CGP rejects.
    """
    if estimated > SPB_WARN_TOKEN_THRESHOLD:
        _log.warning(
            "SPB token estimate %d exceeds SPB_WARN_TOKEN_THRESHOLD=%d "
            "(prompt may approach CGP/PMEP context limit)",
            estimated,
            SPB_WARN_TOKEN_THRESHOLD,
        )
