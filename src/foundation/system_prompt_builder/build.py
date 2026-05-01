"""SPB public entry points — build_generation_prompt + build_evolution_prompt.

Both functions are pure given the template cache (loaded by Story 002's
`load_templates()` at process startup). Same arguments produce identical
`result.text` byte-for-byte (per AC-SPB-13).

2026-04-25 cleanup: dropped the long-vestigial `config: MatchConfig` and
`team_id: str` arguments. Generation v2.0+ rendering is fully generic — neither
arg ever influenced the prompt — and `PromptResult.team_id` was never read
downstream. Callers now invoke without those positional args.
"""

from __future__ import annotations

import logging

from src.foundation.system_prompt_builder.helpers import (
    estimate_tokens,
    warn_if_over_threshold,
)
from src.foundation.system_prompt_builder.templates import get_template
from src.foundation.system_prompt_builder.types import PromptMode, PromptResult

_log = logging.getLogger(__name__)


def build_generation_prompt(user_intent: str = "", language: str = "python") -> PromptResult:
    """Build the GENERATION-mode prompt.

    Pure function: same `user_intent` produces identical output. No randomness,
    no I/O beyond the read-only template cache.

    `language` selects the template: "python" uses generation.jinja2,
    "javascript" uses generation-js.jinja2, "rust" uses generation-rust.jinja2.

    `user_intent` (added v2.5) splices natural-language guidance from the UI's
    New Strategy form into SECTION 13 of the prompt. Empty string (CGP/PMEP
    default) renders the fallback "no specific user intent" line.
    """
    if language == "javascript":
        mode = PromptMode.GENERATION_JS
    elif language == "rust":
        mode = PromptMode.GENERATION_RUST
    else:
        mode = PromptMode.GENERATION
    loaded = get_template(mode)
    text = loaded.template.render(user_intent=user_intent)
    estimated = estimate_tokens(text)
    warn_if_over_threshold(estimated)

    return PromptResult(
        text=text,
        mode=mode,
        estimated_tokens=estimated,
        template_version=loaded.version,
    )


def build_evolution_prompt(prev_strategy: str, match_summary: str, language: str = "python") -> PromptResult:
    """Build the EVOLUTION-mode prompt for the given language.

    Fallback rules (per GDD Detailed Design Rule 4):
      - prev_strategy empty/None → fall back to build_generation_prompt(),
        log WARNING.
      - match_summary empty/None → render evolution template with the
        "no match data" task-section note.

    `language` selects the template: "python" uses evolution.jinja2,
    "javascript" uses evolution-js.jinja2, "rust" uses evolution-rust.jinja2.

    prev_strategy is embedded VERBATIM — no whitespace stripping, no
    comment removal, no normalisation (per AC-SPB-17).
    """
    if not prev_strategy:
        _log.warning(
            "evolution_prompt: no prev_strategy provided, falling back to generation"
        )
        return build_generation_prompt(language=language)

    if language == "javascript":
        mode = PromptMode.EVOLUTION_JS
    elif language == "rust":
        mode = PromptMode.EVOLUTION_RUST
    else:
        mode = PromptMode.EVOLUTION

    summary_text = match_summary if match_summary else (
        "No match result is available. Improve general strategic quality based on the existing code."
    )

    loaded = get_template(mode)
    text = loaded.template.render(
        prev_strategy=prev_strategy,
        match_summary=summary_text,
    )
    estimated = estimate_tokens(text)
    warn_if_over_threshold(estimated)

    return PromptResult(
        text=text,
        mode=mode,
        estimated_tokens=estimated,
        template_version=loaded.version,
    )
