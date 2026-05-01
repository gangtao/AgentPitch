"""PMEP metadata builder — StrategyMetadata construction for evolution pipeline."""

from __future__ import annotations

from pathlib import Path

from src.foundation.config_models import MatchConfig
from src.foundation.strategy_storage import StrategyMetadata
from src.foundation.system_prompt_builder.types import PromptResult
from src.foundation.llm_settings import get_team_llm_settings


def _build_metadata(
    team_id: str,
    config: MatchConfig,
    prompt_result: PromptResult,
    match_number: int,
    data_home: Path | None = None,
    language: str = "python",
) -> StrategyMetadata:
    """GDD Rule 8 — composite generated_by with no new StrategyMetadata field.

    Note: prefix is `post-match-evolution/...` (NOT `code-generation-pipeline/...`)
    to disambiguate evolution-written strategies from initial-generation files.

    Args:
        data_home: optional. If None, derived from `Path(config.output.log_dir).parent`
            for backward compatibility with callers that predate ADR-0021.
    """
    team = config.team_a if team_id == "team_a" else config.team_b

    # Backward-compat default (ADR-0021)
    if data_home is None:
        data_home = Path(config.output.log_dir).parent

    # Get LLM settings (handles deprecated fallback per ADR-0021)
    provider, model = get_team_llm_settings(team, data_home)

    return StrategyMetadata(
        team_id=team_id,
        match_number=match_number,
        llm_provider=provider,
        llm_model=model,
        generated_by=f"post-match-evolution/{prompt_result.template_version}",
        language=language,
    )