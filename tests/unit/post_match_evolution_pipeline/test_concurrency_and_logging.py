"""Tests for PMEP Story 004: Concurrency integration + structured logging coverage."""

from __future__ import annotations

import asyncio
import importlib
import logging
import time
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
from src.foundation.strategy_storage import StrategyMetadata, write_strategy
from src.foundation.system_prompt_builder import load_templates

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
        team_id=team_id,
        name=team_id.replace("_", " ").title(),
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


@pytest.fixture
def patch_dependencies(monkeypatch):
    """Patch all importlib dependencies for testing."""
    # PAL mock
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    # Strategy storage mock
    storage_mod = importlib.import_module("src.foundation.strategy_storage")

    # Sandbox mock
    sandbox_mod = importlib.import_module("src.foundation.sandbox")

    # Constants module
    pmep_constants = importlib.import_module("src.foundation.post_match_evolution_pipeline.constants")

    yield monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants


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
# AC-PMEP-14: gather one fails one succeeds (EC-PMEP-04)
# ---------------------------------------------------------------------------


async def test_ac_pmep_14_one_fails_one_succeeds(patch_dependencies, tmp_path):
    """AC-PMEP-14: team_a succeeds, team_b fails with non-retriable error."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL with team-dependent behavior
    async def fake_pal_mixed(prompt, team_id, cfg, **_kw):
        if team_id == "team_a":
            return LLMResponse(
                text="```python\ndef decide(state, ctx):\n    return Hold()\n```",
                provider="openai",
                model="gpt-4o",
                input_tokens=100,
                output_tokens=30,
                latency_ms=800.0,
                attempt_count=1,
            )
        else:  # team_b
            raise LLMCallError(
                provider="openai",
                model="gpt-4o",
                attempt_count=1,  # Non-retriable
                cause=ValueError("authentication failed"),
            )

    monkeypatch.setattr(pal_gen_mod, "generate", fake_pal_mixed)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Use real storage write to create actual files
    # No mocking needed - let it write to tmp_path

    # Act - gather with return_exceptions=True
    results = await asyncio.gather(
        evolve_strategy(config, "team_a", match_log, 2),
        evolve_strategy(config, "team_b", match_log, 2),
        return_exceptions=True,
    )

    # Assert - team_a succeeds, team_b fails
    assert len(results) == 2
    assert isinstance(results[0], str)
    assert "def decide(" in results[0]
    assert isinstance(results[1], EvolutionFailedError)
    assert results[1].last_failure == "llm_call_error"

    # Verify team_a file exists, team_b doesn't
    assert (tmp_path / "strategies" / "team_a" / "current.py").exists()
    assert not (tmp_path / "strategies" / "team_b" / "current.py").exists()


# ---------------------------------------------------------------------------
# AC-2: Concurrent two-team success (no contamination)
# ---------------------------------------------------------------------------


async def test_concurrent_two_team_success(patch_dependencies, tmp_path):
    """PAL returns team-distinct valid code for each team."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return team-discriminated code
    async def team_specific_pal(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text=f"```python\ndef decide(state, ctx):\n    return Hold()  # strategy for {team_id}\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", team_specific_pal)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Use real storage write to create actual files
    # No mocking needed - let it write to tmp_path

    # Act - gather both teams
    results = await asyncio.gather(
        evolve_strategy(config, "team_a", match_log, 2),
        evolve_strategy(config, "team_b", match_log, 2),
    )

    # Assert - both return valid code strings
    code_a, code_b = results
    assert isinstance(code_a, str)
    assert isinstance(code_b, str)
    assert "def decide(" in code_a
    assert "def decide(" in code_b
    assert "team_a" in code_a
    assert "team_b" in code_b
    assert code_a != code_b

    # Verify both files exist with different contents
    file_a = tmp_path / "strategies" / "team_a" / "current.py"
    file_b = tmp_path / "strategies" / "team_b" / "current.py"

    assert file_a.exists()
    assert file_b.exists()

    content_a = file_a.read_text()
    content_b = file_b.read_text()
    assert "team_a" in content_a
    assert "team_b" in content_b
    assert content_a != content_b


# ---------------------------------------------------------------------------
# AC-3: Concurrency overlaps (wall-clock check)
# ---------------------------------------------------------------------------


