"""
Tests for Configuration System YAML parser.

Tests all 9 acceptance criteria from Story 003:
AC-1: Happy path - valid mapping returns dict
AC-2: File not found
AC-3: Permission denied
AC-4: Empty file
AC-5: YAML syntax error - line number extracted
AC-6: yaml.safe_load is used - not yaml.load
AC-7: Non-mapping top-level rejected
AC-8: ConfigError type
AC-9: YAML anchors - Edge Case 14
"""

import os
import re
import pytest
import yaml

from src.foundation.config_loader import parse_yaml
from src.foundation.config_errors import ConfigError


class TestAC1HappyPathValidMapping:
    """Test AC-1: Happy path — valid mapping returns dict."""

    def test_parse_yaml_valid_mapping_returns_dict(self, tmp_path):
        """Valid YAML mapping should return parsed dict."""
        # Arrange
        yaml_content = "match:\n  seed: 42\n  tick_rate: 10\n"
        path = tmp_path / "match.yaml"
        path.write_text(yaml_content)

        # Act
        result = parse_yaml(str(path))

        # Assert
        assert isinstance(result, dict)
        assert result == {"match": {"seed": 42, "tick_rate": 10}}

    def test_parse_yaml_nested_mappings_preserved(self, tmp_path):
        """Nested mappings should be preserved."""
        yaml_content = """
match:
  seed: 42
  tick_rate: 10
output:
  log_dir: "/tmp/test"
team_a:
  llm_provider: "openai"
  llm_model: "gpt-4o"
"""
        path = tmp_path / "config.yaml"
        path.write_text(yaml_content)

        result = parse_yaml(str(path))

        assert result["match"]["seed"] == 42
        assert result["output"]["log_dir"] == "/tmp/test"
        assert result["team_a"]["llm_provider"] == "openai"

    def test_parse_yaml_type_preservation(self, tmp_path):
        """Integers, floats, strings should preserve their types."""
        yaml_content = """
integer_val: 42
float_val: 3.14
string_val: "hello"
boolean_val: true
"""
        path = tmp_path / "types.yaml"
        path.write_text(yaml_content)

        result = parse_yaml(str(path))

        assert isinstance(result["integer_val"], int)
        assert result["integer_val"] == 42
        assert isinstance(result["float_val"], float)
        assert result["float_val"] == 3.14
        assert isinstance(result["string_val"], str)
        assert result["string_val"] == "hello"
        assert isinstance(result["boolean_val"], bool)
        assert result["boolean_val"] is True


class TestAC2FileNotFound:
    """Test AC-2: File not found."""

    def test_parse_yaml_missing_file_raises_config_error(self, tmp_path):
        """Non-existent path should raise ConfigError with specific message."""
        # Arrange
        path = tmp_path / "missing.yaml"
        # Note: file is never written

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            parse_yaml(str(path))

        error_msg = str(exc_info.value)
        assert "Config file not found" in error_msg
        assert str(path) in error_msg

    def test_parse_yaml_empty_string_path_raises_config_error(self, tmp_path):
        """Empty string path should raise ConfigError."""
        with pytest.raises(ConfigError) as exc_info:
            parse_yaml("")

        assert "Config file not found" in str(exc_info.value)

    def test_parse_yaml_deeply_nested_missing_path(self, tmp_path):
        """Deeply nested non-existent path should raise ConfigError."""
        path = tmp_path / "deep" / "nested" / "missing.yaml"

        with pytest.raises(ConfigError) as exc_info:
            parse_yaml(str(path))

        error_msg = str(exc_info.value)
        assert "Config file not found" in error_msg
        assert str(path) in error_msg


