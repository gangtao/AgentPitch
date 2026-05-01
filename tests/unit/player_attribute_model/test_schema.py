"""
Tests for PlayerAttribute Pydantic model schema validation.

Tests all 7 acceptance criteria from Story 001:
AC-1: Attribute immutability (frozen model)
AC-2: Role enum / Literal completeness (GK, DEF, MID, FWD only)
AC-3: Range enforcement — upper bound (ge=1, le=20 fields)
AC-4: Range enforcement — lower bound, plus save=0 on non-GK
AC-5: GK-only save cross-field validator
AC-6: Schema field count (exactly 9 fields)
AC-7: Float rejection — strict integer mode
"""

import pytest
from pydantic import ValidationError

from src.foundation.player_attribute import PlayerAttribute


class TestAC1Immutability:
    """Test AC-1: Immutability (frozen model)."""

    def test_player_attribute_role_modification_blocked(self):
        """Modifying role after creation should be blocked."""
        player = PlayerAttribute(
            player_id="team_a_0",
            team="team_a",
            role="GK",
            speed=10, skill=10, strength=10, save=10,
            discipline=10, dribbling=10
        )

        with pytest.raises(ValidationError):
            player.role = "DEF"

    def test_player_attribute_player_id_modification_blocked(self):
        """Modifying player_id after creation should be blocked."""
        player = PlayerAttribute(
            player_id="team_a_0",
            team="team_a",
            role="GK",
            speed=10, skill=10, strength=10, save=10,
            discipline=10, dribbling=10
        )

        with pytest.raises(ValidationError):
            player.player_id = "team_b_1"

    def test_player_attribute_save_modification_blocked(self):
        """Modifying save after creation should be blocked."""
        player = PlayerAttribute(
            player_id="team_a_0",
            team="team_a",
            role="GK",
            speed=10, skill=10, strength=10, save=10,
            discipline=10, dribbling=10
        )

        with pytest.raises(ValidationError):
            player.save = 15

    def test_player_attribute_new_attribute_assignment_blocked(self):
        """Adding new attributes should be blocked."""
        player = PlayerAttribute(
            player_id="team_a_0",
            team="team_a",
            role="GK",
            speed=10, skill=10, strength=10, save=10,
            discipline=10, dribbling=10
        )

        with pytest.raises(ValidationError):
            player.new_field = "value"


class TestAC2RoleValidation:
    """Test AC-2: Valid role enum values."""

    @pytest.mark.parametrize("role", ["GK", "DEF", "MID", "FWD"])
    def test_player_attribute_valid_roles_accepted(self, role):
        """Valid role values should be accepted."""
        player = PlayerAttribute(
            player_id="team_a_0",
            team="team_a",
            role=role,
            speed=10, skill=10, strength=10, save=0 if role != "GK" else 10,
            discipline=10, dribbling=10
        )
        assert player.role == role

    def test_player_attribute_empty_string_role_rejected(self):
        """Empty string role should be rejected."""
        with pytest.raises(ValidationError):
            PlayerAttribute(
                player_id="team_a_0",
                team="team_a",
                role="",
                speed=10, skill=10, strength=10, save=0,
                discipline=10, dribbling=10
            )

    def test_player_attribute_lowercase_role_rejected(self):
        """Lowercase role values should be rejected."""
        with pytest.raises(ValidationError):
            PlayerAttribute(
                player_id="team_a_0",
                team="team_a",
                role="gk",
                speed=10, skill=10, strength=10, save=0,
                discipline=10, dribbling=10
            )

    def test_player_attribute_invalid_role_rejected(self):
        """Invalid role values should be rejected."""
        with pytest.raises(ValidationError):
            PlayerAttribute(
                player_id="team_a_0",
                team="team_a",
                role="STRIKER",
                speed=10, skill=10, strength=10, save=0,
                discipline=10, dribbling=10
            )

    def test_player_attribute_numeric_role_rejected(self):
        """Numeric role values should be rejected."""
        with pytest.raises(ValidationError):
            PlayerAttribute(
                player_id="team_a_0",
                team="team_a",
                role=0,
                speed=10, skill=10, strength=10, save=0,
                discipline=10, dribbling=10
            )


