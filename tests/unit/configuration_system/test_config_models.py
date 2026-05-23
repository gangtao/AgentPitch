"""
Tests for Configuration System Pydantic models.

Tests all 14 acceptance criteria from Story 001:
AC-1: PlayerConfig range upper bound
AC-2: PlayerConfig range lower bound
AC-3: GK-only save validation
AC-4: TeamConfig exactly 5 players
AC-5: TeamConfig exactly 1 GK
AC-6: Provider enum validation
AC-7: Strict integer enforcement
AC-8: MatchParams field_width gt=0
AC-9: MatchParams tick_rate / duration bounds
AC-10: Immutability (frozen models)
AC-11: MatchConfig.teams property
AC-12: MatchConfig.total_ticks property
AC-13: api_key exclusion from serialization
AC-14: api_key field validation
"""

import pytest
from pydantic import ValidationError

from src.foundation.config_models import (
    PlayerConfig, TeamConfig, MatchParams, OutputConfig, MatchConfig
)


def _valid_player_kwargs(role: str = "MID", **overrides) -> dict:
    """Return valid PlayerConfig kwargs with optional overrides."""
    base = {
        "player_id": f"team_a_0",
        "role": role,
        "speed": 10,
        "skill": 10,
        "strength": 10,
        "save": 16 if role == "GK" else 0,
        "discipline": 10,
        "dribbling": 10,
    }
    base.update(overrides)
    return base


def _valid_team_kwargs(**overrides) -> dict:
    """Return valid TeamConfig kwargs with optional overrides."""
    # Create 5 players with exactly 1 GK
    players = [
        PlayerConfig(**_valid_player_kwargs("GK", player_id="team_a_0")),
        PlayerConfig(**_valid_player_kwargs("DEF", player_id="team_a_1")),
        PlayerConfig(**_valid_player_kwargs("DEF", player_id="team_a_2")),
        PlayerConfig(**_valid_player_kwargs("MID", player_id="team_a_3")),
        PlayerConfig(**_valid_player_kwargs("FWD", player_id="team_a_4")),
    ]

    base = {
        "team_id": "team_a",
        "name": "Team A",
        "llm_provider": "openai",
        "llm_model": "gpt-4o",
        "api_key": "sk-test-key",
        "players": players,
    }
    base.update(overrides)
    return base


def _valid_match_params_kwargs(**overrides) -> dict:
    """Return valid MatchParams kwargs with optional overrides."""
    base = {
        "seed": 42,
        "tick_rate": 10,
        "duration_minutes": 90,
        "field_width": 105.0,
        "field_height": 68.0,
        "match_id": "test-match",
    }
    base.update(overrides)
    return base


def _valid_match_config_kwargs(**overrides) -> dict:
    """Return valid MatchConfig kwargs with optional overrides."""
    base = {
        "match": MatchParams(**_valid_match_params_kwargs()),
        "output": OutputConfig(log_dir="/tmp/test"),
        "team_a": TeamConfig(**_valid_team_kwargs()),
        "team_b": TeamConfig(**_valid_team_kwargs()),
    }
    base.update(overrides)
    return base


