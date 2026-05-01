"""Tests for PMEP Story 001: Exceptions + module constants + StrategyMetadata builder."""

from __future__ import annotations

from dataclasses import fields

import pytest

from src.foundation.post_match_evolution_pipeline import (
    PMEP_MAX_RETRIES,
    PMEP_CONTEXT_LIMIT_TOKENS,
    PMEP_SUMMARY_MAX_TOKENS,
    EvolutionFailedError,
)
from src.foundation.post_match_evolution_pipeline.metadata import _build_metadata
from src.foundation.config_models import (
    MatchConfig,
    MatchParams,
    OutputConfig,
    PlayerConfig,
    TeamConfig,
)
from src.foundation.system_prompt_builder.types import PromptMode, PromptResult


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
# AC-1: EvolutionFailedError schema (5 fields exactly, Exception subclass)
# ---------------------------------------------------------------------------


class TestAC1EvolutionFailedErrorSchema:
    def test_field_count(self):
        assert len(fields(EvolutionFailedError)) == 5

    def test_field_names(self):
        field_names = {f.name for f in fields(EvolutionFailedError)}
        assert field_names == {"team_id", "match_number", "attempts_made", "last_failure", "cause"}

    def test_exception_subclass(self):
        assert issubclass(EvolutionFailedError, Exception)

    def test_construction_with_all_fields(self):
        # Should construct without error
        err = EvolutionFailedError(
            team_id="team_a",
            match_number=3,
            attempts_made=2,
            last_failure="compile_error",
            cause=None
        )
        assert err.team_id == "team_a"
        assert err.match_number == 3
        assert err.attempts_made == 2
        assert err.last_failure == "compile_error"
        assert err.cause is None

    def test_construction_with_cause(self):
        # Test with actual exception as cause
        inner_exc = ValueError("test error")
        err = EvolutionFailedError(
            team_id="team_b",
            match_number=1,
            attempts_made=1,
            last_failure="llm_call_error",
            cause=inner_exc
        )
        assert err.cause is inner_exc


# ---------------------------------------------------------------------------
# AC-2: last_failure literal set (all 8 documented literals accepted)
# ---------------------------------------------------------------------------


class TestAC2LastFailureLiteralSet:
    @pytest.mark.parametrize("failure_type", [
        "empty_response",
        "no_code_block",
        "no_decide_signature",
        "compile_error",
        "llm_call_error",
        "context_overflow",
        "prompt_build_error",
        "generate_summary_error"
    ])
    def test_each_literal_accepted(self, failure_type):
        err = EvolutionFailedError(
            team_id="team_a",
            match_number=1,
            attempts_made=1,
            last_failure=failure_type,
            cause=None
        )
        # Round-trip check
        assert err.last_failure == failure_type


# ---------------------------------------------------------------------------
# AC-3: __str__ readable (diagnostic fields included)
# ---------------------------------------------------------------------------


class TestAC3StrReadable:
    def test_evolution_failed_error_str_contains_all_fields(self):
        err = EvolutionFailedError(
            team_id="team_a",
            match_number=3,
            attempts_made=2,
            last_failure="compile_error",
            cause=None
        )
        error_str = str(err)
        assert "team_a" in error_str
        assert "3" in error_str
        assert "2" in error_str
        assert "compile_error" in error_str

    def test_evolution_failed_error_str_different_values(self):
        err = EvolutionFailedError(
            team_id="team_b",
            match_number=10,
            attempts_made=1,
            last_failure="llm_call_error",
            cause=None
        )
        error_str = str(err)
        assert "team_b" in error_str
        assert "10" in error_str
        assert "1" in error_str
        assert "llm_call_error" in error_str


# ---------------------------------------------------------------------------
# AC-4: Module constants present + correct defaults
# ---------------------------------------------------------------------------


class TestAC4ModuleConstants:
    def test_pmep_max_retries(self):
        assert PMEP_MAX_RETRIES == 3

    def test_pmep_context_limit_tokens(self):
        assert PMEP_CONTEXT_LIMIT_TOKENS == 16_000

    def test_pmep_summary_max_tokens(self):
        assert PMEP_SUMMARY_MAX_TOKENS == 300


# ---------------------------------------------------------------------------
# AC-5: _build_metadata happy path (team_a path)
# ---------------------------------------------------------------------------


class TestAC5BuildMetadataTeamA:
    def test_team_a_happy_path(self):
        config = _config()  # team_a defaults to openai/gpt-4o
        prompt_result = PromptResult(
            text="test prompt",
            mode=PromptMode.EVOLUTION,
            estimated_tokens=100,
            template_version="1.0",
        )

        metadata = _build_metadata("team_a", config, prompt_result, 3)

        assert metadata.team_id == "team_a"
        assert metadata.match_number == 3
        assert metadata.llm_provider == "openai"
        assert metadata.llm_model == "gpt-4o"
        assert metadata.generated_by == "post-match-evolution/1.0"


# ---------------------------------------------------------------------------
# AC-6: _build_metadata reads team_b correctly
# ---------------------------------------------------------------------------


class TestAC6BuildMetadataTeamB:
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
            mode=PromptMode.EVOLUTION,
            estimated_tokens=100,
            template_version="1.0",
        )

        metadata = _build_metadata("team_b", config, prompt_result, 5)

        assert metadata.team_id == "team_b"
        assert metadata.match_number == 5
        assert metadata.llm_provider == "anthropic"
        assert metadata.llm_model == "claude-sonnet-4-5"
        assert metadata.generated_by == "post-match-evolution/1.0"


