"""Issue #31 — offside_enabled toggle on SimulationConfig (IFAB Law 11)."""

from src.foundation.config_models import SimulationConfig


def test_offside_enabled_defaults_true():
    """Default flipped to True on 2026-06-11 (user decision after the
    detection geometry was validated against a real match log)."""
    assert SimulationConfig().offside_enabled is True


def test_offside_enabled_accepts_false():
    assert SimulationConfig(offside_enabled=False).offside_enabled is False
