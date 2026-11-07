"""Unit tests for src/team_store.py — organisational teams, leads, members."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.team_store import (
    InvalidTeamSlugError,
    Team,
    TeamAlreadyExistsError,
    TeamNotFoundError,
    TeamStoreError,
    add_member,
    create_team,
    delete_team,
    demote_lead,
    get_team,
    is_lead_of_any,
    load_teams,
    promote_lead,
    purge_user,
    remove_member,
    rename_team,
    team_exists,
    teams_for_user,
    teams_led_by,
    teams_path,
)


@pytest.fixture
def data_home(tmp_path: Path) -> Path:
    return tmp_path


# ---------------------------------------------------------------------------
# Creation + invariants
# ---------------------------------------------------------------------------


def test_empty_state(data_home):
    assert load_teams(data_home) == []
    assert team_exists(data_home, "x") is False
    assert not teams_path(data_home).exists()


def test_create_team_lead_is_also_member(data_home):
    t = create_team(data_home, "falcons", "The Falcons",
                    lead_user_ids=["u1"], member_user_ids=["u2"])
    assert t.is_lead("u1")
    assert t.is_member("u1")  # invariant: lead ⊆ members
    assert t.is_member("u2")
    assert team_exists(data_home, "falcons")


def test_duplicate_slug_rejected(data_home):
    create_team(data_home, "falcons", "A")
    with pytest.raises(TeamAlreadyExistsError):
        create_team(data_home, "falcons", "B")


def test_invalid_slug_rejected(data_home):
    for bad in ["Falcons", "has space", "under_SCORE".upper(), "bad/x"]:
        with pytest.raises(InvalidTeamSlugError):
            create_team(data_home, bad, "x")


def test_empty_name_rejected(data_home):
    with pytest.raises(TeamStoreError):
        create_team(data_home, "falcons", "   ")


# ---------------------------------------------------------------------------
# Membership mutations
# ---------------------------------------------------------------------------


def test_add_member_idempotent(data_home):
    create_team(data_home, "falcons", "F")
    add_member(data_home, "falcons", "u1")
    add_member(data_home, "falcons", "u1")  # again
    t = get_team(data_home, "falcons")
    assert list(t.member_user_ids).count("u1") == 1


def test_promote_then_demote_keeps_membership(data_home):
    create_team(data_home, "falcons", "F", member_user_ids=["u1"])
    promote_lead(data_home, "falcons", "u1")
    assert get_team(data_home, "falcons").is_lead("u1")
    demote_lead(data_home, "falcons", "u1")
    t = get_team(data_home, "falcons")
    assert not t.is_lead("u1")
    assert t.is_member("u1")


def test_promote_nonmember_adds_membership(data_home):
    create_team(data_home, "falcons", "F")
    promote_lead(data_home, "falcons", "u9")
    t = get_team(data_home, "falcons")
    assert t.is_lead("u9") and t.is_member("u9")


def test_remove_member_drops_lead_too(data_home):
    create_team(data_home, "falcons", "F", lead_user_ids=["u1"])
    remove_member(data_home, "falcons", "u1")
    t = get_team(data_home, "falcons")
    assert not t.is_member("u1")
    assert not t.is_lead("u1")


def test_rename_team(data_home):
    create_team(data_home, "falcons", "Old")
    rename_team(data_home, "falcons", "New Name")
    assert get_team(data_home, "falcons").name == "New Name"


def test_delete_team(data_home):
    create_team(data_home, "falcons", "F")
    delete_team(data_home, "falcons")
    assert not team_exists(data_home, "falcons")
    with pytest.raises(TeamNotFoundError):
        delete_team(data_home, "falcons")


# ---------------------------------------------------------------------------
# Multi-team lookups + purge
# ---------------------------------------------------------------------------


def test_multi_team_lookups(data_home):
    create_team(data_home, "falcons", "F", member_user_ids=["u3"])
    create_team(data_home, "eagles", "E", lead_user_ids=["u3"])
    assert {t.slug for t in teams_for_user(data_home, "u3")} == {"falcons", "eagles"}
    assert {t.slug for t in teams_led_by(data_home, "u3")} == {"eagles"}
    assert is_lead_of_any(data_home, "u3") is True


def test_purge_user_across_teams(data_home):
    create_team(data_home, "falcons", "F", lead_user_ids=["u3"])
    create_team(data_home, "eagles", "E", member_user_ids=["u3"])
    removed = purge_user(data_home, "u3")
    assert removed == 2
    assert is_lead_of_any(data_home, "u3") is False
    assert teams_for_user(data_home, "u3") == []


def test_get_missing_team_raises(data_home):
    with pytest.raises(TeamNotFoundError):
        get_team(data_home, "ghost")


# ---------------------------------------------------------------------------
# Persistence shape + corruption
# ---------------------------------------------------------------------------


def test_round_trip_shape(data_home):
    create_team(data_home, "falcons", "F", lead_user_ids=["u1"], member_user_ids=["u2"])
    raw = json.loads(teams_path(data_home).read_text())
    assert "teams" in raw and isinstance(raw["teams"], list)
    team = raw["teams"][0]
    assert isinstance(team["lead_user_ids"], list)  # tuples serialized as lists


def test_malformed_file_raises(data_home):
    teams_path(data_home).write_text("{ not json")
    with pytest.raises(TeamStoreError):
        load_teams(data_home)
