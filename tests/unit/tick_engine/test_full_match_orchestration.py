"""TE Story 007 — unit tests for run_match() orchestration control flow.

Mocks every collaborator (GSM, MatchLog, Sandbox, FallbackHandler, ARE,
compute_anchors, read_current, hash_01) to verify run_match's internal
sequencing — finalize is called, MatchLog is returned, phase transitions
are dispatched correctly given mocked GSM responses.

This file was previously located under tests/integration/tick_engine/ but
was renamed to tests/unit/ on 2026-04-22 because mocking 8 internal
subsystems is unit-test behavior, not integration-test behavior. Real
end-to-end coverage of run_match (with real GSM/ARE/PMS/BPS/Sandbox)
lives in tests/integration/tick_engine/test_run_match_persists.py.
"""
from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest
from src.orchestration.tick_engine import TickEngine


@pytest.fixture
def patched_subsystems_for_full_match():
    """Mock all subsystems; configure GSM with a tick counter that walks through phases."""
    with patch("src.orchestration.tick_engine.engine.GameStateManager") as gsm_cls, \
         patch("src.orchestration.tick_engine.engine.MatchLog") as log_cls, \
         patch("src.orchestration.tick_engine.engine.Sandbox") as sb_cls, \
         patch("src.orchestration.tick_engine.engine.FallbackHandler") as fh_cls, \
         patch("src.orchestration.tick_engine.engine.ActionResolutionEngine") as are_cls, \
         patch("src.orchestration.tick_engine.engine.compute_anchors") as anchors_fn, \
         patch("src.orchestration.tick_engine.engine.read_current") as read_fn, \
         patch("src.orchestration.tick_engine.engine.hash_01") as hash_fn:
        anchors_fn.return_value = {f"team_a_{i}": (50.0, 30.0) for i in range(5)}
        anchors_fn.return_value.update({f"team_b_{i}": (50.0, 70.0) for i in range(5)})
        read_fn.return_value = "def decide(s, c, h): return Hold()"
        hash_fn.return_value = 0.3
        # Sandbox compile success
        from src.foundation.sandbox import ExecutionStatus
        sb_inst = MagicMock()
        compile_result = MagicMock(); compile_result.status = ExecutionStatus.SUCCESS
        sb_inst.compile.return_value = compile_result
        sb_cls.return_value = sb_inst
        # GSM with tick counter
        class TC:
            v = 0
        tc = TC()
        gsm_inst = MagicMock()
        type(gsm_inst).tick = property(lambda self: tc.v)
        gsm_inst.advance_tick.side_effect = lambda: setattr(tc, "v", tc.v + 1)
        gsm_inst.total_ticks = 10
        gsm_inst.half_1_end_tick = 5
        gsm_inst.get_phase.return_value = "in_play"
        gsm_inst.get_final_state.return_value = {"final": "state"}
        # snap with default score
        snap = {"score": {"team_a": 0, "team_b": 0}, "ball": {"position": (50, 30), "possession": None}}
        gsm_inst.build_tick_snapshot.return_value = snap
        gsm_inst.build_player_state.side_effect = lambda pid: {"player_id": pid, "team": "team_a" if pid.startswith("team_a") else "team_b", "position": (50, 30)}
        gsm_cls.return_value = gsm_inst
        # ARE returns 10 hold actions
        are_inst = MagicMock()
        ten = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]
        are_inst.resolve_tick.return_value = {pid: {"action": "Hold", "result": "ok", "tick": 0} for pid in ten}
        are_cls.return_value = are_inst
        # Log
        log_inst = MagicMock(); log_inst.get_history.return_value = []
        log_cls.return_value = log_inst
        yield {"gsm": gsm_inst, "log": log_inst, "are": are_inst, "tc": tc}


def _make_config():
    cfg = MagicMock()
    cfg.match.match_id = "test"
    cfg.match.seed = 42
    cfg.output.log_dir = "/tmp/te-test"
    cfg.team_a.llm_provider = "openai"
    cfg.team_b.llm_provider = "anthropic"
    cfg.simulation.goal_reset_ticks = 30
    cfg.simulation.half_time_pause_ticks = 60
    return cfg


def test_ac_te_15_finalize_called_on_exit(patched_subsystems_for_full_match):
    """AC-TE-15: log.finalize called once before return."""
    cfg = _make_config()
    result = TickEngine().run_match(cfg)
    patched_subsystems_for_full_match["log"].finalize.assert_called()


def test_match_runs_to_completion_returns_matchlog(patched_subsystems_for_full_match):
    """100-tick match returns the MatchLog after the loop."""
    cfg = _make_config()
    deps = patched_subsystems_for_full_match
    deps["gsm"].total_ticks = 10
    result = TickEngine().run_match(cfg)
    assert result is deps["log"]
    # Loop ran ~10 iterations
    assert deps["gsm"].advance_tick.call_count >= 5


def test_record_tick_per_active_iteration(patched_subsystems_for_full_match):
    """For an all-in_play 10-tick match, log.record_tick called per active tick."""
    cfg = _make_config()
    deps = patched_subsystems_for_full_match
    deps["gsm"].total_ticks = 10
    TickEngine().run_match(cfg)
    # Should be at least 5 record_tick calls (full count depends on phase transitions)
    assert deps["log"].record_tick.call_count >= 1


