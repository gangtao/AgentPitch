"""Tests for Formation & Role System anchor computation.

Tests all 12 acceptance criteria from Story 001:
AC-1: Anchor x-zones correct (Team A standard)
AC-2: Anchor x-zones (Team B mirrors)
AC-3: Lateral distribution (N=2)
AC-4: Lateral distribution (N=3)
AC-5: GK always at y=30
AC-6: formation_position matches anchor for every player
AC-7: Advisory warning for 0-player role
AC-8: Advisory warning for 4-player role
AC-9: Anchors immutable after init
AC-10: Determinism
AC-11: get_anchor pure function
AC-12: Implicit y-distribution
"""

import pytest
from src.foundation.formation_and_role_system import (
    GK_ANCHOR_X,
    DEF_ANCHOR_X,
    MID_ANCHOR_X,
    FWD_ANCHOR_X,
    FORMATION_ANCHORS,
    get_anchor,
    compute_anchors,
)
from src.foundation.config_models import MatchConfig, MatchParams, OutputConfig, TeamConfig, PlayerConfig


def _create_match_config(
    team_a_roles: list[str],
    team_b_roles: list[str],
    field_width: float = 100.0,
    field_height: float = 60.0,
) -> MatchConfig:
    """Helper to create MatchConfig with specified team roles."""
    # Create team_a players
    team_a_players = []
    for i, role in enumerate(team_a_roles):
        player = PlayerConfig(
            player_id=f"team_a_{i}",
            role=role,  # type: ignore
            speed=10,
            skill=10,
            strength=10,
            save=10 if role == "GK" else 0,
            discipline=10,
            dribbling=10,
        )
        team_a_players.append(player)

    # Create team_b players
    team_b_players = []
    for i, role in enumerate(team_b_roles):
        player = PlayerConfig(
            player_id=f"team_b_{i}",
            role=role,  # type: ignore
            speed=10,
            skill=10,
            strength=10,
            save=10 if role == "GK" else 0,
            discipline=10,
            dribbling=10,
        )
        team_b_players.append(player)

    return MatchConfig(
        match=MatchParams(
            seed=42,
            tick_rate=10,
            duration_minutes=90,
            field_width=field_width,
            field_height=field_height,
            match_id="test_match",
        ),
        output=OutputConfig(log_dir="/tmp/test"),
        team_a=TeamConfig(
            team_id="team_a",
            name="Team A",
            llm_provider="openai",
            llm_model="gpt-4o",
            api_key="test_key",
            players=team_a_players,
        ),
        team_b=TeamConfig(
            team_id="team_b",
            name="Team B",
            llm_provider="openai",
            llm_model="gpt-4o",
            api_key="test_key",
            players=team_b_players,
        ),
    )


class TestAC1AnchorXZonesTeamAStandard:
    """AC-1: Anchor x-zones correct (Team A standard)."""

    def test_formation_anchors_constants_correct(self):
        """Verify module constants have expected values."""
        assert GK_ANCHOR_X == 8.0
        assert DEF_ANCHOR_X == 25.0
        assert MID_ANCHOR_X == 50.0
        assert FWD_ANCHOR_X == 75.0

    def test_formation_anchors_table_correct(self):
        """Verify FORMATION_ANCHORS mapping is correct."""
        expected = {
            "GK": 8.0,
            "DEF": 25.0,
            "MID": 50.0,
            "FWD": 75.0,
        }
        assert FORMATION_ANCHORS == expected

    def test_anchor_x_zones_team_a_standard(self):
        """Test standard team_a config: 1 GK + 2 DEF + 2 MID."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
            field_width=100.0,
            field_height=60.0,
        )

        result = compute_anchors(config)

        # Team A anchors
        assert result["team_a_0"][0] == 8.0  # GK
        assert result["team_a_1"][0] == 25.0  # DEF
        assert result["team_a_2"][0] == 25.0  # DEF
        assert result["team_a_3"][0] == 50.0  # MID
        assert result["team_a_4"][0] == 50.0  # MID

        # Verify all values are float, not int
        for player_id, (x, y) in result.items():
            if player_id.startswith("team_a"):
                assert isinstance(x, float)
                assert isinstance(y, float)


class TestAC2AnchorXZonesTeamBMirrors:
    """AC-2: Anchor x-zones (Team B mirrors)."""

    def test_anchor_x_zones_team_b_mirrors(self):
        """Test Team B mirroring with field_width=100."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
            field_width=100.0,
        )

        result = compute_anchors(config)

        # Team B anchors (mirrored)
        assert result["team_b_0"][0] == 92.0  # GK: 100 - 8 = 92
        assert result["team_b_1"][0] == 75.0  # DEF: 100 - 25 = 75
        assert result["team_b_2"][0] == 75.0  # DEF: 100 - 25 = 75
        assert result["team_b_3"][0] == 50.0  # MID: 100 - 50 = 50 (centerline)
        assert result["team_b_4"][0] == 50.0  # MID: 100 - 50 = 50 (centerline)

    def test_anchor_x_zones_non_default_field_width(self):
        """Test Team B mirroring with non-default field_width=120."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
            field_width=120.0,
        )

        result = compute_anchors(config)

        # Team B anchors with field_width=120
        assert result["team_b_0"][0] == 112.0  # GK: 120 - 8 = 112
        assert result["team_b_1"][0] == 95.0   # DEF: 120 - 25 = 95
        assert result["team_b_3"][0] == 70.0   # MID: 120 - 50 = 70


class TestAC3LateralDistributionN2:
    """AC-3: Lateral distribution (N=2)."""

    def test_lateral_distribution_2_def(self):
        """Test 2 DEF on team_a anchor at y=20, 40."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "FWD"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "FWD"],
            field_height=60.0,
        )

        result = compute_anchors(config)

        # 2 DEF: y = 60 * (1/3, 2/3) = 20.0, 40.0
        assert result["team_a_1"][1] == pytest.approx(20.0)  # First DEF
        assert result["team_a_2"][1] == pytest.approx(40.0)  # Second DEF


