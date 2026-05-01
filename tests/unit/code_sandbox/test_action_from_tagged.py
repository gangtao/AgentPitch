"""Tests for Action.from_tagged() — tagged-dict → Action conversion (ADR-0024)."""

from __future__ import annotations

import pytest

from src.foundation.action import Action, Hold, Move, Pass, Shoot, Tackle


def test_from_tagged_move():
    action = Action.from_tagged({"type": "Move", "dx": 1.0, "dy": -0.5, "speed": 0.8})
    assert isinstance(action, Move)
    assert action.dx == 1.0
    assert action.dy == -0.5
    assert action.speed == 0.8


def test_from_tagged_pass():
    action = Action.from_tagged({"type": "Pass", "target_pos": [50.0, 30.0], "power": 15})
    assert isinstance(action, Pass)
    assert action.target_pos == (50.0, 30.0)
    assert action.power == 15


def test_from_tagged_shoot():
    action = Action.from_tagged({"type": "Shoot", "angle": 5.0, "power": 18})
    assert isinstance(action, Shoot)
    assert action.angle == 5.0
    assert action.power == 18


def test_from_tagged_tackle():
    action = Action.from_tagged({"type": "Tackle", "target_player_id": "team_b_2"})
    assert isinstance(action, Tackle)
    assert action.target_player_id == "team_b_2"


def test_from_tagged_hold():
    action = Action.from_tagged({"type": "Hold"})
    assert isinstance(action, Hold)


def test_from_tagged_missing_type_returns_hold():
    action = Action.from_tagged({"dx": 1.0})
    assert isinstance(action, Hold)


def test_from_tagged_unknown_type_returns_hold():
    action = Action.from_tagged({"type": "Sprint"})
    assert isinstance(action, Hold)


def test_from_tagged_missing_field_returns_hold():
    action = Action.from_tagged({"type": "Move", "dx": 1.0})
    assert isinstance(action, Hold)


def test_from_tagged_target_pos_tuple():
    action = Action.from_tagged({"type": "Pass", "target_pos": (50.0, 30.0), "power": 10})
    assert isinstance(action, Pass)
    assert action.target_pos == (50.0, 30.0)