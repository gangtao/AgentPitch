"""Secrets file storage abstraction per ADR-0020."""
from __future__ import annotations
import json
import os
import stat
import tempfile
import warnings
from pathlib import Path
from typing import Literal


# Environment variable mappings for built-in providers
ENV_VAR_MAP: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GOOGLE_API_KEY",
}


def load_secrets(data_home: Path) -> dict[str, dict]:
    """Load secrets from <DATA_HOME>/.secrets.json.

    Args:
        data_home: DATA_HOME directory path

    Returns:
        Dict mapping provider names to secret data.
        Format: {provider: {api_key: str}}
        Returns empty dict if file missing or malformed.

    Side Effects:
        - Logs warning if file is malformed JSON
        - Auto-fixes file permissions if not 0600
    """
    secrets_path = data_home / ".secrets.json"

    if not secrets_path.exists():
        return {}

    try:
        # Check file permissions and auto-fix if needed
        current_mode = stat.S_IMODE(secrets_path.stat().st_mode)
        if current_mode != 0o600:
            warnings.warn(f"Secrets file {secrets_path} has mode {oct(current_mode)}, fixing to 0600")
            os.chmod(secrets_path, 0o600)

        with open(secrets_path, 'r') as f:
            data = json.load(f)

        # Validate structure - should have "providers" key
        if not isinstance(data, dict):
            warnings.warn(f"Secrets file {secrets_path} is not a valid JSON object")
            return {}

        providers = data.get("providers", {})
        if not isinstance(providers, dict):
            warnings.warn(f"Secrets file {secrets_path} providers section is not a valid object")
            return {}

        return providers

    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
        warnings.warn(f"Could not load secrets file {secrets_path}: {e}")
        return {}


def save_secrets(data_home: Path, secrets: dict) -> None:
    """Save secrets to <DATA_HOME>/.secrets.json atomically.

    Args:
        data_home: DATA_HOME directory path
        secrets: Dict mapping provider names to secret data

    Side Effects:
        - Creates data_home directory if it doesn't exist
        - Writes file with mode 0600
        - Uses atomic temp+replace pattern

    Raises:
        OSError: On file write or permission errors
    """
    data_home.mkdir(parents=True, exist_ok=True)
    secrets_path = data_home / ".secrets.json"

    # Structure as per ADR-0020 spec
    data = {"providers": secrets}

    # Atomic write using temp file + os.replace
    with tempfile.NamedTemporaryFile(
        mode='w',
        dir=data_home,
        prefix='.secrets.json.tmp',
        delete=False
    ) as tmp_file:
        json.dump(data, tmp_file, indent=2)
        tmp_file.flush()
        os.fsync(tmp_file.fileno())  # Force write to disk
        tmp_path = Path(tmp_file.name)

    try:
        # Set permissions on temp file before moving
        os.chmod(tmp_path, 0o600)

        # Atomic replace
        os.replace(tmp_path, secrets_path)

        # Verify final permissions
        os.chmod(secrets_path, 0o600)

    except Exception:
        # Clean up temp file on any error
        tmp_path.unlink(missing_ok=True)
        raise


def get_api_key(data_home: Path, provider: str) -> str | None:
    """Get API key with environment variable precedence per ADR-0020.

    Args:
        data_home: DATA_HOME directory path
        provider: Provider name (built-in or custom)

    Returns:
        API key from env var (if set) OR secrets file (if exists) OR None

    Precedence order (built-in providers only):
        1. Environment variable (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)
        2. Secrets file (<DATA_HOME>/.secrets.json)
        3. None (unset)

    Custom providers (not in ENV_VAR_MAP) only check the secrets file.
    """
    env_var_name = ENV_VAR_MAP.get(provider)

    # Check environment variable first (only for built-in providers)
    if env_var_name:
        env_value = os.environ.get(env_var_name)
        if env_value:
            return env_value.strip()

    # Check secrets file (works for ALL providers including custom)
    secrets = load_secrets(data_home)
    provider_data = secrets.get(provider, {})
    if isinstance(provider_data, dict):
        api_key = provider_data.get("api_key")
        if api_key and isinstance(api_key, str):
            return api_key.strip()

    return None


def get_key_source(data_home: Path, provider: str) -> Literal["env", "secrets_file", "unset"]:
    """Determine the source of an API key for debugging/UI purposes.

    Args:
        data_home: DATA_HOME directory path
        provider: Provider name (built-in or custom)

    Returns:
        Source of the key: "env", "secrets_file", or "unset"

    Custom providers can only return "secrets_file" or "unset" (no env var support).
    """
    env_var_name = ENV_VAR_MAP.get(provider)

    # Check if env var is set (only for built-in providers)
    if env_var_name:
        env_value = os.environ.get(env_var_name)
        if env_value and env_value.strip():
            return "env"

    # Check if secrets file has the key
    secrets = load_secrets(data_home)
    provider_data = secrets.get(provider, {})
    if isinstance(provider_data, dict):
        api_key = provider_data.get("api_key")
        if api_key and isinstance(api_key, str) and api_key.strip():
            return "secrets_file"

    return "unset"


def get_key_status(data_home: Path, provider: str) -> Literal["set", "unset", "env_overridden"]:
    """Get key status for HTTP API responses.

    Args:
        data_home: DATA_HOME directory path
        provider: Provider name (built-in or custom)

    Returns:
        Status for UI display:
        - "set": Key available from effective source
        - "unset": No key available from any source
        - "env_overridden": Both env var AND secrets file have values (env wins)

    Custom providers can only return "set" or "unset" (no env var support).
    """
    env_var_name = ENV_VAR_MAP.get(provider)

    # Check both sources
    has_env = False
    if env_var_name:
        env_value = os.environ.get(env_var_name)
        has_env = env_value and env_value.strip()

    secrets = load_secrets(data_home)
    provider_data = secrets.get(provider, {})
    has_secrets = False
    if isinstance(provider_data, dict):
        api_key = provider_data.get("api_key")
        has_secrets = api_key and isinstance(api_key, str) and api_key.strip()

    # Determine status
    if has_env and has_secrets:
        return "env_overridden"
    elif has_env or has_secrets:
        return "set"
    else:
        return "unset"