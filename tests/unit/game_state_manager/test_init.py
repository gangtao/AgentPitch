"""
Tests for GameState dataclass and GameStateManager initialization.

Tests all 10 acceptance criteria from Story 001:
AC-1: Initialization completes with proper initial state
AC-2: Players positioned at formation anchors
AC-3: Ball at field center with zero velocity
AC-4: Total tick computation formula
AC-5: Kickoff team determinism
AC-6: Kickoff team uses hash_01 correctly
AC-7: Player IDs are strings in ADR-0004 format
AC-8: Construction determinism (same inputs → same state)
AC-9: No _team_providers field (regression guard)
AC-10: Defensive copy of anchors (no mutation during construction)
"""

from __future__ import annotations
import pytest

from src.foundation.simulation_utils import hash_01
from src.core.game_state_manager import GameStateManager
from tests.unit.game_state_manager.conftest import (
    _create_test_config,
    _create_test_anchors,
)


# Pre-computed hash_01 values for deterministic tests (AC-6)
HASH_01_SEED_0_KICKOFF = 0.3804052388295531  # < 0.5 → team_a
HASH_01_SEED_1_KICKOFF = 0.6229347395710647  # >= 0.5 → team_b


class TestAC1InitializationCompletes:
    """Test AC-1: Initialization completes with proper initial state."""

    def test_game_state_manager_initialization_completes_without_error(self):
        """GameStateManager construction should complete without raising."""
        config = _create_test_config()
        anchors = _create_test_anchors()

        # Should not raise
        gsm = GameStateManager(config, anchors)

        # Verify basic state
        assert gsm.state.tick == 0
        assert gsm.state.phase == "PRE_MATCH"
        assert len(gsm.state.players) == 10
        assert gsm.state.score == {"team_a": 0, "team_b": 0}

    def test_game_state_manager_all_players_initialized(self):
        """All 10 players should be initialized in state."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Check that all expected player IDs are present
        expected_ids = set(anchors.keys())
        actual_ids = set(gsm.state.players.keys())
        assert actual_ids == expected_ids

        # Each player should have required fields
        for player_id, player_state in gsm.state.players.items():
            assert "team" in player_state
            assert "role" in player_state
            assert "position" in player_state
            assert "has_ball" in player_state
            assert player_state["has_ball"] is False


class TestAC2BallAtCenter:
    """Test AC-2: Ball positioned at field center with zero velocity."""

    def test_game_state_manager_ball_at_field_center(self):
        """Ball should be positioned at field center on initialization."""
        config = _create_test_config(field_width=100.0, field_height=60.0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        expected_position = (50.0, 30.0)  # width/2, height/2
        assert gsm.state.ball["position"] == expected_position

    def test_game_state_manager_ball_zero_velocity(self):
        """Ball should have zero velocity on initialization."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        assert gsm.state.ball["velocity"] == (0.0, 0.0)
        assert gsm.state.ball["carrier_id"] is None
        assert gsm.state.ball["possession"] is None


