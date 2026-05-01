"""FallbackHandler — universal Hold() substitution + audit-trail emission.

Stateless transform from `SandboxResult` to `FallbackResult` (per ADR-0012),
**aside from** a per-match `_disabled_logged_set` that suppresses duplicate
DISABLED log events (one per player per match max).

Every non-SUCCESS sandbox result is converted into a `Hold()` action plus an
optional `FallbackEvent` record. The handler never silences failures — it
categorizes them and bounds the log volume for the persistent DISABLED state.
"""

from __future__ import annotations

from typing import Callable, Optional, Set

from src.foundation.action import Hold
from src.foundation.fallback.types import (
    ExecutionStatus,
    FallbackEvent,
    FallbackResult,
)
from src.foundation.sandbox.result import SandboxResult


class FallbackHandler:
    """Handler for non-SUCCESS sandbox results.

    Per-match state:
      - `_disabled_logged_set`: player_ids that have already emitted a DISABLED
        FallbackEvent this match. Cleared by `reset_for_match()` at match start.

    The optional `log_emitter` callable receives every emitted FallbackEvent.
    Log-emission failures are silently swallowed (per GDD Rule 7) — a buggy
    Match Log System must never abort the match.
    """

    def __init__(self, log_emitter: Optional[Callable[[FallbackEvent], None]] = None) -> None:
        self._log_emitter = log_emitter
        self._disabled_logged_set: Set[str] = set()

    def reset_for_match(self) -> None:
        """Clear per-match state. Called by the Tick Engine at match start.

        After this call, the next DISABLED result for any player emits a fresh
        FallbackEvent (suppression starts over for the new match).
        """
        self._disabled_logged_set.clear()

    def handle(
        self,
        result: SandboxResult,
        player_id: str,
        team: str,
        llm_provider: str,
        tick: int,
    ) -> FallbackResult:
        """Convert a non-SUCCESS SandboxResult into a FallbackResult.

        Action selection (per ADR-0012):
          - DISABLED: reuse `result.action` (Hold pre-filled by sandbox)
          - EXCEPTION / TIMEOUT / INVALID_RETURN / COMPILE_ERROR: fresh `Hold()`

        DISABLED suppression: the FIRST DISABLED for a player emits a
        FallbackEvent and adds the player_id to `_disabled_logged_set`.
        Subsequent DISABLEDs for the same player return `log_event=None`
        (the action is still the prefilled Hold — suppression affects the
        log only, not the action).

        Log emission: `_log_emitter` exceptions (any BaseException including
        SystemExit / KeyboardInterrupt) are silently swallowed; on failure,
        `log_event=None` is returned to the caller.
        """
        provider = llm_provider if llm_provider else "unknown"

        # Action selection (unchanged from Story 002)
        if result.status is ExecutionStatus.DISABLED:
            action = result.action  # reuse sandbox-prefilled Hold (AC-FH-04)
        else:
            action = Hold()  # fresh per-call (AC-FH-01/02/03)

        # DISABLED suppression — if this player's DISABLED was already logged
        # this match, skip event construction entirely.
        if (
            result.status is ExecutionStatus.DISABLED
            and player_id in self._disabled_logged_set
        ):
            return FallbackResult(action=action, log_event=None)

        # Construct the event (unchanged from Story 002)
        event = FallbackEvent(
            event_type="fallback",
            tick=tick,
            player_id=player_id,
            team=team,
            llm_provider=provider,
            failure_status=result.status.name,
            error_type=result.error_type,
            execution_time_ms=result.execution_time_ms,
            substituted_action="Hold",
            fallback_substituted=True,
        )

        # Best-effort log emit; swallow any exception (per GDD Rule 7).
        log_event_for_caller: Optional[FallbackEvent] = event
        if self._log_emitter is not None:
            try:
                self._log_emitter(event)
            except BaseException:  # noqa: BLE001 — log failure must never abort match
                log_event_for_caller = None

        # Record DISABLED in suppression set AFTER the emit attempt, regardless
        # of success/failure — the "first DISABLED" signal is best-effort, not retried.
        if result.status is ExecutionStatus.DISABLED:
            self._disabled_logged_set.add(player_id)

        return FallbackResult(action=action, log_event=log_event_for_caller)
