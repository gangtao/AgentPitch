"""Tests for src/cup_metadata.py — bracket generation and cup I/O."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from src.cup_metadata import (
    ROUND_NAMES,
    CUP_DIR_PREFIX,
    cup_dir,
    generate_bracket,
    list_cups,
    propagate_winners,
    read_cup_json,
    write_cup_json,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

STRATEGIES_4 = ["alpha", "beta", "gamma", "delta"]
STRATEGIES_8 = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"]
STRATEGIES_16 = [f"t{i}" for i in range(1, 17)]
STRATEGIES_32 = [f"u{i}" for i in range(1, 33)]

CUP_ID = "cup-20260429-1430"


# ---------------------------------------------------------------------------
# 1. generate_bracket — 4-team
# ---------------------------------------------------------------------------


class TestGenerateBracket4:
    def setup_method(self):
        self.data = generate_bracket(4, STRATEGIES_4, CUP_ID)

    def test_teams_count(self):
        assert len(self.data["teams"]) == 4

    def test_teams_slots_sequential(self):
        slots = [t["slot"] for t in self.data["teams"]]
        assert slots == [1, 2, 3, 4]

    def test_teams_all_strategies_present(self):
        names = {t["strategy_name"] for t in self.data["teams"]}
        assert names == set(STRATEGIES_4)

    def test_round_count(self):
        assert len(self.data["rounds"]) == 2

    def test_round1_has_two_matches(self):
        r1 = self.data["rounds"][0]
        assert r1["round_number"] == 1
        assert len(r1["matches"]) == 2

    def test_round1_pairings_seed1_vs_seed4(self):
        """Seed 1 faces seed 4 (standard single-elim seeding)."""
        r1_matches = self.data["rounds"][0]["matches"]
        m1 = r1_matches[0]
        assert m1["team_a_slot"] == 1
        assert m1["team_b_slot"] == 4

    def test_round1_pairings_seed2_vs_seed3(self):
        """Seed 2 faces seed 3."""
        r1_matches = self.data["rounds"][0]["matches"]
        m2 = r1_matches[1]
        assert m2["team_a_slot"] == 2
        assert m2["team_b_slot"] == 3

    def test_round1_match_ids_populated(self):
        r1_matches = self.data["rounds"][0]["matches"]
        for m in r1_matches:
            assert m["match_id"] is not None
            assert CUP_ID in m["match_id"]

    def test_round1_match_slots(self):
        r1_matches = self.data["rounds"][0]["matches"]
        assert r1_matches[0]["match_slot"] == "R1M1"
        assert r1_matches[1]["match_slot"] == "R1M2"

    def test_round2_has_one_match(self):
        r2 = self.data["rounds"][1]
        assert r2["round_number"] == 2
        assert len(r2["matches"]) == 1

    def test_round2_slots_are_null(self):
        r2_match = self.data["rounds"][1]["matches"][0]
        assert r2_match["team_a_slot"] is None
        assert r2_match["team_b_slot"] is None
        assert r2_match["match_id"] is None

    def test_round_names_4team(self):
        rounds = self.data["rounds"]
        assert rounds[0]["round_name"] == "Semi-Finals"
        assert rounds[1]["round_name"] == "Final"

    def test_status_running(self):
        assert self.data["status"] == "running"

    def test_winner_none(self):
        assert self.data["winner"] is None

    def test_bracket_size_field(self):
        assert self.data["bracket_size"] == 4

    def test_cup_id_field(self):
        assert self.data["cup_id"] == CUP_ID

    def test_deterministic_shuffle(self):
        """Same cup_id always yields the same shuffle."""
        data2 = generate_bracket(4, STRATEGIES_4, CUP_ID)
        assert self.data["teams"] == data2["teams"]

    def test_different_cup_id_may_differ(self):
        """Different cup_id may produce different slot assignments."""
        data_other = generate_bracket(4, STRATEGIES_4, "other-cup-id-xyz")
        # It's theoretically possible they're the same, but with enough
        # strategies and two distinct IDs, they should usually differ.
        # We just verify it runs without error and has correct structure.
        assert len(data_other["teams"]) == 4

    def test_invalid_bracket_size_raises(self):
        with pytest.raises(ValueError, match="Unsupported bracket_size"):
            generate_bracket(5, ["a","b","c","d","e"], "x")

    def test_wrong_strategy_count_raises(self):
        with pytest.raises(ValueError, match="must equal bracket_size"):
            generate_bracket(4, ["a","b","c"], "x")


# ---------------------------------------------------------------------------
# 2. generate_bracket — 8-team pairings
# ---------------------------------------------------------------------------


class TestGenerateBracket8:
    def setup_method(self):
        self.data = generate_bracket(8, STRATEGIES_8, CUP_ID)

    def test_teams_count(self):
        assert len(self.data["teams"]) == 8

    def test_round_count(self):
        assert len(self.data["rounds"]) == 3

    def test_round1_has_four_matches(self):
        assert len(self.data["rounds"][0]["matches"]) == 4

    def test_round2_has_two_matches(self):
        assert len(self.data["rounds"][1]["matches"]) == 2

    def test_round3_has_one_match(self):
        assert len(self.data["rounds"][2]["matches"]) == 1

    def test_round1_r1m1_seed1_vs_seed8(self):
        """R1M1: seed 1 vs seed 8."""
        r1_matches = self.data["rounds"][0]["matches"]
        m1 = r1_matches[0]
        assert m1["team_a_slot"] == 1
        assert m1["team_b_slot"] == 8

    def test_round1_r1m2_seed4_vs_seed5(self):
        """R1M2: seed 4 vs seed 5."""
        r1_matches = self.data["rounds"][0]["matches"]
        m2 = r1_matches[1]
        assert m2["team_a_slot"] == 4
        assert m2["team_b_slot"] == 5

    def test_round1_r1m3_seed3_vs_seed6(self):
        """R1M3: seed 3 vs seed 6."""
        r1_matches = self.data["rounds"][0]["matches"]
        m3 = r1_matches[2]
        assert m3["team_a_slot"] == 3
        assert m3["team_b_slot"] == 6

    def test_round1_r1m4_seed2_vs_seed7(self):
        """R1M4: seed 2 vs seed 7."""
        r1_matches = self.data["rounds"][0]["matches"]
        m4 = r1_matches[3]
        assert m4["team_a_slot"] == 2
        assert m4["team_b_slot"] == 7

    def test_future_rounds_null_slots(self):
        for rnd in self.data["rounds"][1:]:
            for m in rnd["matches"]:
                assert m["team_a_slot"] is None
                assert m["team_b_slot"] is None
                assert m["match_id"] is None

    def test_round_names_8team(self):
        rounds = self.data["rounds"]
        assert rounds[0]["round_name"] == "Quarter-Finals"
        assert rounds[1]["round_name"] == "Semi-Finals"
        assert rounds[2]["round_name"] == "Final"


# ---------------------------------------------------------------------------
# 3. generate_bracket — 16-team structure
# ---------------------------------------------------------------------------


class TestGenerateBracket16:
    def setup_method(self):
        self.data = generate_bracket(16, STRATEGIES_16, CUP_ID)

    def test_teams_count(self):
        assert len(self.data["teams"]) == 16

    def test_round_count(self):
        assert len(self.data["rounds"]) == 4

    def test_round1_match_count(self):
        assert len(self.data["rounds"][0]["matches"]) == 8

    def test_round2_match_count(self):
        assert len(self.data["rounds"][1]["matches"]) == 4

    def test_round3_match_count(self):
        assert len(self.data["rounds"][2]["matches"]) == 2

    def test_round4_match_count(self):
        assert len(self.data["rounds"][3]["matches"]) == 1

    def test_round_names_16team(self):
        rounds = self.data["rounds"]
        assert rounds[0]["round_name"] == "Round of 16"
        assert rounds[1]["round_name"] == "Quarter-Finals"
        assert rounds[2]["round_name"] == "Semi-Finals"
        assert rounds[3]["round_name"] == "Final"

    def test_round1_seed1_vs_seed16(self):
        """Seed 1 faces seed 16."""
        m1 = self.data["rounds"][0]["matches"][0]
        assert m1["team_a_slot"] == 1
        assert m1["team_b_slot"] == 16

    def test_future_rounds_null_slots(self):
        for rnd in self.data["rounds"][1:]:
            for m in rnd["matches"]:
                assert m["team_a_slot"] is None
                assert m["team_b_slot"] is None

    def test_all_slots_covered_in_round1(self):
        """Every slot 1..16 appears exactly once in R1 pairings."""
        r1_matches = self.data["rounds"][0]["matches"]
        all_slots = []
        for m in r1_matches:
            all_slots.append(m["team_a_slot"])
            all_slots.append(m["team_b_slot"])
        assert sorted(all_slots) == list(range(1, 17))


# ---------------------------------------------------------------------------
# 4. generate_bracket — 32-team structure
# ---------------------------------------------------------------------------


class TestGenerateBracket32:
    def setup_method(self):
        self.data = generate_bracket(32, STRATEGIES_32, CUP_ID)

    def test_teams_count(self):
        assert len(self.data["teams"]) == 32

    def test_round_count(self):
        assert len(self.data["rounds"]) == 5

    def test_round1_match_count(self):
        assert len(self.data["rounds"][0]["matches"]) == 16

    def test_all_slots_covered_in_round1(self):
        """Every slot 1..32 appears exactly once in R1 pairings."""
        r1_matches = self.data["rounds"][0]["matches"]
        all_slots = []
        for m in r1_matches:
            all_slots.append(m["team_a_slot"])
            all_slots.append(m["team_b_slot"])
        assert sorted(all_slots) == list(range(1, 33))

    def test_round_names_32team(self):
        rounds = self.data["rounds"]
        assert rounds[0]["round_name"] == "Round of 32"
        assert rounds[1]["round_name"] == "Round of 16"
        assert rounds[2]["round_name"] == "Quarter-Finals"
        assert rounds[3]["round_name"] == "Semi-Finals"
        assert rounds[4]["round_name"] == "Final"

    def test_future_rounds_null_slots(self):
        for rnd in self.data["rounds"][1:]:
            for m in rnd["matches"]:
                assert m["team_a_slot"] is None
                assert m["team_b_slot"] is None


# ---------------------------------------------------------------------------
# 5. ROUND_NAMES constant — correct names for all bracket sizes
# ---------------------------------------------------------------------------


class TestRoundNames:
    def test_4team_round_names(self):
        assert ROUND_NAMES[4][1] == "Semi-Finals"
        assert ROUND_NAMES[4][2] == "Final"

    def test_8team_round_names(self):
        assert ROUND_NAMES[8][1] == "Quarter-Finals"
        assert ROUND_NAMES[8][2] == "Semi-Finals"
        assert ROUND_NAMES[8][3] == "Final"

    def test_16team_round_names(self):
        assert ROUND_NAMES[16][1] == "Round of 16"
        assert ROUND_NAMES[16][2] == "Quarter-Finals"
        assert ROUND_NAMES[16][3] == "Semi-Finals"
        assert ROUND_NAMES[16][4] == "Final"

    def test_32team_round_names(self):
        assert ROUND_NAMES[32][1] == "Round of 32"
        assert ROUND_NAMES[32][2] == "Round of 16"
        assert ROUND_NAMES[32][3] == "Quarter-Finals"
        assert ROUND_NAMES[32][4] == "Semi-Finals"
        assert ROUND_NAMES[32][5] == "Final"

    def test_supported_bracket_sizes(self):
        assert set(ROUND_NAMES.keys()) == {4, 8, 16, 32}


# ---------------------------------------------------------------------------
# 6. propagate_winners — after R1 complete, R2 slots filled
# ---------------------------------------------------------------------------


class TestPropagateWinners:
    def _make_4team_cup(self) -> dict:
        data = generate_bracket(4, STRATEGIES_4, CUP_ID)
        # Simulate R1M1 completion: slot 1 wins
        r1 = data["rounds"][0]
        r1["matches"][0]["result"] = "team_a"
        r1["matches"][0]["winner_slot"] = 1
        r1["matches"][0]["status"] = "complete"
        # Simulate R1M2 completion: slot 3 wins
        r1["matches"][1]["result"] = "team_b"
        r1["matches"][1]["winner_slot"] = 3
        r1["matches"][1]["status"] = "complete"
        r1["status"] = "complete"
        return data

    def test_r2_team_a_slot_filled(self):
        data = self._make_4team_cup()
        data = propagate_winners(data, completed_round=1)
        r2_match = data["rounds"][1]["matches"][0]
        assert r2_match["team_a_slot"] == 1

    def test_r2_team_b_slot_filled(self):
        data = self._make_4team_cup()
        data = propagate_winners(data, completed_round=1)
        r2_match = data["rounds"][1]["matches"][0]
        assert r2_match["team_b_slot"] == 3

    def test_r2_match_id_assigned(self):
        data = self._make_4team_cup()
        data = propagate_winners(data, completed_round=1)
        r2_match = data["rounds"][1]["matches"][0]
        assert r2_match["match_id"] == f"{CUP_ID}-R2M1"

    def test_8team_propagation(self):
        """8-team: R1 winners propagate correctly to R2."""
        data = generate_bracket(8, STRATEGIES_8, CUP_ID)
        r1 = data["rounds"][0]
        # Set all R1 winners: each match winner is team_a_slot
        winner_slots = []
        for m in r1["matches"]:
            m["result"] = "team_a"
            m["winner_slot"] = m["team_a_slot"]
            m["status"] = "complete"
            winner_slots.append(m["team_a_slot"])
        r1["status"] = "complete"

        data = propagate_winners(data, completed_round=1)
        r2_matches = data["rounds"][1]["matches"]

        # R2M1: winner of R1M1 vs winner of R1M2
        assert r2_matches[0]["team_a_slot"] == winner_slots[0]
        assert r2_matches[0]["team_b_slot"] == winner_slots[1]
        # R2M2: winner of R1M3 vs winner of R1M4
        assert r2_matches[1]["team_a_slot"] == winner_slots[2]
        assert r2_matches[1]["team_b_slot"] == winner_slots[3]

    def test_propagate_final_round_is_noop(self):
        """Propagating from the final round (no next round) should not error."""
        data = generate_bracket(4, STRATEGIES_4, CUP_ID)
        r2 = data["rounds"][1]
        r2["matches"][0]["winner_slot"] = 1
        r2["matches"][0]["status"] = "complete"
        r2["status"] = "complete"
        # Should not raise; returns data unchanged (no round 3)
        result = propagate_winners(data, completed_round=2)
        assert result is data

    def test_match_id_not_set_with_only_one_slot_filled(self):
        # Set only one winner in round 1 (first match only)
        cup = generate_bracket(4, ["a","b","c","d"], "cup-test")
        cup["rounds"][0]["matches"][0]["winner_slot"] = 1
        # Only propagate one match worth of data
        # After partial propagation, next round match_id should still be None
        # because the second slot isn't filled yet
        result = propagate_winners(cup, 1)
        assert result["rounds"][1]["matches"][0]["match_id"] is None
        assert result["rounds"][1]["matches"][0]["team_a_slot"] == 1
        assert result["rounds"][1]["matches"][0]["team_b_slot"] is None


# ---------------------------------------------------------------------------
# 7. propagate_winners — idempotency
# ---------------------------------------------------------------------------


class TestPropagateWinnersIdempotency:
    def _make_completed_r1(self) -> dict:
        data = generate_bracket(4, STRATEGIES_4, CUP_ID)
        r1 = data["rounds"][0]
        r1["matches"][0]["result"] = "team_a"
        r1["matches"][0]["winner_slot"] = 1
        r1["matches"][0]["status"] = "complete"
        r1["matches"][1]["result"] = "team_b"
        r1["matches"][1]["winner_slot"] = 3
        r1["matches"][1]["status"] = "complete"
        r1["status"] = "complete"
        return data

    def test_double_propagate_same_result(self):
        data = self._make_completed_r1()
        data = propagate_winners(data, completed_round=1)
        first_r2 = data["rounds"][1]["matches"][0].copy()
        # Call again
        data = propagate_winners(data, completed_round=1)
        second_r2 = data["rounds"][1]["matches"][0]
        assert second_r2["team_a_slot"] == first_r2["team_a_slot"]
        assert second_r2["team_b_slot"] == first_r2["team_b_slot"]
        assert second_r2["match_id"] == first_r2["match_id"]

    def test_double_propagate_does_not_corrupt(self):
        data = self._make_completed_r1()
        data = propagate_winners(data, completed_round=1)
        # Change the winner in R1 after propagation (simulate a bug),
        # but idempotency means existing non-None slots are NOT overwritten.
        data["rounds"][0]["matches"][0]["winner_slot"] = 4  # "wrong" winner
        data = propagate_winners(data, completed_round=1)
        # team_a_slot should remain 1 (set by first propagation, not overwritten)
        assert data["rounds"][1]["matches"][0]["team_a_slot"] == 1


# ---------------------------------------------------------------------------
# 8. write_cup_json / read_cup_json — round-trip
# ---------------------------------------------------------------------------


class TestCupJsonIO:
    def test_roundtrip_preserves_all_fields(self, tmp_path):
        cup_d = tmp_path / "cup_test"
        cup_d.mkdir()
        original = generate_bracket(4, STRATEGIES_4, CUP_ID)
        original["name"] = "Spring Cup"
        original["config_name"] = "5v5"
        original["created_iso"] = "2026-04-29T14:30:00Z"

        write_cup_json(cup_d, original)
        read_back = read_cup_json(cup_d)

        assert read_back["cup_id"] == original["cup_id"]
        assert read_back["name"] == "Spring Cup"
        assert read_back["status"] == "running"
        assert read_back["config_name"] == "5v5"
        assert read_back["bracket_size"] == 4
        assert read_back["created_iso"] == "2026-04-29T14:30:00Z"
        assert read_back["completed_iso"] is None
        assert read_back["winner"] is None
        assert len(read_back["teams"]) == 4
        assert len(read_back["rounds"]) == 2

    def test_atomic_write_no_tmp_left_behind(self, tmp_path):
        cup_d = tmp_path / "cup_test"
        cup_d.mkdir()
        data = generate_bracket(4, STRATEGIES_4, CUP_ID)
        write_cup_json(cup_d, data)
        # .tmp file should not exist after write
        assert not (cup_d / "cup.json.tmp").exists()
        assert (cup_d / "cup.json").exists()

    def test_read_missing_raises(self, tmp_path):
        cup_d = tmp_path / "cup_missing"
        cup_d.mkdir()
        with pytest.raises(FileNotFoundError):
            read_cup_json(cup_d)

    def test_write_then_overwrite(self, tmp_path):
        cup_d = tmp_path / "cup_test"
        cup_d.mkdir()
        data = generate_bracket(4, STRATEGIES_4, CUP_ID)
        write_cup_json(cup_d, data)
        data["status"] = "complete"
        data["winner"] = "alpha"
        write_cup_json(cup_d, data)
        read_back = read_cup_json(cup_d)
        assert read_back["status"] == "complete"
        assert read_back["winner"] == "alpha"


# ---------------------------------------------------------------------------
# 9. list_cups — returns [], skips malformed, sorts by created_iso desc
# ---------------------------------------------------------------------------


class TestListCups:
    def test_returns_empty_for_missing_dir(self, tmp_path):
        missing = tmp_path / "nonexistent"
        assert list_cups(missing) == []

    def test_returns_empty_for_empty_dir(self, tmp_path):
        assert list_cups(tmp_path) == []

    def test_ignores_non_cup_dirs(self, tmp_path):
        (tmp_path / "other_dir").mkdir()
        (tmp_path / "series_abc").mkdir()
        assert list_cups(tmp_path) == []

    def test_skips_malformed_cup_json(self, tmp_path):
        bad_cup = tmp_path / "cup_bad"
        bad_cup.mkdir()
        (bad_cup / "cup.json").write_text("not valid json", encoding="utf-8")
        assert list_cups(tmp_path) == []

    def test_skips_dir_missing_cup_json(self, tmp_path):
        no_json = tmp_path / "cup_nojson"
        no_json.mkdir()
        assert list_cups(tmp_path) == []

    def test_returns_summary_fields(self, tmp_path):
        cup_d = tmp_path / "cup_abc"
        cup_d.mkdir()
        data = generate_bracket(4, STRATEGIES_4, "abc")
        data["name"] = "Test Cup"
        data["config_name"] = "5v5"
        data["created_iso"] = "2026-04-29T12:00:00Z"
        write_cup_json(cup_d, data)

        results = list_cups(tmp_path)
        assert len(results) == 1
        s = results[0]
        assert s["cup_id"] == "abc"
        assert s["name"] == "Test Cup"
        assert s["status"] == "running"
        assert s["config_name"] == "5v5"
        assert s["bracket_size"] == 4
        assert s["created_iso"] == "2026-04-29T12:00:00Z"
        assert s["completed_iso"] is None
        assert s["winner"] is None

    def test_sorts_by_created_iso_desc(self, tmp_path):
        timestamps = [
            ("cup_a", "2026-04-29T10:00:00Z"),
            ("cup_b", "2026-04-29T14:00:00Z"),
            ("cup_c", "2026-04-29T08:00:00Z"),
        ]
        for cup_name, ts in timestamps:
            cup_d = tmp_path / cup_name
            cup_d.mkdir()
            data = generate_bracket(4, STRATEGIES_4, cup_name.removeprefix("cup_"))
            data["created_iso"] = ts
            write_cup_json(cup_d, data)

        results = list_cups(tmp_path)
        assert len(results) == 3
        returned_times = [r["created_iso"] for r in results]
        assert returned_times == sorted(returned_times, reverse=True)
        assert returned_times[0] == "2026-04-29T14:00:00Z"

    def test_mixed_valid_and_malformed(self, tmp_path):
        """Valid dirs returned, malformed silently skipped."""
        valid_d = tmp_path / "cup_valid"
        valid_d.mkdir()
        data = generate_bracket(4, STRATEGIES_4, "valid")
        data["created_iso"] = "2026-04-29T10:00:00Z"
        write_cup_json(valid_d, data)

        bad_d = tmp_path / "cup_bad"
        bad_d.mkdir()
        (bad_d / "cup.json").write_text("{bad json}", encoding="utf-8")

        results = list_cups(tmp_path)
        assert len(results) == 1
        assert results[0]["cup_id"] == "valid"


# ---------------------------------------------------------------------------
# 10. cup_dir path helper
# ---------------------------------------------------------------------------


class TestCupDir:
    def test_returns_correct_path(self, tmp_path):
        result = cup_dir(tmp_path, "abc123")
        assert result == tmp_path / "cup_abc123"

    def test_prefix_present(self, tmp_path):
        result = cup_dir(tmp_path, "test")
        assert result.name == "cup_test"
