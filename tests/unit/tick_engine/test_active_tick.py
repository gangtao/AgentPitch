"""Tests for TE Story 004: Active tick execution + event_type classification."""
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
        gsm_instance.total_ticks = 1
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


def test_ac_te_06_history_called_once_per_tick(patched_subsystems):
    """AC-TE-06: log.get_history() called exactly once per active tick (NOT per player)."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]

    # Setup tick counter to run one active tick
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    TickEngine().run_match(config)

    # get_history should be called exactly once per active tick
    log_instance.get_history.assert_called_once()


def test_ac_te_07_resolve_tick_called_with_tick_and_history(patched_subsystems):
    """AC-TE-07: are.resolve_tick(gsm.tick, history) called once per active tick."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]
    are_instance = patched_subsystems["are_instance"]

    # Setup tick counter to run one active tick
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    # Mock history return
    mock_history = [{"tick": -1, "score": {"team_a": 0, "team_b": 0}}]
    log_instance.get_history.return_value = mock_history

    TickEngine().run_match(config)

    # resolve_tick should be called once with current tick and history
    are_instance.resolve_tick.assert_called_once_with(0, mock_history)


def test_ac_te_08_record_fallback_before_record_tick(patched_subsystems):
    """AC-TE-08: record_fallback calls happen BEFORE record_tick for the same tick."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]
    are_instance = patched_subsystems["are_instance"]

    # Setup tick counter to run one active tick
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    # Configure ARE to return tuple with fallback events
    fallback_event = {"type": "timeout", "player_id": "team_a_0"}
    ten_pids = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]
    action_records = {pid: {"action": "Hold", "result": "ok"} for pid in ten_pids}
    are_instance.resolve_tick.return_value = (action_records, [fallback_event])

    # Track call order on the log instance
    call_order = []

    def track_record_fallback(fe):
        call_order.append(("record_fallback", fe))

    def track_record_tick(tr):
        call_order.append(("record_tick", tr))

    log_instance.record_fallback.side_effect = track_record_fallback
    log_instance.record_tick.side_effect = track_record_tick

    TickEngine().run_match(config)

    # Verify record_fallback called before record_tick
    assert len(call_order) == 2
    assert call_order[0][0] == "record_fallback"
    assert call_order[0][1] == fallback_event
    assert call_order[1][0] == "record_tick"


def test_event_type_goal_priority(patched_subsystems):
    """event_type 'goal' when score differs before/after resolve_tick."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]
    base_snapshot = patched_subsystems["base_snapshot"]

    # Setup tick counter to run one active tick
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    # Mock snapshot to return different scores before/after
    score_before = {"team_a": 0, "team_b": 0}
    score_after = {"team_a": 1, "team_b": 0}

    def mock_snapshot_sequence():
        snapshots = [
            {**base_snapshot, "score": score_before},  # before call
            {**base_snapshot, "score": score_after},   # after call
        ]
        for snap in snapshots:
            yield snap

    snapshot_gen = mock_snapshot_sequence()
    gsm_instance.build_tick_snapshot.side_effect = lambda: next(snapshot_gen)

    TickEngine().run_match(config)

    # Verify record_tick called with event_type="goal"
    log_instance.record_tick.assert_called_once()
    tick_record = log_instance.record_tick.call_args[0][0]
    assert tick_record.event_type == "goal"
    assert tick_record.is_key_event is True


def test_event_type_fallback_priority(patched_subsystems):
    """event_type 'fallback' when score unchanged AND fallback_events non-empty."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]
    are_instance = patched_subsystems["are_instance"]

    # Setup tick counter to run one active tick
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    # Configure ARE to return tuple with fallback events, same score
    fallback_event = {"type": "timeout", "player_id": "team_a_0"}
    ten_pids = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]
    action_records = {pid: {"action": "Hold", "result": "ok"} for pid in ten_pids}
    are_instance.resolve_tick.return_value = (action_records, [fallback_event])

    TickEngine().run_match(config)

    # Verify record_tick called with event_type="fallback"
    log_instance.record_tick.assert_called_once()
    tick_record = log_instance.record_tick.call_args[0][0]
    assert tick_record.event_type == "fallback"
    assert tick_record.is_key_event is True


def test_event_type_tackle_controlled(patched_subsystems):
    """event_type 'tackle_controlled' when tackle returns result='controlled'.
    Per ADR-0018 (2026-04-22) the old "success" result was renamed to
    "controlled" (clean take) to make room for the new "blocked" outcome
    (deflection)."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]
    are_instance = patched_subsystems["are_instance"]

    # Setup tick counter to run one active tick
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    # Configure ARE to return tackle controlled, no fallback events
    ten_pids = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]
    action_records = {pid: {"action": "Hold", "result": "ok"} for pid in ten_pids}
    action_records["team_a_0"] = {"action": "Tackle", "result": "controlled"}
    are_instance.resolve_tick.return_value = action_records

    TickEngine().run_match(config)

    # Verify record_tick called with event_type="tackle_controlled"
    log_instance.record_tick.assert_called_once()
    tick_record = log_instance.record_tick.call_args[0][0]
    assert tick_record.event_type == "tackle_controlled"
    assert tick_record.is_key_event is True


