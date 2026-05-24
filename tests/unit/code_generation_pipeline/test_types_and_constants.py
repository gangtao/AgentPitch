"""Tests for CGP Story 001: Exceptions + module constants + StrategyMetadata builder."""

from __future__ import annotations

from dataclasses import fields

import pytest

from src.foundation.code_generation_pipeline import (
    CGP_MAX_RETRIES,
    CGP_CONTEXT_LIMIT_TOKENS,
    GenerationFailedError,
    PromptContextOverflowError,
)
from src.foundation.code_generation_pipeline.metadata import _build_metadata
from src.foundation.config_models import (
    MatchConfig,
    MatchParams,
    OutputConfig,
    PlayerConfig,
    TeamConfig,
)
from src.foundation.system_prompt_builder import PromptMode, PromptResult


def _player(player_id: str, role: str, save: int = 0) -> PlayerConfig:
    """Factory for test PlayerConfig objects."""
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


def _team(team_id: str = "team_a", llm_provider: str = "openai", llm_model: str = "gpt-4o") -> TeamConfig:
    """Factory for test TeamConfig objects."""
    return TeamConfig(
        team_id=team_id,
        name=team_id.replace("_", " ").title(),
        llm_provider=llm_provider,
        llm_model=llm_model,
        api_key="sk-test",
        players=[
            _player(f"{team_id}_0", "GK", save=16),
            _player(f"{team_id}_1", "DEF"),
            _player(f"{team_id}_2", "DEF"),
            _player(f"{team_id}_3", "MID"),
            _player(f"{team_id}_4", "FWD"),
        ],
    )


def _config() -> MatchConfig:
    """Factory for test MatchConfig objects."""
    return MatchConfig(
        match=MatchParams(
            seed=42, tick_rate=10, duration_minutes=90,
            field_width=100.0, field_height=60.0,
        ),
        output=OutputConfig(log_dir="/tmp/test"),
        team_a=_team("team_a"),
        team_b=_team("team_b"),
    )


# ---------------------------------------------------------------------------
# AC-1: GenerationFailedError schema (4 fields exactly, Exception subclass)
# ---------------------------------------------------------------------------


class TestAC1GenerationFailedErrorSchema:
    def test_field_count(self):
        assert len(fields(GenerationFailedError)) == 4

    def test_field_names(self):
        field_names = {f.name for f in fields(GenerationFailedError)}
        assert field_names == {"team_id", "attempts_made", "last_failure", "cause"}

    def test_exception_subclass(self):
        assert issubclass(GenerationFailedError, Exception)

    def test_construction_with_all_fields(self):
        # Should construct without error
        err = GenerationFailedError(
            team_id="team_a",
            attempts_made=3,
            last_failure="compile_error",
            cause=None
        )
        assert err.team_id == "team_a"
        assert err.attempts_made == 3
        assert err.last_failure == "compile_error"
        assert err.cause is None


# ---------------------------------------------------------------------------
# AC-2: last_failure literal set (all 6 documented literals accepted)
# ---------------------------------------------------------------------------


class TestAC2LastFailureLiteralSet:
    @pytest.mark.parametrize("failure_type", [
        "empty_response",
        "no_code_block",
        "no_decide_signature",
        "compile_error",
        "llm_call_error",
        "context_overflow"
    ])
    def test_each_literal_accepted(self, failure_type):
        err = GenerationFailedError(
            team_id="team_a",
            attempts_made=1,
            last_failure=failure_type,
            cause=None
        )
        # Round-trip check
        assert err.last_failure == failure_type


# ---------------------------------------------------------------------------
# AC-3: PromptContextOverflowError schema (3 fields exactly, Exception subclass)
# ---------------------------------------------------------------------------


class TestAC3PromptContextOverflowErrorSchema:
    def test_field_count(self):
        assert len(fields(PromptContextOverflowError)) == 3

    def test_field_names(self):
        field_names = {f.name for f in fields(PromptContextOverflowError)}
        assert field_names == {"team_id", "estimated_tokens", "context_limit"}

    def test_exception_subclass(self):
        assert issubclass(PromptContextOverflowError, Exception)


# ---------------------------------------------------------------------------
# AC-4: Module constants present + correct defaults
# ---------------------------------------------------------------------------


