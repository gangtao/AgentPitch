"""meta.json carries knockout outcome fields (issue #83)."""
from src.core.match_log_system import MatchLog


def test_build_meta_includes_knockout_fields():
    log = MatchLog("m1")
    log.finalize({
        "final_score": {"team_a": 1, "team_b": 1},
        "decided_by": "shootout",
        "regulation_score": {"team_a": 1, "team_b": 1},
        "after_extra_time_score": {"team_a": 1, "team_b": 1},
        "shootout": {"team_a": 4, "team_b": 3, "winner": "team_a", "kicks": []},
    })
    meta = log._build_meta()
    assert meta["decided_by"] == "shootout"
    assert meta["regulation_score"] == {"team_a": 1, "team_b": 1}
    assert meta["after_extra_time_score"] == {"team_a": 1, "team_b": 1}
    assert meta["shootout"]["winner"] == "team_a"
    assert meta["final_score"] == {"team_a": 1, "team_b": 1}  # level score preserved


def test_build_meta_defaults_on_non_knockout():
    """Non-knockout finalize dict → decided_by defaults to 'regulation', rest None."""
    log = MatchLog("m2")
    log.finalize({
        "final_score": {"team_a": 2, "team_b": 1},
    })
    meta = log._build_meta()
    assert meta["decided_by"] == "regulation"
    assert meta["regulation_score"] is None
    assert meta["after_extra_time_score"] is None
    assert meta["shootout"] is None