class TestAC1PlayerConfigRangeUpperBound:
    """Test AC-1: PlayerConfig range enforcement upper bound."""

    @pytest.mark.parametrize("attr_name,boundary_value", [
        ("speed", 20), ("skill", 20), ("strength", 20),
        ("save", 20), ("discipline", 20), ("dribbling", 20)
    ])
    def test_player_config_boundary_values_accepted(self, attr_name, boundary_value):
        """Values at upper boundary should be accepted."""
        kwargs = _valid_player_kwargs("GK" if attr_name == "save" else "MID")
        kwargs[attr_name] = boundary_value
        player = PlayerConfig(**kwargs)
        assert getattr(player, attr_name) == boundary_value

    @pytest.mark.parametrize("attr_name", [
        "speed", "skill", "strength", "save", "discipline", "dribbling"
    ])
    def test_player_config_above_upper_bound_rejected(self, attr_name):
        """Values above upper boundary should be rejected."""
        kwargs = _valid_player_kwargs("GK" if attr_name == "save" else "MID")
        kwargs[attr_name] = 21  # Above le=20
        with pytest.raises(ValidationError) as exc_info:
            PlayerConfig(**kwargs)
        assert attr_name in str(exc_info.value)

    def test_player_config_speed_25_rejected(self):
        """AC-CONFIG-03: speed=25 raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerConfig(**_valid_player_kwargs(speed=25))
        error_msg = str(exc_info.value)
        assert "speed" in error_msg


class TestAC2PlayerConfigRangeLowerBound:
    """Test AC-2: PlayerConfig range enforcement lower bound."""

    @pytest.mark.parametrize("attr_name", [
        "speed", "skill", "strength", "discipline", "dribbling"
    ])
    def test_player_config_lower_bound_accepted(self, attr_name):
        """Values at lower boundary (ge=1) should be accepted."""
        kwargs = _valid_player_kwargs()
        kwargs[attr_name] = 1
        player = PlayerConfig(**kwargs)
        assert getattr(player, attr_name) == 1

    @pytest.mark.parametrize("attr_name", [
        "speed", "skill", "strength", "discipline", "dribbling"
    ])
    def test_player_config_below_lower_bound_rejected(self, attr_name):
        """Values below lower boundary should be rejected."""
        kwargs = _valid_player_kwargs()
        kwargs[attr_name] = 0  # Below ge=1
        with pytest.raises(ValidationError):
            PlayerConfig(**kwargs)

    @pytest.mark.parametrize("attr_name", [
        "speed", "skill", "strength", "discipline", "dribbling"
    ])
    def test_player_config_negative_values_rejected(self, attr_name):
        """Negative values should be rejected."""
        kwargs = _valid_player_kwargs()
        kwargs[attr_name] = -1
        with pytest.raises(ValidationError):
            PlayerConfig(**kwargs)

    def test_player_config_save_zero_accepted_non_gk(self):
        """save=0 should be accepted for non-GK (ge=0)."""
        player = PlayerConfig(**_valid_player_kwargs("DEF", save=0))
        assert player.save == 0

    def test_player_config_save_negative_rejected(self):
        """save=-1 should be rejected (ge=0)."""
        with pytest.raises(ValidationError):
            PlayerConfig(**_valid_player_kwargs("GK", save=-1))


class TestAC3GKOnlySaveReach:
    """Test AC-3: GK-only save validation."""

    def test_player_config_non_gk_save_positive_rejected(self):
        """AC-CONFIG-04: Non-GK with save > 0 raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerConfig(**_valid_player_kwargs("DEF", save=10))

        error_msg = str(exc_info.value)
        assert "save is GK-only" in error_msg

    @pytest.mark.parametrize("role", ["DEF", "MID", "FWD"])
    def test_player_config_outfield_save_one_rejected(self, role):
        """Outfield players with save=1 should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerConfig(**_valid_player_kwargs(role, save=1))
        assert "save is GK-only" in str(exc_info.value)

    @pytest.mark.parametrize("role", ["DEF", "MID", "FWD"])
    def test_player_config_outfield_save_zero_accepted(self, role):
        """Outfield players with save=0 should be accepted."""
        player = PlayerConfig(**_valid_player_kwargs(role, save=0))
        assert player.save == 0

    def test_player_config_gk_save_positive_accepted(self):
        """GK with save > 0 should be accepted."""
        player = PlayerConfig(**_valid_player_kwargs("GK", save=16))
        assert player.save == 16


class TestAC4TeamConfigPlayerCountRange:
    """Test AC-4: TeamConfig player count range. Per 2026-04-23 the
    bounds were widened from exactly-5 to [5, 11] to support 11v11
    matches alongside the original 5v5 config."""

    def test_team_config_4_players_rejected(self):
        """AC-CONFIG-05: 4 players raises validation error."""
        # Create team with only 4 players
        players = [
            PlayerConfig(**_valid_player_kwargs("GK", player_id="team_a_0")),
            PlayerConfig(**_valid_player_kwargs("DEF", player_id="team_a_1")),
            PlayerConfig(**_valid_player_kwargs("MID", player_id="team_a_2")),
            PlayerConfig(**_valid_player_kwargs("FWD", player_id="team_a_3")),
        ]

        with pytest.raises(ValidationError) as exc_info:
            TeamConfig(**_valid_team_kwargs(players=players))

        # Check that validation mentions players field and length constraint
        error_msg = str(exc_info.value)
        assert "players" in error_msg

    def test_team_config_12_players_rejected(self):
        """12 players exceeds the upper bound (11)."""
        players = [
            PlayerConfig(**_valid_player_kwargs("GK", player_id=f"team_a_{i}"))
            if i == 0 else PlayerConfig(**_valid_player_kwargs("DEF", player_id=f"team_a_{i}"))
            for i in range(12)
        ]

        with pytest.raises(ValidationError):
            TeamConfig(**_valid_team_kwargs(players=players))

    def test_team_config_0_players_rejected(self):
        """0 players should be rejected."""
        with pytest.raises(ValidationError):
            TeamConfig(**_valid_team_kwargs(players=[]))

    def test_team_config_5_players_accepted(self):
        """Exactly 5 players should be accepted."""
        team = TeamConfig(**_valid_team_kwargs())
        assert len(team.players) == 5


class TestAC5TeamConfigExactly1GK:
    """Test AC-5: TeamConfig exactly 1 GK."""

    def test_team_config_0_gk_rejected(self):
        """0 GK players should be rejected."""
        players = [
            PlayerConfig(**_valid_player_kwargs("DEF", player_id=f"team_a_{i}"))
            for i in range(5)
        ]

        with pytest.raises(ValidationError) as exc_info:
            TeamConfig(**_valid_team_kwargs(players=players))

        error_msg = str(exc_info.value)
        assert "GK players found — exactly 1 required" in error_msg

    def test_team_config_2_gk_rejected(self):
        """AC-CONFIG-06: 2 GK players raises validation error."""
        players = [
            PlayerConfig(**_valid_player_kwargs("GK", player_id="team_a_0")),
            PlayerConfig(**_valid_player_kwargs("GK", player_id="team_a_1")),
            PlayerConfig(**_valid_player_kwargs("DEF", player_id="team_a_2")),
            PlayerConfig(**_valid_player_kwargs("MID", player_id="team_a_3")),
            PlayerConfig(**_valid_player_kwargs("FWD", player_id="team_a_4")),
        ]

        with pytest.raises(ValidationError) as exc_info:
            TeamConfig(**_valid_team_kwargs(players=players))

        error_msg = str(exc_info.value)
        assert "2 GK players found — exactly 1 required" in error_msg

    def test_team_config_1_gk_accepted(self):
        """Exactly 1 GK should be accepted."""
        team = TeamConfig(**_valid_team_kwargs())
        gk_count = sum(1 for p in team.players if p.role == "GK")
        assert gk_count == 1


class TestAC6ProviderEnumValidation:
    """Test AC-6: Provider enum validation (deprecated - now accepts any string)."""

    def test_team_config_gemini_provider_accepted(self):
        """Gemini is now a built-in provider (post ADR-0021)."""
        team = TeamConfig(**_valid_team_kwargs(llm_provider="gemini"))
        assert team.llm_provider == "gemini"

    @pytest.mark.parametrize("provider_name", [
        "google", "claude", "ChatGPT", "ollama", "my-custom-provider"
    ])
    def test_team_config_custom_providers_accepted(self, provider_name):
        """Custom providers are now accepted (deprecated field, widened to str)."""
        team = TeamConfig(**_valid_team_kwargs(llm_provider=provider_name))
        assert team.llm_provider == provider_name

    @pytest.mark.parametrize("valid_provider", ["openai", "anthropic", "gemini"])
    def test_team_config_builtin_providers_accepted(self, valid_provider):
        """Built-in providers should be accepted."""
        team = TeamConfig(**_valid_team_kwargs(llm_provider=valid_provider))
        assert team.llm_provider == valid_provider


class TestAC7StrictIntegerEnforcement:
    """Test AC-7: Strict integer enforcement."""

    @pytest.mark.parametrize("attr_name", [
        "speed", "skill", "strength", "save", "discipline", "dribbling"
    ])
    def test_player_config_float_in_int_field_rejected(self, attr_name):
        """AC-CONFIG-15: Float values in int fields should be rejected."""
        kwargs = _valid_player_kwargs("GK" if attr_name == "save" else "MID")
        kwargs[attr_name] = 8.0  # Float instead of int

        with pytest.raises(ValidationError):
            PlayerConfig(**kwargs)

    @pytest.mark.parametrize("attr_name,float_val", [
        ("seed", 42.0), ("tick_rate", 10.0), ("duration_minutes", 90.0)
    ])
    def test_match_params_float_in_int_field_rejected(self, attr_name, float_val):
        """Float values in MatchParams int fields should be rejected."""
        kwargs = _valid_match_params_kwargs()
        kwargs[attr_name] = float_val

        with pytest.raises(ValidationError):
            MatchParams(**kwargs)

    def test_player_config_boolean_in_int_field_rejected(self):
        """Boolean values in int fields should be rejected under strict mode."""
        with pytest.raises(ValidationError):
            PlayerConfig(**_valid_player_kwargs(speed=True))


class TestAC8MatchParamsFieldWidthGtZero:
    """Test AC-8: MatchParams field_width gt=0."""

    def test_match_params_field_width_zero_rejected(self):
        """AC-CONFIG-16: field_width=0 raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            MatchParams(**_valid_match_params_kwargs(field_width=0.0))

        error_msg = str(exc_info.value)
        assert "field_width" in error_msg

    def test_match_params_field_width_negative_rejected(self):
        """field_width < 0 should be rejected."""
        with pytest.raises(ValidationError):
            MatchParams(**_valid_match_params_kwargs(field_width=-1.0))

    def test_match_params_field_height_zero_rejected(self):
        """field_height=0 should be rejected (gt=0)."""
        with pytest.raises(ValidationError):
            MatchParams(**_valid_match_params_kwargs(field_height=0.0))

    def test_match_params_field_dimensions_positive_accepted(self):
        """Positive field dimensions should be accepted."""
        params = MatchParams(**_valid_match_params_kwargs(field_width=105.0, field_height=68.0))
        assert params.field_width == 105.0
        assert params.field_height == 68.0

    def test_match_params_field_dimensions_small_positive_accepted(self):
        """Small positive values should be accepted."""
        params = MatchParams(**_valid_match_params_kwargs(field_width=0.001, field_height=0.001))
        assert params.field_width == 0.001
        assert params.field_height == 0.001


