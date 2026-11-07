"""
Shared pytest fixtures for Agent Pitch test suite.

Fixtures here are available to all tests in tests/unit/ and tests/integration/.
"""

import pytest


# ---------------------------------------------------------------------------
# Auth gate default for tests
# ---------------------------------------------------------------------------
#
# The HTTP server installs a session gate (require_auth=True by default) that
# forces login on every /api/* route. The large existing suite constructs
# `create_app(log_dir=...)` and hits endpoints unauthenticated — so for tests
# we flip the DEFAULT of `require_auth` to False. Tests that specifically
# exercise auth/roles/ownership pass `require_auth=True` explicitly, which the
# wrapper leaves untouched. Production and the `serve` entrypoint are
# unaffected (they never import this conftest).


@pytest.fixture(autouse=True, scope="session")
def _disable_auth_gate_for_tests():
    """Disable the HTTP auth gate for the whole test session via env var.

    create_app() treats require_auth=None (its default) as "ON unless
    AGENTPITCH_DISABLE_AUTH=1". Setting it here keeps the ~40 existing
    unauthenticated-endpoint tests green without edits. Auth/role/ownership
    tests pass require_auth=True explicitly, which overrides this.
    """
    import os
    prev = os.environ.get("AGENTPITCH_DISABLE_AUTH")
    os.environ["AGENTPITCH_DISABLE_AUTH"] = "1"
    try:
        yield
    finally:
        if prev is None:
            os.environ.pop("AGENTPITCH_DISABLE_AUTH", None)
        else:
            os.environ["AGENTPITCH_DISABLE_AUTH"] = prev


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
