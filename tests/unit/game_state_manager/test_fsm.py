"""
Tests for Game State Manager FSM functionality (Story 004).

Tests all 12 acceptance criteria from
production/epics/game-state-manager/story-004-match-fsm.md:

AC-1: start_match transitions PRE_MATCH → KICK_OFF
AC-2: start_match in non-PRE_MATCH logs ERROR + no-op
AC-3: KICK_OFF → IN_PLAY transition
AC-4: record_goal + GOAL_SCORED + reset sequence
AC-5: Half-time transition advances state.half
AC-6: advance_tick basic functionality
AC-7: advance_tick FULL_TIME guard
AC-8: set_phase to FULL_TIME terminal guard
AC-9: set_phase to FULL_TIME from any earlier state allowed
AC-10: FULL_TIME during pause clamp
AC-11: reset_to_kickoff conceding team gets ball
AC-12: state.half stays 1 on goal during first half
"""

from __future__ import annotations
import pytest

from src.core.game_state_manager import GameStateManager
from tests.unit.game_state_manager.conftest import (
    _create_test_config,
    _create_test_anchors,
)


class TestAC1StartMatchTransition:
    """Test AC-1: start_match transitions PRE_MATCH → KICK_OFF (AC-GSM-11)."""

    def test_start_match_transitions_to_kick_off(self):
        """AC-1: start_match should set phase=KICK_OFF."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        assert gsm.state.phase == "PRE_MATCH"
        gsm.start_match()
        assert gsm.state.phase == "KICK_OFF"

    def test_start_match_ball_at_center(self):
        """AC-1: start_match should position ball at field center."""
        config = _create_test_config(field_width=100.0, field_height=60.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.start_match()
        expected_center = (50.0, 30.0)  # field_width/2, field_height/2
        assert gsm.state.ball["position"] == expected_center
        assert gsm.state.ball["velocity"] == (0.0, 0.0)

    def test_start_match_all_players_at_legal_kickoff_positions(self):
        """AC-1 (amended 2026-04-22, FIFA Law 8): formation_position is set
        from the anchor, but `position` is overridden to a legal kickoff
        state — kicker at center spot, all others in own half AND outside
        the center circle (radius = 9.15% of field width)."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.start_match()
        # Formation anchors stay equal to the input (used as soft-pull during play).
        for player_id, expected_anchor in anchors.items():
            assert gsm.state.players[player_id]["formation_position"] == expected_anchor

        # The kicker is at the center spot.
        kicker_id = gsm.state.ball["carrier_id"]
        assert kicker_id is not None
        center = (config.match.field_width / 2.0, config.match.field_height / 2.0)
        assert gsm.state.players[kicker_id]["position"] == center
        # Kicker is never the GK (FIFA Law 8).
        assert gsm.state.players[kicker_id]["role"] != "GK"

        # All other players are in their own half AND outside the center circle.
        circle_r = config.match.field_width * 0.0915
        for pid, pstate in gsm.state.players.items():
            if pid == kicker_id:
                continue
            x, y = pstate["position"]
            team_goal_x = gsm.state.field[f"{pstate['team']}_goal_x"]
            if team_goal_x < center[0]:
                assert x <= center[0], f"{pid} at x={x} crossed halfway line into opp half"
            else:
                assert x >= center[0], f"{pid} at x={x} crossed halfway line into opp half"
            d = ((x - center[0]) ** 2 + (y - center[1]) ** 2) ** 0.5
            assert d >= circle_r - 1e-6, f"{pid} at d={d:.3f} is inside center circle (r={circle_r})"

    def test_start_match_exactly_one_player_has_ball(self):
        """AC-1: start_match should give ball to exactly one player from kickoff team."""
        config = _create_test_config(seed=0)  # seed=0 → team_a kicks off
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.start_match()

        players_with_ball = [
            pid for pid, pstate in gsm.state.players.items()
            if pstate["has_ball"]
        ]
        assert len(players_with_ball) == 1

        kickoff_player = players_with_ball[0]
        assert gsm.state.players[kickoff_player]["team"] == gsm.state._kickoff_team