class TestAC3PlayersAtAnchors:
    """Test AC-3: Players positioned at formation anchors (AC-GSM-02)."""

    def test_game_state_manager_players_at_anchor_positions(self):
        """Each player's position should equal its formation anchor."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        for player_id, expected_anchor in anchors.items():
            player_state = gsm.build_player_state(player_id)
            assert player_state["position"] == expected_anchor

    def test_game_state_manager_players_at_field_corners(self):
        """Edge case: players at exact field corners."""
        config = _create_test_config(field_width=100.0, field_height=60.0)
        corner_anchors = {
            "team_a_0": (0.0, 0.0),      # Bottom-left corner
            "team_a_1": (100.0, 0.0),    # Bottom-right corner
            "team_a_2": (0.0, 60.0),     # Top-left corner
            "team_a_3": (100.0, 60.0),   # Top-right corner
            "team_a_4": (50.0, 30.0),    # Center
            "team_b_0": (25.0, 15.0),    # Quarter points
            "team_b_1": (75.0, 15.0),
            "team_b_2": (25.0, 45.0),
            "team_b_3": (75.0, 45.0),
            "team_b_4": (50.0, 30.0),
        }

        gsm = GameStateManager(config, corner_anchors)

        for player_id, expected_position in corner_anchors.items():
            player_state = gsm.build_player_state(player_id)
            assert player_state["position"] == expected_position


class TestAC4TotalTicksFormula:
    """Test AC-4: Total tick computation formula."""

    def test_game_state_manager_total_ticks_standard_match(self):
        """Standard 90-minute match with 10 tick/sec rate."""
        config = _create_test_config(tick_rate=10, duration_minutes=90)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        expected_total = 10 * 90 * 60  # 54000
        expected_half_end = 54000 // 2  # 27000

        assert gsm.state.total_ticks == expected_total
        assert gsm.state.half_1_end_tick == expected_half_end

    def test_game_state_manager_total_ticks_edge_case_short(self):
        """Edge case: 1-minute match with 1 tick/sec."""
        config = _create_test_config(tick_rate=1, duration_minutes=1)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        expected_total = 1 * 1 * 60  # 60
        expected_half_end = 60 // 2  # 30

        assert gsm.state.total_ticks == expected_total
        assert gsm.state.half_1_end_tick == expected_half_end

    def test_game_state_manager_total_ticks_edge_case_odd_duration(self):
        """Edge case: odd duration causing non-round half-time."""
        config = _create_test_config(tick_rate=10, duration_minutes=91)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        expected_total = 10 * 91 * 60  # 54600
        expected_half_end = 54600 // 2  # 27300

        assert gsm.state.total_ticks == expected_total
        assert gsm.state.half_1_end_tick == expected_half_end


class TestAC5KickoffTeamDeterminism:
    """Test AC-5: Kickoff team determinism."""

    def test_game_state_manager_same_seed_same_kickoff_team(self):
        """Same seed should produce identical kickoff team across instances."""
        config1 = _create_test_config(seed=42)
        config2 = _create_test_config(seed=42)
        anchors = _create_test_anchors()

        gsm1 = GameStateManager(config1, anchors)
        gsm2 = GameStateManager(config2, anchors)

        assert gsm1.state._kickoff_team == gsm2.state._kickoff_team

    def test_game_state_manager_seed_zero_valid(self):
        """Edge case: seed=0 should be valid."""
        config = _create_test_config(seed=0)
        anchors = _create_test_anchors()

        # Should not raise
        gsm = GameStateManager(config, anchors)
        assert gsm.state._kickoff_team in ["team_a", "team_b"]

    def test_game_state_manager_seed_one_deterministic(self):
        """Edge case: seed=1 should be deterministic."""
        config = _create_test_config(seed=1)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Should be consistent with hash_01 computation
        expected_team = "team_a" if HASH_01_SEED_1_KICKOFF < 0.5 else "team_b"
        assert gsm.state._kickoff_team == expected_team


class TestAC6KickoffUsesHash01:
    """Test AC-6: Kickoff team uses hash_01 correctly."""

    def test_game_state_manager_kickoff_team_follows_hash_01_rule(self):
        """_kickoff_team should follow hash_01(seed, 0, 'kickoff') < 0.5 rule."""
        # Test known seed with pinned hash_01 value
        config = _create_test_config(seed=0)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # We know hash_01(0, 0, "kickoff") = 0.3804... < 0.5
        assert gsm.state._kickoff_team == "team_a"

    def test_game_state_manager_kickoff_team_hash_01_boundary(self):
        """Test with seed that produces hash_01 >= 0.5."""
        config = _create_test_config(seed=1)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # We know hash_01(1, 0, "kickoff") = 0.6229... >= 0.5
        assert gsm.state._kickoff_team == "team_b"

    def test_game_state_manager_kickoff_uses_tick_zero(self):
        """Verify kickoff determination uses tick=0 parameter."""
        config = _create_test_config(seed=42)
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Manually compute what the result should be
        hash_value = hash_01(42, 0, "kickoff")
        expected_team = "team_a" if hash_value < 0.5 else "team_b"

        assert gsm.state._kickoff_team == expected_team


class TestAC7PlayerIDsAreStrings:
    """Test AC-7: Player IDs are strings in ADR-0004 format."""

    def test_game_state_manager_player_ids_are_strings(self):
        """All player_id keys should be strings."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        for player_id in gsm.state.players.keys():
            assert isinstance(player_id, str)

    def test_game_state_manager_player_ids_match_adr_format(self):
        """Player IDs should match ADR-0004 format: team_{a|b}_{0-4}."""
        import re

        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        adr_pattern = re.compile(r"^team_[ab]_[0-4]$")

        for player_id in gsm.state.players.keys():
            assert adr_pattern.match(player_id), f"Invalid player_id format: {player_id}"

    def test_game_state_manager_no_integer_player_ids(self):
        """Negative test: integer keys should never appear."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        for player_id in gsm.state.players.keys():
            assert not isinstance(player_id, int)


class TestAC8ConstructionDeterminism:
    """Test AC-8: Construction determinism (AC-GSM-18 partial)."""

    def test_game_state_manager_identical_construction(self):
        """Two GSMs from same inputs should have identical internal state."""
        config1 = _create_test_config(seed=42)
        config2 = _create_test_config(seed=42)  # Same config
        anchors1 = _create_test_anchors()
        anchors2 = _create_test_anchors()  # Same anchors

        gsm1 = GameStateManager(config1, anchors1)
        gsm2 = GameStateManager(config2, anchors2)

        # Check key deterministic fields
        assert gsm1.state.players == gsm2.state.players
        assert gsm1.state.ball == gsm2.state.ball
        assert gsm1.state._kickoff_team == gsm2.state._kickoff_team
        assert gsm1.state.total_ticks == gsm2.state.total_ticks
        assert gsm1.state.half_1_end_tick == gsm2.state.half_1_end_tick

    def test_game_state_manager_different_seeds_different_kickoff(self):
        """Different seeds should (usually) produce different kickoff teams."""
        config1 = _create_test_config(seed=0)  # team_a
        config2 = _create_test_config(seed=1)  # team_b
        anchors = _create_test_anchors()

        gsm1 = GameStateManager(config1, anchors)
        gsm2 = GameStateManager(config2, anchors)

        # These specific seeds have different kickoff teams
        assert gsm1.state._kickoff_team != gsm2.state._kickoff_team


class TestAC9NoTeamProvidersField:
    """Test AC-9: No _team_providers field (regression guard)."""

    def test_game_state_manager_no_team_providers_field(self):
        """GSM should not have _team_providers field."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        assert not hasattr(gsm, "_team_providers")

    def test_game_state_no_team_providers_field(self):
        """GameState should not have _team_providers field."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        assert not hasattr(gsm.state, "_team_providers")


class TestAC10DefensiveCopyOfAnchors:
    """Test AC-10: Defensive copy of anchors (no mutation during construction)."""

    def test_game_state_manager_anchors_defensive_copy(self):
        """Mutating external anchors dict should not affect GSM state."""
        config = _create_test_config()
        anchors = _create_test_anchors()

        # Store original anchor position
        original_position = anchors["team_a_0"]

        # Create GSM
        gsm = GameStateManager(config, anchors)

        # Mutate external anchors dict
        anchors["team_a_0"] = (999.0, 999.0)

        # GSM's internal state should be unchanged
        assert gsm.state._anchors["team_a_0"] == original_position
        assert gsm.state.players["team_a_0"]["position"] == original_position

    def test_game_state_manager_anchors_deep_independence(self):
        """GSM anchors should be completely independent of external dict."""
        config = _create_test_config()
        anchors = _create_test_anchors()
        gsm = GameStateManager(config, anchors)

        # Clear external dict
        original_anchors = dict(anchors)
        anchors.clear()

        # GSM should still have all anchors
        assert gsm.state._anchors == original_anchors
        assert len(gsm.state._anchors) == 10