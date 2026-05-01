"""Tests for Configuration System preprocessor module.

Tests all 12 acceptance criteria from Story 002:
AC-1: Default injection — DEF, all omitted
AC-2: Override semantics — FWD with speed override
AC-3: None treated as absent — speed: null
AC-4: Pure function — no input mutation
AC-5: ROLE_DEFAULTS table values match ADR-0003
AC-6: Player ID assignment — team_a
AC-7: assign_player_ids handles None and empty
AC-8: read_api_key — happy path
AC-9: read_api_key — missing env var
AC-10: read_api_key — empty / whitespace env var
AC-11: read_api_key — symmetric matches
AC-12: read_api_key — unknown provider
"""

import pytest
from src.foundation.config_preprocessor import (
    apply_role_defaults,
    assign_player_ids,
    read_api_key,
    ROLE_DEFAULTS,
    PROVIDER_ENV_KEYS,
)
from src.foundation.config_errors import ConfigError


class TestAC1DefaultInjectionDEFAllOmitted:
    """Test AC-1: Default injection — DEF, all omitted."""

    def test_apply_role_defaults_empty_raw_player_def_fills_all_attributes(self):
        """Empty raw_player with role=DEF should fill all 6 numeric attributes from defaults."""
        # Arrange
        raw_player = {}
        role = "DEF"

        # Act
        result = apply_role_defaults(raw_player, role)

        # Assert
        expected = {
            "role": "DEF",
            "speed": 12,
            "skill": 8,
            "strength": 16,
            "save": 0,
            "discipline": 16,
            "dribbling": 6,
        }
        assert result == expected

    @pytest.mark.parametrize("role", ["GK", "DEF", "MID", "FWD"])
    def test_apply_role_defaults_each_role_with_empty_raw_player(self, role):
        """Each role with empty raw_player should return role + all defaults for that role."""
        # Arrange
        raw_player = {}

        # Act
        result = apply_role_defaults(raw_player, role)

        # Assert
        expected = {"role": role, **ROLE_DEFAULTS[role]}
        assert result == expected


class TestAC2OverrideSemanticsFWDSpeedOverride:
    """Test AC-2: Override semantics — FWD with speed override."""

    def test_apply_role_defaults_fwd_speed_override_preserves_override(self):
        """FWD with speed=18 should keep speed=18, fill other attributes from defaults."""
        # Arrange
        raw_player = {"speed": 18}
        role = "FWD"

        # Act
        result = apply_role_defaults(raw_player, role)

        # Assert
        expected = {
            "role": "FWD",
            "speed": 18,  # Override preserved
            "skill": 14,
            "strength": 14,
            "save": 0,
            "discipline": 10,
            "dribbling": 16,
        }
        assert result == expected

    @pytest.mark.parametrize("attr_name,override_value", [
        ("speed", 20),
        ("skill", 18),
        ("strength", 12),
        ("save", 8),  # Note: validation of save on non-GK is handled by Pydantic later
        ("discipline", 18),
        ("dribbling", 20),
    ])
    def test_apply_role_defaults_individual_attribute_overrides(self, attr_name, override_value):
        """Each attribute can be overridden individually."""
        # Arrange
        raw_player = {attr_name: override_value}
        role = "MID"

        # Act
        result = apply_role_defaults(raw_player, role)

        # Assert
        # Should have the override value for the specified attribute
        assert result[attr_name] == override_value
        # Should have defaults for all other attributes
        for key, default_value in ROLE_DEFAULTS[role].items():
            if key != attr_name:
                assert result[key] == default_value
        assert result["role"] == role

    def test_apply_role_defaults_multiple_overrides_combine_correctly(self):
        """Multiple overrides should combine correctly with defaults."""
        # Arrange
        raw_player = {"speed": 18, "dribbling": 20}
        role = "GK"

        # Act
        result = apply_role_defaults(raw_player, role)

        # Assert
        expected = {
            "role": "GK",
            "speed": 18,      # Override
            "skill": 10,      # Default
            "strength": 8,    # Default
            "save": 16, # Default
            "discipline": 14, # Default
            "dribbling": 20,  # Override
        }
        assert result == expected


