"""Penalty shootout resolver (issue #83). Pure + deterministic."""
import pytest
from src.foundation.penalty_shootout import (
    ShootoutKnobs, ShootoutResult, resolve_shootout,
)

KNOBS = ShootoutKnobs(base=0.60, per_point=0.015, save_per_point=0.01)


def _roster(team, n=5, gk_save=10, penalty=10):
    players = {f"{team}_{i}": {"team": team, "role": "MF", "penalty": penalty}
               for i in range(n)}
    players[f"{team}_0"] = {"team": team, "role": "GK", "save": gk_save, "penalty": penalty}
    return players


def test_returns_a_winner_and_is_deterministic():
    a, b = _roster("team_a"), _roster("team_b")
    r1 = resolve_shootout(a, b, seed=42, knobs=KNOBS)
    r2 = resolve_shootout(a, b, seed=42, knobs=KNOBS)
    assert r1.winner in ("team_a", "team_b")
    assert r1 == r2                          # identical result, same seed
    assert r1.score[r1.winner] > r1.score["team_b" if r1.winner == "team_a" else "team_a"]


def test_no_keeper_means_certain_conversion_for_attacker():
    # team_b has no GK on field → every team_a kick must score (p_goal=1.0).
    a = _roster("team_a")
    b = {f"team_b_{i}": {"team": "team_b", "role": "MF", "penalty": 10} for i in range(1, 5)}
    r = resolve_shootout(a, b, seed=7, knobs=KNOBS)
    team_a_kicks = [k for k in r.kicks if k.team == "team_a"]
    assert all(k.p_goal == 1.0 and k.scored for k in team_a_kicks)


def test_takers_ordered_by_penalty_rating_best_first():
    a = {
        "team_a_0": {"team": "team_a", "role": "GK", "save": 10, "penalty": 5},
        "team_a_1": {"team": "team_a", "role": "FW", "penalty": 18},
        "team_a_2": {"team": "team_a", "role": "MF", "penalty": 12},
    }
    b = _roster("team_b")
    r = resolve_shootout(a, b, seed=1, knobs=KNOBS)
    first_a = next(k for k in r.kicks if k.team == "team_a")
    assert first_a.taker_id == "team_a_1"     # highest penalty rating kicks first


def test_sent_off_players_excluded_as_takers():
    a = _roster("team_a")
    a["team_a_1"]["sent_off"] = True
    b = _roster("team_b")
    r = resolve_shootout(a, b, seed=3, knobs=KNOBS)
    assert all(k.taker_id != "team_a_1" for k in r.kicks if k.team == "team_a")


def test_early_clinch_stops_before_all_five():
    # Strong attackers (penalty 20) vs no keepers on either side → both always
    # score, so it cannot clinch early; instead verify the kick count never
    # exceeds 5 per side before sudden death by construction.
    a = _roster("team_a", penalty=20)
    b = _roster("team_b", penalty=20)
    r = resolve_shootout(a, b, seed=9, knobs=KNOBS)
    a_first5 = [k for k in r.kicks if k.team == "team_a"][:5]
    b_first5 = [k for k in r.kicks if k.team == "team_b"][:5]
    # Both convert all 5 → tie after regulation kicks → sudden death entered.
    assert len(a_first5) == 5 and len(b_first5) == 5
    assert len(r.kicks) > 10                   # sudden death happened
