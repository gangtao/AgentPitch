"""Tests for CLI Story 004: PMEP phase + result inspection + failure policies."""
from __future__ import annotations
import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.orchestration.cli import _run_season
from src.foundation.post_match_evolution_pipeline import EvolutionFailedError
from src.foundation.strategy_storage import WriteFailedError


def _make_config():
    cfg = MagicMock()
    cfg.team_a.llm_provider = "openai"
    cfg.team_b.llm_provider = "anthropic"
    return cfg


@pytest.fixture
def patched_subsystems(monkeypatch):
    cgp_spy = AsyncMock(return_value="ok-code")
    import src.foundation.code_generation_pipeline as cgp_mod
    monkeypatch.setattr(cgp_mod, "generate_strategy", cgp_spy)

    te_inst = MagicMock()
    te_log = MagicMock(name="MatchLog")
    te_log._final_state = {"final_score": {"team_a": 2, "team_b": 1}}
    te_inst.run_match.return_value = te_log
    te_cls = MagicMock(return_value=te_inst)
    import src.orchestration.tick_engine as te_mod
    monkeypatch.setattr(te_mod, "TickEngine", te_cls)

    pmep_spy = AsyncMock(return_value="evolved-code")
    import src.foundation.post_match_evolution_pipeline as pmep_mod
    monkeypatch.setattr(pmep_mod, "evolve_strategy", pmep_spy)

    return {"cgp": cgp_spy, "te": te_inst, "pmep": pmep_spy, "match_log": te_log}


def test_ac_cli_09_pmep_gather_per_match(patched_subsystems):
    """evolve_strategy called for all matches except the last one."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 3, cfg))
    # 3-match season: PMEP after match 1 and 2 only (not match 3) → 2 × 2 = 4 calls
    assert patched_subsystems["pmep"].call_count == 4


def test_match_number_passed_to_pmep(patched_subsystems):
    """match_number is passed correctly per iteration."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 2, cfg))
    # 2-match season: PMEP after match 1 only (not match 2) → 1 × 2 = 2 calls
    call_args_list = patched_subsystems["pmep"].call_args_list
    match_numbers = [c.args[3] for c in call_args_list]
    assert sorted(match_numbers) == [1, 1]


def test_ac_cli_10_success_line_printed(patched_subsystems, capsys):
    """Success: [PMEP] team_X: strategy_v{N+1}.py written (requires at least 2 matches)."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 2, cfg))
    captured = capsys.readouterr()
    assert "strategy_v2.py written" in captured.out


def test_ac_cli_11_single_team_failure_continues(monkeypatch, patched_subsystems, capsys):
    """One PMEP fails, season continues."""
    cfg = _make_config()

    async def fake_evolve(config, team_id, log, n, **_kw):
        if team_id == "team_b":
            raise EvolutionFailedError(
                team_id="team_b",
                match_number=n,
                attempts_made=3,
                last_failure="compile_error"
            )
        return "evolved-code"

    import src.foundation.post_match_evolution_pipeline as pmep_mod
    monkeypatch.setattr(pmep_mod, "evolve_strategy", fake_evolve)

    asyncio.run(_run_season("x.yaml", 2, cfg))
    captured = capsys.readouterr()
    assert "team_b" in captured.err
    assert "compile_error" in captured.err
    # Season should complete both matches (TickEngine called twice)
    assert patched_subsystems["te"].run_match.call_count == 2


def test_ac_cli_12_dual_failure_continues_with_extra_error(monkeypatch, patched_subsystems, capsys):
    """Both teams fail PMEP → both ERRORs + extra "both teams" + season continues."""
    cfg = _make_config()

    async def fake_evolve(config, team_id, log, n, **_kw):
        raise EvolutionFailedError(
            team_id=team_id,
            match_number=n,
            attempts_made=3,
            last_failure="llm_call_error"
        )

    import src.foundation.post_match_evolution_pipeline as pmep_mod
    monkeypatch.setattr(pmep_mod, "evolve_strategy", fake_evolve)

    # 2-match season so PMEP runs after match 1 (last match is skipped)
    asyncio.run(_run_season("x.yaml", 2, cfg))
    captured = capsys.readouterr()
    assert "both teams" in captured.err.lower() or "systemic" in captured.err.lower()


def test_write_failed_error_distinct(monkeypatch, patched_subsystems, capsys):
    """WriteFailedError is detected and logged distinctly."""
    cfg = _make_config()

    async def fake_evolve(config, team_id, log, n, **_kw):
        if team_id == "team_a":
            return "ok"
        raise WriteFailedError("disk full")

    import src.foundation.post_match_evolution_pipeline as pmep_mod
    monkeypatch.setattr(pmep_mod, "evolve_strategy", fake_evolve)

    # 2-match season so PMEP runs after match 1
    asyncio.run(_run_season("x.yaml", 2, cfg))
    captured = capsys.readouterr()
    assert "WriteFailedError" in captured.err or "write_error" in captured.out


def test_unexpected_exception_propagates(monkeypatch, patched_subsystems):
    """Generic exception propagates unhandled."""
    cfg = _make_config()

    async def fake_evolve(config, team_id, log, n, **_kw):
        raise RuntimeError("unexpected boom")

    import src.foundation.post_match_evolution_pipeline as pmep_mod
    monkeypatch.setattr(pmep_mod, "evolve_strategy", fake_evolve)

    # 2-match season so PMEP runs after match 1 and raises
    with pytest.raises(RuntimeError, match="unexpected boom"):
        asyncio.run(_run_season("x.yaml", 2, cfg))


def test_match_complete_line_with_score(patched_subsystems, capsys):
    """[season] match N/N complete | team_a S - team_b S printed."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 1, cfg))
    captured = capsys.readouterr()
    assert "complete" in captured.out
    assert "team_a 2" in captured.out
    assert "team_b 1" in captured.out


def test_match_complete_line_score_fallback(patched_subsystems, capsys, monkeypatch):
    """Match complete line falls back to (0, 0) when score unavailable."""
    # Remove _final_state to test fallback
    te_log = MagicMock(name="MatchLog")
    # No _final_state attribute
    te_inst = MagicMock()
    te_inst.run_match.return_value = te_log
    import src.orchestration.tick_engine as te_mod
    monkeypatch.setattr(te_mod, "TickEngine", lambda: te_inst)

    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 1, cfg))
    captured = capsys.readouterr()
    assert "team_a 0 - team_b 0" in captured.out


def test_pmep_failure_message_formats(monkeypatch, patched_subsystems, capsys):
    """Verify specific error message formats for PMEP failures."""
    cfg = _make_config()

    async def fake_evolve(config, team_id, log, n, **_kw):
        if team_id == "team_a":
            raise EvolutionFailedError(
                team_id=team_id,
                match_number=n,
                attempts_made=2,
                last_failure="syntax_error"
            )
        elif team_id == "team_b":
            raise WriteFailedError(f"permission denied for {team_id}")
        return "ok"

    import src.foundation.post_match_evolution_pipeline as pmep_mod
    monkeypatch.setattr(pmep_mod, "evolve_strategy", fake_evolve)

    # 2-match season so PMEP runs after match 1
    asyncio.run(_run_season("x.yaml", 2, cfg))
    captured = capsys.readouterr()

    # Check stderr error messages
    assert "EvolutionFailedError" in captured.err
    assert "syntax_error" in captured.err
    assert "WriteFailedError" in captured.err
    assert "permission denied" in captured.err

    # Check stdout failure messages
    assert "FAILED (syntax_error)" in captured.out
    assert "FAILED (write_error)" in captured.out