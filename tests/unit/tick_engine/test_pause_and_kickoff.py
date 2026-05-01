"""
Test pause-tick execution and kickoff setup (Story 006).

Tests the _handle_pause_tick and _setup_kickoff methods using the direct helper
call pattern proven successful in Story 005.
"""

from unittest.mock import MagicMock

from src.orchestration.tick_engine.engine import TickEngine


class TestHandlePauseTick:
    """Test _handle_pause_tick method."""

    def test_goal_pause_decrement(self):
        """Goal pause counter decrements each call."""
        engine = TickEngine()
        engine._goal_pause_remaining = 5
        engine._conceding_team = "team_a"

        gsm = MagicMock()
        gsm.tick = 50
        gsm.state.total_ticks = 100
        gsm.get_phase.return_value = "goal_scored"
        log = MagicMock()
        config = MagicMock()

        engine._handle_pause_tick(gsm, log, config)

        assert engine._goal_pause_remaining == 4
        gsm.set_phase.assert_not_called()  # pause not done yet

    def test_goal_pause_completion_to_kickoff(self):
        """Goal pause completion transitions to kickoff when time remaining."""
        engine = TickEngine()
        engine._goal_pause_remaining = 1
        engine._conceding_team = "team_a"

        gsm = MagicMock()
        gsm.tick = 50
        gsm.total_ticks = 100  # Property, not nested attribute
        gsm.get_phase.return_value = "goal_scored"
        gsm.state.field_width = 100.0
        gsm.state.field_height = 60.0
        gsm.state._anchors = {f"team_a_{i}": (50.0 + i, 30.0) for i in range(5)}
        gsm.state._anchors.update({f"team_b_{i}": (50.0 + i, 30.0) for i in range(5)})
        gsm.state.ball = {"carrier_id": None}
        log = MagicMock()
        config = MagicMock()

        engine._handle_pause_tick(gsm, log, config)

        assert engine._goal_pause_remaining == 0
        log.record_phase_transition.assert_called_with(50, "goal_scored", "kick_off")

    def test_goal_pause_completion_to_full_time(self):
        """Goal pause completion at time expiry transitions to FULL_TIME."""
        engine = TickEngine()
        engine._goal_pause_remaining = 1
        engine._conceding_team = "team_a"

        gsm = MagicMock()
        gsm.tick = 100
        gsm.total_ticks = 100  # Property, not nested attribute
        gsm.get_phase.return_value = "goal_scored"
        log = MagicMock()
        config = MagicMock()

        engine._handle_pause_tick(gsm, log, config)

        assert engine._goal_pause_remaining == 0
        gsm.set_phase.assert_called_with("FULL_TIME")
        log.record_phase_transition.assert_called_with(100, "goal_scored", "full_time")

    def test_halftime_pause_decrement(self):
        """Half-time pause counter decrements each call."""
        engine = TickEngine()
        engine._halftime_pause_remaining = 3
        engine._second_half_kickoff_team = "team_b"

        gsm = MagicMock()
        gsm.get_phase.return_value = "half_time"
        log = MagicMock()
        config = MagicMock()

        engine._handle_pause_tick(gsm, log, config)

        assert engine._halftime_pause_remaining == 2
        gsm.swap_attack_direction.assert_not_called()  # pause not done yet

    def test_halftime_pause_completion(self):
        """Half-time pause completion swaps direction and sets up kickoff."""
        engine = TickEngine()
        engine._halftime_pause_remaining = 1
        engine._second_half_kickoff_team = "team_b"

        gsm = MagicMock()
        gsm.get_phase.return_value = "half_time"
        gsm.tick = 50
        gsm.total_ticks = 200
        gsm.state.field_width = 100.0
        gsm.state.field_height = 60.0
        gsm.state._anchors = {f"team_b_{i}": (25.0, 30.0 + i) for i in range(5)}
        gsm.state._anchors.update({f"team_a_{i}": (75.0, 30.0 + i) for i in range(5)})
        gsm.state.ball = {"carrier_id": None}
        log = MagicMock()
        config = MagicMock()

        engine._handle_pause_tick(gsm, log, config)

        assert engine._halftime_pause_remaining == 0
        gsm.swap_attack_direction.assert_called_once()
        log.record_phase_transition.assert_called_with(gsm.tick, "half_time", "kick_off")

    def test_case_insensitive_phase_comparison(self):
        """Phase comparisons are case-insensitive."""
        engine = TickEngine()
        engine._goal_pause_remaining = 3

        gsm = MagicMock()
        gsm.get_phase.return_value = "GOAL_SCORED"  # uppercase
        log = MagicMock()
        config = MagicMock()

        engine._handle_pause_tick(gsm, log, config)

        assert engine._goal_pause_remaining == 2


