"""PMEP types — EvolutionFailedError exception envelope.

Per GDD Rule 6: diagnostic envelope for post-match evolution failures.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvolutionFailedError(Exception):
    """GDD Rule 6 — diagnostic envelope for post-match evolution failures.

    Raised by `evolve_strategy` when retries exhaust or non-retriable error
    surfaces. The previous `current.py` is left unchanged on disk.
    """

    team_id: str
    match_number: int
    attempts_made: int
    last_failure: str  # see GDD Rule 6 + EC-PMEP-01/EC-PMEP-11 string set
    cause: Exception | None = None

    def __str__(self) -> str:
        return (
            f"evolution failed for {self.team_id} at match {self.match_number} "
            f"after {self.attempts_made} attempt(s): {self.last_failure}"
        )