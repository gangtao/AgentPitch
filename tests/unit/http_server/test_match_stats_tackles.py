"""Tackle stats semantics fix (issue #38 follow-up).

"Tackles" must count genuine challenges only — not out-of-range whiffs,
settle-grace/stale no-ops, or restart-pending voids. "Tackles won" means
the carrier was dispossessed: a clean take (controlled) OR a deflection
(blocked). Dribble contests are the same duel seen from the attacker's
side — the targeted defender gets a tackle attempt, and a failed dribble
(defender steals) is a tackle won.
"""

from src.api.http_server.match_stats import compute_match_stats


META = {
    "match_id": "m1",
    "teams": {
        "team_a": {"team_id": "bra", "name": "Brazil", "roster": [
            {"player_id": "team_a_3", "name": "Mid", "number": 8, "role": "MID"},
        ]},
        "team_b": {"team_id": "ger", "name": "Germany", "roster": [
            {"player_id": "team_b_1", "name": "Def", "number": 2, "role": "DEF"},
        ]},
    },
}


def _tick(actions, tick=1):
    return {"tick": tick, "ball_possession": None, "player_positions": {},
            "actions": actions}


def _tackle(pid, team, result):
    return {"player_id": pid, "team": team, "action": "Tackle",
            "result": result, "details": {"result": result}}


def _stats(actions):
    return compute_match_stats([_tick(actions)], META)


def test_non_contests_not_counted_as_attempts():
    stats = _stats([
        _tackle("team_b_1", "team_b", "out_of_range"),
        _tackle("team_b_1", "team_b", "no_op_settled"),
        _tackle("team_b_1", "team_b", "no_op_carrier_changed"),
        _tackle("team_b_1", "team_b", "no_op_restart_pending"),
        _tackle("team_b_1", "team_b", "ok"),  # consumed by dribble contest
    ])
    assert stats["teams"]["team_b"]["tackles_attempted"] == 0
    assert stats["players"]["team_b_1"]["tackles_attempted"] == 0


def test_blocked_counts_as_won():
    stats = _stats([
        _tackle("team_b_1", "team_b", "controlled"),
        _tackle("team_b_1", "team_b", "blocked"),
        _tackle("team_b_1", "team_b", "failed"),
        _tackle("team_b_1", "team_b", "foul"),
    ])
    assert stats["teams"]["team_b"]["tackles_attempted"] == 4
    assert stats["teams"]["team_b"]["tackles_successful"] == 2  # controlled + blocked
    assert stats["players"]["team_b_1"]["tackles_successful"] == 2


def test_dribble_contest_credits_targeted_defender():
    # Carrier team_a_3 dribbles at team_b_1: one failed (defender steals),
    # one success (defender beaten). Defender gets 2 attempts, 1 won.
    actions = [
        {"player_id": "team_a_3", "team": "team_a", "action": "Move",
         "result": "ok", "details": {"dribble_result": "failed",
                                     "dribble_target": "team_b_1"}},
        {"player_id": "team_a_3", "team": "team_a", "action": "Move",
         "result": "ok", "details": {"dribble_result": "success",
                                     "dribble_target": "team_b_1"}},
    ]
    stats = _stats(actions)
    assert stats["teams"]["team_b"]["tackles_attempted"] == 2
    assert stats["teams"]["team_b"]["tackles_successful"] == 1
    assert stats["players"]["team_b_1"]["tackles_attempted"] == 2
    assert stats["players"]["team_b_1"]["tackles_successful"] == 1
    # Attacker's dribble stats unchanged by the defender credit.
    assert stats["teams"]["team_a"]["dribbles_attempted"] == 2
    assert stats["teams"]["team_a"]["dribbles_successful"] == 1
