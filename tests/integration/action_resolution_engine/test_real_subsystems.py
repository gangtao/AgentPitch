"""ARE integration tests with real subsystems — no mocks below the test boundary.

Constructs ActionResolutionEngine wired to real GameStateManager, real
PlayerMovementSystem + BallPhysicsSystem modules, real Sandbox, and real
FallbackHandler. Strategies are hand-seeded (not LLM-generated) but compile
through the real Sandbox.

This file replaces the mock-heavy `tests/integration/action_resolution_engine/`
test that was renamed to `tests/unit/action_resolution_engine/test_orchestration.py`
on 2026-04-22. The mock version verifies orchestration invariants; this file
verifies that ARE actually works against real collaborators.

Part of tech-debt #5 cleanup (integration-test mocking audit).
"""

from __future__ import annotations

import pytest

from src.core.game_state_manager import GameStateManager
from src.foundation.action_resolution_engine import ActionResolutionEngine
from src.foundation.fallback import FallbackHandler
from src.foundation.formation_and_role_system import compute_anchors
from src.foundation.sandbox import Sandbox, ExecutionStatus
import src.core.player_movement_system as pms_mod
import src.core.ball_physics_system as bps_mod
from tests.unit.game_state_manager.conftest import _create_test_config


HOLD_STRATEGY = """\
def decide(game_state, player_state, history):
    return Hold()
"""


@pytest.fixture
def real_are(tmp_path):
    """Build an ARE wired to real subsystems with all 10 players seeded with Hold()."""
    config = _create_test_config(
        seed=42,
        tick_rate=10,
        duration_minutes=1,
        log_dir=str(tmp_path),
        match_id="are_real_test",
    )
    anchors = compute_anchors(config)
    gsm = GameStateManager(config, anchors)
    gsm.start_match()  # PRE_MATCH -> KICK_OFF, ball at center, kickoff player has ball

    sandbox = Sandbox()
    fallback_handler = FallbackHandler()

    # Compile Hold strategy for every player so resolve_tick has something to execute.
    all_pids = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]
    for pid in all_pids:
        result = sandbox.compile(pid, HOLD_STRATEGY)
        assert result.status == ExecutionStatus.SUCCESS, (
            f"sandbox.compile failed for {pid}: {result.error_type}"
        )

    are = ActionResolutionEngine(gsm, pms_mod, bps_mod, sandbox, fallback_handler)
    return are, gsm


def test_resolve_tick_returns_record_per_player(real_are):
    """ARE must produce one action record for each of the 10 players."""
    are, _gsm = real_are

    records = are.resolve_tick(tick=0, history=[])

    assert isinstance(records, dict)
    expected_pids = {f"team_a_{i}" for i in range(5)} | {f"team_b_{i}" for i in range(5)}
    assert set(records.keys()) == expected_pids


def test_resolve_tick_hold_strategy_returns_no_fallbacks(real_are):
    """A clean Hold() strategy compiles + executes successfully — no fallback substitutions."""
    are, _gsm = real_are

    records = are.resolve_tick(tick=0, history=[])

    for pid, rec in records.items():
        assert rec.get("action") == "Hold", (
            f"{pid}: expected action=Hold, got {rec.get('action')!r}"
        )
        # `result` field present and non-failure for the success path
        assert rec.get("result") in ("ok", None, "success"), (
            f"{pid}: unexpected result {rec.get('result')!r}"
        )


