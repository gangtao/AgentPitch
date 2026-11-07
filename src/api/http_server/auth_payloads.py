"""Pydantic models for authentication + user/team management endpoints.

API-layer-local (ADR-0006). These validate HTTP request bodies only; the
persisted shapes live in src/user_store.py and src/team_store.py.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Auth ────────────────────────────────────────────────────────────────


class LoginPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    username: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=256)


class ChangePasswordPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=8, max_length=256)


# ── User management (admin) ───────────────────────────────────────────────


class CreateUserPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    username: str = Field(pattern=r"^[A-Za-z0-9_.-]{3,32}$")
    password: str = Field(min_length=8, max_length=256)
    role: Literal["admin", "user"] = "user"
    must_change_password: bool = True


class SetRolePayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    role: Literal["admin", "user"]


class AdminResetPasswordPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    new_password: str = Field(min_length=8, max_length=256)
    must_change_password: bool = True


# ── Team management ───────────────────────────────────────────────────────


class CreateTeamPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    slug: str = Field(pattern=r"^[a-z0-9_-]+$", max_length=64)
    name: str = Field(min_length=1, max_length=64)


class RenameTeamPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str = Field(min_length=1, max_length=64)


class TeamMemberPayload(BaseModel):
    """Add/remove/promote/demote target. `user_id` references a user_store id."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    user_id: str = Field(min_length=1, max_length=64)
