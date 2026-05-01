"""Fallback Handler data types — FallbackEvent + FallbackResult.

Both are frozen dataclasses (per ADR-0012). Schemas defined here are the
contract Match Log System (JSONL serialization) + Tick Engine (event
forwarding) consume.

Note: ExecutionStatus is owned by Code Sandbox (`src.foundation.sandbox.status`)
and re-exported here for downstream-callers' convenience. See ADR-0012 for the
6-value supersession of TR-FH-002's older 5-value GDD wording.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.foundation.action import Action
from src.foundation.sandbox.status import ExecutionStatus

__all__ = ["FallbackEvent", "FallbackResult", "ExecutionStatus"]


@dataclass(frozen=True)
class FallbackEvent:
    """Audit-trail record emitted on every non-SUCCESS sandbox result.

    10 fields exactly, in the schema order Match Log System depends on.
    Per ADR-0012:
      - `event_type` always "fallback"
      - `substituted_action` always "Hold"
      - `fallback_substituted` always True (distinguishes a fallback Hold from
        an intentional Hold returned by the LLM callback)

    Per ADR-0004: `player_id` is `str` in `{team_id}_{index}` format.
    """

    event_type: str               # always "fallback"
    tick: int
    player_id: str                # "team_a_2" (ADR-0004)
    team: str                     # "team_a" or "team_b"
    llm_provider: str             # "openai/gpt-4o" or similar
    failure_status: str           # ExecutionStatus.value as string
    error_type: Optional[str]     # exception class name or None (TIMEOUT/INVALID_RETURN)
    execution_time_ms: float
    substituted_action: str       # always "Hold"
    fallback_substituted: bool    # always True


@dataclass(frozen=True)
class FallbackResult:
    """Return type of `FallbackHandler.handle()`.

    `action` is always a `Hold()` instance (universal substitution per ADR-0012).
    `log_event` is `None` when DISABLED is suppressed (subsequent occurrences
    after the first per match — Story 003).
    """

    action: Action
    log_event: Optional[FallbackEvent]
