"""
Test suite for game_state_schema module.

Tests all acceptance criteria for the GameStateDict TypedDict structure
and validate_game_state() function.
"""

import copy
import pytest

from src.foundation.game_state_schema import (
    GameStateDict,
    BallDict,
    PlayerRecordDict,
    FieldDict,
    ScoreDict,
    Role,
    TeamId,
    validate_game_state,
)


def _valid_game_state() -> dict:
    """Factory for a valid game_state dict fixture."""
    return {
        "tick": 1200,
        "match_time_seconds": 120.5,
        "half": 1,
        "ticks_remaining": 2400,
        "score": {"team_a": 1, "team_b": 0},
        "ball": {
            "position": (50.0, 25.0),
            "possession": "team_a",
            "carrier_id": "team_a_2",
        },
        "players": {
            "team_a_0": {"team": "team_a", "role": "GK", "position": (5.0, 25.0), "has_ball": False},
            "team_a_1": {"team": "team_a", "role": "DEF", "position": (20.0, 15.0), "has_ball": False},
            "team_a_2": {"team": "team_a", "role": "MID", "position": (45.0, 25.0), "has_ball": True},
            "team_a_3": {"team": "team_a", "role": "MID", "position": (40.0, 35.0), "has_ball": False},
            "team_a_4": {"team": "team_a", "role": "FWD", "position": (65.0, 25.0), "has_ball": False},
            "team_b_0": {"team": "team_b", "role": "GK", "position": (95.0, 25.0), "has_ball": False},
            "team_b_1": {"team": "team_b", "role": "DEF", "position": (80.0, 15.0), "has_ball": False},
            "team_b_2": {"team": "team_b", "role": "DEF", "position": (80.0, 35.0), "has_ball": False},
            "team_b_3": {"team": "team_b", "role": "MID", "position": (60.0, 25.0), "has_ball": False},
            "team_b_4": {"team": "team_b", "role": "FWD", "position": (70.0, 25.0), "has_ball": False},
        },
        "field": {
            "width": 100.0,
            "height": 50.0,
            "team_a_goal_x": 0.0,
            "team_b_goal_x": 100.0,
            "goal_top": 20.0,
            "goal_bottom": 30.0,
        },
        "my_team": "team_a",
        "my_player_id": "team_a_2",
    }


