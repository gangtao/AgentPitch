"""Tests for SPB Story 005: build_evolution_prompt + fallback rules + schema-drop."""

from __future__ import annotations

import logging
import math

import pytest

from src.foundation.config_models import (
    MatchConfig,
    MatchParams,
    OutputConfig,
    PlayerConfig,
    TeamConfig,
)
from src.foundation.system_prompt_builder import (
    SPB_MAX_KEY_EVENTS,
    PromptMode,
    PromptResult,
    build_evolution_prompt,
    load_templates,
)


EVOLUTION_SECTION_MARKERS = [
    "=== SECTION 1: ROLE DECLARATION ===",
    "=== SECTION 2: PRIOR STRATEGY ===",
    "=== SECTION 3: MATCH LOG SUMMARY ===",
    "=== SECTION 4: CALLBACK CONTRACT ===",
    "=== SECTION 5: ACTION SPACE ===",
    "=== SECTION 6: ATTRIBUTE REFERENCE ===",
    "=== SECTION 7: ROSTER ACCESS ===",
    "=== SECTION 8: FORMATION + SNAP MECHANICS ===",
    "=== SECTION 9: SANDBOX CONSTRAINTS ===",
    "=== SECTION 10: TASK ===",
    "=== SECTION 11: OUTPUT FORMAT ===",
]


@pytest.fixture(scope="module", autouse=True)
def _load_templates_once():
    load_templates()


def _player(player_id: str, role: str, save: int = 0) -> PlayerConfig:
    return PlayerConfig(
        player_id=player_id, role=role,
        speed=10, skill=10, strength=10, save=save,
        discipline=10, dribbling=10,
    )


def _team(team_id: str = "team_a") -> TeamConfig:
    return TeamConfig(
        llm_provider="openai", llm_model="gpt-4o", api_key="sk-test",
        players=[
            _player(f"{team_id}_0", "GK", save=16),
            _player(f"{team_id}_1", "DEF"),
            _player(f"{team_id}_2", "DEF"),
            _player(f"{team_id}_3", "MID"),
            _player(f"{team_id}_4", "FWD"),
        ],
    )


def _config() -> MatchConfig:
    return MatchConfig(
        match=MatchParams(
            seed=42, tick_rate=10, duration_minutes=90,
            field_width=100.0, field_height=60.0,
        ),
        output=OutputConfig(log_dir="/tmp/test"),
        team_a=_team("team_a"),
        team_b=_team("team_b"),
    )


_VALID_PREV = "def decide(g, p, h):\n    return Hold()\n"
_VALID_SUMMARY = "Score: team_a 2 - team_b 1. Possession: 55%."


# ---------------------------------------------------------------------------
# AC-1: Returns PromptResult with mode=EVOLUTION (AC-SPB-02)
# ---------------------------------------------------------------------------


class TestAC1ReturnsEvolutionPromptResult:
    def test_returns_evolution(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY)
        assert isinstance(result, PromptResult)
        assert result.mode is PromptMode.EVOLUTION
        assert len(result.text) > 0


# ---------------------------------------------------------------------------
# AC-2: prev_strategy fallback to GENERATION (AC-SPB-06)
# ---------------------------------------------------------------------------


class TestAC2PrevStrategyFallback:
    def test_empty_prev_falls_back_to_generation(self, caplog):
        with caplog.at_level(logging.WARNING):
            result = build_evolution_prompt("", "summary text")
        assert result.mode is PromptMode.GENERATION
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert any(
            "evolution_prompt: no prev_strategy provided, falling back to generation"
            in r.getMessage()
            for r in warnings
        )

    def test_none_prev_falls_back_to_generation(self, caplog):
        with caplog.at_level(logging.WARNING):
            result = build_evolution_prompt(None, "summary")  # type: ignore[arg-type]
        assert result.mode is PromptMode.GENERATION


# ---------------------------------------------------------------------------
# AC-3: match_summary fallback (AC-SPB-07)
# ---------------------------------------------------------------------------


class TestAC3MatchSummaryFallback:
    def test_empty_summary_uses_no_data_note(self):
        result = build_evolution_prompt(_VALID_PREV, "")
        assert result.mode is PromptMode.EVOLUTION
        assert "No match result is available" in result.text

    def test_none_summary_uses_no_data_note(self):
        result = build_evolution_prompt(_VALID_PREV, None)  # type: ignore[arg-type]
        assert result.mode is PromptMode.EVOLUTION
        assert "No match result is available" in result.text


# ---------------------------------------------------------------------------
# AC-4: Section ordering + prev_strategy precedes Match Log Summary (AC-SPB-09)
# ---------------------------------------------------------------------------


class TestAC4SectionOrdering:
    def test_prev_strategy_precedes_match_log_summary_marker(self):
        prev = "UNIQUE_PREV_STRATEGY_MARKER\nreturn Hold()\n"
        result = build_evolution_prompt(prev, _VALID_SUMMARY)
        assert "UNIQUE_PREV_STRATEGY_MARKER" in result.text
        prev_idx = result.text.index("UNIQUE_PREV_STRATEGY_MARKER")
        marker_idx = result.text.index("=== SECTION 3: MATCH LOG SUMMARY ===")
        assert prev_idx < marker_idx

    def test_all_11_markers_in_order(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY)
        positions = [result.text.index(m) for m in EVOLUTION_SECTION_MARKERS]
        assert positions == sorted(positions)
        assert len(positions) == 11


