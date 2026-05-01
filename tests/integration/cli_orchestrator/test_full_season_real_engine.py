"""CLI integration test with REAL TickEngine + subsystems.

Companion to `test_full_season.py` (which keeps every subsystem mocked to test
CLI-internal concerns like stdout format and exit codes). This file exercises
the full season path with a real TickEngine, real GSM/ARE/PMS/BPS/Sandbox, and
hand-seeded strategies — only the LLM-bound CGP/PMEP calls are mocked
(justified: they wrap external API calls).

Asserts the orchestrator + engine round-trip produces events.jsonl/meta.json
for each match in the season.

Part of tech-debt #5 cleanup (integration-test mocking audit).
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.foundation.strategy_storage import StrategyMetadata, write_strategy
from src.orchestration.cli import _run_season
from tests.unit.game_state_manager.conftest import _create_test_config


HOLD_STRATEGY = """\
def decide(game_state, player_state, history):
    return Hold()
"""


def _seed_strategy(log_dir: str, team_id: str, match_number: int) -> None:
    """Helper to write a Hold strategy via real Strategy Storage."""
    write_strategy(
        log_dir=log_dir,
        team_id=team_id,
        code=HOLD_STRATEGY,
        metadata=StrategyMetadata(
            team_id=team_id,
            match_number=match_number,
            llm_provider="manual",
            llm_model="n/a",
            generated_by="real-engine-integration-test",
        ),
    )


@pytest.fixture
def real_engine_config(tmp_path):
    """Real MatchConfig pointed at tmp_path with a 1-minute match."""
    return _create_test_config(
        seed=42,
        tick_rate=10,
        duration_minutes=1,
        log_dir=str(tmp_path),
        match_id="cli_real_test",
    )


@pytest.fixture
def patched_llm_only(real_engine_config, monkeypatch):
    """Mock only the LLM-bound boundaries (CGP, PMEP). TickEngine runs for real.

    CGP and PMEP each have side effects that write a fresh Hold strategy to
    disk via the real Strategy Storage — emulates the real LLM-driven output
    so the real TickEngine has something to read in its compile phase.
    """
    log_dir = real_engine_config.output.log_dir

    async def cgp_side_effect(config, team_id, **_kw):
        _seed_strategy(log_dir, team_id, match_number=0)
        return "ok-code"

    async def pmep_side_effect(config, team_id, match_log, match_number, **_kw):
        _seed_strategy(log_dir, team_id, match_number=match_number)
        return "evolved-code"

    cgp_spy = AsyncMock(side_effect=cgp_side_effect)
    pmep_spy = AsyncMock(side_effect=pmep_side_effect)

    import src.foundation.code_generation_pipeline as cgp_mod
    import src.foundation.post_match_evolution_pipeline as pmep_mod
    monkeypatch.setattr(cgp_mod, "generate_strategy", cgp_spy)
    monkeypatch.setattr(pmep_mod, "evolve_strategy", pmep_spy)

    return {"cgp": cgp_spy, "pmep": pmep_spy}


def test_full_season_real_engine_writes_match_artifacts(real_engine_config, patched_llm_only):
    """A 1-match season with a real TickEngine produces events.jsonl + meta.json on disk."""
    asyncio.run(_run_season("ignored.yaml", 1, real_engine_config))

    match_dir = (
        Path(real_engine_config.output.log_dir)
        / f"match_{real_engine_config.match.match_id}"
    )
    assert (match_dir / "events.jsonl").exists()
    assert (match_dir / "meta.json").exists()

    meta = json.loads((match_dir / "meta.json").read_text())
    assert meta["match_id"] == real_engine_config.match.match_id


def test_full_season_real_engine_calls_cgp_and_pmep(real_engine_config, patched_llm_only):
    """Verify CLI orchestrator drove CGP once pre-season; PMEP skipped for a 1-match season (final match)."""
    asyncio.run(_run_season("ignored.yaml", 1, real_engine_config))

    # CGP called once per team pre-season
    assert patched_llm_only["cgp"].call_count == 2
    # PMEP skipped — a 1-match season means the only match is the final; no evolution needed
    assert patched_llm_only["pmep"].call_count == 0


def test_explicit_strategy_mode_skips_global_strategy_archive(tmp_path):
    """Per-team baseline mode (--strategy-a/--strategy-b) hands code to the
    engine directly. No write_strategy() to <log_dir>/strategies/ should
    happen — that archive is reserved for season/PMEP. Per-match snapshots
    land inside the match dir instead.
    """
    strat_a = tmp_path / "user_strategy_a.py"
    strat_b = tmp_path / "user_strategy_b.py"
    strat_a.write_text(HOLD_STRATEGY)
    strat_b.write_text(HOLD_STRATEGY)

    config = _create_test_config(
        seed=42, tick_rate=10, duration_minutes=1,
        log_dir=str(tmp_path), match_id="explicit_test",
    )

    asyncio.run(_run_season(
        "ignored.yaml", 1, config,
        strategy_a_path=str(strat_a),
        strategy_b_path=str(strat_b),
    ))

    # Match dir + per-match snapshots exist.
    match_dir = tmp_path / "match_explicit_test"
    assert (match_dir / "events.jsonl").exists()
    assert (match_dir / "meta.json").exists()
    assert (match_dir / "strategy_team_a.py").read_text() == HOLD_STRATEGY
    assert (match_dir / "strategy_team_b.py").read_text() == HOLD_STRATEGY

    # Critically: the global archive is NOT touched.
    assert not (tmp_path / "strategies").exists(), (
        "Explicit-strategy mode should not write to <log_dir>/strategies/ — "
        "that archive is for season/PMEP only."
    )


def test_full_season_real_engine_2_matches_persists_each(tmp_path, monkeypatch):
    """Two matches in a season — last match's artifacts overwrite the first's
    (same match_id), proving the write loop fires per match."""
    config = _create_test_config(
        seed=42, tick_rate=10, duration_minutes=1,
        log_dir=str(tmp_path), match_id="multimatch_test",
    )

    async def cgp_side_effect(config, team_id, **_kw):
        _seed_strategy(str(tmp_path), team_id, match_number=0)
        return "ok-code"

    async def pmep_side_effect(config, team_id, match_log, match_number, **_kw):
        _seed_strategy(str(tmp_path), team_id, match_number=match_number)
        return "evolved-code"

    import src.foundation.code_generation_pipeline as cgp_mod
    import src.foundation.post_match_evolution_pipeline as pmep_mod
    monkeypatch.setattr(cgp_mod, "generate_strategy", AsyncMock(side_effect=cgp_side_effect))
    monkeypatch.setattr(pmep_mod, "evolve_strategy", AsyncMock(side_effect=pmep_side_effect))

    asyncio.run(_run_season("ignored.yaml", 2, config))

    match_dir = tmp_path / "match_multimatch_test"
    # Both files must exist after the season
    assert (match_dir / "events.jsonl").exists()
    assert (match_dir / "meta.json").exists()
