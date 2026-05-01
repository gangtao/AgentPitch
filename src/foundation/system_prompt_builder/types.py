"""SPB data types — PromptMode enum + PromptResult frozen dataclass.

Per ADR-0007 / ADR-0012 conventions for runtime envelopes: dataclass(frozen=True)
not Pydantic (the latter is reserved for config models loaded from YAML).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PromptMode(Enum):
    """Valid modes for SPB prompt construction.

    Downstream callers (CGP, PMEP) check `result.mode == PromptMode.GENERATION`
    to detect generation fallback when an EVOLUTION call had empty prev_strategy.
    """

    GENERATION = "generation"
    GENERATION_JS = "generation-js"
    GENERATION_RUST = "generation-rust"
    EVOLUTION = "evolution"
    EVOLUTION_JS = "evolution-js"
    EVOLUTION_RUST = "evolution-rust"


@dataclass(frozen=True)
class PromptResult:
    """Frozen envelope returned by build_generation_prompt / build_evolution_prompt.

    Downstream callers read `.text` to feed PAL.generate(), check `.mode` for
    fallback detection, and persist `.template_version` into
    StrategyMetadata.generated_by for prompt-version traceability.

    Note: `team_id` was removed 2026-04-25 — no consumer ever read it (callers
    always carried their own team_id in surrounding scope).
    """

    text: str
    mode: PromptMode
    estimated_tokens: int      # ceil(len(text) / SPB_TOKEN_CHARS_RATIO)
    template_version: str      # extracted from {# version: X #} comment