def test_resolve_tick_determinism_same_seed_same_records(tmp_path):
    """Two ARE instances over identical configs produce identical tick records."""
    def _build_engine():
        config = _create_test_config(
            seed=42, tick_rate=10, duration_minutes=1,
            log_dir=str(tmp_path), match_id="determinism_test",
        )
        anchors = compute_anchors(config)
        gsm = GameStateManager(config, anchors)
        gsm.start_match()
        sandbox = Sandbox()
        fallback = FallbackHandler()
        for i in range(5):
            for team in ("team_a", "team_b"):
                pid = f"{team}_{i}"
                sandbox.compile(pid, HOLD_STRATEGY)
        return ActionResolutionEngine(gsm, pms_mod, bps_mod, sandbox, fallback)

    are1 = _build_engine()
    are2 = _build_engine()

    records1 = are1.resolve_tick(tick=0, history=[])
    records2 = are2.resolve_tick(tick=0, history=[])

    # Compare action types per player — full record may include non-deterministic
    # diagnostic fields (e.g. timing), so compare the deterministic surface.
    assert {pid: r.get("action") for pid, r in records1.items()} == \
           {pid: r.get("action") for pid, r in records2.items()}


# ---------------------------------------------------------------------------
# ADR-0015 — action cooldowns
# ---------------------------------------------------------------------------


def test_cooldown_blocks_consecutive_pass(tmp_path):
    """Per ADR-0015 amended (2026-04-22): a player cannot take any of
    Pass/Shoot/Tackle/Pickup within action_cooldown_ticks of their previous
    non-trivial action.

    Strategy: kickoff player has just acted at tick 0; tries to Pass at tick 1
    (must be blocked because cooldown=10).
    """
    config = _create_test_config(
        seed=42, tick_rate=10, duration_minutes=1,
        log_dir=str(tmp_path), match_id="cooldown_test",
    )
    anchors = compute_anchors(config)
    gsm = GameStateManager(config, anchors)
    gsm.start_match()

    # Manually mark an action as just performed at tick 0 by the kickoff carrier.
    carrier_id = gsm.state.ball["carrier_id"]
    gsm.record_action_cooldown(carrier_id, 0)

    sandbox = Sandbox()
    fallback_handler = FallbackHandler()
    pass_strategy = """
def decide(game_state, player_state, history):
    return Pass(target_pos=(80.0, 30.0), power=10)
"""
    for i in range(5):
        for team in ("team_a", "team_b"):
            pid = f"{team}_{i}"
            sandbox.compile(pid, pass_strategy)

    are = ActionResolutionEngine(gsm, pms_mod, bps_mod, sandbox, fallback_handler)

    # Tick 1 — within cooldown window for the kickoff carrier
    records = are.resolve_tick(tick=1, history=[])

    rec = records[carrier_id]
    assert rec.get("action") == "Hold", "Effective action is Hold when cooldown active"
    assert rec.get("result") == "cooldown_blocked", \
        f"Expected cooldown_blocked, got {rec.get('result')!r}"
    assert rec.get("intended_action") == "Pass", \
        f"Intent surfaced as intended_action, got {rec.get('intended_action')!r}"


def test_goal_line_check_robust_to_halftime_swap(tmp_path):
    """Regression: _is_goal_line_crossed must check geometric x=0/field_width,
    not team_*_goal_x (which swaps at halftime).

    Bug history (2026-04-22): the check used `x <= team_a_goal_x or x >=
    team_b_goal_x`. After swap_attack_direction, team_a_goal_x=field_width
    and team_b_goal_x=0, making the predicate True for ANY x — every tick
    fired a phantom goal. Surfaced when post-halftime kickoffs each scored
    1 tick later (8 fake goals in succession).
    """
    config = _create_test_config(
        seed=42, tick_rate=10, duration_minutes=1,
        log_dir=str(tmp_path), match_id="halftime_swap_test",
    )
    anchors = compute_anchors(config)
    gsm = GameStateManager(config, anchors)
    sandbox = Sandbox()
    fallback = FallbackHandler()
    are = ActionResolutionEngine(gsm, pms_mod, bps_mod, sandbox, fallback)

    # Simulate halftime swap.
    gsm.swap_attack_direction()
    snap = gsm.build_tick_snapshot()
    # Sanity: post-swap, goals are at swapped x positions.
    assert gsm.state.field["team_a_goal_x"] == config.match.field_width
    assert gsm.state.field["team_b_goal_x"] == 0.0

    # Ball in the middle of the field — NOT at any goal line.
    middle_pos = (config.match.field_width / 2.0, config.match.field_height / 2.0)
    assert not are._is_goal_line_crossed(middle_pos, snap), (
        "Phantom goal: middle-field position incorrectly classified as goal-line crossing post-halftime"
    )

    # Ball at x=0 (geometric goal line) WITH y in goal extents — should fire.
    on_left_line = (0.0, config.match.field_height / 2.0)
    assert are._is_goal_line_crossed(on_left_line, snap), \
        "Ball at x=0 in goal mouth should be a goal line crossing"
    # Defending team is whichever team's goal is at x=0 — which is team_b post-swap.
    assert are._get_defending_team(on_left_line, snap) == "team_b"

    # Ball at x=field_width with y in goal extents.
    on_right_line = (config.match.field_width, config.match.field_height / 2.0)
    assert are._is_goal_line_crossed(on_right_line, snap)
    # Post-swap, team_a's goal is at x=field_width — so they're the defender.
    assert are._get_defending_team(on_right_line, snap) == "team_a"