class TestAC4ModuleConstants:
    def test_cgp_max_retries(self):
        assert CGP_MAX_RETRIES == 3

    def test_cgp_context_limit_tokens(self):
        assert CGP_CONTEXT_LIMIT_TOKENS == 16000


# ---------------------------------------------------------------------------
# AC-5: _build_metadata returns StrategyMetadata (team_a path)
# ---------------------------------------------------------------------------


class TestAC5BuildMetadataTeamA:
    def test_team_a_happy_path(self):
        config = _config()  # team_a defaults to openai/gpt-4o
        prompt_result = PromptResult(
            text="test prompt",
            mode=PromptMode.GENERATION,
            estimated_tokens=100,
            template_version="1.0",
        )

        metadata = _build_metadata("team_a", config, prompt_result)

        assert metadata.team_id == "team_a"
        assert metadata.match_number == 0
        assert metadata.llm_provider == "openai"
        assert metadata.llm_model == "gpt-4o"
        assert metadata.generated_by == "code-generation-pipeline/1.0"


# ---------------------------------------------------------------------------
# AC-6: generated_by template-version pass-through
# ---------------------------------------------------------------------------


class TestAC6TemplateVersionPassThrough:
    @pytest.mark.parametrize("template_version", ["1.0", "2.5", "v3-beta"])
    def test_template_version_reflected(self, template_version):
        config = _config()
        prompt_result = PromptResult(
            text="test",
            mode=PromptMode.GENERATION,
            estimated_tokens=100,
            template_version=template_version,
        )

        metadata = _build_metadata("team_a", config, prompt_result)
        assert metadata.generated_by == f"code-generation-pipeline/{template_version}"


# ---------------------------------------------------------------------------
# AC-7: team_b path (_build_metadata reads config.team_b when team_id == "team_b")
# ---------------------------------------------------------------------------


class TestAC7BuildMetadataTeamB:
    def test_team_b_path(self):
        # Create config with team_b configured for anthropic/claude-sonnet-4-5
        config = MatchConfig(
            match=MatchParams(
                seed=42, tick_rate=10, duration_minutes=90,
                field_width=100.0, field_height=60.0,
            ),
            output=OutputConfig(log_dir="/tmp/test"),
            team_a=_team("team_a", "openai", "gpt-4o"),
            team_b=_team("team_b", "anthropic", "claude-sonnet-4-5"),
        )
        prompt_result = PromptResult(
            text="test",
            mode=PromptMode.GENERATION,
            estimated_tokens=100,
            template_version="1.0",
        )

        metadata = _build_metadata("team_b", config, prompt_result)

        assert metadata.team_id == "team_b"
        assert metadata.llm_provider == "anthropic"
        assert metadata.llm_model == "claude-sonnet-4-5"


# ---------------------------------------------------------------------------
# AC-8: Exception __str__ readable (diagnostic fields included)
# ---------------------------------------------------------------------------


class TestAC8ExceptionStrReadable:
    def test_generation_failed_error_str(self):
        err = GenerationFailedError(
            team_id="team_a",
            attempts_made=3,
            last_failure="compile_error",
            cause=None
        )
        error_str = str(err)
        assert "team_a" in error_str
        assert "3" in error_str
        assert "compile_error" in error_str

    def test_prompt_context_overflow_error_str(self):
        err = PromptContextOverflowError(
            team_id="team_b",
            estimated_tokens=18000,
            context_limit=16000
        )
        error_str = str(err)
        assert "team_b" in error_str
        assert "18000" in error_str
        assert "16000" in error_str


# ---------------------------------------------------------------------------
# AC-9: Importability (package re-exports public names)
# ---------------------------------------------------------------------------


class TestAC9Importability:
    def test_import_succeeds(self):
        # Re-import to verify package-level re-export works
        from src.foundation.code_generation_pipeline import (
            GenerationFailedError as GFE,
            PromptContextOverflowError as PCOE,
            CGP_MAX_RETRIES as CMR,
            CGP_CONTEXT_LIMIT_TOKENS as CCLT,
        )
        assert GFE is GenerationFailedError
        assert PCOE is PromptContextOverflowError
        assert CMR is CGP_MAX_RETRIES
        assert CCLT is CGP_CONTEXT_LIMIT_TOKENS