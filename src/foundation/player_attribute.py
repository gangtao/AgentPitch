"""
Player Attribute Model for Agent Pitch soccer simulation.

This module defines the PlayerAttribute Pydantic model that stores
all player attributes used throughout the simulation.
"""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class PlayerAttribute(BaseModel):
    """
    Player attribute data model.

    Contains all player attributes used in the simulation:
    - Identification: player_id, team, role
    - Physical: speed, skill, strength, save
    - Tactical: discipline, dribbling
    """

    model_config = ConfigDict(frozen=True, strict=True)

    player_id: str = Field(
        min_length=1,
        description="Player identifier in format 'team_{a|b}_{0-4}'"
    )

    team: str = Field(
        min_length=1,
        description="Team assignment"
    )

    role: Literal["GK", "DEF", "MID", "FWD"] = Field(
        description="Player position role"
    )

    speed: int = Field(
        ge=1,
        le=20,
        description="Movement speed (1-20 scale)"
    )

    skill: int = Field(
        ge=1,
        le=20,
        description="Technical skill level (1-20 scale)"
    )

    strength: int = Field(
        ge=1,
        le=20,
        description="Physical strength (1-20 scale)"
    )

    save: int = Field(
        ge=0,
        le=20,
        description="Goalkeeper save reach (0-20; non-GK must be 0)"
    )

    discipline: int = Field(
        ge=1,
        le=20,
        description="Tactical positioning awareness (1-20 scale)"
    )

    dribbling: int = Field(
        ge=1,
        le=20,
        description="Ball control and dribbling ability (1-20 scale)"
    )

    @model_validator(mode="after")
    def validate_save_gk_only(self) -> "PlayerAttribute":
        """save is GK-only — non-GK players must have save == 0."""
        if self.role != "GK" and self.save != 0:
            raise ValueError(
                f"{self.player_id}: save is GK-only (got {self.save})"
            )
        return self


# Role-based default values for player attributes
# Source: PAM GDD Role Defaults table — authoritative data source
ROLE_DEFAULTS: dict[str, dict[str, int]] = {
    "GK":  {"speed": 8,  "skill": 10, "strength": 8,  "save": 16, "discipline": 14, "dribbling": 4},
    "DEF": {"speed": 12, "skill": 8,  "strength": 16, "save": 0,  "discipline": 16, "dribbling": 6},
    "MID": {"speed": 14, "skill": 16, "strength": 10, "save": 0,  "discipline": 14, "dribbling": 12},
    "FWD": {"speed": 16, "skill": 14, "strength": 14, "save": 0,  "discipline": 10, "dribbling": 16},
}