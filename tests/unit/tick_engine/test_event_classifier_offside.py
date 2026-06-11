"""Issue #31 — offside surfaces as a distinct event_type in events.jsonl."""

from src.orchestration.tick_engine.engine import TickEngine


def test_offside_classified_above_action_priorities():
    records = {
        "system": {"offside": True, "restart_type": "free_kick_offside",
                   "restart_team": "team_b", "kicker_id": "team_b_1"},
        "team_a_1": {"offside_offence": True, "action": "Hold", "result": "ok"},
    }
    assert TickEngine()._classify_event(records, [], 0, 0) == "offside"


def test_goal_still_outranks_offside():
    records = {"system": {"offside": True}}
    assert TickEngine()._classify_event(records, [], 0, 1) == "goal"
