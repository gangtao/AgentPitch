"""PMEP evolve.py — async evolve_strategy coroutine implementation.

GDD Rule 2: mandatory step sequence (read prev_strategy, generate summary,
build evolution prompt, mode check, token check outside retry;
PAL + extract + compile inside retry; write_strategy outside retry).
GDD Rule 3: retry loop wraps steps 6-9 only.
"""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any, Callable

# Reuse CGP helpers — extraction functions + _classify_failure are shared with CGP.
from src.foundation.code_generation_pipeline.classifier import _classify_failure
from src.foundation.code_generation_pipeline.extraction import (
    extract_decide_code,
    extract_decide_code_js,
    extract_decide_code_rust,
)
from src.foundation.code_generation_pipeline.generate import _build_repair_prompt
from src.foundation.config_models import MatchConfig
from src.foundation.post_match_evolution_pipeline.metadata import _build_metadata
from src.foundation.post_match_evolution_pipeline.preloop import (
    _generate_match_summary,
    _read_prev_strategy_or_fallback,
)
from src.foundation.post_match_evolution_pipeline.types import EvolutionFailedError
from src.foundation.system_prompt_builder import build_evolution_prompt
from src.foundation.system_prompt_builder.types import PromptMode

logger = logging.getLogger(__name__)


async def evolve_strategy(
    config: MatchConfig,
    team_id: str,
    match_log: Any,
    match_number: int,
    strategy_log_dir: Path | None = None,
    on_event: Callable[[str, dict], None] | None = None,
    language: str = "python",
) -> str:
    """GDD Rule 2 — mandatory step sequence; returns the persisted code string.

    Outside retry: read prev_strategy, generate summary, build prompt, mode check,
    token check, write_strategy.
    Inside retry (PMEP_MAX_RETRIES attempts): pal.generate, extract, sandbox.compile.
    """
    log_dir = strategy_log_dir if strategy_log_dir is not None else Path(config.output.log_dir)
    logger.info("pmep: %s evolution started for match_number=%d", team_id, match_number)

    # Step 1: Read prev_strategy with StrategyNotFoundError handling (Rule 10)
    prev_strategy = _read_prev_strategy_or_fallback(log_dir, team_id, match_number)

    # Step 2: Generate match summary (raises EvolutionFailedError on exception)
    match_summary = _generate_match_summary(match_log, team_id=team_id, match_number=match_number)

    # Step 3: Build evolution prompt (any exception → EvolutionFailedError immediately)
    try:
        prompt_result = build_evolution_prompt(prev_strategy, match_summary, language=language)
    except Exception as exc:
        raise EvolutionFailedError(
            team_id=team_id,
            match_number=match_number,
            attempts_made=0,
            last_failure="prompt_build_error",
            cause=exc,
        ) from exc

    # Step 4: Mode check — log if SPB triggered generation fallback (Rule 2 step 4)
    if prompt_result.mode == PromptMode.GENERATION:
        logger.warning(
            "pmep: %s SPB returned generation mode (fallback); prev_strategy was empty",
            team_id,
        )

    # Step 5: Token check (outside retry)
    pmep_constants = importlib.import_module(
        "src.foundation.post_match_evolution_pipeline.constants"
    )
    if prompt_result.estimated_tokens > pmep_constants.PMEP_CONTEXT_LIMIT_TOKENS:
        raise EvolutionFailedError(
            team_id=team_id,
            match_number=match_number,
            attempts_made=0,
            last_failure="context_overflow",
        )

    # Resolve dependencies at call time (monkeypatch friendly)
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")
    sandbox_mod = importlib.import_module("src.foundation.sandbox")
    storage_mod = importlib.import_module("src.foundation.strategy_storage")

    # Look up custom provider metadata so PAL can resolve non-built-in providers.
    from src.foundation.llm_settings import load_llm_settings
    data_home = Path(config.output.log_dir).parent
    llm_cfg = load_llm_settings(data_home)
    team_cfg = getattr(config, team_id)
    effective_provider = getattr(team_cfg, "llm_provider", None)
    prov_meta = (llm_cfg["providers"] or {}).get(effective_provider) or {} if effective_provider else {}
    provider_type: str | None = prov_meta.get("type") if isinstance(prov_meta, dict) else None
    base_url: str | None = prov_meta.get("url") if isinstance(prov_meta, dict) else None

    last_failure_reason: str = "unknown"
    last_cause: Exception | None = None
    code_str: str | None = None
    active_prompt: str = prompt_result.text  # may be replaced by repair prompt on compile error
    if language == "javascript":
        from src.foundation.sandbox.quickjs_sandbox import QuickJSSandbox
        sandbox = QuickJSSandbox()
    elif language == "rust":
        from src.foundation.sandbox.wasm_sandbox import WasmtimeSandbox
        sandbox = WasmtimeSandbox()
    else:
        sandbox = sandbox_mod.Sandbox()

    # Steps 6-9 — retry loop
    for attempt in range(1, pmep_constants.PMEP_MAX_RETRIES + 1):
        logger.info("pmep: %s attempt %d/%d", team_id, attempt, pmep_constants.PMEP_MAX_RETRIES)
        print(f"pmep: {team_id} calling {effective_provider} (attempt {attempt}/{pmep_constants.PMEP_MAX_RETRIES})…", flush=True)
        if on_event:
            on_event("pmep-attempt", {
                "match_number": match_number,
                "team_id": team_id,
                "attempt": attempt,
                "max_attempts": pmep_constants.PMEP_MAX_RETRIES,
                "provider": effective_provider,
            })
        try:
            response = await pal_gen_mod.generate(
                active_prompt, team_id, config,
                provider_type=provider_type, base_url=base_url,
            )
        except Exception as exc:
            reason, retriable = _classify_failure(exc)
            logger.warning(
                "pmep: %s pal failure attempt %d: %s (retriable=%s): %s",
                team_id, attempt, reason, retriable, exc,
            )
            print(f"pmep: {team_id} {reason} (attempt {attempt}, retriable={retriable}): {exc}", flush=True)
            last_failure_reason = reason
            last_cause = exc if isinstance(exc, Exception) else None
            if on_event:
                on_event("pmep-attempt-failed", {
                    "match_number": match_number,
                    "team_id": team_id,
                    "attempt": attempt,
                    "reason": reason,
                    "retriable": retriable,
                })
            if not retriable:
                raise EvolutionFailedError(
                    team_id=team_id,
                    match_number=match_number,
                    attempts_made=attempt,
                    last_failure=last_failure_reason,
                    cause=last_cause,
                )
            continue

        if not response.text:
            logger.warning("pmep: %s empty_response attempt %d", team_id, attempt)
            last_failure_reason = "empty_response"
            last_cause = None
            if on_event:
                on_event("pmep-attempt-failed", {
                    "match_number": match_number,
                    "team_id": team_id,
                    "attempt": attempt,
                    "reason": "empty_response",
                    "retriable": True,
                })
            continue

        if language == "javascript":
            code, extract_err = extract_decide_code_js(response.text)
        elif language == "rust":
            code, extract_err = extract_decide_code_rust(response.text)
        else:
            code, extract_err = extract_decide_code(response.text)
        if extract_err is not None:
            logger.warning("pmep: %s %s attempt %d", team_id, extract_err, attempt)
            last_failure_reason = extract_err
            last_cause = None
            if on_event:
                on_event("pmep-attempt-failed", {
                    "match_number": match_number,
                    "team_id": team_id,
                    "attempt": attempt,
                    "reason": extract_err,
                    "retriable": True,
                })
            continue

        compile_result = sandbox.compile(team_id, code)
        if compile_result.status != sandbox_mod.ExecutionStatus.SUCCESS:
            logger.warning(
                "pmep: %s compile_error attempt %d (%s)",
                team_id, attempt, compile_result.error_type,
            )
            last_failure_reason = "compile_error"
            last_cause = None
            active_prompt = _build_repair_prompt(code, compile_result.error_message or compile_result.error_type or "compile error", language)
            if on_event:
                on_event("pmep-attempt-failed", {
                    "match_number": match_number,
                    "team_id": team_id,
                    "attempt": attempt,
                    "reason": "compile_error",
                    "retriable": True,
                })
            continue

        code_str = code
        break

    if code_str is None:
        raise EvolutionFailedError(
            team_id=team_id,
            match_number=match_number,
            attempts_made=pmep_constants.PMEP_MAX_RETRIES,
            last_failure=last_failure_reason,
            cause=last_cause,
        )

    # No-op evolution detection (AC-PMEP-12 + EC-PMEP-08)
    if code_str == prev_strategy:
        logger.info("pmep: %s no-op evolution detected (identical to prev_strategy)", team_id)

    # Step 10: Write (outside retry; WriteFailedError propagates raw)
    metadata = _build_metadata(team_id, config, prompt_result, match_number, language=language)
    storage_mod.write_strategy(log_dir, team_id, code_str, metadata)

    logger.info("pmep: %s success — strategy written for match_number=%d, code length %d",
                team_id, match_number, len(code_str))
    return code_str