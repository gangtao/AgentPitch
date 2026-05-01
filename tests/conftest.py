"""
Shared pytest fixtures for Agent Pitch test suite.

Fixtures here are available to all tests in tests/unit/ and tests/integration/.
"""

import pytest


# ---------------------------------------------------------------------------
# Player ID helpers
# ---------------------------------------------------------------------------

ALL_PLAYER_IDS = [f"team_a_{i}" for i in range(5)] + [f"team_b_{i}" for i in range(5)]


@pytest.fixture
def all_player_ids():
    """All 10 valid player IDs for a 5v5 match."""
    return list(ALL_PLAYER_IDS)


@pytest.fixture
def team_a_ids():
    return [f"team_a_{i}" for i in range(5)]


@pytest.fixture
def team_b_ids():
    return [f"team_b_{i}" for i in range(5)]
