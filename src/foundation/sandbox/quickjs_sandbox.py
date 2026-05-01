"""QuickJSSandbox — JavaScript sandbox via quickjs PyPI binding (ADR-0025).

Implements the Sandbox Protocol (ADR-0024) for JavaScript strategies.
Each player gets a fresh quickjs.Context with no host bindings beyond
Math + JSON. Cross-tick state persists via JS module globals (CR-5).

Spike-verified API (2026-04-26, quickjs 1.19.4):
  - ctx.set_time_limit(seconds) for timeout
  - quickjs.JSException for errors
  - JSON-string bridge for dict marshalling

This is the **designated JS sandbox module** per ADR-0025. exec() is NOT
used here — all code evaluation goes through quickjs.Context.eval().
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass

import quickjs

from src.foundation.action import Action, Hold
from src.foundation.sandbox.result import SandboxResult
from src.foundation.sandbox.status import ExecutionStatus


_SANDBOX_PRELUDE = """\
globalThis.Date = undefined;
globalThis.setTimeout = undefined;
globalThis.setInterval = undefined;
globalThis.clearTimeout = undefined;
globalThis.clearInterval = undefined;
globalThis.console = undefined;
globalThis.eval = function(){ throw new Error("eval blocked"); };
globalThis.Function = function(){ throw new Error("Function blocked"); };
Object.freeze(globalThis.Math);
"""


@dataclass
class _QuickJSPlayerContext:
    """Per-player QuickJS state. Sibling of PlayerSandboxContext (Python)."""

    js_context: quickjs.Context
    consecutive_timeout_count: int = 0
    disabled: bool = False
    has_decide: bool = False


class QuickJSSandbox:
    """Sandbox Protocol implementation for JavaScript strategies (ADR-0025)."""

    def __init__(
        self,
        timeout_ms: float = 5.0,
        consecutive_failures_limit: int = 10,
    ) -> None:
        self.timeout_ms = timeout_ms
        self.consecutive_failures_limit = consecutive_failures_limit
        self._contexts: dict[str, _QuickJSPlayerContext] = {}

    @property
    def language(self) -> str:
        return "javascript"

    def compile(self, player_id: str, source: str) -> SandboxResult:
        """Eval prelude + source in a fresh Context, verify decide exists."""
        self._contexts.pop(player_id, None)

        ctx = quickjs.Context()
        try:
            ctx.eval(_SANDBOX_PRELUDE)
            ctx.eval(source)
            ctx.eval("if (typeof decide !== 'function') throw new Error('MissingDecideFunction');")
        except quickjs.JSException as e:
            err_str = str(e)
            if "MissingDecideFunction" in err_str:
                error_type = "MissingDecideFunction"
            else:
                error_type = "JSException"
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type=error_type,
                error_message=err_str,
            )
        except Exception as e:
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type=type(e).__name__,
                error_message=str(e),
            )

        player_ctx = _QuickJSPlayerContext(js_context=ctx, has_decide=True)
        self._contexts[player_id] = player_ctx
        return SandboxResult(status=ExecutionStatus.SUCCESS)

    def execute(
        self,
        player_id: str,
        game_state,
        player_state,
        history,
    ) -> SandboxResult:
        """JSON-bridge marshal, eval decide(...), parse result, normalize via from_tagged()."""
        pctx = self._contexts.get(player_id)
        if pctx is None or not pctx.has_decide:
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type="NoCompiledContext",
            )

        if pctx.disabled:
            return SandboxResult(
                status=ExecutionStatus.DISABLED,
                action=Hold(),
                execution_time_ms=0.0,
            )

        pctx.js_context.set_time_limit(self.timeout_ms / 1000.0)

        serial_start_ns = time.perf_counter_ns()
        args_json = json.dumps([game_state, player_state, history])
        serial_ms = (time.perf_counter_ns() - serial_start_ns) / 1_000_000

        start_ns = time.perf_counter_ns()

        try:
            result_str = pctx.js_context.eval(
                f"JSON.stringify(decide.apply(null, {args_json}))"
            )
        except quickjs.JSException as e:
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
            if "interrupted" in str(e).lower():
                pctx.consecutive_timeout_count += 1
                if pctx.consecutive_timeout_count >= self.consecutive_failures_limit:
                    pctx.disabled = True
                return SandboxResult(
                    status=ExecutionStatus.TIMEOUT,
                    serialization_ms=serial_ms,
                    execution_time_ms=elapsed_ms,
                )
            return SandboxResult(
                status=ExecutionStatus.EXCEPTION,
                serialization_ms=serial_ms,
                execution_time_ms=elapsed_ms,
                error_type="JSException",
            )
        except BaseException as e:
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
            return SandboxResult(
                status=ExecutionStatus.EXCEPTION,
                serialization_ms=serial_ms,
                execution_time_ms=elapsed_ms,
                error_type=type(e).__name__,
            )

        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000

        try:
            tagged = json.loads(result_str) if result_str else None
        except (json.JSONDecodeError, TypeError):
            tagged = None

        if not isinstance(tagged, dict):
            action = Hold()
        else:
            action = Action.from_tagged(tagged)

        pctx.consecutive_timeout_count = 0
        return SandboxResult(
            action=action,
            status=ExecutionStatus.SUCCESS,
            serialization_ms=serial_ms,
            execution_time_ms=elapsed_ms,
        )

    def disable(self, player_id: str) -> None:
        """Manually disable a player's strategy. Raises KeyError if not compiled."""
        self._contexts[player_id].disabled = True