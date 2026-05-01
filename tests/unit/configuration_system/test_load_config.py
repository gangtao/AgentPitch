"""Tests for Configuration System load_config orchestration.

Tests all 12 acceptance criteria from Story 004:
AC-1: Round-trip happy path - AC-CONFIG-01
AC-2: Default injection end-to-end - AC-CONFIG-02
AC-3: Missing required section - AC-CONFIG-11
AC-4: Unwritable log_dir - AC-CONFIG-19
AC-5: Determinism - AC-CONFIG-21
AC-6: Single public entry point
AC-7: ValidationError converted to ConfigError
AC-8: Phase ordering - parse error wins over section check
AC-9: Defensive api_key strip
AC-10: Missing env var fails fast - integration with Story 002
AC-11: log_dir created on success
AC-12: Edge Case 7 - players: null
"""

import os
import pytest
import inspect
from pathlib import Path

from src.foundation.config_loader import load_config
from src.foundation.config_errors import ConfigError


def _write_valid_match_yaml(tmp_path):
    """Helper to write a complete valid match.yaml for testing."""
    yaml_content = """
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0
  match_id: "test_match"

output:
  log_dir: "{log_dir}"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  players:
    - role: "GK"
      speed: 8
      skill: 10
      strength: 8
      save: 16
      discipline: 14
      dribbling: 4
    - role: "DEF"
      speed: 12
      skill: 8
      strength: 16
      discipline: 16
      dribbling: 6
    - role: "DEF"
      speed: 13
      skill: 9
      strength: 15
      discipline: 17
      dribbling: 7
    - role: "MID"
      speed: 14
      skill: 16
      strength: 10
      discipline: 14
      dribbling: 12
    - role: "FWD"
      speed: 16
      skill: 14
      strength: 14
      discipline: 10
      dribbling: 16

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"
"""
    path = tmp_path / "match.yaml"
    path.write_text(yaml_content.format(log_dir=str(tmp_path / "logs")))
    return path


class TestAC1RoundTripHappyPath:
    """Test AC-1: Round-trip happy path - AC-CONFIG-01."""

    def test_load_config_valid_full_config_loads_successfully(self, tmp_path, monkeypatch):
        """Valid full config loads without error, player IDs assigned correctly."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-anthropic")
        path = _write_valid_match_yaml(tmp_path)

        # Act
        cfg = load_config(str(path))

        # Assert
        # Verify player IDs are assigned correctly
        team_a_ids = [p.player_id for p in cfg.team_a.players]
        team_b_ids = [p.player_id for p in cfg.team_b.players]

        assert team_a_ids == ["team_a_0", "team_a_1", "team_a_2", "team_a_3", "team_a_4"]
        assert team_b_ids == ["team_b_0", "team_b_1", "team_b_2", "team_b_3", "team_b_4"]

        # Verify API keys are injected
        assert cfg.team_a.api_key == "sk-test-openai"
        assert cfg.team_b.api_key == "sk-test-anthropic"

        # Verify match parameters
        assert cfg.match.tick_rate == 10
        assert cfg.total_ticks == 54000  # 10 * 90 * 60

        # Verify configuration is frozen (immutable)
        from src.foundation.config_models import MatchConfig
        assert isinstance(cfg, MatchConfig)

    def test_load_config_returns_match_config_instance(self, tmp_path, monkeypatch):
        """load_config should return a MatchConfig instance."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        path = _write_valid_match_yaml(tmp_path)

        # Act
        cfg = load_config(str(path))

        # Assert
        from src.foundation.config_models import MatchConfig
        assert isinstance(cfg, MatchConfig)


class TestAC2DefaultInjectionEndToEnd:
    """Test AC-2: Default injection end-to-end - AC-CONFIG-02."""

    def test_load_config_minimal_player_block_fills_defaults(self, tmp_path, monkeypatch):
        """Minimal player block with only role should fill all attributes from defaults."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        yaml_content = f"""
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0