async def test_concurrency_overlaps_wall_clock(patch_dependencies, tmp_path):
    """PAL with asyncio.sleep should complete gather < 0.18s."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL with sleep to simulate network delay
    async def slow_pal(prompt, team_id, cfg, **_kw):
        await asyncio.sleep(0.1)  # 100ms delay
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    return Hold()\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=30,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", slow_pal)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Mock storage write
    mock_write = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)

    # Act - measure wall-clock time
    t0 = time.perf_counter()
    await asyncio.gather(
        evolve_strategy(config, "team_a", match_log, 2),
        evolve_strategy(config, "team_b", match_log, 2),
    )
    elapsed = time.perf_counter() - t0

    # Assert - concurrent should be ~0.1s, sequential would be ~0.2s
    assert elapsed < 0.18, f"Expected < 0.18s for concurrent calls, got {elapsed:.3f}s"


# ---------------------------------------------------------------------------
# AC-PMEP-15: Both teams fail under gather
# ---------------------------------------------------------------------------


async def test_ac_pmep_15_both_teams_fail(patch_dependencies, tmp_path):
    """Both teams fail with non-retriable errors."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to always fail
    async def fail_pal(prompt, team_id, cfg, **_kw):
        raise LLMCallError(
            provider="openai",
            model="gpt-4o",
            attempt_count=1,  # Non-retriable
            cause=ValueError("auth failed"),
        )

    monkeypatch.setattr(pal_gen_mod, "generate", fail_pal)

    # Mock sandbox (should never be called)
    sandbox_mock = MagicMock()
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Mock storage write
    mock_write = MagicMock()
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)

    # Act - gather with return_exceptions=True
    results = await asyncio.gather(
        evolve_strategy(config, "team_a", match_log, 2),
        evolve_strategy(config, "team_b", match_log, 2),
        return_exceptions=True,
    )

    # Assert - both return EvolutionFailedError instances
    assert len(results) == 2
    assert isinstance(results[0], EvolutionFailedError)
    assert isinstance(results[1], EvolutionFailedError)
    assert results[0].last_failure == "llm_call_error"
    assert results[1].last_failure == "llm_call_error"

    # Neither file should exist
    assert not (tmp_path / "strategies" / "team_a" / "current.py").exists()
    assert not (tmp_path / "strategies" / "team_b" / "current.py").exists()
    mock_write.assert_not_called()


# ---------------------------------------------------------------------------
# AC-5: No cross-team contamination
# ---------------------------------------------------------------------------


async def test_no_cross_team_contamination(patch_dependencies, tmp_path):
    """Verify team-specific outputs persist correctly to separate files."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return team-discriminated code
    async def discriminating_pal(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text=f"```python\ndef decide(state, ctx):\n    # unique code for {team_id}\n    return Hold()\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", discriminating_pal)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Use real storage write to create actual files
    # No mocking needed - let it write to tmp_path

    # Act - gather both teams
    await asyncio.gather(
        evolve_strategy(config, "team_a", match_log, 2),
        evolve_strategy(config, "team_b", match_log, 2),
    )

    # Assert - read each file and verify content matches team
    file_a = tmp_path / "strategies" / "team_a" / "current.py"
    file_b = tmp_path / "strategies" / "team_b" / "current.py"

    assert file_a.exists()
    assert file_b.exists()

    content_a = file_a.read_text()
    content_b = file_b.read_text()

    # Each file should contain its team's unique marker
    assert "unique code for team_a" in content_a
    assert "unique code for team_b" in content_b
    assert content_a != content_b


# ---------------------------------------------------------------------------
# AC-6: Logging — INFO at start (Rule 11)
# ---------------------------------------------------------------------------


async def test_logging_info_at_start(caplog, patch_dependencies, tmp_path):
    """Verify INFO log with team_id and match_number at start."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return valid code
    async def success_pal(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    return Hold()\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=30,
            latency_ms=800.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", success_pal)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Mock storage write
    mock_write = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)

    # Act
    with caplog.at_level(logging.INFO):
        await evolve_strategy(config, "team_a", match_log, 3)

    # Assert - find INFO record with team_id and match_number
    info_records = [
        r for r in caplog.records
        if r.levelno == logging.INFO
        and r.name.startswith("src.foundation.post_match_evolution_pipeline")
        and "team_a" in r.getMessage()
        and "3" in r.getMessage()
    ]

    assert len(info_records) >= 1, f"Expected INFO log with team_a and match_number. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-7: Logging — WARNING for empty response
# ---------------------------------------------------------------------------