# ---------------------------------------------------------------------------
# AC-7: generated_by template-version pass-through
# ---------------------------------------------------------------------------


class TestAC7TemplateVersionPassThrough:
    @pytest.mark.parametrize("template_version", ["1.0", "2.5", "v3-beta"])
    def test_template_version_reflected_in_generated_by(self, template_version):
        config = _config()
        prompt_result = PromptResult(
            text="test",
            mode=PromptMode.EVOLUTION,
            estimated_tokens=100,
            template_version=template_version,
        )

        metadata = _build_metadata("team_a", config, prompt_result, 1)
        assert metadata.generated_by == f"post-match-evolution/{template_version}"

    def test_generated_by_prefix_differs_from_cgp(self):
        """Verify PMEP uses different prefix than CGP."""
        config = _config()
        prompt_result = PromptResult(
            text="test",
            mode=PromptMode.EVOLUTION,
            estimated_tokens=100,
            template_version="1.0",
        )

        metadata = _build_metadata("team_a", config, prompt_result, 1)
        # PMEP uses "post-match-evolution/" not "code-generation-pipeline/"
        assert metadata.generated_by.startswith("post-match-evolution/")
        assert not metadata.generated_by.startswith("code-generation-pipeline/")


# ---------------------------------------------------------------------------
# AC-8: match_number is 1-indexed and pass-through
# ---------------------------------------------------------------------------


class TestAC8MatchNumberPassThrough:
    @pytest.mark.parametrize("match_number", [1, 2, 5, 10])
    def test_match_number_pass_through(self, match_number):
        config = _config()
        prompt_result = PromptResult(
            text="test",
            mode=PromptMode.EVOLUTION,
            estimated_tokens=100,
            template_version="1.0",
        )

        metadata = _build_metadata("team_a", config, prompt_result, match_number)
        assert metadata.match_number == match_number

    def test_match_number_independent_of_other_fields(self):
        """Verify match_number doesn't affect other fields."""
        config = _config()
        prompt_result = PromptResult(
            text="test",
            mode=PromptMode.EVOLUTION,
            estimated_tokens=100,
            template_version="1.0",
        )

        metadata1 = _build_metadata("team_a", config, prompt_result, 1)
        metadata2 = _build_metadata("team_a", config, prompt_result, 99)

        # Everything else should be identical
        assert metadata1.team_id == metadata2.team_id
        assert metadata1.llm_provider == metadata2.llm_provider
        assert metadata1.llm_model == metadata2.llm_model
        assert metadata1.generated_by == metadata2.generated_by
        # Only match_number should differ
        assert metadata1.match_number != metadata2.match_number


# ---------------------------------------------------------------------------
# AC-9: Importability (package re-exports public names)
# ---------------------------------------------------------------------------


class TestAC9Importability:
    def test_import_succeeds(self):
        # Re-import to verify package-level re-export works
        from src.foundation.post_match_evolution_pipeline import (
            EvolutionFailedError as EFE,
            PMEP_MAX_RETRIES as PMR,
            PMEP_CONTEXT_LIMIT_TOKENS as PCLT,
            PMEP_SUMMARY_MAX_TOKENS as PSMT,
        )
        assert EFE is EvolutionFailedError
        assert PMR is PMEP_MAX_RETRIES
        assert PCLT is PMEP_CONTEXT_LIMIT_TOKENS
        assert PSMT is PMEP_SUMMARY_MAX_TOKENS

    def test_private_build_metadata_not_exported(self):
        """Verify _build_metadata is private and not in __all__."""
        from src.foundation.post_match_evolution_pipeline import __all__
        assert "_build_metadata" not in __all__

        # Should not be importable from package level
        with pytest.raises(ImportError):
            from src.foundation.post_match_evolution_pipeline import _build_metadata


# ---------------------------------------------------------------------------
# Additional edge case tests for robustness
# ---------------------------------------------------------------------------


class TestAdditionalEdgeCases:
    def test_different_llm_providers_reflected(self):
        """Test various LLM provider/model combinations."""
        config = MatchConfig(
            match=MatchParams(
                seed=42, tick_rate=10, duration_minutes=90,
                field_width=100.0, field_height=60.0,
            ),
            output=OutputConfig(log_dir="/tmp/test"),
            team_a=_team("team_a", "anthropic", "claude-opus-4-6"),
            team_b=_team("team_b", "openai", "gpt-4o-mini"),
        )

        prompt_result = PromptResult(
            text="test",
            mode=PromptMode.EVOLUTION,
            estimated_tokens=100,
            template_version="1.0",
        )

        metadata_a = _build_metadata("team_a", config, prompt_result, 1)
        metadata_b = _build_metadata("team_b", config, prompt_result, 1)

        assert metadata_a.llm_provider == "anthropic"
        assert metadata_a.llm_model == "claude-opus-4-6"
        assert metadata_b.llm_provider == "openai"
        assert metadata_b.llm_model == "gpt-4o-mini"

    def test_template_version_special_characters(self):
        """Test template versions with special characters."""
        config = _config()
        prompt_result = PromptResult(
            text="test",
            mode=PromptMode.EVOLUTION,
            estimated_tokens=100,
            template_version="v2.1-beta.3",
        )

        metadata = _build_metadata("team_a", config, prompt_result, 1)
        assert metadata.generated_by == "post-match-evolution/v2.1-beta.3"