class TestAC2StartMatchErrorGuard:
    """Test AC-2: start_match in non-PRE_MATCH logs ERROR + no-op."""

    def test_start_match_in_in_play_logs_error(self, caplog):
        """AC-2: start_match in IN_PLAY should log ERROR and be no-op."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Directly set phase to IN_PLAY (test-only mutation)
        gsm.state.phase = "IN_PLAY"

        gsm.start_match()

        # Phase should stay IN_PLAY
        assert gsm.state.phase == "IN_PLAY"

        # Should log ERROR with specific substrings
        assert "start_match" in caplog.text
        assert "phase=IN_PLAY" in caplog.text


class TestAC3KickOffToInPlay:
    """Test AC-3: KICK_OFF → IN_PLAY transition (AC-GSM-12)."""

    def test_kick_off_to_in_play_transition(self):
        """AC-3: advance_tick + set_phase should work correctly."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.start_match()
        assert gsm.state.phase == "KICK_OFF"
        assert gsm.state.tick == 0

        gsm.advance_tick()
        assert gsm.state.tick == 1

        gsm.set_phase("IN_PLAY")
        assert gsm.state.phase == "IN_PLAY"


class TestAC4RecordGoalResetSequence:
    """Test AC-4: record_goal + GOAL_SCORED + reset sequence (AC-GSM-13)."""

    def test_full_goal_sequence(self):
        """AC-4: Full goal sequence ending with proper reset state."""
        config = _create_test_config(tick_rate=1, duration_minutes=1)  # total_ticks=60
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Setup: start match and advance to IN_PLAY
        gsm.start_match()
        gsm.advance_tick()  # tick=1
        gsm.set_phase("IN_PLAY")
        gsm.advance_tick()  # tick=2

        # Goal sequence
        gsm.record_goal("team_a")
        gsm.set_phase("GOAL_SCORED")
        gsm.advance_tick()  # tick=3
        gsm.reset_to_kickoff("team_b")  # conceding team kicks off
        gsm.advance_tick()  # tick=4
        gsm.set_phase("KICK_OFF")

        # Verify final state
        assert gsm.state.score == {"team_a": 1, "team_b": 0}
        assert gsm.state.phase == "KICK_OFF"
        assert gsm.state.tick == 4

        # All players should be back to legal kickoff positions (FIFA Law 8,
        # 2026-04-22). Formation_position still equals the static anchor —
        # only `position` is overridden for kickoff.
        for player_id, expected_anchor in anchors.items():
            assert gsm.state.players[player_id]["formation_position"] == expected_anchor
        # Kicker (whoever has the ball after reset_to_kickoff) is at the
        # center spot, others outside the center circle in their own half.
        kicker_id = gsm.state.ball["carrier_id"]
        center = (config.match.field_width / 2.0, config.match.field_height / 2.0)
        assert gsm.state.players[kicker_id]["position"] == center

        # Ball should be at center
        expected_center = (config.match.field_width / 2.0, config.match.field_height / 2.0)
        assert gsm.state.ball["position"] == expected_center

        # One team_b player should have ball
        players_with_ball = [
            pid for pid, pstate in gsm.state.players.items()
            if pstate["has_ball"] and pstate["team"] == "team_b"
        ]
        assert len(players_with_ball) == 1


class TestAC5HalfTime:
    """Test AC-5: Half-time transition advances state.half (AC-GSM-14)."""

    def test_half_time_advances_half_counter(self):
        """AC-5: HALF_TIME → KICK_OFF should advance half from 1 to 2."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        assert gsm.state.half == 1

        gsm.set_phase("HALF_TIME")
        assert gsm.state.half == 1  # Should not change until KICK_OFF

        gsm.set_phase("KICK_OFF")
        assert gsm.state.half == 2  # Now it should advance


class TestAC6AdvanceTickBasic:
    """Test AC-6: advance_tick basic functionality."""

    def test_advance_tick_increments_counter(self):
        """AC-6: advance_tick should increment tick counter."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        assert gsm.state.tick == 0

        for expected_tick in range(1, 6):
            gsm.advance_tick()
            assert gsm.state.tick == expected_tick


class TestAC7AdvanceTickFullTimeGuard:
    """Test AC-7: advance_tick FULL_TIME guard (AC-GSM-15)."""

    def test_advance_tick_at_total_ticks_logs_warning(self, caplog):
        """AC-7: advance_tick at total_ticks should be no-op with WARNING."""
        config = _create_test_config(tick_rate=1, duration_minutes=1)  # total_ticks=60
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Set tick to total_ticks (test-only mutation)
        gsm.state.tick = gsm.state.total_ticks  # 60

        gsm.advance_tick()

        # Should stay at total_ticks
        assert gsm.state.tick == gsm.state.total_ticks

        # Should log WARNING with specific substrings
        assert "advance_tick" in caplog.text
        assert "total_ticks=60" in caplog.text


