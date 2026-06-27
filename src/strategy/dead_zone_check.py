"""Zero-shot dead-zone detector (issue #71).

A recurring simulation bug: a team holds a meaningful share of possession yet
logs near-zero shots for a whole match, because the generated `decide()` strategy
has a positional *dead zone* — its pass-first rule releases the ball before its
shoot gate ever fires (see session memory `agentpitch_zero_shot_dead_zone`).

Historically this was caught reactively, by hand, every match day. This module
turns the detection into a pure, reusable function so it can be run as a CLI
gate (`agent-pitch check-match`) or imported by the match-day report pipeline.

Layer-neutral: operates on the already-computed `teams` block returned by
`src.api.http_server.match_stats.compute_match_stats` and imports nothing from
the api/foundation engine layers.
"""

from __future__ import annotations

# Defaults match the issue's recommended thresholds. Teams below
# POSSESSION_MIN are intentionally not flagged — a genuinely dominated side is
# expected to barely shoot (e.g. Haiti 36% / 0 shots), so flagging it would be a
# false positive. The signal we want is "held the ball but didn't shoot".
DEFAULT_POSSESSION_MIN = 45.0
DEFAULT_SHOTS_MAX = 3

_SLOTS = ("team_a", "team_b")


def detect_dead_zone(
    teams: dict,
    *,
    possession_min: float = DEFAULT_POSSESSION_MIN,
    shots_max: int = DEFAULT_SHOTS_MAX,
) -> list[dict]:
    """Flag teams that held the ball but barely shot.

    Args:
        teams: The `teams` block from ``compute_match_stats(...)["teams"]`` —
            a dict keyed by "team_a"/"team_b", each with `possession_pct`,
            `shots`, `team_id`, and `name`.
        possession_min: Minimum possession percentage to consider a team
            "in control" enough that near-zero shots is anomalous.
        shots_max: A team is flagged when its shot count is at or below this.

    Returns:
        A list of flag dicts (in team_a, team_b order), one per flagged team:
        ``{"slot", "team_id", "name", "possession_pct", "shots"}``. Empty when
        no team trips the thresholds.
    """
    flags: list[dict] = []
    for slot in _SLOTS:
        ts = teams.get(slot) or {}
        possession = ts.get("possession_pct", 0.0) or 0.0
        shots = ts.get("shots", 0) or 0
        if possession >= possession_min and shots <= shots_max:
            flags.append({
                "slot": slot,
                "team_id": ts.get("team_id", slot),
                "name": ts.get("name", slot),
                "possession_pct": possession,
                "shots": shots,
            })
    return flags
