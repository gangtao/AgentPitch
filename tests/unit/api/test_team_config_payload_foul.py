"""Issue #38: API mirrors accept offensive/penalty (ADR-0006 — independent
of foundation models)."""

from src.api.http_server.team_config_payload import TeamPlayerPayload


def test_player_payload_accepts_offensive_and_penalty():
    p = TeamPlayerPayload(role="MID", offensive=15, penalty=18)
    assert p.offensive == 15
    assert p.penalty == 18


def test_player_payload_defaults_none():
    p = TeamPlayerPayload(role="MID")
    assert p.offensive is None
    assert p.penalty is None