class TestAC8SetPhaseTerminalGuard:
    """Test AC-8: set_phase to FULL_TIME terminal guard."""

    def test_set_phase_after_full_time_logs_error(self, caplog):
        """AC-8: set_phase from FULL_TIME should log ERROR and refuse."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Set to FULL_TIME (test-only mutation)
        gsm.state.phase = "FULL_TIME"

        gsm.set_phase("KICK_OFF")

        # Should stay FULL_TIME
        assert gsm.state.phase == "FULL_TIME"

        # Should log ERROR with specific substring
        assert "after FULL_TIME" in caplog.text


class TestAC9SetPhaseToFullTimeAllowed:
    """Test AC-9: set_phase to FULL_TIME from any earlier state allowed."""

    def test_set_phase_to_full_time_from_in_play(self):
        """AC-9: set_phase to FULL_TIME should work from any phase."""
        config = _create_test_config(tick_rate=1, duration_minutes=1)  # total_ticks=60
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Set to IN_PLAY and total_ticks (test-only mutation)
        gsm.state.phase = "IN_PLAY"
        gsm.state.tick = gsm.state.total_ticks

        gsm.set_phase("FULL_TIME")
        assert gsm.state.phase == "FULL_TIME"


class TestAC10FullTimePauseClamp:
    """Test AC-10: FULL_TIME during pause clamp (AC-GSM-22)."""

    def test_set_phase_kick_off_at_total_ticks_clamps_to_full_time(self, caplog):
        """AC-10: set_phase to KICK_OFF at tick >= total_ticks should clamp to FULL_TIME."""
        config = _create_test_config(tick_rate=1, duration_minutes=1)  # total_ticks=60
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Set to GOAL_SCORED at total_ticks (test-only mutation)
        gsm.state.phase = "GOAL_SCORED"
        gsm.state.tick = gsm.state.total_ticks  # 60

        gsm.set_phase("KICK_OFF")

        # Should be clamped to FULL_TIME
        assert gsm.state.phase == "FULL_TIME"

        # Should log ERROR with specific substring
        assert "clamping to FULL_TIME" in caplog.text


class TestAC11ResetToKickoffConcedingTeam:
    """Test AC-11: reset_to_kickoff conceding team gets ball."""

    def test_reset_to_kickoff_team_b_kicker_gets_ball(self):
        """AC-11 (amended 2026-04-22, FIFA Law 8): reset_to_kickoff('team_b')
        gives the ball to a non-GK team_b player whose anchor is closest to
        center (typically the central midfielder), not necessarily team_b_0
        which is the GK. Exactly one player has the ball after the reset."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.reset_to_kickoff("team_b")

        # Ball position is the kicker's position = center spot.
        expected_center = (config.match.field_width / 2.0, config.match.field_height / 2.0)
        assert gsm.state.ball["position"] == expected_center

        # Exactly one team_b player has the ball, and they are not the GK.
        with_ball = [pid for pid, p in gsm.state.players.items() if p["has_ball"]]
        assert len(with_ball) == 1
        kicker_id = with_ball[0]
        assert gsm.state.players[kicker_id]["team"] == "team_b"
        assert gsm.state.players[kicker_id]["role"] != "GK"


class TestAC12HalfStaysOnGoals:
    """Test AC-12: state.half stays 1 on goal during first half."""

    def test_half_stays_one_during_goal_restart_sequence(self):
        """AC-12: goal restart should NOT change half (only HALF_TIME→KICK_OFF does)."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Setup: start in first half IN_PLAY
        gsm.state.phase = "IN_PLAY"
        gsm.state.half = 1

        # Goal restart sequence
        gsm.record_goal("team_a")
        assert gsm.state.half == 1

        gsm.set_phase("GOAL_SCORED")
        assert gsm.state.half == 1

        gsm.reset_to_kickoff("team_b")
        assert gsm.state.half == 1

        gsm.set_phase("KICK_OFF")
        assert gsm.state.half == 1  # Should STILL be 1 (not the HALF_TIME→KICK_OFF transition)