class TestAC4LateralDistributionN3:
    """AC-4: Lateral distribution (N=3)."""

    def test_lateral_distribution_3_mid(self):
        """Test 3 MID on team_a anchor at y=15, 30, 45."""
        config = _create_match_config(
            team_a_roles=["GK", "MID", "MID", "MID", "FWD"],
            team_b_roles=["GK", "MID", "MID", "MID", "FWD"],
            field_height=60.0,
        )

        result = compute_anchors(config)

        # 3 MID: y = 60 * (1/4, 2/4, 3/4) = 15.0, 30.0, 45.0
        assert result["team_a_1"][1] == pytest.approx(15.0)  # First MID
        assert result["team_a_2"][1] == pytest.approx(30.0)  # Second MID
        assert result["team_a_3"][1] == pytest.approx(45.0)  # Third MID

    def test_lateral_distribution_4_players(self):
        """Test N=4 distribution: y=12, 24, 36, 48."""
        config = _create_match_config(
            team_a_roles=["GK", "FWD", "FWD", "FWD", "FWD"],
            team_b_roles=["GK", "FWD", "FWD", "FWD", "FWD"],
            field_height=60.0,
        )

        result = compute_anchors(config)

        # 4 FWD: y = 60 * (1/5, 2/5, 3/5, 4/5) = 12.0, 24.0, 36.0, 48.0
        assert result["team_a_1"][1] == pytest.approx(12.0)
        assert result["team_a_2"][1] == pytest.approx(24.0)
        assert result["team_a_3"][1] == pytest.approx(36.0)
        assert result["team_a_4"][1] == pytest.approx(48.0)

    def test_lateral_distribution_1_player(self):
        """Test N=1 distribution: y=30 (field center)."""
        config = _create_match_config(
            team_a_roles=["GK", "FWD", "DEF", "DEF", "DEF"],
            team_b_roles=["GK", "FWD", "DEF", "DEF", "DEF"],
            field_height=60.0,
        )

        result = compute_anchors(config)

        # 1 FWD: y = 60 * 1/2 = 30.0
        assert result["team_a_1"][1] == pytest.approx(30.0)


