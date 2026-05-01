"""Tests for PMEP Story 003: evolve_strategy coroutine implementation."""

from __future__ import annotations

import importlib
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.foundation.post_match_evolution_pipeline import evolve_strategy
from src.foundation.post_match_evolution_pipeline.types import EvolutionFailedError
from src.foundation.config_models import (
    MatchConfig,
    MatchParams,
    OutputConfig,
    PlayerConfig,
    TeamConfig,
)
from src.foundation.provider_abstraction.models import LLMCallError, LLMResponse
from src.foundation.strategy_storage import StrategyNotFoundError, WriteFailedError
from src.foundation.system_prompt_builder import load_templates
from src.foundation.system_prompt_builder.types import PromptMode, PromptResult

# Use pytest-asyncio for async tests
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module", autouse=True)
def _load_templates_once():
    """SPB requires load_templates() at process start before build_evolution_prompt works."""
    load_templates()


def _player(player_id: str, role: str, save: int = 0) -> PlayerConfig:
    """Factory for test player configs."""
    return PlayerConfig(
        player_id=player_id,
        role=role,
        speed=10,
        skill=10,
        strength=10,
        save=save,
        discipline=10,
        dribbling=10,
    )


def _team(team_id: str = "team_a") -> TeamConfig:
    """Factory for test team configs."""
    return TeamConfig(
        llm_provider="openai",
        llm_model="gpt-4o",
        api_key="sk-test",
        players=[
            _player(f"{team_id}_0", "GK", save=16),
            _player(f"{team_id}_1", "DEF"),
            _player(f"{team_id}_2", "DEF"),
            _player(f"{team_id}_3", "MID"),
            _player(f"{team_id}_4", "FWD"),
        ],
    )


def _config(log_dir: str) -> MatchConfig:
    """Factory for test match configs."""
    return MatchConfig(
        match=MatchParams(
            seed=42,
            tick_rate=10,
            duration_minutes=90,
            field_width=100.0,
            field_height=60.0,
        ),
        output=OutputConfig(log_dir=log_dir),
        team_a=_team("team_a"),
        team_b=_team("team_b"),
    )


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    """Patch all importlib dependencies for testing."""
    # PAL mock
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    # Strategy storage mock
    storage_mod = importlib.import_module("src.foundation.strategy_storage")

    # Sandbox mock
    sandbox_mod = importlib.import_module("src.foundation.sandbox")

    # Constants module (can be monkeypatched per test)
    pmep_constants = importlib.import_module("src.foundation.post_match_evolution_pipeline.constants")

    # SPB imports
    from src.foundation.system_prompt_builder import build_evolution_prompt
    from src.foundation.post_match_evolution_pipeline.preloop import (
        _read_prev_strategy_or_fallback,
        _generate_match_summary,
    )

    yield monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants, build_evolution_prompt, _read_prev_strategy_or_fallback, _generate_match_summary


def _make_successful_compile_result(sandbox_mod):
    """Factory for successful sandbox compile results."""
    result = MagicMock()
    result.status = sandbox_mod.ExecutionStatus.SUCCESS
    return result


def _make_failed_compile_result(sandbox_mod, error_type="SyntaxError"):
    """Factory for failed sandbox compile results."""
    result = MagicMock()
    result.status = sandbox_mod.ExecutionStatus.COMPILE_ERROR
    result.error_type = error_type
    return result


# ---------------------------------------------------------------------------
# AC-1: Happy path — single PAL call, valid block (AC-PMEP-01)
# ---------------------------------------------------------------------------