def _valid_kwargs(**overrides) -> dict:
    """Return a dict of valid PlayerAttribute kwargs, optionally overridden."""
    base = {
        "player_id": "team_a_0",
        "team": "team_a",
        "role": "DEF",
        "speed": 10, "skill": 10, "strength": 10,
        "save": 0,
        "discipline": 10, "dribbling": 10,
    }
    base.update(overrides)
    return base


# Fields with ge=1, le=20 — save has its own range (ge=0) tested under AC-4.
_GE1_LE20_FIELDS = ["speed", "skill", "strength", "discipline", "dribbling"]


class TestAC3RangeUpperBound:
    """Test AC-3: Range enforcement — upper bound (ge=1, le=20 fields)."""

    @pytest.mark.parametrize("attr_name", _GE1_LE20_FIELDS)
    def test_player_attribute_value_at_upper_bound_accepted(self, attr_name):
        """Value=20 should be accepted (boundary, inclusive)."""
        player = PlayerAttribute(**_valid_kwargs(**{attr_name: 20}))
        assert getattr(player, attr_name) == 20

    @pytest.mark.parametrize("attr_name", _GE1_LE20_FIELDS)
    def test_player_attribute_value_above_upper_bound_rejected(self, attr_name):
        """Value=21 should be rejected."""
        with pytest.raises(ValidationError):
            PlayerAttribute(**_valid_kwargs(**{attr_name: 21}))

    @pytest.mark.parametrize("attr_name", _GE1_LE20_FIELDS)
    def test_player_attribute_value_far_above_upper_bound_rejected(self, attr_name):
        """Value=99 should be rejected."""
        with pytest.raises(ValidationError):
            PlayerAttribute(**_valid_kwargs(**{attr_name: 99}))

    @pytest.mark.parametrize("attr_name", _GE1_LE20_FIELDS)
    def test_player_attribute_negative_value_rejected(self, attr_name):
        """Value=-1 should be rejected for ge=1 fields."""
        with pytest.raises(ValidationError):
            PlayerAttribute(**_valid_kwargs(**{attr_name: -1}))


class TestAC4RangeLowerBound:
    """Test AC-4: Range enforcement — lower bound, plus save=0 on non-GK."""

    @pytest.mark.parametrize("attr_name", _GE1_LE20_FIELDS)
    def test_player_attribute_value_at_lower_bound_accepted(self, attr_name):
        """Value=1 should be accepted for ge=1 fields (boundary, inclusive)."""
        player = PlayerAttribute(**_valid_kwargs(**{attr_name: 1}))
        assert getattr(player, attr_name) == 1

    @pytest.mark.parametrize("attr_name", _GE1_LE20_FIELDS)
    def test_player_attribute_value_below_lower_bound_rejected(self, attr_name):
        """Value=0 should be rejected for ge=1 fields."""
        with pytest.raises(ValidationError):
            PlayerAttribute(**_valid_kwargs(**{attr_name: 0}))

    # save has its own bound: ge=0. The default-injected value for
    # non-GK players is 0, so it must accept on DEF/MID/FWD.
    @pytest.mark.parametrize("role", ["DEF", "MID", "FWD"])
    def test_player_attribute_save_zero_accepted_on_non_gk(self, role):
        """save=0 must be accepted on non-GK roles (default value)."""
        player = PlayerAttribute(**_valid_kwargs(role=role, save=0))
        assert player.save == 0

    def test_player_attribute_save_zero_accepted_on_gk(self):
        """save=0 is also valid on GK (boundary)."""
        player = PlayerAttribute(**_valid_kwargs(role="GK", save=0))
        assert player.save == 0

    def test_player_attribute_save_negative_rejected(self):
        """save=-1 should be rejected (ge=0)."""
        with pytest.raises(ValidationError):
            PlayerAttribute(**_valid_kwargs(role="GK", save=-1))

    def test_player_attribute_save_above_twenty_rejected(self):
        """save=21 should be rejected (le=20)."""
        with pytest.raises(ValidationError):
            PlayerAttribute(**_valid_kwargs(role="GK", save=21))


