"""Tests for TE Story 001: TickEngine class scaffold + composition root."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.orchestration.tick_engine import TickEngine


@pytest.fixture
def patched_subsystems():
    """Patch all subsystem constructors at engine module level."""
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

        # Mock sandbox.compile to return success
        sb_instance = MagicMock()
        from src.foundation.sandbox import ExecutionStatus
        compile_result = MagicMock()
        compile_result.status = ExecutionStatus.SUCCESS
        sb_instance.compile.return_value = compile_result
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
            "gsm": gsm_cls, "log": log_cls, "sb": sb_cls,
            "fh": fh_cls, "are": are_cls, "anchors": anchors_fn,
        }


def _make_config():
    config = MagicMock()
    config.match.match_id = "test-match-id"
    config.match.seed = 42  # Add seed for Story 003
    config.output.log_dir = "/tmp/test-logs"
    # Mock team configs with llm_provider for compile phase
    config.team_a.llm_provider = "openai"
    config.team_b.llm_provider = "anthropic"
    return config


def test_ac_te_01_composition_root(patched_subsystems):
    """AC-TE-01: All 7 subsystems constructed in dependency order."""
    config = _make_config()
    TickEngine().run_match(config)
    patched_subsystems["gsm"].assert_called_once()
    patched_subsystems["log"].assert_called_once()
    # Engine builds one sandbox per team (mono-language match → 2 calls).
    assert patched_subsystems["sb"].call_count == 2
    patched_subsystems["fh"].assert_called_once()
    patched_subsystems["are"].assert_called_once()


def test_no_init_args():
    """TickEngine.__init__ accepts no non-self args."""
    TickEngine()  # should not raise


def test_no_persistent_self_state(patched_subsystems):
    """No subsystems remain as self attrs after run_match returns."""
    config = _make_config()
    engine = TickEngine()
    engine.run_match(config)
    for attr in ("gsm", "log", "sb", "fh", "are"):
        assert not hasattr(engine, attr), f"engine retained '{attr}' attribute"


def test_are_constructed_with_correct_arg_count(patched_subsystems):
    """ActionResolutionEngine receives exactly 5 args (gsm, pms, bps, sb, fh)."""
    config = _make_config()
    TickEngine().run_match(config)
    are_call = patched_subsystems["are"].call_args
    args = are_call.args
    assert len(args) == 5


def test_are_first_arg_is_gsm(patched_subsystems):
    """ARE's first arg is the GSM instance (verifies dep injection order)."""
    config = _make_config()
    TickEngine().run_match(config)
    are_call = patched_subsystems["are"].call_args
    assert are_call.args[0] is patched_subsystems["gsm"].return_value


def test_returns_matchlog(patched_subsystems):
    """run_match returns the constructed MatchLog."""
    config = _make_config()
    result = TickEngine().run_match(config)
    assert result is patched_subsystems["log"].return_value


def test_importability():
    """TickEngine importable from package."""
    from src.orchestration.tick_engine import TickEngine
    assert TickEngine is not None


def test_gsm_constructed_with_config(patched_subsystems):
    """GameStateManager receives the config arg (and anchors)."""
    config = _make_config()
    TickEngine().run_match(config)
    gsm_call = patched_subsystems["gsm"].call_args
    # First positional should be config (anchors comes second)
    assert gsm_call.args[0] is config
