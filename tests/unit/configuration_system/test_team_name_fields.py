"""Tests for team_id / name on TeamConfig and name on PlayerConfig."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.foundation.config_models import PlayerConfig, TeamConfig


def _player_kwargs(**overrides):
    base = dict(
        player_id="team_a_0",
        role="GK",
        speed=8,
        skill=10,
        strength=8,
        save=16,
        discipline=14,
        dribbling=4,
        name="Alex",
    )
    base.update(overrides)
    return base


def _team_kwargs(**overrides):
    base = dict(
        team_id="manchester",
        name="Manchester United",
        players=[PlayerConfig(**_player_kwargs())] + [
            PlayerConfig(**_player_kwargs(
                player_id=f"team_a_{i}",
                role="DEF",
                save=0,
                name=f"Player {i+1}",
            ))
            for i in range(1, 5)
        ],
    )
    base.update(overrides)
    return base


class TestPlayerConfigName:
    def test_name_stored(self):
        p = PlayerConfig(**_player_kwargs(name="Alex"))
        assert p.name == "Alex"

    def test_name_defaults_to_empty(self):
        kwargs = _player_kwargs()
        kwargs.pop("name")
        p = PlayerConfig(**kwargs)
        assert p.name == ""

    def test_name_explicit_empty_allowed(self):
        p = PlayerConfig(**_player_kwargs(name=""))
        assert p.name == ""

    def test_name_too_long_rejected(self):
        with pytest.raises(ValidationError):
            PlayerConfig(**_player_kwargs(name="x" * 65))


class TestTeamConfigDisplay:
    def test_team_id_required(self):
        kwargs = _team_kwargs()
        kwargs.pop("team_id")
        with pytest.raises(ValidationError):
            TeamConfig(**kwargs)

    def test_team_id_regex_lowercase_alnum_dash_underscore(self):
        ok_ids = ["manchester", "real-madrid", "team_b", "fc1893", "a"]
        for slug in ok_ids:
            t = TeamConfig(**_team_kwargs(team_id=slug))
            assert t.team_id == slug

        for bad in ["Manchester", "Real Madrid", "manch*ester", ""]:
            with pytest.raises(ValidationError):
                TeamConfig(**_team_kwargs(team_id=bad))

    def test_name_required_and_bounded(self):
        kwargs = _team_kwargs()
        kwargs.pop("name")
        with pytest.raises(ValidationError):
            TeamConfig(**kwargs)

        with pytest.raises(ValidationError):
            TeamConfig(**_team_kwargs(name=""))

        with pytest.raises(ValidationError):
            TeamConfig(**_team_kwargs(name="x" * 65))

        t = TeamConfig(**_team_kwargs(name="Manchester United"))
        assert t.name == "Manchester United"
