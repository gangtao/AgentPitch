"""Unit tests for src/user_store.py — file-backed users + argon2 hashing."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from src.user_store import (
    InvalidUsernameError,
    User,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserStoreError,
    WeakPasswordError,
    count_users,
    create_user,
    delete_user,
    get_user_by_id,
    get_user_by_username,
    has_any_admin,
    load_users,
    set_password,
    set_role,
    username_exists,
    users_path,
    verify_password,
)


@pytest.fixture
def data_home(tmp_path: Path) -> Path:
    return tmp_path


# ---------------------------------------------------------------------------
# Bootstrap / empty state
# ---------------------------------------------------------------------------


def test_empty_bootstrap_state(data_home):
    assert load_users(data_home) == []
    assert count_users(data_home) == 0
    assert has_any_admin(data_home) is False
    assert username_exists(data_home, "nobody") is False


def test_missing_file_does_not_create(data_home):
    load_users(data_home)
    assert not users_path(data_home).exists()


# ---------------------------------------------------------------------------
# Creation + persistence
# ---------------------------------------------------------------------------


def test_create_user_persists_with_0600(data_home):
    u = create_user(data_home, "alice", "password1")
    assert isinstance(u, User)
    assert u.role == "user"
    assert u.username == "alice"
    assert u.id  # non-empty id
    path = users_path(data_home)
    assert path.exists()
    mode = stat.S_IMODE(os.stat(path).st_mode)
    assert mode == 0o600


def test_create_admin_and_flag(data_home):
    admin = create_user(data_home, "root", "password1", role="admin",
                        must_change_password=True)
    assert admin.role == "admin"
    assert admin.must_change_password is True
    assert has_any_admin(data_home) is True


def test_public_dict_strips_hash(data_home):
    u = create_user(data_home, "alice", "password1")
    pub = u.to_public_dict()
    assert "password_hash" not in pub
    assert pub["username"] == "alice"
    # the stored record itself retains the hash
    assert u.password_hash.startswith("$argon2")


def test_password_hash_not_plaintext_in_file(data_home):
    create_user(data_home, "alice", "sup3rsecret")
    raw = users_path(data_home).read_text()
    assert "sup3rsecret" not in raw
    assert "$argon2" in raw


# ---------------------------------------------------------------------------
# Uniqueness + validation
# ---------------------------------------------------------------------------


def test_duplicate_username_case_insensitive(data_home):
    create_user(data_home, "Alice", "password1")
    with pytest.raises(UserAlreadyExistsError):
        create_user(data_home, "alice", "password2")


def test_invalid_username_rejected(data_home):
    for bad in ["ab", "has space", "x" * 33, "bad/slash"]:
        with pytest.raises(InvalidUsernameError):
            create_user(data_home, bad, "password1")


def test_weak_password_rejected(data_home):
    with pytest.raises(WeakPasswordError):
        create_user(data_home, "alice", "short")


def test_invalid_role_rejected(data_home):
    with pytest.raises(UserStoreError):
        create_user(data_home, "alice", "password1", role="superuser")


# ---------------------------------------------------------------------------
# Lookups
# ---------------------------------------------------------------------------


def test_lookups_by_id_and_username(data_home):
    u = create_user(data_home, "alice", "password1")
    assert get_user_by_id(data_home, u.id).username == "alice"
    assert get_user_by_username(data_home, "ALICE").id == u.id
    with pytest.raises(UserNotFoundError):
        get_user_by_id(data_home, "no-such-id")
    with pytest.raises(UserNotFoundError):
        get_user_by_username(data_home, "ghost")


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def test_verify_password_success_and_failure(data_home):
    create_user(data_home, "alice", "password1")
    ok = verify_password(data_home, "alice", "password1")
    assert ok.username == "alice"
    # case-insensitive username on verify
    assert verify_password(data_home, "ALICE", "password1").username == "alice"
    with pytest.raises(UserStoreError):
        verify_password(data_home, "alice", "wrongpass")
    with pytest.raises(UserNotFoundError):
        verify_password(data_home, "ghost", "password1")


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------


def test_set_role(data_home):
    u = create_user(data_home, "alice", "password1")
    updated = set_role(data_home, u.id, "admin")
    assert updated.role == "admin"
    assert get_user_by_id(data_home, u.id).role == "admin"
    with pytest.raises(UserNotFoundError):
        set_role(data_home, "nope", "admin")


def test_set_password_rehashes_and_clears_flag(data_home):
    u = create_user(data_home, "alice", "password1", must_change_password=True)
    old_hash = u.password_hash
    updated = set_password(data_home, u.id, "newpassword1")
    assert updated.password_hash != old_hash
    assert updated.must_change_password is False
    assert verify_password(data_home, "alice", "newpassword1").id == u.id
    with pytest.raises(UserStoreError):
        verify_password(data_home, "alice", "password1")


def test_set_password_weak_rejected(data_home):
    u = create_user(data_home, "alice", "password1")
    with pytest.raises(WeakPasswordError):
        set_password(data_home, u.id, "weak")


def test_delete_user(data_home):
    u = create_user(data_home, "alice", "password1")
    delete_user(data_home, u.id)
    assert count_users(data_home) == 0
    with pytest.raises(UserNotFoundError):
        delete_user(data_home, u.id)


# ---------------------------------------------------------------------------
# Corruption / malformed file
# ---------------------------------------------------------------------------


def test_malformed_file_raises(data_home):
    users_path(data_home).write_text("not json")
    with pytest.raises(UserStoreError):
        load_users(data_home)


def test_wrong_shape_raises(data_home):
    users_path(data_home).write_text(json.dumps({"not_users": []}))
    with pytest.raises(UserStoreError):
        load_users(data_home)
