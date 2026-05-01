"""Tests for SPB Story 003: helpers + token estimation + tuning constants.

Note: tests for the removed `_build_team_context` helper were deleted in
2026-04-25 alongside the function — generation v2.4 and evolution v2.0
dropped all per-team substitutions, so the helper had no callers.
"""

from __future__ import annotations

import logging

from src.foundation.system_prompt_builder import (
    SPB_MAX_KEY_EVENTS,
    SPB_TOKEN_CHARS_RATIO,
    SPB_WARN_TOKEN_THRESHOLD,
    estimate_tokens,
    warn_if_over_threshold,
)
from src.foundation.system_prompt_builder import helpers as helpers_module


# ---------------------------------------------------------------------------
# AC-1: estimate_tokens — known values (AC-SPB-10)
# ---------------------------------------------------------------------------


class TestAC1EstimateTokensKnownValues:
    def test_length_35_returns_10(self):
        assert estimate_tokens("x" * 35) == 10  # 35 / 3.5 = 10.0

    def test_empty_string_zero(self):
        assert estimate_tokens("") == 0

    def test_length_1_returns_1(self):
        assert estimate_tokens("x") == 1  # ceil(1/3.5) = 1

    def test_length_350_returns_100(self):
        assert estimate_tokens("x" * 350) == 100


# ---------------------------------------------------------------------------
# AC-2: warn_if_over_threshold logs above threshold
# ---------------------------------------------------------------------------


class TestAC2WarnIfOverThreshold:
    def test_above_threshold_warns(self, caplog):
        with caplog.at_level(logging.WARNING):
            warn_if_over_threshold(12001)
        assert len(caplog.records) == 1
        msg = caplog.records[0].getMessage()
        assert "12001" in msg
        assert "12000" in msg


# ---------------------------------------------------------------------------
# AC-3: warn_if_over_threshold silent at threshold (strict greater than)
# ---------------------------------------------------------------------------


class TestAC3WarnSilentAtThreshold:
    def test_at_threshold_no_warning(self, caplog):
        with caplog.at_level(logging.WARNING):
            warn_if_over_threshold(12000)
        assert len(caplog.records) == 0

    def test_below_threshold_no_warning(self, caplog):
        with caplog.at_level(logging.WARNING):
            warn_if_over_threshold(0)
            warn_if_over_threshold(11999)
        assert len(caplog.records) == 0


# ---------------------------------------------------------------------------
# AC-9: module constants present + correct values
# ---------------------------------------------------------------------------


class TestAC9ModuleConstants:
    def test_warn_token_threshold(self):
        assert SPB_WARN_TOKEN_THRESHOLD == 12000

    def test_max_key_events(self):
        assert SPB_MAX_KEY_EVENTS == 5

    def test_token_chars_ratio(self):
        assert SPB_TOKEN_CHARS_RATIO == 3.5


# ---------------------------------------------------------------------------
# AC-10: estimate_tokens uses module constant (not hardcoded)
# ---------------------------------------------------------------------------


class TestAC10EstimateUsesConstant:
    def test_patched_constant_changes_result(self, monkeypatch):
        monkeypatch.setattr(helpers_module, "SPB_TOKEN_CHARS_RATIO", 7.0)
        # Length 70 / 7.0 = 10
        assert helpers_module.estimate_tokens("x" * 70) == 10