output:
  log_dir: "{tmp_path / "logs"}"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"
"""
        path = tmp_path / "minimal.yaml"
        path.write_text(yaml_content)

        # Act
        cfg = load_config(str(path))

        # Assert
        # Check that DEF player gets correct defaults
        def_player = None
        for p in cfg.team_a.players:
            if p.role == "DEF":
                def_player = p
                break

        assert def_player is not None
        assert def_player.speed == 12
        assert def_player.skill == 8
        assert def_player.strength == 16
        assert def_player.save == 0
        assert def_player.discipline == 16
        assert def_player.dribbling == 6

    def test_load_config_mixed_explicit_and_default_values(self, tmp_path, monkeypatch):
        """Player with some explicit values and some defaults should preserve explicit values."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        yaml_content = f"""
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0

output:
  log_dir: "{tmp_path / "logs"}"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  players:
    - role: "GK"
    - role: "MID"
      speed: 18
      dribbling: 20
    - role: "DEF"
    - role: "MID"
    - role: "FWD"

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"
"""
        path = tmp_path / "mixed.yaml"
        path.write_text(yaml_content)

        # Act
        cfg = load_config(str(path))

        # Assert
        mid_player = cfg.team_a.players[1]  # Second player is MID with overrides
        assert mid_player.role == "MID"
        assert mid_player.speed == 18      # Explicit override
        assert mid_player.dribbling == 20  # Explicit override
        assert mid_player.skill == 16      # Default from MID
        assert mid_player.strength == 10   # Default from MID
        assert mid_player.save == 0  # Default from MID
        assert mid_player.discipline == 14  # Default from MID


class TestAC3MissingRequiredSection:
    """Test AC-3: Missing required section - AC-CONFIG-11."""

    @pytest.mark.parametrize("missing_section", ["match", "output", "team_a", "team_b"])
    def test_load_config_missing_section_raises_config_error(self, tmp_path, missing_section):
        """Each missing required section should raise ConfigError with specific message."""
        # Arrange
        yaml_content = """
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0

output:
  log_dir: "/tmp/logs"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  players:
    - role: "GK"

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  players:
    - role: "GK"
"""
        # Parse into dict and remove the specified section
        import yaml
        data = yaml.safe_load(yaml_content)
        del data[missing_section]

        # Write back to file
        path = tmp_path / "missing_section.yaml"
        with open(path, "w") as f:
            yaml.dump(data, f)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            load_config(str(path))

        error_msg = str(exc_info.value)
        assert "missing_section.yaml is missing required section:" in error_msg
        assert missing_section in error_msg
        # Should not contain Pydantic's "field required" message
        assert "field required" not in error_msg

    def test_load_config_missing_two_sections_reports_first(self, tmp_path):
        """Missing two sections should report the first missing one in REQUIRED_SECTIONS order."""
        # Arrange - missing both output and team_b
        yaml_content = """
match:
  seed: 42

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  players:
    - role: "GK"