class TestAC3NoneTreatedAsAbsentSpeedNull:
    """Test AC-3: None treated as absent — speed: null."""

    def test_apply_role_defaults_speed_none_routes_to_default(self):
        """speed: None should route to the MID default (14), not None."""
        # Arrange
        raw_player = {"speed": None}
        role = "MID"

        # Act
        result = apply_role_defaults(raw_player, role)

        # Assert
        assert result["speed"] == 14  # MID default, not None

    def test_apply_role_defaults_save_none_gk_returns_default(self):
        """save: None on GK should return save=16."""
        # Arrange
        raw_player = {"save": None}
        role = "GK"

        # Act
        result = apply_role_defaults(raw_player, role)

        # Assert
        assert result["save"] == 16

    def test_apply_role_defaults_save_none_def_returns_zero(self):
        """save: None on DEF should return save=0."""
        # Arrange
        raw_player = {"save": None}
        role = "DEF"

        # Act
        result = apply_role_defaults(raw_player, role)

        # Assert
        assert result["save"] == 0


class TestAC4PureFunctionNoInputMutation:
    """Test AC-4: Pure function — no input mutation."""

    def test_apply_role_defaults_input_dict_unchanged(self):
        """Input dict should be unchanged after function call."""
        # Arrange
        raw = {"speed": 18}
        original_raw = raw.copy()

        # Act
        result = apply_role_defaults(raw, "FWD")

        # Assert
        assert raw == original_raw  # No mutation
        assert raw == {"speed": 18}  # No role or other keys added
        assert result != raw  # Returns new dict

    def test_apply_role_defaults_idempotent_behavior(self):
        """Calling apply_role_defaults twice should produce same result."""
        # Arrange
        raw_player = {}
        role = "MID"

        # Act
        result1 = apply_role_defaults(raw_player, role)
        result2 = apply_role_defaults(result1, role)

        # Assert
        assert result1 == result2

    def test_apply_role_defaults_returns_new_dict_instance(self):
        """Function should return a new dict instance, not modify input."""
        # Arrange
        raw_player = {"speed": 15}

        # Act
        result = apply_role_defaults(raw_player, "DEF")

        # Assert
        assert result is not raw_player
        assert id(result) != id(raw_player)


class TestAC5ROLEDEFAULTSTableValuesMatchADR:
    """Test AC-5: ROLE_DEFAULTS table values match ADR-0003."""

    def test_role_defaults_gk_values_match_adr(self):
        """GK values should match ADR-0003 table exactly."""
        expected_gk = {
            "speed": 8,
            "skill": 10,
            "strength": 8,
            "save": 16,
            "discipline": 14,
            "dribbling": 4,
        }
        assert ROLE_DEFAULTS["GK"] == expected_gk

    def test_role_defaults_def_values_match_adr(self):
        """DEF values should match ADR-0003 table exactly."""
        expected_def = {
            "speed": 12,
            "skill": 8,
            "strength": 16,
            "save": 0,
            "discipline": 16,
            "dribbling": 6,
        }
        assert ROLE_DEFAULTS["DEF"] == expected_def

    def test_role_defaults_mid_values_match_adr(self):
        """MID values should match ADR-0003 table exactly."""
        expected_mid = {
            "speed": 14,
            "skill": 16,
            "strength": 10,
            "save": 0,
            "discipline": 14,
            "dribbling": 12,
        }
        assert ROLE_DEFAULTS["MID"] == expected_mid

    def test_role_defaults_fwd_values_match_adr(self):
        """FWD values should match ADR-0003 table exactly."""
        expected_fwd = {
            "speed": 16,
            "skill": 14,
            "strength": 14,
            "save": 0,
            "discipline": 10,
            "dribbling": 16,
        }
        assert ROLE_DEFAULTS["FWD"] == expected_fwd

    def test_role_defaults_all_roles_have_six_attributes(self):
        """Each role should have exactly 6 attributes."""
        for role, attributes in ROLE_DEFAULTS.items():
            assert len(attributes) == 6, f"Role {role} should have 6 attributes"
            expected_keys = {"speed", "skill", "strength", "save", "discipline", "dribbling"}
            assert set(attributes.keys()) == expected_keys, f"Role {role} has wrong attribute names"

    def test_role_defaults_save_values(self):
        """save should be 16 for GK and 0 for DEF/MID/FWD."""
        assert ROLE_DEFAULTS["GK"]["save"] == 16
        assert ROLE_DEFAULTS["DEF"]["save"] == 0
        assert ROLE_DEFAULTS["MID"]["save"] == 0
        assert ROLE_DEFAULTS["FWD"]["save"] == 0


