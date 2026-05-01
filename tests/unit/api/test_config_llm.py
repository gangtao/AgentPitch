"""Tests for config LLM tab API endpoints (per ADR-0019 + ADR-0020)."""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app
from src.secrets_store import (
    load_secrets,
    save_secrets,
    get_api_key,
    get_key_status,
)


@pytest.fixture
def temp_data_home(tmp_path):
    """Use a clean tmp dir as DATA_HOME for each test."""
    return tmp_path


@pytest.fixture
def client(temp_data_home):
    app = create_app(log_dir=str(temp_data_home))
    return TestClient(app)


@pytest.fixture(autouse=True)
def _clear_env_vars(monkeypatch):
    """Default to NO env vars set; tests opt in via monkeypatch.setenv."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/config — LLM section shape
# ──────────────────────────────────────────────────────────────────────────────


def test_api_config_llm_section_returns_providers_with_key_status(client):
    """GET /api/config exposes llm.providers list, each with key_status."""
    response = client.get("/api/config")
    assert response.status_code == 200

    llm = response.json()["llm"]
    assert "providers" in llm
    assert isinstance(llm["providers"], list)

    for provider in llm["providers"]:
        assert "name" in provider
        assert "key_status" in provider
        assert provider["key_status"] in ("set", "unset", "env_overridden")
        # CRITICAL: never expose plaintext key
        assert "key" not in provider


def test_api_config_llm_no_plaintext_key_when_secrets_file_set(
    client, temp_data_home
):
    """Even with a secrets file present, GET /api/config returns key_status, not the key."""
    save_secrets(
        temp_data_home, {"openai": {"api_key": "sk-secret-must-not-leak"}}
    )

    response = client.get("/api/config")
    body = json.dumps(response.json())
    assert "sk-secret-must-not-leak" not in body


# ──────────────────────────────────────────────────────────────────────────────
# PUT /api/config/llm — write semantics
# ──────────────────────────────────────────────────────────────────────────────


def test_put_llm_with_new_key_persists_to_secrets_file_with_mode_0600(
    client, temp_data_home
):
    """PUT /api/config/llm with a key writes .secrets.json at mode 0600."""
    payload = {
        "providers": [
            {
                "name": "openai",
                "url": "https://api.openai.com/v1",
                "model": "gpt-4o",
                "key": "sk-test-1234567890",
            }
        ]
    }
    response = client.put("/api/config/llm", json=payload)
    assert response.status_code == 200

    secrets_file = temp_data_home / ".secrets.json"
    assert secrets_file.exists()

    # Mode 0600 enforced
    actual_mode = stat.S_IMODE(secrets_file.stat().st_mode)
    assert actual_mode == 0o600, (
        f"Expected .secrets.json mode 0600, got {oct(actual_mode)}"
    )

    # Key actually persisted
    secrets = load_secrets(temp_data_home)
    assert secrets["openai"]["api_key"] == "sk-test-1234567890"


def test_put_llm_with_empty_key_clears_the_key(client, temp_data_home):
    """PUT /api/config/llm with key="" (empty string) removes that provider's key.

    Convention (matches UI): explicit empty string = clear; omitted/null = preserve.
    """
    save_secrets(
        temp_data_home, {"openai": {"api_key": "sk-existing"}}
    )

    payload = {
        "providers": [
            {
                "name": "openai",
                "url": "https://api.openai.com/v1",
                "model": "gpt-4o",
                "key": "",
            }
        ]
    }
    response = client.put("/api/config/llm", json=payload)
    assert response.status_code == 200

    secrets = load_secrets(temp_data_home)
    assert "openai" not in secrets or "api_key" not in secrets.get("openai", {})


def test_put_llm_with_key_omitted_preserves_existing_key(client, temp_data_home):
    """PUT /api/config/llm without `key` field keeps the existing secrets-file value."""
    save_secrets(
        temp_data_home, {"openai": {"api_key": "sk-keepme"}}
    )

    payload = {
        "providers": [
            {
                "name": "openai",
                "url": "https://api.openai.com/v1",
                "model": "gpt-4o-mini",
                # NO key field — should preserve existing
            }
        ]
    }
    response = client.put("/api/config/llm", json=payload)
    assert response.status_code == 200

    secrets = load_secrets(temp_data_home)
    assert secrets["openai"]["api_key"] == "sk-keepme"


def test_put_llm_response_does_not_leak_plaintext_key(client, temp_data_home):
    """PUT /api/config/llm response uses key_status — never echoes the key back."""
    payload = {
        "providers": [
            {
                "name": "openai",
                "url": "https://api.openai.com/v1",
                "model": "gpt-4o",
                "key": "sk-do-not-echo-back",
            }
        ]
    }
    response = client.put("/api/config/llm", json=payload)
    assert response.status_code == 200
    body = json.dumps(response.json())
    assert "sk-do-not-echo-back" not in body


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/config/llm/test — connection test
# ──────────────────────────────────────────────────────────────────────────────


def test_post_llm_test_returns_400_when_no_key_set(client):
    """POST /api/config/llm/test returns 400 if neither env var nor secrets file has a key."""
    response = client.post("/api/config/llm/test", json={"provider": "openai"})
    assert response.status_code == 400
    assert "no_key" in response.json().get("error", "") or "key" in response.text.lower()


def test_post_llm_test_uses_inline_key_from_request_body(client):
    """ADR-0020 amendment 2026-04-25 — test-before-save.

    When `key` is in the request body, the server tests THAT key directly
    without reading env or secrets file. Lets the UI validate an unsaved
    key the user just typed.
    """
    captured = {}

    async def fake_list(api_key: str) -> list[str]:
        captured["key"] = api_key
        return ["gpt-4o", "gpt-4o-mini"]

    with patch("src.api.http_server.app._list_openai_chat_models", side_effect=fake_list):
        response = client.post(
            "/api/config/llm/test",
            json={"provider": "openai", "key": "sk-typed-in-ui"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert captured["key"] == "sk-typed-in-ui"


def test_post_llm_test_inline_key_overrides_env_var(client, monkeypatch):
    """The in-flight `key` wins over env var — user is testing the value they typed."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
    captured = {}

    async def fake_list(api_key: str) -> list[str]:
        captured["key"] = api_key
        return ["gpt-4o"]

    with patch("src.api.http_server.app._list_openai_chat_models", side_effect=fake_list):
        response = client.post(
            "/api/config/llm/test",
            json={"provider": "openai", "key": "sk-typed-in-ui"},
        )

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert captured["key"] == "sk-typed-in-ui"