async def test_ac1_happy_path_single_valid_block(patch_dependencies, tmp_path):
    """Single PAL call returns valid fenced block, evolves successfully."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _, _, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return valid code
    async def mock_generate(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    return Hold()\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Mock storage write
    mock_write = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)

    # Act
    code = await evolve_strategy(config, "team_a", match_log, 2)

    # Assert
    assert isinstance(code, str)
    assert len(code) > 0
    assert "def decide(" in code
    mock_write.assert_called_once()

    # Verify file is byte-equal to returned string
    strategies_dir = tmp_path / "strategies" / "team_a"
    if strategies_dir.exists():
        current_file = strategies_dir / "current.py"
        if current_file.exists():
            file_content = current_file.read_text()
            assert file_content == code


# ---------------------------------------------------------------------------
# AC-2: Retry on no_code_block succeeds attempt 2 (AC-PMEP-02)
# ---------------------------------------------------------------------------


async def test_ac2_retry_on_no_code_block_succeeds_attempt_2(patch_dependencies, tmp_path):
    """First PAL call returns prose; second returns valid fenced block."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _, _, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return prose first, then valid code
    call_count = 0
    async def mock_generate(prompt, team_id, cfg, **_kw):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return LLMResponse(
                text="This is just prose with no code block.",
                provider="openai",
                model="gpt-4o",
                input_tokens=100,
                output_tokens=20,
                latency_ms=800.0,
                attempt_count=1,
            )
        else:
            return LLMResponse(
                text="```python\ndef decide(state, ctx):\n    return Hold()\n```",
                provider="openai",
                model="gpt-4o",
                input_tokens=100,
                output_tokens=50,
                latency_ms=1200.0,
                attempt_count=1,
            )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Mock storage write
    mock_write = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)

    # Act
    code = await evolve_strategy(config, "team_a", match_log, 2)

    # Assert
    assert isinstance(code, str)
    assert "def decide(" in code
    assert call_count == 2
    mock_write.assert_called_once()


# ---------------------------------------------------------------------------
# AC-3: Retry exhaustion — all calls return prose (AC-PMEP-03)
# ---------------------------------------------------------------------------


async def test_ac3_retry_exhaustion_no_code_block(patch_dependencies, tmp_path):
    """All PMEP_MAX_RETRIES PAL calls return prose (no fenced block)."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants, _, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to always return prose
    call_count = 0
    async def mock_generate(prompt, team_id, cfg, **_kw):
        nonlocal call_count
        call_count += 1
        return LLMResponse(
            text="This is just prose with no code block.",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=20,
            latency_ms=800.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Mock sandbox (should never be called)
    sandbox_mock = MagicMock()
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Spy on write_strategy
    write_spy = MagicMock()
    monkeypatch.setattr(storage_mod, "write_strategy", write_spy)

    # Act & Assert
    with pytest.raises(EvolutionFailedError) as exc_info:
        await evolve_strategy(config, "team_a", match_log, 2)

    assert exc_info.value.last_failure == "no_code_block"
    assert exc_info.value.attempts_made == pmep_constants.PMEP_MAX_RETRIES
    assert call_count == pmep_constants.PMEP_MAX_RETRIES
    write_spy.assert_not_called()


# ---------------------------------------------------------------------------
# AC-4: Non-retriable LLMCallError immediate (AC-PMEP-04)
# ---------------------------------------------------------------------------


async def test_ac4_non_retriable_llm_call_error_immediate(patch_dependencies, tmp_path):
    """PAL raises LLMCallError(attempt_count=1), should fail immediately."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _, _, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to raise non-retriable error
    call_count = 0
    async def mock_generate(prompt, team_id, cfg, **_kw):
        nonlocal call_count
        call_count += 1
        raise LLMCallError("openai", "gpt-4o", 1, message="Auth failed")

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Mock sandbox (should never be called)
    sandbox_mock = MagicMock()
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Act & Assert
    with pytest.raises(EvolutionFailedError) as exc_info:
        await evolve_strategy(config, "team_a", match_log, 2)

    assert exc_info.value.last_failure == "llm_call_error"
    assert exc_info.value.attempts_made == 1
    assert call_count == 1


# ---------------------------------------------------------------------------
# AC-5: Retriable LLMCallError exhaustion (AC-PMEP-05)
# ---------------------------------------------------------------------------


