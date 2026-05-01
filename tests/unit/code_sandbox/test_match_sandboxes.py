"""MatchSandboxes — per-player sandbox dispatch (ADR-0024)."""

from __future__ import annotations

import pytest

from src.foundation.sandbox.match_sandboxes import MatchSandboxes
from src.foundation.sandbox.python_sandbox import RestrictedPythonSandbox
from src.foundation.sandbox.status import ExecutionStatus


def test_register_and_getitem():
    ms = MatchSandboxes()
    sb = RestrictedPythonSandbox()
    ms.register("team_a_0", sb)
    assert ms["team_a_0"] is sb


def test_getitem_missing_raises_keyerror():
    ms = MatchSandboxes()
    with pytest.raises(KeyError):
        ms["nonexistent"]


def test_execute_delegates_to_correct_sandbox():
    ms = MatchSandboxes()
    sb = RestrictedPythonSandbox()
    code = "def decide(game_state, player_state, history):\n    return Hold()\n"
    sb.compile("team_a_0", code)
    ms.register("team_a_0", sb)

    result = ms.execute("team_a_0", {}, {}, [])
    assert result.status == ExecutionStatus.SUCCESS


def test_execute_missing_player_raises_keyerror():
    ms = MatchSandboxes()
    with pytest.raises(KeyError):
        ms.execute("nonexistent", {}, {}, [])


def test_cross_player_isolation():
    """Two players on the same sandbox instance must not share module globals."""
    ms = MatchSandboxes()
    sb = RestrictedPythonSandbox()

    code_a = "counter = 0\ndef decide(gs, ps, h):\n    global counter\n    counter += 1\n    return Hold()\n"
    code_b = "def decide(gs, ps, h):\n    return Hold()\n"

    sb.compile("team_a_0", code_a)
    sb.compile("team_a_1", code_b)

    ms.register("team_a_0", sb)
    ms.register("team_a_1", sb)

    # Execute player A twice — counter should increment
    ms.execute("team_a_0", {}, {}, [])
    ms.execute("team_a_0", {}, {}, [])

    # Player B's namespace must not contain player A's counter
    ctx_b = sb._contexts["team_a_1"]
    assert "counter" not in ctx_b.module_globals or ctx_b.module_globals.get("counter") == 0


def test_players_property():
    ms = MatchSandboxes()
    sb = RestrictedPythonSandbox()
    ms.register("team_a_0", sb)
    ms.register("team_b_0", sb)
    assert set(ms.players) == {"team_a_0", "team_b_0"}