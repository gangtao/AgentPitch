"""Test that the new teams_meta shape lands in meta.json."""

from __future__ import annotations

from src.core.match_log_system import MatchLog


def test_meta_json_carries_team_display_and_player_names():
    """set_teams_meta() with the new dict-per-slot shape lands verbatim in
    meta.json under the "teams" key — including team display name, slug
    (team_id), and per-player display name.
    """
    ml = MatchLog("test-match")
    ml.set_teams_meta(
        {
            "team_a": {
                "team_id": "manchester",
                "name": "Manchester United",
                "roster": [
                    {"player_id": "team_a_0", "name": "Onana", "number": 1, "role": "GK"},
                ],
            },
            "team_b": {
                "team_id": "barcelona",
                "name": "FC Barcelona",
                "roster": [
                    {"player_id": "team_b_0", "name": "TerStegen", "number": 1, "role": "GK"},
                ],
            },
        }
    )
    ml.finalize({"final_score": {"team_a": 0, "team_b": 0}})

    meta = ml._build_meta()

    assert meta["teams"]["team_a"]["name"] == "Manchester United"
    assert meta["teams"]["team_a"]["team_id"] == "manchester"
    assert meta["teams"]["team_a"]["roster"][0]["name"] == "Onana"
    assert meta["teams"]["team_b"]["name"] == "FC Barcelona"