class TestSetupKickoff:
    """Test _setup_kickoff method."""

    def test_all_players_reset_to_anchors(self):
        """All 10 players are reset to their anchors."""
        engine = TickEngine()

        gsm = MagicMock()
        gsm.state.field_width = 100.0
        gsm.state.field_height = 60.0
        gsm.state._anchors = {}
        for i in range(5):
            gsm.state._anchors[f"team_a_{i}"] = (25.0 + i, 30.0)
            gsm.state._anchors[f"team_b_{i}"] = (75.0 + i, 30.0)
        gsm.state.ball = {"carrier_id": None}
        log = MagicMock()

        engine._setup_kickoff(gsm, log, "team_a")

        # Verify all 10 players were moved to anchors
        assert gsm.apply_move.call_count == 10
        for i in range(5):
            gsm.apply_move.assert_any_call(f"team_a_{i}", (25.0 + i, 30.0))
            gsm.apply_move.assert_any_call(f"team_b_{i}", (75.0 + i, 30.0))

    def test_ball_centered_and_zeroed(self):
        """Ball is positioned at center with zero velocity."""
        engine = TickEngine()

        gsm = MagicMock()
        gsm.state.field_width = 100.0
        gsm.state.field_height = 60.0
        gsm.state._anchors = {f"team_a_{i}": (25.0, 30.0) for i in range(5)}
        gsm.state._anchors.update({f"team_b_{i}": (75.0, 30.0) for i in range(5)})
        gsm.state.ball = {"carrier_id": None}
        log = MagicMock()

        engine._setup_kickoff(gsm, log, "team_a")

        gsm.update_ball_position.assert_called_with((50.0, 30.0))
        gsm.update_ball_velocity.assert_called_with((0.0, 0.0))

    def test_ball_carrier_cleared(self):
        """Ball carrier is cleared before assigning new possession."""
        engine = TickEngine()

        gsm = MagicMock()
        gsm.state.field_width = 100.0
        gsm.state.field_height = 60.0
        gsm.state._anchors = {f"team_a_{i}": (25.0, 30.0) for i in range(5)}
        gsm.state._anchors.update({f"team_b_{i}": (75.0, 30.0) for i in range(5)})
        gsm.state.ball = {"carrier_id": "team_b_2"}
        log = MagicMock()

        engine._setup_kickoff(gsm, log, "team_a")

        # First call clears carrier, second call assigns to kickoff player
        expected_calls = [
            ((("team_b_2", None),)),  # Clear existing carrier
            (((None, "team_a_0"),))   # Assign to kickoff player
        ]
        assert gsm.transfer_possession.call_count == 2
        gsm.transfer_possession.assert_any_call("team_b_2", None)
        gsm.transfer_possession.assert_any_call(None, "team_a_0")

    def test_kickoff_player_closest_to_center(self):
        """Kickoff player is the one closest to field center on kickoff team."""
        engine = TickEngine()

        gsm = MagicMock()
        gsm.state.field_width = 100.0
        gsm.state.field_height = 60.0
        # Set up anchors where team_a_2 is closest to center (50, 30)
        gsm.state._anchors = {
            "team_a_0": (20.0, 30.0),  # distance = 30
            "team_a_1": (40.0, 30.0),  # distance = 10
            "team_a_2": (48.0, 30.0),  # distance = 2 (closest)
            "team_a_3": (60.0, 30.0),  # distance = 10
            "team_a_4": (80.0, 30.0),  # distance = 30
        }
        gsm.state._anchors.update({f"team_b_{i}": (75.0, 30.0) for i in range(5)})
        gsm.state.ball = {"carrier_id": None}
        log = MagicMock()

        engine._setup_kickoff(gsm, log, "team_a")

        # team_a_2 should receive possession (closest to center)
        gsm.transfer_possession.assert_any_call(None, "team_a_2")

    def test_phase_set_to_kick_off(self):
        """Phase is set to KICK_OFF."""
        engine = TickEngine()

        gsm = MagicMock()
        gsm.state.field_width = 100.0
        gsm.state.field_height = 60.0
        gsm.state._anchors = {f"team_a_{i}": (25.0, 30.0) for i in range(5)}
        gsm.state._anchors.update({f"team_b_{i}": (75.0, 30.0) for i in range(5)})
        gsm.state.ball = {"carrier_id": None}
        log = MagicMock()

        engine._setup_kickoff(gsm, log, "team_a")

        gsm.set_phase.assert_called_with("KICK_OFF")

    def test_kickoff_team_b_selection(self):
        """Kickoff player selection works for team_b."""
        engine = TickEngine()

        gsm = MagicMock()
        gsm.state.field_width = 100.0
        gsm.state.field_height = 60.0
        gsm.state._anchors = {f"team_a_{i}": (25.0, 30.0) for i in range(5)}
        # Set up team_b anchors where team_b_1 is closest to center
        gsm.state._anchors.update({
            "team_b_0": (70.0, 30.0),  # distance = 20
            "team_b_1": (52.0, 30.0),  # distance = 2 (closest)
            "team_b_2": (60.0, 30.0),  # distance = 10
            "team_b_3": (80.0, 30.0),  # distance = 30
            "team_b_4": (90.0, 30.0),  # distance = 40
        })
        gsm.state.ball = {"carrier_id": None}
        log = MagicMock()

        engine._setup_kickoff(gsm, log, "team_b")

        # team_b_1 should receive possession
        gsm.transfer_possession.assert_any_call(None, "team_b_1")