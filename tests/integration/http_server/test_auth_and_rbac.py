"""Integration tests for the user-management feature: auth, roles, ownership.

Unlike the rest of the http_server suite (which runs with the auth gate
disabled via the session-wide conftest env), these construct the app with
`require_auth=True` explicitly so the gate is active, and authenticate by
logging in through the real endpoints.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app
from src import user_store


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def data_home(tmp_path, monkeypatch):
    """A data dir with a static/index.html stub so create_app() doesn't raise."""
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html>ok</html>")
    import src.api.http_server.app as app_module
    monkeypatch.setattr(app_module, "_STATIC_DIR", static)
    return tmp_path


def _app(data_home):
    # Explicit require_auth=True overrides the suite-wide env that disables it.
    return create_app(log_dir=str(data_home), seed_defaults=False, require_auth=True)


def _login(client: TestClient, username: str, password: str) -> TestClient:
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, f"login failed for {username}: {r.status_code} {r.text}"
    return client


def _seed(data_home, username, password, role="user"):
    return user_store.create_user(data_home, username, password, role=role)


# ---------------------------------------------------------------------------
# Auth gate + login/logout
# ---------------------------------------------------------------------------


def test_protected_route_requires_login(data_home):
    _seed(data_home, "admin", "adminpass1", role="admin")
    client = TestClient(_app(data_home))
    # Public endpoints
    assert client.get("/api/health").status_code == 200
    # Protected endpoint without a session → 401
    assert client.get("/api/strategies").status_code == 401
    assert client.get("/api/users").status_code == 401


def test_me_reports_setup_required_when_no_admin(data_home):
    client = TestClient(_app(data_home))
    r = client.get("/api/auth/me")
    assert r.status_code == 401
    assert r.json()["setup_required"] is True


def test_login_logout_cycle(data_home):
    _seed(data_home, "alice", "alicepass1")
    client = TestClient(_app(data_home))
    assert client.post("/api/auth/login",
                       json={"username": "alice", "password": "wrong"}).status_code == 401
    _login(client, "alice", "alicepass1")
    me = client.get("/api/auth/me")
    assert me.status_code == 200 and me.json()["user"]["username"] == "alice"
    assert client.get("/api/strategies").status_code == 200
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/strategies").status_code == 401


# ---------------------------------------------------------------------------
# User management (admin only)
# ---------------------------------------------------------------------------


def test_only_admin_can_create_users(data_home):
    _seed(data_home, "admin", "adminpass1", role="admin")
    _seed(data_home, "bob", "bobpass1234")

    bob = _login(TestClient(_app(data_home)), "bob", "bobpass1234")
    assert bob.post("/api/users",
                    json={"username": "x", "password": "password1"}).status_code == 403

    admin = _login(TestClient(_app(data_home)), "admin", "adminpass1")
    r = admin.post("/api/users", json={"username": "carol", "password": "carolpass1"})
    assert r.status_code == 201
    assert r.json()["user"]["username"] == "carol"
    assert "password_hash" not in r.json()["user"]


def test_duplicate_username_rejected(data_home):
    _seed(data_home, "admin", "adminpass1", role="admin")
    admin = _login(TestClient(_app(data_home)), "admin", "adminpass1")
    admin.post("/api/users", json={"username": "dup", "password": "password1"})
    r = admin.post("/api/users", json={"username": "dup", "password": "password2"})
    assert r.status_code == 409


def test_cannot_delete_last_admin_or_self(data_home):
    _seed(data_home, "admin", "adminpass1", role="admin")
    admin = _login(TestClient(_app(data_home)), "admin", "adminpass1")
    admin_id = admin.get("/api/auth/me").json()["user"]["id"]
    # self-delete blocked
    assert admin.delete(f"/api/users/{admin_id}").status_code == 409
    # demote-last-admin blocked
    assert admin.put(f"/api/users/{admin_id}/role",
                     json={"role": "user"}).status_code == 409


def test_admin_password_reset_invalidates_sessions(data_home):
    _seed(data_home, "admin", "adminpass1", role="admin")
    bob = _seed(data_home, "bob", "bobpass1234")

    bob_client = _login(TestClient(_app(data_home)), "bob", "bobpass1234")
    assert bob_client.get("/api/strategies").status_code == 200

    admin = _login(TestClient(_app(data_home)), "admin", "adminpass1")
    assert admin.put(f"/api/users/{bob.id}/password",
                     json={"new_password": "resetpass1"}).status_code == 200

    # Bob's old session is now dead.
    assert bob_client.get("/api/strategies").status_code == 401


# ---------------------------------------------------------------------------
# Teams + team-lead capability
# ---------------------------------------------------------------------------


