"""Tests for TE Story 002: Compile phase + COMPILE_ERROR handling."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.orchestration.tick_engine import TickEngine
from src.foundation.sandbox import ExecutionStatus
from src.foundation.fallback.types import FallbackEvent


@pytest.fixture
def patched_subsystems():
    """Patch all subsystem constructors and strategy storage at engine module level."""
    with patch("src.orchestration.tick_engine.engine.GameStateManager") as gsm_cls, \
         patch("src.orchestration.tick_engine.engine.MatchLog") as log_cls, \
         patch("src.orchestration.tick_engine.engine.RestrictedPythonSandbox") as sb_cls, \
         patch("src.orchestration.tick_engine.engine.FallbackHandler") as fh_cls, \
         patch("src.orchestration.tick_engine.engine.ActionResolutionEngine") as are_cls, \
         patch("src.orchestration.tick_engine.engine.compute_anchors") as anchors_fn, \
         patch("src.orchestration.tick_engine.engine.read_current") as read_current_fn, \
         patch("src.orchestration.tick_engine.engine.hash_01") as hash_01_fn:

        anchors_fn.return_value = {f"team_a_{i}": (50.0, 30.0) for i in range(5)}
        read_current_fn.side_effect = lambda log_dir, team_id: f"# strategy for {team_id}\ndef decide(gs, ps, h): return Hold()"

        # Engine constructs one RestrictedPythonSandbox per team. Reuse a single
        # mock instance so tests can assert on aggregate compile/disable counts
        # the same way they did when the engine used a single Sandbox().
        sb_instance = MagicMock()
        sb_cls.return_value = sb_instance

        # Mock GSM instance to handle Story 003 additions
        gsm_instance = MagicMock()
        gsm_instance.tick = 0
        gsm_instance.total_ticks = 0  # Will exit loop immediately in existing tests
        gsm_instance.get_phase.return_value = "in_play"
        gsm_cls.return_value = gsm_instance

        # Mock hash_01 for kickoff team derivation
        hash_01_fn.return_value = 0.3  # Default to team_a

        yield {
            "gsm": gsm_cls, "log": log_cls, "sb": sb_cls, "sb_instance": sb_instance,
            "fh": fh_cls, "are": are_cls, "anchors": anchors_fn, "read_current": read_current_fn,
        }


def _make_config():
    """Create a mock config with all required fields for compile phase."""
    config = MagicMock()
    config.match.match_id = "test-match-id"
    config.output.log_dir = "/tmp/test-logs"

    # Mock team configs with llm_provider
    config.team_a.llm_provider = "openai"
    config.team_b.llm_provider = "anthropic"

    return config


def test_ac_te_02_per_player_compile(patched_subsystems):
    """AC-TE-02: sb.compile called exactly 10 times with correct args."""
    config = _make_config()

    # Mock successful compilation
    compile_result = MagicMock()
    compile_result.status = ExecutionStatus.SUCCESS
    patched_subsystems["sb_instance"].compile.return_value = compile_result

    TickEngine().run_match(config)

    # Verify compile called 10 times
    assert patched_subsystems["sb_instance"].compile.call_count == 10

    # Verify player IDs and code are correct
    compile_calls = patched_subsystems["sb_instance"].compile.call_args_list
    expected_pids = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]
    actual_pids = [call.args[0] for call in compile_calls]
    assert actual_pids == expected_pids

    # Verify strategy code comes from read_current
    for call in compile_calls:
        assert "def decide(gs, ps, h): return Hold()" in call.args[1]


def test_ac_te_03_compile_error_handling(patched_subsystems):
    """AC-TE-03: COMPILE_ERROR triggers sb.disable + log.record_fallback."""
    config = _make_config()

    # Mock compile error for team_a_1
    def mock_compile(player_id, code):
        result = MagicMock()
        if player_id == "team_a_1":
            result.status = ExecutionStatus.COMPILE_ERROR
            result.error_type = "SyntaxError"
        else:
            result.status = ExecutionStatus.SUCCESS
            result.error_type = None
        return result

    patched_subsystems["sb_instance"].compile.side_effect = mock_compile

    log_instance = MagicMock()
    patched_subsystems["log"].return_value = log_instance

    TickEngine().run_match(config)

    # Verify sb.disable called for failing player
    patched_subsystems["sb_instance"].disable.assert_called_once_with("team_a_1")

    # Verify record_fallback called once
    log_instance.record_fallback.assert_called_once()

    # Verify FallbackEvent fields
    fallback_event = log_instance.record_fallback.call_args.args[0]
    assert fallback_event.event_type == "fallback"
    assert fallback_event.tick == 0
    assert fallback_event.player_id == "team_a_1"
    assert fallback_event.team == "team_a"
    assert fallback_event.llm_provider == "openai"
    assert fallback_event.failure_status == "COMPILE_ERROR"
    assert fallback_event.error_type == "SyntaxError"
    assert fallback_event.execution_time_ms == 0.0
    assert fallback_event.substituted_action == "Hold"
    assert fallback_event.fallback_substituted is True


def test_match_proceeds_despite_all_compile_failures(patched_subsystems):
    """Match proceeds even if all 10 players fail to compile."""
    config = _make_config()

    # Mock compile error for all players
    compile_result = MagicMock()
    compile_result.status = ExecutionStatus.COMPILE_ERROR
    compile_result.error_type = "ParseError"
    patched_subsystems["sb_instance"].compile.return_value = compile_result

    log_instance = MagicMock()
    patched_subsystems["log"].return_value = log_instance

    # Should not raise
    result = TickEngine().run_match(config)

    # Verify we get the log back
    assert result is log_instance

    # Verify all players disabled
    assert patched_subsystems["sb_instance"].disable.call_count == 10

    # Verify all players logged as fallback
    assert log_instance.record_fallback.call_count == 10


def test_no_fallback_handler_calls_during_compile(patched_subsystems):
    """fh.handle is NEVER called during compile phase."""
    config = _make_config()

    # Mock mix of success and failure
    def mock_compile(player_id, code):
        result = MagicMock()
        if player_id in ["team_a_0", "team_b_2"]:
            result.status = ExecutionStatus.COMPILE_ERROR
            result.error_type = "TypeError"
        else:
            result.status = ExecutionStatus.SUCCESS
        return result

    patched_subsystems["sb_instance"].compile.side_effect = mock_compile

    fh_instance = MagicMock()
    patched_subsystems["fh"].return_value = fh_instance

    TickEngine().run_match(config)

    # FallbackHandler.handle should never be called
    fh_instance.handle.assert_not_called()


def test_strategy_read_once_per_team(patched_subsystems):
    """Strategy code read once per team, reused across 5 players."""
    config = _make_config()

    # Mock successful compilation
    compile_result = MagicMock()
    compile_result.status = ExecutionStatus.SUCCESS
    patched_subsystems["sb_instance"].compile.return_value = compile_result

    TickEngine().run_match(config)

    # read_current should be called exactly twice
    read_calls = patched_subsystems["read_current"].call_args_list
    assert len(read_calls) == 2

    # Should read for both teams
    called_teams = {call.args[1] for call in read_calls}
    assert called_teams == {"team_a", "team_b"}


def test_team_b_compile_error_uses_correct_provider(patched_subsystems):
    """COMPILE_ERROR for team_b uses team_b.llm_provider in FallbackEvent."""
    config = _make_config()

    # Mock compile error for team_b_3
    def mock_compile(player_id, code):
        result = MagicMock()
        if player_id == "team_b_3":
            result.status = ExecutionStatus.COMPILE_ERROR
            result.error_type = "NameError"
        else:
            result.status = ExecutionStatus.SUCCESS
        return result

    patched_subsystems["sb_instance"].compile.side_effect = mock_compile

    log_instance = MagicMock()
    patched_subsystems["log"].return_value = log_instance

    TickEngine().run_match(config)

    # Verify FallbackEvent uses team_b config
    fallback_event = log_instance.record_fallback.call_args.args[0]
    assert fallback_event.player_id == "team_b_3"
    assert fallback_event.team == "team_b"
    assert fallback_event.llm_provider == "anthropic"  # team_b provider


def test_compile_phase_happens_after_subsystem_construction(patched_subsystems):
    """Compile phase happens after all subsystems are built."""
    config = _make_config()

    # Mock successful compilation
    compile_result = MagicMock()
    compile_result.status = ExecutionStatus.SUCCESS
    patched_subsystems["sb_instance"].compile.return_value = compile_result

    # Track call order
    call_order = []

    def track_gsm(*args):
        call_order.append("gsm")
        m = MagicMock()
        m.tick = 0
        m.total_ticks = 0
        m.get_phase.return_value = "in_play"
        return m

    def track_sb(*args):
        sb_mock = MagicMock()
        def track_compile(*args):
            call_order.append("compile")
            return compile_result
        sb_mock.compile = track_compile
        return sb_mock

    patched_subsystems["gsm"].side_effect = track_gsm
    patched_subsystems["sb"].side_effect = track_sb

    TickEngine().run_match(config)

    # GSM should be constructed before any compile calls
    assert call_order[0] == "gsm"
    assert "compile" in call_order
    assert call_order.index("gsm") < call_order.index("compile")