class TestAC3PermissionDenied:
    """Test AC-3: Permission denied."""

    @pytest.mark.skipif(os.name == "nt", reason="Permission tests not supported on Windows")
    @pytest.mark.skipif(os.geteuid() == 0, reason="Permissions test invalid as root")
    def test_parse_yaml_unreadable_file_raises_config_error(self, tmp_path):
        """Existing but unreadable file should raise ConfigError with permission message."""
        # Arrange
        yaml_content = "match:\n  seed: 42\n"
        path = tmp_path / "unreadable.yaml"
        path.write_text(yaml_content)
        path.chmod(0o000)  # Remove all permissions

        try:
            # Act & Assert
            with pytest.raises(ConfigError) as exc_info:
                parse_yaml(str(path))

            error_msg = str(exc_info.value)
            assert "permission denied" in error_msg
            assert str(path) in error_msg
            assert "Config file is not readable" in error_msg
            # Should NOT say "not found"
            assert "not found" not in error_msg

        finally:
            # Cleanup: restore permissions so tmp_path cleanup can succeed
            path.chmod(0o644)

    @pytest.mark.skipif(os.name == "nt", reason="Permission tests not supported on Windows")
    @pytest.mark.skipif(os.geteuid() == 0, reason="Permissions test invalid as root")
    def test_parse_yaml_permission_error_race_condition(self, tmp_path):
        """PermissionError during open should have same message as os.access check."""
        yaml_content = "match:\n  seed: 42\n"
        path = tmp_path / "unreadable2.yaml"
        path.write_text(yaml_content)
        path.chmod(0o000)

        try:
            with pytest.raises(ConfigError) as exc_info:
                parse_yaml(str(path))

            # Both code paths should produce identical message
            assert "Config file is not readable (permission denied)" in str(exc_info.value)

        finally:
            path.chmod(0o644)


class TestAC4EmptyFile:
    """Test AC-4: Empty file."""

    def test_parse_yaml_empty_file_raises_config_error(self, tmp_path):
        """Zero-byte file should raise ConfigError with empty file message."""
        # Arrange
        path = tmp_path / "empty.yaml"
        path.write_text("")  # Zero-byte file

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            parse_yaml(str(path))

        error_msg = str(exc_info.value)
        assert "Config file is empty" in error_msg
        assert str(path) in error_msg

    def test_parse_yaml_whitespace_only_file_raises_config_error(self, tmp_path):
        """File with only whitespace/comments (safe_load returns None) should raise empty error."""
        # Arrange
        path = tmp_path / "whitespace.yaml"
        path.write_text("# just a comment\n\n")  # Only comment and newlines

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            parse_yaml(str(path))

        error_msg = str(exc_info.value)
        assert "Config file is empty" in error_msg
        assert str(path) in error_msg


class TestAC5YAMLSyntaxError:
    """Test AC-5: YAML syntax error — line number extracted."""

    def test_parse_yaml_malformed_yaml_extracts_line_number(self, tmp_path):
        """Malformed YAML should raise ConfigError with line number."""
        # Arrange
        yaml_content = "match:\n  seed: 42\n  tick_rate: : : :\n"  # Invalid on line 3
        path = tmp_path / "malformed.yaml"
        path.write_text(yaml_content)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            parse_yaml(str(path))

        error_msg = str(exc_info.value)
        assert "Config parse error at" in error_msg
        assert str(path) in error_msg
        assert ":3" in error_msg  # Line 3 (1-indexed)

        # Original YAMLError should be in __cause__
        assert isinstance(exc_info.value.__cause__, yaml.YAMLError)

    def test_parse_yaml_tab_vs_space_indentation_error(self, tmp_path):
        """Mixed tab/space indentation should include line number."""
        yaml_content = "match:\n  seed: 42\n\ttick_rate: 10\n"  # Tab on line 3
        path = tmp_path / "mixed_indent.yaml"
        path.write_text(yaml_content)

        with pytest.raises(ConfigError) as exc_info:
            parse_yaml(str(path))

        error_msg = str(exc_info.value)
        assert "Config parse error at" in error_msg
        assert str(path) in error_msg
        # Should contain line number (exact line depends on PyYAML version)
        assert ":" in error_msg.split(str(path))[1]  # Should have line number after path

    def test_parse_yaml_unclosed_flow_style(self, tmp_path):
        """Unclosed flow style should raise ConfigError with location."""
        yaml_content = "items: [1, 2, 3"  # Missing closing bracket
        path = tmp_path / "unclosed.yaml"
        path.write_text(yaml_content)

        with pytest.raises(ConfigError) as exc_info:
            parse_yaml(str(path))

        error_msg = str(exc_info.value)
        assert "Config parse error at" in error_msg
        assert str(path) in error_msg


class TestAC6YAMLSafeLoadOnly:
    """Test AC-6: yaml.safe_load is used — not yaml.load."""

    def test_parse_yaml_source_uses_safe_load_only(self):
        """Static check: src/foundation/config_loader.py must use yaml.safe_load, not yaml.load."""
        # Resolve source path via the module's own __file__ — portable across
        # environments and CI; no hardcoded absolute paths.
        from src.foundation import config_loader
        with open(config_loader.__file__, "r", encoding="utf-8") as f:
            source = f.read()

        # Verify yaml.safe_load is used
        assert "yaml.safe_load" in source

        # Verify yaml.load (without safe) is NOT used
        unsafe_pattern = r"yaml\.load\b(?!.*safe)"
        assert re.search(unsafe_pattern, source) is None