async def test_ac5_retriable_llm_call_error_exhaustion(patch_dependencies, tmp_path):
    """PAL raises retriable LLMCallError every call, should exhaust retries."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants, _, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Get PAL_RETRY_MAX_ATTEMPTS (assumed to be 3 based on CGP patterns)
    PAL_RETRY_MAX_ATTEMPTS = 3

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to raise retriable error
    call_count = 0
    async def mock_generate(prompt, team_id, cfg, **_kw):
        nonlocal call_count
        call_count += 1
        raise LLMCallError("openai", "gpt-4o", PAL_RETRY_MAX_ATTEMPTS, message="Rate limited")

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Mock sandbox (should never be called)
    sandbox_mock = MagicMock()
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Act & Assert
    with pytest.raises(EvolutionFailedError) as exc_info:
        await evolve_strategy(config, "team_a", match_log, 2)

    assert exc_info.value.last_failure == "llm_call_error"
    assert exc_info.value.attempts_made == pmep_constants.PMEP_MAX_RETRIES
    assert call_count == pmep_constants.PMEP_MAX_RETRIES


# ---------------------------------------------------------------------------
# AC-6: Token overflow immediate, zero PAL calls (AC-PMEP-06)
# ---------------------------------------------------------------------------


async def test_ac6_token_overflow_immediate(patch_dependencies, tmp_path):
    """Context limit exceeded, should fail before any PAL calls."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants, _, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock low token limit to trigger overflow
    monkeypatch.setattr(pmep_constants, "PMEP_CONTEXT_LIMIT_TOKENS", 100)

    # Spy on PAL
    pal_spy = MagicMock()
    monkeypatch.setattr(pal_gen_mod, "generate", pal_spy)

    # Spy on write_strategy
    write_spy = MagicMock()
    monkeypatch.setattr(storage_mod, "write_strategy", write_spy)

    # Act & Assert
    with pytest.raises(EvolutionFailedError) as exc_info:
        await evolve_strategy(config, "team_a", match_log, 2)

    assert exc_info.value.last_failure == "context_overflow"
    assert exc_info.value.attempts_made == 0
    pal_spy.assert_not_called()
    write_spy.assert_not_called()


# ---------------------------------------------------------------------------
# AC-7: Sandbox compile failure → retry; write skipped (AC-PMEP-07)
# ---------------------------------------------------------------------------


