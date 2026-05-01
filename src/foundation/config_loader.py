"""YAML configuration file parser and load orchestrator for the Agent Pitch project.

Phase 1-3 of the configuration loading pipeline:
- Phase 1: YAML parsing with comprehensive error handling
- Phase 2: Section validation and preprocessing (role defaults, player IDs, API keys)
- Phase 3: Pydantic model validation and log_dir creation
"""

from __future__ import annotations

import os
import yaml
from typing import Any
from pydantic import ValidationError

from src.foundation.config_errors import ConfigError


def parse_yaml(path: str) -> dict[str, Any]:
    """Phase 1 of the config load pipeline. Returns the raw parsed YAML as a dict.

    Raises ConfigError on:
      - File not found
      - Permission denied
      - Empty file (yaml.safe_load returns None)
      - YAML syntax errors
      - Top-level YAML that is not a mapping
    """
    # Distinguish "not found" from "exists but unreadable" before opening
    if not os.path.exists(path):
        raise ConfigError(f"Config file not found: {path}")
    if not os.access(path, os.R_OK):
        raise ConfigError(f"Config file is not readable (permission denied): {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except PermissionError as e:
        # Defensive — os.access can race; surface the same message
        raise ConfigError(f"Config file is not readable (permission denied): {path}") from e
    except yaml.YAMLError as e:
        line = _extract_yaml_line(e)
        line_str = f":{line}" if line is not None else ""
        raise ConfigError(f"Config parse error at {path}{line_str}: {e}") from e

    if raw is None:
        raise ConfigError(f"Config file is empty: {path}")
    if not isinstance(raw, dict):
        raise ConfigError(
            f"Config file must be a YAML mapping, got {type(raw).__name__}: {path}"
        )
    return raw


def _extract_yaml_line(exc: yaml.YAMLError) -> int | None:
    """Pull line number from a yaml.YAMLError if available (1-indexed)."""
    mark = getattr(exc, "problem_mark", None)
    if mark is None:
        return None
    # PyYAML's mark.line is 0-indexed; convert to 1-indexed for human messages.
    return mark.line + 1


# Required top-level sections for a valid match configuration
REQUIRED_SECTIONS = ("match", "output", "team_a", "team_b")


def load_config(path: str) -> "MatchConfig":
    """Single public entry point. Loads, validates, returns immutable MatchConfig.

    Orchestrates the three-phase configuration loading pipeline:
    1. Parse YAML file (parse_yaml)
    2. Validate sections and preprocess (apply defaults, assign IDs, read API keys)
    3. Validate via Pydantic models and create log_dir

    Raises ConfigError for any failure. Caller (CLI Orchestrator) prints message
    to stderr and exits with code 1.

    Args:
        path: Filesystem path to YAML configuration file

    Returns:
        Immutable MatchConfig instance ready for simulation use
    """
    # Import here to avoid circular imports
    from src.foundation.config_models import MatchConfig

    # Phase 1: Parse YAML
    raw = parse_yaml(path)

    # Phase 2: Preprocess (section checks first, then per-team transformation)
    _check_required_sections(raw, path)
    preprocessed = _preprocess(raw)

    # Phase 3: Validate via Pydantic
    try:
        cfg = MatchConfig(**preprocessed)
    except ValidationError as e:
        raise ConfigError(_format_validation_error(e)) from e

    # Post-validation side effect: ensure log_dir exists
    _ensure_log_dir(cfg.output.log_dir)
    return cfg


def _check_required_sections(raw: dict, path: str) -> None:
    """Validate that all required top-level sections are present in the configuration.

    Args:
        raw: Parsed YAML as a dict
        path: Original file path for error messaging

    Raises:
        ConfigError: If any required section is missing
    """
    for section in REQUIRED_SECTIONS:
        if section not in raw:
            raise ConfigError(f"{os.path.basename(path)} is missing required section: {section}")


def _preprocess(raw: dict) -> dict:
    """Apply role defaults, assign player IDs, read API keys per team.

    Transforms the raw parsed YAML into a structure ready for Pydantic validation:
    - Applies role-based attribute defaults for players
    - Assigns player_id by position (team_a_0, team_a_1, etc.)
    - Reads API keys from environment variables
    - Strips any YAML-supplied api_key values (defensive)

    Args:
        raw: Parsed YAML dict with all required sections

    Returns:
        Preprocessed dict ready for MatchConfig construction
    """
    from src.foundation.config_preprocessor import (
        apply_role_defaults, assign_player_ids, read_api_key
    )

    out: dict = {"match": raw["match"], "output": raw["output"]}
    # Preserve the optional simulation section if present. Without this,
    # YAML-supplied simulation overrides (e.g. formation_snap_enabled,
    # min_player_separation) would be silently dropped — fall back to
    # SimulationConfig defaults regardless of what the user wrote.
    if "simulation" in raw:
        out["simulation"] = raw["simulation"]
    for team_id in ("team_a", "team_b"):
        team_raw = dict(raw[team_id])  # shallow copy so we don't mutate input
        team_raw.pop("api_key", None)  # defensive: never trust YAML-supplied api_key
        provider = team_raw.get("llm_provider")
        team_raw["api_key"] = read_api_key(provider) if provider else ""
        raw_players = team_raw.get("players")
        ided = assign_player_ids(team_id, raw_players)
        team_raw["players"] = [
            {**apply_role_defaults(p, p.get("role", "")), "player_id": p["player_id"]}
            for p in ided
        ]
        out[team_id] = team_raw
    return out


def _format_validation_error(e: ValidationError) -> str:
    """Convert Pydantic v2 ValidationError to a single field-path-prefixed message.

    Uses only the first error for fail-fast behavior per ADR-0003.

    Args:
        e: Pydantic ValidationError containing one or more validation failures

    Returns:
        Human-readable error message with field path prefix
    """
    errors = e.errors()
    if not errors:
        return str(e)
    first = errors[0]
    loc = ".".join(str(x) for x in first["loc"])
    msg = first["msg"]
    return f"{loc}: {msg}"


def _ensure_log_dir(log_dir: str) -> None:
    """Create the log directory if it doesn't exist.

    Called only after successful configuration validation to avoid side effects
    from invalid configurations.

    Args:
        log_dir: Directory path to create

    Raises:
        ConfigError: If directory creation fails due to permissions or filesystem errors
    """
    try:
        os.makedirs(log_dir, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise ConfigError(f"Cannot create log directory {log_dir}: {e}") from e