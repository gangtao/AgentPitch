"""Unit tests for src/session_store.py — server-side sessions."""

from __future__ import annotations

import os
import stat
import time
from pathlib import Path

import pytest

from src.session_store import (
    SessionStoreError,
    create_session,
    destroy_session,
    destroy_user_sessions,
    resolve_session,
    sessions_path,
)


@pytest.fixture
def data_home(tmp_path: Path) -> Path:
    return tmp_path


def test_unknown_token_resolves_none(data_home):
    assert resolve_session(data_home, "whatever") is None
    assert resolve_session(data_home, "") is None


def test_create_and_resolve(data_home):
    token = create_session(data_home, "user-123")
    assert isinstance(token, str) and len(token) > 20
    assert resolve_session(data_home, token) == "user-123"
    assert resolve_session(data_home, token + "x") is None


def test_file_is_0600_and_hashes_token(data_home):
    token = create_session(data_home, "user-123")
    path = sessions_path(data_home)
    mode = stat.S_IMODE(os.stat(path).st_mode)
    assert mode == 0o600
    raw = path.read_text()
    # raw token must never be persisted — only its sha256 hash
    assert token not in raw
    assert "token_hash" in raw


def test_destroy_single_session(data_home):
    token = create_session(data_home, "u1")
    assert destroy_session(data_home, token) is True
    assert resolve_session(data_home, token) is None
    # second destroy is a no-op
    assert destroy_session(data_home, token) is False


def test_destroy_user_sessions(data_home):
    a = create_session(data_home, "u9")
    b = create_session(data_home, "u9")
    c = create_session(data_home, "u8")
    removed = destroy_user_sessions(data_home, "u9")
    assert removed == 2
    assert resolve_session(data_home, a) is None
    assert resolve_session(data_home, b) is None
    assert resolve_session(data_home, c) == "u8"


def test_multiple_sessions_same_user_coexist(data_home):
    a = create_session(data_home, "u1")
    b = create_session(data_home, "u1")
    assert a != b
    assert resolve_session(data_home, a) == "u1"
    assert resolve_session(data_home, b) == "u1"


def test_expired_session_pruned(data_home):
    token = create_session(data_home, "ttl-user", ttl_seconds=1)
    assert resolve_session(data_home, token) == "ttl-user"
    time.sleep(1.2)
    assert resolve_session(data_home, token) is None


def test_malformed_file_raises(data_home):
    sessions_path(data_home).write_text("not json at all")
    with pytest.raises(SessionStoreError):
        resolve_session(data_home, "x")
