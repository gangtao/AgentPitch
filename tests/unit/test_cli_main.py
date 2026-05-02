"""Tests for top-level CLI dispatcher (src/cli.py)."""
from __future__ import annotations

import sys
from unittest.mock import patch

import pytest


def _run_cli(*args):
    """Run src.cli.main with given argv and return exit_code."""
    from src.cli import main
    with patch.object(sys, "argv", ["agent-pitch", *args]):
        with pytest.raises(SystemExit) as exc_info:
            main()
    return exc_info.value.code


def test_version_flag_exits_zero(capsys):
    code = _run_cli("--version")
    assert code == 0


def test_version_flag_short_exits_zero(capsys):
    code = _run_cli("-V")
    assert code == 0


def test_version_flag_prints_name_and_version(capsys):
    _run_cli("--version")
    out = capsys.readouterr().out
    assert out.startswith("agent-pitch ")
    version_part = out.strip().split(" ", 1)[1]
    assert "." in version_part, f"Expected semver-like version, got: {version_part!r}"


def test_no_subcommand_exits_two():
    code = _run_cli()
    assert code == 2


def test_unknown_subcommand_exits_two():
    code = _run_cli("bogus")
    assert code == 2
