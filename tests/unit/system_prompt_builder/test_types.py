"""Tests for SPB Story 001: PromptMode + PromptResult."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields

import pytest

from src.foundation.system_prompt_builder import PromptMode, PromptResult


# ---------------------------------------------------------------------------
# AC-1: PromptMode exact membership (2 members)
# ---------------------------------------------------------------------------


class TestAC1PromptModeMembership:
    def test_exactly_three_members(self):
        # Members grew to 4 with ADR-0026 (GENERATION_RUST), then 6 with
        # language-aware evolution (EVOLUTION_JS, EVOLUTION_RUST). Test name kept.
        assert len(PromptMode) == 6

    def test_member_names(self):
        names = set(PromptMode.__members__.keys())
        assert names == {
            "GENERATION", "GENERATION_JS", "GENERATION_RUST",
            "EVOLUTION", "EVOLUTION_JS", "EVOLUTION_RUST",
        }


# ---------------------------------------------------------------------------
# AC-2: PromptMode values are lowercase strings
# ---------------------------------------------------------------------------


class TestAC2PromptModeValues:
    def test_generation_value(self):
        assert PromptMode.GENERATION.value == "generation"

    def test_evolution_value(self):
        assert PromptMode.EVOLUTION.value == "evolution"

    @pytest.mark.parametrize("member", list(PromptMode))
    def test_value_is_lowercase_string(self, member):
        assert member.value == member.value.lower()


# ---------------------------------------------------------------------------
# AC-3: PromptResult schema (4 fields exactly, in spec order)
# 2026-04-25: team_id removed — never read by any consumer.
# ---------------------------------------------------------------------------


class TestAC3PromptResultSchema:
    def test_field_count(self):
        assert len(fields(PromptResult)) == 4

    def test_field_names_in_order(self):
        expected = ["text", "mode", "estimated_tokens", "template_version"]
        assert [f.name for f in fields(PromptResult)] == expected


# ---------------------------------------------------------------------------
# AC-4: PromptResult round-trip — all 4 fields readable post-construction
# ---------------------------------------------------------------------------


class TestAC4PromptResultRoundTrip:
    def test_round_trip(self):
        r = PromptResult(
            text="hello prompt",
            mode=PromptMode.GENERATION,
            estimated_tokens=100,
            template_version="1.0",
        )
        assert r.text == "hello prompt"
        assert r.mode is PromptMode.GENERATION
        assert r.estimated_tokens == 100
        assert r.template_version == "1.0"


# ---------------------------------------------------------------------------
# AC-5: PromptResult frozen — AC-SPB-03
# ---------------------------------------------------------------------------


class TestAC5PromptResultFrozen:
    @pytest.mark.parametrize("field_name,new_value", [
        ("text", "modified"),
        ("mode", PromptMode.EVOLUTION),
        ("estimated_tokens", 999),
        ("template_version", "2.0"),
    ])
    def test_each_field_rejects_mutation(self, field_name, new_value):
        r = PromptResult(
            text="x",
            mode=PromptMode.GENERATION,
            estimated_tokens=1,
            template_version="1.0",
        )
        with pytest.raises(FrozenInstanceError):
            setattr(r, field_name, new_value)


# ---------------------------------------------------------------------------
# AC-6: Importability from package
# ---------------------------------------------------------------------------


class TestAC6Importability:
    def test_imports_from_package_root(self):
        # Re-import to verify package-level re-export works
        from src.foundation.system_prompt_builder import PromptMode as PM, PromptResult as PR
        assert PM is PromptMode
        assert PR is PromptResult
