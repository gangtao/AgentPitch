"""Integration test for `agent-pitch check-match` (issue #71).

Drives the dead-zone gate end-to-end: synthesize a match dir (events.jsonl +
meta.json), compute stats via the real `compute_match_stats`, and assert the
runner flags the high-possession / zero-shot team with a non-zero exit code.
"""

from __future__ import annotations

import argparse
import json

import pytest

from src.orchestration.cli.check_runner import (
    _resolve_match_dirs,
    check_match_dir,
    run,
)


def _write_match(
    match_dir,
    *,
    a_poss_ticks: int,
    b_poss_ticks: int,
    a_shots: int,
    b_shots: int,
    a_name="Alpha",
    b_name="Beta",
):
    """Write a minimal events.jsonl + meta.json into match_dir."""
    match_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "match_id": match_dir.name.replace("match_", ""),
        "teams": {
            "team_a": {"team_id": "team_a", "name": a_name,
                       "roster": [{"player_id": "team_a_4", "role": "FWD", "number": 9}]},
            "team_b": {"team_id": "team_b", "name": b_name,
                       "roster": [{"player_id": "team_b_4", "role": "FWD", "number": 9}]},
        },
    }
    (match_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")

    lines = []
    tick = 0
    for _ in range(a_poss_ticks):
        lines.append({"tick": tick, "ball_possession": "team_a", "actions": []})
        tick += 1
    for _ in range(b_poss_ticks):
        lines.append({"tick": tick, "ball_possession": "team_b", "actions": []})
        tick += 1
    for _ in range(a_shots):
        lines.append({"tick": tick, "ball_possession": "team_a",
                      "actions": [{"player_id": "team_a_4", "team": "team_a",
                                   "action": "shoot", "result": "ok", "details": {}}]})
        tick += 1
    for _ in range(b_shots):
        lines.append({"tick": tick, "ball_possession": "team_b",
                      "actions": [{"player_id": "team_b_4", "team": "team_b",
                                   "action": "shoot", "result": "ok", "details": {}}]})
        tick += 1
    (match_dir / "events.jsonl").write_text(
        "\n".join(json.dumps(line) for line in lines) + "\n", encoding="utf-8"
    )


def _args(match_dirs, possession_min=45.0, shots_max=3):
    return argparse.Namespace(
        match_dir=[str(d) for d in match_dirs],
        possession_min=possession_min,
        shots_max=shots_max,
    )


def test_flags_dead_zone_and_exits_nonzero(tmp_path, capsys):
    match_dir = tmp_path / "match_deadzone"
    # team_a: ~90% possession, 0 shots; team_b: 17 shots.
    _write_match(match_dir, a_poss_ticks=90, b_poss_ticks=10,
                 a_shots=0, b_shots=17, a_name="Alpha")

    exit_code = run(_args([match_dir]))
    out = capsys.readouterr().out

    assert exit_code == 1
    assert "DEAD ZONE" in out
    assert "Alpha" in out
    assert "FAIL" in out


def test_healthy_match_passes(tmp_path, capsys):
    match_dir = tmp_path / "match_healthy"
    # Balanced possession, both teams shoot plenty.
    _write_match(match_dir, a_poss_ticks=50, b_poss_ticks=50,
                 a_shots=9, b_shots=8)

    exit_code = run(_args([match_dir]))
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "PASS" in out
    assert "DEAD ZONE" not in out


def test_check_match_dir_returns_flags(tmp_path):
    match_dir = tmp_path / "match_x"
    _write_match(match_dir, a_poss_ticks=80, b_poss_ticks=20,
                 a_shots=1, b_shots=10, a_name="Gamma")

    flags = check_match_dir(match_dir)
    assert [f["slot"] for f in flags] == ["team_a"]
    assert flags[0]["name"] == "Gamma"


def test_parent_dir_is_scanned_for_match_subdirs(tmp_path):
    _write_match(tmp_path / "match_one", a_poss_ticks=80, b_poss_ticks=20,
                 a_shots=0, b_shots=9)
    _write_match(tmp_path / "match_two", a_poss_ticks=50, b_poss_ticks=50,
                 a_shots=7, b_shots=7)
    resolved = _resolve_match_dirs([str(tmp_path)])
    assert [d.name for d in resolved] == ["match_one", "match_two"]


def test_missing_match_dir_errors(tmp_path, capsys):
    exit_code = run(_args([tmp_path / "does_not_exist"]))
    assert exit_code == 1
