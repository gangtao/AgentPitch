"""
Tests for GameStateManager snapshot builders (Story 002).

Covers all 11 acceptance criteria from
production/epics/game-state-manager/story-002-snapshot-builders.md:

AC-1  (AC-GSM-04): build_tick_snapshot top-level keys match the spec exactly
AC-2  (AC-GSM-05): 10 player entries keyed team_a_0..team_b_4, all str
AC-3  (AC-GSM-06): no my_player_id / my_team in snapshot
AC-4  (AC-GSM-07): build_player_state returns 12-key dict (incl. player_id)
AC-5  (AC-GSM-08): snapshot mutations do not leak into internal state
AC-6: snapshot identity — fresh dicts per call (s1 is not s2)
AC-7  (AC-GSM-18 full): two GSMs from same inputs → equal snapshots
AC-8: match_phase serialised as lowercase
AC-9: ticks_remaining = total_ticks - tick (incl. after manual tick advance)
AC-10: ball state shape and initial values
AC-11: no _-prefixed private fields leak (top-level + nested)
"""

from __future__ import annotations
from typing import Any
import pytest

from src.core.game_state_manager import GameStateManager
from tests.unit.game_state_manager.conftest import (
    _create_test_config,
    _create_test_anchors,
)


def _walk_keys(d: Any) -> set[str]:
    """Recursively collect all dict keys from a nested structure."""
    keys: set[str] = set()
    if isinstance(d, dict):
        for k, v in d.items():
            keys.add(str(k))
            keys.update(_walk_keys(v))
    elif isinstance(d, (list, tuple)):
        for item in d:
            keys.update(_walk_keys(item))
    return keys


# ---------------------------------------------------------------------------
# AC-1 (AC-GSM-04): top-level keys match spec exactly
# ---------------------------------------------------------------------------


