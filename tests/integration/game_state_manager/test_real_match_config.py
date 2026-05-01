"""Regression test for the GSM ↔ MatchConfig contract at integration level.

Constructs GameStateManager from a `load_config()` result (i.e. the path the
production CLI orchestrator and TickEngine actually take). Catches the class of
defect that the unit-test `_create_test_config` factory cannot — namely, drift
between the real `MatchConfig` schema and what GSM expects.

Originating defect (resolved 2026-04-21): GSM read `config.players`, `attr.team`,
and `config.field.width/height`, none of which existed on the real MatchConfig.
The unit-test fixture bank had grown a parallel imagined schema, so 1944 tests
passed while the first end-to-end run aborted on `AttributeError`.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.foundation.config_loader import load_config
from src.foundation.formation_and_role_system import compute_anchors
from src.core.game_state_manager import GameStateManager


# Use the playtest YAML as the canonical "real-world" config sample.
PLAYTEST_CONFIG_PATH = (
    Path(__file__).resolve().parents[3] / "playtest" / "match.yaml"
)


@pytest.fixture
def real_match_config(monkeypatch):
    """load_config() requires both API keys to be set in env (config_preprocessor.py)."""
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-not-used-in-tests")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy-not-used-in-tests")
    if not PLAYTEST_CONFIG_PATH.exists():
        pytest.skip(f"sample config not present at {PLAYTEST_CONFIG_PATH}")
    return load_config(str(PLAYTEST_CONFIG_PATH))


def test_gsm_constructs_from_real_loaded_config(real_match_config):
    """GSM must accept the real MatchConfig produced by load_config() — no shim."""
    anchors = compute_anchors(real_match_config)
    gsm = GameStateManager(real_match_config, anchors)

    # Sanity: the 10 expected players landed in state.players keyed by ADR-0004 ID.
    assert set(gsm.state.players.keys()) == {
        f"team_a_{i}" for i in range(5)
    } | {f"team_b_{i}" for i in range(5)}

    # Each player's `team` must be derived from player_id (PlayerConfig has no team).
    for pid, pstate in gsm.state.players.items():
        assert pstate["team"] == pid.rsplit("_", 1)[0]
        # Required attribute fields populated from PlayerConfig
        for key in ("role", "speed", "skill", "strength", "save",
                    "discipline", "dribbling", "position", "formation_position"):
            assert key in pstate, f"{pid} missing {key}"


def test_gsm_field_dims_come_from_match_section(real_match_config):
    """field_width/field_height live under config.match (not config.field)."""
    anchors = compute_anchors(real_match_config)
    gsm = GameStateManager(real_match_config, anchors)

    assert gsm.state.field_width == real_match_config.match.field_width
    assert gsm.state.field_height == real_match_config.match.field_height
    assert gsm.state.ball["position"] == (
        real_match_config.match.field_width / 2.0,
        real_match_config.match.field_height / 2.0,
    )


def test_snapshot_player_dicts_carry_player_id(real_match_config):
    """build_tick_snapshot must inject player_id into each inner dict so ARE
    can iterate snap['players'].values() and read player['player_id']."""
    anchors = compute_anchors(real_match_config)
    gsm = GameStateManager(real_match_config, anchors)
    snap = gsm.build_tick_snapshot()

    for pid, player_dict in snap["players"].items():
        assert player_dict["player_id"] == pid


def test_gsm_cooldown_methods_round_trip(real_match_config):
    """ADR-0015 amended (2026-04-22): record_action_cooldown +
    get_last_action_tick contract for the unified single-timer model.

    Initial state: never performed → -10**9. After recording, get returns
    the recorded tick. One timer per player, no per-action-type fanout.
    """
    anchors = compute_anchors(real_match_config)
    gsm = GameStateManager(real_match_config, anchors)

    # Initially never performed
    assert gsm.get_last_action_tick("team_a_3") == -10**9

    # Record an action at tick 42
    gsm.record_action_cooldown("team_a_3", 42)
    assert gsm.get_last_action_tick("team_a_3") == 42

    # Other players still untouched
    assert gsm.get_last_action_tick("team_a_4") == -10**9


def test_gsm_carries_config_reference(real_match_config):
    """ADR-0015 amended: GSM stores the MatchConfig so ARE can read the
    unified action_cooldown_ticks value."""
    anchors = compute_anchors(real_match_config)
    gsm = GameStateManager(real_match_config, anchors)

    assert gsm.config is real_match_config
    # Sanity: unified cooldown default present
    assert gsm.config.simulation.action_cooldown_ticks == 10


def test_player_state_exposes_cooldown_remaining(real_match_config):
    """Per ADR-0015 amendment (2026-04-22): build_player_state must expose
    `cooldown_remaining` (single field) so the LLM can plan around blocked
    actions instead of discovering them via silent Hold() substitution.
    """
    anchors = compute_anchors(real_match_config)
    gsm = GameStateManager(real_match_config, anchors)

    ps = gsm.build_player_state("team_a_3")

    assert "cooldown_remaining" in ps
    # Initially 0 (never performed)
    assert ps["cooldown_remaining"] == 0

    # After an action at tick 5, cooldown_remaining ticks down per game tick.
    # GSM.tick is still 0 → remaining = 5 + action_cooldown_ticks(10) - 0 = 15.
    gsm.record_action_cooldown("team_a_3", 5)
    ps2 = gsm.build_player_state("team_a_3")
    assert ps2["cooldown_remaining"] == 15

    # Other players unaffected
    ps_other = gsm.build_player_state("team_a_4")
    assert ps_other["cooldown_remaining"] == 0


def test_field_dict_includes_goal_vertical_extents(real_match_config):
    """ARE Phase 7 _is_goal_line_crossed reads field['goal_top'] and
    field['goal_bottom']. GSM must populate them or shots crash with KeyError.

    Surfaced 2026-04-22 by realistic-strategy playtest — chase-ball strategy
    never shot so the gap stayed hidden across two prior playtests.
    """
    anchors = compute_anchors(real_match_config)
    gsm = GameStateManager(real_match_config, anchors)

    field = gsm.state.field
    assert "goal_top" in field, "GSM.state.field missing goal_top — ARE will KeyError on shots"
    assert "goal_bottom" in field, "GSM.state.field missing goal_bottom — ARE will KeyError on shots"

    # Sanity: goal must be vertically symmetric around field midline + non-empty.
    field_h = real_match_config.match.field_height
    midline = field_h / 2.0
    assert field["goal_bottom"] < midline < field["goal_top"]
    assert (field["goal_top"] - field["goal_bottom"]) > 0
