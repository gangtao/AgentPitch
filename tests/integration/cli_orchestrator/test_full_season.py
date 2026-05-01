"""CLI Story 005 integration tests — full-season smoke + KeyboardInterrupt + exit codes."""
from __future__ import annotations
import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.orchestration.cli import main, _run_season


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
    te_log._final_state = {'final_score': {'team_a': 1, 'team_b': 0}}
    te_log.get_final_score = MagicMock(return_value=(1, 0))
    te_inst.run_match.return_value = te_log
    te_cls = MagicMock(return_value=te_inst)
    import src.orchestration.tick_engine as te_mod
    monkeypatch.setattr(te_mod, "TickEngine", te_cls)

    pmep_spy = AsyncMock(return_value="evolved-code")
    import src.foundation.post_match_evolution_pipeline as pmep_mod
    monkeypatch.setattr(pmep_mod, "evolve_strategy", pmep_spy)

    return {"cgp": cgp_spy, "te": te_inst, "pmep": pmep_spy}


def test_ac_cli_13_progress_format(patched_subsystems, capsys):
    """A successful 2-match season produces stdout matching GDD format."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 2, cfg))
    captured = capsys.readouterr()
    out = captured.out
    # Verify expected progress lines per GDD Rule 7
    assert "[season] generating initial strategies" in out
    assert "[CGP] team_a" in out
    assert "[CGP] team_b" in out
    assert "match 1/2 starting" in out
    assert "match 2/2 starting" in out
    assert "[PMEP] team_a" in out
    assert "[PMEP] team_b" in out
    assert "season complete" in out
    assert "2 matches played" in out


def test_ac_cli_14_no_http_imports():
    """agent_pitch run does NOT trigger HTTP framework imports.

    Verifies via static source-text inspection (no sys.modules manipulation,
    which would pollute other tests).
    """
    from pathlib import Path
    cli_root = Path("src/orchestration/cli")
    forbidden = ["fastapi", "uvicorn", "flask", "starlette"]
    for py_file in cli_root.rglob("*.py"):
        text = py_file.read_text()
        for f in forbidden:
            assert f not in text, f"{py_file} mentions forbidden {f}"


def test_ac_cli_15_keyboard_interrupt_exits_130(monkeypatch, capsys):
    """KeyboardInterrupt in asyncio.run → [agent_pitch] Season aborted. + sys.exit(130)."""
    # Mock argv
    monkeypatch.setattr(sys, "argv", ["agent_pitch", "run", "--config", "x.yaml", "--season-length", "1"])

    # Mock successful config load first
    cfg = _make_config()
    monkeypatch.setattr("src.orchestration.cli.load_config", lambda p: cfg)

    # Mock asyncio.run to raise KeyboardInterrupt - use the same pattern as existing tests
    def raise_kbd(*args, **kw):
        raise KeyboardInterrupt
    monkeypatch.setattr("src.orchestration.cli.asyncio.run", raise_kbd)

    with pytest.raises(SystemExit) as ei:
        main()
    assert ei.value.code == 130
    captured = capsys.readouterr()
    assert "Season aborted" in captured.out


def test_exit_code_0_on_season_complete(monkeypatch, patched_subsystems):
    """After season completes naturally, main() returns (no sys.exit). Exit code 0 implicit."""
    # Mock argv
    monkeypatch.setattr(sys, "argv", ["agent_pitch", "run", "--config", "x.yaml", "--season-length", "1"])

    # Mock successful config load
    cfg = _make_config()
    monkeypatch.setattr("src.orchestration.cli.load_config", lambda p: cfg)

    # main() should return without raising SystemExit
    main()


def test_closure_line_match_count(patched_subsystems, capsys):
    """[season] season complete | {N} matches played printed for season_length=5."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 5, cfg))
    captured = capsys.readouterr()
    assert "5 matches played" in captured.out


def test_full_season_2_match_smoke(patched_subsystems, capsys):
    """End-to-end 2-match season runs all 4 phase types without raising."""
    cfg = _make_config()
    asyncio.run(_run_season("x.yaml", 2, cfg))
    # Verify each subsystem called expected times
    assert patched_subsystems["cgp"].call_count == 2  # 1 pre-season × 2 teams
    assert patched_subsystems["te"].run_match.call_count == 2  # 2 matches
    assert patched_subsystems["pmep"].call_count == 2  # (season_length - 1) matches × 2 teams; final match skips PMEP


def test_keyboard_interrupt_message_format(monkeypatch, capsys):
    """KeyboardInterrupt message exactly matches GDD spec: '[agent_pitch] Season aborted.'."""
    # Mock argv
    monkeypatch.setattr(sys, "argv", ["agent_pitch", "run", "--config", "x.yaml", "--season-length", "1"])

    # Mock successful config load first
    cfg = _make_config()
    monkeypatch.setattr("src.orchestration.cli.load_config", lambda p: cfg)

    # Mock asyncio.run to raise KeyboardInterrupt
    def raise_kbd(*args, **kw):
        raise KeyboardInterrupt
    monkeypatch.setattr("src.orchestration.cli.asyncio.run", raise_kbd)

    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    # Exact message per story spec
    assert "[agent_pitch] Season aborted." in captured.out


def test_config_load_failure_exits_1(monkeypatch, capsys):
    """Config load exception → stderr message + sys.exit(1)."""
    monkeypatch.setattr(sys, "argv", ["agent_pitch", "run", "--config", "bad.yaml", "--season-length", "1"])

    # Use the same pattern as existing tests for config load failure
    monkeypatch.setattr("src.orchestration.cli.load_config", lambda p: (_ for _ in ()).throw(ValueError("config parse failed")))

    with pytest.raises(SystemExit) as ei:
        main()
    assert ei.value.code == 1
    captured = capsys.readouterr()
    assert "config load failed" in captured.err
    assert "config parse failed" in captured.err