class TestAC9MatchParamsRangeBounds:
    """Test AC-9: MatchParams tick_rate and duration_minutes bounds."""

    @pytest.mark.parametrize("tick_rate", [0, 61, -1, 100])
    def test_match_params_tick_rate_out_of_bounds_rejected(self, tick_rate):
        """tick_rate outside [1, 60] should be rejected."""
        with pytest.raises(ValidationError):
            MatchParams(**_valid_match_params_kwargs(tick_rate=tick_rate))

    @pytest.mark.parametrize("tick_rate", [1, 30, 60])
    def test_match_params_tick_rate_in_bounds_accepted(self, tick_rate):
        """tick_rate in [1, 60] should be accepted."""
        params = MatchParams(**_valid_match_params_kwargs(tick_rate=tick_rate))
        assert params.tick_rate == tick_rate

    @pytest.mark.parametrize("duration", [0, 121, -1, 200])
    def test_match_params_duration_out_of_bounds_rejected(self, duration):
        """duration_minutes outside [1, 120] should be rejected."""
        with pytest.raises(ValidationError):
            MatchParams(**_valid_match_params_kwargs(duration_minutes=duration))

    @pytest.mark.parametrize("duration", [1, 90, 120])
    def test_match_params_duration_in_bounds_accepted(self, duration):
        """duration_minutes in [1, 120] should be accepted."""
        params = MatchParams(**_valid_match_params_kwargs(duration_minutes=duration))
        assert params.duration_minutes == duration


