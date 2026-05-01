"""Post-Match Evolution Pipeline — feature layer for evolving strategies after matches.

Public API exports from PMEP foundation modules. Note: _build_metadata is private
and not re-exported — tests import via fully-qualified path.
"""

from __future__ import annotations

from src.foundation.post_match_evolution_pipeline.evolve import evolve_strategy
from src.foundation.post_match_evolution_pipeline.types import EvolutionFailedError
from src.foundation.post_match_evolution_pipeline.constants import (
    PMEP_MAX_RETRIES,
    PMEP_CONTEXT_LIMIT_TOKENS,
    PMEP_SUMMARY_MAX_TOKENS,
)

__all__ = [
    "evolve_strategy",
    "EvolutionFailedError",
    "PMEP_MAX_RETRIES",
    "PMEP_CONTEXT_LIMIT_TOKENS",
    "PMEP_SUMMARY_MAX_TOKENS",
]