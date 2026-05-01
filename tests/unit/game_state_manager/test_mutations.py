"""
Tests for GameStateManager mutation API (Story 003).

Covers all 15 acceptance criteria from
production/epics/game-state-manager/story-003-mutation-api.md:

AC-1: apply_move basic position updates
AC-2: apply_move clamping (AC-GSM-20) - clamps silently, edge cases
AC-3: transfer_possession to player (AC-GSM-09) - atomic update of all 3 slots
AC-4: transfer_possession to None (AC-GSM-10) - clears all 3 slots
AC-5: transfer_possession no-op (EC-GSM-03) - (None, None) does nothing
AC-6: stale from_id WARNING (EC-GSM-04) - still transfers with warning
AC-7: transfer_possession switches teams - possession derived correctly
AC-8: update_ball_position basic - in-bounds update
AC-9: update_ball_position OOB awards possession (AC-GSM-21) - to kickoff team
AC-10: OOB awards to non-touching team
AC-11: OOB tie-break by player_id (ADR-0004) - lexicographic ordering
AC-12: update_ball_velocity - direct setter
AC-13: record_goal increments score (AC-GSM-13) - IN_PLAY context
AC-14: record_goal in non-IN_PLAY logs ERROR (EC-GSM-07) - but score still applies
AC-15: mutations don't break snapshot contract - post-mutation snapshot works
"""

from __future__ import annotations
import logging
import pytest

from src.core.game_state_manager import GameStateManager
from tests.unit.game_state_manager.conftest import (
    _create_test_config,
    _create_test_anchors,
)


# ---------------------------------------------------------------------------
# AC-1: apply_move basic position updates
# ---------------------------------------------------------------------------


class TestAC1ApplyMoveBasic:
    """Test AC-1: apply_move basic position updates."""

    def test_apply_move_updates_position_in_place(self):
        """apply_move should update player position directly."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: player starts at anchor position
        initial_pos = gsm.state.players["team_a_0"]["position"]
        assert initial_pos == (8.0, 30.0)

        # Act: move player to new position within bounds
        new_pos = (25.0, 45.0)
        gsm.apply_move("team_a_0", new_pos)

        # Assert: position updated
        assert gsm.state.players["team_a_0"]["position"] == new_pos

    def test_apply_move_multiple_players_independent(self):
        """apply_move should work independently for multiple players."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: move two different players
        gsm.apply_move("team_a_1", (30.0, 25.0))
        gsm.apply_move("team_b_3", (70.0, 35.0))

        # Assert: both positions updated independently
        assert gsm.state.players["team_a_1"]["position"] == (30.0, 25.0)
        assert gsm.state.players["team_b_3"]["position"] == (70.0, 35.0)
        # Other players unchanged
        assert gsm.state.players["team_a_0"]["position"] == (8.0, 30.0)


# ---------------------------------------------------------------------------
# AC-2: apply_move clamping (AC-GSM-20)
# ---------------------------------------------------------------------------