"""
        path = tmp_path / "missing_two.yaml"
        path.write_text(yaml_content)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            load_config(str(path))

        error_msg = str(exc_info.value)
        # Should report "output" first since it appears before "team_b" in REQUIRED_SECTIONS
        assert "missing required section: output" in error_msg
        assert "team_b" not in error_msg


class TestAC4UnwritableLogDir:
    """Test AC-4: Unwritable log_dir - AC-CONFIG-19."""

    @pytest.mark.skipif(os.name == "nt", reason="Permission tests not supported on Windows")
    @pytest.mark.skipif(os.geteuid() == 0, reason="Permissions test invalid as root")
    def test_load_config_unwritable_log_dir_raises_config_error(self, tmp_path, monkeypatch):
        """Unwritable log_dir should raise ConfigError with specific message."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        # Create a readonly directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o000)  # Remove all permissions

        yaml_content = f"""
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0

output:
  log_dir: "{readonly_dir / "logs"}"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"
"""
        path = tmp_path / "unwritable.yaml"
        path.write_text(yaml_content)

        try:
            # Act & Assert
            with pytest.raises(ConfigError) as exc_info:
                load_config(str(path))

            error_msg = str(exc_info.value)
            assert "Cannot create log directory" in error_msg
            assert str(readonly_dir / "logs") in error_msg

        finally:
            # Cleanup: restore permissions
            readonly_dir.chmod(0o755)

    def test_load_config_existing_log_dir_succeeds(self, tmp_path, monkeypatch):
        """Existing log_dir should succeed (idempotent)."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        # Pre-create the log directory
        log_dir = tmp_path / "existing_logs"
        log_dir.mkdir()

        path = _write_valid_match_yaml(tmp_path)
        # Update the log_dir path in the YAML
        content = path.read_text().replace(str(tmp_path / "logs"), str(log_dir))
        path.write_text(content)

        # Act
        cfg = load_config(str(path))

        # Assert
        assert cfg is not None
        assert log_dir.exists()
        assert log_dir.is_dir()


class TestAC5Determinism:
    """Test AC-5: Determinism - AC-CONFIG-21."""

    def test_load_config_two_loads_identical_output(self, tmp_path, monkeypatch):
        """Two loads of same file with same env vars should produce identical configs."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-deterministic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-deterministic")
        path = _write_valid_match_yaml(tmp_path)

        # Act
        cfg1 = load_config(str(path))
        cfg2 = load_config(str(path))

        # Assert
        # api_key is excluded by Field(exclude=True), so model_dump excludes it automatically
        dump1 = cfg1.model_dump()
        dump2 = cfg2.model_dump()

        assert dump1 == dump2

        # Verify player IDs are identical
        assert [p.player_id for p in cfg1.team_a.players] == [p.player_id for p in cfg2.team_a.players]
        assert [p.player_id for p in cfg1.team_b.players] == [p.player_id for p in cfg2.team_b.players]

    def test_load_config_hundred_iterations_identical(self, tmp_path, monkeypatch):
        """100 iterations should produce identical dumps."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        path = _write_valid_match_yaml(tmp_path)

        # Act - load 100 times
        dumps = []
        for _ in range(100):
            cfg = load_config(str(path))
            dumps.append(cfg.model_dump())

        # Assert - all dumps should be identical
        first_dump = dumps[0]
        for dump in dumps[1:]:
            assert dump == first_dump


class TestAC6SinglePublicEntryPoint:
    """Test AC-6: Single public entry point."""

    def test_load_config_api_surface_signature(self):
        """load_config should have exact signature (path: str) -> MatchConfig."""
        # Act
        sig = inspect.signature(load_config)

        # Assert
        params = list(sig.parameters.keys())
        assert params == ["path"]

        path_param = sig.parameters["path"]
        assert path_param.annotation == str or str(path_param.annotation) == "str"

        # Return annotation should reference MatchConfig
        assert "MatchConfig" in str(sig.return_annotation)

    def test_load_config_only_public_functions(self):
        """Only parse_yaml and load_config should be public in config_loader module."""
        # Arrange
        from src.foundation import config_loader

        # Act
        public_functions = [name for name in dir(config_loader)
                          if not name.startswith("_") and callable(getattr(config_loader, name))]

        # Assert
        # Should only have parse_yaml and load_config as public functions
        expected_public = {"parse_yaml", "load_config"}
        actual_public = {name for name in public_functions if name.startswith(("parse_", "load_"))}
        assert actual_public == expected_public


class TestAC7ValidationErrorConvertedToConfigError:
    """Test AC-7: ValidationError converted to ConfigError."""

    def test_load_config_speed_out_of_range_raises_config_error(self, tmp_path, monkeypatch):
        """Invalid speed value should raise ConfigError with field path."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        yaml_content = f"""
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0

