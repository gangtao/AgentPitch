"""Tests for CGP Story 004: generate_strategy coroutine implementation."""

from __future__ import annotations

import importlib
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.foundation.code_generation_pipeline import generate_strategy
from src.foundation.code_generation_pipeline.types import (
    GenerationFailedError,
    PromptContextOverflowError,
)
from src.foundation.config_models import (
    MatchConfig,
    MatchParams,
    OutputConfig,
    PlayerConfig,
    TeamConfig,
)
from src.foundation.provider_abstraction.models import LLMCallError, LLMResponse
from src.foundation.system_prompt_builder import load_templates
from src.foundation.system_prompt_builder.types import PromptMode, PromptResult

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


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    """Patch all importlib dependencies for testing."""
    # PAL mock
    pal_gen_mod = importlib.import_module("src.foundation.provider_abstraction.generate")

    # Strategy storage mock
    storage_mod = importlib.import_module("src.foundation.strategy_storage")

    # Constants module (can be monkeypatched per test)
    cgp_constants = importlib.import_module("src.foundation.code_generation_pipeline.constants")

    # SPB mock
    from src.foundation.system_prompt_builder import build_generation_prompt

    yield monkeypatch, pal_gen_mod, storage_mod, cgp_constants, build_generation_prompt


# ---------------------------------------------------------------------------
# AC-1: Happy path — single PAL call, valid block (AC-CGP-01)
# ---------------------------------------------------------------------------


async def test_ac1_happy_path_single_valid_block(patch_dependencies, tmp_path):
    """Single PAL call returns valid fenced block, generates successfully."""
    monkeypatch, pal_gen_mod, storage_mod, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock PAL to return valid code
    async def mock_generate(prompt, team_id, cfg, **_kwargs):
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

    # Mock storage write
    mock_write = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)

    # Act
    code = await generate_strategy(config, "team_a")

    # Assert
    assert isinstance(code, str)
    assert len(code) > 0
    assert "def decide(" in code
    mock_write.assert_called_once()


# ---------------------------------------------------------------------------
# AC-2: Byte-equal write — file content matches return (AC-CGP-02)
# ---------------------------------------------------------------------------


