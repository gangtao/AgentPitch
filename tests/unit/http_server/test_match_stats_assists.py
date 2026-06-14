"""Unit tests for assist attribution in match_stats.compute_match_stats() (issue #47).

An assist is credited to the player who made the last completed pass to the
goalscorer, when the goal comes directly off that pass with no intervening
ball-touch (tackle, dribble, opponent possession, save, or restart). Many goals
have NO assist — penalties, solo dribbles, rebounds, won-possession, etc.

Data model notes (verified against real events.jsonl):
  - A goal is recorded on the OPPONENT GK's action record via
    details.goal_scored (scoring team) + details.scored_by (scorer pid). The
    GK record's goalkeeper_save is "failed" for a conceded goal.
  - The scorer's Shoot action appears on an EARLIER tick; the ball then travels.
  - Passes carry no receiver id — the receiver is whoever next touches the ball.

Tests follow TDD: written before the implementation.
"""
import pytest

from src.api.http_server.match_stats import compute_match_stats


# ── Fixtures ─────────────────────────────────────────────────────────────────

def _tick(tick_num, ball_possession=None, player_positions=None, actions=None):
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
    return {
        "player_id": player_id,
        "team": team,
        "action": action,
        "result": result,
        "details": details or {},
    }


def _goal(scorer, scoring_team, gk_player="team_b_0", gk_team="team_b"):
    """A conceded-goal record as written on the opponent GK's action."""
    return _action(gk_player, gk_team, "Move", result="ok", details={
        "goalkeeper_save": "failed",
        "goal_scored": scoring_team,
        "scored_by": scorer,
    })


def _meta():
    """team_a has GK + two outfield players (passer + shooter); team_b has GK + DEF."""
    return {
        "match_id": "assist-test",
        "final_score": {"team_a": 0, "team_b": 0},
        "teams": {
            "team_a": [
                {"player_id": "team_a_0", "number": 1, "role": "GK"},
                {"player_id": "team_a_1", "number": 9, "role": "FWD"},
                {"player_id": "team_a_2", "number": 10, "role": "MID"},
            ],
            "team_b": [
                {"player_id": "team_b_0", "number": 1, "role": "GK"},
                {"player_id": "team_b_1", "number": 4, "role": "DEF"},
            ],
        },
    }


# ── Default / shape ───────────────────────────────────────────────────────────

def test_assists_zero_by_default():
    stats = compute_match_stats([], _meta())
    assert stats["teams"]["team_a"]["assists"] == 0
    assert stats["teams"]["team_b"]["assists"] == 0
    assert stats["players"]["team_a_1"]["assists"] == 0


# ── The happy path ────────────────────────────────────────────────────────────

