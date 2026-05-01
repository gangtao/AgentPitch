"""Unit tests for league_metadata — schedule generation, standings, I/O."""
import json
import os
import pytest
from pathlib import Path
from src.league_metadata import (
    generate_schedule,
    compute_standings,
    read_league_json,
    write_league_json,
    list_leagues,
    league_dir,
    LEAGUE_DIR_PREFIX,
)


# ── Schedule generation ──────────────────────────────────────────────────────

def test_generate_schedule_4_teams_single_round_returns_6_matches():
    data = generate_schedule(4, ["a", "b", "c", "d"], "lg-test", num_rounds=1)
    total = sum(len(md["matches"]) for md in data["matchdays"])
    assert total == 6  # 4*(4-1)/2


def test_generate_schedule_4_teams_double_round_returns_12_matches():
    data = generate_schedule(4, ["a", "b", "c", "d"], "lg-test", num_rounds=2)
    total = sum(len(md["matches"]) for md in data["matchdays"])
    assert total == 12  # 4*(4-1)


def test_generate_schedule_6_teams_single_round_returns_15_matches():
    data = generate_schedule(6, ["a", "b", "c", "d", "e", "f"], "lg-test", num_rounds=1)
    total = sum(len(md["matches"]) for md in data["matchdays"])
    assert total == 15  # 6*5/2


def test_generate_schedule_single_round_each_pair_appears_once():
    strategies = ["a", "b", "c", "d"]
    data = generate_schedule(4, strategies, "lg-test", num_rounds=1)
    pairs = set()
    for md in data["matchdays"]:
        for m in md["matches"]:
            a = m["team_a_slot"]
            b = m["team_b_slot"]
            pair = (min(a, b), max(a, b))
            assert pair not in pairs, f"Duplicate pair {pair}"
            pairs.add(pair)
    # 4 teams → 6 unique pairs
    assert len(pairs) == 6


def test_generate_schedule_double_round_each_pair_appears_twice():
    strategies = ["a", "b", "c", "d"]
    data = generate_schedule(4, strategies, "lg-test", num_rounds=2)
    from collections import Counter
    pair_counter = Counter()
    for md in data["matchdays"]:
        for m in md["matches"]:
            a = m["team_a_slot"]
            b = m["team_b_slot"]
            pair_counter[(min(a, b), max(a, b))] += 1
    assert all(v == 2 for v in pair_counter.values())


def test_generate_schedule_no_match_has_same_team_on_both_sides():
    strategies = ["a", "b", "c", "d"]
    data = generate_schedule(4, strategies, "lg-test", num_rounds=1)
    for md in data["matchdays"]:
        for m in md["matches"]:
            assert m["team_a_slot"] != m["team_b_slot"]


def test_generate_schedule_odd_team_count_raises():
    with pytest.raises(ValueError, match="even"):
        generate_schedule(3, ["a", "b", "c"], "lg-test", num_rounds=1)


def test_generate_schedule_invalid_num_rounds_raises():
    with pytest.raises(ValueError, match="num_rounds"):
        generate_schedule(4, ["a", "b", "c", "d"], "lg-test", num_rounds=3)


def test_generate_schedule_match_slots_use_D_prefix_format():
    data = generate_schedule(4, ["a", "b", "c", "d"], "lg-test", num_rounds=1)
    for md in data["matchdays"]:
        dn = md["matchday_number"]
        for i, m in enumerate(md["matches"], start=1):
            assert m["match_slot"] == f"D{dn}M{i}"
            assert m["match_id"] == f"lg-test-D{dn}M{i}"


def test_generate_schedule_returns_pending_status_and_null_results():
    data = generate_schedule(4, ["a", "b", "c", "d"], "lg-test", num_rounds=1)
    assert data["status"] == "running"
    assert data["champion"] is None
    assert len(data["standings"]) == 4
    for md in data["matchdays"]:
        assert md["status"] == "pending"
        for m in md["matches"]:
            assert m["status"] == "pending"
            assert m["result"] is None
            assert m["final_score"] is None


# ── Standings computation ────────────────────────────────────────────────────

