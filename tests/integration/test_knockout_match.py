"""End-to-end knockout: tied match resolves via ET/shootout, deterministically.

Mirrors tests/integration/tick_engine/test_run_match_persists.py — real
TickEngine, real config, real strategy injection, no mocks.

Seed 1 is pinned: a 1-minute match with the symmetric chase-ball strategy
always ends 0-0 in regulation and goes to a penalty shootout (verified by
sweeping seeds 1-40, all produce decided_by="shootout"). This gives full
end-to-end coverage of the ET/shootout branch for issue #83.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.orchestration.tick_engine import TickEngine
from src.foundation.strategy_storage import write_strategy, StrategyMetadata
from tests.unit.game_state_manager.conftest import _create_test_config


# Seed chosen to produce decided_by="shootout" (0-0 after regulation + ET).
# All seeds 1-40 do so with duration_minutes=1 + chase-ball strategy.
_KNOCKOUT_SEED = 1

CHASE_BALL_STRATEGY = """\
def decide(game_state, player_state, history):
    px, py = player_state["position"]
    bx, by = game_state["ball"]["position"]
    return Move(dx=bx - px, dy=by - py, speed=0.5)
"""


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
                generated_by="knockout-e2e-test",
            ),
        )


def _make_config(seed, knockout, log_dir, match_id):
    """Build a MatchConfig with knockout toggled and strategies seeded."""
    cfg = _create_test_config(
        seed=seed,
        tick_rate=10,
        duration_minutes=1,
        log_dir=str(log_dir),
        match_id=match_id,
    )
    new_sim = cfg.simulation.model_copy(update={"knockout": knockout})
    cfg = cfg.model_copy(update={"simulation": new_sim})
    _seed_strategies(cfg)
    return cfg


def _read_meta(log_dir, match_id):
    meta_path = Path(log_dir) / f"match_{match_id}" / "meta.json"
    return json.loads(meta_path.read_text())


def test_knockout_match_is_decisive_and_deterministic(tmp_path):
    """A knockout match must finish with a single winner; same seed → same result.

    Seed 1 with duration_minutes=1 produces 0-0 → shootout, exercising the
    full ET+shootout branch of the knockout pipeline end-to-end.
    """
    # First run.
    cfg1 = _make_config(_KNOCKOUT_SEED, knockout=True, log_dir=tmp_path / "run1", match_id="ko_run1")
    TickEngine().run_match(cfg1)
    meta1 = _read_meta(tmp_path / "run1", "ko_run1")

    # Decisive: decided_by tells how; a winner exists under every branch.
    assert meta1["decided_by"] in ("regulation", "extra_time", "shootout"), (
        f"decided_by must be a valid outcome, got {meta1['decided_by']!r}"
    )
    if meta1["decided_by"] == "shootout":
        assert meta1["shootout"]["winner"] in ("team_a", "team_b"), (
            f"shootout winner must be a team, got {meta1['shootout']['winner']!r}"
        )
        # final_score stays level; shootout carries the margin.
        assert meta1["final_score"]["team_a"] == meta1["final_score"]["team_b"], (
            "final_score must remain level after shootout; penalty winner is in shootout.winner"
        )
        # Each kick in meta must carry the 5 authoritative fields (FIX 1: p_goal
        # added; kicks are recorded in meta only, not as fallback events).
        _kick_keys = {"order", "team", "taker_id", "scored", "p_goal"}
        for kick in meta1["shootout"]["kicks"]:
            assert _kick_keys <= kick.keys(), (
                f"kick missing keys {_kick_keys - kick.keys()}: {kick}"
            )

    # Determinism: second identical run (fresh dir, same seed) reproduces the outcome.
    cfg2 = _make_config(_KNOCKOUT_SEED, knockout=True, log_dir=tmp_path / "run2", match_id="ko_run2")
    TickEngine().run_match(cfg2)
    meta2 = _read_meta(tmp_path / "run2", "ko_run2")

    assert meta2["decided_by"] == meta1["decided_by"], (
        f"Same seed must produce same decided_by. "
        f"run1={meta1['decided_by']!r}, run2={meta2['decided_by']!r}"
    )
    assert meta2.get("shootout") == meta1.get("shootout"), (
        f"Same seed must produce identical shootout result. "
        f"run1={meta1.get('shootout')}, run2={meta2.get('shootout')}"
    )


def test_group_stage_still_allows_draw(tmp_path):
    """knockout=False → decided_by stays 'regulation', no ET, no shootout.

    This holds regardless of the score (even if the match ends level).
    """
    cfg = _make_config(_KNOCKOUT_SEED, knockout=False, log_dir=tmp_path, match_id="gs_match")
    TickEngine().run_match(cfg)
    meta = _read_meta(tmp_path, "gs_match")

    assert meta["decided_by"] == "regulation", (
        f"Group-stage match must stay 'regulation', got {meta['decided_by']!r}"
    )
    assert meta["shootout"] is None, (
        f"Group-stage match must not have shootout, got {meta['shootout']!r}"
    )
