"""Tests for CGP Story 005: Concurrency integration + structured logging coverage."""

from __future__ import annotations

import asyncio
import importlib
import logging
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.foundation.code_generation_pipeline import generate_strategy
from src.foundation.code_generation_pipeline.types import GenerationFailedError
from src.foundation.config_models import (
    MatchConfig,
    MatchParams,
    OutputConfig,
    PlayerConfig,
    TeamConfig,
)
from src.foundation.provider_abstraction.models import LLMCallError, LLMResponse
from src.foundation.system_prompt_builder import load_templates

# Use pytest-asyncio for async tests
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module", autouse=True)
def _load_templates_once():
    """SPB requires load_templates() at process start before build_generation_prompt works."""
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


@pytest.fixture
def patch_pal_success(monkeypatch):
    """Mock PAL to return successful code generation."""
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    async def fake_generate(prompt, team_id, cfg, **_kwargs):
        return LLMResponse(
            text=f"```python\ndef decide(state, ctx):\n    return Hold()  # generated for {team_id}\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", fake_generate)
    return fake_generate


@pytest.fixture
def patch_storage(monkeypatch):
    """Mock strategy storage to avoid disk writes in most tests."""
    storage_mod = importlib.import_module("src.foundation.strategy_storage")
    mock_write = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)
    return mock_write


# ---------------------------------------------------------------------------
# AC-1: AC-CGP-12 — gather two teams
# ---------------------------------------------------------------------------


async def test_ac1_concurrent_gather_two_teams(patch_pal_success, tmp_path):
    """AC-CGP-12: asyncio.gather returns two different code strings."""
    config = _config(str(tmp_path))

    # Act - gather two team generations
    results = await asyncio.gather(
        generate_strategy(config, "team_a"),
        generate_strategy(config, "team_b"),
    )

    # Assert - both return valid code strings
    code_a, code_b = results
    assert isinstance(code_a, str)
    assert isinstance(code_b, str)
    assert "def decide(" in code_a
    assert "def decide(" in code_b
    assert "team_a" in code_a
    assert "team_b" in code_b


# ---------------------------------------------------------------------------
# AC-2: No cross-team contamination
# ---------------------------------------------------------------------------


async def test_ac2_no_cross_team_contamination(tmp_path, monkeypatch):
    """Verify team-specific outputs and separate file persistence."""
    config = _config(str(tmp_path))

    # Mock PAL to return team-discriminated content
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    async def discriminating_generate(prompt, team_id, cfg, **_kwargs):
        return LLMResponse(
            text=f"```python\ndef decide(state, ctx):\n    return Hold()  # strategy for {team_id}\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", discriminating_generate)

    # Act - gather both teams
    code_a, code_b = await asyncio.gather(
        generate_strategy(config, "team_a"),
        generate_strategy(config, "team_b"),
    )

    # Assert - content is team-discriminated
    assert "team_a" in code_a
    assert "team_b" in code_b
    assert code_a != code_b

    # Verify separate files on disk
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
# AC-3: Gather actually overlaps (wall-clock check)
# ---------------------------------------------------------------------------


async def test_ac3_gather_overlaps_wall_clock(patch_storage, tmp_path, monkeypatch):
    """Verify gather actually runs concurrently via wall-clock timing."""
    config = _config(str(tmp_path))

    # Mock PAL with asyncio.sleep to simulate LLM latency
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    async def slow_generate(prompt, team_id, cfg, **_kwargs):
        await asyncio.sleep(0.1)  # Simulate 100ms LLM call
        return LLMResponse(
            text=f"```python\ndef decide(state, ctx):\n    return Hold()\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=30,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", slow_generate)

    # Act - measure wall-clock time
    t0 = time.perf_counter()
    await asyncio.gather(
        generate_strategy(config, "team_a"),
        generate_strategy(config, "team_b"),
    )
    elapsed = time.perf_counter() - t0

    # Assert - concurrent should be ~0.1s, sequential would be ~0.2s
    assert elapsed < 0.18, f"Expected < 0.18s for concurrent calls, got {elapsed:.3f}s"


# ---------------------------------------------------------------------------
# AC-4: EC-CGP-04 — one succeeds, one fails
# ---------------------------------------------------------------------------


async def test_ac4_one_succeeds_one_fails(tmp_path, monkeypatch):
    """EC-CGP-04: gather with return_exceptions=True handles mixed results."""
    config = _config(str(tmp_path))

    # Mock PAL with team-dependent behavior
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    async def mixed_generate(prompt, team_id, cfg, **_kwargs):
        if team_id == "team_a":
            return LLMResponse(
                text="```python\ndef decide(state, ctx):\n    return Hold()\n```",
                provider="openai",
                model="gpt-4o",
                input_tokens=100,
                output_tokens=30,
                latency_ms=1000.0,
                attempt_count=1,
            )
        else:  # team_b
            raise LLMCallError(
                provider="openai",
                model="gpt-4o",
                attempt_count=1,  # Non-retriable
                cause=ValueError("authentication failed"),
            )

    monkeypatch.setattr(pal_gen_mod, "generate", mixed_generate)

    # Act - gather with return_exceptions=True
    results = await asyncio.gather(
        generate_strategy(config, "team_a"),
        generate_strategy(config, "team_b"),
        return_exceptions=True,
    )

    # Assert - mixed results
    assert len(results) == 2
    assert isinstance(results[0], str)  # team_a succeeded
    assert "def decide(" in results[0]
    assert isinstance(results[1], GenerationFailedError)  # team_b failed
    assert results[1].last_failure == "llm_call_error"

    # Verify only team_a file exists
    assert (tmp_path / "strategies" / "team_a" / "current.py").exists()
    assert not (tmp_path / "strategies" / "team_b" / "current.py").exists()


