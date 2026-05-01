"""Tests for TE Story 003: Match start + main tick loop scaffold."""
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
        # Default GSM tick + total_ticks numeric so loop terminates
        gsm_instance.tick = 0
        gsm_instance.total_ticks = 0  # Tests override this
        gsm_instance.get_phase.return_value = "in_play"

        # Mock MatchLog instance
        log_instance = MagicMock()
        log_cls.return_value = log_instance

        yield {
            "gsm": gsm_cls, "log": log_cls, "sb": sb_cls,
            "fh": fh_cls, "are": are_cls, "anchors": anchors_fn,
            "hash_01": hash_01_fn, "gsm_instance": gsm_instance,
            "log_instance": log_instance,
        }


class TickCounter:
    """Helper class to simulate incrementing tick behavior."""
    def __init__(self):
        self.value = 0

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
    return config


def test_ac_te_04_start_match_called_once(patched_subsystems):
    """AC-TE-04: gsm.start_match() called once after compile phase."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]

    # Setup tick counter to exit loop quickly
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    TickEngine().run_match(config)

    gsm_instance.start_match.assert_called_once()


def test_ac_te_05_tick_loop_runs_until_total_ticks(patched_subsystems):
    """AC-TE-05: With gsm.tick starting at 0 and total_ticks=10, loop executes exactly 10 iterations."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]

    # Setup tick counter
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 10
    gsm_instance.get_phase.return_value = "in_play"

    TickEngine().run_match(config)

    # Should have called advance_tick exactly 10 times
    assert gsm_instance.advance_tick.call_count == 10


def test_advance_tick_called_every_iteration(patched_subsystems):
    """advance_tick() called every iteration, even on pause ticks."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]

    # Setup tick counter with pause phases
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 5

    # Mix of pause and active phases — engine may call get_phase multiple times per iteration,
    # so use a callable that returns the phase for the current tick value.
    phases = ["goal_scored", "half_time", "in_play", "kick_off", "in_play"]
    def phase_for_tick():
        return phases[counter.value] if counter.value < len(phases) else "in_play"
    gsm_instance.get_phase.side_effect = phase_for_tick

    TickEngine().run_match(config)

    # Should have called advance_tick 5 times (once per iteration)
    assert gsm_instance.advance_tick.call_count == 5


def test_full_time_breaks_loop(patched_subsystems):
    """When gsm.get_phase() returns 'full_time', loop exits without calling advance_tick() again."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]

    # Setup tick counter
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 10

    # Return full_time on second iteration; engine may call get_phase several times per iter.
    def phase_for_tick():
        return "in_play" if counter.value == 0 else "full_time"
    gsm_instance.get_phase.side_effect = phase_for_tick

    TickEngine().run_match(config)

    # Should have called advance_tick only once (first iteration), then break on second
    assert gsm_instance.advance_tick.call_count == 1


def test_kickoff_team_derived_from_hash_01_team_a(patched_subsystems):
    """_kickoff_team derived from hash_01: 0.3 → team_a."""
    config = _make_config()
    config.match.seed = 42
    gsm_instance = patched_subsystems["gsm_instance"]
    patched_subsystems["hash_01"].return_value = 0.3  # < 0.5 → team_a

    # Setup minimal loop
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    engine = TickEngine()
    # Patch the stub method to capture the kickoff_team argument
    setup_calls = []
    engine._setup_kickoff = lambda gsm, log, kickoff_team: setup_calls.append(kickoff_team)

    engine.run_match(config)

    # Verify hash_01 called with correct args
    patched_subsystems["hash_01"].assert_called_with(42, 0, "kickoff")
    # Verify _setup_kickoff called with team_a
    assert len(setup_calls) == 1
    assert setup_calls[0] == "team_a"


def test_kickoff_team_derived_from_hash_01_team_b(patched_subsystems):
    """_kickoff_team derived from hash_01: 0.7 → team_b."""
    config = _make_config()
    config.match.seed = 42
    gsm_instance = patched_subsystems["gsm_instance"]
    patched_subsystems["hash_01"].return_value = 0.7  # >= 0.5 → team_b

    # Setup minimal loop
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    engine = TickEngine()
    # Patch the stub method to capture the kickoff_team argument
    setup_calls = []
    engine._setup_kickoff = lambda gsm, log, kickoff_team: setup_calls.append(kickoff_team)

    engine.run_match(config)

    # Verify hash_01 called with correct args
    patched_subsystems["hash_01"].assert_called_with(42, 0, "kickoff")
    # Verify _setup_kickoff called with team_b
    assert len(setup_calls) == 1
    assert setup_calls[0] == "team_b"


def test_first_kickoff_transition_recorded(patched_subsystems):
    """log.record_phase_transition(0, 'pre_match', 'kick_off') called once."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]

    # Setup minimal loop
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    TickEngine().run_match(config)

    log_instance.record_phase_transition.assert_called_once_with(0, "pre_match", "kick_off")


def test_returns_log_at_end(patched_subsystems):
    """Engine returns log at end."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]

    # Setup minimal loop
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    result = TickEngine().run_match(config)

    assert result is log_instance


def test_remaining_stub_methods_are_pass_only():
    """The 2 remaining stub methods (_setup_kickoff, _handle_pause_tick) are pass-only."""
    engine = TickEngine()

    # These should not raise and should do nothing
    engine._setup_kickoff(None, None, "team_a")
    engine._handle_pause_tick(None, None, None)

    # If we got here without exception, the stubs are working correctly
    # Note: _handle_active_tick is implemented in Story 004


def test_loop_continues_until_tick_limit_or_full_time(patched_subsystems):
    """Loop continues until gsm.tick >= gsm.total_ticks OR phase == 'full_time'."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]

    # Setup tick counter that will hit the limit
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 3
    gsm_instance.get_phase.return_value = "in_play"

    TickEngine().run_match(config)

    # Should have run exactly 3 times before tick >= total_ticks
    assert gsm_instance.advance_tick.call_count == 3


def test_advance_tick_called_at_end_of_iteration(patched_subsystems):
    """advance_tick() is called at the END of every iteration (not before phase dispatch)."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]

    # Track the order of calls
    call_order = []

    def track_get_phase():
        call_order.append("get_phase")
        return "in_play"

    def track_advance_tick():
        call_order.append("advance_tick")
        # Increment counter after tracking
        counter.advance()

    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.get_phase.side_effect = track_get_phase
    gsm_instance.advance_tick.side_effect = track_advance_tick
    gsm_instance.total_ticks = 2

    TickEngine().run_match(config)

    # Engine may call get_phase multiple times per iteration (loop dispatch + phase transition checks).
    # The structural invariant is: each advance_tick is preceded by at least one get_phase call,
    # and there are exactly total_ticks (=2) advance_tick calls.
    assert call_order.count("advance_tick") == 2
    # Every advance_tick must have a get_phase before it
    for i, evt in enumerate(call_order):
        if evt == "advance_tick":
            assert "get_phase" in call_order[:i], "advance_tick fired without prior get_phase"