"""CGP metadata builder — StrategyMetadata construction helper.

Per GDD Rule 8. Builds metadata for strategy persistence with composite
generated_by field that includes template version traceability.
"""

from __future__ import annotations

from pathlib import Path

from src.foundation.config_models import MatchConfig
from src.foundation.provider_abstraction.models import LLMResponse
from src.foundation.strategy_storage import StrategyMetadata
from src.foundation.system_prompt_builder import PromptResult
from src.foundation.llm_settings import get_team_llm_settings


def _build_metadata(
    team_id: str,
    config: MatchConfig,
    prompt_result: PromptResult,
    data_home: Path | None = None,
    language: str = "python",
    response: LLMResponse | None = None,
    strategy_size_bytes: int | None = None,
) -> StrategyMetadata:
    """Build StrategyMetadata for strategy storage with composite generated_by field.

    Per GDD Rule 8 — the generated_by field combines the module name with the
    template version for complete traceability of generation provenance.

    Args:
        team_id: "team_a" or "team_b" (ADR-0004 format)
        config: Complete match configuration with team settings
        prompt_result: SPB output containing template version
        data_home: Path to data directory for LLM settings lookup. If None,
            derives from `Path(config.output.log_dir).parent` for backward
            compatibility with callers that haven't been updated post-ADR-0021.

    Returns:
        StrategyMetadata with match_number=0 (pre-season) and composite generated_by
    """
    # Select the correct team config by team_id value (not dict lookup)
    team = config.team_a if team_id == "team_a" else config.team_b

    # Backward-compat: derive data_home from log_dir if caller didn't pass one.
    # Most existing callers predate ADR-0021 and don't know about data_home.
    if data_home is None:
        data_home = Path(config.output.log_dir).parent

    # Get LLM settings (handles deprecated fallback per ADR-0021)
    provider, model = get_team_llm_settings(team, data_home)

    return StrategyMetadata(
        team_id=team_id,
        match_number=0,  # Pre-season initial generation per GDD Rule 8
        llm_provider=provider,
        llm_model=model,
        generated_by=f"code-generation-pipeline/{prompt_result.template_version}",
        language=language,
        generation_latency_ms=response.latency_ms if response is not None else None,
        generation_input_tokens=response.input_tokens if response is not None else None,
        generation_output_tokens=response.output_tokens if response is not None else None,
        strategy_size_bytes=strategy_size_bytes,
    )