class TestAC5GKOnlySaveReachValidation:
    """Test AC-5: GK-only save validation."""

    def test_player_attribute_def_save_positive_rejected(self):
        """DEF with save > 0 should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerAttribute(
                player_id="team_a_1",
                team="team_a",
                role="DEF",
                speed=10, skill=10, strength=10, save=5,
                discipline=10, dribbling=10
            )

        error_msg = str(exc_info.value)
        assert "save is GK-only" in error_msg

    def test_player_attribute_mid_save_positive_rejected(self):
        """MID with save > 0 should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerAttribute(
                player_id="team_a_2",
                team="team_a",
                role="MID",
                speed=10, skill=10, strength=10, save=10,
                discipline=10, dribbling=10
            )

        error_msg = str(exc_info.value)
        assert "save is GK-only" in error_msg

    def test_player_attribute_fwd_save_positive_rejected(self):
        """FWD with save > 0 should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerAttribute(
                player_id="team_a_3",
                team="team_a",
                role="FWD",
                speed=10, skill=10, strength=10, save=1,
                discipline=10, dribbling=10
            )

        error_msg = str(exc_info.value)
        assert "save is GK-only" in error_msg

    def test_player_attribute_gk_save_positive_accepted(self):
        """GK with save > 0 should be accepted."""
        player = PlayerAttribute(
            player_id="team_a_0",
            team="team_a",
            role="GK",
            speed=10, skill=10, strength=10, save=15,
            discipline=10, dribbling=10
        )
        assert player.save == 15


class TestAC6FieldCountValidation:
    """Test AC-6: Field count validation."""

    def test_player_attribute_model_has_nine_fields(self):
        """PlayerAttribute model should have exactly 9 fields."""
        assert len(PlayerAttribute.model_fields) == 9

        expected_fields = {
            "player_id", "team", "role", "speed", "skill",
            "strength", "save", "discipline", "dribbling"
        }
        actual_fields = set(PlayerAttribute.model_fields.keys())
        assert actual_fields == expected_fields


class TestAC7FloatRejection:
    """Test AC-7: Strict validation (reject floats)."""

    @pytest.mark.parametrize("attr_name", [
        "speed", "skill", "strength", "save", "discipline", "dribbling"
    ])
    def test_player_attribute_float_values_rejected(self, attr_name):
        """Float values should be rejected for integer fields."""
        kwargs = {
            "player_id": "team_a_0",
            "team": "team_a",
            "role": "GK" if attr_name == "save" else "DEF",
            "speed": 10, "skill": 10, "strength": 10,
            "save": 10 if attr_name == "save" else 0,
            "discipline": 10, "dribbling": 10
        }
        kwargs[attr_name] = 10.5

        with pytest.raises(ValidationError):
            PlayerAttribute(**kwargs)

    def test_player_attribute_string_numbers_rejected(self):
        """String representations of numbers should be rejected."""
        with pytest.raises(ValidationError):
            PlayerAttribute(
                player_id="team_a_0",
                team="team_a",
                role="DEF",
                speed="10",  # String instead of int
                skill=10, strength=10, save=0,
                discipline=10, dribbling=10
            )

    def test_player_attribute_string_player_id_accepted(self):
        """String player_id should be accepted (not strict for this field)."""
        player = PlayerAttribute(
            player_id="team_a_0",
            team="team_a",
            role="DEF",
            speed=10, skill=10, strength=10, save=0,
            discipline=10, dribbling=10
        )
        assert player.player_id == "team_a_0"

    def test_player_attribute_empty_string_player_id_rejected(self):
        """Empty string player_id should be rejected."""
        with pytest.raises(ValidationError):
            PlayerAttribute(
                player_id="",
                team="team_a",
                role="DEF",
                speed=10, skill=10, strength=10, save=0,
                discipline=10, dribbling=10
            )