# ---------------------------------------------------------------------------
# AC-5: Logging — generation started (INFO)
# ---------------------------------------------------------------------------


async def test_ac5_logging_info_at_start(caplog, patch_pal_success, patch_storage, tmp_path):
    """Verify INFO log with team_id when generation starts."""
    config = _config(str(tmp_path))

    with caplog.at_level(logging.INFO):
        await generate_strategy(config, "team_a")

    # Find CGP INFO record containing team_id
    cgp_info_records = [
        rec for rec in caplog.records
        if rec.levelno == logging.INFO
        and rec.name.startswith("src.foundation.code_generation_pipeline")
        and "team_a" in rec.getMessage()
    ]

    assert len(cgp_info_records) > 0, f"Expected INFO log with team_a. Records: {[(r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-6: Logging — empty response (WARNING)
# ---------------------------------------------------------------------------


async def test_ac6_logging_empty_response_warning(caplog, patch_storage, tmp_path, monkeypatch):
    """Verify WARNING log for empty PAL response."""
    config = _config(str(tmp_path))

    # Mock PAL to return empty response first, then success
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    responses = [
        LLMResponse(text="", provider="openai", model="gpt-4o", input_tokens=100, output_tokens=0, latency_ms=500.0, attempt_count=1),
        LLMResponse(text="```python\ndef decide(s,c):\n    return Hold()\n```", provider="openai", model="gpt-4o", input_tokens=100, output_tokens=30, latency_ms=1000.0, attempt_count=1),
    ]

    mock_generate = AsyncMock(side_effect=responses)
    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    with caplog.at_level(logging.WARNING):
        await generate_strategy(config, "team_a")

    # Find WARNING record for empty response
    empty_warning_records = [
        rec for rec in caplog.records
        if rec.levelno == logging.WARNING
        and rec.name.startswith("src.foundation.code_generation_pipeline")
        and "team_a" in rec.getMessage()
        and "empty" in rec.getMessage().lower()
    ]

    assert len(empty_warning_records) > 0, f"Expected WARNING log for empty response. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-7: Logging — no_code_block (WARNING)
# ---------------------------------------------------------------------------


