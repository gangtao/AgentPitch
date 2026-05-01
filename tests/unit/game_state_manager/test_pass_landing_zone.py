"""
Tests for pass landing zone API (Story 006).

Tests all 8 acceptance criteria from
production/epics/game-state-manager/story-006-pass-landing-zone-api.md:

AC-1: Initial state - get_pass_landing_zone() returns None
AC-2: Set then get - round-trip works correctly
AC-3: Set then clear - setter accepts None
AC-4: Setter overwrites - subsequent set replaces
AC-5: Privacy - not in build_tick_snapshot() (top-level + nested)
AC-6: reset_to_kickoff clears landing zone (SKIP - awaiting Story 004)
AC-7: hash_01 cross-machine determinism pin (AC-GSM-19)
AC-8: No leak into build_player_state either
"""

from __future__ import annotations
from typing import Any
import pytest

from src.foundation.simulation_utils import hash_01
from src.core.game_state_manager import GameStateManager
from tests.unit.game_state_manager.conftest import (
    _create_test_config,
    _create_test_anchors,
)


def _walk_keys(d: Any) -> set[str]:
    """Recursively collect all dict keys from a nested structure (from test_snapshot.py)."""
    keys: set[str] = set()
    if isinstance(d, dict):
        for k, v in d.items():
            keys.add(str(k))
            keys.update(_walk_keys(v))
    elif isinstance(d, (list, tuple)):
        for item in d:
            keys.update(_walk_keys(item))
    return keys


def _walk_values(d: Any) -> list[Any]:
    """Recursively collect all leaf values from a nested structure."""
    values: list[Any] = []
    if isinstance(d, dict):
        for v in d.values():
            values.extend(_walk_values(v))
    elif isinstance(d, (list, tuple)):
        for item in d:
            values.extend(_walk_values(item))
    else:
        # Leaf value
        values.append(d)
    return values


class TestAC1InitialState:
    """Test AC-1: Initial state - freshly constructed GSM has get_pass_landing_zone() == None."""

    def test_initial_pass_landing_zone_is_none(self):
        """AC-1: freshly constructed GSM has no landing zone."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        assert gsm.get_pass_landing_zone() is None


class TestAC2SetThenGet:
    """Test AC-2: Set then get - round-trip works correctly."""

    def test_set_pass_landing_zone_round_trip(self):
        """AC-2: set landing zone, then get should return the same tuple."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.set_pass_landing_zone((45.5, 28.0))
        result = gsm.get_pass_landing_zone()
        assert result == (45.5, 28.0)

    def test_set_multiple_coordinates_round_trip(self):
        """AC-2: multiple different coordinates should work."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        test_positions = [(0.0, 0.0), (100.0, 60.0), (50.5, 30.25), (99.9, 0.1)]
        for pos in test_positions:
            gsm.set_pass_landing_zone(pos)
            assert gsm.get_pass_landing_zone() == pos


class TestAC3SetThenClear:
    """Test AC-3: Set then clear - setter accepts None."""

    def test_set_then_clear_with_none(self):
        """AC-3: set to position, then clear with None."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.set_pass_landing_zone((40.0, 30.0))
        assert gsm.get_pass_landing_zone() == (40.0, 30.0)

        gsm.set_pass_landing_zone(None)
        assert gsm.get_pass_landing_zone() is None

    def test_set_none_on_fresh_gsm(self):
        """AC-3: setting None on already-None state is valid."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        assert gsm.get_pass_landing_zone() is None
        gsm.set_pass_landing_zone(None)
        assert gsm.get_pass_landing_zone() is None


class TestAC4SetterOverwrites:
    """Test AC-4: Setter overwrites - subsequent set replaces."""

    def test_setter_overwrites_previous_value(self):
        """AC-4: subsequent set replaces the previous value."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.set_pass_landing_zone((40.0, 30.0))
        assert gsm.get_pass_landing_zone() == (40.0, 30.0)

        gsm.set_pass_landing_zone((10.0, 5.0))
        assert gsm.get_pass_landing_zone() == (10.0, 5.0)

    def test_multiple_overwrites(self):
        """AC-4: multiple overwrites work correctly."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        positions = [(20.0, 20.0), (50.0, 30.0), (80.0, 40.0), None, (25.5, 35.5)]
        for pos in positions:
            gsm.set_pass_landing_zone(pos)
            assert gsm.get_pass_landing_zone() == pos


class TestAC5PrivacySnapshot:
    """Test AC-5: Privacy - not in build_tick_snapshot() (top-level + nested)."""

    def test_pass_landing_zone_not_in_snapshot_keys(self):
        """AC-5: pass_landing_zone should not appear in any snapshot key."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.set_pass_landing_zone((45.5, 28.0))
        snap = gsm.build_tick_snapshot()
        all_keys = _walk_keys(snap)

        assert "pass_landing_zone" not in all_keys
        assert "_pass_landing_zone" not in all_keys

    def test_pass_landing_zone_value_not_in_snapshot_values(self):
        """AC-5: the landing zone tuple should not appear in flattened snapshot values."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        sentinel_pos = (45.5, 28.0)
        gsm.set_pass_landing_zone(sentinel_pos)
        snap = gsm.build_tick_snapshot()
        all_values = _walk_values(snap)

        assert sentinel_pos not in all_values

    def test_privacy_with_none_value(self):
        """AC-5: even with None value, no pass_landing_zone key should leak."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.set_pass_landing_zone(None)
        snap = gsm.build_tick_snapshot()
        all_keys = _walk_keys(snap)

        assert "pass_landing_zone" not in all_keys
        assert "_pass_landing_zone" not in all_keys