class TestAC5GKAlwaysAtY30:
    """AC-5: GK always at y=30."""

    def test_gk_always_at_field_center(self):
        """Test GK anchor_y = 30 regardless of position in player list."""
        # GK third in list
        config = _create_match_config(
            team_a_roles=["DEF", "DEF", "GK", "MID", "MID"],
            team_b_roles=["DEF", "DEF", "GK", "MID", "MID"],
            field_height=60.0,
        )

        result = compute_anchors(config)

        # GK has N=1 → y = 60 * 1/2 = 30.0
        assert result["team_a_2"][1] == pytest.approx(30.0)  # GK at index 2

    def test_gk_last_player(self):
        """Test GK as last player in config order."""
        config = _create_match_config(
            team_a_roles=["DEF", "MID", "MID", "FWD", "GK"],
            team_b_roles=["DEF", "MID", "MID", "FWD", "GK"],
            field_height=60.0,
        )

        result = compute_anchors(config)

        # GK at index 4
        assert result["team_a_4"][1] == pytest.approx(30.0)

    def test_gk_non_default_field_height(self):
        """Test GK with non-default field_height=80."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
            field_height=80.0,
        )

        result = compute_anchors(config)

        # GK: y = 80 * 1/2 = 40.0
        assert result["team_a_0"][1] == pytest.approx(40.0)


class TestAC6FormationPositionMatchesAnchor:
    """AC-6: formation_position matches anchor for every player."""

    def test_returned_dict_has_all_10_players(self):
        """Test returned dict has exactly 10 keys for 5v5 config."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
        )

        result = compute_anchors(config)

        # Should have exactly 10 players
        assert len(result) == 10

        # All team_a players
        for i in range(5):
            assert f"team_a_{i}" in result

        # All team_b players
        for i in range(5):
            assert f"team_b_{i}" in result

        # Every value is a tuple of floats
        for player_id, anchor in result.items():
            assert isinstance(anchor, tuple)
            assert len(anchor) == 2
            assert isinstance(anchor[0], float)
            assert isinstance(anchor[1], float)

    def test_anchor_x_values_in_expected_set(self):
        """Test all anchor_x values are in expected set."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
            field_width=100.0,
        )

        result = compute_anchors(config)

        expected_x_values = {8.0, 25.0, 50.0, 75.0, 92.0}  # team_a + team_b values
        actual_x_values = {anchor[0] for anchor in result.values()}
        assert actual_x_values == expected_x_values


class TestAC7AdvisoryWarning0PlayerRole:
    """AC-7: Advisory warning for 0-player role."""

    def test_warning_0_def_0_mid(self, caplog):
        """Test 0 DEF + 0 MID logs warnings, no exception."""
        config = _create_match_config(
            team_a_roles=["GK", "FWD", "FWD", "FWD", "FWD"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
        )

        result = compute_anchors(config)

        # Function returns successfully
        assert len(result) == 10

        # Check log warnings contain expected messages
        log_messages = [record.message for record in caplog.records]
        assert any("team_a has 0 DEF" in msg for msg in log_messages)
        assert any("team_a has 0 MID" in msg for msg in log_messages)

        # FWD anchors are computed (4 FWD at y=12, 24, 36, 48)
        assert result["team_a_1"][1] == pytest.approx(12.0)  # First FWD
        assert result["team_a_2"][1] == pytest.approx(24.0)  # Second FWD
        assert result["team_a_3"][1] == pytest.approx(36.0)  # Third FWD
        assert result["team_a_4"][1] == pytest.approx(48.0)  # Fourth FWD


class TestAC8AdvisoryWarning4PlayerRole:
    """AC-8: Advisory warning for 4-player role."""

    def test_warning_4_mid(self, caplog):
        """Test 4 MID logs warning, function returns successfully."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "MID", "MID", "MID", "MID"],
        )

        result = compute_anchors(config)

        # Function returns successfully
        assert len(result) == 10

        # Check log warning
        log_messages = [record.message for record in caplog.records]
        assert any("team_b has 4 MID" in msg for msg in log_messages)

        # 4 MID anchors at y=12, 24, 36, 48
        assert result["team_b_1"][1] == pytest.approx(12.0)
        assert result["team_b_2"][1] == pytest.approx(24.0)
        assert result["team_b_3"][1] == pytest.approx(36.0)
        assert result["team_b_4"][1] == pytest.approx(48.0)

    def test_warning_4_def_and_4_fwd(self, caplog):
        """Test warnings for both 4 DEF and 4 FWD."""
        # Create configs that trigger both warnings
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "DEF", "DEF"],
            team_b_roles=["GK", "FWD", "FWD", "FWD", "FWD"],
        )

        result = compute_anchors(config)

        # Function returns successfully
        assert len(result) == 10

        # Check both warnings
        log_messages = [record.message for record in caplog.records]
        assert any("team_a has 4 DEF" in msg for msg in log_messages)
        assert any("team_b has 4 FWD" in msg for msg in log_messages)

    def test_no_warning_3_players(self, caplog):
        """Test 3 players of same role does NOT warn."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "DEF", "MID"],
            team_b_roles=["GK", "MID", "MID", "MID", "FWD"],
        )

        compute_anchors(config)

        # Should have no warnings for 3-player roles
        log_messages = [record.message for record in caplog.records]
        assert not any("has 3" in msg for msg in log_messages)


class TestAC9AnchorsImmutableAfterInit:
    """AC-9: Anchors immutable after init."""

    def test_returned_dict_is_fresh_copy(self):
        """Test returned dict is a new copy each call."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
        )

        result1 = compute_anchors(config)
        result2 = compute_anchors(config)

        # Results are equal but not the same object
        assert result1 == result2
        assert result1 is not result2

    def test_tuple_values_are_immutable(self):
        """Test tuple values cannot be mutated."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
        )

        result = compute_anchors(config)

        # Tuples are inherently immutable
        with pytest.raises(TypeError):
            result["team_a_0"][0] = 99.0  # type: ignore

    def test_dict_mutation_does_not_affect_new_calls(self):
        """Test modifying returned dict does not affect future calls."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
        )

        result1 = compute_anchors(config)
        original_anchor = result1["team_a_0"]

        # Modify the dict (this is allowed - the dict itself is mutable)
        result1["team_a_0"] = (0.0, 0.0)

        # New call should return original values
        result2 = compute_anchors(config)
        assert result2["team_a_0"] == original_anchor


