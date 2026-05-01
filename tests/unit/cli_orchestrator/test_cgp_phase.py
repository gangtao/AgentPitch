"""Tests for CLI Story 002: CGP phase + abort policy."""
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


def test_ac_cli_04_cgp_gather_called(monkeypatch):
    """asyncio.gather called once with both generate_strategy invocations."""
    cfg = _make_config()

    gen_spy = AsyncMock(return_value="def decide(s, c, h): return Hold()")
    import src.foundation.code_generation_pipeline as cgp_mod
    monkeypatch.setattr(cgp_mod, "generate_strategy", gen_spy)

    # Patch TickEngine to prevent real execution
    te_cls = MagicMock()
    te_inst = MagicMock()
    te_inst.run_match.return_value = MagicMock(name="MatchLog")
    te_cls.return_value = te_inst
    import src.orchestration.tick_engine as te_mod
    monkeypatch.setattr(te_mod, "TickEngine", te_cls)

    asyncio.run(_run_season("x.yaml", 1, cfg))

    assert gen_spy.call_count == 2
    # Verify the calls were made with correct parameters
    calls = gen_spy.call_args_list
    assert calls[0][0] == (cfg, "team_a")
    assert calls[1][0] == (cfg, "team_b")


def test_ac_cli_05_single_team_failure_exits_1(monkeypatch, capsys):
    """Single CGP failure → ERROR + exit 1."""
    cfg = _make_config()

    async def fake_gen(config, team_id, **_kwargs):
        if team_id == "team_a":
            return "def decide(s, c, h): return Hold()"
        raise RuntimeError("LLM unavailable")

    import src.foundation.code_generation_pipeline as cgp_mod
    monkeypatch.setattr(cgp_mod, "generate_strategy", fake_gen)

    with pytest.raises(SystemExit) as ei:
        asyncio.run(_run_season("x.yaml", 1, cfg))
    assert ei.value.code == 1
    captured = capsys.readouterr()
    assert "team_b" in captured.err
    assert "RuntimeError" in captured.err
    assert "LLM unavailable" in captured.err


def test_ac_cli_06_dual_team_failure_exits_1(monkeypatch, capsys):
    """Both teams fail → both ERRORs + exit 1."""
    cfg = _make_config()

    async def fake_gen(config, team_id, **_kwargs):
        raise RuntimeError(f"{team_id} failed")

    import src.foundation.code_generation_pipeline as cgp_mod
    monkeypatch.setattr(cgp_mod, "generate_strategy", fake_gen)

    with pytest.raises(SystemExit) as ei:
        asyncio.run(_run_season("x.yaml", 1, cfg))
    assert ei.value.code == 1
    captured = capsys.readouterr()
    assert "team_a" in captured.err
    assert "team_b" in captured.err


def test_cgp_success_no_exit(monkeypatch):
    """When both teams succeed, _run_season completes without sys.exit."""
    cfg = _make_config()
    gen_spy = AsyncMock(return_value="def decide(s, c, h): return Hold()")
    import src.foundation.code_generation_pipeline as cgp_mod
    monkeypatch.setattr(cgp_mod, "generate_strategy", gen_spy)

    # Patch TickEngine to prevent real execution
    te_cls = MagicMock()
    te_inst = MagicMock()
    te_inst.run_match.return_value = MagicMock(name="MatchLog")
    te_cls.return_value = te_inst
    import src.orchestration.tick_engine as te_mod
    monkeypatch.setattr(te_mod, "TickEngine", te_cls)

    # Should complete normally without raising SystemExit
    asyncio.run(_run_season("x.yaml", 1, cfg))


def test_cgp_success_prints_per_team(monkeypatch, capsys):
    """For each successful team, [CGP] team_X: strategy_v1.py written line printed."""
    cfg = _make_config()
    gen_spy = AsyncMock(return_value="def decide(s, c, h): return Hold()")
    import src.foundation.code_generation_pipeline as cgp_mod
    monkeypatch.setattr(cgp_mod, "generate_strategy", gen_spy)

    # Patch TickEngine to prevent real execution
    te_cls = MagicMock()
    te_inst = MagicMock()
    te_inst.run_match.return_value = MagicMock(name="MatchLog")
    te_cls.return_value = te_inst
    import src.orchestration.tick_engine as te_mod
    monkeypatch.setattr(te_mod, "TickEngine", te_cls)

    asyncio.run(_run_season("x.yaml", 1, cfg))
    captured = capsys.readouterr()

    assert "[season] generating initial strategies..." in captured.out
    assert "[CGP] team_a: strategy_v1.py written (openai)" in captured.out
    assert "[CGP] team_b: strategy_v1.py written (anthropic)" in captured.out


def test_cgp_mixed_success_failure_exits_1(monkeypatch, capsys):
    """Mixed results: one success, one failure → ERROR for failed team + exit 1."""
    cfg = _make_config()

    async def fake_gen(config, team_id, **_kwargs):
        if team_id == "team_a":
            return "def decide(s, c, h): return Hold()"
        raise ValueError("team_b specific error")

    import src.foundation.code_generation_pipeline as cgp_mod
    monkeypatch.setattr(cgp_mod, "generate_strategy", fake_gen)

    with pytest.raises(SystemExit) as ei:
        asyncio.run(_run_season("x.yaml", 1, cfg))
    assert ei.value.code == 1

    captured = capsys.readouterr()
    # Should show success for team_a and error for team_b
    assert "[CGP] team_a: strategy_v1.py written (openai)" in captured.out
    assert "[CGP-ERROR] team_b: ValueError: team_b specific error" in captured.err