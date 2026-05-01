"""CGP generate.py — async generate_strategy coroutine implementation.

GDD Rule 2: mandatory step sequence (build prompt + token check outside retry;
PAL + extract + compile inside retry; write_strategy outside retry).
GDD Rule 3: retry loop wraps steps 3-6 only.
"""

from __future__ import annotations

import importlib
import logging
from pathlib import Path

from src.foundation.code_generation_pipeline.classifier import _classify_failure
from src.foundation.code_generation_pipeline.extraction import (
    extract_decide_code,
    extract_decide_code_js,
    extract_decide_code_rust,
)
from src.foundation.code_generation_pipeline.metadata import _build_metadata
from src.foundation.code_generation_pipeline.types import (
    GenerationFailedError,
    PromptContextOverflowError,
)
from src.foundation.config_models import MatchConfig
from src.foundation.sandbox import ExecutionStatus, Sandbox
from src.foundation.system_prompt_builder import build_generation_prompt

logger = logging.getLogger(__name__)

_FENCE = {"python": "python", "javascript": "javascript", "rust": "rust"}


def _build_repair_prompt(failed_code: str, error: str, language: str) -> str:
    """Build a focused repair prompt that feeds the compile error back to the LLM."""
    fence = _FENCE.get(language, language)
    return (
        f"The following {language} code failed to compile:\n\n"
        f"```{fence}\n{failed_code}\n```\n\n"
        f"Compile error:\n{error}\n\n"
        f"Fix only the compile error. Return the corrected complete code "
        f"in a {fence} fenced code block. No explanation."
    )