class TestAC6PlayerIDAssignmentTeamA:
    """Test AC-6: Player ID assignment — team_a."""

    def test_assign_player_ids_five_players_sequential_ids(self):
        """5 players should get sequential IDs team_a_0 through team_a_4."""
        # Arrange
        raw_players = [
            {"role": "GK"},
            {"role": "DEF"},
            {"role": "DEF"},
            {"role": "MID"},
            {"role": "FWD"},
        ]

        # Act
        result = assign_player_ids("team_a", raw_players)

        # Assert
        expected_player_ids = ["team_a_0", "team_a_1", "team_a_2", "team_a_3", "team_a_4"]
        actual_player_ids = [p["player_id"] for p in result]
        assert actual_player_ids == expected_player_ids

        # Original role and other keys should be preserved
        for i, player in enumerate(result):
            assert player["role"] == raw_players[i]["role"]

    def test_assign_player_ids_team_b_produces_team_b_ids(self):
        """team_b should produce team_b_0..team_b_4 IDs."""
        # Arrange
        raw_players = [{"role": "GK"}, {"role": "DEF"}]

        # Act
        result = assign_player_ids("team_b", raw_players)

        # Assert
        assert result[0]["player_id"] == "team_b_0"
        assert result[1]["player_id"] == "team_b_1"

    def test_assign_player_ids_input_list_not_mutated(self):
        """Input list should not be mutated."""
        # Arrange
        raw_players = [{"role": "GK"}, {"role": "DEF"}]
        original = [p.copy() for p in raw_players]

        # Act
        result = assign_player_ids("team_a", raw_players)

        # Assert
        assert raw_players == original  # No mutation
        assert "player_id" not in raw_players[0]  # Original doesn't have player_id
        assert "player_id" not in raw_players[1]
        assert result[0]["player_id"] == "team_a_0"  # Result does have player_id

    def test_assign_player_ids_player_id_is_string_not_int(self):
        """player_id should be str, not int."""
        # Arrange
        raw_players = [{"role": "GK"}]

        # Act
        result = assign_player_ids("team_a", raw_players)

        # Assert
        player_id = result[0]["player_id"]
        assert isinstance(player_id, str)
        assert player_id == "team_a_0"


class TestAC7AssignPlayerIDsHandlesNoneAndEmpty:
    """Test AC-7: assign_player_ids handles None and empty."""

    def test_assign_player_ids_none_returns_empty_list(self):
        """assign_player_ids(team_id, None) should return []."""
        # Act
        result = assign_player_ids("team_a", None)

        # Assert
        assert result == []

    def test_assign_player_ids_empty_list_returns_empty_list(self):
        """assign_player_ids(team_id, []) should return []."""
        # Act
        result = assign_player_ids("team_a", [])

        # Assert
        assert result == []

    def test_assign_player_ids_both_teams_none_handling(self):
        """Both team_a and team_b should handle None consistently."""
        # Act
        result_a = assign_player_ids("team_a", None)
        result_b = assign_player_ids("team_b", None)

        # Assert
        assert result_a == []
        assert result_b == []


class TestAC8ReadAPIKeyHappyPath:
    """Test AC-8: read_api_key — happy path."""

    def test_read_api_key_openai_valid_key_returns_value(self, monkeypatch):
        """OPENAI_API_KEY set with valid value should return that value."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-123")

        # Act
        result = read_api_key("openai")

        # Assert
        assert result == "sk-test-123"

    def test_read_api_key_anthropic_valid_key_returns_value(self, monkeypatch):
        """ANTHROPIC_API_KEY set with valid value should return that value."""
        # Arrange
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-456")

        # Act
        result = read_api_key("anthropic")

        # Assert
        assert result == "sk-ant-test-456"

    def test_read_api_key_strips_surrounding_whitespace(self, monkeypatch):
        """Surrounding whitespace should be stripped."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "  sk-test-key  ")

        # Act
        result = read_api_key("openai")

        # Assert
        assert result == "sk-test-key"


