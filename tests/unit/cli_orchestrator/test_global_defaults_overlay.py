"""Tests for the CLI's --global-defaults overlay (added 2026-04-24).

The overlay reads the Config UI's Game-tab YAML and applies its
SimulationConfig-shaped subset onto the loaded MatchConfig before the
season runs. This lets users edit one global file instead of re-saving
every match config when they tune simulation parameters.

Three behaviors covered here:
  1. Valid overlay actually replaces the targeted simulation values.
  2. Invalid values are rejected (Pydantic re-validates) — the prior
     simulation block is preserved and stderr explains why.
  3. Match-level keys (tick_rate, seed, field_width…) in the global file
     are silently filtered: only SimulationConfig field names overlay.
"""
from __future__ import annotations
import sys
from unittest.mock import MagicMock

import pytest
import yaml

from src.foundation.config_models import (
    MatchConfig, MatchParams, OutputConfig, PlayerConfig,
    SimulationConfig, TeamConfig,
)
from src.orchestration.cli import main


def _five_player_team() -> TeamConfig:
    """Minimal valid 5-player roster (1 GK + 4 outfield)."""
    return TeamConfig(
        players=[
            PlayerConfig(player_id="p1", role="GK",  speed=8,  skill=10, strength=8,
                         save=16, discipline=10, dribbling=10),
            PlayerConfig(player_id="p2", role="DEF", speed=12, skill=12, strength=14,
                         save=0,  discipline=10, dribbling=10),
            PlayerConfig(player_id="p3", role="DEF", speed=12, skill=12, strength=14,
                         save=0,  discipline=10, dribbling=10),
            PlayerConfig(player_id="p4", role="MID", speed=14, skill=14, strength=12,
                         save=0,  discipline=10, dribbling=10),
            PlayerConfig(player_id="p5", role="FWD", speed=16, skill=8,  strength=10,
                         save=0,  discipline=10, dribbling=10),
        ],
    )


def _baseline_config() -> MatchConfig:
    """Hand-built MatchConfig with default simulation values — the overlay's
    starting point for every test in this module.
    """
    return MatchConfig(
        match=MatchParams(
            seed=42, tick_rate=10, duration_minutes=5,
            field_width=100.0, field_height=60.0,
        ),
        simulation=SimulationConfig(),  # all defaults
        output=OutputConfig(log_dir="./logs"),
        team_a=_five_player_team(),
        team_b=_five_player_team(),
    )


@pytest.fixture
def captured_config(monkeypatch):
    """Run main() with stubbed load_config + _run_season + asyncio.run, and
    return whatever config eventually reaches _run_season. Each test in the
    module sets argv before yielding back into the fixture's stash.
    """
    stash: dict = {}

    def fake_load(_path: str) -> MatchConfig:
        return _baseline_config()

    async def fake_run_season(config_path, season_length, config, **_kw):
        stash["config"] = config

    monkeypatch.setattr("src.orchestration.cli.load_config", fake_load)
    monkeypatch.setattr("src.orchestration.cli._run_season", fake_run_season)
    # asyncio.run still runs the coroutine — it'll await fake_run_season and
    # populate stash. (No need to stub asyncio itself.)
    return stash


def test_global_defaults_overlay_valid_values_replace_simulation(
    monkeypatch, tmp_path, captured_config
):
    """Valid overlay → simulation fields take the global file's values; match
    section is untouched."""
    # Arrange — write a global-defaults YAML with values that differ from
    # SimulationConfig defaults.
    gd = tmp_path / "global-defaults.yaml"
    gd.write_text(yaml.safe_dump({
        "goal_reset_ticks": 45,
        "half_time_pause_ticks": 90,
        "action_cooldown_ticks": 5,
    }))
    monkeypatch.setattr(sys, "argv", [
        "agent_pitch", "run",
        "--config", "ignored.yaml",
        "--season-length", "1",
        "--global-defaults", str(gd),
    ])

    # Act
    main()

    # Assert
    cfg = captured_config["config"]
    assert cfg.simulation.goal_reset_ticks == 45
    assert cfg.simulation.half_time_pause_ticks == 90
    assert cfg.simulation.action_cooldown_ticks == 5
    # Match section unchanged.
    assert cfg.match.seed == 42
    assert cfg.match.tick_rate == 10


def test_global_defaults_overlay_invalid_value_keeps_simulation(
    monkeypatch, tmp_path, capsys, captured_config
):
    """Invalid value (out of range) → overlay rejected, prior simulation kept,
    stderr message logged. SimulationConfig.goal_reset_ticks is le=300 — 9999
    must NOT silently land in the runtime config (regression: model_copy with
    update= bypasses Pydantic v2 validation; we reconstruct to force it).
    """
    # Arrange
    gd = tmp_path / "global-defaults.yaml"
    gd.write_text(yaml.safe_dump({"goal_reset_ticks": 9999}))
    monkeypatch.setattr(sys, "argv", [
        "agent_pitch", "run",
        "--config", "ignored.yaml",
        "--season-length", "1",
        "--global-defaults", str(gd),
    ])

    # Act
    main()

    # Assert — simulation stayed at defaults (the bad value was discarded).
    cfg = captured_config["config"]
    assert cfg.simulation.goal_reset_ticks == 30, (
        "Out-of-range global-default must be rejected; original simulation kept"
    )
    # And the user got told why on stderr.
    err = capsys.readouterr().err
    assert "global-defaults overlay rejected" in err


def test_global_defaults_overlay_filters_match_level_keys(
    monkeypatch, tmp_path, captured_config
):
    """Keys that name match-level fields (tick_rate, seed, field_*) must be
    filtered before overlay — only SimulationConfig.model_fields apply. The
    match-level fields stay per-match by design.
    """
    # Arrange — mix match-level fields (which must be ignored) with one
    # legitimate simulation field (which must apply).
    gd = tmp_path / "global-defaults.yaml"
    gd.write_text(yaml.safe_dump({
        "tick_rate": 60,            # match-level — must be ignored
        "seed": 9999,               # match-level — must be ignored
        "field_width": 200.0,       # match-level — must be ignored
        "duration_minutes": 90,     # match-level — must be ignored
        "action_cooldown_ticks": 7, # simulation — must apply
    }))
    monkeypatch.setattr(sys, "argv", [
        "agent_pitch", "run",
        "--config", "ignored.yaml",
        "--season-length", "1",
        "--global-defaults", str(gd),
    ])

    # Act
    main()

    # Assert — match-level fields preserved at their baseline values.
    cfg = captured_config["config"]
    assert cfg.match.tick_rate == 10
    assert cfg.match.seed == 42
    assert cfg.match.field_width == 100.0
    assert cfg.match.duration_minutes == 5
    # Only the simulation key landed.
    assert cfg.simulation.action_cooldown_ticks == 7
