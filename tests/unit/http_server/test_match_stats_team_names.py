"""Unit tests for team display name surfacing in compute_match_stats().

Verifies that compute_match_stats:
  - Reads team_id/name from the new meta.teams.<slot> dict shape.
  - Falls back to slot labels when meta is missing or empty.
  - Tolerates the legacy bare-list meta shape without crashing.
"""
from src.api.http_server.match_stats import compute_match_stats


def test_team_names_passed_through_from_meta():
    ticks: list = []
    meta = {
        "teams": {
            "team_a": {"team_id": "manchester", "name": "Manchester United"},
            "team_b": {"team_id": "barcelona", "name": "FC Barcelona"},
        }
    }
    stats = compute_match_stats(ticks, meta)
    assert stats["teams"]["team_a"]["name"] == "Manchester United"
    assert stats["teams"]["team_a"]["team_id"] == "manchester"
    assert stats["teams"]["team_b"]["name"] == "FC Barcelona"
    assert stats["teams"]["team_b"]["team_id"] == "barcelona"


def test_team_names_fallback_when_meta_missing():
    stats = compute_match_stats([], {})
    assert stats["teams"]["team_a"]["name"] == "Team A"
    assert stats["teams"]["team_a"]["team_id"] == "team_a"
    assert stats["teams"]["team_b"]["name"] == "Team B"
    assert stats["teams"]["team_b"]["team_id"] == "team_b"


def test_legacy_bare_list_meta_does_not_crash():
    ticks: list = []
    meta = {
        "teams": {
            "team_a": [{"player_id": "team_a_0", "number": 1, "role": "GK"}],
            "team_b": [{"player_id": "team_b_0", "number": 1, "role": "GK"}],
        }
    }
    stats = compute_match_stats(ticks, meta)
    assert stats["teams"]["team_a"]["name"] == "Team A"
    assert stats["teams"]["team_a"]["team_id"] == "team_a"
    assert stats["teams"]["team_b"]["name"] == "Team B"
    assert stats["teams"]["team_b"]["team_id"] == "team_b"
