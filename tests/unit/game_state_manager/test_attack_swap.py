"""
Tests for GameStateManager.swap_attack_direction() method (Story 005).

Covers all 9 acceptance criteria from the story implementation notes:
AC-1: Single swap mirrors goal_x (both team_a_goal_x and team_b_goal_x)
AC-2: Single swap mirrors formation_position for all 10 players, y unchanged
AC-3: _anchors mirrored too
AC-4: Live position UNCHANGED (only formation targets mirror)
AC-5: Double-call returns to original + WARNING with "called 2 times"
AC-6: Triple-call ends in mirrored state, WARNING only on even calls
AC-7: y-coordinates never mirrored across any number of calls
AC-8: Snapshot reflects swap (integration with Story 002)
AC-9: Symmetry of mirror (midline = fixed point)
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
# Test Classes for Each Acceptance Criterion
# ---------------------------------------------------------------------------


class TestAC1SingleSwapMirrorsGoalX:
    """AC-1: Single swap mirrors both goal_x values."""

    def test_single_swap_mirrors_team_a_goal_x(self):
        """team_a_goal_x should be mirrored from 0.0 to 100.0."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Verify initial state
        assert gsm.state.field["team_a_goal_x"] == 0.0
        assert gsm.state.field["team_b_goal_x"] == 100.0

        # Apply swap
        gsm.swap_attack_direction()

        # Verify both goals are mirrored
        assert gsm.state.field["team_a_goal_x"] == 100.0
        assert gsm.state.field["team_b_goal_x"] == 0.0

    def test_single_swap_mirrors_team_b_goal_x(self):
        """team_b_goal_x should be mirrored from 100.0 to 0.0."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Apply swap
        gsm.swap_attack_direction()

        # Verify team_b_goal_x specifically
        assert gsm.state.field["team_b_goal_x"] == 0.0

    def test_single_swap_no_warning_logged(self, caplog):
        """First call should not generate any warnings."""
        caplog.set_level(logging.WARNING)
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.swap_attack_direction()

        # No warnings should be logged
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) == 0


class TestAC2SingleSwapMirrorsFormationPositions:
    """AC-2: Single swap mirrors formation_position for all 10 players, y unchanged."""

    def test_single_swap_mirrors_team_a_0_formation_position(self):
        """team_a_0 at (8.0, 30.0) should mirror to (92.0, 30.0)."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Verify initial formation position
        assert gsm.state.players["team_a_0"]["formation_position"] == (8.0, 30.0)

        gsm.swap_attack_direction()

        # Verify mirrored position: 100.0 - 8.0 = 92.0
        assert gsm.state.players["team_a_0"]["formation_position"] == (92.0, 30.0)

    def test_single_swap_mirrors_team_a_4_formation_position(self):
        """team_a_4 at (60.0, 30.0) should mirror to (40.0, 30.0)."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Verify initial formation position
        assert gsm.state.players["team_a_4"]["formation_position"] == (60.0, 30.0)

        gsm.swap_attack_direction()

        # Verify mirrored position: 100.0 - 60.0 = 40.0
        assert gsm.state.players["team_a_4"]["formation_position"] == (40.0, 30.0)

    def test_single_swap_mirrors_all_10_players(self):
        """All 10 players should have their x-coordinates mirrored."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Record original positions
        original_positions = {
            pid: pstate["formation_position"]
            for pid, pstate in gsm.state.players.items()
        }

        gsm.swap_attack_direction()

        # Verify all players are mirrored
        for pid, original_pos in original_positions.items():
            current_pos = gsm.state.players[pid]["formation_position"]
            expected_x = 100.0 - original_pos[0]
            expected_y = original_pos[1]  # y unchanged
            assert current_pos == (expected_x, expected_y)

    def test_single_swap_y_coordinates_unchanged_for_all_players(self):
        """Y coordinates should remain unchanged for all 10 players."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Record original y coordinates
        original_y_coords = {
            pid: pstate["formation_position"][1]
            for pid, pstate in gsm.state.players.items()
        }

        gsm.swap_attack_direction()

        # Verify all y coordinates unchanged
        for pid, original_y in original_y_coords.items():
            current_y = gsm.state.players[pid]["formation_position"][1]
            assert current_y == original_y


class TestAC3AnchorsMirrored:
    """AC-3: _anchors internal dict is also mirrored."""

    def test_anchors_mirrored_team_a_0(self):
        """Internal _anchors dict should mirror team_a_0 from (8.0, 30.0) to (92.0, 30.0)."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Verify initial anchors
        assert gsm.state._anchors["team_a_0"] == (8.0, 30.0)

        gsm.swap_attack_direction()

        # Verify mirrored anchors
        assert gsm.state._anchors["team_a_0"] == (92.0, 30.0)

    def test_anchors_mirrored_all_players(self):
        """All _anchors should be mirrored."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Record original anchors
        original_anchors = dict(gsm.state._anchors)

        gsm.swap_attack_direction()

        # Verify all anchors are mirrored
        for pid, original_anchor in original_anchors.items():
            current_anchor = gsm.state._anchors[pid]
            expected_x = 100.0 - original_anchor[0]
            expected_y = original_anchor[1]  # y unchanged
            assert current_anchor == (expected_x, expected_y)


class TestAC4LivePositionUnchanged:
    """AC-4: Live position values stay where they are, only formation targets mirror."""

    def test_live_position_unchanged_after_swap(self):
        """Player's current position should NOT be mirrored, only formation_position."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Move player to mid-game position (simulating gameplay movement)
        gsm.state.players["team_a_0"]["position"] = (45.0, 25.0)

        # Record states before swap
        original_live_position = gsm.state.players["team_a_0"]["position"]
        original_formation_position = gsm.state.players["team_a_0"]["formation_position"]

        gsm.swap_attack_direction()

        # Verify live position is unchanged
        assert gsm.state.players["team_a_0"]["position"] == original_live_position
        assert gsm.state.players["team_a_0"]["position"] == (45.0, 25.0)

        # Verify formation position IS mirrored
        assert gsm.state.players["team_a_0"]["formation_position"] != original_formation_position
        expected_formation_x = 100.0 - original_formation_position[0]
        expected_formation_pos = (expected_formation_x, original_formation_position[1])
        assert gsm.state.players["team_a_0"]["formation_position"] == expected_formation_pos

    def test_multiple_players_live_positions_unchanged(self):
        """Multiple players' live positions should remain unchanged."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Move multiple players to mid-game positions
        gsm.state.players["team_a_0"]["position"] = (30.0, 10.0)
        gsm.state.players["team_a_3"]["position"] = (70.0, 45.0)
        gsm.state.players["team_b_1"]["position"] = (15.0, 35.0)

        # Record original live positions
        original_positions = {
            "team_a_0": gsm.state.players["team_a_0"]["position"],
            "team_a_3": gsm.state.players["team_a_3"]["position"],
            "team_b_1": gsm.state.players["team_b_1"]["position"],
        }

        gsm.swap_attack_direction()

        # Verify all live positions unchanged
        for pid, original_pos in original_positions.items():
            assert gsm.state.players[pid]["position"] == original_pos


class TestAC5DoubleCallReturnsToOriginal:
    """AC-5: Double-call returns to original + WARNING with 'called 2 times'."""

    def test_double_swap_returns_formation_positions_to_original(self):
        """After two swaps, all formation_position values return to original."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Record original formation positions
        original_formation_positions = {
            pid: pstate["formation_position"]
            for pid, pstate in gsm.state.players.items()
        }

        # Double swap
        gsm.swap_attack_direction()
        gsm.swap_attack_direction()

        # Verify all formation positions returned to original
        for pid, original_pos in original_formation_positions.items():
            assert gsm.state.players[pid]["formation_position"] == original_pos

    def test_double_swap_returns_goals_to_original(self):
        """After two swaps, both goal_x values return to original."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Record original goal positions
        original_team_a_goal_x = gsm.state.field["team_a_goal_x"]
        original_team_b_goal_x = gsm.state.field["team_b_goal_x"]

        # Double swap
        gsm.swap_attack_direction()
        gsm.swap_attack_direction()

        # Verify goals returned to original
        assert gsm.state.field["team_a_goal_x"] == original_team_a_goal_x
        assert gsm.state.field["team_b_goal_x"] == original_team_b_goal_x

    def test_double_swap_returns_anchors_to_original(self):
        """After two swaps, all _anchors return to original."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Record original anchors
        original_anchors = dict(gsm.state._anchors)

        # Double swap
        gsm.swap_attack_direction()
        gsm.swap_attack_direction()

        # Verify anchors returned to original
        assert gsm.state._anchors == original_anchors

    def test_double_swap_logs_warning_with_count(self, caplog):
        """Second call should log WARNING mentioning 'called 2 times'."""
        caplog.set_level(logging.WARNING)
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # First call - no warning
        gsm.swap_attack_direction()
        assert len([r for r in caplog.records if r.levelno == logging.WARNING]) == 0

        # Second call - should warn
        gsm.swap_attack_direction()
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) == 1
        assert "called 2 times" in warnings[0].message

    def test_double_swap_no_exception_raised(self):
        """Double swap should complete without raising any exception."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Should not raise
        gsm.swap_attack_direction()
        gsm.swap_attack_direction()


class TestAC6TripleCallEndsInMirrored:
    """AC-6: Triple-call ends in mirrored state, WARNING only on even calls."""

    def test_triple_swap_matches_single_swap_result(self):
        """After 3 swaps, state should match single swap result."""
        config = _create_test_config()
        anchors = _create_test_anchors()

        # Create two GSMs with same config
        gsm_single = GameStateManager(config, anchors)
        gsm_triple = GameStateManager(config, anchors)

        # Single swap
        gsm_single.swap_attack_direction()

        # Triple swap
        gsm_triple.swap_attack_direction()
        gsm_triple.swap_attack_direction()
        gsm_triple.swap_attack_direction()

        # States should be identical
        assert gsm_single.state.field == gsm_triple.state.field
        assert gsm_single.state._anchors == gsm_triple.state._anchors
        for pid in gsm_single.state.players:
            assert (gsm_single.state.players[pid]["formation_position"] ==
                    gsm_triple.state.players[pid]["formation_position"])

    def test_triple_swap_warning_only_on_second_call(self, caplog):
        """Only the second call (even count) should log WARNING."""
        caplog.set_level(logging.WARNING)
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Call 1 - odd, no warning
        gsm.swap_attack_direction()
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) == 0

        # Call 2 - even, should warn
        gsm.swap_attack_direction()
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) == 1

        # Call 3 - odd, no new warning
        gsm.swap_attack_direction()
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) == 1  # Still just the one from call 2


class TestAC7YCoordinatesNeverMirrored:
    """AC-7: y-coordinates never mirrored across any number of calls."""

    def test_y_coordinates_invariant_across_multiple_swaps(self):
        """Y coordinates should remain unchanged after any number of swaps."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Record original y coordinates
        original_y_coords = {
            pid: pstate["formation_position"][1]
            for pid, pstate in gsm.state.players.items()
        }

        # Apply varying numbers of swaps to different test runs
        for num_swaps in [1, 2, 3, 4, 5]:
            # Reset GSM
            gsm = GameStateManager(config, anchors)

            # Apply swaps
            for _ in range(num_swaps):
                gsm.swap_attack_direction()

            # Verify y coordinates unchanged
            for pid, original_y in original_y_coords.items():
                current_y = gsm.state.players[pid]["formation_position"][1]
                assert current_y == original_y, f"Y changed after {num_swaps} swaps for {pid}"

    def test_varied_y_coordinates_stay_unchanged(self):
        """Test with non-standard y coordinates to ensure they're preserved."""
        config = _create_test_config()

        # Create anchors with varied y coordinates
        varied_anchors = {
            "team_a_0": (10.0, 5.0),
            "team_a_1": (25.0, 15.0),
            "team_a_2": (25.0, 45.0),
            "team_a_3": (50.0, 10.0),
            "team_a_4": (75.0, 55.0),
            "team_b_0": (90.0, 50.0),
            "team_b_1": (75.0, 40.0),
            "team_b_2": (75.0, 20.0),
            "team_b_3": (50.0, 35.0),
            "team_b_4": (25.0, 25.0),
        }

        gsm = GameStateManager(config, varied_anchors)

        # Record y coordinates
        original_y_coords = {
            pid: pstate["formation_position"][1]
            for pid, pstate in gsm.state.players.items()
        }

        # Single swap
        gsm.swap_attack_direction()

        # Verify all y coordinates unchanged
        for pid, original_y in original_y_coords.items():
            current_y = gsm.state.players[pid]["formation_position"][1]
            assert current_y == original_y


