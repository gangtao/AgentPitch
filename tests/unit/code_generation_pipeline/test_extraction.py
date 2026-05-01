"""Tests for CGP Story 002: extract_decide_code — fenced code block extractor."""

from __future__ import annotations

import pytest

from src.foundation.code_generation_pipeline import extract_decide_code


class TestExtractDecideCodeHappyPath:
    """AC-1: Returns code on happy path."""

    def test_extract_decide_code_single_python_fenced_block_success(self):
        # Arrange
        response = "Sure, here's the code:\n\n```python\ndef decide(state, ctx):\n    return Hold()\n```"

        # Act
        code, err = extract_decide_code(response)

        # Assert
        assert err is None
        assert code == "def decide(state, ctx):\n    return Hold()"
        assert "```" not in code  # No fence remnants


class TestFenceStrippingMandatory:
    """AC-2 (AC-CGP-13): Fence stripping verified — stripped output is bare Python."""

    def test_fence_stripping_removes_all_fence_markers(self):
        # Arrange
        response = "```python\ndef decide(state, ctx):\n    return Hold()\n```"

        # Act
        code, err = extract_decide_code(response)

        # Assert
        assert err is None
        assert "```" not in code
        assert not code.startswith("python\n")
        assert code.startswith("def decide(")


class TestLastBlockSelection:
    """AC-3 (AC-CGP-14): Last block wins — second lacks decide."""

    def test_last_block_wins_second_lacks_decide_signature(self):
        # Arrange - first block has decide, second doesn't
        response = (
            "```python\n"
            "def decide(state, ctx):\n"
            "    return Hold()\n"
            "```\n\n"
            "And then:\n\n"
            "```python\n"
            "x = 1\n"
            "```"
        )

        # Act
        code, err = extract_decide_code(response)

        # Assert
        assert code is None
        assert err == "no_decide_signature"

    def test_last_block_wins_last_is_valid(self):
        """AC-4: Last block wins, last is valid."""
        # Arrange - first block invalid, second has decide
        response = (
            "```python\n"
            "x = 1\n"
            "```\n\n"
            "And the actual strategy:\n\n"
            "```python\n"
            "def decide(state, ctx):\n"
            "    return Hold()\n"
            "```"
        )

        # Act
        code, err = extract_decide_code(response)

        # Assert
        assert err is None
        assert code == "def decide(state, ctx):\n    return Hold()"


class TestNoFencedBlock:
    """AC-5: No fenced block at all."""

    def test_no_fenced_block_returns_no_code_block_error(self):
        # Arrange
        response = "I would suggest the following strategy: hold the line."

        # Act
        code, err = extract_decide_code(response)

        # Assert
        assert code is None
        assert err == "no_code_block"


class TestBareDecideFallback:
    """AC-12 (added 2026-04-25): some LLMs (notably Claude with reasoning,
    and gpt-5.x) ignore the 'wrap in fences' instruction. The extractor
    falls back to a column-0 `def decide(` line."""

    def test_bare_decide_at_column_0_extracts(self):
        # Arrange — function preceded by prose, no fences
        response = (
            "Here's a strategy that prioritises ball control:\n"
            "\n"
            "def decide(g, p, h):\n"
            "    if p['has_ball']:\n"
            "        return Hold()\n"
            "    return Move(dx=1.0, dy=0.0, speed=1.0)\n"
        )

        code, err = extract_decide_code(response)

        assert err is None
        assert code is not None
        assert code.startswith("def decide(")
        assert "return Hold()" in code

    def test_fenced_block_still_preferred_over_bare_decide(self):
        # If both forms appear, the fenced block wins (matches existing AC-3).
        response = (
            "def decide(g, p, h):\n"
            "    return Hold()\n"
            "\n"
            "Actually, use this one instead:\n"
            "```python\n"
            "def decide(g, p, h):\n"
            "    return Move(dx=1.0, dy=0.0, speed=1.0)\n"
            "```\n"
        )

        code, err = extract_decide_code(response)

        assert err is None
        assert "return Move" in code  # fenced block, not the bare one

    def test_bare_decide_inside_indented_text_not_matched(self):
        # If `def decide(` only appears indented (e.g. as part of a code
        # snippet inside an explanation), don't try to extract — too risky.
        response = "I'd write something like:\n    def decide(g, p, h):\n        return Hold()\n"

        code, err = extract_decide_code(response)

        assert code is None
        assert err == "no_code_block"