class TestAC2ApplyMoveClamping:
    """Test AC-2: apply_move clamping (AC-GSM-20) - clamps silently, no exception."""

    def test_apply_move_clamps_oversized_coordinates(self):
        """apply_move should clamp coordinates that exceed field bounds."""
        gsm = GameStateManager(_create_test_config(field_width=100.0, field_height=60.0), _create_test_anchors())

        # Act: try to move beyond field bounds (150, 80) on 100×60 field
        gsm.apply_move("team_a_0", (150.0, 80.0))

        # Assert: clamped to field boundary (100, 60)
        assert gsm.state.players["team_a_0"]["position"] == (100.0, 60.0)

    def test_apply_move_clamps_negative_coordinates(self):
        """apply_move should clamp negative coordinates to zero."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Act: try negative coordinates
        gsm.apply_move("team_a_1", (-5.0, -10.0))

        # Assert: clamped to (0, 0)
        assert gsm.state.players["team_a_1"]["position"] == (0.0, 0.0)

    def test_apply_move_clamps_one_axis_only(self):
        """apply_move should clamp only the out-of-bounds axis."""
        gsm = GameStateManager(_create_test_config(field_width=100.0, field_height=60.0), _create_test_anchors())

        # Act: only X axis out of bounds
        gsm.apply_move("team_a_2", (150.0, 30.0))

        # Assert: X clamped, Y unchanged
        assert gsm.state.players["team_a_2"]["position"] == (100.0, 30.0)

    def test_apply_move_exactly_at_boundary_unchanged(self):
        """apply_move should leave coordinates exactly at boundaries unchanged."""
        gsm = GameStateManager(_create_test_config(field_width=100.0, field_height=60.0), _create_test_anchors())

        # Act: move to exact boundary
        gsm.apply_move("team_a_3", (100.0, 60.0))

        # Assert: unchanged (at boundary)
        assert gsm.state.players["team_a_3"]["position"] == (100.0, 60.0)


# ---------------------------------------------------------------------------
# AC-3: transfer_possession to player (AC-GSM-09) - atomic update ALL 3 slots
# ---------------------------------------------------------------------------


class TestAC3TransferPossessionToPlayer:
    """Test AC-3: transfer_possession to player (AC-GSM-09) - atomic update of all 3 slots."""

    def test_transfer_possession_to_player_updates_all_three_slots(self):
        """transfer_possession must atomically update carrier_id, has_ball flags, and possession."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Act: transfer possession to team_a_2
        gsm.transfer_possession(None, "team_a_2")

        # Assert: ALL THREE slots updated atomically
        # 1. ball.carrier_id updated
        assert gsm.state.ball["carrier_id"] == "team_a_2"

        # 2. exactly one has_ball flag is True (the receiver)
        assert gsm.state.players["team_a_2"]["has_ball"] is True
        # All other 9 players have has_ball False
        for pid in gsm.state.players:
            if pid != "team_a_2":
                assert gsm.state.players[pid]["has_ball"] is False

        # 3. possession derived from carrier's team
        assert gsm.state.ball["possession"] == "team_a"

    def test_transfer_possession_switches_between_players(self):
        """Transfer from one player to another should reset all flags correctly."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: team_a_1 starts with ball
        gsm.transfer_possession(None, "team_a_1")
        assert gsm.state.players["team_a_1"]["has_ball"] is True

        # Act: transfer to team_b_3
        gsm.transfer_possession("team_a_1", "team_b_3")

        # Assert: ALL THREE slots updated correctly
        assert gsm.state.ball["carrier_id"] == "team_b_3"
        assert gsm.state.players["team_b_3"]["has_ball"] is True
        assert gsm.state.players["team_a_1"]["has_ball"] is False  # Previous carrier cleared
        assert gsm.state.ball["possession"] == "team_b"

        # Verify all other players have has_ball False
        for pid in gsm.state.players:
            if pid != "team_b_3":
                assert gsm.state.players[pid]["has_ball"] is False


# ---------------------------------------------------------------------------
# AC-4: transfer_possession to None (AC-GSM-10) - clears ALL 3 slots
# ---------------------------------------------------------------------------


class TestAC4TransferPossessionToNone:
    """Test AC-4: transfer_possession to None (AC-GSM-10) - clears all 3 slots."""

    def test_transfer_possession_to_none_clears_all_three_slots(self):
        """transfer_possession(player, None) must clear carrier_id, all has_ball flags, and possession."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: team_a_2 starts with ball
        gsm.transfer_possession(None, "team_a_2")
        assert gsm.state.ball["carrier_id"] == "team_a_2"
        assert gsm.state.players["team_a_2"]["has_ball"] is True
        assert gsm.state.ball["possession"] == "team_a"

        # Act: transfer to None
        gsm.transfer_possession("team_a_2", None)

        # Assert: ALL THREE slots cleared
        # 1. carrier_id is None
        assert gsm.state.ball["carrier_id"] is None

        # 2. all 10 has_ball flags are False
        for pid in gsm.state.players:
            assert gsm.state.players[pid]["has_ball"] is False

        # 3. possession is None
        assert gsm.state.ball["possession"] is None


# ---------------------------------------------------------------------------
# AC-5: transfer_possession no-op (EC-GSM-03)
# ---------------------------------------------------------------------------