async def generate_strategy(
    config: MatchConfig,
    team_id: str,
    language: str = "python",
    strategy_log_dir: Path | None = None,
) -> str:
    """GDD Rule 2 — mandatory step sequence; returns the persisted code string.

    Outside retry: build prompt, token check, write_strategy.
    Inside retry (CGP_MAX_RETRIES attempts): pal.generate, extract, compile.

    Args:
        config: Complete match configuration with team settings
        team_id: "team_a" or "team_b" (ADR-0004 format)
        language: Strategy language — "python" (default), "javascript", or "rust"

    Returns:
        The compiled and persisted strategy code string

    Raises:
        PromptContextOverflowError: prompt too large for LLM context limit
        GenerationFailedError: exhausted retries or non-retriable failure
        WriteFailedError: strategy persistence failed (propagates raw)
    """
    # Step 1: Build prompt (outside retry)
    prompt_result = build_generation_prompt(language=language)

    # Step 2: Token check (outside retry; raises PromptContextOverflowError)
    cgp_constants = importlib.import_module("src.foundation.code_generation_pipeline.constants")
    if prompt_result.estimated_tokens > cgp_constants.CGP_CONTEXT_LIMIT_TOKENS:
        raise PromptContextOverflowError(
            team_id=team_id,
            estimated_tokens=prompt_result.estimated_tokens,
            context_limit=cgp_constants.CGP_CONTEXT_LIMIT_TOKENS,
        )

    # Resolve PAL + storage at call time for monkeypatch support
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")
    storage_mod = importlib.import_module("src.foundation.strategy_storage")

    from src.foundation.provider_abstraction.models import LLMResponse as _LLMResponse

    # Look up custom provider metadata (type/url) from llm-providers.yaml so PAL
    # can resolve providers like "openrouter" that are not in the built-in registry.
    from pathlib import Path
    from src.foundation.llm_settings import load_llm_settings, get_default_provider
    data_home = Path(config.output.log_dir).parent
    llm_cfg = load_llm_settings(data_home)
    team_cfg = getattr(config, team_id)
    effective_provider = getattr(team_cfg, "llm_provider", None) or get_default_provider(data_home)
    prov_meta = (llm_cfg["providers"] or {}).get(effective_provider) or {}
    provider_type: str | None = prov_meta.get("type") if isinstance(prov_meta, dict) else None
    base_url: str | None = prov_meta.get("url") if isinstance(prov_meta, dict) else None

    last_failure_reason: str = "unknown"
    last_cause: Exception | None = None
    code_str: str | None = None
    response: _LLMResponse | None = None
    active_prompt: str = prompt_result.text  # may be replaced by repair prompt on compile error

    # Steps 3-6 — retry loop
    for attempt in range(1, cgp_constants.CGP_MAX_RETRIES + 1):
        logger.info("cgp: %s attempt %d/%d", team_id, attempt, cgp_constants.CGP_MAX_RETRIES)
        print(f"cgp: {team_id} calling {effective_provider} (attempt {attempt}/{cgp_constants.CGP_MAX_RETRIES})…", flush=True)

        # Step 3: PAL.generate
        try:
            response = await pal_gen_mod.generate(
                active_prompt, team_id, config,
                provider_type=provider_type, base_url=base_url,
            )
        except Exception as exc:  # PAL raises LLMCallError; classify it
            reason, retriable = _classify_failure(exc)
            logger.warning("cgp: %s %s (attempt %d): %s", team_id, reason, attempt, exc)
            print(f"cgp: {team_id} {reason} (attempt {attempt}): {exc}", flush=True)
            last_failure_reason = reason
            last_cause = exc if isinstance(exc, Exception) else None
            if not retriable:
                raise GenerationFailedError(
                    team_id=team_id,
                    attempts_made=attempt,
                    last_failure=last_failure_reason,
                    cause=last_cause,
                )
            continue

        # Empty response is its own retriable reason
        if not response.text:
            logger.warning("cgp: %s empty_response (attempt %d)", team_id, attempt)
            last_failure_reason = "empty_response"
            last_cause = None
            continue

        # Steps 4-5: Extract + def decide( / function decide( check
        if language == "javascript":
            code, extract_err = extract_decide_code_js(response.text)
        elif language == "rust":
            code, extract_err = extract_decide_code_rust(response.text)
        else:
            code, extract_err = extract_decide_code(response.text)
        if extract_err is not None:
            logger.warning("cgp: %s %s (attempt %d)", team_id, extract_err, attempt)
            last_failure_reason = extract_err
            last_cause = None
            continue

        # Step 6: sandbox.compile gate
        if language == "javascript":
            from src.foundation.sandbox.quickjs_sandbox import QuickJSSandbox
            sandbox: Sandbox = QuickJSSandbox()  # type: ignore[assignment]
        elif language == "rust":
            from src.foundation.sandbox.wasm_sandbox import WasmtimeSandbox
            sandbox = WasmtimeSandbox()  # type: ignore[assignment]
        else:
            sandbox = Sandbox()
        result = sandbox.compile(team_id, code)
        if result.status != ExecutionStatus.SUCCESS:
            logger.warning("cgp: %s compile_error (attempt %d)", team_id, attempt)
            last_failure_reason = "compile_error"
            last_cause = None
            active_prompt = _build_repair_prompt(code, result.error_message or result.error_type or "compile error", language)
            continue

        # Success — exit retry loop
        code_str = code
        break

    if code_str is None:
        raise GenerationFailedError(
            team_id=team_id,
            attempts_made=cgp_constants.CGP_MAX_RETRIES,
            last_failure=last_failure_reason,
            cause=last_cause,
        )

    # Step 7: Write (outside retry; WriteFailedError propagates raw)
    size_bytes = len(code_str.encode("utf-8"))
    metadata = _build_metadata(team_id, config, prompt_result, language=language, response=response, strategy_size_bytes=size_bytes)
    log_dir = strategy_log_dir if strategy_log_dir is not None else Path(config.output.log_dir)
    storage_mod.write_strategy(log_dir, team_id, code_str, metadata)

    logger.info("cgp: %s success — strategy written, code length %d", team_id, len(code_str))
    return code_str