class TestAC1SnapshotTopLevelKeys:

    def test_snapshot_top_level_keys_exact_match(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        expected = {
            "tick", "ticks_remaining", "match_phase", "half", "score",
            "ball", "players", "field",
            # ADR-0022: per-team phase classification each tick.
            "team_phase",
        }
        assert set(snap.keys()) == expected


# ---------------------------------------------------------------------------
# AC-2 (AC-GSM-05): 10 player entries keyed team_a_0..team_b_4
# ---------------------------------------------------------------------------


class TestAC2PlayersDict:

    def test_snapshot_players_count_is_ten(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        assert len(snap["players"]) == 10

    def test_snapshot_player_ids_exact_set(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        expected = {f"team_a_{i}" for i in range(5)} | {f"team_b_{i}" for i in range(5)}
        assert set(snap["players"].keys()) == expected

    def test_snapshot_player_ids_all_strings(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        for pid in snap["players"].keys():
            assert isinstance(pid, str)


# ---------------------------------------------------------------------------
# AC-3 (AC-GSM-06): no my_player_id / my_team in snapshot
# ---------------------------------------------------------------------------


class TestAC3NoPersonalInjection:

    def test_snapshot_does_not_include_my_player_id(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        assert "my_player_id" not in snap

    def test_snapshot_does_not_include_my_team(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        assert "my_team" not in snap


# ---------------------------------------------------------------------------
# AC-4 (AC-GSM-07): build_player_state returns 12-key dict
# ---------------------------------------------------------------------------


class TestAC4PlayerStateShape:

    def test_player_state_keys_exact_match(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        ps = gsm.build_player_state("team_a_0")
        expected = {
            "player_id", "team", "number", "role", "position", "formation_position",
            "has_ball", "speed", "skill", "strength", "save",
            "discipline", "dribbling",
            # Specialised pass / shoot ratings (added 2026-04-23).
            # Default to skill when unset in config.
            "passing", "shooting",
            # Stamina + dynamic health (added 2026-04-23).
            "stamina", "current_health",
            # Cooldown feedback per ADR-0015 amendment (2026-04-22) —
            # unified single-timer model.
            "cooldown_remaining",
            # Phase-aware formation zones per ADR-0022 (2026-04-25).
            # formation_position is now the CENTER of formation_zone, which
            # shifts each tick based on formation_zone_phase.
            "formation_zone", "formation_zone_phase",
        }
        assert set(ps.keys()) == expected

    def test_player_state_includes_player_id_field(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        ps = gsm.build_player_state("team_a_3")
        assert ps["player_id"] == "team_a_3"

    def test_player_state_gk_save_positive(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        ps = gsm.build_player_state("team_a_0")  # GK
        assert ps["role"] == "GK"
        assert ps["save"] > 0

    def test_player_state_non_gk_save_zero(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        ps = gsm.build_player_state("team_a_3")  # MID, not GK
        assert ps["role"] != "GK"
        assert ps["save"] == 0


# ---------------------------------------------------------------------------
# AC-5 (AC-GSM-08): mutation of snapshot does not leak into internal state
# ---------------------------------------------------------------------------


class TestAC5SnapshotMutationIsolation:

    def test_snapshot_score_mutation_does_not_leak(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        snap["score"]["team_a"] = 99
        assert gsm.state.score["team_a"] == 0

    def test_snapshot_player_position_mutation_does_not_leak(self):
        anchors = _create_test_anchors()
        gsm = GameStateManager(_create_test_config(), anchors)
        original_pos = anchors["team_a_0"]
        snap = gsm.build_tick_snapshot()
        snap["players"]["team_a_0"]["position"] = (-1.0, -1.0)
        assert gsm.state.players["team_a_0"]["position"] == original_pos

    def test_snapshot_ball_mutation_does_not_leak(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        snap["ball"]["carrier_id"] = "team_a_0"
        assert gsm.state.ball["carrier_id"] is None


# ---------------------------------------------------------------------------
# AC-6: snapshot identity — fresh dict per call
# ---------------------------------------------------------------------------


class TestAC6SnapshotIdentity:

    def test_two_calls_return_distinct_top_level_dicts(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        s1 = gsm.build_tick_snapshot()
        s2 = gsm.build_tick_snapshot()
        assert s1 is not s2

    def test_two_calls_return_distinct_players_dicts(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        s1 = gsm.build_tick_snapshot()
        s2 = gsm.build_tick_snapshot()
        assert s1["players"] is not s2["players"]

    def test_two_calls_return_distinct_score_dicts(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        s1 = gsm.build_tick_snapshot()
        s2 = gsm.build_tick_snapshot()
        assert s1["score"] is not s2["score"]

    def test_two_calls_return_equal_content(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        s1 = gsm.build_tick_snapshot()
        s2 = gsm.build_tick_snapshot()
        assert s1 == s2


# ---------------------------------------------------------------------------
# AC-7 (AC-GSM-18 full): two GSMs from same inputs produce equal snapshots
# ---------------------------------------------------------------------------


class TestAC7CrossGsmDeterminism:

    def test_two_gsms_with_identical_inputs_produce_equal_snapshots(self):
        gsm1 = GameStateManager(_create_test_config(seed=42), _create_test_anchors())
        gsm2 = GameStateManager(_create_test_config(seed=42), _create_test_anchors())
        s1 = gsm1.build_tick_snapshot()
        s2 = gsm2.build_tick_snapshot()
        assert s1 == s2


# ---------------------------------------------------------------------------
# AC-8: match_phase serialised as lowercase
# ---------------------------------------------------------------------------


class TestAC8MatchPhaseLowercase:

    def test_initial_match_phase_is_lowercase_pre_match(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        assert snap["match_phase"] == "pre_match"

    @pytest.mark.parametrize(
        "internal_phase,expected_lower",
        [
            ("PRE_MATCH", "pre_match"),
            ("KICK_OFF", "kick_off"),
            ("IN_PLAY", "in_play"),
            ("GOAL_SCORED", "goal_scored"),
            ("HALF_TIME", "half_time"),
            ("FULL_TIME", "full_time"),
        ],
    )
    def test_all_phase_values_lowercased_in_snapshot(self, internal_phase, expected_lower):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        gsm.state.phase = internal_phase  # type: ignore[assignment]
        snap = gsm.build_tick_snapshot()
        assert snap["match_phase"] == expected_lower


# ---------------------------------------------------------------------------
# AC-9: ticks_remaining = total_ticks - tick
# ---------------------------------------------------------------------------


class TestAC9TicksRemainingFormula:

    def test_ticks_remaining_at_tick_zero_equals_total_ticks(self):
        gsm = GameStateManager(_create_test_config(tick_rate=10, duration_minutes=90), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        assert snap["ticks_remaining"] == 54000

    def test_ticks_remaining_after_manual_tick_advance(self):
        # Story 003 will provide proper tick-advance API; manually mutate for this test
        gsm = GameStateManager(_create_test_config(tick_rate=10, duration_minutes=90), _create_test_anchors())
        gsm.state.tick = 27000
        snap = gsm.build_tick_snapshot()
        assert snap["ticks_remaining"] == 27000

    def test_ticks_remaining_at_full_match_end(self):
        gsm = GameStateManager(_create_test_config(tick_rate=10, duration_minutes=90), _create_test_anchors())
        gsm.state.tick = gsm.state.total_ticks
        snap = gsm.build_tick_snapshot()
        assert snap["ticks_remaining"] == 0


# ---------------------------------------------------------------------------
# AC-10: ball state shape and initial values
# ---------------------------------------------------------------------------


class TestAC10BallState:

    def test_ball_state_initial_values(self):
        gsm = GameStateManager(
            _create_test_config(field_width=100.0, field_height=60.0),
            _create_test_anchors(),
        )
        snap = gsm.build_tick_snapshot()
        assert snap["ball"] == {
            "position": (50.0, 30.0),
            "velocity": (0.0, 0.0),
            "carrier_id": None,
            "possession": None,
        }


# ---------------------------------------------------------------------------
# AC-11: no _-prefixed private fields leak (top-level AND recursive)
# ---------------------------------------------------------------------------


class TestAC11NoPrivateFieldsLeak:

    def test_no_underscore_prefixed_keys_at_top_level(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        for key in snap.keys():
            assert not key.startswith("_"), f"private field leaked at top level: {key}"

    def test_no_underscore_prefixed_keys_recursively(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        snap = gsm.build_tick_snapshot()
        all_keys = _walk_keys(snap)
        for key in all_keys:
            assert not key.startswith("_"), f"private field leaked in nested dict: {key}"

    def test_specific_private_fields_absent(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        # Set _pass_landing_zone to a sentinel so we'd notice if it leaked
        gsm.state._pass_landing_zone = (45.5, 28.0)
        snap = gsm.build_tick_snapshot()
        all_keys = _walk_keys(snap)
        for forbidden in ("_anchors", "_kickoff_team", "_last_touching_team", "_pass_landing_zone"):
            assert forbidden not in all_keys, f"private field {forbidden} leaked into snapshot"


# ---------------------------------------------------------------------------
# Bonus: build_player_state returns a defensive copy (the /code-review suggestion)
# ---------------------------------------------------------------------------


class TestBuildPlayerStateDefensiveCopy:

    def test_mutating_returned_dict_does_not_leak(self):
        anchors = _create_test_anchors()
        gsm = GameStateManager(_create_test_config(), anchors)
        ps = gsm.build_player_state("team_a_0")
        ps["position"] = (-99.0, -99.0)
        ps["has_ball"] = True
        assert gsm.state.players["team_a_0"]["position"] == anchors["team_a_0"]
        assert gsm.state.players["team_a_0"]["has_ball"] is False

    def test_two_calls_return_distinct_dicts(self):
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        ps1 = gsm.build_player_state("team_a_0")
        ps2 = gsm.build_player_state("team_a_0")
        assert ps1 is not ps2
        assert ps1 == ps2
