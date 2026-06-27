"""Tests for SPB Story 002: template loader + cache + version extraction."""

from __future__ import annotations

import pytest

from src.foundation.system_prompt_builder import (
    PromptMode,
    TemplateLoadError,
    TemplateRenderError,
    get_template,
    load_templates,
)
from src.foundation.system_prompt_builder import templates as templates_module


_VALID_GENERATION = """{# version: 1.0 #}
GEN: {{ prev_strategy }}
"""

_VALID_GENERATION_JS = """{# version: 1.0 #}
GEN-JS: {{ user_intent }}
"""

_VALID_GENERATION_RUST = """{# version: 1.0 #}
GEN-RUST: {{ user_intent }}
"""

_VALID_EVOLUTION = """{# version: 1.0 #}
PREV: {{ prev_strategy }}
SUMMARY: {{ match_summary }}
"""

_VALID_EVOLUTION_JS = """{# version: 1.0 #}
EVO-JS: {{ prev_strategy }} {{ match_summary }}
"""

_VALID_EVOLUTION_RUST = """{# version: 1.0 #}
EVO-RUST: {{ prev_strategy }} {{ match_summary }}
"""


@pytest.fixture(autouse=True)
def _reset_cache():
    """Clear the module-level template cache before AND after each test."""
    templates_module._template_cache.clear()
    yield
    templates_module._template_cache.clear()


def _write_pair(
    tmp_path,
    gen_content: str = _VALID_GENERATION,
    evo_content: str = _VALID_EVOLUTION,
    gen_js_content: str = _VALID_GENERATION_JS,
    gen_rust_content: str = _VALID_GENERATION_RUST,
    evo_js_content: str = _VALID_EVOLUTION_JS,
    evo_rust_content: str = _VALID_EVOLUTION_RUST,
):
    (tmp_path / "generation.jinja2").write_text(gen_content)
    (tmp_path / "generation-js.jinja2").write_text(gen_js_content)
    (tmp_path / "generation-rust.jinja2").write_text(gen_rust_content)
    (tmp_path / "evolution.jinja2").write_text(evo_content)
    (tmp_path / "evolution-js.jinja2").write_text(evo_js_content)
    (tmp_path / "evolution-rust.jinja2").write_text(evo_rust_content)


# ---------------------------------------------------------------------------
# AC-1: load_templates happy path
# ---------------------------------------------------------------------------


class TestAC1HappyPath:
    def test_load_succeeds(self, tmp_path):
        _write_pair(tmp_path)
        load_templates(str(tmp_path))
        assert PromptMode.GENERATION in templates_module._template_cache
        assert PromptMode.EVOLUTION in templates_module._template_cache
        assert PromptMode.EVOLUTION_JS in templates_module._template_cache
        assert PromptMode.EVOLUTION_RUST in templates_module._template_cache

    def test_versions_extracted(self, tmp_path):
        _write_pair(tmp_path)
        load_templates(str(tmp_path))
        assert templates_module._template_cache[PromptMode.GENERATION].version == "1.0"
        assert templates_module._template_cache[PromptMode.EVOLUTION].version == "1.0"
        assert templates_module._template_cache[PromptMode.EVOLUTION_JS].version == "1.0"
        assert templates_module._template_cache[PromptMode.EVOLUTION_RUST].version == "1.0"


# ---------------------------------------------------------------------------
# AC-2: missing template file → TemplateLoadError (AC-SPB-04)
# ---------------------------------------------------------------------------


class TestAC2MissingFile:
    def test_missing_generation_raises(self, tmp_path):
        # Only write evolution
        (tmp_path / "evolution.jinja2").write_text(_VALID_EVOLUTION)
        with pytest.raises(TemplateLoadError, match="generation.jinja2"):
            load_templates(str(tmp_path))

    def test_missing_evolution_raises(self, tmp_path):
        (tmp_path / "generation.jinja2").write_text(_VALID_GENERATION)
        (tmp_path / "generation-js.jinja2").write_text(_VALID_GENERATION_JS)
        (tmp_path / "generation-rust.jinja2").write_text(_VALID_GENERATION_RUST)
        with pytest.raises(TemplateLoadError, match="evolution.jinja2"):
            load_templates(str(tmp_path))