def test_assist_credited_for_direct_pass_then_goal():
    events = [
        _tick(0, actions=[_action("team_a_2", "team_a", "Pass")]),
        _tick(1, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(2, actions=[_goal("team_a_1", "team_a")]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["assists"] == 1
    assert stats["players"]["team_a_2"]["assists"] == 1   # passer
    assert stats["players"]["team_a_1"]["assists"] == 0   # scorer, not assister


def test_assist_credited_to_last_passer_only():
    # Two passes precede the shot — only the LAST passer (team_a_2) assists.
    events = [
        _tick(0, actions=[_action("team_a_0", "team_a", "Pass")]),
        _tick(1, actions=[_action("team_a_2", "team_a", "Pass")]),
        _tick(2, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(3, actions=[_goal("team_a_1", "team_a")]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["assists"] == 1
    assert stats["players"]["team_a_2"]["assists"] == 1
    assert stats["players"]["team_a_0"]["assists"] == 0


# ── Goals with NO assist ──────────────────────────────────────────────────────

def test_no_assist_for_solo_goal_no_pass():
    events = [
        _tick(0, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(1, actions=[_goal("team_a_1", "team_a")]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["goals"] == 1
    assert stats["teams"]["team_a"]["assists"] == 0


def test_no_assist_when_scorer_dribbles_after_the_pass():
    # Pass → scorer dribbles (takes the ball himself) → shoots: not a direct assist.
    events = [
        _tick(0, actions=[_action("team_a_2", "team_a", "Pass")]),
        _tick(1, actions=[_action("team_a_1", "team_a", "Move", details={"dribble_result": "success"})]),
        _tick(2, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(3, actions=[_goal("team_a_1", "team_a")]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["assists"] == 0


def test_no_self_assist_when_passer_is_scorer():
    events = [
        _tick(0, actions=[_action("team_a_1", "team_a", "Pass")]),
        _tick(1, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(2, actions=[_goal("team_a_1", "team_a")]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["assists"] == 0


def test_no_assist_for_penalty_goal():
    # Penalty goal is recorded via the foul branch (issue #38), not a Shoot chain.
    events = [
        _tick(0, actions=[_action("team_a_2", "team_a", "Pass")]),  # an earlier pass that must NOT carry over
        _tick(1, actions=[_action("system", "system", "system", details={
            "foul": True,
            "offender_id": "team_b_1",
            "restart_type": "penalty_kick",
            "restart_team": "team_a",
            "penalty_outcome": "goal",
            "scored_by": "team_a_1",
        })]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["penalties_scored"] == 1
    assert stats["teams"]["team_a"]["goals"] == 1
    assert stats["teams"]["team_a"]["assists"] == 0


def test_no_assist_when_tackle_breaks_the_chain():
    # Pass → opponent contests (tackle) → scorer shoots: won-possession, no assist.
    events = [
        _tick(0, actions=[_action("team_a_2", "team_a", "Pass")]),
        _tick(1, actions=[_action("team_b_1", "team_b", "Tackle", result="failed")]),
        _tick(2, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(3, actions=[_goal("team_a_1", "team_a")]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["assists"] == 0


def test_out_of_range_tackle_does_not_break_the_chain():
    # An out_of_range tackle is a no-op (never touched the ball) — assist survives.
    events = [
        _tick(0, actions=[_action("team_a_2", "team_a", "Pass")]),
        _tick(1, actions=[_action("team_b_1", "team_b", "Tackle", result="out_of_range")]),
        _tick(2, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(3, actions=[_goal("team_a_1", "team_a")]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["assists"] == 1
    assert stats["players"]["team_a_2"]["assists"] == 1


def test_no_assist_when_opponent_possession_breaks_the_chain():
    events = [
        _tick(0, actions=[_action("team_a_2", "team_a", "Pass")]),
        _tick(1, actions=[_action("team_b_1", "team_b", "Pass")]),  # opponent now has it
        _tick(2, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(3, actions=[_goal("team_a_1", "team_a")]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["assists"] == 0


def test_no_assist_carried_over_from_an_earlier_saved_shot():
    # First shot is solo and saved; only the SECOND (assisted) goal should count.
    events = [
        _tick(0, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(1, actions=[_action("team_b_0", "team_b", "Move", details={
            "goalkeeper_save": "success", "saved_from": "team_a_1"})]),
        _tick(2, actions=[_action("team_a_2", "team_a", "Pass")]),
        _tick(3, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(4, actions=[_goal("team_a_1", "team_a")]),
    ]
    stats = compute_match_stats(events, _meta())
    assert stats["teams"]["team_a"]["assists"] == 1
    assert stats["players"]["team_a_2"]["assists"] == 1


# ── Invariants ────────────────────────────────────────────────────────────────

def test_assists_never_exceed_goals_and_sum_matches_team():
    events = [
        # Assisted goal for team_a (team_a_2 → team_a_1)
        _tick(0, actions=[_action("team_a_2", "team_a", "Pass")]),
        _tick(1, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(2, actions=[_goal("team_a_1", "team_a")]),
        # Solo goal for team_a (no assist)
        _tick(3, actions=[_action("team_a_1", "team_a", "Shoot")]),
        _tick(4, actions=[_goal("team_a_1", "team_a")]),
    ]
    stats = compute_match_stats(events, _meta())
    team = stats["teams"]["team_a"]
    assert team["goals"] == 2
    assert team["assists"] == 1
    assert team["assists"] <= team["goals"]
    player_sum = sum(p["assists"] for p in stats["players"].values() if p["team"] == "team_a")
    assert player_sum == team["assists"]
