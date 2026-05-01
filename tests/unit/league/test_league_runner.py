"""Unit tests for league_runner helper functions."""
import pytest
from src.orchestration.cli.league_runner import _determine_result


def test_determine_result_team_a_wins():
    result = _determine_result(score_a=3, score_b=1)
    assert result == ("team_a", 3, 1)


def test_determine_result_team_b_wins():
    result = _determine_result(score_a=0, score_b=2)
    assert result == ("team_b", 0, 2)


def test_determine_result_draw():
    result = _determine_result(score_a=1, score_b=1)
    assert result == ("draw", 1, 1)


def test_determine_result_zero_zero_draw():
    result = _determine_result(score_a=0, score_b=0)
    assert result == ("draw", 0, 0)