class TestAC6ResetClearsLandingZone:
    """Test AC-6: reset_to_kickoff clears landing zone (SKIP - awaiting Story 004)."""

    def test_reset_to_kickoff_clears_landing_zone(self):
        """AC-6: reset_to_kickoff should clear the pass landing zone."""
        # Story 004 implemented reset_to_kickoff with `self.state._pass_landing_zone = None`
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)
        gsm.set_pass_landing_zone((40.0, 30.0))
        gsm.reset_to_kickoff("team_a")  # ← method introduced by Story 004
        assert gsm.get_pass_landing_zone() is None


class TestAC7Hash01CrossMachineDeterminism:
    """Test AC-7 (AC-GSM-19): hash_01 cross-machine determinism pin."""

    def test_hash_01_cross_machine_determinism_pin(self):
        """AC-7 (AC-GSM-19): hash_01 returns 0.546607501571998 for the pinned input."""
        result = hash_01(42, 5, "team_a_0", "pass")
        assert result == 0.546607501571998  # Exact float equality — pinned in PAM Story 003 AC-4


class TestAC8NoLeakIntoPlayerState:
    """Test AC-8: No leak into build_player_state either."""

    def test_pass_landing_zone_not_in_player_state_keys(self):
        """AC-8: pass_landing_zone should not appear in any player state key."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.set_pass_landing_zone((45.5, 28.0))
        ps = gsm.build_player_state("team_a_0")
        all_keys = _walk_keys(ps)

        assert "pass_landing_zone" not in all_keys
        assert "_pass_landing_zone" not in all_keys

    def test_pass_landing_zone_value_not_in_player_state_values(self):
        """AC-8: the landing zone tuple should not appear in player state values."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        sentinel_pos = (45.5, 28.0)
        gsm.set_pass_landing_zone(sentinel_pos)
        ps = gsm.build_player_state("team_a_0")
        all_values = _walk_values(ps)

        assert sentinel_pos not in all_values

    def test_player_state_privacy_all_players(self):
        """AC-8: check privacy across all 10 players."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        gsm.set_pass_landing_zone((45.5, 28.0))

        for player_id in anchors.keys():
            ps = gsm.build_player_state(player_id)
            all_keys = _walk_keys(ps)
            assert "pass_landing_zone" not in all_keys
            assert "_pass_landing_zone" not in all_keys