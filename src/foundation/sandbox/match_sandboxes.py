"""MatchSandboxes — per-player sandbox dispatch for mixed-language matches.

ADR-0024. Each player maps to their team's Sandbox implementation.
In a mono-language match all players point to the same instance.
In a mixed-language match, team_a players may use RestrictedPythonSandbox
while team_b players use QuickJSSandbox.

Implements the same compile/execute/disable surface as a single Sandbox so
TickEngine can pass it to ActionResolutionEngine without ARE caring whether
the match is mixed-language. Players must be `register()`-ed to a sandbox
before compile/execute/disable is called for them.
"""

from __future__ import annotations

import time

from src.foundation.sandbox.result import SandboxResult


class MatchSandboxes:
    """Per-player sandbox dispatch — supports mixed-language matches."""

    def __init__(self) -> None:
        self._by_player: dict[str, object] = {}
        # Per-tick timing accumulator. Each value is {"serial_ms", "exec_ms"}.
        # Populated by execute(); cleared by drain_exec_times(). TickEngine
        # reads this after each tick to build the perf record.
        self._exec_times: dict[str, dict] = {}

    def register(self, player_id: str, sandbox: object) -> None:
        self._by_player[player_id] = sandbox

    def __getitem__(self, player_id: str) -> object:
        return self._by_player[player_id]

    def language_for(self, player_id: str) -> str:
        """Return the sandbox language tag for a registered player."""
        sb = self._by_player.get(player_id)
        if sb is None:
            return "unknown"
        return getattr(sb, "language", "unknown")

    def drain_exec_times(self) -> dict[str, dict]:
        """Return and clear the accumulated per-player timing dicts.

        Each value is {"serial_ms": float, "exec_ms": float} where:
          serial_ms — data-prep cost (deepcopy / json.dumps / msgpack.dumps)
          exec_ms   — runtime cost (compiled_fn / ctx.eval / wasm pipeline)
        The two are comparable across sandbox types; their sum is the total
        cost of one execute() call.
        """
        times = dict(self._exec_times)
        self._exec_times.clear()
        return times

    def compile(self, player_id: str, source: str) -> SandboxResult:
        sb = self._by_player[player_id]
        return sb.compile(player_id, source)  # type: ignore[union-attr]

    def execute(
        self,
        player_id: str,
        game_state,
        player_state,
        history,
    ) -> SandboxResult:
        sb = self._by_player[player_id]
        result = sb.execute(player_id, game_state, player_state, history)  # type: ignore[union-attr]
        self._exec_times[player_id] = {
            "serial_ms": round(result.serialization_ms, 4),
            "exec_ms": round(result.execution_time_ms, 4),
        }
        return result

    def disable(self, player_id: str) -> None:
        sb = self._by_player[player_id]
        sb.disable(player_id)  # type: ignore[union-attr]

    @property
    def players(self) -> list[str]:
        return list(self._by_player.keys())