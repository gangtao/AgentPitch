"""Configuration preprocessor for the Agent Pitch project.

Phase 2 of the configuration loading pipeline. Applies role defaults, assigns
player IDs, and reads API keys from environment variables.
"""

from __future__ import annotations

import os
from typing import Any


ROLE_DEFAULTS: dict[str, dict[str, int]] = {
    "GK": {"speed": 8, "skill": 10, "strength": 8, "save": 16, "discipline": 14, "dribbling": 4},
    "DEF": {"speed": 12, "skill": 8, "strength": 16, "save": 0, "discipline": 16, "dribbling": 6},
    "MID": {"speed": 14, "skill": 16, "strength": 10, "save": 0, "discipline": 14, "dribbling": 12},
    "FWD": {"speed": 16, "skill": 14, "strength": 14, "save": 0, "discipline": 10, "dribbling": 16},
}


PROVIDER_ENV_KEYS: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GOOGLE_API_KEY",
}


def apply_role_defaults(raw_player: dict[str, Any], role: str) -> dict[str, Any]:
    """Fill omitted/None numeric attributes from ROLE_DEFAULTS[role]. Pure function."""
    if role not in ROLE_DEFAULTS:
        # Let Pydantic surface the role-validity error in Phase 3; just pass through.
        return {**raw_player, "role": role}

    defaults = ROLE_DEFAULTS[role]
    result: dict[str, Any] = {"role": role}

    for key, default_value in defaults.items():
        raw_value = raw_player.get(key)
        result[key] = raw_value if raw_value is not None else default_value

    # Preserve any non-None values that aren't in defaults (e.g., player_id)
    for key, value in raw_player.items():
        if key != "role" and key not in defaults and value is not None:
            result[key] = value

    return result


def assign_player_ids(team_id: str, raw_players: list[dict] | None) -> list[dict]:
    """Insert player_id by list position. Returns a new list; does not mutate input."""
    if raw_players is None:
        return []
    return [{**p, "player_id": f"{team_id}_{i}"} for i, p in enumerate(raw_players)]


def read_api_key(provider: str) -> str:
    """Read API key from environment variable. Empty/whitespace treated as missing.

    Raises ConfigError (defined in Story 003) on missing key.
    """
    from src.foundation.config_errors import ConfigError  # imported lazily; defined in Story 003

    env_key = PROVIDER_ENV_KEYS.get(provider)
    if env_key is None:
        raise ConfigError(f"Unknown provider: {provider!r}")

    raw = os.environ.get(env_key, "").strip()
    if raw == "":
        raise ConfigError(
            f"{env_key} is set but empty — provider {provider} cannot initialize"
            if env_key in os.environ
            else f"{env_key} is not set — provider {provider} cannot initialize"
        )
    return raw


def apply_player_name_default(raw_player: dict[str, Any], index: int) -> dict[str, Any]:
    """Return a copy of `raw_player` with a non-empty `name`.

    Missing / None / empty / whitespace-only names become `"Player {index+1}"`.
    Pure function; does not mutate input.
    """
    name = raw_player.get("name")
    if not isinstance(name, str) or name.strip() == "":
        name = f"Player {index + 1}"
    return {**raw_player, "name": name}