class TestAC5TransferPossessionNoOp:
    """Test AC-5: transfer_possession no-op (EC-GSM-03) - (None, None) does nothing."""

    def test_transfer_possession_none_to_none_is_noop(self, caplog):
        """transfer_possession(None, None) should be a no-op with no warning."""
        caplog.set_level(logging.WARNING)
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: initial state (no possession)
        initial_carrier = gsm.state.ball["carrier_id"]
        initial_possession = gsm.state.ball["possession"]
        initial_has_ball_state = {pid: pdata["has_ball"] for pid, pdata in gsm.state.players.items()}

        # Act: no-op transfer
        gsm.transfer_possession(None, None)

        # Assert: no state change
        assert gsm.state.ball["carrier_id"] == initial_carrier
        assert gsm.state.ball["possession"] == initial_possession
        for pid, pdata in gsm.state.players.items():
            assert pdata["has_ball"] == initial_has_ball_state[pid]

        # Assert: no warning logged
        assert not any("transfer_possession" in record.message for record in caplog.records)


# ---------------------------------------------------------------------------
# AC-6: stale from_id WARNING (EC-GSM-04)
# ---------------------------------------------------------------------------


class TestAC6StaleFromIdWarning:
    """Test AC-6: stale from_id WARNING (EC-GSM-04) - still transfers with warning."""

    def test_stale_from_id_warning_but_transfer_applied(self, caplog):
        """Stale from_id should log WARNING but still apply the transfer."""
        caplog.set_level(logging.WARNING)
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: set up team_a_2 as actual carrier
        gsm.transfer_possession(None, "team_a_2")
        assert gsm.state.ball["carrier_id"] == "team_a_2"

        # Act: transfer with stale from_id (team_b_0 doesn't have ball)
        gsm.transfer_possession("team_b_0", "team_a_3")

        # Assert: warning logged with specific substrings
        warning_logged = any(
            "from_id=team_b_0" in record.message and "actual carrier=team_a_2" in record.message
            for record in caplog.records if record.levelno == logging.WARNING
        )
        assert warning_logged

        # Assert: transfer happened despite stale from_id
        assert gsm.state.ball["carrier_id"] == "team_a_3"
        assert gsm.state.players["team_a_3"]["has_ball"] is True
        assert gsm.state.players["team_a_2"]["has_ball"] is False
        assert gsm.state.ball["possession"] == "team_a"


# ---------------------------------------------------------------------------
# AC-7: transfer_possession switches teams
# ---------------------------------------------------------------------------