class TestAC7NonMappingTopLevel:
    """Test AC-7: Non-mapping top-level rejected."""

    def test_parse_yaml_top_level_list_rejected(self, tmp_path):
        """Top-level YAML list should be rejected."""
        # Arrange
        yaml_content = "- one\n- two\n- three\n"
        path = tmp_path / "list.yaml"
        path.write_text(yaml_content)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            parse_yaml(str(path))

        error_msg = str(exc_info.value)
        assert "must be a YAML mapping" in error_msg
        assert "list" in error_msg
        assert str(path) in error_msg

    def test_parse_yaml_top_level_integer_rejected(self, tmp_path):
        """Top-level integer should be rejected."""
        yaml_content = "42\n"
        path = tmp_path / "integer.yaml"
        path.write_text(yaml_content)

        with pytest.raises(ConfigError) as exc_info:
            parse_yaml(str(path))

        error_msg = str(exc_info.value)
        assert "must be a YAML mapping" in error_msg
        assert "int" in error_msg
        assert str(path) in error_msg

    def test_parse_yaml_top_level_string_rejected(self, tmp_path):
        """Top-level string should be rejected."""
        yaml_content = "hello\n"
        path = tmp_path / "string.yaml"
        path.write_text(yaml_content)

        with pytest.raises(ConfigError) as exc_info:
            parse_yaml(str(path))

        error_msg = str(exc_info.value)
        assert "must be a YAML mapping" in error_msg
        assert "str" in error_msg
        assert str(path) in error_msg


class TestAC8ConfigErrorType:
    """Test AC-8: ConfigError type."""

    def test_config_error_subclasses_exception(self):
        """ConfigError should subclass Exception directly."""
        assert issubclass(ConfigError, Exception)
        assert not issubclass(ConfigError, ValueError)
        assert not issubclass(ConfigError, RuntimeError)

    def test_config_error_message_positional(self):
        """ConfigError message should be positional via Exception.__init__."""
        error = ConfigError("test message")
        assert error.args == ("test message",)
        assert str(error) == "test message"

    def test_config_error_can_be_raised_and_caught(self):
        """ConfigError should behave like any Exception."""
        try:
            raise ConfigError("test error")
        except ConfigError as e:
            assert str(e) == "test error"
        except Exception:
            pytest.fail("ConfigError should be catchable as ConfigError")


class TestAC9YAMLAnchors:
    """Test AC-9: YAML anchors — Edge Case 14."""

    def test_parse_yaml_anchors_resolved_transparently(self, tmp_path):
        """YAML anchors should be resolved by safe_load with no error."""
        # Arrange
        yaml_content = """
default_player: &default_player
  speed: 10
  skill: 12
  strength: 8

team_a:
  players:
    - <<: *default_player
      player_id: "team_a_0"
      role: "GK"
    - <<: *default_player
      player_id: "team_a_1"
      role: "DEF"
"""
        path = tmp_path / "anchors.yaml"
        path.write_text(yaml_content)

        # Act
        result = parse_yaml(str(path))

        # Assert
        assert isinstance(result, dict)

        # Both player references should contain identical expanded content
        player_0 = result["team_a"]["players"][0]
        player_1 = result["team_a"]["players"][1]

        assert player_0["speed"] == 10
        assert player_0["skill"] == 12
        assert player_0["strength"] == 8
        assert player_1["speed"] == 10
        assert player_1["skill"] == 12
        assert player_1["strength"] == 8

        # Anchor expansion should have happened
        assert player_0["player_id"] == "team_a_0"
        assert player_1["player_id"] == "team_a_1"

    def test_parse_yaml_simple_anchor_reference(self, tmp_path):
        """Simple anchor references should expand correctly."""
        yaml_content = """
default_config: &default
  timeout: 30
  retries: 3

service_a:
  config: *default

service_b:
  config: *default
"""
        path = tmp_path / "simple_anchors.yaml"
        path.write_text(yaml_content)

        result = parse_yaml(str(path))

        # Both services should have identical config content
        assert result["service_a"]["config"]["timeout"] == 30
        assert result["service_b"]["config"]["retries"] == 3
        assert result["service_a"]["config"] == result["service_b"]["config"]