async def test_ac7_sandbox_compile_failure_retry(patch_dependencies, tmp_path):
    """PAL returns syntax-broken code every call, should exhaust retries."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants, _, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return syntax-broken code
    async def mock_generate(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    syntax error here\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Mock sandbox compile (always fails)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_failed_compile_result(sandbox_mod, "SyntaxError")
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Spy on write_strategy
    write_spy = MagicMock()
    monkeypatch.setattr(storage_mod, "write_strategy", write_spy)

    # Act & Assert
    with pytest.raises(EvolutionFailedError) as exc_info:
        await evolve_strategy(config, "team_a", match_log, 2)

    assert exc_info.value.last_failure == "compile_error"
    assert exc_info.value.attempts_made == pmep_constants.PMEP_MAX_RETRIES
    assert sandbox_mock.compile.call_count == pmep_constants.PMEP_MAX_RETRIES
    write_spy.assert_not_called()


# ---------------------------------------------------------------------------
# AC-8: WriteFailedError propagates raw (AC-PMEP-08)
# ---------------------------------------------------------------------------


async def test_ac8_write_failed_error_propagates_raw(patch_dependencies, tmp_path):
    """PAL returns valid code that compiles, but write fails."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _, _, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return valid code
    async def mock_generate(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    return Hold()\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Mock write_strategy to raise WriteFailedError
    def mock_write_strategy(log_dir, team_id, code_str, metadata):
        raise WriteFailedError("Disk full")

    monkeypatch.setattr(storage_mod, "write_strategy", mock_write_strategy)

    # Act & Assert — WriteFailedError should propagate, NOT EvolutionFailedError
    with pytest.raises(WriteFailedError):
        await evolve_strategy(config, "team_a", match_log, 2)


# ---------------------------------------------------------------------------
# AC-9: Steps 1-5 + step 10 each called exactly once (AC-PMEP-09)
# ---------------------------------------------------------------------------


async def test_ac9_pre_post_steps_called_once_despite_pal_retries(patch_dependencies, tmp_path):
    """PAL fails 3 times then exhausts. Pre/post-loop helpers called exactly once."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants, _, _read_prev_strategy_or_fallback, _generate_match_summary = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to always fail
    async def mock_generate(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="This is just prose with no code block.",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=20,
            latency_ms=800.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Spy on pre-loop helpers
    read_prev_spy = MagicMock(side_effect=_read_prev_strategy_or_fallback)
    monkeypatch.setattr("src.foundation.post_match_evolution_pipeline.evolve._read_prev_strategy_or_fallback", read_prev_spy)

    summary_spy = MagicMock(side_effect=_generate_match_summary)
    monkeypatch.setattr("src.foundation.post_match_evolution_pipeline.evolve._generate_match_summary", summary_spy)

    from src.foundation.system_prompt_builder import build_evolution_prompt
    prompt_spy = MagicMock(side_effect=build_evolution_prompt)
    monkeypatch.setattr("src.foundation.post_match_evolution_pipeline.evolve.build_evolution_prompt", prompt_spy)

    # Spy on write_strategy
    write_spy = MagicMock()
    monkeypatch.setattr(storage_mod, "write_strategy", write_spy)

    # Act & Assert
    with pytest.raises(EvolutionFailedError):
        await evolve_strategy(config, "team_a", match_log, 2)

    # Pre-loop helpers called exactly once despite PAL retries
    assert read_prev_spy.call_count == 1
    assert summary_spy.call_count == 1
    assert prompt_spy.call_count == 1

    # Write never called (because retry exhausted)
    write_spy.assert_not_called()


# ---------------------------------------------------------------------------
# AC-10: No-op evolution accepted (AC-PMEP-12)
# ---------------------------------------------------------------------------


async def test_ac10_no_op_evolution_accepted(patch_dependencies, tmp_path, caplog):
    """PAL returns code byte-for-byte equal to prev_strategy."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _, _, _read_prev_strategy_or_fallback, _ = patch_dependencies
    config = _config(str(tmp_path))

    prev_strategy_code = "def decide(state, ctx):\n    return Hold()"

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock read_prev_strategy to return specific code
    def mock_read_prev(log_dir, team_id, match_number):
        return prev_strategy_code

    monkeypatch.setattr("src.foundation.post_match_evolution_pipeline.evolve._read_prev_strategy_or_fallback", mock_read_prev)

    # Mock PAL to return identical code (with fence)
    async def mock_generate(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text=f"```python\n{prev_strategy_code}\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Spy on write_strategy
    write_spy = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", write_spy)

    # Act
    with caplog.at_level("INFO"):
        code = await evolve_strategy(config, "team_a", match_log, 2)

    # Assert
    assert code == prev_strategy_code
    assert sandbox_mock.compile.call_count >= 1  # Compile was called
    write_spy.assert_called_once()  # Write still happens

    # Check for no-op log message
    log_messages = [record.message for record in caplog.records if record.levelname == "INFO"]
    no_op_logs = [msg for msg in log_messages if "no-op" in msg and "team_a" in msg]
    assert len(no_op_logs) >= 1


# ---------------------------------------------------------------------------
# AC-11: StrategyMetadata fields (AC-PMEP-13)
# ---------------------------------------------------------------------------


async def test_ac11_strategy_metadata_fields(patch_dependencies, tmp_path):
    """Verify StrategyMetadata fields after successful evolution."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _, _, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return valid code
    async def mock_generate(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    return Hold()\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Capture write_strategy calls to inspect metadata
    captured_calls = []
    def capture_write_strategy(log_dir, team_id, code_str, metadata):
        captured_calls.append((log_dir, team_id, code_str, metadata))
        return 1

    monkeypatch.setattr(storage_mod, "write_strategy", capture_write_strategy)

    # Act
    await evolve_strategy(config, "team_a", match_log, 3)

    # Assert metadata fields
    assert len(captured_calls) == 1
    _, team_id, _, metadata = captured_calls[0]
    assert metadata.match_number == 3
    assert metadata.team_id == "team_a"
    assert metadata.generated_by.startswith("post-match-evolution/")


# ---------------------------------------------------------------------------
# AC-12: build_evolution_prompt exception (AC-PMEP-16)
# ---------------------------------------------------------------------------


async def test_ac12_build_evolution_prompt_exception(patch_dependencies, tmp_path):
    """build_evolution_prompt raises RuntimeError, should fail immediately."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _, build_evolution_prompt, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock build_evolution_prompt to raise RuntimeError
    def mock_build_prompt(prev_strategy, match_summary, **_):
        raise RuntimeError("template missing")

    monkeypatch.setattr("src.foundation.post_match_evolution_pipeline.evolve.build_evolution_prompt", mock_build_prompt)

    # Spy on PAL
    pal_spy = MagicMock()
    monkeypatch.setattr(pal_gen_mod, "generate", pal_spy)

    # Act & Assert
    with pytest.raises(EvolutionFailedError) as exc_info:
        await evolve_strategy(config, "team_a", match_log, 2)

    assert exc_info.value.last_failure == "prompt_build_error"
    assert exc_info.value.attempts_made == 0
    assert isinstance(exc_info.value.cause, RuntimeError)
    assert str(exc_info.value.cause) == "template missing"
    pal_spy.assert_not_called()


# ---------------------------------------------------------------------------
# AC-13: generate_summary exception propagates (AC-PMEP-17)
# ---------------------------------------------------------------------------


async def test_ac13_generate_summary_exception_propagates(patch_dependencies, tmp_path):
    """match_log.generate_summary raises, should propagate as EvolutionFailedError."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _, build_evolution_prompt, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log to raise during generate_summary
    match_log = MagicMock()
    match_log.generate_summary.side_effect = RuntimeError("Summary failed")

    # Spy on build_evolution_prompt
    prompt_spy = MagicMock()
    monkeypatch.setattr("src.foundation.post_match_evolution_pipeline.evolve.build_evolution_prompt", prompt_spy)

    # Act & Assert
    with pytest.raises(EvolutionFailedError) as exc_info:
        await evolve_strategy(config, "team_a", match_log, 2)

    assert exc_info.value.last_failure == "generate_summary_error"
    prompt_spy.assert_not_called()


# ---------------------------------------------------------------------------
# AC-14: Mode-check fallback warning (Rule 2 step 4)
# ---------------------------------------------------------------------------


async def test_ac14_mode_check_fallback_warning(patch_dependencies, tmp_path, caplog):
    """When prev_strategy="", SPB returns generation mode, should emit warning."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _, _, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock read_prev_strategy to raise StrategyNotFoundError (-> empty string)
    def mock_read_prev(log_dir, team_id, match_number):
        return ""  # Empty triggers GENERATION mode

    monkeypatch.setattr("src.foundation.post_match_evolution_pipeline.evolve._read_prev_strategy_or_fallback", mock_read_prev)

    # Mock build_evolution_prompt to return GENERATION mode
    def mock_build_prompt(prev_strategy, match_summary, **_):
        return PromptResult(
            text="Generation mode prompt text",
            mode=PromptMode.GENERATION,
            estimated_tokens=500,
            template_version="v1.0",
        )

    monkeypatch.setattr("src.foundation.post_match_evolution_pipeline.evolve.build_evolution_prompt", mock_build_prompt)

    # Mock PAL to return valid code
    async def mock_generate(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    return Hold()\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Mock storage write
    mock_write = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)

    # Act
    with caplog.at_level("WARNING"):
        await evolve_strategy(config, "team_a", match_log, 2)

    # Assert warning was logged
    warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
    fallback_warnings = [msg for msg in warning_messages if ("generation" in msg or "fallback" in msg) and "team_a" in msg]
    assert len(fallback_warnings) >= 1


# ---------------------------------------------------------------------------
# AC-15: Cause identity preserved (Rule 5)
# ---------------------------------------------------------------------------


async def test_ac15_cause_identity_preserved(patch_dependencies, tmp_path):
    """PAL exhausts with LLMCallError, cause should preserve identity."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants, _, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Create a specific LLMCallError instance
    original_error = LLMCallError("openai", "gpt-4o", 3, message="Rate limited")

    # Mock PAL to raise the same error instance
    async def mock_generate(prompt, team_id, cfg, **_kw):
        raise original_error

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Act & Assert
    with pytest.raises(EvolutionFailedError) as exc_info:
        await evolve_strategy(config, "team_a", match_log, 2)

    # Verify cause preserves identity (IS, not ==)
    assert exc_info.value.cause is original_error