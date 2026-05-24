import pytest
from pydantic import ValidationError

from src.api.http_server.team_config_payload import TeamConfigPayload


def _minimal(**overrides):
    base = dict(
        team_id="manchester",
        name="Manchester United",
        players=[
            {"role": "GK", "save": 16, "name": "Onana"},
            {"role": "DEF"},
            {"role": "DEF"},
            {"role": "MID"},
            {"role": "FWD"},
        ],
    )
    base.update(overrides)
    return base


def test_minimal_valid():
    TeamConfigPayload(**_minimal())


def test_rejects_invalid_team_id():
    with pytest.raises(ValidationError):
        TeamConfigPayload(**_minimal(team_id="Manchester"))


def test_rejects_too_few_players():
    with pytest.raises(ValidationError):
        TeamConfigPayload(**_minimal(players=[{"role": "GK", "save": 16}]))


def test_rejects_extra_fields():
    payload = _minimal()
    payload["foo"] = "bar"
    with pytest.raises(ValidationError):
        TeamConfigPayload(**payload)
