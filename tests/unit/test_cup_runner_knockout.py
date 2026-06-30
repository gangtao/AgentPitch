"""Cup runner trusts the engine's knockout winner; coin-flip is fallback only."""
from src.orchestration.cli.cup_runner import _winner_from_meta


def _match():
    return {"match_id": "r16-m1", "team_a_slot": 3, "team_b_slot": 6}


def test_regulation_winner_from_score():
    meta = {"final_score": {"team_a": 2, "team_b": 1}, "decided_by": "regulation",
            "shootout": None}
    result, slot, decided_by = _winner_from_meta(_match(), meta)
    assert result == "team_a" and slot == 3 and decided_by == "regulation"


def test_shootout_winner_overrides_level_score():
    meta = {"final_score": {"team_a": 1, "team_b": 1}, "decided_by": "shootout",
            "shootout": {"team_a": 4, "team_b": 3, "winner": "team_b", "kicks": []}}
    result, slot, decided_by = _winner_from_meta(_match(), meta)
    assert result == "team_b" and slot == 6 and decided_by == "shootout"


def test_extra_time_winner_from_level_aware_score():
    meta = {"final_score": {"team_a": 2, "team_b": 1}, "decided_by": "extra_time",
            "shootout": None}
    result, slot, decided_by = _winner_from_meta(_match(), meta)
    assert result == "team_a" and slot == 3 and decided_by == "extra_time"