def test_post_llm_test_empty_inline_key_falls_back_to_env(client, monkeypatch):
    """Empty/whitespace inline key triggers env > secrets lookup (existing behavior)."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
    captured = {}

    async def fake_list(api_key: str) -> list[str]:
        captured["key"] = api_key
        return ["gpt-4o"]

    with patch("src.api.http_server.app._list_openai_chat_models", side_effect=fake_list):
        response = client.post(
            "/api/config/llm/test",
            json={"provider": "openai", "key": "   "},
        )

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert captured["key"] == "sk-from-env"


def test_post_llm_test_returns_models_list_for_dropdown(client):
    """Successful test response includes `models` array — UI populates dropdown from it."""
    async def fake_list(api_key: str) -> list[str]:
        return ["claude-haiku-4-5-20251001", "claude-sonnet-4-6", "claude-opus-4-7"]

    with patch("src.api.http_server.app._list_anthropic_models", side_effect=fake_list):
        response = client.post(
            "/api/config/llm/test",
            json={"provider": "anthropic", "key": "sk-ant-test"},
        )

    body = response.json()
    assert body["ok"] is True
    assert "models" in body
    assert "claude-sonnet-4-6" in body["models"]
    assert len(body["models"]) == 3


def test_filter_openai_chat_models_drops_non_chat_entries():
    """OpenAI's /v1/models returns lots of noise (embeddings, dall-e, whisper).
    Filter to chat-capable families only and sort newest-first."""
    from src.api.http_server.app import _filter_openai_chat_models

    raw = [
        "gpt-4o", "gpt-3.5-turbo", "gpt-4o-mini",
        "text-embedding-3-small", "text-embedding-ada-002",
        "dall-e-3", "dall-e-2",
        "whisper-1", "tts-1",
        "babbage-002", "davinci-002",
        "o1-mini", "o3-mini",
        "chatgpt-4o-latest",
        "ft:gpt-3.5-turbo:org::xyz",  # fine-tunes — explicitly excluded
    ]
    filtered = _filter_openai_chat_models(raw)

    assert "text-embedding-3-small" not in filtered
    assert "dall-e-3" not in filtered
    assert "whisper-1" not in filtered
    assert "tts-1" not in filtered
    assert "babbage-002" not in filtered
    assert any(m.startswith("ft:") for m in filtered) is False

    assert "gpt-4o" in filtered
    assert "gpt-4o-mini" in filtered
    assert "o1-mini" in filtered
    assert "o3-mini" in filtered
    assert "chatgpt-4o-latest" in filtered

    # Descending order — sorted reverse-lexicographically
    assert filtered == sorted(filtered, reverse=True)


def test_filter_openai_chat_models_excludes_gpt_prefixed_non_chat_families():
    """Several recent OpenAI families share the gpt- prefix but use different
    APIs (image generation, TTS, transcription, Realtime). They must not leak
    into the chat-completions dropdown."""
    from src.api.http_server.app import _filter_openai_chat_models

    raw = [
        "gpt-4o",                          # ✓ chat
        "gpt-4o-mini",                     # ✓ chat
        "gpt-4o-audio-preview",            # ✗ audio I/O (16x cost, not for text-only)
        "gpt-image-1",                     # ✗ image generation
        "gpt-4o-transcribe",               # ✗ speech-to-text
        "gpt-4o-mini-transcribe",          # ✗ speech-to-text
        "gpt-4o-mini-tts",                 # ✗ text-to-speech
        "gpt-4o-realtime-preview",         # ✗ Realtime websocket API
        "gpt-4o-mini-realtime-preview",    # ✗ Realtime websocket API
        "omni-moderation-latest",          # ✗ moderation
    ]
    filtered = _filter_openai_chat_models(raw)

    assert "gpt-image-1" not in filtered
    assert "gpt-4o-transcribe" not in filtered
    assert "gpt-4o-mini-transcribe" not in filtered
    assert "gpt-4o-mini-tts" not in filtered
    assert "gpt-4o-realtime-preview" not in filtered
    assert "gpt-4o-mini-realtime-preview" not in filtered

    assert "gpt-4o" in filtered
    assert "gpt-4o-mini" in filtered
    # audio models excluded as of e88234d (16x cost, not suitable for text-only strategy gen)
    assert "gpt-4o-audio-preview" not in filtered


# ──────────────────────────────────────────────────────────────────────────────
# Env-var precedence (via secrets_store helpers)
# ──────────────────────────────────────────────────────────────────────────────


def test_env_var_takes_precedence_over_secrets_file(temp_data_home, monkeypatch):
    """get_api_key returns env var value when both env and secrets file are set."""
    save_secrets(temp_data_home, {"openai": {"api_key": "sk-from-secrets"}})
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")

    assert get_api_key(temp_data_home, "openai") == "sk-from-env"


def test_get_api_key_falls_back_to_secrets_file_when_env_unset(
    temp_data_home, monkeypatch
):
    """get_api_key returns secrets-file value when env var is not set."""
    save_secrets(temp_data_home, {"openai": {"api_key": "sk-from-secrets"}})
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert get_api_key(temp_data_home, "openai") == "sk-from-secrets"


def test_get_api_key_returns_none_when_neither_set(temp_data_home, monkeypatch):
    """get_api_key returns None when neither env var nor secrets file has the key."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert get_api_key(temp_data_home, "openai") is None


