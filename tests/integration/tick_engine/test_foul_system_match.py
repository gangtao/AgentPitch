"""Issue #38 — end-to-end: a deterministic match with fouls enabled produces
foul events with legal restarts, and is reproducible under the seed.

True end-to-end path, no mocks: real TickEngine / GSM / ARE / sandbox with a
hand-seeded press-and-tackle strategy. The foul base rate is cranked to 0.8
and both teams get offensive=18 so fouls reliably occur inside a 1-minute
match.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.foundation.config_models import SimulationConfig
from src.foundation.strategy_storage import write_strategy, StrategyMetadata
from src.orchestration.tick_engine import TickEngine
from tests.unit.game_state_manager.conftest import _create_test_config


# Carrier holds; everyone else chases the ball and tackles the opposing
# carrier when in range — maximizes tackle attempts, hence fouls.
PRESS_AND_TACKLE_STRATEGY = """\
def decide(game_state, player_state, history):
    px, py = player_state["position"]
    bx, by = game_state["ball"]["position"]
    if player_state["has_ball"]:
        return Hold()
    carrier = game_state["ball"]["carrier_id"]
    if carrier and carrier in game_state["players"]:
        cp = game_state["players"][carrier]
        if cp["team"] != player_state["team"]:
            cx, cy = cp["position"]
            if (px - cx) ** 2 + (py - cy) ** 2 <= 4.0:
                return Tackle(target_player_id=carrier)
    return Move(dx=bx - px, dy=by - py, speed=1.0)
"""


def _aggressive_config(tmp_path, seed=42):
    config = _create_test_config(
        seed=seed,
        tick_rate=10,
        duration_minutes=1,
        log_dir=str(tmp_path),
        match_id="foul_test",
    )
    # Aggressive players: rebuild both teams with offensive=18.
    def _aggro(team_cfg):
        players = [p.model_copy(update={"offensive": 18}) for p in team_cfg.players]
        return team_cfg.model_copy(update={"players": players})
    return config.model_copy(update={
        "simulation": SimulationConfig(tackle_foul_base=0.8),
        "team_a": _aggro(config.team_a),
        "team_b": _aggro(config.team_b),
    })


def _seed_strategies(config):
    for team_id in ("team_a", "team_b"):
        write_strategy(
            log_dir=config.output.log_dir,
            team_id=team_id,
            code=PRESS_AND_TACKLE_STRATEGY,
            metadata=StrategyMetadata(
                team_id=team_id,
                match_number=0,
                llm_provider="manual",
                llm_model="n/a",
                generated_by="foul-system-integration-test",
            ),
        )


def _run(tmp_path, seed=42):
    config = _aggressive_config(tmp_path, seed=seed)
    _seed_strategies(config)
    TickEngine().run_match(config)
    match_dir = Path(config.output.log_dir) / f"match_{config.match.match_id}"
    events = [json.loads(line)
              for line in (match_dir / "events.jsonl").read_text().splitlines()]
    meta = json.loads((match_dir / "meta.json").read_text())
    return events, meta


def _foul_details(events):
    return [a.get("details") or {}
            for t in events for a in (t.get("actions") or [])
            if (a.get("details") or {}).get("foul")]


def test_fouls_occur_and_restart_legally(tmp_path):
    events, _ = _run(tmp_path)
    fouls = _foul_details(events)
    assert fouls, "no fouls in a high-foul-rate match"
    for d in fouls:
        assert d["restart_type"] in ("free_kick_foul", "penalty_kick")
        assert d["restart_team"] in ("team_a", "team_b")
        assert d["offender_id"].startswith("team_")
        # The fouled team takes the restart — never the fouling team.
        assert d["restart_team"] != d["fouling_team"]


def test_foul_severities_recorded_on_tackler(tmp_path):
    events, _ = _run(tmp_path)
    severities = [a["details"].get("foul_severity")
                  for t in events for a in (t.get("actions") or [])
                  if (a.get("details") or {}).get("result") == "foul"
                  or a.get("result") == "foul"]
    severities = [s for s in severities if s]
    assert severities, "no tackler foul records with severity"
    assert set(severities) <= {"careless", "reckless", "excessive_force"}


def test_free_kick_taker_protected_and_auto_kick_fires(tmp_path):
    """Law 13 follow-up: the press strategy Holds when carrying, so every
    free-kick taker stalls — the engine must auto-kick for them, and
    opponents' tackles on the waiting taker must be voided."""
    events, _ = _run(tmp_path)
    auto_kicks = sum(1 for t in events for a in (t.get("actions") or [])
                     if (a.get("details") or {}).get("free_kick_auto_kick"))
    voided = sum(1 for t in events for a in (t.get("actions") or [])
                 if (a.get("details") or {}).get("result") == "no_op_free_kick")
    free_kicks = sum(1 for d in _foul_details(events)
                     if d["restart_type"] == "free_kick_foul")
    assert free_kicks > 0
    assert auto_kicks > 0, "stalling takers must be auto-kicked, not frozen"
    assert voided > 0, "takers must be untacklable while the kick is pending"


def test_match_deterministic_under_seed(tmp_path):
    events1, meta1 = _run(tmp_path / "run1", seed=7)
    events2, meta2 = _run(tmp_path / "run2", seed=7)
    assert meta1["final_score"] == meta2["final_score"]
    assert len(_foul_details(events1)) == len(_foul_details(events2))