class TestAC10Determinism:
    """AC-10: Determinism."""

    def test_two_runs_identical_results(self):
        """Test two runs with same config produce identical results."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
        )

        result1 = compute_anchors(config)
        result2 = compute_anchors(config)

        assert result1 == result2

    def test_different_config_instances_same_data(self):
        """Test different MatchConfig instances with same data produce identical results."""
        # Create two separate config instances with identical data
        config1 = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
        )
        config2 = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "MID", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "MID", "MID"],
        )

        result1 = compute_anchors(config1)
        result2 = compute_anchors(config2)

        assert result1 == result2


class TestAC11GetAnchorPureFunction:
    """AC-11: get_anchor pure function."""

    def test_get_anchor_team_a(self):
        """Test get_anchor for Team A returns base values."""
        assert get_anchor("GK", "team_a", 100.0) == 8.0
        assert get_anchor("DEF", "team_a", 100.0) == 25.0
        assert get_anchor("MID", "team_a", 100.0) == 50.0
        assert get_anchor("FWD", "team_a", 100.0) == 75.0

    def test_get_anchor_team_b_mirrors(self):
        """Test get_anchor for Team B mirrors correctly."""
        assert get_anchor("GK", "team_b", 100.0) == 92.0   # 100 - 8
        assert get_anchor("DEF", "team_b", 100.0) == 75.0  # 100 - 25
        assert get_anchor("MID", "team_b", 100.0) == 50.0  # 100 - 50 (centerline)
        assert get_anchor("FWD", "team_b", 100.0) == 25.0  # 100 - 75

    def test_get_anchor_anchor_x_does_not_scale_with_field_width(self):
        """Test anchor x does NOT scale with field_width (per edge case 10)."""
        # Different field widths should not affect the base anchor values
        assert get_anchor("GK", "team_a", 120.0) == 8.0   # Still 8, not scaled
        assert get_anchor("DEF", "team_a", 80.0) == 25.0  # Still 25, not scaled

        # But Team B mirroring does use field_width
        assert get_anchor("GK", "team_b", 120.0) == 112.0  # 120 - 8
        assert get_anchor("DEF", "team_b", 80.0) == 55.0   # 80 - 25


class TestAC12ImplicitYDistribution:
    """AC-12: Implicit y-distribution."""

    def test_no_role_labels_needed(self):
        """Test 3-DEF roster has no _L/_R labels, just config order."""
        config = _create_match_config(
            team_a_roles=["GK", "DEF", "DEF", "DEF", "MID"],
            team_b_roles=["GK", "DEF", "DEF", "DEF", "MID"],
            field_height=60.0,
        )

        result = compute_anchors(config)

        # All three DEF players have role="DEF" in config
        team_a = config.team_a
        def_players = [p for p in team_a.players if p.role == "DEF"]
        assert len(def_players) == 3
        assert all(p.role == "DEF" for p in def_players)  # No _L/_R variants

        # Y-distribution: first config DEF gets lowest y, last gets highest
        assert result["team_a_1"][1] == pytest.approx(15.0)  # First DEF (lowest y)
        assert result["team_a_2"][1] == pytest.approx(30.0)  # Second DEF (middle y)
        assert result["team_a_3"][1] == pytest.approx(45.0)  # Third DEF (highest y)