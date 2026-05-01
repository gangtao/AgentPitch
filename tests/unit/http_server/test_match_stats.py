"""Unit tests for match_stats.compute_match_stats().

Tests follow TDD: written before the implementation.
Each test covers one behaviour; all use synthetic in-memory fixtures.
"""
import math
import pytest

from src.api.http_server.match_stats import compute_match_stats


# ── Fixtures ─────────────────────────────────────────────────────────────────

def _tick(tick_num, ball_possession=None, player_positions=None, actions=None):
    """Minimal tick record matching the events.jsonl shape."""
    return {
        "tick": tick_num,
        "ball_position": [50.0, 30.0],
        "ball_possession": ball_possession,
        "score": {"team_a": 0, "team_b": 0},
        "player_positions": player_positions or {},
        "actions": actions or [],
        "is_key_event": False,
        "event_type": None,
    }


def _action(player_id, team, action, result="ok", details=None):
    """Minimal action record matching the events.jsonl actions[] shape."""
    return {
        "player_id": player_id,
        "team": team,
        "action": action,
        "result": result,
        "details": details or {},
    }


def _meta(team_a=None, team_b=None):
    """Minimal meta.json dict."""
    return {
        "match_id": "test-match",
        "final_score": {"team_a": 0, "team_b": 0},
        "teams": {
            "team_a": team_a or [
                {"player_id": "team_a_0", "number": 1, "role": "GK"},
                {"player_id": "team_a_1", "number": 2, "role": "FWD"},
            ],
            "team_b": team_b or [
                {"player_id": "team_b_0", "number": 1, "role": "GK"},
                {"player_id": "team_b_1", "number": 2, "role": "DEF"},
            ],
        },
    }


# ── Return shape ──────────────────────────────────────────────────────────────

def test_compute_match_stats_returns_expected_top_level_keys():
    stats = compute_match_stats([], _meta())
    assert "match_id" in stats
    assert "teams" in stats
    assert "players" in stats


def test_compute_match_stats_team_keys_present():
    stats = compute_match_stats([], _meta())
    assert "team_a" in stats["teams"]
    assert "team_b" in stats["teams"]


def test_compute_match_stats_player_keys_from_meta():
    stats = compute_match_stats([], _meta())
    assert "team_a_0" in stats["players"]
    assert "team_a_1" in stats["players"]
    assert "team_b_0" in stats["players"]
    assert "team_b_1" in stats["players"]


# ── Possession ────────────────────────────────────────────────────────────────