def test_team_lead_manages_only_own_team(data_home):
    _seed(data_home, "admin", "adminpass1", role="admin")
    lead = _seed(data_home, "lead1", "leadpass1")
    member = _seed(data_home, "bob", "bobpass1234")

    admin = _login(TestClient(_app(data_home)), "admin", "adminpass1")
    assert admin.post("/api/teams", json={"slug": "falcons", "name": "Falcons"}).status_code == 201
    assert admin.post("/api/teams", json={"slug": "eagles", "name": "Eagles"}).status_code == 201
    # make lead1 a lead of falcons only
    assert admin.post("/api/teams/falcons/leads",
                      json={"user_id": lead.id}).status_code == 200

    lead_client = _login(TestClient(_app(data_home)), "lead1", "leadpass1")
    # Can add a member to falcons (their team)
    assert lead_client.post("/api/teams/falcons/members",
                            json={"user_id": member.id}).status_code == 200
    # Cannot manage eagles (not their team)
    assert lead_client.post("/api/teams/eagles/members",
                            json={"user_id": member.id}).status_code == 403
    # Cannot create a new team (admin-only)
    assert lead_client.post("/api/teams",
                            json={"slug": "hawks", "name": "Hawks"}).status_code == 403


def test_plain_user_cannot_manage_teams(data_home):
    _seed(data_home, "admin", "adminpass1", role="admin")
    bob = _seed(data_home, "bob", "bobpass1234")
    admin = _login(TestClient(_app(data_home)), "admin", "adminpass1")
    admin.post("/api/teams", json={"slug": "falcons", "name": "Falcons"})

    bob_client = _login(TestClient(_app(data_home)), "bob", "bobpass1234")
    assert bob_client.get("/api/teams").status_code == 200   # read allowed
    assert bob_client.post("/api/teams/falcons/members",
                           json={"user_id": bob.id}).status_code == 403


def test_promote_demote_and_lead_appears_in_me(data_home):
    _seed(data_home, "admin", "adminpass1", role="admin")
    bob = _seed(data_home, "bob", "bobpass1234")
    admin = _login(TestClient(_app(data_home)), "admin", "adminpass1")
    admin.post("/api/teams", json={"slug": "falcons", "name": "Falcons"})
    admin.post("/api/teams/falcons/leads", json={"user_id": bob.id})

    bob_client = _login(TestClient(_app(data_home)), "bob", "bobpass1234")
    me = bob_client.get("/api/auth/me").json()
    assert me["is_team_lead"] is True
    assert any(t["slug"] == "falcons" and t["is_lead"] for t in me["teams"])


# ---------------------------------------------------------------------------
# Strategy ownership ("agent" ↔ user)
# ---------------------------------------------------------------------------


def test_strategy_ownership_rules(data_home):
    _seed(data_home, "admin", "adminpass1", role="admin")
    _seed(data_home, "alice", "alicepass1")
    _seed(data_home, "bob", "bobpass1234")

    alice = _login(TestClient(_app(data_home)), "alice", "alicepass1")
    bob = _login(TestClient(_app(data_home)), "bob", "bobpass1234")
    admin = _login(TestClient(_app(data_home)), "admin", "adminpass1")

    src = "def decide(g, p, h):\n    return Hold()\n"
    r = alice.post("/api/strategies", json={"name": "alice_strat", "source": src})
    assert r.status_code == 201

    alice_id = alice.get("/api/auth/me").json()["user"]["id"]
    meta = alice.get("/api/strategies/alice_strat").json()["meta"]
    assert meta["owner_user_id"] == alice_id

    # Non-owner cannot edit or delete.
    assert bob.put("/api/strategies/alice_strat",
                   json={"source": src + "# x\n"}).status_code == 403
    assert bob.delete("/api/strategies/alice_strat").status_code == 403

    # Owner can edit.
    assert alice.put("/api/strategies/alice_strat",
                     json={"source": src + "# mine\n"}).status_code in (200, 201)

    # Admin can delete anyone's.
    assert admin.delete("/api/strategies/alice_strat").status_code == 204


def test_ownerless_legacy_strategy_editable_by_any_user(data_home):
    _seed(data_home, "admin", "adminpass1", role="admin")
    _seed(data_home, "bob", "bobpass1234")

    # Simulate a legacy strategy written with no sidecar/owner.
    strat_dir = Path(data_home) / "strategies"
    strat_dir.mkdir(parents=True, exist_ok=True)
    (strat_dir / "legacy.py").write_text("def decide(g, p, h):\n    return Hold()\n")

    bob = _login(TestClient(_app(data_home)), "bob", "bobpass1234")
    r = bob.put("/api/strategies/legacy",
                json={"source": "def decide(g, p, h):\n    return Hold()  # edited\n"})
    assert r.status_code in (200, 201)