def test_compute_standings_win_gives_3_points():
    data = generate_schedule(4, ["a", "b", "c", "d"], "lg-test", num_rounds=1)
    first_match = data["matchdays"][0]["matches"][0]
    first_match["status"] = "complete"
    first_match["result"] = "team_a"
    first_match["final_score"] = {"team_a": 2, "team_b": 0}

    standings = compute_standings(data)
    winner_row = next(s for s in standings if s["slot"] == first_match["team_a_slot"])
    loser_row = next(s for s in standings if s["slot"] == first_match["team_b_slot"])
    assert winner_row["points"] == 3
    assert winner_row["won"] == 1
    assert loser_row["points"] == 0
    assert loser_row["lost"] == 1


def test_compute_standings_draw_gives_1_point_each():
    data = generate_schedule(4, ["a", "b", "c", "d"], "lg-test", num_rounds=1)
    first_match = data["matchdays"][0]["matches"][0]
    first_match["status"] = "complete"
    first_match["result"] = "draw"
    first_match["final_score"] = {"team_a": 1, "team_b": 1}

    standings = compute_standings(data)
    row_a = next(s for s in standings if s["slot"] == first_match["team_a_slot"])
    row_b = next(s for s in standings if s["slot"] == first_match["team_b_slot"])
    assert row_a["points"] == 1
    assert row_a["drawn"] == 1
    assert row_b["points"] == 1
    assert row_b["drawn"] == 1


def test_compute_standings_goal_difference():
    data = generate_schedule(4, ["a", "b", "c", "d"], "lg-test", num_rounds=1)
    first_match = data["matchdays"][0]["matches"][0]
    first_match["status"] = "complete"
    first_match["result"] = "team_a"
    first_match["final_score"] = {"team_a": 3, "team_b": 1}

    standings = compute_standings(data)
    winner_row = next(s for s in standings if s["slot"] == first_match["team_a_slot"])
    assert winner_row["goals_for"] == 3
    assert winner_row["goals_against"] == 1
    assert winner_row["goal_diff"] == 2


def test_compute_standings_rank_by_points():
    data = generate_schedule(4, ["a", "b", "c", "d"], "lg-test", num_rounds=1)
    first_match = data["matchdays"][0]["matches"][0]
    a_slot = first_match["team_a_slot"]
    first_match["status"] = "complete"
    first_match["result"] = "team_a"
    first_match["final_score"] = {"team_a": 2, "team_b": 0}

    standings = compute_standings(data)
    top = standings[0]
    assert top["slot"] == a_slot
    assert top["rank"] == 1


# ── I/O ─────────────────────────────────────────────────────────────────────

def test_write_then_read_league_json_returns_original_data(tmp_path):
    league_d = tmp_path / "league_test"
    league_d.mkdir()
    data = {"league_id": "test", "name": "Test League", "status": "running"}
    write_league_json(league_d, data)
    result = read_league_json(league_d)
    assert result == data


def test_write_league_json_leaves_no_tmp_file(tmp_path):
    league_d = tmp_path / "league_test"
    league_d.mkdir()
    data = {"league_id": "test", "status": "running"}
    write_league_json(league_d, data)
    assert not (league_d / "league.json.tmp").exists()
    assert (league_d / "league.json").exists()


def test_list_leagues_empty(tmp_path):
    result = list_leagues(tmp_path)
    assert result == []


def test_list_leagues_returns_summary(tmp_path):
    league_d = tmp_path / f"{LEAGUE_DIR_PREFIX}lg-001"
    league_d.mkdir()
    data = {
        "league_id": "lg-001",
        "name": "Test",
        "status": "complete",
        "config_name": "5v5",
        "num_rounds": 1,
        "created_iso": "2026-04-30T10:00:00Z",
        "completed_iso": "2026-04-30T11:00:00Z",
        "champion": "alpha",
        "teams": [{"slot": 1, "strategy_name": "alpha"}],
    }
    write_league_json(league_d, data)
    results = list_leagues(tmp_path)
    assert len(results) == 1
    assert results[0]["league_id"] == "lg-001"
    assert results[0]["champion"] == "alpha"
    assert "matchdays" not in results[0]


def test_league_dir_path(tmp_path):
    d = league_dir(tmp_path, "lg-001")
    assert d == tmp_path / f"{LEAGUE_DIR_PREFIX}lg-001"