class TestGameStateValidation:
    """Test cases for validate_game_state() function."""

    def test_ac1_valid_snapshot_passes(self):
        """AC-1: A fully-populated dict validates without exception."""
        snapshot = _valid_game_state()
        validate_game_state(snapshot)  # Should not raise

    def test_ac1_accepts_variable_player_count(self):
        """AC-1 edge case: Validator accepts any positive player count, not hardcoded 10."""
        snapshot = _valid_game_state()
        # Remove some players to test variable count
        del snapshot["players"]["team_a_3"]
        del snapshot["players"]["team_a_4"]
        del snapshot["players"]["team_b_3"]
        del snapshot["players"]["team_b_4"]
        validate_game_state(snapshot)  # Should not raise

    def test_ac2_missing_top_level_key_rejected(self):
        """AC-2: Removing required top-level key raises ValueError."""
        snapshot = _valid_game_state()
        del snapshot["tick"]

        with pytest.raises(ValueError, match="missing.*tick"):
            validate_game_state(snapshot)

    def test_ac2_missing_various_keys(self):
        """AC-2 edge cases: Test missing various required keys."""
        required_keys = ["my_player_id", "score", "ball", "players", "field", "my_team"]

        for key in required_keys:
            snapshot = _valid_game_state()
            del snapshot[key]

            with pytest.raises(ValueError, match=f"missing.*{key}"):
                validate_game_state(snapshot)

    def test_ac3_extra_top_level_key_rejected(self):
        """AC-3: Adding unexpected top-level key raises ValueError."""
        snapshot = _valid_game_state()
        snapshot["_pass_landing_zone"] = (50.0, 25.0)

        with pytest.raises(ValueError, match="unexpected.*_pass_landing_zone"):
            validate_game_state(snapshot)

    def test_ac4_tick_must_be_int_not_bool(self):
        """AC-4: tick=True is rejected (bool is int subclass in Python)."""
        snapshot = _valid_game_state()
        snapshot["tick"] = True

        with pytest.raises(ValueError, match="tick.*expected int"):
            validate_game_state(snapshot)

    def test_ac4_tick_accepts_valid_ints(self):
        """AC-4 edge cases: Valid int values for tick."""
        snapshot = _valid_game_state()

        # These should pass
        for valid_tick in [0, -1, 1, 999]:
            snapshot["tick"] = valid_tick
            validate_game_state(snapshot)

    def test_ac4_tick_rejects_float(self):
        """AC-4 edge case: tick=1.0 is rejected."""
        snapshot = _valid_game_state()
        snapshot["tick"] = 1.0

        with pytest.raises(ValueError, match="tick.*expected int"):
            validate_game_state(snapshot)

    def test_ac5_my_player_id_must_be_str(self):
        """AC-5: my_player_id=2 is rejected (must be str per ADR-0004)."""
        snapshot = _valid_game_state()
        snapshot["my_player_id"] = 2

        with pytest.raises(ValueError, match="my_player_id.*expected str.*ADR-0004"):
            validate_game_state(snapshot)

    def test_ac5_my_player_id_accepts_valid_str(self):
        """AC-5 edge case: Valid str values for my_player_id."""
        snapshot = _valid_game_state()
        snapshot["my_player_id"] = "team_a_2"
        validate_game_state(snapshot)

    def test_ac5_my_player_id_rejects_none(self):
        """AC-5 edge case: my_player_id=None is rejected."""
        snapshot = _valid_game_state()
        snapshot["my_player_id"] = None

        with pytest.raises(ValueError, match="my_player_id.*expected str"):
            validate_game_state(snapshot)

    def test_ac6_carrier_id_accepts_str_and_none(self):
        """AC-6: ball.carrier_id accepts both valid str and None."""
        snapshot = _valid_game_state()

        # Test valid str
        snapshot["ball"]["carrier_id"] = "team_a_3"
        validate_game_state(snapshot)

        # Test None
        snapshot["ball"]["carrier_id"] = None
        validate_game_state(snapshot)

    def test_ac6_carrier_id_rejects_int(self):
        """AC-6: ball.carrier_id=3 (int) is rejected."""
        snapshot = _valid_game_state()
        snapshot["ball"]["carrier_id"] = 3

        with pytest.raises(ValueError, match="carrier_id.*expected str or None.*ADR-0004"):
            validate_game_state(snapshot)

    def test_ac6_carrier_id_accepts_empty_str(self):
        """AC-6 edge case: Empty string accepts structurally."""
        snapshot = _valid_game_state()
        snapshot["ball"]["carrier_id"] = ""
        validate_game_state(snapshot)  # Structural check only, semantic is GSM's job

    def test_ac7_ball_possession_enum_values(self):
        """AC-7: ball.possession accepts only team_a/team_b/None."""
        snapshot = _valid_game_state()

        # Valid values
        for valid_possession in ["team_a", "team_b", None]:
            snapshot["ball"]["possession"] = valid_possession
            validate_game_state(snapshot)

    def test_ac7_ball_possession_rejects_invalid(self):
        """AC-7: ball.possession rejects invalid strings."""
        snapshot = _valid_game_state()
        snapshot["ball"]["possession"] = "team_c"

        with pytest.raises(ValueError, match="possession.*expected one of.*team_a.*team_b"):
            validate_game_state(snapshot)

    def test_ac8_player_id_keys_are_str(self):
        """AC-8: Non-string player_id keys are rejected."""
        snapshot = _valid_game_state()

        # Add numeric key (wrong)
        player_record = snapshot["players"]["team_a_0"]
        del snapshot["players"]["team_a_0"]
        snapshot["players"][3] = player_record

        with pytest.raises(ValueError, match="player_id key.*not str.*ADR-0004"):
            validate_game_state(snapshot)

    def test_ac8_player_id_format_validation(self):
        """AC-8 edge case: Malformed player_id format rejected."""
        snapshot = _valid_game_state()

        # Wrong format
        player_record = snapshot["players"]["team_a_0"]
        del snapshot["players"]["team_a_0"]
        snapshot["players"]["player_0"] = player_record

        with pytest.raises(ValueError, match="invalid team in player_id.*player_0"):
            validate_game_state(snapshot)

    def test_ac8_player_id_requires_numeric_index(self):
        """AC-8 edge case: Non-numeric index rejected."""
        snapshot = _valid_game_state()

        player_record = snapshot["players"]["team_a_0"]
        del snapshot["players"]["team_a_0"]
        snapshot["players"]["team_a_abc"] = player_record

        with pytest.raises(ValueError, match="non-numeric index in player_id.*team_a_abc"):
            validate_game_state(snapshot)

    def test_ac9_missing_player_field_rejected(self):
        """AC-9: Missing player record field rejected."""
        snapshot = _valid_game_state()
        del snapshot["players"]["team_a_0"]["has_ball"]

        with pytest.raises(ValueError, match="players\\[team_a_0\\].*missing.*has_ball"):
            validate_game_state(snapshot)

    def test_ac9_extra_player_field_rejected(self):
        """AC-9 edge case: Extra player field rejected."""
        snapshot = _valid_game_state()
        snapshot["players"]["team_a_0"]["speed"] = 12  # This belongs in player_state

        with pytest.raises(ValueError, match="players\\[team_a_0\\].*unexpected.*speed"):
            validate_game_state(snapshot)

    def test_ac10_role_enum_values(self):
        """AC-10: Valid roles accepted."""
        snapshot = _valid_game_state()

        # Test all valid roles
        valid_roles = ["GK", "DEF", "MID", "FWD"]
        for i, role in enumerate(valid_roles):
            snapshot["players"][f"team_a_{i}"]["role"] = role
            validate_game_state(snapshot)

    def test_ac10_role_rejects_invalid(self):
        """AC-10: Invalid role rejected."""
        snapshot = _valid_game_state()
        snapshot["players"]["team_a_0"]["role"] = "STRIKER"

        with pytest.raises(ValueError, match="role.*expected one of.*DEF.*FWD.*GK.*MID"):
            validate_game_state(snapshot)

    def test_ac10_role_rejects_lowercase(self):
        """AC-10 edge case: Lowercase roles rejected."""
        snapshot = _valid_game_state()
        snapshot["players"]["team_a_0"]["role"] = "gk"

        with pytest.raises(ValueError, match="role.*expected one of"):
            validate_game_state(snapshot)

    def test_ac11_ball_substructure_missing_key(self):
        """AC-11: Missing ball substructure key rejected."""
        snapshot = _valid_game_state()
        del snapshot["ball"]["position"]

        with pytest.raises(ValueError, match="ball.*missing.*position"):
            validate_game_state(snapshot)

    def test_ac11_ball_substructure_extra_key(self):
        """AC-11: Extra ball substructure key rejected."""
        snapshot = _valid_game_state()
        snapshot["ball"]["velocity"] = (1.0, 0.5)

        with pytest.raises(ValueError, match="ball.*unexpected.*velocity"):
            validate_game_state(snapshot)

    def test_ac11_field_substructure_missing_key(self):
        """AC-11: Missing field substructure key rejected."""
        snapshot = _valid_game_state()
        del snapshot["field"]["goal_top"]

        with pytest.raises(ValueError, match="field.*missing.*goal_top"):
            validate_game_state(snapshot)

    def test_ac11_score_substructure_extra_key(self):
        """AC-11: Extra score substructure key rejected."""
        snapshot = _valid_game_state()
        snapshot["score"]["team_c"] = 2

        with pytest.raises(ValueError, match="score.*unexpected.*team_c"):
            validate_game_state(snapshot)

    def test_ac12_deep_copyability(self):
        """AC-12: game_state survives copy.deepcopy() without loss."""
        snapshot = _valid_game_state()

        # Deep copy should work
        deep_copy = copy.deepcopy(snapshot)

        # Copy should validate
        validate_game_state(deep_copy)

        # Should be structurally equal
        assert deep_copy == snapshot

        # But not the same object
        assert deep_copy is not snapshot
        assert deep_copy["players"] is not snapshot["players"]

        # Mutations should not cross-affect
        deep_copy["players"]["team_a_0"]["position"] = (99.0, 99.0)
        assert snapshot["players"]["team_a_0"]["position"] == (5.0, 25.0)

    def test_ac13_typeddict_imports(self):
        """AC-13: All TypedDict classes are importable."""
        # If we got here, imports worked in the module header
        # Test that they're actually usable as type hints
        assert GameStateDict is not None
        assert BallDict is not None
        assert PlayerRecordDict is not None
        assert FieldDict is not None
        assert ScoreDict is not None
        assert Role is not None
        assert TeamId is not None