# ---------------------------------------------------------------------------
# AC-3: invalid Jinja2 syntax → TemplateLoadError (AC-SPB-05)
# ---------------------------------------------------------------------------


class TestAC3InvalidSyntax:
    def test_unclosed_for_loop_raises(self, tmp_path):
        bad = "{# version: 1.0 #}\n{% for x in %}\n"
        _write_pair(tmp_path, gen_content=bad)
        with pytest.raises(TemplateLoadError, match="invalid Jinja2 syntax"):
            load_templates(str(tmp_path))

    def test_unclosed_if_raises(self, tmp_path):
        bad = "{# version: 1.0 #}\n{% if true %}\nno endif\n"
        _write_pair(tmp_path, gen_content=bad)
        with pytest.raises(TemplateLoadError):
            load_templates(str(tmp_path))


# ---------------------------------------------------------------------------
# AC-4: vacuous template → TemplateRenderError (AC-SPB-18)
# ---------------------------------------------------------------------------


class TestAC4VacuousRender:
    def test_empty_body_raises(self, tmp_path):
        # Comments + whitespace only — renders empty
        empty_body = "{# version: 1.0 #}\n   \n\n"
        _write_pair(tmp_path, gen_content=empty_body)
        with pytest.raises(TemplateRenderError, match="empty output"):
            load_templates(str(tmp_path))


# ---------------------------------------------------------------------------
# AC-5: version extraction (AC-SPB-12)
# ---------------------------------------------------------------------------


class TestAC5VersionExtraction:
    @pytest.mark.parametrize("comment,expected", [
        ("{# version: 1.0 #}", "1.0"),
        ("{# version: 2.5 #}", "2.5"),
        ("{# version: alpha-1 #}", "alpha-1"),
        ("{#  version:   3.14   #}", "3.14"),  # extra whitespace
    ])
    def test_version_pattern_variations(self, tmp_path, comment, expected):
        body = f"{comment}\nGEN: {{{{ prev_strategy }}}}\n"
        _write_pair(tmp_path, gen_content=body)
        load_templates(str(tmp_path))
        assert templates_module._template_cache[PromptMode.GENERATION].version == expected


# ---------------------------------------------------------------------------
# AC-6: missing version comment → TemplateLoadError
# ---------------------------------------------------------------------------


class TestAC6MissingVersion:
    def test_no_version_raises(self, tmp_path):
        no_version = "GEN: {{ prev_strategy }}\n"  # no version comment
        _write_pair(tmp_path, gen_content=no_version)
        with pytest.raises(TemplateLoadError, match="missing"):
            load_templates(str(tmp_path))


# ---------------------------------------------------------------------------
# AC-7: get_template before load → RuntimeError
# ---------------------------------------------------------------------------


class TestAC7GetTemplateBeforeLoad:
    def test_raises_runtime_error(self):
        # autouse fixture cleared the cache — load_templates not called
        with pytest.raises(RuntimeError, match="load_templates"):
            get_template(PromptMode.GENERATION)


# ---------------------------------------------------------------------------
# AC-8: atomic replace — partial failure leaves cache untouched
# ---------------------------------------------------------------------------


class TestAC8AtomicReplace:
    def test_failed_reload_preserves_old_cache(self, tmp_path):
        # First successful load
        _write_pair(tmp_path)
        load_templates(str(tmp_path))
        old_gen = templates_module._template_cache[PromptMode.GENERATION]

        # Now break the generation template
        (tmp_path / "generation.jinja2").write_text(
            "{# version: 1.0 #}\n{% for x in %}\n"  # syntax error
        )
        with pytest.raises(TemplateLoadError):
            load_templates(str(tmp_path))

        # Old cache preserved
        assert templates_module._template_cache[PromptMode.GENERATION] is old_gen