def test_compute_match_stats_possession_equal_split():
    events = [
        _tick(0, ball_possession="team_a"),
        _tick(1, ball_possession="team_b"),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["possession_pct"] == pytest.approx(50.0)
    assert stats["teams"]["team_b"]["possession_pct"] == pytest.approx(50.0)


def test_compute_match_stats_possession_team_a_leads():
    events = [
        _tick(0, ball_possession="team_a"),
        _tick(1, ball_possession="team_a"),
        _tick(2, ball_possession="team_b"),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["possession_pct"] == pytest.approx(100 * 2 / 3, rel=1e-3)
    assert stats["teams"]["team_b"]["possession_pct"] == pytest.approx(100 * 1 / 3, rel=1e-3)


def test_compute_match_stats_possession_null_ticks_excluded():
    events = [
        _tick(0, ball_possession="team_a"),
        _tick(1, ball_possession=None),   # contested/loose — excluded from denominator
        _tick(2, ball_possession="team_a"),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["possession_pct"] == pytest.approx(100.0)


def test_compute_match_stats_possession_all_null_defaults_to_fifty():
    events = [_tick(0, ball_possession=None), _tick(1, ball_possession=None)]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["possession_pct"] == pytest.approx(50.0)
    assert stats["teams"]["team_b"]["possession_pct"] == pytest.approx(50.0)


# ── Goals ─────────────────────────────────────────────────────────────────────
# Goals are recorded on the GK's action record via details.goal_scored (which
# team scored) and details.scored_by (scorer player_id). The shoot action
# itself always has result="ok" — outcome lives on the GK record, not the shooter.

def test_compute_match_stats_goal_counted_from_gk_record():
    # team_b scores; recorded on team_a's GK (team_a_0), scored by team_b_1
    events = [
        _tick(0, actions=[
            _action("team_a_0", "team_a", "move", details={
                "goalkeeper_save": "failed",
                "goal_scored": "team_b",
                "scored_by": "team_b_1",
            }),
        ]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_b"]["goals"] == 1
    assert stats["teams"]["team_a"]["goals"] == 0
    assert stats["players"]["team_b_1"]["goals"] == 1
    assert stats["players"]["team_a_0"]["goals"] == 0


def test_compute_match_stats_multiple_goals_accumulated():
    # team_a scores twice (on team_b's GK), team_b scores once (on team_a's GK)
    events = [
        _tick(0, actions=[_action("team_b_0", "team_b", "move", details={
            "goalkeeper_save": "failed", "goal_scored": "team_a", "scored_by": "team_a_1"})]),
        _tick(1, actions=[_action("team_b_0", "team_b", "move", details={
            "goalkeeper_save": "failed", "goal_scored": "team_a", "scored_by": "team_a_1"})]),
        _tick(2, actions=[_action("team_a_0", "team_a", "move", details={
            "goalkeeper_save": "failed", "goal_scored": "team_b", "scored_by": "team_b_1"})]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["goals"] == 2
    assert stats["teams"]["team_b"]["goals"] == 1


# ── Shots & shots on target ───────────────────────────────────────────────────
# Shoot actions always have result="ok". Outcome (on-target, goal) is inferred
# from the GK's record: goalkeeper_save present = on target, goal_scored = goal.

def test_compute_match_stats_shots_total_from_shoot_actions():
    events = [
        _tick(0, actions=[
            _action("team_a_1", "team_a", "Shoot"),   # PascalCase as in real data
            _action("team_b_1", "team_b", "Shoot"),
        ]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["shots"] == 1
    assert stats["teams"]["team_b"]["shots"] == 1


def test_compute_match_stats_shots_on_target_from_gk_record():
    # team_b shot saved (on target), team_a shot scored (on target via goal), team_b shot missed (not on target)
    events = [
        # team_b shot → team_a GK saves it (caught): team_b gets shot_on_target
        _tick(0, actions=[_action("team_a_0", "team_a", "move", details={
            "goalkeeper_save": "success", "saved_from": "team_b_1"})]),
        # team_b shot → team_a GK parried (blocked): team_b gets shot_on_target
        _tick(1, actions=[_action("team_a_0", "team_a", "move", details={
            "goalkeeper_save": "blocked", "saved_from": "team_b_1"})]),
        # team_b scored → team_b gets goal AND shot_on_target
        _tick(2, actions=[_action("team_a_0", "team_a", "move", details={
            "goalkeeper_save": "failed", "goal_scored": "team_b", "scored_by": "team_b_1"})]),
        # team_a Shoot with no GK reaction = missed/blocked before GK, not on target
        _tick(3, actions=[_action("team_a_1", "team_a", "Shoot")]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_b"]["shots_on_target"] == 3   # 2 saves + 1 goal
    assert stats["teams"]["team_a"]["shots_on_target"] == 0   # missed
    assert stats["players"]["team_b_1"]["shots_on_target"] == 3


# ── Passes ────────────────────────────────────────────────────────────────────

def test_compute_match_stats_passes_attempted_per_team():
    events = [
        _tick(0, actions=[
            _action("team_a_1", "team_a", "pass"),
            _action("team_a_1", "team_a", "pass"),
            _action("team_b_1", "team_b", "pass"),
        ]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["passes_attempted"] == 2
    assert stats["teams"]["team_b"]["passes_attempted"] == 1
    assert stats["players"]["team_a_1"]["passes_attempted"] == 2


# ── Tackles ───────────────────────────────────────────────────────────────────

def test_compute_match_stats_tackles_attempted_and_successful():
    events = [
        _tick(0, actions=[
            _action("team_a_1", "team_a", "tackle", result="controlled"),
            _action("team_a_1", "team_a", "tackle", result="failed"),
            _action("team_b_1", "team_b", "tackle", result="controlled"),
        ]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["tackles_attempted"] == 2
    assert stats["teams"]["team_a"]["tackles_successful"] == 1
    assert stats["teams"]["team_b"]["tackles_attempted"] == 1
    assert stats["teams"]["team_b"]["tackles_successful"] == 1
    assert stats["players"]["team_a_1"]["tackles_attempted"] == 2
    assert stats["players"]["team_a_1"]["tackles_successful"] == 1


# ── Dribbles ──────────────────────────────────────────────────────────────────

def test_compute_match_stats_dribbles_from_move_details():
    events = [
        _tick(0, actions=[
            _action("team_a_1", "team_a", "move", details={"dribble_result": "success"}),
            _action("team_a_1", "team_a", "move", details={"dribble_result": "failed"}),
            _action("team_a_0", "team_a", "move", details={}),  # plain move — not a dribble
        ]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["dribbles_attempted"] == 2
    assert stats["teams"]["team_a"]["dribbles_successful"] == 1
    assert stats["players"]["team_a_1"]["dribbles_attempted"] == 2
    assert stats["players"]["team_a_1"]["dribbles_successful"] == 1
    assert stats["players"]["team_a_0"]["dribbles_attempted"] == 0


# ── Callback failures ─────────────────────────────────────────────────────────

def test_compute_match_stats_callback_failures_from_fallback_substituted():
    events = [
        _tick(0, actions=[
            _action("team_a_1", "team_a", "hold", details={"fallback_substituted": True}),
            _action("team_a_0", "team_a", "hold", details={}),  # normal hold — not a failure
            _action("team_b_1", "team_b", "hold", details={"fallback_substituted": True}),
        ]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["callback_failures"] == 1
    assert stats["teams"]["team_b"]["callback_failures"] == 1
    assert stats["players"]["team_a_1"]["callback_failures"] == 1
    assert stats["players"]["team_a_0"]["callback_failures"] == 0


# ── GK saves ──────────────────────────────────────────────────────────────────

def test_compute_match_stats_gk_saves_caught_and_parried():
    events = [
        _tick(0, actions=[
            _action("team_a_0", "team_a", "hold", details={"goalkeeper_save": "success"}),
            _action("team_a_0", "team_a", "hold", details={"goalkeeper_save": "blocked"}),
        ]),
        _tick(1, actions=[
            _action("team_b_0", "team_b", "hold", details={"goalkeeper_save": "success"}),
        ]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["gk_saves_caught"] == 1
    assert stats["teams"]["team_a"]["gk_saves_parried"] == 1
    assert stats["teams"]["team_b"]["gk_saves_caught"] == 1
    assert stats["teams"]["team_b"]["gk_saves_parried"] == 0
    assert stats["players"]["team_a_0"]["gk_saves_caught"] == 1
    assert stats["players"]["team_a_0"]["gk_saves_parried"] == 1
    assert stats["players"]["team_b_0"]["gk_saves_caught"] == 1


# ── OOB restarts ─────────────────────────────────────────────────────────────

def test_compute_match_stats_oob_restarts_counted_by_type():
    events = [
        _tick(0, actions=[
            _action("system", "system", "system", details={
                "out_of_bounds": True,
                "restart_type": "corner_kick",
                "restart_team": "team_a",
            }),
        ]),
        _tick(1, actions=[
            _action("system", "system", "system", details={
                "out_of_bounds": True,
                "restart_type": "throw_in",
                "restart_team": "team_b",
            }),
        ]),
        _tick(2, actions=[
            _action("system", "system", "system", details={
                "out_of_bounds": True,
                "restart_type": "goal_kick",
                "restart_team": "team_a",
            }),
        ]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["oob_corners"] == 1
    assert stats["teams"]["team_a"]["oob_goal_kicks"] == 1
    assert stats["teams"]["team_a"]["oob_throw_ins"] == 0
    assert stats["teams"]["team_b"]["oob_throw_ins"] == 1
    assert stats["teams"]["team_b"]["oob_corners"] == 0


# ── Distance run ─────────────────────────────────────────────────────────────

def test_compute_match_stats_distance_run_accumulated_across_ticks():
    events = [
        _tick(0, player_positions={"team_a_0": [0.0, 0.0]}),
        _tick(1, player_positions={"team_a_0": [3.0, 4.0]}),   # distance = 5.0
        _tick(2, player_positions={"team_a_0": [3.0, 4.0]}),   # no movement = 0.0
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["players"]["team_a_0"]["distance_run"] == pytest.approx(5.0)


def test_compute_match_stats_distance_run_first_tick_zero():
    events = [_tick(0, player_positions={"team_a_0": [10.0, 20.0]})]
    stats = compute_match_stats(events, _meta())
    assert stats["players"]["team_a_0"]["distance_run"] == pytest.approx(0.0)


def test_compute_match_stats_distance_run_per_player_independent():
    events = [
        _tick(0, player_positions={"team_a_0": [0.0, 0.0], "team_b_0": [50.0, 50.0]}),
        _tick(1, player_positions={"team_a_0": [3.0, 4.0], "team_b_0": [50.0, 50.0]}),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["players"]["team_a_0"]["distance_run"] == pytest.approx(5.0)
    assert stats["players"]["team_b_0"]["distance_run"] == pytest.approx(0.0)


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_compute_match_stats_empty_events_returns_zeros():
    stats = compute_match_stats([], _meta())
    assert stats["teams"]["team_a"]["goals"] == 0
    assert stats["teams"]["team_a"]["shots"] == 0
    assert stats["teams"]["team_a"]["possession_pct"] == pytest.approx(50.0)


def test_compute_match_stats_match_id_propagated():
    meta = _meta()
    meta["match_id"] = "my-match-001"
    stats = compute_match_stats([], meta)
    assert stats["match_id"] == "my-match-001"


def test_compute_match_stats_player_role_in_output():
    stats = compute_match_stats([], _meta())
    assert stats["players"]["team_a_0"]["role"] == "GK"
    assert stats["players"]["team_a_1"]["role"] == "FWD"
    assert stats["players"]["team_b_1"]["role"] == "DEF"


def test_compute_match_stats_unknown_player_in_positions_ignored():
    """Player in player_positions but not in meta['teams'] doesn't crash."""
    events = [
        _tick(0, player_positions={"ghost_player": [10.0, 10.0]}),
        _tick(1, player_positions={"ghost_player": [20.0, 10.0]}),
    ]
    stats = compute_match_stats(events, _meta())
    assert "ghost_player" not in stats["players"]


def test_compute_match_stats_missing_details_field_does_not_crash():
    events = [
        _tick(0, actions=[{"player_id": "team_a_1", "team": "team_a", "action": "hold", "result": "ok"}]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["callback_failures"] == 0