class TestAC10Immutability:
    """Test AC-10: Immutability (frozen models)."""

    def test_player_config_immutable_after_construction(self):
        """PlayerConfig should be immutable after construction."""
        player = PlayerConfig(**_valid_player_kwargs())

        with pytest.raises(ValidationError):
            player.speed = 15

        with pytest.raises(ValidationError):
            player.role = "GK"

    def test_team_config_immutable_after_construction(self):
        """TeamConfig should be immutable after construction."""
        team = TeamConfig(**_valid_team_kwargs())

        with pytest.raises(ValidationError):
            team.llm_model = "different-model"

    def test_match_params_immutable_after_construction(self):
        """MatchParams should be immutable after construction."""
        params = MatchParams(**_valid_match_params_kwargs())

        with pytest.raises(ValidationError):
            params.tick_rate = 20

    def test_output_config_immutable_after_construction(self):
        """OutputConfig should be immutable after construction."""
        output = OutputConfig(log_dir="/tmp/test")

        with pytest.raises(ValidationError):
            output.log_dir = "/tmp/different"

    def test_match_config_immutable_after_construction(self):
        """AC-CONFIG-20: MatchConfig should be immutable after construction."""
        config = MatchConfig(**_valid_match_config_kwargs())

        with pytest.raises(ValidationError):
            config.match = MatchParams(**_valid_match_params_kwargs())

    def test_nested_mutation_blocked(self):
        """Nested mutations should also be blocked."""
        config = MatchConfig(**_valid_match_config_kwargs())

        with pytest.raises(ValidationError):
            config.team_a.players[0].speed = 99


