"""Issue #38 (IFAB Law 12): foul-system config — offensive/penalty player
attributes and SimulationConfig foul knobs."""

import pytest
from pydantic import ValidationError

from src.foundation.config_models import PlayerConfig, SimulationConfig


def _player(**overrides):
    base = dict(
        player_id="team_a_1", role="MID", speed=10, skill=10, strength=10,
        save=0, discipline=10, dribbling=10,
    )
    base.update(overrides)
    return PlayerConfig(**base)


class TestOffensiveAttribute:
    def test_defaults_to_10(self):
        assert _player().offensive == 10

    def test_accepts_range_bounds(self):
        assert _player(offensive=1).offensive == 1
        assert _player(offensive=20).offensive == 20

    def test_rejects_out_of_range(self):
        with pytest.raises(ValidationError):
            _player(offensive=0)
        with pytest.raises(ValidationError):
            _player(offensive=21)


class TestPenaltyAttribute:
    def test_defaults_to_none_for_shooting_fallback(self):
        assert _player().penalty is None

    def test_accepts_range_bounds(self):
        assert _player(penalty=1).penalty == 1
        assert _player(penalty=20).penalty == 20

    def test_rejects_out_of_range(self):
        with pytest.raises(ValidationError):
            _player(penalty=0)
        with pytest.raises(ValidationError):
            _player(penalty=21)


class TestFoulSimulationKnobs:
    def test_defaults(self):
        sim = SimulationConfig()
        assert sim.fouls_enabled is True
        assert sim.tackle_foul_base == 0.10
        assert sim.foul_yellow_share == 0.25
        assert sim.foul_red_share == 0.05
        assert sim.penalty_goal_base == 0.60
        assert sim.penalty_goal_per_point == 0.015
        assert sim.free_kick_exclusion_radius == 9.15

    def test_shares_bounded(self):
        with pytest.raises(ValidationError):
            SimulationConfig(foul_yellow_share=1.5)
        with pytest.raises(ValidationError):
            SimulationConfig(foul_red_share=-0.1)