# ---------------------------------------------------------------------------
# AC-9: exception class hierarchy
# ---------------------------------------------------------------------------


class TestAC9ExceptionHierarchy:
    def test_template_load_error_subclasses_exception_directly(self):
        assert issubclass(TemplateLoadError, Exception)
        # NOT a subclass of more-specific stdlib errors
        assert not issubclass(TemplateLoadError, RuntimeError)
        assert not issubclass(TemplateLoadError, ValueError)

    def test_template_render_error_subclasses_exception_directly(self):
        assert issubclass(TemplateRenderError, Exception)
        assert not issubclass(TemplateRenderError, RuntimeError)


# ---------------------------------------------------------------------------
# AC-10: idempotent reload — happy path
# ---------------------------------------------------------------------------


class TestAC10IdempotentReload:
    def test_two_consecutive_loads_succeed(self, tmp_path):
        _write_pair(tmp_path)
        load_templates(str(tmp_path))
        load_templates(str(tmp_path))
        assert PromptMode.GENERATION in templates_module._template_cache
        assert PromptMode.EVOLUTION in templates_module._template_cache


# ---------------------------------------------------------------------------
# Bonus: real production templates load successfully
# ---------------------------------------------------------------------------


class TestRealProductionTemplatesLoad:
    def test_default_prompts_load(self):
        load_templates()
        assert PromptMode.GENERATION in templates_module._template_cache
        assert PromptMode.EVOLUTION in templates_module._template_cache
        # 1.0 → 1.1: schema sync (cooldown_remaining, goal_top/goal_bottom).
        # 1.1 → 1.2: attribute rename (save_reach → save, position_sense → discipline).
        # 1.2 → 1.3: ADR-0022 — phase-aware zones, corrected snap formula,
        #            team_phase + formation_zone schema additions.
        # 1.3 → 2.0: dropped per-team bake-in (team_id, attack_direction,
        #            field dims, roster) so generated strategies are portable
        #            across rosters and field sizes (5v5 ↔ 11v11). Evolution
        #            jumped from 1.1 → 2.0 in the same change for symmetry.
        # 2.0 → 2.1 (generation only): swapped sections 1 and 2 so callback
        #            contract precedes role declaration (which references the
        #            game_state parameter the contract introduces).
        # 2.1 → 2.2 (generation only): added a goal-framing preamble above
        #            SECTION 1 so the LLM gets the "why" (win the match) before
        #            the "how" (callback contract).
        # 2.2 → 2.3 (generation only): rewrote section 2 as RUNTIME IDENTITY
        #            (pure state access). Goal x-coords consolidated into
        #            section 4. Portability constraint moved to preamble.
        # 2.3 → 2.4 (generation only): moved schemas right after contract;
        #            added HISTORY SCHEMA section. 13 sections → 14.
        # 2.4 → 2.5 (generation only): added SECTION 13: USER INTENT for the
        #            UI New Strategy splice point. 14 sections → 15.
        # 2.5 → 2.6 (generation only): strengthened SECTION 12 to spell out
        #            "no imports" with explicit math.* alternatives — Claude
        #            and gpt-5 had been ignoring the terse one-liner and
        #            generating import math, which compiles but blows up at
        #            runtime (every tick → silent Hold()).
        # 2.8 → 2.9 (generation only): issue #38 — foul system (Law 12),
        #            offensive/penalty attributes, yellow_cards state.
        # 2.9 → 2.10 (gen) / 2.1 → 2.2 (evo): issue #71 — SHOOTING DISCIPLINE
        #            guidance against the zero-shot dead zone.
        assert templates_module._template_cache[PromptMode.GENERATION].version == "2.10"
        assert templates_module._template_cache[PromptMode.EVOLUTION].version == "2.2"
