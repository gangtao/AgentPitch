"""Issue #38 — match stats counters for fouls, cards, penalties."""

from src.api.http_server.match_stats import compute_match_stats


META = {
    "match_id": "m1",
    "teams": {
        "team_a": {"team_id": "bra", "name": "Brazil", "roster": [
            {"player_id": "team_a_4", "name": "Nine", "number": 9, "role": "FWD"},
        ]},
        "team_b": {"team_id": "ger", "name": "Germany", "roster": [
            {"player_id": "team_b_1", "name": "Two", "number": 2, "role": "DEF"},
        ]},
    },
}


def tick_with(actions):
    return {"tick": 1, "ball_possession": None, "player_positions": {},
            "actions": actions}


def foul_system_action(restart_type="free_kick_foul", card=None, outcome=None):
    details = {"foul": True, "offender_id": "team_b_1",
               "fouling_team": "team_b", "restart_type": restart_type,
               "restart_team": "team_a", "kicker_id": "team_a_4",
               "card": card, "sent_off": card == "red"}
    if outcome:
        details["penalty_outcome"] = outcome
        if outcome == "goal":
            details["goal_scored"] = "team_a"
            details["scored_by"] = "team_a_4"
    return {"player_id": "system", "team": "system", "action": "Hold",
            "result": "ok", "details": details}


def test_foul_counts_to_offending_team_and_player():
    stats = compute_match_stats([tick_with([foul_system_action()])], META)
    assert stats["teams"]["team_b"]["fouls"] == 1
    assert stats["players"]["team_b_1"]["fouls"] == 1
    assert stats["teams"]["team_a"]["fouls"] == 0


def test_yellow_card_counted():
    stats = compute_match_stats(
        [tick_with([foul_system_action(card="yellow")])], META)
    assert stats["teams"]["team_b"]["yellow_cards"] == 1
    assert stats["players"]["team_b_1"]["yellow_cards"] == 1


def test_red_card_counted():
    stats = compute_match_stats(
        [tick_with([foul_system_action(card="red")])], META)
    assert stats["teams"]["team_b"]["red_cards"] == 1
    assert stats["players"]["team_b_1"]["red_cards"] == 1


def test_penalty_awarded_and_scored():
    stats = compute_match_stats(
        [tick_with([foul_system_action("penalty_kick", outcome="goal")])], META)
    assert stats["teams"]["team_a"]["penalties_awarded"] == 1
    assert stats["teams"]["team_a"]["penalties_scored"] == 1
    assert stats["teams"]["team_a"]["goals"] == 1
    assert stats["players"]["team_a_4"]["goals"] == 1


def test_penalty_saved_not_scored():
    stats = compute_match_stats(
        [tick_with([foul_system_action("penalty_kick", outcome="saved")])], META)
    assert stats["teams"]["team_a"]["penalties_awarded"] == 1
    assert stats["teams"]["team_a"]["penalties_scored"] == 0
    assert stats["teams"]["team_a"]["goals"] == 0