class TestAC11MatchConfigTeamsProperty:
    """Test AC-11: MatchConfig.teams property."""

    def test_match_config_teams_property_returns_dict(self):
        """teams property should return dict keyed by team name."""
        config = MatchConfig(**_valid_match_config_kwargs())

        teams = config.teams
        assert isinstance(teams, dict)
        assert set(teams.keys()) == {"team_a", "team_b"}
        assert isinstance(teams["team_a"], TeamConfig)
        assert isinstance(teams["team_b"], TeamConfig)

    def test_match_config_teams_property_identity_check(self):
        """teams property should return references to actual team objects."""
        config = MatchConfig(**_valid_match_config_kwargs())

        teams = config.teams
        assert teams["team_a"] is config.team_a
        assert teams["team_b"] is config.team_b


class TestAC12MatchConfigTotalTicksProperty:
    """Test AC-12: MatchConfig.total_ticks property."""

    def test_match_config_total_ticks_computation(self):
        """total_ticks should compute tick_rate * duration_minutes * 60."""
        config = MatchConfig(**_valid_match_config_kwargs(
            match=MatchParams(**_valid_match_params_kwargs(tick_rate=10, duration_minutes=90))
        ))

        assert config.total_ticks == 54000  # 10 * 90 * 60

    @pytest.mark.parametrize("tick_rate,duration,expected", [
        (1, 1, 60),           # Minimum values
        (60, 120, 432000),    # Maximum values
        (30, 45, 81000),      # Mid-range values
    ])
    def test_match_config_total_ticks_edge_cases(self, tick_rate, duration, expected):
        """total_ticks computation should work for edge cases."""
        config = MatchConfig(**_valid_match_config_kwargs(
            match=MatchParams(**_valid_match_params_kwargs(
                tick_rate=tick_rate, duration_minutes=duration
            ))
        ))

        assert config.total_ticks == expected


class TestAC13ApiKeyExclusionFromSerialization:
    """Test AC-13: api_key exclusion from serialization."""

    def test_team_config_model_dump_excludes_api_key(self):
        """TeamConfig.model_dump() should not contain api_key."""
        team = TeamConfig(**_valid_team_kwargs(api_key="sk-secret-key"))

        dumped = team.model_dump()
        assert "api_key" not in dumped
        assert "sk-secret-key" not in str(dumped)

    def test_team_config_model_dump_json_excludes_api_key(self):
        """TeamConfig.model_dump_json() should not contain api_key."""
        team = TeamConfig(**_valid_team_kwargs(api_key="sk-secret-key"))

        json_str = team.model_dump_json()
        assert "api_key" not in json_str
        assert "sk-secret-key" not in json_str

    def test_match_config_model_dump_excludes_api_keys(self):
        """MatchConfig.model_dump() should not contain any api_key fields."""
        config = MatchConfig(**_valid_match_config_kwargs(
            team_a=TeamConfig(**_valid_team_kwargs(api_key="sk-test-a")),
            team_b=TeamConfig(**_valid_team_kwargs(api_key="sk-test-b"))
        ))

        dumped = config.model_dump()
        dumped_str = str(dumped)

        assert "sk-test-a" not in dumped_str
        assert "sk-test-b" not in dumped_str
        assert "api_key" not in dumped["team_a"]
        assert "api_key" not in dumped["team_b"]


class TestAC14ApiKeyFieldValidation:
    """Test AC-14: api_key field validation."""

    def test_team_config_empty_api_key_accepted_post_adr_0021(self):
        """Per ADR-0021, empty api_key is allowed (provider-call sites validate
        at use time). LLM settings now live in the global LLM tab, so this
        config-load-time check is no longer the right gate."""
        team = TeamConfig(**_valid_team_kwargs(api_key=""))
        # Construction succeeds; provider-call sites must validate non-empty
        # before actually calling any LLM.
        assert len(team.players) == 5

    def test_team_config_valid_api_key_accepted(self):
        """Valid api_key should be accepted."""
        team = TeamConfig(**_valid_team_kwargs(api_key="sk-valid-key"))
        # Note: we can't access api_key directly due to exclude=True
        # but we can verify construction succeeded
        assert len(team.players) == 5  # Verify object was created successfully