def test_event_type_shot_on_target(patched_subsystems):
    """event_type 'shot_on_target' when shoot with result='save'."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]
    are_instance = patched_subsystems["are_instance"]

    # Setup tick counter to run one active tick
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    # Configure ARE to return shoot save, no fallback, no tackle success
    ten_pids = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]
    action_records = {pid: {"action": "Hold", "result": "ok"} for pid in ten_pids}
    action_records["team_a_0"] = {"action": "Shoot", "result": "save"}
    are_instance.resolve_tick.return_value = action_records

    TickEngine().run_match(config)

    # Verify record_tick called with event_type="shot_on_target"
    log_instance.record_tick.assert_called_once()
    tick_record = log_instance.record_tick.call_args[0][0]
    assert tick_record.event_type == "shot_on_target"
    assert tick_record.is_key_event is True


def test_event_type_none_for_quiet_tick(patched_subsystems):
    """event_type None when no special conditions are met."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]
    are_instance = patched_subsystems["are_instance"]

    # Setup tick counter to run one active tick
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    # Configure ARE to return all Hold actions, no fallback events
    ten_pids = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]
    action_records = {pid: {"action": "Hold", "result": "ok"} for pid in ten_pids}
    are_instance.resolve_tick.return_value = action_records

    TickEngine().run_match(config)

    # Verify record_tick called with event_type=None
    log_instance.record_tick.assert_called_once()
    tick_record = log_instance.record_tick.call_args[0][0]
    assert tick_record.event_type is None
    assert tick_record.is_key_event is False


def test_tick_record_includes_ball_position_and_score(patched_subsystems):
    """TickRecord includes ball_position, ball_possession, score from GSM after resolve_tick."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]
    base_snapshot = patched_subsystems["base_snapshot"]

    # Setup tick counter to run one active tick
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    # Configure specific ball position and possession
    test_snapshot = {
        **base_snapshot,
        "ball": {
            "position": (75.5, 42.3),
            "possession": "team_b",
            "velocity": (0.0, 0.0),
            "carrier_id": "team_b_2"
        },
        "score": {"team_a": 2, "team_b": 1}
    }

    # Return same snapshot twice (before and after calls)
    gsm_instance.build_tick_snapshot.return_value = test_snapshot

    TickEngine().run_match(config)

    # Verify record_tick called with correct ball_position, ball_possession, score
    log_instance.record_tick.assert_called_once()
    tick_record = log_instance.record_tick.call_args[0][0]
    assert tick_record.ball_position == (75.5, 42.3)
    assert tick_record.ball_possession == "team_b"
    assert tick_record.score == {"team_a": 2, "team_b": 1}


def test_event_type_priority_order(patched_subsystems):
    """Test that event_type follows correct priority: goal > fallback > tackle > shoot > None."""
    config = _make_config()
    gsm_instance = patched_subsystems["gsm_instance"]
    log_instance = patched_subsystems["log_instance"]
    are_instance = patched_subsystems["are_instance"]
    base_snapshot = patched_subsystems["base_snapshot"]

    # Setup tick counter to run one active tick
    counter = TickCounter()
    type(gsm_instance).tick = property(lambda self: counter.value)
    gsm_instance.advance_tick.side_effect = counter.advance
    gsm_instance.total_ticks = 1
    gsm_instance.get_phase.return_value = "in_play"

    # Configure ARE to have fallback, tackle success, AND shoot save
    # But goal should have highest priority
    fallback_event = {"type": "timeout", "player_id": "team_a_0"}
    ten_pids = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]
    action_records = {pid: {"action": "Hold", "result": "ok"} for pid in ten_pids}
    action_records["team_a_0"] = {"action": "Tackle", "result": "success"}
    action_records["team_a_1"] = {"action": "Shoot", "result": "save"}
    are_instance.resolve_tick.return_value = (action_records, [fallback_event])

    # Mock different scores (goal condition)
    score_before = {"team_a": 0, "team_b": 0}
    score_after = {"team_a": 1, "team_b": 0}

    def mock_snapshot_sequence():
        snapshots = [
            {**base_snapshot, "score": score_before},  # before call
            {**base_snapshot, "score": score_after},   # after call
        ]
        for snap in snapshots:
            yield snap

    snapshot_gen = mock_snapshot_sequence()
    gsm_instance.build_tick_snapshot.side_effect = lambda: next(snapshot_gen)

    TickEngine().run_match(config)

    # Even with fallback, tackle, and shoot, goal should win
    log_instance.record_tick.assert_called_once()
    tick_record = log_instance.record_tick.call_args[0][0]
    assert tick_record.event_type == "goal"
    assert tick_record.is_key_event is True