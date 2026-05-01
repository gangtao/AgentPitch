"""PMEP pre-loop helpers — input boundary gates before LLM retry loop.

GDD Rule 10 (StrategyNotFoundError handling) + EC-PMEP-01 (generate_summary wrapping).
Private helpers — not exported from __init__.py.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from src.foundation.post_match_evolution_pipeline.constants import (
    PMEP_SUMMARY_MAX_TOKENS,
)
from src.foundation.post_match_evolution_pipeline.types import EvolutionFailedError
from src.foundation.strategy_storage import StrategyNotFoundError, read_current

logger = logging.getLogger(__name__)


def _read_prev_strategy_or_fallback(
    log_dir: Path,
    team_id: str,
    match_number: int,
) -> str:
    """GDD Rule 10 — read prev strategy; on missing return "" and log per match_number.

    Empty string triggers SPB's EVOLUTION → GENERATION fallback (SPB Story 005 Rule 4).
    """
    try:
        return read_current(str(log_dir), team_id)
    except StrategyNotFoundError:
        if match_number == 1:
            logger.warning(
                "pmep: %s no prev strategy at match_number=1 (fresh season); falling back to generation",
                team_id,
            )
        else:
            logger.error(
                "pmep: %s no prev strategy at match_number=%d (mid-season — expected from prior evolution); falling back to generation",
                team_id,
                match_number,
            )
        return ""


def _generate_match_summary(
    match_log: Any,
    *,
    team_id: str,
    match_number: int,
) -> str:
    """GDD EC-PMEP-01 — wrap generate_summary; raise EvolutionFailedError on any exception."""
    try:
        return match_log.generate_summary(max_tokens=PMEP_SUMMARY_MAX_TOKENS)
    except Exception as exc:
        raise EvolutionFailedError(
            team_id=team_id,
            match_number=match_number,
            attempts_made=0,
            last_failure="generate_summary_error",
            cause=exc,
        ) from exc