class TestAC7TransferPossessionTeamSwitch:
    """Test AC-7: transfer_possession switches teams - possession derived correctly."""

    def test_transfer_possession_derives_possession_from_carrier_team(self):
        """Possession should be derived from the new carrier's team."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Act: give ball to team_b player
        gsm.transfer_possession(None, "team_b_1")

        # Assert: possession derived from team_b
        assert gsm.state.ball["possession"] == "team_b"
        assert gsm.state.ball["carrier_id"] == "team_b_1"

        # Act: transfer to team_a player
        gsm.transfer_possession("team_b_1", "team_a_4")

        # Assert: possession switched to team_a
        assert gsm.state.ball["possession"] == "team_a"
        assert gsm.state.ball["carrier_id"] == "team_a_4"


# ---------------------------------------------------------------------------
# AC-8: update_ball_position basic
# ---------------------------------------------------------------------------


class TestAC8UpdateBallPositionBasic:
    """Test AC-8: update_ball_position basic - in-bounds update."""

    def test_update_ball_position_in_bounds_updates_position(self):
        """update_ball_position should update ball position when in bounds."""
        gsm = GameStateManager(_create_test_config(field_width=100.0, field_height=60.0), _create_test_anchors())

        # Arrange: ball starts at center (50, 30)
        assert gsm.state.ball["position"] == (50.0, 30.0)

        # Act: move ball to new in-bounds position
        gsm.update_ball_position((75.0, 45.0))

        # Assert: position updated
        assert gsm.state.ball["position"] == (75.0, 45.0)

    def test_update_ball_position_in_bounds_velocity_unchanged(self):
        """update_ball_position in-bounds should not affect velocity."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: set initial velocity
        gsm.state.ball["velocity"] = (5.0, -3.0)

        # Act: move ball (in bounds)
        gsm.update_ball_position((25.0, 15.0))

        # Assert: velocity unchanged
        assert gsm.state.ball["velocity"] == (5.0, -3.0)

    def test_update_ball_position_updates_last_touching_team(self):
        """update_ball_position should update _last_touching_team when provided."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: initial _last_touching_team is None
        assert gsm.state._last_touching_team is None

        # Act: update with last_touching_team
        gsm.update_ball_position((30.0, 20.0), last_touching_team="team_a")

        # Assert: _last_touching_team updated
        assert gsm.state._last_touching_team == "team_a"


# ---------------------------------------------------------------------------
# AC-9/10/11: OOB handling MOVED to ARE Phase 7 `_apply_oob_restart` per
# 2026-04-23. The original GSM auto-clamping + nearest-opponent
# possession-award conflicted with ARE's FIFA Laws 15-17 restart logic
# (throw-in / goal kick / corner) — both layers tried to handle OOB,
# producing carrier-ball position mismatches surfaced in the 10-round
# strategy iteration. GSM.update_ball_position is now a pure setter.
# OOB-restart contract is covered by ARE Phase 7 tests.


class TestAC9UpdateBallPositionIsPureSetter:
    """Per 2026-04-23: update_ball_position no longer handles OOB.
    Setting an out-of-field value just records that value verbatim;
    ARE Phase 7 detects OOB via BPS's `out_of_bounds` flag and routes
    through `_apply_oob_restart`."""

    def test_oob_position_set_verbatim_no_clamp(self):
        gsm = GameStateManager(_create_test_config(seed=0, field_width=100.0, field_height=60.0), _create_test_anchors())
        gsm.update_ball_position((-5.0, 30.0))
        # No clamp: position is whatever was passed in.
        assert gsm.state.ball["position"] == (-5.0, 30.0)
        # No auto-possession-transfer.
        assert gsm.state.ball["carrier_id"] is None
        assert gsm.state.ball["possession"] is None

    def test_last_touching_team_still_recorded(self):
        gsm = GameStateManager(_create_test_config(field_width=100.0, field_height=60.0), _create_test_anchors())
        gsm.update_ball_position((105.0, 30.0), last_touching_team="team_a")
        assert gsm.state._last_touching_team == "team_a"


# ---------------------------------------------------------------------------
# AC-12: update_ball_velocity
# ---------------------------------------------------------------------------


class TestAC12UpdateBallVelocity:
    """Test AC-12: update_ball_velocity - direct setter."""

    def test_update_ball_velocity_sets_velocity_directly(self):
        """update_ball_velocity should set ball velocity directly."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: initial velocity is (0, 0)
        assert gsm.state.ball["velocity"] == (0.0, 0.0)

        # Act: set new velocity
        gsm.update_ball_velocity((12.5, -8.0))

        # Assert: velocity updated
        assert gsm.state.ball["velocity"] == (12.5, -8.0)

    def test_update_ball_velocity_does_not_affect_position(self):
        """update_ball_velocity should not change ball position."""
        gsm = GameStateManager(_create_test_config(field_width=100.0, field_height=60.0), _create_test_anchors())

        # Arrange: note initial position
        initial_pos = gsm.state.ball["position"]
        assert initial_pos == (50.0, 30.0)

        # Act: update velocity
        gsm.update_ball_velocity((5.0, 5.0))

        # Assert: position unchanged
        assert gsm.state.ball["position"] == initial_pos


# ---------------------------------------------------------------------------
# AC-13: record_goal increments score (AC-GSM-13)
# ---------------------------------------------------------------------------


class TestAC13RecordGoalIncrementsScore:
    """Test AC-13: record_goal increments score (AC-GSM-13) - IN_PLAY context."""

    def test_record_goal_increments_team_a_score_in_play_phase(self, caplog):
        """record_goal should increment score for team_a in IN_PLAY phase without error."""
        caplog.set_level(logging.ERROR)
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: set phase to IN_PLAY
        gsm.state.phase = "IN_PLAY"
        initial_score_a = gsm.state.score["team_a"]
        initial_score_b = gsm.state.score["team_b"]

        # Act: record goal for team_a
        gsm.record_goal("team_a")

        # Assert: score incremented, no error logged
        assert gsm.state.score["team_a"] == initial_score_a + 1
        assert gsm.state.score["team_b"] == initial_score_b  # unchanged
        assert not any("record_goal" in record.message for record in caplog.records if record.levelno == logging.ERROR)

    def test_record_goal_multiple_goals_accumulate(self):
        """record_goal should accumulate multiple goals for same team."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        gsm.state.phase = "IN_PLAY"

        # Act: record multiple goals
        gsm.record_goal("team_b")
        gsm.record_goal("team_b")
        gsm.record_goal("team_a")

        # Assert: scores accumulate correctly
        assert gsm.state.score["team_a"] == 1
        assert gsm.state.score["team_b"] == 2

    def test_record_goal_both_teams_independently(self):
        """record_goal should work independently for both teams."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())
        gsm.state.phase = "IN_PLAY"

        # Act: alternate goals between teams
        gsm.record_goal("team_a")
        gsm.record_goal("team_b")
        gsm.record_goal("team_a")

        # Assert: both teams' scores tracked independently
        assert gsm.state.score["team_a"] == 2
        assert gsm.state.score["team_b"] == 1