class TestEmptyFencedBlock:
    """AC-6: Empty fenced block."""

    def test_empty_fenced_block_returns_no_decide_signature_error(self):
        # Arrange
        response = "```python\n```"

        # Act
        code, err = extract_decide_code(response)

        # Assert
        assert code is None
        assert err == "no_decide_signature"


class TestBareFence:
    """AC-7: Bare fence (no language tag) accepted."""

    def test_bare_fence_no_language_tag_accepted(self):
        # Arrange
        response = "```\ndef decide(state, ctx):\n    return Hold()\n```"

        # Act
        code, err = extract_decide_code(response)

        # Assert
        assert err is None
        assert code == "def decide(state, ctx):\n    return Hold()"


class TestIndentationPreserved:
    """AC-8: Indentation preserved."""

    def test_indentation_preserved_nested_block_code(self):
        # Arrange
        response = (
            "```python\n"
            "def decide(state, ctx):\n"
            "    if state[\"score\"] > 0:\n"
            "        return Hold()\n"
            "```"
        )

        # Act
        code, err = extract_decide_code(response)

        # Assert
        assert err is None
        assert "\n    if " in code  # 4-space indent on if
        assert "\n        return" in code  # 8-space indent on return


class TestSurroundingBlankLinesStripped:
    """AC-9: Surrounding blank lines stripped."""

    def test_surrounding_blank_lines_stripped_function_boundaries_clean(self):
        # Arrange - blank lines before and after function inside fences
        response = (
            "```python\n"
            "\n\n"  # Leading blank lines inside fence
            "def decide(state, ctx):\n"
            "    return Hold()\n"
            "\n\n"  # Trailing blank lines inside fence
            "```"
        )

        # Act
        code, err = extract_decide_code(response)

        # Assert
        assert err is None
        assert code.startswith("def decide(")
        assert code.rstrip().endswith("return Hold()")
        assert not code.startswith("\n")  # No leading newlines


class TestSubstringExactness:
    """AC-10: `def decide(` substring is exact."""

    def test_substring_exactness_decide_v2_rejected(self):
        # Arrange - function name has decide as prefix only
        response = (
            "```python\n"
            "def decide_v2(state, ctx):\n"
            "    return Hold()\n"
            "```"
        )

        # Act
        code, err = extract_decide_code(response)

        # Assert
        assert code is None
        assert err == "no_decide_signature"


class TestOtherLanguageTagsAccepted:
    """AC-11: Other language tags accepted."""

    @pytest.mark.parametrize("lang", ["py", "python3", "Python"])
    def test_other_language_tags_accepted_parametrized(self, lang):
        # Arrange
        response = f"```{lang}\ndef decide(state, ctx):\n    return Hold()\n```"

        # Act
        code, err = extract_decide_code(response)

        # Assert
        assert err is None
        assert code == "def decide(state, ctx):\n    return Hold()"


class TestPurity:
    """AC-12: Purity — deterministic, no I/O."""

    def test_purity_deterministic_no_side_effects(self):
        # Arrange
        response = "```python\ndef decide(state, ctx):\n    return Hold()\n```"

        # Act - call twice with same input
        result1 = extract_decide_code(response)
        result2 = extract_decide_code(response)

        # Assert - byte-equal results both times
        assert result1 == result2
        assert result1[0] == result2[0]  # Same code
        assert result1[1] == result2[1]  # Same error (None)

        # No filesystem, network, or logging side effects are possible to test
        # directly, but the function is pure by design (no I/O imports/calls)