class TestAC9ReadAPIKeyMissingEnvVar:
    """Test AC-9: read_api_key — missing env var."""

    def test_read_api_key_openai_missing_raises_config_error(self, monkeypatch):
        """Unset OPENAI_API_KEY should raise ConfigError with specific message."""
        # Arrange
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            read_api_key("openai")

        error_msg = str(exc_info.value)
        assert "OPENAI_API_KEY" in error_msg
        assert "openai cannot initialize" in error_msg
        assert "is not set" in error_msg

    def test_read_api_key_anthropic_missing_raises_config_error(self, monkeypatch):
        """Unset ANTHROPIC_API_KEY should raise ConfigError with specific message."""
        # Arrange
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            read_api_key("anthropic")

        error_msg = str(exc_info.value)
        assert "ANTHROPIC_API_KEY" in error_msg
        assert "anthropic cannot initialize" in error_msg
        assert "is not set" in error_msg


class TestAC10ReadAPIKeyEmptyWhitespaceEnvVar:
    """Test AC-10: read_api_key — empty / whitespace env var."""

    def test_read_api_key_empty_string_raises_config_error(self, monkeypatch):
        """Empty OPENAI_API_KEY should raise ConfigError with 'set but empty' message."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "")

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            read_api_key("openai")

        error_msg = str(exc_info.value)
        assert "OPENAI_API_KEY is set but empty" in error_msg

    def test_read_api_key_whitespace_only_raises_config_error(self, monkeypatch):
        """Whitespace-only OPENAI_API_KEY should raise ConfigError."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "   ")

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            read_api_key("openai")

        error_msg = str(exc_info.value)
        assert "OPENAI_API_KEY is set but empty" in error_msg

    def test_read_api_key_tabs_newlines_raises_config_error(self, monkeypatch):
        """Tab and newline whitespace should also raise error."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "\t\n")

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            read_api_key("openai")

        error_msg = str(exc_info.value)
        assert "OPENAI_API_KEY is set but empty" in error_msg

    def test_read_api_key_error_messages_distinguishable(self, monkeypatch):
        """'set but empty' vs 'not set' messages should be distinguishable."""
        # Test empty (set but empty)
        monkeypatch.setenv("OPENAI_API_KEY", "")
        with pytest.raises(ConfigError) as exc_info_empty:
            read_api_key("openai")

        # Test missing (not set)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ConfigError) as exc_info_missing:
            read_api_key("openai")

        empty_msg = str(exc_info_empty.value)
        missing_msg = str(exc_info_missing.value)

        assert "is set but empty" in empty_msg
        assert "is not set" in missing_msg
        assert empty_msg != missing_msg


class TestAC11ReadAPIKeySymmetricMatches:
    """Test AC-11: read_api_key — symmetric matches."""

    def test_read_api_key_same_provider_both_teams_works(self, monkeypatch):
        """Calling read_api_key("openai") twice should return same value both times."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-shared")

        # Act
        result1 = read_api_key("openai")
        result2 = read_api_key("openai")

        # Assert
        assert result1 == "sk-shared"
        assert result2 == "sk-shared"
        assert result1 == result2

    def test_read_api_key_alternating_calls_both_succeed(self, monkeypatch):
        """Alternating openai/anthropic/openai calls should all succeed when both env vars set."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-anthropic")

        # Act
        result1 = read_api_key("openai")
        result2 = read_api_key("anthropic")
        result3 = read_api_key("openai")

        # Assert
        assert result1 == "sk-openai"
        assert result2 == "sk-anthropic"
        assert result3 == "sk-openai"


class TestAC12ReadAPIKeyUnknownProvider:
    """Test AC-12: read_api_key — unknown provider."""

    def test_read_api_key_gemini_reads_google_api_key(self, monkeypatch):
        """read_api_key("gemini") should read GOOGLE_API_KEY from environment."""
        # Arrange
        monkeypatch.setenv("GOOGLE_API_KEY", "test-gemini-key-123")

        # Act
        result = read_api_key("gemini")

        # Assert
        assert result == "test-gemini-key-123"

    def test_read_api_key_empty_string_provider_raises_config_error(self):
        """Empty string provider should raise ConfigError."""
        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            read_api_key("")

        error_msg = str(exc_info.value)
        assert "Unknown provider" in error_msg

    def test_provider_env_keys_contains_all_builtin_providers(self):
        """PROVIDER_ENV_KEYS should contain openai, anthropic, and gemini."""
        expected = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GOOGLE_API_KEY"
        }
        assert PROVIDER_ENV_KEYS == expected