def test_key_status_env_overridden_when_both_set(temp_data_home, monkeypatch):
    """key_status is 'env_overridden' when env var AND secrets file both have value."""
    save_secrets(temp_data_home, {"openai": {"api_key": "sk-from-secrets"}})
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")

    assert get_key_status(temp_data_home, "openai") == "env_overridden"


def test_key_status_set_when_only_env(temp_data_home, monkeypatch):
    """key_status is 'set' when only env var has value."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
    assert get_key_status(temp_data_home, "openai") == "set"


def test_key_status_set_when_only_secrets_file(temp_data_home, monkeypatch):
    """key_status is 'set' when only secrets file has value."""
    save_secrets(temp_data_home, {"openai": {"api_key": "sk-from-secrets"}})
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert get_key_status(temp_data_home, "openai") == "set"


def test_key_status_unset_when_neither(temp_data_home, monkeypatch):
    """key_status is 'unset' when neither env nor secrets has value."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert get_key_status(temp_data_home, "openai") == "unset"


# ──────────────────────────────────────────────────────────────────────────────
# Secrets store edge cases
# ──────────────────────────────────────────────────────────────────────────────


def test_load_secrets_returns_empty_when_file_missing(temp_data_home):
    """load_secrets returns empty dict when .secrets.json doesn't exist (not an error)."""
    assert load_secrets(temp_data_home) == {}


def test_load_secrets_returns_empty_on_malformed_json(temp_data_home):
    """load_secrets logs a warning and returns empty dict when JSON is malformed."""
    secrets_file = temp_data_home / ".secrets.json"
    secrets_file.write_text("{ this is not valid json")
    secrets_file.chmod(0o600)

    # Should NOT raise — just return empty
    result = load_secrets(temp_data_home)
    assert result == {}


def test_save_secrets_enforces_mode_0600(temp_data_home):
    """save_secrets always writes .secrets.json at mode 0600, regardless of prior mode."""
    save_secrets(temp_data_home, {"openai": {"api_key": "sk-x"}})
    secrets_file = temp_data_home / ".secrets.json"
    assert stat.S_IMODE(secrets_file.stat().st_mode) == 0o600

    # Tamper with mode then save again
    secrets_file.chmod(0o644)
    save_secrets(temp_data_home, {"openai": {"api_key": "sk-y"}})
    assert stat.S_IMODE(secrets_file.stat().st_mode) == 0o600
