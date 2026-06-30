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


def test_early_clinch_stops_before_all_five_kicks():
    """Deterministic early clinch: team_a always scores, team_b always misses.

    Using base=1.0 with save_per_point=0.1, conversion is fully determined by
    the opposing keeper's save rating (no RNG):
      team_a faces team_b GK save=10 -> p_goal = 1.0  (always scores)
      team_b faces team_a GK save=20 -> p_goal = clamp(1.0 - 0.1*10) = 0.0 (always misses)
    team_a reaches 3 while team_b is on 0 -> clinched after team_b's 3rd kick (6 total).
    """
    knobs = ShootoutKnobs(base=1.0, per_point=0.0, save_per_point=0.1)
    a = {"team_a_0": {"team": "team_a", "role": "GK", "save": 20, "penalty": 10},
         "team_a_1": {"team": "team_a", "role": "FW", "penalty": 10},
         "team_a_2": {"team": "team_a", "role": "MF", "penalty": 10},
         "team_a_3": {"team": "team_a", "role": "MF", "penalty": 10},
         "team_a_4": {"team": "team_a", "role": "MF", "penalty": 10}}
    b = {"team_b_0": {"team": "team_b", "role": "GK", "save": 10, "penalty": 10},
         "team_b_1": {"team": "team_b", "role": "FW", "penalty": 10},
         "team_b_2": {"team": "team_b", "role": "MF", "penalty": 10},
         "team_b_3": {"team": "team_b", "role": "MF", "penalty": 10},
         "team_b_4": {"team": "team_b", "role": "MF", "penalty": 10}}
    r = resolve_shootout(a, b, seed=5, knobs=knobs)
    assert r.winner == "team_a"
    assert r.score == {"team_a": 3, "team_b": 0}
    assert len(r.kicks) == 6


def test_sudden_death_cap_terminates_when_all_miss():
    """Sudden-death loop must terminate even when p_goal=0.0 for every taker.

    With base=0.0 and per_point=0.0 no taker ever scores; the old `while True`
    loop would hang forever. The cap (_MAX_SUDDEN_DEATH_PAIRS=100) must fire and
    return a deterministic winner without new randomness.

    Why the OLD code hangs: the `while True` block only breaks when
    `score["team_a"] != score["team_b"]`, which never happens if neither team
    ever scores — infinite loop.
    """
    knobs = ShootoutKnobs(base=0.0, per_point=0.0, save_per_point=0.0)
    a = _roster("team_a", gk_save=10, penalty=10)
    b = _roster("team_b", gk_save=10, penalty=10)
    r1 = resolve_shootout(a, b, seed=99, knobs=knobs)
    r2 = resolve_shootout(a, b, seed=99, knobs=knobs)
    assert r1.winner in ("team_a", "team_b")
    assert r1 == r2                          # same seed → same winner (deterministic)
    # Both teams score 0 (every kick missed)
    assert r1.score["team_a"] == 0
    assert r1.score["team_b"] == 0


def test_sudden_death_after_tied_best_of_five():
    """Sudden death is entered when both teams convert equally in the best-of-5.

    seed=2 was found by searching 0..500 for a result with len(kicks) > 10
    using equal rosters and default KNOBS (p_goal=0.75 per taker).
    Kick-by-kick: after 10 kicks both teams are tied at 4 goals each,
    so sudden death runs until team_a wins 8-7 after 18 total kicks.
    """
    a, b = _roster("team_a"), _roster("team_b")
    r = resolve_shootout(a, b, seed=2, knobs=KNOBS)  # seed=2 found by search 0..500
    # Entered sudden death
    assert len(r.kicks) > 10
    # Best-of-5 was tied (first 10 kicks: 5 from each team)
    first10 = r.kicks[:10]
    a_bo5 = sum(1 for k in first10 if k.team == "team_a" and k.scored)
    b_bo5 = sum(1 for k in first10 if k.team == "team_b" and k.scored)
    assert a_bo5 == b_bo5
    # A valid winner is declared
    assert r.winner in ("team_a", "team_b")
    assert r.score[r.winner] > r.score["team_b" if r.winner == "team_a" else "team_a"]
    # Deterministic: same seed → identical result
    r2 = resolve_shootout(a, b, seed=2, knobs=KNOBS)
    assert r == r2
