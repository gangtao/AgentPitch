"""League metadata — data model, round-robin schedule, standings, I/O.

league.json schema:
{
  "league_id": "<id>",
  "name": "<display name>",
  "status": "running" | "complete" | "errored",
  "config_name": "<match config name>",
  "num_rounds": 1 | 2,
  "created_iso": "<ISO timestamp>",
  "completed_iso": null | "<ISO timestamp>",
  "champion": null | "<strategy_name>",
  "teams": [{"slot": 1, "strategy_name": "<name>"}, ...],
  "matchdays": [
    {
      "matchday_number": 1,
      "status": "pending" | "running" | "complete",
      "matches": [
        {
          "match_slot": "D1M1",
          "match_id": "<league_id>-D1M1",
          "team_a_slot": 1,
          "team_b_slot": 2,
          "status": "pending" | "running" | "complete",
          "result": "team_a" | "team_b" | "draw" | null,
          "final_score": {"team_a": N, "team_b": N} | null
        }
      ]
    }
  ],
  "standings": [
    {
      "slot": 1, "strategy_name": "<name>",
      "played": N, "won": N, "drawn": N, "lost": N,
      "goals_for": N, "goals_against": N, "goal_diff": N,
      "points": N, "rank": N
    }
  ]
}
"""
from __future__ import annotations

import json
import os
import random
from pathlib import Path

LEAGUE_DIR_PREFIX = "league_"


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def league_dir(leagues_dir: Path, league_id: str) -> Path:
    """Return the league directory path: leagues_dir / 'league_<league_id>'."""
    return leagues_dir / f"{LEAGUE_DIR_PREFIX}{league_id}"


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def read_league_json(league_d: Path) -> dict:
    """Read and return league.json as dict.

    Raises:
        FileNotFoundError: if league.json is absent.
        json.JSONDecodeError: if the file is malformed.
    """
    path = league_d / "league.json"
    return json.loads(path.read_text(encoding="utf-8"))


def write_league_json(league_d: Path, data: dict) -> None:
    """Atomically write league.json via os.replace.

    Writes to a temporary file first, then renames to the target path so
    concurrent readers never see a partial write.
    """
    target = league_d / "league.json"
    tmp = league_d / "league.json.tmp"
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, target)