# ---------------------------------------------------------------------------
# AC-14: record_goal in non-IN_PLAY logs ERROR (EC-GSM-07)
# ---------------------------------------------------------------------------


class TestAC14RecordGoalNonInPlayError:
    """Test AC-14: record_goal in non-IN_PLAY logs ERROR (EC-GSM-07) - but score still applies."""

    def test_record_goal_in_pre_match_logs_error_but_applies_score(self, caplog):
        """record_goal in PRE_MATCH should log ERROR but still increment score."""
        caplog.set_level(logging.ERROR)
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: phase is PRE_MATCH by default
        assert gsm.state.phase == "PRE_MATCH"
        initial_score = gsm.state.score["team_a"]

        # Act: record goal in wrong phase
        gsm.record_goal("team_a")

        # Assert: score incremented despite wrong phase
        assert gsm.state.score["team_a"] == initial_score + 1

        # Assert: ERROR logged with specific substrings
        error_logged = any(
            "record_goal" in record.message and "phase=PRE_MATCH" in record.message
            for record in caplog.records if record.levelno == logging.ERROR
        )
        assert error_logged

    def test_record_goal_in_goal_scored_phase_logs_error(self, caplog):
        """record_goal in GOAL_SCORED phase should log ERROR."""
        caplog.set_level(logging.ERROR)
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Arrange: set phase to GOAL_SCORED
        gsm.state.phase = "GOAL_SCORED"

        # Act: record goal
        gsm.record_goal("team_b")

        # Assert: ERROR logged
        error_logged = any(
            "record_goal" in record.message and "phase=GOAL_SCORED" in record.message
            for record in caplog.records if record.levelno == logging.ERROR
        )
        assert error_logged

        # Assert: score still applies
        assert gsm.state.score["team_b"] == 1


# ---------------------------------------------------------------------------
# AC-15: mutations don't break snapshot contract
# ---------------------------------------------------------------------------


class TestAC15MutationsDontBreakSnapshotContract:
    """Test AC-15: mutations don't break snapshot contract - post-mutation snapshot works."""

    def test_mutations_observable_via_snapshot(self):
        """Post-mutation state should be correctly reflected in snapshot."""
        gsm = GameStateManager(_create_test_config(field_width=100.0, field_height=60.0), _create_test_anchors())

        # Act: perform multiple mutations
        gsm.apply_move("team_a_1", (35.0, 25.0))
        gsm.transfer_possession(None, "team_b_2")
        gsm.record_goal("team_a")

        # Act: get snapshot after mutations
        snapshot = gsm.build_tick_snapshot()

        # Assert: all mutations reflected in snapshot
        # 1. apply_move reflected
        assert snapshot["players"]["team_a_1"]["position"] == (35.0, 25.0)

        # 2. transfer_possession reflected
        assert snapshot["ball"]["carrier_id"] == "team_b_2"
        assert snapshot["ball"]["possession"] == "team_b"
        assert snapshot["players"]["team_b_2"]["has_ball"] is True
        # All other players don't have ball
        for pid, pdata in snapshot["players"].items():
            if pid != "team_b_2":
                assert pdata["has_ball"] is False

        # 3. record_goal reflected
        assert snapshot["score"]["team_a"] == 1
        assert snapshot["score"]["team_b"] == 0

    def test_snapshot_build_player_state_after_mutations(self):
        """build_player_state should work correctly after mutations."""
        gsm = GameStateManager(_create_test_config(), _create_test_anchors())

        # Act: mutate and get player state
        gsm.apply_move("team_a_0", (15.0, 25.0))
        gsm.transfer_possession(None, "team_a_0")

        player_state = gsm.build_player_state("team_a_0")

        # Assert: mutations reflected in player state
        assert player_state["position"] == (15.0, 25.0)
        assert player_state["has_ball"] is True