async def test_ac7_logging_no_code_block_warning(caplog, tmp_path, monkeypatch):
    """Verify WARNING log for no_code_block failure."""
    config = _config(str(tmp_path))

    # Mock PAL to return prose (no code blocks)
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    async def prose_generate(prompt, team_id, cfg, **_kwargs):
        return LLMResponse(
            text="This is just prose with no code blocks at all.",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=20,
            latency_ms=800.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", prose_generate)

    with caplog.at_level(logging.WARNING):
        with pytest.raises(GenerationFailedError):
            await generate_strategy(config, "team_a")

    # Find WARNING record containing "no_code_block"
    no_code_block_records = [
        rec for rec in caplog.records
        if rec.levelno == logging.WARNING
        and rec.name.startswith("src.foundation.code_generation_pipeline")
        and "no_code_block" in rec.getMessage()
    ]

    assert len(no_code_block_records) > 0, f"Expected WARNING log with 'no_code_block'. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-8: Logging — no_decide_signature (WARNING)
# ---------------------------------------------------------------------------


async def test_ac8_logging_no_decide_signature_warning(caplog, tmp_path, monkeypatch):
    """Verify WARNING log for no_decide_signature failure."""
    config = _config(str(tmp_path))

    # Mock PAL to return wrong function signature
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    async def wrong_sig_generate(prompt, team_id, cfg, **_kwargs):
        return LLMResponse(
            text="```python\ndef strategy(params):\n    return 42\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=25,
            latency_ms=900.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", wrong_sig_generate)

    with caplog.at_level(logging.WARNING):
        with pytest.raises(GenerationFailedError):
            await generate_strategy(config, "team_a")

    # Find WARNING record containing "no_decide_signature"
    no_decide_records = [
        rec for rec in caplog.records
        if rec.levelno == logging.WARNING
        and rec.name.startswith("src.foundation.code_generation_pipeline")
        and "no_decide_signature" in rec.getMessage()
    ]

    assert len(no_decide_records) > 0, f"Expected WARNING log with 'no_decide_signature'. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-9: Logging — compile_error (WARNING)
# ---------------------------------------------------------------------------


async def test_ac9_logging_compile_error_warning(caplog, tmp_path, monkeypatch):
    """Verify WARNING log for compile failure."""
    config = _config(str(tmp_path))

    # Mock PAL to return syntax error
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    async def syntax_error_generate(prompt, team_id, cfg, **_kwargs):
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    syntax !! error here\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=30,
            latency_ms=1100.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", syntax_error_generate)

    with caplog.at_level(logging.WARNING):
        with pytest.raises(GenerationFailedError):
            await generate_strategy(config, "team_a")

    # Find WARNING record containing "compile" substring
    compile_error_records = [
        rec for rec in caplog.records
        if rec.levelno == logging.WARNING
        and rec.name.startswith("src.foundation.code_generation_pipeline")
        and "compile" in rec.getMessage().lower()
    ]

    assert len(compile_error_records) > 0, f"Expected WARNING log with 'compile'. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-10: Logging — non-retriable LLMCallError (WARNING+)
# ---------------------------------------------------------------------------


async def test_ac10_logging_llm_call_error_warning(caplog, tmp_path, monkeypatch):
    """Verify WARNING+ log for non-retriable LLMCallError before raising."""
    config = _config(str(tmp_path))

    # Mock PAL to raise non-retriable LLMCallError
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    async def error_generate(prompt, team_id, cfg, **_kwargs):
        raise LLMCallError(
            provider="openai",
            model="gpt-4o",
            attempt_count=1,  # Non-retriable
            cause=ValueError("auth failed"),
        )

    monkeypatch.setattr(pal_gen_mod, "generate", error_generate)

    with caplog.at_level(logging.WARNING):
        with pytest.raises(GenerationFailedError):
            await generate_strategy(config, "team_a")

    # Find WARNING+ record with both "llm_call_error" and team_id
    llm_error_records = [
        rec for rec in caplog.records
        if rec.levelno >= logging.WARNING
        and rec.name.startswith("src.foundation.code_generation_pipeline")
        and "llm_call_error" in rec.getMessage()
        and "team_a" in rec.getMessage()
    ]

    assert len(llm_error_records) > 0, f"Expected WARNING+ log with 'llm_call_error' and team_a. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-11: Logging — strategy written (INFO)
# ---------------------------------------------------------------------------


async def test_ac11_logging_success_info(caplog, patch_pal_success, patch_storage, tmp_path):
    """Verify INFO log after successful strategy write."""
    config = _config(str(tmp_path))

    with caplog.at_level(logging.INFO):
        await generate_strategy(config, "team_a")

    # Find INFO record with success/written and team_id
    success_records = [
        rec for rec in caplog.records
        if rec.levelno == logging.INFO
        and rec.name.startswith("src.foundation.code_generation_pipeline")
        and ("success" in rec.getMessage() or "written" in rec.getMessage())
        and "team_a" in rec.getMessage()
    ]

    assert len(success_records) > 0, f"Expected INFO log with 'success' and team_a. Records: {[(r.levelno, r.name, r.getMessage()) for r in caplog.records]}"


# ---------------------------------------------------------------------------
# AC-12: Logger name discoverable
# ---------------------------------------------------------------------------


async def test_ac12_logger_name_prefix(caplog, patch_pal_success, patch_storage, tmp_path):
    """Verify all CGP log records have correct namespace prefix."""
    config = _config(str(tmp_path))

    with caplog.at_level(logging.DEBUG):
        await generate_strategy(config, "team_a")

    # Filter to CGP-specific records and verify prefix
    cgp_records = [
        rec for rec in caplog.records
        if rec.name.startswith("src.foundation.code_generation_pipeline")
    ]

    # All CGP records should have the proper namespace
    assert len(cgp_records) > 0, "Expected at least one CGP log record"

    for rec in cgp_records:
        assert rec.name.startswith("src.foundation.code_generation_pipeline"), f"Record name '{rec.name}' doesn't start with CGP namespace"


# ---------------------------------------------------------------------------
# AC-13: No module-level state contamination
# ---------------------------------------------------------------------------


async def test_ac13_no_module_state_contamination(patch_storage, tmp_path, monkeypatch):
    """Verify gather calls don't contaminate each other's state."""
    config = _config(str(tmp_path))

    # Mock PAL to return team-discriminated outputs
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    async def team_specific_generate(prompt, team_id, cfg, **_kwargs):
        return LLMResponse(
            text=f"```python\ndef decide(state, ctx):\n    return Hold()  # {team_id} specific\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", team_specific_generate)

    # Act - run gather twice to test state isolation
    first_run = await asyncio.gather(
        generate_strategy(config, "team_a"),
        generate_strategy(config, "team_b"),
    )

    second_run = await asyncio.gather(
        generate_strategy(config, "team_a"),
        generate_strategy(config, "team_b"),
    )

    # Assert - both runs produce the same discriminated outputs
    assert first_run[0] == second_run[0]  # team_a consistent
    assert first_run[1] == second_run[1]  # team_b consistent
    assert "team_a specific" in first_run[0]
    assert "team_b specific" in first_run[1]
    assert first_run[0] != first_run[1]  # Still discriminated