class TestValidationEdgeCases:
    """Additional edge cases and type validation tests."""

    def test_non_dict_input_rejected(self):
        """Root input must be a dict."""
        with pytest.raises(ValueError, match="expected dict, got"):
            validate_game_state("not a dict")

    def test_bool_exclusion_for_numeric_fields(self):
        """Bool values rejected for all numeric fields (AC-4 pattern)."""
        snapshot = _valid_game_state()

        # Test all int fields
        int_fields = ["tick", "half", "ticks_remaining"]
        for field in int_fields:
            snapshot = _valid_game_state()
            snapshot[field] = True
            with pytest.raises(ValueError, match=f"{field}.*expected int"):
                validate_game_state(snapshot)

        # Test score fields
        snapshot = _valid_game_state()
        snapshot["score"]["team_a"] = False
        with pytest.raises(ValueError, match="score.team_a.*expected int"):
            validate_game_state(snapshot)

    def test_position_tuple_validation(self):
        """Position fields must be 2-tuples of numbers."""
        snapshot = _valid_game_state()

        # Test ball position
        snapshot["ball"]["position"] = [50.0, 25.0]  # List instead of tuple
        with pytest.raises(ValueError, match="ball.position.*expected 2-tuple"):
            validate_game_state(snapshot)

        # Test wrong length
        snapshot = _valid_game_state()
        snapshot["ball"]["position"] = (50.0, 25.0, 0.0)
        with pytest.raises(ValueError, match="ball.position.*expected 2-tuple"):
            validate_game_state(snapshot)

        # Test non-numeric content
        snapshot = _valid_game_state()
        snapshot["ball"]["position"] = ("x", "y")
        with pytest.raises(ValueError, match="ball.position.*expected tuple of float"):
            validate_game_state(snapshot)

    def test_my_team_validation(self):
        """my_team field must be valid TeamId."""
        snapshot = _valid_game_state()
        snapshot["my_team"] = "team_c"

        with pytest.raises(ValueError, match="my_team.*expected one of.*team_a.*team_b"):
            validate_game_state(snapshot)

    def test_substructure_type_validation(self):
        """Substructures must be dicts."""
        snapshot = _valid_game_state()

        # Test each substructure
        substructures = ["score", "ball", "field"]
        for sub in substructures:
            snapshot = _valid_game_state()
            snapshot[sub] = "not a dict"
            with pytest.raises(ValueError, match=f"{sub}.*expected dict"):
                validate_game_state(snapshot)

    def test_players_dict_type_validation(self):
        """Players must be a dict."""
        snapshot = _valid_game_state()
        snapshot["players"] = []

        with pytest.raises(ValueError, match="players.*expected dict"):
            validate_game_state(snapshot)

    def test_player_record_type_validation(self):
        """Each player record must be a dict."""
        snapshot = _valid_game_state()
        snapshot["players"]["team_a_0"] = "not a dict"

        with pytest.raises(ValueError, match="players\\[team_a_0\\].*expected dict"):
            validate_game_state(snapshot)