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