# ---------------------------------------------------------------------------
# AC-5: Schemas dropped (AC-SPB-15 evolution-side)
# ---------------------------------------------------------------------------


class TestAC5SchemasDropped:
    def test_no_game_state_schema_marker(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY)
        assert "=== SECTION 9: GAME_STATE SCHEMA ===" not in result.text
        assert "=== SECTION 10: PLAYER_STATE SCHEMA ===" not in result.text

    def test_substitution_string_present(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY)
        # The evolution prompt references the generation prompt's schemas
        # rather than re-printing them. Per ADR-0022 the wording calls out
        # the new team_phase / formation_zone keys but otherwise refers
        # back. The "unchanged from your previous prompt" tail is the
        # invariant we care about.
        assert "unchanged from your previous prompt" in result.text


# ---------------------------------------------------------------------------
# AC-6: prev_strategy verbatim — no normalisation (AC-SPB-17)
# ---------------------------------------------------------------------------


class TestAC6PrevStrategyVerbatim:
    def test_exact_substring_match(self):
        prev = "def decide(gs, ps, h): return Hold()"
        result = build_evolution_prompt(prev, _VALID_SUMMARY)
        assert prev in result.text

    def test_whitespace_preserved(self):
        prev = "def decide(   gs   ,   ps,h   ):    return    Hold()"
        result = build_evolution_prompt(prev, _VALID_SUMMARY)
        assert prev in result.text


# ---------------------------------------------------------------------------
# AC-7 (was: team_id on fallback path) — REMOVED 2026-04-25.
# PromptResult.team_id was deleted; team identity isn't carried by SPB.
# Fallback-mode detection is still tested via TestAC2/AC3 .mode assertions.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# AC-8: SPB_MAX_KEY_EVENTS plumbed (AC-SPB-19 advisory)
# ---------------------------------------------------------------------------


class TestAC8MaxKeyEventsPlumbed:
    def test_constant_is_5_default(self):
        assert SPB_MAX_KEY_EVENTS == 5

    def test_evolution_call_succeeds(self):
        # Smoke check — the constant is referenced in build.py; the evolution
        # call completes without error. Truncation logic deferred until PMEP
        # defines the match_summary format.
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY)
        assert result.mode is PromptMode.EVOLUTION


# ---------------------------------------------------------------------------
# AC-9: Pure function (AC-SPB-13 evolution-side)
# ---------------------------------------------------------------------------


class TestAC9PureFunction:
    def test_two_calls_byte_identical(self):
        cfg = _config()
        r1 = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY)
        r2 = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY)
        assert r1.text == r2.text


# ---------------------------------------------------------------------------
# AC-10: estimated_tokens correct (AC-SPB-10 integration)
# ---------------------------------------------------------------------------


class TestAC10EstimatedTokens:
    def test_token_count_matches_formula(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY)
        assert result.estimated_tokens == math.ceil(len(result.text) / 3.5)


# ---------------------------------------------------------------------------
# AC-11: template_version copied (AC-SPB-12 integration)
# ---------------------------------------------------------------------------


class TestAC11TemplateVersion:
    def test_version_is_2_0(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY)
        # 1.0 → 1.1: ADR-0022 — phase-aware zones, corrected snap formula.
        # 1.1 → 2.0: dropped per-team bake-in (team_id, attack_direction,
        #            roster) so revised strategies stay portable. Bumped
        #            in lockstep with generation v2.0.
        assert result.template_version == "2.0"


# ---------------------------------------------------------------------------
# AC-12: 11 sections in order
# ---------------------------------------------------------------------------


class TestAC12Sections:
    def test_eleven_markers_strictly_increasing(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY)
        positions = [result.text.index(m) for m in EVOLUTION_SECTION_MARKERS]
        # strictly increasing
        for i in range(1, len(positions)):
            assert positions[i] > positions[i - 1]


# ---------------------------------------------------------------------------
# Language routing — JS and Rust evolution templates
# ---------------------------------------------------------------------------


class TestLanguageRouting:
    def test_javascript_returns_evolution_js_mode(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY, language="javascript")
        assert result.mode is PromptMode.EVOLUTION_JS
        assert len(result.text) > 0

    def test_rust_returns_evolution_rust_mode(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY, language="rust")
        assert result.mode is PromptMode.EVOLUTION_RUST
        assert len(result.text) > 0

    def test_python_default_returns_evolution_mode(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY, language="python")
        assert result.mode is PromptMode.EVOLUTION

    def test_unknown_language_defaults_to_python(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY, language="cobol")
        assert result.mode is PromptMode.EVOLUTION

    def test_javascript_fallback_uses_generation_js(self, caplog):
        with caplog.at_level(logging.WARNING):
            result = build_evolution_prompt("", _VALID_SUMMARY, language="javascript")
        assert result.mode is PromptMode.GENERATION_JS

    def test_rust_fallback_uses_generation_rust(self, caplog):
        with caplog.at_level(logging.WARNING):
            result = build_evolution_prompt("", _VALID_SUMMARY, language="rust")
        assert result.mode is PromptMode.GENERATION_RUST

    def test_prev_strategy_embedded_in_js_evolution(self):
        result = build_evolution_prompt(_VALID_PREV, _VALID_SUMMARY, language="javascript")
        assert _VALID_PREV in result.text
