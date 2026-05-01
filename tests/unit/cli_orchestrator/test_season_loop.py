"""Tests for CLI Story 003: season loop + match execution."""
from __future__ import annotations
import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.orchestration.cli import _run_season


def _make_config():
    """Create mock config with team configurations."""
    cfg = MagicMock()
    cfg.team_a.llm_provider = "openai"
    cfg.team_b.llm_provider = "anthropic"
    return cfg


@pytest.fixture
def patched_subsystems(monkeypatch):
    """Patch CGP + TickEngine."""
    # Patch CGP to succeed
    cgp_spy = AsyncMock(return_value="def decide(s, c, h): return Hold()")
    import src.foundation.code_generation_pipeline as cgp_mod
    monkeypatch.setattr(cgp_mod, "generate_strategy", cgp_spy)

    # Patch TickEngine
    te_cls = MagicMock()
    te_inst = MagicMock()
    te_inst.run_match.return_value = MagicMock(name="MatchLog")
    te_cls.return_value = te_inst

    # Patch the import in the CLI module
    import src.orchestration.tick_engine as te_mod
    monkeypatch.setattr(te_mod, "TickEngine", te_cls)

    return {"cgp": cgp_spy, "te_cls": te_cls, "te_inst": te_inst}


def test_ac_cli_07_loop_runs_season_length_times(patched_subsystems):
    """Season loop iterates exactly season_length times."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 5, cfg))
    assert patched_subsystems["te_inst"].run_match.call_count == 5


def test_ac_cli_08_tick_engine_called_per_match(patched_subsystems):
    """TickEngine().run_match(config) called once per match."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 3, cfg))
    assert patched_subsystems["te_inst"].run_match.call_count == 3


def test_match_start_line_printed(patched_subsystems, capsys):
    """[season] match N/N starting printed at top of each iteration."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 2, cfg))
    captured = capsys.readouterr()
    assert "match 1/2 starting" in captured.out
    assert "match 2/2 starting" in captured.out


def test_match_evolving_line_printed(patched_subsystems, capsys):
    """[season] match N/N evolving... printed after run_match (requires ≥2 matches)."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 2, cfg))
    captured = capsys.readouterr()
    assert "evolving" in captured.out


def test_tick_engine_exception_propagates(patched_subsystems):
    """If TickEngine.run_match raises, the exception propagates (NOT caught)."""
    cfg = _make_config()
    patched_subsystems["te_inst"].run_match.side_effect = RuntimeError("fatal sim error")
    with pytest.raises(RuntimeError, match="fatal sim error"):
        asyncio.run(_run_season("x.yaml", 1, cfg))


def test_season_loop_uses_1_indexed_match_numbers(patched_subsystems, capsys):
    """Match numbers are 1-indexed (1, 2, 3...) not 0-indexed."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 3, cfg))
    captured = capsys.readouterr()
    assert "match 1/3" in captured.out
    assert "match 2/3" in captured.out
    assert "match 3/3" in captured.out
    # Should not have match 0
    assert "match 0/3" not in captured.out


def test_tick_engine_instantiated_per_match(patched_subsystems):
    """TickEngine() is instantiated once per match (new instance each time)."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 2, cfg))
    # Should have been called twice (once per match)
    assert patched_subsystems["te_cls"].call_count == 2


def test_match_log_variable_created_but_unused(patched_subsystems):
    """match_log variable is created per iteration (for Story 004)."""
    cfg = _make_config()
    # This test verifies the code structure compiles and runs without error
    # The match_log variable is created but not used until Story 004
    asyncio.run(_run_season("x.yaml", 1, cfg))
    # If we get here without syntax/runtime errors, the variable creation works
    assert patched_subsystems["te_inst"].run_match.call_count == 1


def test_season_loop_after_cgp_success_only(patched_subsystems):
    """Season loop only runs when CGP succeeds (not when CGP fails)."""
    cfg = _make_config()

    # First test: CGP succeeds → season loop runs
    asyncio.run(_run_season("x.yaml", 2, cfg))
    assert patched_subsystems["te_inst"].run_match.call_count == 2

    # Reset for second test
    patched_subsystems["te_inst"].run_match.reset_mock()
    patched_subsystems["cgp"].side_effect = RuntimeError("CGP failed")

    # Second test: CGP fails → season loop should not run
    with pytest.raises(SystemExit):
        asyncio.run(_run_season("x.yaml", 2, cfg))
    assert patched_subsystems["te_inst"].run_match.call_count == 0