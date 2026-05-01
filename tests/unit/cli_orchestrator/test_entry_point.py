"""Tests for CLI Story 001: entry point + argparse + load_config."""
from __future__ import annotations
import sys
from unittest.mock import MagicMock, patch

import pytest

from src.orchestration.cli import main, _run_season, _build_parser


def test_main_importable():
    """AC-CLI-01: main is importable and callable."""
    assert callable(main)


def test_argparse_missing_args_exits_2(monkeypatch):
    """AC-CLI-02: missing required args → usage error + exit 2."""
    monkeypatch.setattr(sys, "argv", ["agent_pitch"])
    with pytest.raises(SystemExit) as ei:
        main()
    assert ei.value.code == 2


def test_argparse_missing_season_length_exits_2(monkeypatch):
    """Missing --season-length → exit 2."""
    monkeypatch.setattr(sys, "argv", ["agent_pitch", "run", "--config", "x.yaml"])
    with pytest.raises(SystemExit) as ei:
        main()
    assert ei.value.code == 2


def test_argparse_zero_season_length_exits_2(monkeypatch):
    """--season-length 0 → exit 2."""
    monkeypatch.setattr(sys, "argv", ["agent_pitch", "run", "--config", "x.yaml", "--season-length", "0"])
    with pytest.raises(SystemExit) as ei:
        main()
    assert ei.value.code == 2


def test_argparse_negative_season_length_exits_2(monkeypatch):
    """--season-length -5 → exit 2."""
    monkeypatch.setattr(sys, "argv", ["agent_pitch", "run", "--config", "x.yaml", "--season-length", "-5"])
    with pytest.raises(SystemExit) as ei:
        main()
    assert ei.value.code == 2


def test_load_config_failure_exits_1(monkeypatch, capsys):
    """AC: load_config exception → stderr + sys.exit(1)."""
    monkeypatch.setattr(sys, "argv", ["agent_pitch", "run", "--config", "missing.yaml", "--season-length", "1"])
    monkeypatch.setattr("src.orchestration.cli.load_config", lambda p: (_ for _ in ()).throw(FileNotFoundError("nope")))
    with pytest.raises(SystemExit) as ei:
        main()
    assert ei.value.code == 1
    captured = capsys.readouterr()
    assert "config load failed" in captured.err


def test_no_async_before_load_config(monkeypatch):
    """asyncio.run called only AFTER load_config succeeds."""
    monkeypatch.setattr(sys, "argv", ["agent_pitch", "run", "--config", "ok.yaml", "--season-length", "1"])
    monkeypatch.setattr("src.orchestration.cli.load_config", lambda p: MagicMock())
    asyncio_run_spy = MagicMock()
    monkeypatch.setattr("src.orchestration.cli.asyncio.run", asyncio_run_spy)
    main()
    assert asyncio_run_spy.call_count == 1


def test_run_season_invoked_with_args(monkeypatch):
    """_run_season receives (config_path, season_length, config, baseline_path=None)."""
    monkeypatch.setattr(sys, "argv", ["agent_pitch", "run", "--config", "x.yaml", "--season-length", "5"])
    fake_config = MagicMock()
    monkeypatch.setattr("src.orchestration.cli.load_config", lambda p: fake_config)
    captured = {}
    async def fake_run_season(
        config_path,
        season_length,
        config,
        baseline_path=None,
        strategy_a_path=None,
        strategy_b_path=None,
        language_a=None,
        language_b=None,
        arena_id=None,
        arena_dir=None,
    ):
        captured["args"] = (config_path, season_length, config)
        captured["baseline_path"] = baseline_path
        captured["strategy_a_path"] = strategy_a_path
        captured["strategy_b_path"] = strategy_b_path
    monkeypatch.setattr("src.orchestration.cli._run_season", fake_run_season)
    main()
    assert captured["args"] == ("x.yaml", 5, fake_config)
    assert captured["baseline_path"] is None  # default — bypass not active