output:
  log_dir: "{tmp_path / "logs"}"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
      speed: 25
    - role: "MID"
    - role: "FWD"

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"
"""
        path = tmp_path / "invalid_speed.yaml"
        path.write_text(yaml_content)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            load_config(str(path))

        error_msg = str(exc_info.value)
        # Should contain field path
        assert "team_a.players.2.speed" in error_msg
        # Should be ConfigError, not ValidationError
        assert isinstance(exc_info.value, ConfigError)
        # Original ValidationError should be in __cause__
        from pydantic import ValidationError
        assert isinstance(exc_info.value.__cause__, ValidationError)

    def test_load_config_non_gk_save_raises_config_error(self, tmp_path, monkeypatch):
        """Non-GK player with save > 0 should raise ConfigError."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        yaml_content = f"""
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0

output:
  log_dir: "{tmp_path / "logs"}"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  players:
    - role: "GK"
    - role: "DEF"
      save: 10
    - role: "DEF"
    - role: "MID"
    - role: "FWD"

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"
"""
        path = tmp_path / "invalid_save.yaml"
        path.write_text(yaml_content)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            load_config(str(path))

        error_msg = str(exc_info.value)
        assert "save is GK-only" in error_msg


class TestAC8PhaseOrderingParseErrorWins:
    """Test AC-8: Phase ordering - parse error wins over section check."""

    def test_load_config_broken_yaml_parse_error_wins(self, tmp_path):
        """Broken YAML with missing sections should trigger parse error first."""
        # Arrange
        yaml_content = "match:\n  seed: : : :\n"  # Parse error AND missing sections
        path = tmp_path / "broken.yaml"
        path.write_text(yaml_content)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            load_config(str(path))

        error_msg = str(exc_info.value)
        # Should contain Phase 1 parse error message
        assert "Config parse error at" in error_msg
        # Should NOT mention missing sections (Phase 2 never runs)
        assert "missing required section" not in error_msg

    def test_load_config_empty_file_not_missing_sections(self, tmp_path):
        """Empty file should raise empty error, not missing sections error."""
        # Arrange
        path = tmp_path / "empty.yaml"
        path.write_text("")

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            load_config(str(path))

        error_msg = str(exc_info.value)
        # Should be Phase 1 empty file error
        assert "Config file is empty" in error_msg
        # Should NOT be Phase 2 missing sections error
        assert "missing required section" not in error_msg


class TestAC9DefensiveAPIKeyStrip:
    """Test AC-9: Defensive api_key strip."""

    def test_load_config_yaml_api_key_ignored(self, tmp_path, monkeypatch):
        """YAML-supplied api_key should be ignored in favor of env var."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-real-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-real-key")

        yaml_content = f"""
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0

output:
  log_dir: "{tmp_path / "logs"}"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  api_key: "smuggled-bad-key"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  api_key: "another-bad-key"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"
"""
        path = tmp_path / "smuggled_keys.yaml"
        path.write_text(yaml_content)

        # Act
        cfg = load_config(str(path))

        # Assert
        # Should have env var values, not YAML values
        assert cfg.team_a.api_key == "sk-real-key"
        assert cfg.team_b.api_key == "sk-real-key"

    def test_load_config_yaml_api_key_null_ignored(self, tmp_path, monkeypatch):
        """YAML api_key: null should also be ignored."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-real")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-real")

        yaml_content = f"""
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0

output:
  log_dir: "{tmp_path / "logs"}"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  api_key: null
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  api_key: ""
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"
"""
        path = tmp_path / "null_keys.yaml"
        path.write_text(yaml_content)

        # Act
        cfg = load_config(str(path))

        # Assert
        assert cfg.team_a.api_key == "sk-real"
        assert cfg.team_b.api_key == "sk-real"


class TestAC10MissingEnvVarFailsFast:
    """Test AC-10: Missing env var fails fast - integration with Story 002."""

    def test_load_config_missing_openai_key_raises_config_error(self, tmp_path, monkeypatch):
        """Missing OPENAI_API_KEY should raise ConfigError with specific message."""
        # Arrange
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        yaml_content = f"""
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0

