"""
Tests for the specialised passing / shooting PlayerConfig attributes
(added 2026-04-23). These default to None so old fixtures keep working;
ARE blends them with skill as `(2 * specialised + skill) / 3`.

Covers:
- defaults to None
- range validation [1, 20]
- alias: YAML key "pass" maps to Python attr `passing`
- alias: YAML key "shoot" maps to Python attr `shooting`
- model_dump preserves the alias when by_alias=True
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.foundation.config_models import PlayerConfig


def _kwargs(**overrides) -> dict:
    base = {
        "player_id": "team_a_3",
        "role": "MID",
        "speed": 10,
        "skill": 10,
        "strength": 10,
        "save": 0,
        "discipline": 10,
        "dribbling": 10,
    }
    base.update(overrides)
    return base


# -----------------------------------------------------------------------------
# Defaults
# -----------------------------------------------------------------------------


def test_specialised_attrs_default_to_none():
    p = PlayerConfig(**_kwargs())
    assert p.passing is None
    assert p.shooting is None


def test_specialised_attrs_explicit_value_kept():
    p = PlayerConfig(**_kwargs(passing=18, shooting=15))
    assert p.passing == 18
    assert p.shooting == 15


# -----------------------------------------------------------------------------
# Range validation [1, 20]
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("attr", ["passing", "shooting"])
def test_specialised_attr_below_one_rejected(attr):
    with pytest.raises(ValidationError):
        PlayerConfig(**_kwargs(**{attr: 0}))


@pytest.mark.parametrize("attr", ["passing", "shooting"])
def test_specialised_attr_above_twenty_rejected(attr):
    with pytest.raises(ValidationError):
        PlayerConfig(**_kwargs(**{attr: 21}))


@pytest.mark.parametrize("attr,value", [
    ("passing", 1), ("passing", 20),
    ("shooting", 1), ("shooting", 20),
])
def test_specialised_attr_boundary_values_accepted(attr, value):
    p = PlayerConfig(**_kwargs(**{attr: value}))
    assert getattr(p, attr) == value


# -----------------------------------------------------------------------------
# YAML alias: `pass` → passing, `shoot` → shooting
# -----------------------------------------------------------------------------


def test_yaml_alias_pass_maps_to_passing():
    """YAML can use the natural soccer term "pass" — Python keyword
    forces us to expose `passing` as the attribute name."""
    raw = _kwargs()
    raw["pass"] = 17
    p = PlayerConfig(**raw)
    assert p.passing == 17


def test_yaml_alias_shoot_maps_to_shooting():
    raw = _kwargs()
    raw["shoot"] = 12
    p = PlayerConfig(**raw)
    assert p.shooting == 12


def test_python_attr_name_still_works():
    """populate_by_name=True means both the alias and the Python name are
    valid input keys — important so direct constructor calls in tests
    don't have to use the YAML-style "pass" form."""
    p = PlayerConfig(**_kwargs(passing=14, shooting=8))
    assert p.passing == 14
    assert p.shooting == 8


def test_dump_preserves_alias_when_requested():
    p = PlayerConfig(**_kwargs(passing=14, shooting=8))
    dumped = p.model_dump(by_alias=True)
    assert dumped["pass"] == 14
    assert dumped["shoot"] == 8
