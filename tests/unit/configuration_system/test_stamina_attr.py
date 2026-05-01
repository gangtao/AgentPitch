"""
Tests for the stamina PlayerConfig attribute (added 2026-04-23).

Stamina is required to be in [1, 20]. Defaults to 10 so existing
fixtures keep working without migration. Drives the health-drain
formula in ARE: drain = base_cost × (1 - stamina/20).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.foundation.config_models import PlayerConfig, SimulationConfig


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


def test_stamina_default_is_ten():
    p = PlayerConfig(**_kwargs())
    assert p.stamina == 10


def test_stamina_explicit_value():
    p = PlayerConfig(**_kwargs(stamina=18))
    assert p.stamina == 18


@pytest.mark.parametrize("bad", [0, -1, 21, 100])
def test_stamina_out_of_range_rejected(bad):
    with pytest.raises(ValidationError):
        PlayerConfig(**_kwargs(stamina=bad))


@pytest.mark.parametrize("ok", [1, 10, 20])
def test_stamina_boundary_accepted(ok):
    p = PlayerConfig(**_kwargs(stamina=ok))
    assert p.stamina == ok


# -----------------------------------------------------------------------------
# SimulationConfig knobs
# -----------------------------------------------------------------------------


def test_health_max_default():
    sc = SimulationConfig()
    assert sc.health_max == 100.0


def test_health_drain_factor_default():
    sc = SimulationConfig()
    assert sc.health_drain_factor == 1.0


def test_health_floor_default():
    sc = SimulationConfig()
    assert sc.health_floor == 0.6


def test_health_floor_clamped():
    with pytest.raises(ValidationError):
        SimulationConfig(health_floor=-0.1)
    with pytest.raises(ValidationError):
        SimulationConfig(health_floor=1.5)


def test_health_max_must_be_positive():
    with pytest.raises(ValidationError):
        SimulationConfig(health_max=0.0)
