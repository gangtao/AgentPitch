"""Deterministic penalty-shootout resolver (issue #83).

Pure: no engine state, no live field. Resolves a knockout match still level
after extra time. Reuses the IFAB Law 14 conversion model used for in-match
penalties (action_resolution_engine.engine ~line 1507) so behaviour is
consistent, and the shared hash_01 RNG so results are reproducible.

Rules: 5 kicks per side, alternating A,B,A,B,...; stop as soon as the result is
mathematically decided ("early clinch"); then sudden-death pairs (one kick each)
until one team leads after an equal number of kicks.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.foundation.simulation_utils import hash_01

_MAX_SUDDEN_DEATH_PAIRS = 100


@dataclass(frozen=True)
class ShootoutKnobs:
    base: float
    per_point: float
    save_per_point: float


@dataclass(frozen=True)
class ShootoutKick:
    order: int          # global kick index, 0-based (also the RNG discriminator)
    team: str
    taker_id: str
    p_goal: float
    scored: bool


@dataclass(frozen=True)
class ShootoutResult:
    winner: str                 # "team_a" | "team_b"
    score: dict[str, int]       # goals made per team
    kicks: tuple[ShootoutKick, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "kicks", tuple(self.kicks))


def _eligible_takers(players: dict[str, dict], team: str) -> list[str]:
    """Player IDs for `team`, on-field, ordered by penalty rating (best first).

    Deterministic tie-break by player_id so equal ratings order stably.
    """
    candidates = []
    for pid in sorted(players):
        p = players[pid]
        if not isinstance(p, dict) or p.get("team") != team:
            continue
        if p.get("sent_off", False) is True:
            continue
        rating = p.get("penalty", p.get("shooting", p.get("skill", 10)))
        if not isinstance(rating, (int, float)):
            rating = 10
        candidates.append((-float(rating), pid))
    candidates.sort()                       # best rating first, then pid asc
    return [pid for _, pid in candidates]


def _gk_save(players: dict[str, dict], team: str) -> float | None:
    """Save rating of `team`'s on-field GK, or None if no keeper available."""
    for pid in sorted(players):
        p = players[pid]
        if (isinstance(p, dict) and p.get("team") == team
                and p.get("role") == "GK" and p.get("sent_off", False) is not True):
            rating = p.get("save", 10)
            return float(rating) if isinstance(rating, (int, float)) else 10.0
    return None


def _p_goal(taker_penalty: float, gk_save: float | None, knobs: ShootoutKnobs) -> float:
    if gk_save is None:
        return 1.0                          # Law 14: no keeper, nothing to beat
    val = (knobs.base + knobs.per_point * taker_penalty
           - knobs.save_per_point * (gk_save - 10.0))
    return max(0.0, min(1.0, val))


def _remaining(kicks_taken: int) -> int:
    """Kicks left for a side within the best-of-5 phase (5 each)."""
    return max(0, 5 - kicks_taken)


def resolve_shootout(
    team_a_players: dict[str, dict],
    team_b_players: dict[str, dict],
    seed: int,
    knobs: ShootoutKnobs,
) -> ShootoutResult:
    takers = {
        "team_a": _eligible_takers(team_a_players, "team_a"),
        "team_b": _eligible_takers(team_b_players, "team_b"),
    }
    gk_save = {
        "team_a": _gk_save(team_a_players, "team_a"),   # save rating of team_a's GK (faced when team_b attacks)
        "team_b": _gk_save(team_b_players, "team_b"),   # save rating of team_b's GK (faced when team_a attacks)
    }
    # Penalty rating lookup keyed by taker id.
    def _rating(team: str, pid: str) -> float:
        players = team_a_players if team == "team_a" else team_b_players
        p = players.get(pid, {})
        r = p.get("penalty", p.get("shooting", p.get("skill", 10)))
        return float(r) if isinstance(r, (int, float)) else 10.0

    score = {"team_a": 0, "team_b": 0}
    taken = {"team_a": 0, "team_b": 0}
    kicks: list[ShootoutKick] = []
    order = 0

    def _take(team: str) -> None:
        nonlocal order
        pool = takers[team]
        if not pool:
            # Degenerate: no eligible taker → counts as a miss, advance count.
            taken[team] += 1
            return
        taker_id = pool[taken[team] % len(pool)]   # cycle for sudden death
        opp = "team_b" if team == "team_a" else "team_a"
        pg = _p_goal(_rating(team, taker_id), gk_save[opp], knobs)
        scored = hash_01(seed, order, taker_id, "shootout") < pg
        kicks.append(ShootoutKick(order=order, team=team, taker_id=taker_id,
                                  p_goal=pg, scored=scored))
        if scored:
            score[team] += 1
        taken[team] += 1
        order += 1

    def _clinched() -> bool:
        # Decided if one side's goals exceed the other's max possible remaining.
        a_max = score["team_a"] + _remaining(taken["team_a"])
        b_max = score["team_b"] + _remaining(taken["team_b"])
        return score["team_a"] > b_max or score["team_b"] > a_max

    # Best-of-5, alternating, with early-clinch after every kick.
    while (taken["team_a"] < 5 or taken["team_b"] < 5):
        team = "team_a" if taken["team_a"] <= taken["team_b"] else "team_b"
        _take(team)
        if _clinched():
            winner = "team_a" if score["team_a"] > score["team_b"] else "team_b"
            return ShootoutResult(winner=winner, score=score, kicks=kicks)

    # Sudden death: equal pairs until someone leads after both have kicked.
    # Capped at _MAX_SUDDEN_DEATH_PAIRS to avoid infinite loop when p_goal=0.0
    # for all takers (e.g. extreme knob/save values).
    for _sd_pair in range(_MAX_SUDDEN_DEATH_PAIRS):
        _take("team_a")
        _take("team_b")
        if score["team_a"] != score["team_b"]:
            winner = "team_a" if score["team_a"] > score["team_b"] else "team_b"
            return ShootoutResult(winner=winner, score=score, kicks=kicks)
    # Cap reached: still level — resolve deterministically without new RNG.
    winner = "team_a" if hash_01(seed, 0, "shootout_sudden_death_cap") < 0.5 else "team_b"
    return ShootoutResult(winner=winner, score=score, kicks=kicks)


__all__ = ["ShootoutKnobs", "ShootoutKick", "ShootoutResult", "resolve_shootout"]
