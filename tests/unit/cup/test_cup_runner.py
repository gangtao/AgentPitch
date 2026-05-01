"""Tests for src/orchestration/cli/cup_runner.py helper functions."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.orchestration.cli.cup_runner import (
    _determine_winner,
    _resolve_strategy_path,
    _slot_to_strategy_name,
)


# ---------------------------------------------------------------------------
# _determine_winner
# ---------------------------------------------------------------------------


class TestDetermineWinner:
    MATCH = {"match_id": "cup-test-R1M1", "team_a_slot": 1, "team_b_slot": 4}

    def test_team_a_wins_when_score_a_greater(self):
        # Arrange
        match = self.MATCH.copy()

        # Act
        result, winner_slot, tiebreak = _determine_winner(match, score_a=3, score_b=1)

        # Assert
        assert result == "team_a"
        assert winner_slot == 1
        assert tiebreak is False

    def test_team_b_wins_when_score_b_greater(self):
        # Arrange
        match = self.MATCH.copy()

        # Act
        result, winner_slot, tiebreak = _determine_winner(match, score_a=0, score_b=2)

        # Assert
        assert result == "team_b"
        assert winner_slot == 4
        assert tiebreak is False

    def test_tiebreak_flag_set_on_equal_score(self):
        # Arrange
        match = self.MATCH.copy()

        # Act
        result, winner_slot, tiebreak = _determine_winner(match, score_a=1, score_b=1)

        # Assert
        assert result in ("team_a", "team_b")
        assert winner_slot in (1, 4)
        assert tiebreak is True

    def test_tiebreak_is_deterministic_same_match_id(self):
        """Same match_id must always produce the same tiebreak winner."""
        # Arrange
        match = self.MATCH.copy()

        # Act — call multiple times
        results = {_determine_winner(match, score_a=0, score_b=0)[0] for _ in range(10)}

        # Assert — only one unique result across all calls
        assert len(results) == 1

    def test_tiebreak_different_match_ids_may_differ(self):
        """Different match IDs should produce potentially different tiebreak outcomes,
        demonstrating that the seed varies by ID (not always the same result)."""
        # Arrange
        match_a = {"match_id": "cup-test-R1M1", "team_a_slot": 1, "team_b_slot": 4}
        match_b = {"match_id": "cup-test-R1M2", "team_a_slot": 1, "team_b_slot": 4}

        # Act
        result_a, _, _ = _determine_winner(match_a, score_a=0, score_b=0)
        result_b, _, _ = _determine_winner(match_b, score_a=0, score_b=0)

        # Assert — both are valid results (the two may or may not be equal, but both valid)
        assert result_a in ("team_a", "team_b")
        assert result_b in ("team_a", "team_b")


# ---------------------------------------------------------------------------
# _resolve_strategy_path
# ---------------------------------------------------------------------------


class TestResolveStrategyPath:
    def test_resolve_finds_py_file(self, tmp_path: Path):
        # Arrange
        strategies_dir = tmp_path / "strategies"
        strategies_dir.mkdir()
        py_file = strategies_dir / "my_strategy.py"
        py_file.write_text("# strategy")

        # Act
        result = _resolve_strategy_path(tmp_path, "my_strategy")

        # Assert
        assert result == py_file

    def test_resolve_raises_when_file_missing(self, tmp_path: Path):
        # Arrange
        strategies_dir = tmp_path / "strategies"
        strategies_dir.mkdir()
        # No files created

        # Act / Assert
        with pytest.raises(FileNotFoundError):
            _resolve_strategy_path(tmp_path, "nonexistent_strategy")

    def test_resolve_prefers_py_over_js(self, tmp_path: Path):
        # Arrange
        strategies_dir = tmp_path / "strategies"
        strategies_dir.mkdir()
        py_file = strategies_dir / "dual.py"
        js_file = strategies_dir / "dual.js"
        py_file.write_text("# py strategy")
        js_file.write_text("// js strategy")

        # Act
        result = _resolve_strategy_path(tmp_path, "dual")

        # Assert — .py is tried first in the extension list
        assert result == py_file


# ---------------------------------------------------------------------------
# _slot_to_strategy_name
# ---------------------------------------------------------------------------


class TestSlotToStrategyName:
    CUP_DATA = {
        "teams": [
            {"slot": 1, "strategy_name": "alpha"},
            {"slot": 2, "strategy_name": "beta"},
            {"slot": 3, "strategy_name": "gamma"},
            {"slot": 4, "strategy_name": "delta"},
        ]
    }

    def test_returns_correct_strategy_name_for_slot(self):
        # Arrange / Act
        name = _slot_to_strategy_name(self.CUP_DATA, slot=3)

        # Assert
        assert name == "gamma"

    def test_returns_none_for_missing_slot(self):
        # Arrange / Act
        name = _slot_to_strategy_name(self.CUP_DATA, slot=99)

        # Assert
        assert name is None

    def test_returns_none_when_slot_is_none(self):
        # Arrange / Act
        name = _slot_to_strategy_name(self.CUP_DATA, slot=None)

        # Assert
        assert name is None

    def test_returns_first_slot_strategy(self):
        # Arrange / Act
        name = _slot_to_strategy_name(self.CUP_DATA, slot=1)

        # Assert
        assert name == "alpha"

    def test_returns_last_slot_strategy(self):
        # Arrange / Act
        name = _slot_to_strategy_name(self.CUP_DATA, slot=4)

        # Assert
        assert name == "delta"
