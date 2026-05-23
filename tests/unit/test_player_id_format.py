"""
Unit tests for the player ID format contract (ADR-0004).

Validates: format, uniqueness, ordering, parsing, and type invariants.
These tests are framework smoke tests — they exercise pytest itself and
document the ADR-0004 validation criteria in executable form.
"""

import re
import pytest


# ---------------------------------------------------------------------------
# Helpers (inline — src/ not yet built)
# ---------------------------------------------------------------------------

PLAYER_ID_PATTERN = re.compile(r"^team_[ab]_[0-4]$")


def generate_all_player_ids() -> list[str]:
    return [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]


def parse_player_id(player_id: str) -> tuple[str, int]:
    parts = player_id.rsplit("_", 1)
    return parts[0], int(parts[1])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPlayerIdFormat:
    """ADR-0004 Validation Criteria 1–3: format, uniqueness, ordering."""

    def test_all_ids_match_pattern(self):
        for pid in generate_all_player_ids():
            assert PLAYER_ID_PATTERN.match(pid), f"{pid!r} does not match player ID pattern"

    def test_all_ids_are_unique(self):
        ids = generate_all_player_ids()
        assert len(ids) == len(set(ids))

    def test_all_ids_are_strings(self):
        for pid in generate_all_player_ids():
            assert isinstance(pid, str), f"{pid!r} must be str, got {type(pid)}"

    def test_sorted_order(self):
        ids = generate_all_player_ids()
        expected = [
            "team_a_0", "team_a_1", "team_a_2", "team_a_3", "team_a_4",
            "team_b_0", "team_b_1", "team_b_2", "team_b_3", "team_b_4",
        ]
        assert sorted(ids) == expected

    def test_total_player_count(self):
        assert len(generate_all_player_ids()) == 10


class TestParsePlayerId:
    """ADR-0004 Validation Criterion 4: parse contract."""

    @pytest.mark.parametrize("player_id,expected_team,expected_index", [
        ("team_a_0", "team_a", 0),
        ("team_a_4", "team_a", 4),
        ("team_b_0", "team_b", 0),
        ("team_b_4", "team_b", 4),
        ("team_a_2", "team_a", 2),
    ])
    def test_parse_returns_team_and_index(self, player_id, expected_team, expected_index):
        team, index = parse_player_id(player_id)
        assert team == expected_team
        assert index == expected_index

    def test_parse_index_is_int(self):
        _, index = parse_player_id("team_a_3")
        assert isinstance(index, int)

    def test_parse_team_is_str(self):
        team, _ = parse_player_id("team_b_1")
        assert isinstance(team, str)


def test_player_ids_stay_slot_based_with_custom_team_id(tmp_path):
    """ADR-0004: player_id format `team_a_*` / `team_b_*` is independent of
    the team's team_id slug. A team named `manchester` still produces
    player ids `team_a_0`...`team_a_4` when it occupies the team_a slot.
    """
    import os
    from src.foundation.config_loader import load_config

    teams_dir = tmp_path / "configs" / "teams"
    teams_dir.mkdir(parents=True)
    body = (
        "team_id: {slug}\n"
        "name: {name}\n"
        "players:\n"
        "  - role: GK\n    save: 16\n"
        "  - role: DEF\n"
        "  - role: DEF\n"
        "  - role: MID\n"
        "  - role: FWD\n"
    )
    (teams_dir / "manchester.yaml").write_text(body.format(slug="manchester", name="Manchester"))
    (teams_dir / "barcelona.yaml").write_text(body.format(slug="barcelona", name="Barcelona"))

    match_yaml = (
        "match:\n  seed: 1\n  tick_rate: 10\n  duration_minutes: 5\n"
        f"  field_width: 60.0\n  field_height: 40.0\noutput:\n  log_dir: {tmp_path / 'logs'}\n"
        "team_a: manchester\nteam_b: barcelona\n"
    )
    match_path = tmp_path / "configs" / "match.yaml"
    match_path.write_text(match_yaml)

    cfg = load_config(str(match_path))

    for i, p in enumerate(cfg.team_a.players):
        assert p.player_id == f"team_a_{i}"
    for i, p in enumerate(cfg.team_b.players):
        assert p.player_id == f"team_b_{i}"
