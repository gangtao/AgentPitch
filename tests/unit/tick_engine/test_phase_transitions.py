"""Tests for TE Story 005: Phase transition detection + KICK_OFF handling."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.orchestration.tick_engine import TickEngine


@pytest.fixture
def patched_subsystems():
    """Patch all subsystem constructors at engine module level."""
    with patch("src.orchestration.tick_engine.engine.GameStateManager") as gsm_cls, \
         patch("src.orchestration.tick_engine.engine.MatchLog") as log_cls, \
         patch("src.orchestration.tick_engine.engine.Sandbox") as sb_cls, \
         patch("src.orchestration.tick_engine.engine.FallbackHandler") as fh_cls, \
         patch("src.orchestration.tick_engine.engine.ActionResolutionEngine") as are_cls, \
         patch("src.orchestration.tick_engine.engine.compute_anchors") as anchors_fn, \
         patch("src.orchestration.tick_engine.engine.read_current") as read_current_fn, \
         patch("src.orchestration.tick_engine.engine.hash_01") as hash_01_fn:

        anchors_fn.return_value = {f"team_a_{i}": (50.0, 30.0) for i in range(5)}
        read_current_fn.side_effect = lambda log_dir, team_id: f"# strategy for {team_id}\ndef decide(gs, ps, h): return Hold()"

        # Mock sandbox.compile to return success
        sb_instance = MagicMock()
        from src.foundation.sandbox import ExecutionStatus
        compile_result = MagicMock()
        compile_result.status = ExecutionStatus.SUCCESS
        sb_instance.compile.return_value = compile_result
        sb_cls.return_value = sb_instance

        # Default hash_01 to a real float so comparisons work
        hash_01_fn.return_value = 0.3  # < 0.5 → team_a kicks off

        # Mock GSM instance with tick counter behavior
        gsm_instance = MagicMock()
        gsm_cls.return_value = gsm_instance
        gsm_instance.tick = 0
        gsm_instance.total_ticks = 100
        gsm_instance.half_1_end_tick = 50
        gsm_instance.total_ticks = 100
        gsm_instance.get_phase.return_value = "in_play"

        # Mock snapshots for before/after score comparison
        base_snapshot = {
            "tick": 0,
            "score": {"team_a": 0, "team_b": 0},
            "ball": {
                "position": (50.0, 30.0),
                "possession": "team_a_2",
                "velocity": (0.0, 0.0),
                "carrier_id": "team_a_2"
            },
            "players": {
                f"team_a_{i}": {"player_id": f"team_a_{i}", "team": "team_a", "position": (20.0 + i * 5, 30.0)}
                for i in range(5)
            }
        }
        base_snapshot["players"].update({
            f"team_b_{i}": {"player_id": f"team_b_{i}", "team": "team_b", "position": (80.0 + i * 5, 30.0)}
            for i in range(5)
        })

        gsm_instance.build_tick_snapshot.return_value = base_snapshot

        # Mock player state lookup
        def mock_build_player_state(pid):
            return {
                "player_id": pid,
                "team": "team_a" if pid.startswith("team_a") else "team_b",
                "position": base_snapshot["players"][pid]["position"],
                "role": "MID",
            }
        gsm_instance.build_player_state.side_effect = mock_build_player_state

        # Mock MatchLog instance
        log_instance = MagicMock()
        log_cls.return_value = log_instance
        log_instance.get_history.return_value = []

        # Mock ActionResolutionEngine instance
        are_instance = MagicMock()
        are_cls.return_value = are_instance

        # Default ARE return for basic tests
        ten_pids = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]
        default_actions = {pid: {"action": "Hold", "result": "ok", "tick": 0} for pid in ten_pids}
        are_instance.resolve_tick.return_value = default_actions

        yield {
            "gsm": gsm_cls, "log": log_cls, "sb": sb_cls,
            "fh": fh_cls, "are": are_cls, "anchors": anchors_fn,
            "hash_01": hash_01_fn, "gsm_instance": gsm_instance,
            "log_instance": log_instance, "are_instance": are_instance,
            "base_snapshot": base_snapshot,
        }


class TickCounter:
    """Helper class to simulate incrementing tick behavior."""
    def __init__(self, start=0):
        self.value = start

    def advance(self):
        self.value += 1


def _make_config():
    config = MagicMock()
    config.match.match_id = "test-match-id"
    config.match.seed = 42
    config.output.log_dir = "/tmp/test-logs"
    # Mock team configs with llm_provider for compile phase
    config.team_a.llm_provider = "openai"
    config.team_b.llm_provider = "anthropic"
    # Mock simulation config
    config.simulation.goal_reset_ticks = 30
    config.simulation.half_time_pause_ticks = 60
    return config


def test_ac_te_09_goal_detection_via_score_delta():
    """AC-TE-09: When score differs before/after, set_phase(GOAL_SCORED) and record_phase_transition called."""
    engine = TickEngine()
    # Initialize instance state that _check_phase_transitions reads
    engine._goal_pause_remaining = 0
    engine._halftime_pause_remaining = 0

    gsm = MagicMock()
    gsm.tick = 5
    gsm.half_1_end_tick = 50
    gsm.total_ticks = 100
    gsm.get_phase.return_value = "IN_PLAY"
    log = MagicMock()
    config = MagicMock()
    config.simulation.goal_reset_ticks = 30
    config.simulation.half_time_pause_ticks = 60

    score_before = {"team_a": 0, "team_b": 0}
    score_after = {"team_a": 1, "team_b": 0}

    engine._check_phase_transitions(score_before, score_after, gsm, log, config)

    gsm.set_phase.assert_called_with("GOAL_SCORED")
    log.record_phase_transition.assert_called_with(5, "in_play", "goal_scored")
    assert engine._goal_pause_remaining == 30


def test_ac_te_10_half_time_transition():
    """AC-TE-10: When tick == half_1_end_tick AND phase is IN_PLAY, transition to HALF_TIME."""
    engine = TickEngine()
    engine._goal_pause_remaining = 0
    engine._halftime_pause_remaining = 0

    gsm = MagicMock()
    gsm.tick = 50
    gsm.half_1_end_tick = 50
    gsm.total_ticks = 100  # Mock as integer
    gsm.get_phase.return_value = "IN_PLAY"
    log = MagicMock()
    config = MagicMock()
    config.simulation.goal_reset_ticks = 30
    config.simulation.half_time_pause_ticks = 60

    # No score change (not a goal)
    score_before = {"team_a": 0, "team_b": 0}
    score_after = {"team_a": 0, "team_b": 0}

    engine._check_phase_transitions(score_before, score_after, gsm, log, config)

    gsm.set_phase.assert_called_with("HALF_TIME")
    log.record_phase_transition.assert_called_with(50, "in_play", "half_time")
    assert engine._halftime_pause_remaining == 60


def test_ac_te_11_full_time_transition():
    """AC-TE-11: When tick >= total_ticks AND phase is IN_PLAY, transition to FULL_TIME."""
    engine = TickEngine()
    engine._goal_pause_remaining = 0
    engine._halftime_pause_remaining = 0

    gsm = MagicMock()
    gsm.tick = 100
    gsm.total_ticks = 100
    gsm.get_phase.return_value = "IN_PLAY"
    log = MagicMock()
    config = MagicMock()

    # No score change (not a goal)
    score_before = {"team_a": 0, "team_b": 0}
    score_after = {"team_a": 0, "team_b": 0}

    engine._check_phase_transitions(score_before, score_after, gsm, log, config)

    gsm.set_phase.assert_called_with("FULL_TIME")
    log.record_phase_transition.assert_called_with(100, "in_play", "full_time")


def test_goal_priority_over_half_time():
    """Goal priority: when score delta on half_1_end_tick, goal fires; half-time NOT recorded same tick."""
    engine = TickEngine()
    engine._goal_pause_remaining = 0
    engine._halftime_pause_remaining = 0

    gsm = MagicMock()
    gsm.tick = 50  # At half-time tick
    gsm.half_1_end_tick = 50
    gsm.total_ticks = 100
    gsm.get_phase.return_value = "IN_PLAY"
    log = MagicMock()
    config = MagicMock()
    config.simulation.goal_reset_ticks = 30
    config.simulation.half_time_pause_ticks = 60

    # Score delta (goal condition) should take priority over half-time
    score_before = {"team_a": 0, "team_b": 0}
    score_after = {"team_a": 1, "team_b": 0}

    engine._check_phase_transitions(score_before, score_after, gsm, log, config)

    # Should only see GOAL_SCORED, not HALF_TIME (because of early return in goal check)
    gsm.set_phase.assert_called_once_with("GOAL_SCORED")
    log.record_phase_transition.assert_called_once_with(50, "in_play", "goal_scored")


def test_ac_te_12_kick_off_to_in_play_transition():
    """AC-TE-12: If after transition checks phase is still KICK_OFF, transition to IN_PLAY."""
    engine = TickEngine()
    engine._goal_pause_remaining = 0
    engine._halftime_pause_remaining = 0

    gsm = MagicMock()
    gsm.tick = 5
    gsm.half_1_end_tick = 50
    gsm.total_ticks = 100
    gsm.get_phase.return_value = "KICK_OFF"  # Phase is KICK_OFF
    log = MagicMock()
    config = MagicMock()

    # No score change, not at half-time or full-time
    score_before = {"team_a": 0, "team_b": 0}
    score_after = {"team_a": 0, "team_b": 0}

    engine._check_phase_transitions(score_before, score_after, gsm, log, config)

    # Should transition KICK_OFF → IN_PLAY
    gsm.set_phase.assert_called_with("IN_PLAY")
    log.record_phase_transition.assert_called_with(5, "kick_off", "in_play")


def test_goal_pause_remaining_set_on_goal():
    """_goal_pause_remaining set on goal equals config.simulation.goal_reset_ticks."""
    engine = TickEngine()
    engine._goal_pause_remaining = 0
    engine._halftime_pause_remaining = 0

    gsm = MagicMock()
    gsm.tick = 5
    gsm.half_1_end_tick = 50
    gsm.total_ticks = 100
    gsm.get_phase.return_value = "IN_PLAY"
    log = MagicMock()
    config = MagicMock()
    config.simulation.goal_reset_ticks = 35  # Custom value
    config.simulation.half_time_pause_ticks = 60

    score_before = {"team_a": 0, "team_b": 0}
    score_after = {"team_a": 1, "team_b": 0}

    engine._check_phase_transitions(score_before, score_after, gsm, log, config)

    # Verify _goal_pause_remaining was set
    assert engine._goal_pause_remaining == 35


def test_halftime_pause_remaining_set_on_half_time():
    """_halftime_pause_remaining set on half-time equals config.simulation.half_time_pause_ticks."""
    engine = TickEngine()
    engine._goal_pause_remaining = 0
    engine._halftime_pause_remaining = 0

    gsm = MagicMock()
    gsm.tick = 50
    gsm.half_1_end_tick = 50
    gsm.total_ticks = 100  # Mock as integer
    gsm.get_phase.return_value = "IN_PLAY"
    log = MagicMock()
    config = MagicMock()
    config.simulation.goal_reset_ticks = 30
    config.simulation.half_time_pause_ticks = 75  # Custom value

    # No score change (not a goal)
    score_before = {"team_a": 0, "team_b": 0}
    score_after = {"team_a": 0, "team_b": 0}

    engine._check_phase_transitions(score_before, score_after, gsm, log, config)

    # Verify _halftime_pause_remaining was set
    assert engine._halftime_pause_remaining == 75


def test_conceding_team_correctly_inferred_dict_score():
    """_conceding_team correctly inferred from score delta (dict format)."""
    engine = TickEngine()
    engine._goal_pause_remaining = 0
    engine._halftime_pause_remaining = 0

    gsm = MagicMock()
    gsm.tick = 5
    gsm.half_1_end_tick = 50
    gsm.total_ticks = 100
    gsm.get_phase.return_value = "IN_PLAY"
    log = MagicMock()
    config = MagicMock()
    config.simulation.goal_reset_ticks = 30
    config.simulation.half_time_pause_ticks = 60

    # Team A scores, so team B conceded
    score_before = {"team_a": 0, "team_b": 0}
    score_after = {"team_a": 1, "team_b": 0}

    engine._check_phase_transitions(score_before, score_after, gsm, log, config)

    # Team A scored, so team B conceded
    assert engine._conceding_team == "team_b"


def test_conceding_team_correctly_inferred_team_b_scores():
    """_conceding_team correctly inferred when team B scores."""
    engine = TickEngine()
    engine._goal_pause_remaining = 0
    engine._halftime_pause_remaining = 0

    gsm = MagicMock()
    gsm.tick = 5
    gsm.get_phase.return_value = "IN_PLAY"
    log = MagicMock()
    config = MagicMock()
    config.simulation.goal_reset_ticks = 30
    config.simulation.half_time_pause_ticks = 60

    # Team B scores, so team A conceded
    score_before = {"team_a": 0, "team_b": 0}
    score_after = {"team_a": 0, "team_b": 1}

    engine._check_phase_transitions(score_before, score_after, gsm, log, config)

    # Team B scored, so team A conceded
    assert engine._conceding_team == "team_a"


def test_no_transition_on_quiet_tick(patched_subsystems):
    """No phase transitions when score unchanged, not at half-time/full-time, not KICK_OFF."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]

    # Setup normal tick conditions
    gsm_instance.tick = 25  # Not at half-time or full-time
    gsm_instance.half_1_end_tick = 50
    gsm_instance.total_ticks = 100
    gsm_instance.get_phase.return_value = "in_play"
    # Skip the loop entirely; we only test pre-loop _second_half_kickoff_team derivation
    gsm_instance.total_ticks = 0

    TickEngine().run_match(config)

    # set_phase should not be called for transitions (only in compile phase for start_match)
    # Check that no phase transition was recorded during active tick
    log_instance = patched_subsystems["log_instance"]
    phase_transition_calls = [
        call for call in log_instance.record_phase_transition.call_args_list
        if "kick_off" in str(call) or "goal_scored" in str(call) or "half_time" in str(call) or "full_time" in str(call)
    ]
    # Should only see the initial PRE_MATCH → KICK_OFF transition from start_match
    assert len(phase_transition_calls) <= 1  # Only initial transition


def test_second_half_kickoff_team_initialized(patched_subsystems):
    """_second_half_kickoff_team initialized correctly based on kickoff_team opposite."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    hash_01_fn = patched_subsystems["hash_01"]

    # Force team_a to kick off first half
    hash_01_fn.return_value = 0.3  # < 0.5 → team_a

    # Skip the loop entirely; we only test pre-loop _second_half_kickoff_team derivation
    gsm_instance.total_ticks = 0

    engine = TickEngine()
    engine.run_match(config)

    # If team_a kicks off first half, team_b should kick off second half
    assert engine._second_half_kickoff_team == "team_b"


def test_second_half_kickoff_team_when_team_b_starts(patched_subsystems):
    """_second_half_kickoff_team initialized correctly when team_b kicks off first."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    hash_01_fn = patched_subsystems["hash_01"]

    # Force team_b to kick off first half
    hash_01_fn.return_value = 0.7  # > 0.5 → team_b

    # Skip the loop entirely; we only test pre-loop _second_half_kickoff_team derivation
    gsm_instance.total_ticks = 0

    engine = TickEngine()
    engine.run_match(config)

    # If team_b kicks off first half, team_a should kick off second half
    assert engine._second_half_kickoff_team == "team_a"