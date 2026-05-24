import json
from pathlib import Path

from src.api.http_server.cup_payload import team_names_for_match


def test_returns_names_when_meta_present(tmp_path: Path):
    (tmp_path / "meta.json").write_text(json.dumps({
        "teams": {
            "team_a": {"team_id": "manchester", "name": "Manchester United"},
            "team_b": {"team_id": "barcelona", "name": "FC Barcelona"},
        }
    }))
    names = team_names_for_match(tmp_path)
    assert names == {"team_a": "Manchester United", "team_b": "FC Barcelona"}


def test_returns_fallback_when_meta_missing(tmp_path: Path):
    names = team_names_for_match(tmp_path)
    assert names == {"team_a": "Team A", "team_b": "Team B"}


def test_returns_fallback_when_meta_unreadable(tmp_path: Path):
    (tmp_path / "meta.json").write_text("not valid json {")
    names = team_names_for_match(tmp_path)
    assert names == {"team_a": "Team A", "team_b": "Team B"}


def test_legacy_bare_list_meta_returns_fallback(tmp_path: Path):
    (tmp_path / "meta.json").write_text(json.dumps({
        "teams": {
            "team_a": [{"player_id": "team_a_0", "number": 1, "role": "GK"}],
            "team_b": [{"player_id": "team_b_0", "number": 1, "role": "GK"}],
        }
    }))
    names = team_names_for_match(tmp_path)
    assert names == {"team_a": "Team A", "team_b": "Team B"}