async def test_logging_warning_empty_response(caplog, patch_dependencies, tmp_path):
    """Verify WARNING log for empty PAL response."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to always return empty response
    async def empty_pal(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=0,
            latency_ms=500.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", empty_pal)

    # Mock sandbox (should never be called)
    sandbox_mock = MagicMock()
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Act
    with caplog.at_level(logging.WARNING):
        with pytest.raises(EvolutionFailedError):
            await evolve_strategy(config, "team_a", match_log, 2)

    # Assert - find WARNING record with empty_response and team_id
    empty_response_records = [
        r for r in caplog.records
        if r.levelno == logging.WARNING
        and r.name.startswith("src.foundation.post_match_evolution_pipeline")
        and "empty_response" in r.getMessage()
        and "team_a" in r.getMessage()
    ]

    assert len(empty_response_records) >= 1, f"Expected WARNING log with 'empty_response'. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-7: Logging — WARNING for no_code_block
# ---------------------------------------------------------------------------


async def test_logging_warning_no_code_block(caplog, patch_dependencies, tmp_path):
    """Verify WARNING log for no_code_block failure."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return prose (no code block)
    async def prose_pal(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="This is just prose with no code blocks.",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=20,
            latency_ms=800.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", prose_pal)

    # Mock sandbox (should never be called)
    sandbox_mock = MagicMock()
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Act
    with caplog.at_level(logging.WARNING):
        with pytest.raises(EvolutionFailedError):
            await evolve_strategy(config, "team_a", match_log, 2)

    # Assert - find WARNING record with no_code_block and team_id
    no_code_block_records = [
        r for r in caplog.records
        if r.levelno == logging.WARNING
        and r.name.startswith("src.foundation.post_match_evolution_pipeline")
        and "no_code_block" in r.getMessage()
        and "team_a" in r.getMessage()
    ]

    assert len(no_code_block_records) >= 1, f"Expected WARNING log with 'no_code_block'. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-7: Logging — WARNING for no_decide_signature
# ---------------------------------------------------------------------------


async def test_logging_warning_no_decide_signature(caplog, patch_dependencies, tmp_path):
    """Verify WARNING log for no_decide_signature failure."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return wrong function signature
    async def wrong_sig_pal(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="```python\ndef strategy(state, ctx):\n    return Hold()\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=25,
            latency_ms=900.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", wrong_sig_pal)

    # Mock sandbox (should never be called)
    sandbox_mock = MagicMock()
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Act
    with caplog.at_level(logging.WARNING):
        with pytest.raises(EvolutionFailedError):
            await evolve_strategy(config, "team_a", match_log, 2)

    # Assert - find WARNING record with no_decide_signature and team_id
    no_decide_records = [
        r for r in caplog.records
        if r.levelno == logging.WARNING
        and r.name.startswith("src.foundation.post_match_evolution_pipeline")
        and "no_decide_signature" in r.getMessage()
        and "team_a" in r.getMessage()
    ]

    assert len(no_decide_records) >= 1, f"Expected WARNING log with 'no_decide_signature'. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-7: Logging — WARNING for compile_error
# ---------------------------------------------------------------------------


async def test_logging_warning_compile_error(caplog, patch_dependencies, tmp_path):
    """Verify WARNING log for compile failure."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, pmep_constants = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return syntax error code
    async def syntax_error_pal(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    syntax !! error\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=30,
            latency_ms=1100.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", syntax_error_pal)

    # Mock sandbox compile (always fails)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_failed_compile_result(sandbox_mod, "SyntaxError")
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Act
    with caplog.at_level(logging.WARNING):
        with pytest.raises(EvolutionFailedError):
            await evolve_strategy(config, "team_a", match_log, 2)

    # Assert - find WARNING record with compile_error and team_id
    compile_error_records = [
        r for r in caplog.records
        if r.levelno == logging.WARNING
        and r.name.startswith("src.foundation.post_match_evolution_pipeline")
        and "compile_error" in r.getMessage()
        and "team_a" in r.getMessage()
    ]

    assert len(compile_error_records) >= 1, f"Expected WARNING log with 'compile_error'. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-8: Logging — WARNING for llm_call_error
# ---------------------------------------------------------------------------


async def test_logging_warning_llm_call_error(caplog, patch_dependencies, tmp_path):
    """Verify WARNING log for non-retriable LLMCallError."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to raise non-retriable LLMCallError
    async def error_pal(prompt, team_id, cfg, **_kw):
        raise LLMCallError(
            provider="openai",
            model="gpt-4o",
            attempt_count=1,  # Non-retriable
            cause=ValueError("auth failed"),
        )

    monkeypatch.setattr(pal_gen_mod, "generate", error_pal)

    # Mock sandbox (should never be called)
    sandbox_mock = MagicMock()
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Act
    with caplog.at_level(logging.WARNING):
        with pytest.raises(EvolutionFailedError):
            await evolve_strategy(config, "team_a", match_log, 2)

    # Assert - find WARNING+ record with llm_call_error and team_id
    llm_error_records = [
        r for r in caplog.records
        if r.levelno >= logging.WARNING
        and r.name.startswith("src.foundation.post_match_evolution_pipeline")
        and "llm_call_error" in r.getMessage()
        and "team_a" in r.getMessage()
    ]

    assert len(llm_error_records) >= 1, f"Expected WARNING+ log with 'llm_call_error'. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-9: Logging — INFO for evolved strategy written
# ---------------------------------------------------------------------------


async def test_logging_info_success(caplog, patch_dependencies, tmp_path):
    """Verify INFO log after successful strategy write."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return valid code
    async def success_pal(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    return Hold()\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=30,
            latency_ms=800.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", success_pal)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Mock storage write
    mock_write = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)

    # Act
    with caplog.at_level(logging.INFO):
        await evolve_strategy(config, "team_a", match_log, 3)

    # Assert - find INFO record with success and team_id and match_number
    success_records = [
        r for r in caplog.records
        if r.levelno == logging.INFO
        and r.name.startswith("src.foundation.post_match_evolution_pipeline")
        and "success" in r.getMessage()
        and "team_a" in r.getMessage()
        and "3" in r.getMessage()
    ]

    assert len(success_records) >= 1, f"Expected INFO log with 'success' and team_a. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-10: Logging — INFO for no-op detection
# ---------------------------------------------------------------------------


async def test_logging_info_no_op_detection(caplog, patch_dependencies, tmp_path):
    """Verify INFO log when PAL returns code identical to prev_strategy."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _ = patch_dependencies
    config = _config(str(tmp_path))

    prev_code = "def decide(state, ctx):\n    return Hold()"

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock _read_prev_strategy_or_fallback to return specific code
    def mock_read_prev(log_dir, team_id, match_number):
        return prev_code

    monkeypatch.setattr("src.foundation.post_match_evolution_pipeline.evolve._read_prev_strategy_or_fallback", mock_read_prev)

    # Mock PAL to return identical code
    async def identical_pal(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text=f"```python\n{prev_code}\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=20,
            latency_ms=800.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", identical_pal)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Mock storage write
    mock_write = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)

    # Act
    with caplog.at_level(logging.INFO):
        result = await evolve_strategy(config, "team_a", match_log, 2)

    # Assert - find INFO record with no-op and team_id
    no_op_records = [
        r for r in caplog.records
        if r.levelno == logging.INFO
        and "no-op" in r.getMessage()
        and "team_a" in r.getMessage()
        and r.name.startswith("src.foundation.post_match_evolution_pipeline")
    ]

    assert len(no_op_records) >= 1, f"Expected INFO log with 'no-op'. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-11: Logger name discoverable
# ---------------------------------------------------------------------------


async def test_logger_name_prefix(caplog, patch_dependencies, tmp_path):
    """Verify all PMEP log records use correct namespace prefix."""
    monkeypatch, pal_gen_mod, storage_mod, sandbox_mod, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock match_log
    match_log = MagicMock()
    match_log.generate_summary.return_value = "summary text"

    # Mock PAL to return valid code
    async def success_pal(prompt, team_id, cfg, **_kw):
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    return Hold()\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=30,
            latency_ms=800.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", success_pal)

    # Mock sandbox compile (success)
    sandbox_mock = MagicMock()
    sandbox_mock.compile.return_value = _make_successful_compile_result(sandbox_mod)
    monkeypatch.setattr(sandbox_mod, "Sandbox", lambda: sandbox_mock)

    # Mock storage write
    mock_write = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)

    # Act
    with caplog.at_level(logging.DEBUG):
        await evolve_strategy(config, "team_a", match_log, 2)

    # Assert - filter to PMEP-specific records and verify prefix
    pmep_records = [
        rec for rec in caplog.records
        if rec.name.startswith("src.foundation.post_match_evolution_pipeline")
    ]

    assert len(pmep_records) > 0, "Expected at least one PMEP log record"

    for rec in pmep_records:
        assert rec.name.startswith("src.foundation.post_match_evolution_pipeline"), f"Record name '{rec.name}' doesn't start with PMEP namespace"