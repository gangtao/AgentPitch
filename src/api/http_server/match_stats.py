"""Match statistics computation for the HTTP API layer.

Computes per-team and per-player statistics from a completed match's
events.jsonl records and meta.json. Pure function: no filesystem I/O,
no simulation imports (ADR-0006 compliant).

Called by the GET /api/match/stats endpoint in app.py.
"""
from __future__ import annotations

import math
from typing import Any


def compute_match_stats(events: list[dict], meta: dict) -> dict:
    """Compute full match statistics from events.jsonl records and meta.json.

    Args:
        events: Parsed list of tick records from events.jsonl.
        meta: Parsed meta.json dict for the match.

    Returns:
        Dict with keys: match_id, teams (team_a/team_b stats), players (per-player stats).
    """
    roster = _build_roster(meta)
    team_stats = _empty_team_stats()
    player_stats = {pid: _empty_player_stats(info) for pid, info in roster.items()}

    poss_a = 0
    poss_b = 0
    prev_positions: dict[str, list[float]] = {}

    for tick in events:
        # Possession
        bp = tick.get("ball_possession")
        if bp == "team_a":
            poss_a += 1
        elif bp == "team_b":
            poss_b += 1

        # Distance run
        positions: dict[str, Any] = tick.get("player_positions") or {}
        for pid, pos in positions.items():
            if pid not in roster:
                continue
            if pid in prev_positions:
                prev = prev_positions[pid]
                dx = pos[0] - prev[0]
                dy = pos[1] - prev[1]
                player_stats[pid]["distance_run"] += math.hypot(dx, dy)
            prev_positions[pid] = pos

        # Actions
        for action_rec in tick.get("actions") or []:
            _process_action(action_rec, team_stats, player_stats, roster)

    # Compute possession percentages
    total_poss = poss_a + poss_b
    if total_poss > 0:
        team_stats["team_a"]["possession_pct"] = 100.0 * poss_a / total_poss
        team_stats["team_b"]["possession_pct"] = 100.0 * poss_b / total_poss

    # Round distance_run to 1 decimal
    for pstats in player_stats.values():
        pstats["distance_run"] = round(pstats["distance_run"], 1)

    # Surface team display names (team_id / name) from meta.teams.
    teams_meta = (meta or {}).get("teams") or {}
    for slot in ("team_a", "team_b"):
        td = teams_meta.get(slot)
        if isinstance(td, dict):
            team_stats[slot]["team_id"] = td.get("team_id") or slot
            team_stats[slot]["name"] = td.get("name") or _slot_default(slot)
        else:
            team_stats[slot]["team_id"] = slot
            team_stats[slot]["name"] = _slot_default(slot)

    return {
        "match_id": meta.get("match_id", ""),
        "teams": team_stats,
        "players": player_stats,
    }


def _slot_default(slot: str) -> str:
    return "Team A" if slot == "team_a" else "Team B"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_roster(meta: dict) -> dict[str, dict]:
    """Extract {player_id: {team, role, number}} from meta['teams'].

    Tolerates both meta shapes:
      - Legacy bare list: meta.teams.team_a = [{player_id, ...}, ...]
      - New dict shape:   meta.teams.team_a = {"team_id", "name", "roster": [...]}
    """
    roster: dict[str, dict] = {}
    for team_id, team_block in (meta.get("teams") or {}).items():
        if isinstance(team_block, list):
            players = team_block
        elif isinstance(team_block, dict):
            players = team_block.get("roster") or []
        else:
            players = []
        for p in players:
            pid = p.get("player_id")
            if pid:
                roster[pid] = {
                    "team": team_id,
                    "role": p.get("role", ""),
                    "number": p.get("number", 0),
                }
    return roster


def _empty_team_stats() -> dict[str, dict]:
    def _zeros():
        return {
            "possession_pct": 50.0,
            "goals": 0,
            "shots": 0,
            "shots_on_target": 0,
            "passes_attempted": 0,
            "tackles_attempted": 0,
            "tackles_successful": 0,
            "dribbles_attempted": 0,
            "dribbles_successful": 0,
            "callback_failures": 0,
            "oob_corners": 0,
            "oob_throw_ins": 0,
            "oob_goal_kicks": 0,
            "gk_saves_caught": 0,
            "gk_saves_parried": 0,
        }
    return {"team_a": _zeros(), "team_b": _zeros()}


