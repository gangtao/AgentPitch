"""Regression test for the `run_match()` auto-persistence contract.

Closes tech-debt #2 (resolved 2026-04-22): TickEngine.run_match() previously
returned an in-memory MatchLog without serializing to disk. The HTTP server and
CLI orchestrator's PMEP step both depend on disk artifacts existing — without
the explicit serialize call, the browser saw nothing and live LLM seasons
produced no observable history.

This test exercises the true end-to-end path with NO mocks: real MatchConfig
constructed via the GSM conftest factory, real TickEngine, real GSM, real
ARE/PMS/BPS, real Sandbox compiling a hand-seeded chase-ball strategy. Asserts
events.jsonl and meta.json appear on disk after run_match() returns.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.orchestration.tick_engine import TickEngine
from src.foundation.strategy_storage import write_strategy, StrategyMetadata
from tests.unit.game_state_manager.conftest import _create_test_config


CHASE_BALL_STRATEGY = """\
def decide(game_state, player_state, history):
    px, py = player_state["position"]
    bx, by = game_state["ball"]["position"]
    return Move(dx=bx - px, dy=by - py, speed=0.5)
"""


@pytest.fixture
def fast_config(tmp_path):
    """Real MatchConfig pointed at tmp_path, short enough for a fast test."""
    return _create_test_config(
        seed=42,
        tick_rate=10,
        duration_minutes=1,           # 600 ticks total — keeps the test under a second
        log_dir=str(tmp_path),
        match_id="persist_test",
    )


def _seed_strategies(config):
    """Hand-write current.py for both teams so TickEngine's compile phase succeeds."""
    for team_id in ("team_a", "team_b"):
        write_strategy(
            log_dir=config.output.log_dir,
            team_id=team_id,
            code=CHASE_BALL_STRATEGY,
            metadata=StrategyMetadata(
                team_id=team_id,
                match_number=0,
                llm_provider="manual",
                llm_model="n/a",
                generated_by="persistence-regression-test",
            ),
        )


def test_run_match_writes_events_jsonl_to_disk(fast_config):
    """run_match() must serialize events.jsonl without an explicit caller call."""
    _seed_strategies(fast_config)

    TickEngine().run_match(fast_config)

    match_dir = Path(fast_config.output.log_dir) / f"match_{fast_config.match.match_id}"
    events_path = match_dir / "events.jsonl"
    assert events_path.exists(), (
        f"events.jsonl not written — run_match() must persist before returning. "
        f"Expected at {events_path}"
    )
    # File should contain at least one tick record.
    lines = events_path.read_text().splitlines()
    assert len(lines) > 0, "events.jsonl is empty"
    first = json.loads(lines[0])
    assert "tick" in first
    assert "player_positions" in first


def test_run_match_writes_meta_json_to_disk(fast_config):
    """meta.json must be written last (atomic sentinel per ADR-0005)."""
    _seed_strategies(fast_config)

    TickEngine().run_match(fast_config)

    meta_path = (
        Path(fast_config.output.log_dir)
        / f"match_{fast_config.match.match_id}"
        / "meta.json"
    )
    assert meta_path.exists(), f"meta.json not written at {meta_path}"
    meta = json.loads(meta_path.read_text())
    assert meta["match_id"] == fast_config.match.match_id
    assert "final_score" in meta
    assert "tick_count" in meta


def test_run_match_caller_does_not_need_to_call_serialize(fast_config):
    """Demonstrates the contract: caller gets persistence with zero ceremony."""
    _seed_strategies(fast_config)

    # Note: NO match_log.serialize() call here.
    log = TickEngine().run_match(fast_config)

    # Caller still receives the in-memory log for inline analysis.
    assert log is not None
    # And the disk artifacts are already there.
    match_dir = Path(fast_config.output.log_dir) / f"match_{fast_config.match.match_id}"
    assert (match_dir / "events.jsonl").exists()
    assert (match_dir / "meta.json").exists()