def list_leagues(leagues_dir: Path) -> list[dict]:
    """Scan leagues_dir for league_* subdirectories, return summaries sorted by created_iso desc.

    Each returned dict contains summary fields: league_id, name, status, config_name,
    num_rounds, team_count, created_iso, completed_iso, champion.
    Directories missing or with malformed league.json are silently skipped.

    Returns an empty list if leagues_dir does not exist.
    """
    if not leagues_dir.exists():
        return []
    results = []
    try:
        for entry in leagues_dir.iterdir():
            if not entry.is_dir():
                continue
            if not entry.name.startswith(LEAGUE_DIR_PREFIX):
                continue
            try:
                data = read_league_json(entry)
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                continue
            summary = {
                "league_id":    data.get("league_id", entry.name.removeprefix(LEAGUE_DIR_PREFIX)),
                "name":         data.get("name", ""),
                "status":       data.get("status", ""),
                "config_name":  data.get("config_name", ""),
                "num_rounds":   data.get("num_rounds", 1),
                "team_count":   len(data.get("teams", [])),
                "created_iso":  data.get("created_iso", ""),
                "completed_iso": data.get("completed_iso"),
                "champion":     data.get("champion"),
            }
            results.append(summary)
    except (OSError, PermissionError):
        return []
    results.sort(key=lambda x: x["created_iso"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Schedule generation (circle method)
# ---------------------------------------------------------------------------

def _circle_method(slots: list[int]) -> list[list[tuple[int, int]]]:
    """Return matchday pairings using the circle method.

    Fixed slot at index 0; rotate the rest N-1 times to produce N-1 matchdays.
    Each matchday has N/2 matches.
    """
    n = len(slots)
    fixed = slots[0]
    rotating = list(slots[1:])
    matchdays = []
    for _ in range(n - 1):
        pairs = [(fixed, rotating[0])]
        for i in range(1, n // 2):
            pairs.append((rotating[i], rotating[n - 1 - i]))
        matchdays.append(pairs)
        # Rotate right: last element moves to front
        rotating = [rotating[-1]] + rotating[:-1]
    return matchdays


def generate_schedule(
    num_teams: int,
    strategies: list[str],
    league_id: str,
    num_rounds: int = 1,
) -> dict:
    """Build initial league.json dict.

    Args:
        num_teams: Must be even, 2-16.
        strategies: Strategy names, len must equal num_teams.
        league_id: Unique identifier (used as RNG seed for reproducible shuffling).
        num_rounds: 1 (single round-robin) or 2 (double round-robin).

    Returns:
        Complete league.json dict. Caller must set name, config_name, created_iso.

    Raises:
        ValueError: if num_teams is odd, or num_rounds not in {1, 2}, or len mismatch.
    """
    if num_teams % 2 != 0:
        raise ValueError(f"League requires an even number of teams; got {num_teams}")
    if num_rounds not in (1, 2):
        raise ValueError(f"num_rounds must be 1 or 2; got {num_rounds}")
    if len(strategies) != num_teams:
        raise ValueError(
            f"strategies length ({len(strategies)}) must equal num_teams ({num_teams})"
        )

    # Shuffle deterministically from league_id
    rng = random.Random(league_id)
    shuffled = list(strategies)
    rng.shuffle(shuffled)

    teams = [{"slot": i + 1, "strategy_name": shuffled[i]} for i in range(num_teams)]
    slot_list = [t["slot"] for t in teams]

    # Build matchday pairings via circle method
    round1_pairings = _circle_method(slot_list)

    all_pairings: list[list[tuple[int, int]]] = list(round1_pairings)
    if num_rounds == 2:
        # Second half: swap team_a/team_b so each pair plays home and away
        round2_pairings = [[(b, a) for (a, b) in day] for day in round1_pairings]
        all_pairings = list(round1_pairings) + round2_pairings

    matchdays = []
    for day_idx, day_pairs in enumerate(all_pairings, start=1):
        matches = []
        for match_idx, (a_slot, b_slot) in enumerate(day_pairs, start=1):
            match_slot = f"D{day_idx}M{match_idx}"
            matches.append({
                "match_slot":   match_slot,
                "match_id":     f"{league_id}-{match_slot}",
                "team_a_slot":  a_slot,
                "team_b_slot":  b_slot,
                "status":       "pending",
                "result":       None,
                "final_score":  None,
            })
        matchdays.append({
            "matchday_number": day_idx,
            "status":          "pending",
            "matches":         matches,
        })

    standings = _build_empty_standings(teams)

    return {
        "league_id":    league_id,
        "name":         "",
        "status":       "running",
        "config_name":  "",
        "num_rounds":   num_rounds,
        "created_iso":  None,
        "completed_iso": None,
        "champion":     None,
        "teams":        teams,
        "matchdays":    matchdays,
        "standings":    standings,
    }


# ---------------------------------------------------------------------------
# Standings computation
# ---------------------------------------------------------------------------

def _build_empty_standings(teams: list[dict]) -> list[dict]:
    return [
        {
            "slot":           t["slot"],
            "strategy_name":  t["strategy_name"],
            "played":         0,
            "won":            0,
            "drawn":          0,
            "lost":           0,
            "goals_for":      0,
            "goals_against":  0,
            "goal_diff":      0,
            "points":         0,
            "rank":           0,
        }
        for t in teams
    ]


def compute_standings(league_data: dict) -> list[dict]:
    """Recompute standings from all completed matches in league_data.

    Tiebreaker order: points -> goal_diff -> goals_for -> head-to-head points.
    Returns a new standings list (does not mutate league_data).
    """
    teams = league_data["teams"]
    rows: dict[int, dict] = {
        t["slot"]: {
            "slot":           t["slot"],
            "strategy_name":  t["strategy_name"],
            "played":         0,
            "won":            0,
            "drawn":          0,
            "lost":           0,
            "goals_for":      0,
            "goals_against":  0,
            "goal_diff":      0,
            "points":         0,
        }
        for t in teams
    }

    completed: list[dict] = []
    for md in league_data.get("matchdays", []):
        for m in md.get("matches", []):
            if m.get("status") == "complete" and m.get("result") is not None:
                completed.append(m)

    for m in completed:
        a = m.get("team_a_slot")
        b = m.get("team_b_slot")
        if a is None or b is None or a not in rows or b not in rows:
            continue
        score = m.get("final_score") or {}
        ga = score.get("team_a", 0)
        gb = score.get("team_b", 0)
        result = m["result"]

        rows[a]["played"] += 1
        rows[b]["played"] += 1
        rows[a]["goals_for"]     += ga
        rows[a]["goals_against"] += gb
        rows[b]["goals_for"]     += gb
        rows[b]["goals_against"] += ga

        if result == "team_a":
            rows[a]["won"] += 1
            rows[a]["points"] += 3
            rows[b]["lost"] += 1
        elif result == "team_b":
            rows[b]["won"] += 1
            rows[b]["points"] += 3
            rows[a]["lost"] += 1
        else:  # draw
            rows[a]["drawn"] += 1
            rows[a]["points"] += 1
            rows[b]["drawn"] += 1
            rows[b]["points"] += 1

    for row in rows.values():
        row["goal_diff"] = row["goals_for"] - row["goals_against"]

    sorted_rows = sorted(
        rows.values(),
        key=lambda r: (
            -r["points"],
            -r["goal_diff"],
            -r["goals_for"],
        ),
    )

    sorted_rows = _apply_head_to_head(sorted_rows, completed)

    for rank, row in enumerate(sorted_rows, start=1):
        row["rank"] = rank

    return sorted_rows


def _head_to_head_points(slot_a: int, slot_b: int, completed: list[dict]) -> int:
    pts = 0
    for m in completed:
        if m["team_a_slot"] == slot_a and m["team_b_slot"] == slot_b:
            if m["result"] == "team_a":
                pts += 3
            elif m["result"] == "draw":
                pts += 1
        elif m["team_a_slot"] == slot_b and m["team_b_slot"] == slot_a:
            if m["result"] == "team_b":
                pts += 3
            elif m["result"] == "draw":
                pts += 1
    return pts


def _apply_head_to_head(sorted_rows: list[dict], completed: list[dict]) -> list[dict]:
    result: list[dict] = []
    i = 0
    while i < len(sorted_rows):
        j = i + 1
        while j < len(sorted_rows) and (
            sorted_rows[j]["points"]    == sorted_rows[i]["points"] and
            sorted_rows[j]["goal_diff"] == sorted_rows[i]["goal_diff"] and
            sorted_rows[j]["goals_for"] == sorted_rows[i]["goals_for"]
        ):
            j += 1
        group = sorted_rows[i:j]
        if len(group) > 1:
            slots_in_group = {r["slot"] for r in group}
            group = sorted(
                group,
                key=lambda r: -sum(
                    _head_to_head_points(r["slot"], other, completed)
                    for other in slots_in_group
                    if other != r["slot"]
                ),
            )
        result.extend(group)
        i = j
    return result


__all__ = [
    "LEAGUE_DIR_PREFIX",
    "league_dir",
    "read_league_json",
    "write_league_json",
    "list_leagues",
    "generate_schedule",
    "compute_standings",
]
