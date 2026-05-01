"""Tests for PMEP Story 002: Pre-loop helpers — _read_prev_strategy_or_fallback + _generate_match_summary."""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.foundation.post_match_evolution_pipeline.preloop import (
    _read_prev_strategy_or_fallback,
    _generate_match_summary,
)
from src.foundation.post_match_evolution_pipeline.types import EvolutionFailedError
from src.foundation.post_match_evolution_pipeline.constants import PMEP_SUMMARY_MAX_TOKENS
from src.foundation.strategy_storage import StrategyNotFoundError


class TestReadPrevStrategyOrFallback:
    """Tests for _read_prev_strategy_or_fallback helper function."""

    def test_read_prev_strategy_happy_path_returns_strategy(self, monkeypatch, caplog):
        """AC-1: When read_current returns strategy, helper returns it with no logs."""
        # Arrange
        expected_strategy = "def decide(game_state): return Hold()"
        preloop_mod = importlib.import_module("src.foundation.post_match_evolution_pipeline.preloop")
        mock_read_current = MagicMock(return_value=expected_strategy)
        monkeypatch.setattr(preloop_mod, "read_current", mock_read_current)

        log_dir = Path("/tmp/test")
        team_id = "team_a"
        match_number = 2

        # Act
        with caplog.at_level(logging.WARNING):
            result = _read_prev_strategy_or_fallback(log_dir, team_id, match_number)

        # Assert
        assert result == expected_strategy
        mock_read_current.assert_called_once_with(str(log_dir), team_id)
        assert len(caplog.records) == 0  # No WARNING+ logs

    def test_read_prev_strategy_match_1_warning_on_not_found(self, monkeypatch, caplog):
        """AC-2 (AC-PMEP-10): StrategyNotFoundError + match_number==1 → WARNING log, return empty."""
        # Arrange
        preloop_mod = importlib.import_module("src.foundation.post_match_evolution_pipeline.preloop")
        mock_read_current = MagicMock(side_effect=StrategyNotFoundError("No strategy found for team_a"))
        monkeypatch.setattr(preloop_mod, "read_current", mock_read_current)

        log_dir = Path("/tmp/test")
        team_id = "team_a"
        match_number = 1

        # Act
        with caplog.at_level(logging.WARNING):
            result = _read_prev_strategy_or_fallback(log_dir, team_id, match_number)

        # Assert
        assert result == ""
        warning_records = [r for r in caplog.records if r.levelno == logging.WARNING]
        error_records = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(warning_records) == 1
        assert len(error_records) == 0  # Must NOT be ERROR
        assert team_id in warning_records[0].message
        assert "match_number=1" in warning_records[0].message

    def test_read_prev_strategy_match_gt_1_error_on_not_found(self, monkeypatch, caplog):
        """AC-3 (AC-PMEP-11): StrategyNotFoundError + match_number>1 → ERROR log, return empty."""
        # Arrange
        preloop_mod = importlib.import_module("src.foundation.post_match_evolution_pipeline.preloop")
        mock_read_current = MagicMock(side_effect=StrategyNotFoundError("No strategy found for team_a"))
        monkeypatch.setattr(preloop_mod, "read_current", mock_read_current)

        log_dir = Path("/tmp/test")
        team_id = "team_a"
        match_number = 5

        # Act
        with caplog.at_level(logging.WARNING):
            result = _read_prev_strategy_or_fallback(log_dir, team_id, match_number)

        # Assert
        assert result == ""
        warning_records = [r for r in caplog.records if r.levelno == logging.WARNING]
        error_records = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(warning_records) == 0  # Must NOT be WARNING
        assert len(error_records) == 1
        assert team_id in error_records[0].message
        assert "5" in error_records[0].message  # match_number substring

    def test_read_prev_strategy_other_exception_propagates(self, monkeypatch):
        """Anti-drift: Only StrategyNotFoundError is caught; other exceptions propagate."""
        # Arrange
        preloop_mod = importlib.import_module("src.foundation.post_match_evolution_pipeline.preloop")
        filesystem_error = OSError("Disk full")
        mock_read_current = MagicMock(side_effect=filesystem_error)
        monkeypatch.setattr(preloop_mod, "read_current", mock_read_current)

        log_dir = Path("/tmp/test")
        team_id = "team_a"
        match_number = 1

        # Act & Assert
        with pytest.raises(OSError) as exc_info:
            _read_prev_strategy_or_fallback(log_dir, team_id, match_number)
        assert exc_info.value is filesystem_error

    def test_read_prev_strategy_log_namespace_filter(self, monkeypatch, caplog):
        """Anti-drift: Verify caplog tests filter for the pmep namespace to avoid false positives."""
        # Arrange
        preloop_mod = importlib.import_module("src.foundation.post_match_evolution_pipeline.preloop")
        mock_read_current = MagicMock(side_effect=StrategyNotFoundError("No strategy found for team_a"))
        monkeypatch.setattr(preloop_mod, "read_current", mock_read_current)

        log_dir = Path("/tmp/test")
        team_id = "team_a"
        match_number = 1

        # Act
        with caplog.at_level(logging.WARNING):
            _read_prev_strategy_or_fallback(log_dir, team_id, match_number)

        # Assert
        warning_records = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warning_records) == 1
        # Logger name should be the preloop module's __name__
        assert warning_records[0].name.startswith("src.foundation.post_match_evolution_pipeline")


