"""Tests for `_load_team_baseline` sidecar lookup (ADR-0023).

Verifies that the CLI's per-team baseline loader pulls provider/model from
the strategy's sidecar instead of hardcoding `baseline / hand-written`.
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from src.orchestration.cli import _load_team_baseline


def _write_pair(strategies_dir: Path, name: str, source: str, meta: dict | None) -> Path:
    """Helper: write `<name>.py` and (optionally) `<name>.meta.json`."""
    strategies_dir.mkdir(parents=True, exist_ok=True)
    src = strategies_dir / f"{name}.py"
    src.write_text(source, encoding="utf-8")
    if meta is not None:
        (strategies_dir / f"{name}.meta.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )
    return src


def test_baseline_loader_reads_llm_sidecar(tmp_path):
    """LLM-generated library file should report its true provider/model."""
    src = _write_pair(
        tmp_path / "strategies",
        "anthropic-claude-sonnet-4-6-1",
        "def decide(g, p, h): return Hold()\n",
        {
            "provider":         "anthropic",
            "model":            "claude-sonnet-4-6",
            "created_by":       "llm",
            "created_at":       "2026-04-25T21:30:00Z",
            "last_modified_at": "2026-04-25T21:30:00Z",
            "prompt":           "press the midfield",
            "template_version": "2.5",
        },
    )

    code, meta, _ = _load_team_baseline("team_a", str(src))

    assert "decide" in code
    assert meta["provider"] == "anthropic"
    assert meta["model"] == "claude-sonnet-4-6"
    assert meta["name"] == "anthropic-claude-sonnet-4-6-1"
    assert meta["version"] == 0


def test_baseline_loader_reads_baseline_sidecar(tmp_path):
    """Seeded baseline.py with sidecar reports provider=baseline."""
    src = _write_pair(
        tmp_path / "strategies",
        "baseline",
        "def decide(g, p, h): return Hold()\n",
        {
            "provider":         "baseline",
            "model":            "hand-written",
            "created_by":       "manual",
            "created_at":       "2026-04-25T21:30:00Z",
            "last_modified_at": "2026-04-25T21:30:00Z",
        },
    )

    _, meta, _ = _load_team_baseline("team_b", str(src))
    assert meta["provider"] == "baseline"
    assert meta["model"] == "hand-written"


def test_baseline_loader_legacy_file_falls_back_to_unknown(tmp_path):
    """Library file without a sidecar (predates ADR-0023) reports unknown."""
    src = _write_pair(
        tmp_path / "strategies",
        "legacy",
        "def decide(g, p, h): return Hold()\n",
        meta=None,  # no sidecar
    )

    _, meta, _ = _load_team_baseline("team_a", str(src))
    assert meta["provider"] == "unknown"
    assert meta["model"] == "unknown"
    assert meta["name"] == "legacy"


def test_baseline_loader_malformed_sidecar_warns_and_falls_back(tmp_path, capsys):
    """A garbage sidecar must not crash the loader — warn and degrade."""
    strategies_dir = tmp_path / "strategies"
    strategies_dir.mkdir(parents=True)
    src = strategies_dir / "broken.py"
    src.write_text("def decide(g, p, h): return Hold()\n", encoding="utf-8")
    (strategies_dir / "broken.meta.json").write_text("not valid json {", encoding="utf-8")

    _, meta, _ = _load_team_baseline("team_a", str(src))
    assert meta["provider"] == "unknown"
    captured = capsys.readouterr()
    assert "WARN sidecar unreadable" in captured.out


def test_baseline_loader_logs_provider_in_status_line(tmp_path, capsys):
    """The status line should expose the provider/model so a season log
    immediately shows what was loaded."""
    src = _write_pair(
        tmp_path / "strategies",
        "openai-gpt-4o-1",
        "def decide(g, p, h): return Hold()\n",
        {
            "provider":         "openai",
            "model":            "gpt-4o",
            "created_by":       "llm",
            "created_at":       "2026-04-25T21:30:00Z",
            "last_modified_at": "2026-04-25T21:30:00Z",
            "prompt":           "x",
            "template_version": "2.5",
        },
    )

    _load_team_baseline("team_a", str(src))
    out = capsys.readouterr().out
    assert "provider=openai" in out
    assert "model=gpt-4o" in out