class TestAC8SnapshotReflectsSwap:
    """AC-8: Snapshot reflects swap (integration with Story 002)."""

    def test_snapshot_shows_mirrored_field_goals(self):
        """After swap, snapshot should show mirrored field.team_a_goal_x."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Get original snapshot
        s0 = gsm.build_tick_snapshot()
        original_team_a_goal_x = s0["field"]["team_a_goal_x"]

        # Apply swap and get new snapshot
        gsm.swap_attack_direction()
        s1 = gsm.build_tick_snapshot()

        # Verify snapshot reflects mirrored goal
        expected_team_a_goal_x = 100.0 - original_team_a_goal_x
        assert s1["field"]["team_a_goal_x"] == expected_team_a_goal_x

    def test_snapshot_shows_mirrored_formation_positions(self):
        """After swap, snapshot should show mirrored player formation_position."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Get original snapshot
        s0 = gsm.build_tick_snapshot()
        original_team_a_0_formation_x = s0["players"]["team_a_0"]["formation_position"][0]

        # Apply swap and get new snapshot
        gsm.swap_attack_direction()
        s1 = gsm.build_tick_snapshot()

        # Verify snapshot reflects mirrored formation position
        expected_formation_x = 100.0 - original_team_a_0_formation_x
        actual_formation_x = s1["players"]["team_a_0"]["formation_position"][0]
        assert actual_formation_x == expected_formation_x

    def test_snapshot_field_width_unchanged(self):
        """Field width itself should not change, only goal positions."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        s0 = gsm.build_tick_snapshot()
        gsm.swap_attack_direction()
        s1 = gsm.build_tick_snapshot()

        # Field dimensions should be unchanged
        assert s1["field"]["width"] == s0["field"]["width"]
        assert s1["field"]["height"] == s0["field"]["height"]


class TestAC9SymmetryOfMirror:
    """AC-9: Symmetry of mirror (midline = fixed point)."""

    def test_midline_formation_position_fixed_point(self):
        """Player at x=field_width/2 should stay at same position after swap."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Manually set a player at midline
        gsm.state.players["team_a_3"]["formation_position"] = (50.0, 30.0)

        gsm.swap_attack_direction()

        # Should remain at same position (midline fixed point)
        assert gsm.state.players["team_a_3"]["formation_position"] == (50.0, 30.0)

    def test_midline_anchor_fixed_point(self):
        """Anchor at x=field_width/2 should stay unchanged after swap."""
        config = _create_test_config(field_width=100.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Set anchor at midline
        gsm.state._anchors["team_a_3"] = (50.0, 30.0)

        gsm.swap_attack_direction()

        # Should remain at same position
        assert gsm.state._anchors["team_a_3"] == (50.0, 30.0)

    def test_various_field_widths_midline_fixed_point(self):
        """Test midline fixed point property with different field widths."""
        for field_width in [80.0, 120.0, 200.0]:
            config = _create_test_config(field_width=field_width)
            anchors = _create_test_anchors()
            gsm = GameStateManager(config, anchors)

            midline_x = field_width / 2.0

            # Set player at midline
            gsm.state.players["team_a_2"]["formation_position"] = (midline_x, 25.0)

            gsm.swap_attack_direction()

            # Should remain at midline
            assert gsm.state.players["team_a_2"]["formation_position"] == (midline_x, 25.0)