class TestGenerateMatchSummary:
    """Tests for _generate_match_summary helper function."""

    def test_generate_match_summary_happy_path_returns_summary(self):
        """AC-4: When generate_summary returns text, helper returns it verbatim."""
        # Arrange
        match_log = MagicMock()
        expected_summary = "team_a scored 1 goal in tick 47"
        match_log.generate_summary.return_value = expected_summary

        team_id = "team_a"
        match_number = 2

        # Act
        result = _generate_match_summary(match_log, team_id=team_id, match_number=match_number)

        # Assert
        assert result == expected_summary

    def test_generate_match_summary_empty_result_ok(self):
        """AC-5 (EC-PMEP-03): Empty summary is NOT an error, return empty string."""
        # Arrange
        match_log = MagicMock()
        match_log.generate_summary.return_value = ""

        team_id = "team_a"
        match_number = 2

        # Act
        result = _generate_match_summary(match_log, team_id=team_id, match_number=match_number)

        # Assert
        assert result == ""

    def test_generate_match_summary_exception_raises_evolution_failed_error(self):
        """AC-6 (AC-PMEP-17): generate_summary exception → EvolutionFailedError with cause identity."""
        # Arrange
        match_log = MagicMock()
        the_exception = RuntimeError("MLS broken")
        match_log.generate_summary.side_effect = the_exception

        team_id = "team_a"
        match_number = 3

        # Act & Assert
        with pytest.raises(EvolutionFailedError) as exc_info:
            _generate_match_summary(match_log, team_id=team_id, match_number=match_number)

        assert exc_info.value.last_failure == "generate_summary_error"
        assert exc_info.value.cause is the_exception  # Identity check
        assert exc_info.value.team_id == team_id
        assert exc_info.value.match_number == match_number
        assert exc_info.value.attempts_made == 0

    def test_generate_match_summary_passes_max_tokens_constant(self):
        """AC-7: max_tokens=PMEP_SUMMARY_MAX_TOKENS passed to generate_summary."""
        # Arrange
        match_log = MagicMock()
        match_log.generate_summary.return_value = "summary text"

        team_id = "team_a"
        match_number = 2

        # Act
        _generate_match_summary(match_log, team_id=team_id, match_number=match_number)

        # Assert
        match_log.generate_summary.assert_called_once_with(max_tokens=PMEP_SUMMARY_MAX_TOKENS)
        # Verify the constant value is what we expect (300)
        assert PMEP_SUMMARY_MAX_TOKENS == 300

    def test_generate_match_summary_no_retry_on_failure(self):
        """AC-9: Helper does NOT retry on generate_summary failure, call count == 1."""
        # Arrange
        match_log = MagicMock()
        match_log.generate_summary.side_effect = RuntimeError("broken")

        team_id = "team_a"
        match_number = 3

        # Act
        with pytest.raises(EvolutionFailedError):
            _generate_match_summary(match_log, team_id=team_id, match_number=match_number)

        # Assert
        assert match_log.generate_summary.call_count == 1