async def test_ac2_byte_equal_persistence(patch_dependencies, tmp_path):
    """Returned string is byte-equal to persisted file content."""
    monkeypatch, pal_gen_mod, storage_mod, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    test_code = "def decide(state, ctx):\n    return Hold()"

    # Mock PAL
    async def mock_generate(prompt, team_id, cfg, **_kwargs):
        return LLMResponse(
            text=f"```python\n{test_code}\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Use real strategy storage (not mocked) to verify file write
    code = await generate_strategy(config, "team_a")

    # Read back the file
    strategy_file = tmp_path / "strategies" / "team_a" / "current.py"
    file_content = strategy_file.read_text()

    # Strip the header to compare just the code part
    lines = file_content.split('\n')
    code_start = None
    for i, line in enumerate(lines):
        if line.startswith('#') or line.strip() == '':
            continue
        code_start = i
        break

    if code_start is not None:
        file_code = '\n'.join(lines[code_start:]).rstrip()
        assert code == file_code


# ---------------------------------------------------------------------------
# AC-3: Retry succeeds on attempt 2 (AC-CGP-03)
# ---------------------------------------------------------------------------


async def test_ac3_retry_succeeds_attempt_2(patch_dependencies, tmp_path):
    """First PAL call returns empty, second succeeds."""
    monkeypatch, pal_gen_mod, storage_mod, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    responses = [
        LLMResponse(text="", provider="openai", model="gpt-4o", input_tokens=100, output_tokens=0, latency_ms=500.0, attempt_count=1),
        LLMResponse(text="```python\ndef decide(s,c):\n    return Hold()\n```", provider="openai", model="gpt-4o", input_tokens=100, output_tokens=30, latency_ms=1000.0, attempt_count=1),
    ]

    mock_generate = AsyncMock(side_effect=responses)
    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    mock_write = MagicMock(return_value=1)
    monkeypatch.setattr(storage_mod, "write_strategy", mock_write)

    code = await generate_strategy(config, "team_a")

    assert "def decide(" in code
    assert mock_generate.call_count == 2


# ---------------------------------------------------------------------------
# AC-4: no_code_block exhaustion (AC-CGP-04)
# ---------------------------------------------------------------------------


async def test_ac4_no_code_block_exhaustion(patch_dependencies, tmp_path):
    """Every PAL call returns prose, exhausts retries."""
    monkeypatch, pal_gen_mod, storage_mod, cgp_constants, _ = patch_dependencies
    config = _config(str(tmp_path))

    async def mock_generate(prompt, team_id, cfg, **_kwargs):
        return LLMResponse(
            text="just prose, no code blocks here",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=20,
            latency_ms=800.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    with pytest.raises(GenerationFailedError) as exc_info:
        await generate_strategy(config, "team_a")

    err = exc_info.value
    assert err.last_failure == "no_code_block"
    assert err.attempts_made == cgp_constants.CGP_MAX_RETRIES
    assert err.team_id == "team_a"


# ---------------------------------------------------------------------------
# AC-5: no_decide_signature exhaustion (AC-CGP-05)
# ---------------------------------------------------------------------------


async def test_ac5_no_decide_signature_exhaustion(patch_dependencies, tmp_path):
    """Every PAL call returns wrong function signature."""
    monkeypatch, pal_gen_mod, storage_mod, cgp_constants, _ = patch_dependencies
    config = _config(str(tmp_path))

    async def mock_generate(prompt, team_id, cfg, **_kwargs):
        return LLMResponse(
            text="```python\ndef strategy(params):\n    return 42\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=25,
            latency_ms=900.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    with pytest.raises(GenerationFailedError) as exc_info:
        await generate_strategy(config, "team_a")

    err = exc_info.value
    assert err.last_failure == "no_decide_signature"
    assert err.attempts_made == cgp_constants.CGP_MAX_RETRIES


# ---------------------------------------------------------------------------
# AC-6: compile_error exhaustion (AC-CGP-06)
# ---------------------------------------------------------------------------


async def test_ac6_compile_error_exhaustion(patch_dependencies, tmp_path):
    """Every PAL call returns syntax errors."""
    monkeypatch, pal_gen_mod, storage_mod, cgp_constants, _ = patch_dependencies
    config = _config(str(tmp_path))

    async def mock_generate(prompt, team_id, cfg, **_kwargs):
        return LLMResponse(
            text="```python\ndef decide(state, ctx):\n    syntax !! error here\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=30,
            latency_ms=1100.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    with pytest.raises(GenerationFailedError) as exc_info:
        await generate_strategy(config, "team_a")

    err = exc_info.value
    assert err.last_failure == "compile_error"
    assert err.attempts_made == cgp_constants.CGP_MAX_RETRIES


# ---------------------------------------------------------------------------
# AC-7: non-retriable LLMCallError immediate (AC-CGP-07)
# ---------------------------------------------------------------------------


async def test_ac7_non_retriable_llm_error_immediate(patch_dependencies, tmp_path):
    """First PAL call raises non-retriable LLMCallError."""
    monkeypatch, pal_gen_mod, storage_mod, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock LLMCallError with attempt_count=1 (non-retriable)
    async def mock_generate(prompt, team_id, cfg, **_kwargs):
        raise LLMCallError(
            provider="openai",
            model="gpt-4o",
            attempt_count=1,
            cause=ValueError("authentication failed"),
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    with pytest.raises(GenerationFailedError) as exc_info:
        await generate_strategy(config, "team_a")

    err = exc_info.value
    assert err.last_failure == "llm_call_error"
    assert err.attempts_made == 1  # Immediate failure


# ---------------------------------------------------------------------------
# AC-8: retriable LLMCallError exhaustion (AC-CGP-08)
# ---------------------------------------------------------------------------


async def test_ac8_retriable_llm_error_exhaustion(patch_dependencies, tmp_path):
    """Every PAL call raises retriable LLMCallError."""
    monkeypatch, pal_gen_mod, storage_mod, cgp_constants, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Need to get PAL_RETRY_MAX_ATTEMPTS for retriable classification
    pal_retry_max = pal_gen_mod.PAL_RETRY_MAX_ATTEMPTS

    async def mock_generate(prompt, team_id, cfg, **_kwargs):
        raise LLMCallError(
            provider="openai",
            model="gpt-4o",
            attempt_count=pal_retry_max,  # Makes it retriable
            cause=ConnectionError("rate limit"),
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    with pytest.raises(GenerationFailedError) as exc_info:
        await generate_strategy(config, "team_a")

    err = exc_info.value
    assert err.last_failure == "llm_call_error"
    assert err.attempts_made == cgp_constants.CGP_MAX_RETRIES


# ---------------------------------------------------------------------------
# AC-9: token overflow immediate (AC-CGP-09)
# ---------------------------------------------------------------------------


async def test_ac9_token_overflow_immediate(patch_dependencies, tmp_path):
    """Token limit exceeded, raises before PAL call."""
    monkeypatch, pal_gen_mod, storage_mod, cgp_constants, build_generation_prompt = patch_dependencies
    config = _config(str(tmp_path))

    # Mock low token limit
    monkeypatch.setattr(cgp_constants, "CGP_CONTEXT_LIMIT_TOKENS", 100)

    # Mock high token estimate
    def mock_build_prompt(user_intent="", **_):
        return PromptResult(
            text="x" * 1000,  # Long text
            mode=PromptMode.GENERATION,
            estimated_tokens=500,  # > 100
            template_version="1.0",
        )

    monkeypatch.setattr("src.foundation.code_generation_pipeline.generate.build_generation_prompt", mock_build_prompt)

    # Spy on PAL to verify it's not called
    pal_spy = AsyncMock()
    monkeypatch.setattr(pal_gen_mod, "generate", pal_spy)

    with pytest.raises(PromptContextOverflowError) as exc_info:
        await generate_strategy(config, "team_a")

    err = exc_info.value
    assert err.team_id == "team_a"
    assert err.estimated_tokens > 100
    assert err.context_limit == 100
    pal_spy.assert_not_called()


# ---------------------------------------------------------------------------
# AC-10: WriteFailedError propagates raw (AC-CGP-10)
# ---------------------------------------------------------------------------


async def test_ac10_write_failed_error_propagates_raw(patch_dependencies, tmp_path):
    """Write failure propagates as WriteFailedError, not GenerationFailedError."""
    monkeypatch, pal_gen_mod, storage_mod, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock successful PAL
    async def mock_generate(prompt, team_id, cfg, **_kwargs):
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

    # Mock write_strategy to raise WriteFailedError
    def mock_write_strategy(log_dir, team_id, code, metadata):
        raise storage_mod.WriteFailedError("disk full")

    monkeypatch.setattr(storage_mod, "write_strategy", mock_write_strategy)

    # Should raise WriteFailedError directly, not wrapped
    with pytest.raises(storage_mod.WriteFailedError):
        await generate_strategy(config, "team_a")


# ---------------------------------------------------------------------------
# AC-11: template_version in StrategyMetadata (AC-CGP-11)
# ---------------------------------------------------------------------------


async def test_ac11_template_version_in_metadata(patch_dependencies, tmp_path):
    """Template version is persisted in metadata."""
    monkeypatch, pal_gen_mod, storage_mod, _, build_generation_prompt = patch_dependencies
    config = _config(str(tmp_path))

    # Mock SPB to return specific template version
    def mock_build_prompt(user_intent="", **_):
        return PromptResult(
            text="test prompt",
            mode=PromptMode.GENERATION,
            estimated_tokens=100,
            template_version="2.5",
        )

    monkeypatch.setattr("src.foundation.code_generation_pipeline.generate.build_generation_prompt", mock_build_prompt)

    # Mock PAL
    async def mock_generate(prompt, team_id, cfg, **_kwargs):
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

    # Use real storage to verify metadata persistence
    await generate_strategy(config, "team_a")

    # Read back the strategy file and check header contains template version
    strategy_content = storage_mod.read_version(str(tmp_path), "team_a", 1)
    assert "code-generation-pipeline/2.5" in strategy_content  # Check in the header comment


# ---------------------------------------------------------------------------
# AC-13: cause preserved (AC-CGP-15)
# ---------------------------------------------------------------------------


async def test_ac13_cause_preserved_identity(patch_dependencies, tmp_path):
    """GenerationFailedError.cause is the actual LLMCallError instance."""
    monkeypatch, pal_gen_mod, storage_mod, cgp_constants, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Create specific LLMCallError instance
    pal_retry_max = pal_gen_mod.PAL_RETRY_MAX_ATTEMPTS
    original_error = LLMCallError(
        provider="openai",
        model="gpt-4o",
        attempt_count=pal_retry_max,
        cause=TimeoutError("connection timeout"),
    )

    async def mock_generate(prompt, team_id, cfg, **_kwargs):
        raise original_error

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    with pytest.raises(GenerationFailedError) as exc_info:
        await generate_strategy(config, "team_a")

    err = exc_info.value
    assert err.cause is original_error  # Identity check, not equality
    assert isinstance(err.cause, LLMCallError)


# ---------------------------------------------------------------------------
# AC-14: build_generation_prompt called exactly once (Rule 3)
# ---------------------------------------------------------------------------


async def test_ac14_build_prompt_called_once_despite_retries(patch_dependencies, tmp_path):
    """build_generation_prompt called exactly once despite PAL failures."""
    monkeypatch, pal_gen_mod, storage_mod, cgp_constants, build_generation_prompt = patch_dependencies
    config = _config(str(tmp_path))

    # Spy on build_generation_prompt
    original_build = build_generation_prompt
    mock_build = MagicMock(wraps=original_build)
    monkeypatch.setattr("src.foundation.code_generation_pipeline.generate.build_generation_prompt", mock_build)

    # Mock PAL to fail every time
    async def mock_generate(prompt, team_id, cfg, **_kwargs):
        return LLMResponse(
            text="no code here",  # Causes extraction failure
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=20,
            latency_ms=800.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    with pytest.raises(GenerationFailedError):
        await generate_strategy(config, "team_a")

    # Verify build_generation_prompt called exactly once
    assert mock_build.call_count == 1


# ---------------------------------------------------------------------------
# AC-12: concurrent calls non-interfering (sequential here; full concurrency in Story 005)
# ---------------------------------------------------------------------------


async def test_ac12_sequential_team_calls_non_interfering(patch_dependencies, tmp_path):
    """Two sequential team calls write to separate files."""
    monkeypatch, pal_gen_mod, storage_mod, _, _ = patch_dependencies
    config = _config(str(tmp_path))

    # Mock PAL to return different code based on team_id
    async def mock_generate(prompt, team_id, cfg, **_kwargs):
        if team_id == "team_a":
            code_content = "def decide(state, ctx):\n    return Hold()  # team A"
        else:
            code_content = "def decide(state, ctx):\n    return Hold()  # team B"

        return LLMResponse(
            text=f"```python\n{code_content}\n```",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000.0,
            attempt_count=1,
        )

    monkeypatch.setattr(pal_gen_mod, "generate", mock_generate)

    # Call for both teams sequentially
    code_a = await generate_strategy(config, "team_a")
    code_b = await generate_strategy(config, "team_b")

    # Verify different codes returned
    assert "team A" in code_a
    assert "team B" in code_b
    assert code_a != code_b

    # Verify separate files created
    file_a = tmp_path / "strategies" / "team_a" / "current.py"
    file_b = tmp_path / "strategies" / "team_b" / "current.py"

    assert file_a.exists()
    assert file_b.exists()
    assert file_a.read_text() != file_b.read_text()