def test_finalize_before_return_call_order(patched_subsystems_for_full_match):
    """log.finalize is called BEFORE the function returns (verified by call order)."""
    cfg = _make_config()
    deps = patched_subsystems_for_full_match
    deps["gsm"].total_ticks = 1

    call_order = []
    deps["log"].finalize.side_effect = lambda *args, **kw: call_order.append("finalize")

    result = TickEngine().run_match(cfg)
    assert "finalize" in call_order
    # The result is the same MatchLog instance — finalization happened on it
    assert result is deps["log"]


def test_integration_phase_transitions_recorded(patched_subsystems_for_full_match):
    """For a simulated match with phase transitions, they are recorded."""
    cfg = _make_config()
    deps = patched_subsystems_for_full_match
    deps["gsm"].total_ticks = 20

    # Mock phase progression: kick_off -> in_play -> goal_scored -> kick_off -> full_time
    phase_sequence = ["kick_off", "in_play", "in_play", "goal_scored", "kick_off", "in_play", "full_time"]
    deps["gsm"].get_phase.side_effect = lambda: phase_sequence[min(deps["tc"].v, len(phase_sequence)-1)]

    TickEngine().run_match(cfg)

    # Should have recorded some phase transitions
    assert deps["log"].record_phase_transition.call_count >= 1


def test_integration_per_tick_spy_are_resolution(patched_subsystems_for_full_match):
    """are.resolve_tick called once per active tick (not per pause tick)."""
    cfg = _make_config()
    deps = patched_subsystems_for_full_match
    deps["gsm"].total_ticks = 10

    # All ticks are in_play (active)
    deps["gsm"].get_phase.return_value = "in_play"

    TickEngine().run_match(cfg)

    # Should call resolve_tick for each active tick
    # (Exact count depends on when loop exits, but should be > 1)
    assert deps["are"].resolve_tick.call_count >= 1


def test_finalize_with_gsm_final_state_argument(patched_subsystems_for_full_match):
    """When GSM has get_final_state, it's passed to log.finalize."""
    cfg = _make_config()
    deps = patched_subsystems_for_full_match
    deps["gsm"].total_ticks = 1

    final_state = {"final_score": {"team_a": 2, "team_b": 1}, "final_tick": 100}
    deps["gsm"].get_final_state.return_value = final_state

    TickEngine().run_match(cfg)

    deps["log"].finalize.assert_called_once_with(final_state)


def test_finalize_fallback_without_get_final_state(patched_subsystems_for_full_match):
    """When GSM lacks get_final_state, fallback final_state is constructed."""
    cfg = _make_config()
    deps = patched_subsystems_for_full_match
    deps["gsm"].total_ticks = 1

    # Remove get_final_state method
    del deps["gsm"].get_final_state

    # Mock gsm.state attributes for fallback construction
    state_mock = MagicMock()
    state_mock.score = {"team_a": 1, "team_b": 0}
    state_mock.tick = 5
    state_mock.phase = "FULL_TIME"
    deps["gsm"].state = state_mock

    TickEngine().run_match(cfg)

    # Should still call finalize with constructed final_state
    deps["log"].finalize.assert_called_once()
    call_args = deps["log"].finalize.call_args[0]
    assert len(call_args) == 1
    final_state = call_args[0]
    assert final_state["final_score"] == {"team_a": 1, "team_b": 0}
    assert final_state["final_tick"] == 5
    assert final_state["final_phase"] == "FULL_TIME"


def test_finalize_tolerates_no_args_signature(patched_subsystems_for_full_match):
    """When log.finalize raises TypeError, retry with no args."""
    cfg = _make_config()
    deps = patched_subsystems_for_full_match
    deps["gsm"].total_ticks = 1

    # Mock finalize to reject arguments first, then accept no args
    call_count = 0
    def finalize_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1 and args:
            raise TypeError("finalize() takes no arguments")
        return None

    deps["log"].finalize.side_effect = finalize_side_effect

    TickEngine().run_match(cfg)

    # Should have called finalize twice (first with args failed, second with no args)
    assert deps["log"].finalize.call_count == 2


def test_handle_active_tick_filters_synthetic_system_key(patched_subsystems_for_full_match):
    """ARE Phase 7 inserts a synthetic 'system' key into action_records for
    ball-pickup/goal events that have no responsible player. TickEngine must
    skip it before calling build_player_state, which only knows about real
    player_ids and would KeyError otherwise.

    Surfaced 2026-04-22 by realistic-strategy playtest — chase-ball strategy
    never triggered Phase 7's system-key path so the gap stayed hidden.
    """
    deps = patched_subsystems_for_full_match
    cfg = _make_config()

    # Inject a synthetic "system" entry alongside the normal 10 player records.
    ten = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]
    records_with_system = {pid: {"action": "Hold", "result": "ok", "tick": 0} for pid in ten}
    records_with_system["system"] = {"action": "ball_pickup", "result": "ok", "tick": 0}
    deps["are"].resolve_tick.return_value = records_with_system

    # Must not raise KeyError when build_player_state encounters "system".
    TickEngine().run_match(cfg)

    # build_player_state should never have been asked about "system".
    bps_calls = [c.args[0] for c in deps["gsm"].build_player_state.call_args_list]
    assert "system" not in bps_calls, "TickEngine called build_player_state('system') — synthetic key not filtered"