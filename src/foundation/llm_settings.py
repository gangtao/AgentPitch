"""
Global LLM settings management for Agent Pitch.

This module provides the global LLM configuration source for CGP and PMEP
after the ADR-0021 migration that removes llm_provider/llm_model from TeamConfig.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml


class LLMSettingsError(Exception):
    """Raised when LLM settings cannot be loaded or are invalid."""
    pass


def load_llm_settings(data_home: Path) -> Dict:
    """Load LLM settings from <DATA_HOME>/llm-providers.yaml.

    Args:
        data_home: Path to the data directory

    Returns:
        Dictionary with 'providers' and 'active' keys. Empty defaults if file missing.

    Example return:
        {
            "providers": {
                "openai": {"url": "https://api.openai.com/v1"},
                "anthropic": {"url": "https://api.anthropic.com"}
            },
            "active": {"provider": "openai", "model": "gpt-4o"}
        }
    """
    settings_path = data_home / "llm-providers.yaml"

    if not settings_path.exists():
        return {
            "providers": {},
            "active": None
        }

    try:
        with open(settings_path, 'r') as f:
            data = yaml.safe_load(f) or {}

        # Ensure required structure exists
        if not isinstance(data, dict):
            data = {}

        # Support both formats:
        #   nested: {providers: {openai: ...}, active: {...}}  (original design)
        #   flat:   {openai: {...}, anthropic: {...}}           (written by LLM tab)
        if "providers" in data:
            providers = data.get("providers") or {}
            active = data.get("active")
        else:
            providers = {k: v for k, v in data.items() if k != "active"}
            active = data.get("active")

        return {
            "providers": providers,
            "active": active
        }
    except (yaml.YAMLError, FileNotFoundError, OSError) as e:
        warnings.warn(f"Failed to load LLM settings from {settings_path}: {e}")
        return {
            "providers": {},
            "active": None
        }


def get_default_provider(data_home: Path) -> str:
    """Get the active provider name, or 'openai' as fallback.

    Args:
        data_home: Path to the data directory

    Returns:
        Provider name string (e.g., "openai", "anthropic")
    """
    settings = load_llm_settings(data_home)

    if settings["active"] and isinstance(settings["active"], dict):
        provider = settings["active"].get("provider")
        if provider:
            return provider

    # Fallback: use first available provider, or "openai" as ultimate fallback
    if settings["providers"]:
        return list(settings["providers"].keys())[0]

    return "openai"


def get_default_model(data_home: Path, provider: Optional[str] = None) -> str:
    """Get the model for the specified provider, or a sensible default.

    Args:
        data_home: Path to the data directory
        provider: Provider name. If None, uses the default provider.

    Returns:
        Model name string (e.g., "gpt-4o", "claude-sonnet-4-6")
    """
    if provider is None:
        provider = get_default_provider(data_home)

    settings = load_llm_settings(data_home)

    # Check active settings first
    if (settings["active"] and
        isinstance(settings["active"], dict) and
        settings["active"].get("provider") == provider):
        model = settings["active"].get("model")
        if model:
            return model

    # Check provider-specific settings
    if provider in settings["providers"]:
        provider_config = settings["providers"][provider]
        if isinstance(provider_config, dict):
            model = provider_config.get("model")
            if model:
                return model

    # Sensible per-provider defaults
    provider_defaults = {
        "openai": "gpt-4o",
        "anthropic": "claude-sonnet-4-6",
        "gemini": "gemini-2.0-flash",
    }

    return provider_defaults.get(provider, "gpt-4o")


def get_team_llm_settings(team_config, data_home: Path) -> Tuple[str, str]:
    """Get LLM provider and model for a team, with deprecation fallback.

    This function handles the ADR-0021 v1 migration by falling back to
    deprecated team-level fields if global settings are unavailable.

    Args:
        team_config: TeamConfig instance (may have deprecated llm_provider/llm_model)
        data_home: Path to the data directory

    Returns:
        Tuple of (provider, model) strings

    Raises:
        LLMSettingsError: If no valid settings found anywhere
    """
    # ADR-0021 graceful migration: team-level fields WIN if explicitly set
    # (researcher knows what they wanted for that match). Otherwise fall through
    # to global LLM-tab settings.
    team_provider = getattr(team_config, "llm_provider", None)
    if team_provider is not None:
        # Deprecated path — emit warning so the user migrates eventually.
        # (TeamConfig's own model_validator already warns once at construction;
        # this second warning here is redundant — skip it to avoid double-warn.)
        provider = team_provider
        model = getattr(team_config, "llm_model", None) or get_default_model(
            data_home, provider
        )
        return (provider, model)

    # New path: read from <DATA_HOME>/llm-providers.yaml
    try:
        provider = get_default_provider(data_home)
        model = get_default_model(data_home, provider)
        return (provider, model)
    except Exception as e:
        raise LLMSettingsError(
            "No LLM settings found. Configure global settings via the Config UX "
            f"LLM tab, or set llm_provider/llm_model in the match config: {e}"
        )