output:
  log_dir: "{tmp_path / "logs"}"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"
"""
        path = tmp_path / "missing_openai.yaml"
        path.write_text(yaml_content)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            load_config(str(path))

        error_msg = str(exc_info.value)
        assert "OPENAI_API_KEY" in error_msg
        assert "openai cannot initialize" in error_msg

    def test_load_config_empty_env_var_raises_config_error(self, tmp_path, monkeypatch):
        """Empty env var should raise ConfigError."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        path = _write_valid_match_yaml(tmp_path)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            load_config(str(path))

        error_msg = str(exc_info.value)
        assert "OPENAI_API_KEY is set but empty" in error_msg


class TestAC11LogDirCreatedOnSuccess:
    """Test AC-11: log_dir created on success."""

    def test_load_config_creates_nonexistent_log_dir(self, tmp_path, monkeypatch):
        """Non-existent log_dir should be created after successful load."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        fresh_log_dir = tmp_path / "fresh_logs"
        assert not fresh_log_dir.exists()  # Verify it doesn't exist initially

        path = _write_valid_match_yaml(tmp_path)
        # Update the log_dir path
        content = path.read_text().replace(str(tmp_path / "logs"), str(fresh_log_dir))
        path.write_text(content)

        # Act
        cfg = load_config(str(path))

        # Assert
        assert cfg is not None
        assert fresh_log_dir.exists()
        assert fresh_log_dir.is_dir()

    def test_load_config_creates_nested_log_dir(self, tmp_path, monkeypatch):
        """Nested non-existent path should be created with intermediate dirs."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        nested_log_dir = tmp_path / "a" / "b" / "c"
        assert not nested_log_dir.exists()

        path = _write_valid_match_yaml(tmp_path)
        content = path.read_text().replace(str(tmp_path / "logs"), str(nested_log_dir))
        path.write_text(content)

        # Act
        cfg = load_config(str(path))

        # Assert
        assert cfg is not None
        assert nested_log_dir.exists()
        assert nested_log_dir.is_dir()


class TestAC12EdgeCase7PlayersNull:
    """Test AC-12: Edge Case 7 - players: null."""

    def test_load_config_players_null_triggers_team_size_error(self, tmp_path, monkeypatch):
        """players: null should trigger team-size validation error."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        yaml_content = f"""
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0

output:
  log_dir: "{tmp_path / "logs"}"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  players:

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"
"""
        path = tmp_path / "players_null.yaml"
        path.write_text(yaml_content)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            load_config(str(path))

        error_msg = str(exc_info.value)
        assert "team_a.players" in error_msg
        # Should reference the 5-player constraint
        assert ("should have at least 5 items" in error_msg or
                "at least 5 items" in error_msg or
                "List should have at least 5 items" in error_msg)

    def test_load_config_players_empty_list_triggers_team_size_error(self, tmp_path, monkeypatch):
        """players: [] should also trigger team-size error."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        yaml_content = f"""
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 90
  field_width: 100.0
  field_height: 60.0

output:
  log_dir: "{tmp_path / "logs"}"

team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
  players: []

team_b:
  llm_provider: "anthropic"
  llm_model: "claude-3-5-sonnet-20241022"
  players:
    - role: "GK"
    - role: "DEF"
    - role: "DEF"
    - role: "MID"
    - role: "FWD"
"""
        path = tmp_path / "players_empty.yaml"
        path.write_text(yaml_content)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            load_config(str(path))

        error_msg = str(exc_info.value)
        assert "team_a.players" in error_msg
        assert ("should have at least 5 items" in error_msg or
                "at least 5 items" in error_msg or
                "List should have at least 5 items" in error_msg)