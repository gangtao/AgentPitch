"""Issue #38 — event classification for fouls, cards, and penalties."""

from src.orchestration.tick_engine.engine import TickEngine


def classify(recs, score_before=None, score_after=None):
    eng = TickEngine()
    return eng._classify_event(
        recs, [],
        score_before or {"team_a": 0, "team_b": 0},
        score_after or {"team_a": 0, "team_b": 0},
    )


def test_red_card_outranks_foul():
    recs = {"team_b_1": {"action": "Tackle", "result": "foul",
                         "foul_severity": "excessive_force", "card": "red"},
            "system": {"foul": True, "restart_type": "free_kick_foul",
                       "card": "red"}}
    assert classify(recs) == "red_card"


def test_yellow_card():
    recs = {"system": {"foul": True, "restart_type": "free_kick_foul",
                       "card": "yellow"}}
    assert classify(recs) == "yellow_card"


def test_penalty_kick_saved():
    recs = {"system": {"foul": True, "restart_type": "penalty_kick",
                       "card": None, "penalty_outcome": "saved"}}
    assert classify(recs) == "penalty_kick"


def test_penalty_goal_classified_as_goal():
    recs = {"system": {"foul": True, "restart_type": "penalty_kick",
                       "card": None, "penalty_outcome": "goal"}}
    assert classify(recs, {"team_a": 0, "team_b": 0},
                    {"team_a": 1, "team_b": 0}) == "goal"


def test_plain_foul():
    recs = {"system": {"foul": True, "restart_type": "free_kick_foul",
                       "card": None}}
    assert classify(recs) == "foul"


def test_foul_outranks_tackle():
    recs = {"team_b_1": {"action": "Tackle", "result": "foul"},
            "system": {"foul": True, "restart_type": "free_kick_foul",
                       "card": None}}
    assert classify(recs) == "foul"