def _empty_player_stats(info: dict) -> dict:
    return {
        "team": info["team"],
        "role": info["role"],
        "number": info["number"],
        "goals": 0,
        "shots": 0,
        "shots_on_target": 0,
        "passes_attempted": 0,
        "tackles_attempted": 0,
        "tackles_successful": 0,
        "dribbles_attempted": 0,
        "dribbles_successful": 0,
        "distance_run": 0.0,
        "gk_saves_caught": 0,
        "gk_saves_parried": 0,
        "callback_failures": 0,
    }


def _process_action(
    rec: dict,
    team_stats: dict[str, dict],
    player_stats: dict[str, dict],
    roster: dict[str, dict],
) -> None:
    """Update team and player counters for one action record."""
    pid = rec.get("player_id", "")
    team = rec.get("team", "")
    action = (rec.get("action") or "").lower()
    result = (rec.get("result") or "").lower()
    details: dict = rec.get("details") or {}

    ts = team_stats.get(team)
    ps = player_stats.get(pid)

    # OOB restart — keyed to the team that takes the restart
    if details.get("out_of_bounds"):
        restart_type = details.get("restart_type", "")
        restart_team = details.get("restart_team", "")
        rts = team_stats.get(restart_team)
        if rts is not None:
            if restart_type == "corner_kick":
                rts["oob_corners"] += 1
            elif restart_type == "throw_in":
                rts["oob_throw_ins"] += 1
            elif restart_type == "goal_kick":
                rts["oob_goal_kicks"] += 1
        return  # system record — skip other counters

    if ts is None and ps is None:
        return

    # Goals and shots-on-target — recorded on the GK's action record, not the shooter's.
    # details.goal_scored = team that scored; details.scored_by = scorer player_id.
    # details.goalkeeper_save = "success"|"blocked"|"failed"; saved_from = shooter pid.
    goal_scored_team = details.get("goal_scored")
    if goal_scored_team:
        scoring_ts = team_stats.get(goal_scored_team)
        if scoring_ts is not None:
            scoring_ts["goals"] += 1
            scoring_ts["shots_on_target"] += 1
        scorer_pid = details.get("scored_by", "")
        scoring_ps = player_stats.get(scorer_pid)
        if scoring_ps is not None:
            scoring_ps["goals"] += 1
            scoring_ps["shots_on_target"] += 1

    gk_save = details.get("goalkeeper_save")
    if gk_save in ("success", "blocked"):
        # Save — attribute shot_on_target to the shooting team (opponent of GK's team)
        shooter_pid = details.get("saved_from", "")
        shooter_ps = player_stats.get(shooter_pid)
        if shooter_ps is not None:
            shooter_team = shooter_ps["team"]
            team_stats[shooter_team]["shots_on_target"] += 1
            shooter_ps["shots_on_target"] += 1
        # GK save stats belong to the GK's team (the defending team = `team`)
        if gk_save == "success":
            if ts:
                ts["gk_saves_caught"] += 1
            if ps:
                ps["gk_saves_caught"] += 1
        else:
            if ts:
                ts["gk_saves_parried"] += 1
            if ps:
                ps["gk_saves_parried"] += 1

    # Callback failure: Hold injected by engine instead of player's intended action
    if action == "hold" and details.get("fallback_substituted"):
        if ts:
            ts["callback_failures"] += 1
        if ps:
            ps["callback_failures"] += 1

    if action == "shoot":
        if ts:
            ts["shots"] += 1
        if ps:
            ps["shots"] += 1

    elif action == "pass":
        if ts:
            ts["passes_attempted"] += 1
        if ps:
            ps["passes_attempted"] += 1

    elif action == "tackle":
        if ts:
            ts["tackles_attempted"] += 1
        if ps:
            ps["tackles_attempted"] += 1
        if result == "controlled":
            if ts:
                ts["tackles_successful"] += 1
            if ps:
                ps["tackles_successful"] += 1

    elif action == "move":
        dribble_result = details.get("dribble_result")
        if dribble_result is not None:
            if ts:
                ts["dribbles_attempted"] += 1
            if ps:
                ps["dribbles_attempted"] += 1
            if dribble_result == "success":
                if ts:
                    ts["dribbles_successful"] += 1
                if ps:
                    ps["dribbles_successful"] += 1