def test_player_separation_enforced_after_movement(tmp_path):
    """Per ADR-0017: after Phase 4 movement-commit, no two players should
    be within min_player_separation of each other.

    Setup: GK + DEF on team_a both placed near each other; force movement
    that would put them at the same position. Verify they end up >= 1.0u
    apart after Phase 4.
    """
    config = _create_test_config(
        seed=42, tick_rate=10, duration_minutes=1,
        log_dir=str(tmp_path), match_id="separation_test",
    )
    anchors = compute_anchors(config)
    gsm = GameStateManager(config, anchors)

    # Force two players to overlap in GSM state — directly mutate.
    gsm.state.players["team_a_0"]["position"] = (50.0, 30.0)
    gsm.state.players["team_a_1"]["position"] = (50.0, 30.0)

    sandbox = Sandbox()
    fallback = FallbackHandler()
    # Hold strategy — no movement intent. Separation should still push them
    # apart because they start overlapping.
    for i in range(5):
        for team in ("team_a", "team_b"):
            sandbox.compile(f"{team}_{i}", HOLD_STRATEGY)

    are = ActionResolutionEngine(gsm, pms_mod, bps_mod, sandbox, fallback)
    are.resolve_tick(tick=0, history=[])

    # After Phase 4, the two players should be apart by at least min_player_separation
    p0 = gsm.state.players["team_a_0"]["position"]
    p1 = gsm.state.players["team_a_1"]["position"]
    d = ((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2) ** 0.5
    min_sep = config.simulation.min_player_separation
    assert d >= min_sep - 1e-6, (
        f"Players still overlapping: team_a_0 at {p0}, team_a_1 at {p1}, distance {d}"
    )


def test_player_separation_disabled_when_zero(tmp_path):
    """Per ADR-0017: setting min_player_separation=0 disables the constraint."""
    from src.foundation.config_models import (
        MatchConfig, MatchParams, OutputConfig, PlayerConfig, TeamConfig, SimulationConfig
    )
    config = MatchConfig(
        match=MatchParams(
            seed=42, tick_rate=10, duration_minutes=1,
            field_width=100.0, field_height=60.0, match_id="sep_off",
        ),
        # Disable both separation AND snap so positions stay exactly where
        # we set them. Per ADR-0022 amendment d, Hold actions now go through
        # PMS and the snap can drift idle players — this test only cares
        # about ADR-0017 separation behavior, so snap is turned off to
        # isolate that one variable.
        simulation=SimulationConfig(
            min_player_separation=0.0,
            formation_snap_enabled=False,
        ),
        output=OutputConfig(log_dir=str(tmp_path)),
        team_a=TeamConfig(
            team_id="team_a", name="Team A",
            llm_provider="openai", llm_model="gpt-4o", api_key="t",
            players=[
                PlayerConfig(player_id=f"team_a_{i}", role=role,
                             speed=10, skill=10, strength=10,
                             save=10 if role == "GK" else 0,
                             discipline=10, dribbling=10)
                for i, role in enumerate(["GK", "DEF", "DEF", "MID", "FWD"])
            ],
        ),
        team_b=TeamConfig(
            team_id="team_b", name="Team B",
            llm_provider="anthropic", llm_model="claude", api_key="t",
            players=[
                PlayerConfig(player_id=f"team_b_{i}", role=role,
                             speed=10, skill=10, strength=10,
                             save=10 if role == "GK" else 0,
                             discipline=10, dribbling=10)
                for i, role in enumerate(["GK", "DEF", "DEF", "MID", "FWD"])
            ],
        ),
    )
    anchors = compute_anchors(config)
    gsm = GameStateManager(config, anchors)
    gsm.state.players["team_a_0"]["position"] = (50.0, 30.0)
    gsm.state.players["team_a_1"]["position"] = (50.0, 30.0)

    sandbox = Sandbox()
    fallback = FallbackHandler()
    for i in range(5):
        for team in ("team_a", "team_b"):
            sandbox.compile(f"{team}_{i}", HOLD_STRATEGY)

    are = ActionResolutionEngine(gsm, pms_mod, bps_mod, sandbox, fallback)
    are.resolve_tick(tick=0, history=[])

    # With separation disabled, the two players should remain overlapping
    p0 = gsm.state.players["team_a_0"]["position"]
    p1 = gsm.state.players["team_a_1"]["position"]
    assert p0 == p1 == (50.0, 30.0), f"Expected positions unchanged; got {p0}, {p1}"


def test_cooldown_zero_disables_blocking(tmp_path):
    """Per ADR-0015 amended: setting action_cooldown_ticks=0 disables blocking."""
    from src.foundation.config_models import (
        MatchConfig, MatchParams, OutputConfig, PlayerConfig, TeamConfig, SimulationConfig
    )
    config = MatchConfig(
        match=MatchParams(
            seed=42, tick_rate=10, duration_minutes=1,
            field_width=100.0, field_height=60.0, match_id="cd_off",
        ),
        simulation=SimulationConfig(action_cooldown_ticks=0),  # disabled
        output=OutputConfig(log_dir=str(tmp_path)),
        team_a=TeamConfig(
            team_id="team_a", name="Team A",
            llm_provider="openai", llm_model="gpt-4o", api_key="test",
            players=[
                PlayerConfig(player_id=f"team_a_{i}", role=role,
                             speed=10, skill=10, strength=10,
                             save=10 if role == "GK" else 0,
                             discipline=10, dribbling=10)
                for i, role in enumerate(["GK", "DEF", "DEF", "MID", "FWD"])
            ],
        ),
        team_b=TeamConfig(
            team_id="team_b", name="Team B",
            llm_provider="anthropic", llm_model="claude", api_key="test",
            players=[
                PlayerConfig(player_id=f"team_b_{i}", role=role,
                             speed=10, skill=10, strength=10,
                             save=10 if role == "GK" else 0,
                             discipline=10, dribbling=10)
                for i, role in enumerate(["GK", "DEF", "DEF", "MID", "FWD"])
            ],
        ),
    )
    anchors = compute_anchors(config)
    gsm = GameStateManager(config, anchors)
    gsm.start_match()

    carrier_id = gsm.state.ball["carrier_id"]
    gsm.record_action_cooldown(carrier_id, 0)

    sandbox = Sandbox()
    fallback_handler = FallbackHandler()
    pass_strategy = """
def decide(game_state, player_state, history):
    return Pass(target_pos=(80.0, 30.0), power=10)
"""
    for i in range(5):
        for team in ("team_a", "team_b"):
            sandbox.compile(f"{team}_{i}", pass_strategy)

    are = ActionResolutionEngine(gsm, pms_mod, bps_mod, sandbox, fallback_handler)

    records = are.resolve_tick(tick=1, history=[])

    # With cooldown disabled, the Pass should NOT be blocked
    assert records[carrier_id].get("result") != "cooldown_blocked"
