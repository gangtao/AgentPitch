"""SimulationConfig gains knockout + extra_time_ratio knobs (issue #83)."""
import pytest
from pydantic import ValidationError
from src.foundation.config_models import SimulationConfig


def _make(**overrides):
    base = dict(goal_reset_ticks=30, half_time_pause_ticks=60)
    base.update(overrides)
    return SimulationConfig(**base)


def test_defaults_are_non_knockout_third_ratio():
    cfg = _make()
    assert cfg.knockout is False
    assert cfg.extra_time_ratio == pytest.approx(1 / 3)


def test_knockout_and_ratio_settable():
    cfg = _make(knockout=True, extra_time_ratio=0.5)
    assert cfg.knockout is True
    assert cfg.extra_time_ratio == 0.5


def test_ratio_bounds_enforced():
    with pytest.raises(ValidationError):
        _make(extra_time_ratio=-0.1)
    with pytest.raises(ValidationError):
        _make(extra_time_ratio=1.5)
