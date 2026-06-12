"""Tests for SPB Story 004: build_generation_prompt + 13 sections."""

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
    PromptMode,
    PromptResult,
    build_generation_prompt,
    load_templates,
)
from src.foundation.system_prompt_builder import helpers as helpers_module


GENERATION_SECTION_MARKERS = [
    "=== SECTION 1: CALLBACK CONTRACT ===",
    "=== SECTION 2: GAME_STATE SCHEMA ===",
    "=== SECTION 3: PLAYER_STATE SCHEMA ===",
    "=== SECTION 4: HISTORY SCHEMA ===",
    "=== SECTION 5: RUNTIME IDENTITY ===",
    "=== SECTION 6: FEW-SHOT SKELETON ===",
    "=== SECTION 7: FIELD GEOMETRY ===",
    "=== SECTION 8: ACTION SPACE ===",
    "=== SECTION 9: ATTRIBUTE REFERENCE ===",
    "=== SECTION 10: ROSTER ACCESS ===",
    "=== SECTION 11: FORMATION + SNAP MECHANICS ===",
    "=== SECTION 12: SANDBOX CONSTRAINTS ===",
    "=== SECTION 13: USER INTENT ===",
    "=== SECTION 14: TASK ===",
    "=== SECTION 15: OUTPUT FORMAT ===",
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


# ---------------------------------------------------------------------------
# AC-1: Returns PromptResult with mode=GENERATION (AC-SPB-01)
# ---------------------------------------------------------------------------


class TestAC1ReturnsGenerationPromptResult:
    def test_returns_prompt_result(self):
        result = build_generation_prompt()
        assert isinstance(result, PromptResult)

    def test_mode_is_generation(self):
        result = build_generation_prompt()
        assert result.mode is PromptMode.GENERATION

    def test_text_non_empty(self):
        result = build_generation_prompt()
        assert len(result.text) > 0

    def test_language_javascript_dispatches_to_generation_js(self):
        result = build_generation_prompt(language="javascript")
        assert result.mode is PromptMode.GENERATION_JS
        # Sanity-check the template body is JS-flavoured (function decide).
        assert "function decide(" in result.text

    def test_language_rust_dispatches_to_generation_rust(self):
        result = build_generation_prompt(language="rust")
        assert result.mode is PromptMode.GENERATION_RUST
        # Sanity-check the template body is Rust-flavoured.
        assert "fn decide_logic(" in result.text
        assert "wasm32-wasip1" in result.text

    def test_language_python_default_dispatches_to_generation(self):
        result = build_generation_prompt(language="python")
        assert result.mode is PromptMode.GENERATION


# ---------------------------------------------------------------------------
# AC-2: 15 sections in correct order (HISTORY added in v2.4, USER INTENT in v2.5)
# ---------------------------------------------------------------------------


class TestAC2SectionsInOrder:
    def test_all_markers_present_in_order(self):
        text = build_generation_prompt().text
        positions = [text.index(m) for m in GENERATION_SECTION_MARKERS]
        assert positions == sorted(positions)
        assert len(positions) == 15


# ---------------------------------------------------------------------------
# AC-3: Cross-team symmetry (AC-SPB-11)
# ---------------------------------------------------------------------------


class TestAC3CrossTeamSymmetry:
    """v2.0+ contract: identical text regardless of team. With team_id removed
    from the call, both invocations are now provably the same call — these
    tests now check stability across calls rather than across teams, but the
    structural guarantee is preserved by `test_renders_identically...` below."""

    def test_marker_counts_stable(self):
        text = build_generation_prompt().text
        for marker in GENERATION_SECTION_MARKERS:
            assert text.count(marker) == 1

    def test_section_ordering_correct(self):
        text = build_generation_prompt().text
        positions = [text.index(m) for m in GENERATION_SECTION_MARKERS]
        assert positions == sorted(positions)


# ---------------------------------------------------------------------------
# AC-4: Pure function (AC-SPB-13)
# ---------------------------------------------------------------------------


class TestAC4PureFunction:
    def test_100_calls_byte_identical(self):
        first = build_generation_prompt().text
        for _ in range(100):
            assert build_generation_prompt().text == first


# ---------------------------------------------------------------------------
# AC-5: Schemas present in GENERATION (AC-SPB-15 generation-side)
# ---------------------------------------------------------------------------


class TestAC5SchemasPresent:
    def test_game_state_schema_marker_present(self):
        text = build_generation_prompt().text
        assert "=== SECTION 2: GAME_STATE SCHEMA ===" in text

    def test_player_state_schema_marker_present(self):
        text = build_generation_prompt().text
        assert "=== SECTION 3: PLAYER_STATE SCHEMA ===" in text

    def test_history_schema_marker_present(self):
        # v2.4 added — was a documented gap in earlier versions.
        text = build_generation_prompt().text
        assert "=== SECTION 4: HISTORY SCHEMA ===" in text


# ---------------------------------------------------------------------------
# AC-6 (was: team_id in result) — REMOVED 2026-04-25.
# PromptResult.team_id was deleted; callers track team_id in their own scope.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# AC-7: estimated_tokens correct (AC-SPB-10 integration)
# ---------------------------------------------------------------------------


class TestAC7EstimatedTokens:
    def test_token_count_matches_formula(self):
        result = build_generation_prompt()
        assert result.estimated_tokens == math.ceil(len(result.text) / 3.5)


# ---------------------------------------------------------------------------
# AC-8: template_version copied (AC-SPB-12 integration)
# ---------------------------------------------------------------------------


class TestAC8TemplateVersion:
    def test_version_is_2_7(self):
        result = build_generation_prompt()
        # 1.0 → 1.1: schema sync (cooldown_remaining, goal_top/goal_bottom).
        # 1.1 → 1.2: attribute rename (save_reach → save, position_sense → discipline).
        # 1.2 → 1.3: ADR-0022 — phase-aware zones, corrected snap formula.
        # 1.3 → 2.0: dropped per-team bake-in (team_id, attack_direction,
        #            field dims, roster) so generated strategies are portable.
        # 2.0 → 2.1: swapped sections 1 and 2 — callback contract now comes
        #            before role declaration, since role declaration references
        #            the game_state parameter that the contract introduces.
        # 2.1 → 2.2: added a goal-framing preamble above SECTION 1.
        # 2.2 → 2.3: rewrote section 2 as RUNTIME IDENTITY — purely state
        #            access (my_team, my_player_id, role). Goal x-coords moved
        #            to section 4 alongside other field geometry. Portability
        #            constraint moved to preamble.
        # 2.3 → 2.4: moved schemas (game_state, player_state) right after the
        #            callback contract; added HISTORY SCHEMA section (was a
        #            documented gap — function signature took history but no
        #            schema described it). Section count 13 → 14.
        # 2.4 → 2.5: added SECTION 13: USER INTENT for the UI New Strategy
        #            flow. Empty when called from CGP (default), filled with
        #            the user's typed prompt when called from the API. Section
        #            count 14 → 15.
        # 2.7 → 2.8: issue #31 — documented the offside rule (IFAB Law 11)
        #            in SECTION 8 so strategies time runs / hold a line.
        assert result.template_version == "2.8"


# ---------------------------------------------------------------------------
# AC-9 (was: no team_id branching) — REMOVED 2026-04-25.
# build_generation_prompt() no longer takes team_id, so cross-team symmetry
# is structurally guaranteed; redundant with TestAC11RosterPortability.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# AC-10: Token estimate within sane bounds
# ---------------------------------------------------------------------------


class TestAC10TokenSanityBounds:
    def test_estimate_in_range(self):
        result = build_generation_prompt()
        assert 0 < result.estimated_tokens < 6000


# ---------------------------------------------------------------------------
# AC-11: Roster portability — no per-team bake-in (v2.0 contract)
# ---------------------------------------------------------------------------


class TestAC11RosterPortability:
    """v2.0 generalization (and v2.6 cleanup): the prompt has no per-team
    inputs at all. Cross-team symmetry is structurally guaranteed since
    build_generation_prompt() takes no team identifier. The remaining
    invariants worth testing are determinism + 'reads field dims from
    inputs, not literals'."""

    def test_repeated_calls_byte_identical(self):
        assert build_generation_prompt().text == build_generation_prompt().text

    def test_field_dims_described_via_schema_not_literal(self):
        # The LLM must be told to read game_state["field"]["width"], not
        # given the literal value of any specific config's field_width.
        text = build_generation_prompt().text
        assert 'game_state["field"]["width"]' in text


# ---------------------------------------------------------------------------
# AC-12 (was AC-13): user_intent parameter — UI New Strategy splice point (v2.5)
# ---------------------------------------------------------------------------


class TestUserIntentSplice:
    """v2.5 added an optional user_intent kwarg. CGP callers pass nothing
    (fallback prose renders); the API generate endpoint passes the user's
    typed prompt verbatim into SECTION 13."""

    def test_user_intent_appears_verbatim_when_passed(self):
        intent = "focus on dribbling through the midfield and shoot from outside the box"
        text = build_generation_prompt(user_intent=intent).text
        assert intent in text
        assert "no specific user intent" not in text  # fallback prose suppressed

    def test_default_renders_fallback_prose(self):
        text = build_generation_prompt().text
        assert "no specific user intent" in text

    def test_empty_string_renders_fallback_prose(self):
        # Explicit empty string must behave the same as the default.
        text = build_generation_prompt(user_intent="").text
        assert "no specific user intent" in text

    def test_user_intent_section_marker_present(self):
        text = build_generation_prompt().text
        assert "=== SECTION 13: USER INTENT ===" in text


# ---------------------------------------------------------------------------
# AC-13: Warning logged when estimated > threshold (AC-SPB-14 integration)
# ---------------------------------------------------------------------------


class TestAC12WarningLoggedAtThreshold:
    def test_warning_emitted_when_threshold_lowered(self, caplog, monkeypatch):
        monkeypatch.setattr(helpers_module, "SPB_WARN_TOKEN_THRESHOLD", 100)
        with caplog.at_level(logging.WARNING):
            build_generation_prompt()
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) >= 1
        # Warning text format: "SPB token estimate <N> exceeds SPB_WARN_TOKEN_THRESHOLD=100"
        assert any("SPB_WARN_TOKEN_THRESHOLD" in r.getMessage() for r in warnings)
