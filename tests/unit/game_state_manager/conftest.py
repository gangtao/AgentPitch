"""Shared fixtures and helpers for GameStateManager unit tests.

Replaces the per-file stub `MatchConfig` / `FieldConfig` / `MatchParams`
dataclasses that previously diverged from `src/foundation/config_models.py`.
All GSM tests now construct the **real** MatchConfig via `_create_test_config`,
catching schema-drift regressions at unit-test time.
"""

from __future__ import annotations

from src.foundation.config_models import (
    MatchConfig,
    MatchParams,
    OutputConfig,
    PlayerConfig,
    TeamConfig,
)


# Roster shape used by every GSM test: GK + 2 DEF + MID + FWD with the same
# attribute distribution as the original per-file _create_test_config helpers.
_TEAM_ROSTER_SPEC: list[tuple[str, dict[str, int]]] = [
    ("GK",  {"speed": 8,  "skill": 10, "strength": 8,  "save": 16, "discipline": 14, "dribbling": 4}),
    ("DEF", {"speed": 12, "skill": 10, "strength": 12, "save": 0,  "discipline": 12, "dribbling": 8}),
    ("DEF", {"speed": 12, "skill": 10, "strength": 12, "save": 0,  "discipline": 12, "dribbling": 8}),
    ("MID", {"speed": 12, "skill": 10, "strength": 12, "save": 0,  "discipline": 12, "dribbling": 8}),
    ("FWD", {"speed": 12, "skill": 10, "strength": 12, "save": 0,  "discipline": 12, "dribbling": 8}),
]


def _build_team_players(team_id: str) -> list[PlayerConfig]:
    return [
        PlayerConfig(player_id=f"{team_id}_{i}", role=role, **attrs)  # type: ignore[arg-type]
        for i, (role, attrs) in enumerate(_TEAM_ROSTER_SPEC)
    ]


def _create_test_config(
    seed: int = 42,
    tick_rate: int = 10,
    duration_minutes: int = 90,
    field_width: float = 100.0,
    field_height: float = 60.0,
    log_dir: str = "/tmp/test",
    match_id: str = "test_match",
) -> MatchConfig:
    """Build a real MatchConfig for GSM tests.

    Signature matches the legacy per-file helper so existing test bodies need no
    changes. Both teams get the same 5-player GK/DEF/DEF/MID/FWD roster.
    `log_dir` and `match_id` are exposed as kwargs for tests that need to write
    real artifacts (e.g. integration tests using tmp_path).
    """
    return MatchConfig(
        match=MatchParams(
            seed=seed,
            tick_rate=tick_rate,
            duration_minutes=duration_minutes,
            field_width=field_width,
            field_height=field_height,
            match_id=match_id,
        ),
        output=OutputConfig(log_dir=log_dir),
        team_a=TeamConfig(
            team_id="team_a",
            name="Team A",
            llm_provider="openai",
            llm_model="gpt-4o",
            api_key="test_key",
            players=_build_team_players("team_a"),
        ),
        team_b=TeamConfig(
            team_id="team_b",
            name="Team B",
            llm_provider="anthropic",
            llm_model="claude-opus-4",
            api_key="test_key",
            players=_build_team_players("team_b"),
        ),
    )


def _create_test_anchors() -> dict[str, tuple[float, float]]:
    """Standard 4-2-1-1 formation anchors used by every GSM test file."""
    return {
        # Team A formation
        "team_a_0": (8.0, 30.0),   # GK
        "team_a_1": (20.0, 20.0),  # DEF
        "team_a_2": (20.0, 40.0),  # DEF
        "team_a_3": (40.0, 30.0),  # MID
        "team_a_4": (60.0, 30.0),  # FWD
        # Team B formation
        "team_b_0": (92.0, 30.0),  # GK
        "team_b_1": (80.0, 20.0),  # DEF
        "team_b_2": (80.0, 40.0),  # DEF
        "team_b_3": (60.0, 30.0),  # MID
        "team_b_4": (40.0, 30.0),  # FWD
    }
