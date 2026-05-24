"""Tests for apply_player_name_default in config_preprocessor."""
from __future__ import annotations

from src.foundation.config_preprocessor import apply_player_name_default


def test_missing_name_defaults_to_index_label():
    raw = {"role": "DEF"}
    out = apply_player_name_default(raw, index=0)
    assert out["name"] == "Player 1"


def test_none_name_defaults_to_index_label():
    raw = {"role": "DEF", "name": None}
    out = apply_player_name_default(raw, index=2)
    assert out["name"] == "Player 3"


def test_empty_string_defaults_to_index_label():
    raw = {"role": "DEF", "name": ""}
    out = apply_player_name_default(raw, index=4)
    assert out["name"] == "Player 5"


def test_whitespace_only_defaults_to_index_label():
    raw = {"role": "DEF", "name": "   "}
    out = apply_player_name_default(raw, index=1)
    assert out["name"] == "Player 2"


def test_explicit_name_preserved():
    raw = {"role": "DEF", "name": "Alex"}
    out = apply_player_name_default(raw, index=0)
    assert out["name"] == "Alex"


def test_does_not_mutate_input():
    raw = {"role": "DEF"}
    apply_player_name_default(raw, index=0)
    assert "name" not in raw
