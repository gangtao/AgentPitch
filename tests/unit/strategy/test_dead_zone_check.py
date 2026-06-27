"""Unit tests for the zero-shot dead-zone detector (issue #71).

`detect_dead_zone` flags any team that held a meaningful share of possession yet
logged near-zero shots — the symptom of the positional dead zone documented in
the issue. It operates on the `teams` block produced by
`src.api.http_server.match_stats.compute_match_stats`.
"""

from __future__ import annotations

import pytest

from src.strategy.dead_zone_check import detect_dead_zone


def _teams(a_poss, a_shots, b_poss, b_shots,
           a_name="Team A", b_name="Team B"):
    """Build a minimal `teams` block in compute_match_stats shape."""
    return {
        "team_a": {"team_id": "team_a", "name": a_name,
                   "possession_pct": a_poss, "shots": a_shots},
        "team_b": {"team_id": "team_b", "name": b_name,
                   "possession_pct": b_poss, "shots": b_shots},
    }


# ── Issue table cases (default thresholds: possession>=45, shots<=3) ──────────

@pytest.mark.parametrize("poss,shots", [
    (70.0, 3),   # Japan, Day 16
    (51.0, 2),   # New Zealand, Day 17
    (52.0, 0),   # Croatia, Day 17
    (45.0, 0),   # Scotland, Day 15 (possession exactly on the boundary)
    (89.7, 0),   # real logged match observed in data/matches
])
def test_flags_high_possession_low_shots(poss, shots):
    flags = detect_dead_zone(_teams(poss, shots, 100 - poss, 12))
    assert [f["slot"] for f in flags] == ["team_a"]
    assert flags[0]["possession_pct"] == poss
    assert flags[0]["shots"] == shots


def test_haiti_style_low_possession_is_not_flagged():
    # Haiti 36% / 0 shots — below the possession gate, a genuinely dominated
    # side is expected to barely shoot, so it must NOT be flagged by default.
    flags = detect_dead_zone(_teams(36.0, 0, 64.0, 15))
    assert flags == []


def test_healthy_team_not_flagged():
    # Plenty of possession AND plenty of shots — no dead zone.
    flags = detect_dead_zone(_teams(60.0, 12, 40.0, 8))
    assert flags == []


# ── Boundary behaviour ───────────────────────────────────────────────────────

def test_shots_boundary_is_inclusive():
    assert detect_dead_zone(_teams(60.0, 3, 40.0, 9))  # shots==max → flagged
    assert not detect_dead_zone(_teams(60.0, 4, 40.0, 9))  # shots>max → clear


def test_possession_boundary_is_inclusive():
    assert detect_dead_zone(_teams(45.0, 1, 55.0, 9))  # poss==min → flagged
    assert not detect_dead_zone(_teams(44.9, 1, 55.1, 9))  # poss<min → clear


# ── Both teams / custom thresholds ───────────────────────────────────────────

def test_both_teams_can_be_flagged():
    flags = detect_dead_zone(_teams(50.0, 1, 50.0, 2))
    assert sorted(f["slot"] for f in flags) == ["team_a", "team_b"]


def test_custom_thresholds():
    # Tighten: only flag teams with >=60% possession and <=1 shot.
    teams = _teams(55.0, 1, 65.0, 1)
    flags = detect_dead_zone(teams, possession_min=60.0, shots_max=1)
    assert [f["slot"] for f in flags] == ["team_b"]


def test_flag_carries_team_name():
    flags = detect_dead_zone(_teams(70.0, 1, 30.0, 9, a_name="Brazil"))
    assert flags[0]["name"] == "Brazil"
    assert flags[0]["team_id"] == "team_a"


def test_missing_fields_default_safely():
    # A sparse/partial team block must not raise — treat missing as 0.
    flags = detect_dead_zone({"team_a": {}, "team_b": {}})
    assert flags == []
