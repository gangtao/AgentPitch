"""Issue #31 — offside_enabled toggle on SimulationConfig (IFAB Law 11)."""

from src.foundation.config_models import SimulationConfig


def test_offside_enabled_defaults_false():
    assert SimulationConfig().offside_enabled is False


def test_offside_enabled_accepts_true():
    assert SimulationConfig(offside_enabled=True).offside_enabled is True
