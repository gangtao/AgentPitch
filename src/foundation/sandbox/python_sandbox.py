"""RestrictedPython-based sandbox — public entry points for compile() and execute().

This is the **designated sandbox module** per technical-preferences.md, so
`exec()` is permitted here (and required for module-body evaluation of
RestrictedPython-compiled code). All other modules MUST NOT use exec().

Per ADR-0001 + ADR-0012.
"""

from __future__ import annotations

import copy
import inspect
import signal
import time
from typing import Dict

from RestrictedPython import compile_restricted

from src.foundation.action import Action, Hold
from src.foundation.sandbox.namespace import make_restricted_globals
from src.foundation.sandbox.result import PlayerSandboxContext, SandboxResult
from src.foundation.sandbox.status import ExecutionStatus


class _SandboxTimeoutError(BaseException):
    """Sentinel raised by the SIGALRM handler. Subclasses BaseException so
    LLM-generated `try: ... except Exception:` blocks cannot swallow it.
    """


def _timeout_handler(signum, frame):
    raise _SandboxTimeoutError()


class RestrictedPythonSandbox:
    """RestrictedPython-based sandbox — the original ADR-0001 implementation.

    Renamed from ``Sandbox`` per ADR-0024 (sandbox protocol abstraction).
    """

    def __init__(
        self,
        timeout_ms: float = 5.0,
        consecutive_failures_limit: int = 10,
    ) -> None:
        self.timeout_ms = timeout_ms
        self.consecutive_failures_limit = consecutive_failures_limit
        self._contexts: Dict[str, PlayerSandboxContext] = {}

    @property
    def language(self) -> str:
        return "python"

    def compile(self, player_id: str, code_str: str) -> SandboxResult:
        """Compile LLM-generated strategy code into a callable `decide` function.

        Stores the compiled function and module globals in the player's context
        on success. Returns SandboxResult — never raises on user-supplied
        invalid code.

        Per AC-7: a fresh context is installed UNCONDITIONALLY (recompile must
        replace any prior state, even if the new code fails to compile).
        """
        # Always start with a fresh context — recompile semantics
        ctx = PlayerSandboxContext(module_globals=make_restricted_globals())
        self._contexts[player_id] = ctx

        # Step 1: AST-level compile via RestrictedPython
        try:
            compiled = compile_restricted(code_str, "<strategy>", "exec")
        except SyntaxError as e:
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type="SyntaxError",
                error_message=str(e),
            )
        except BaseException as e:  # noqa: BLE001 — defensive: RestrictedPython internals
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type=type(e).__name__,
                error_message=str(e),
            )

        # Step 2: execute the module body in the restricted namespace
        try:
            exec(compiled, ctx.module_globals)  # noqa: S102 — designated sandbox module
        except BaseException as e:  # noqa: BLE001 — module-level exec must not crash startup
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type=type(e).__name__,
                error_message=str(e),
            )

        # Step 3: verify a callable `decide` symbol is present
        decide = ctx.module_globals.get("decide")
        if decide is None or not callable(decide):
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type="MissingDecideFunction",
            )

        ctx.compiled_fn = decide
        return SandboxResult(status=ExecutionStatus.SUCCESS)

    def execute(
        self,
        player_id: str,
        game_state,
        player_state,
        history,
    ) -> SandboxResult:
        """Run the player's compiled `decide` callback within a 5ms wall-clock budget.

        Deep-copies all 3 args, arms `signal.setitimer(ITIMER_REAL)`, calls
        `compiled_fn(...)`, validates the return is an `Action` (rejects
        generators/coroutines/None), catches `BaseException` so SystemExit and
        KeyboardInterrupt are contained.

        Returns SandboxResult; never raises (callback failures contained).

        Main thread only — `signal.setitimer` requires it (per ADR-0001).
        """
        ctx = self._contexts.get(player_id)
        if ctx is None:
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type="NoCompiledContext",
            )

        # DISABLED short-circuit — pre-fills Hold() per ADR-0012.
        # Fresh Hold() per call (no shared singleton) so downstream code can't
        # mutate "the" Hold and corrupt future returns.
        if ctx.disabled:
            return SandboxResult(
                status=ExecutionStatus.DISABLED,
                action=Hold(),
                execution_time_ms=0.0,
            )

        # Deep-copy BEFORE arming timer (deep-copy is bounded; not subject to timeout).
        # Timed separately so callers can distinguish serialisation vs execution cost.
        serial_start_ns = time.perf_counter_ns()
        gs_copy = copy.deepcopy(game_state)
        ps_copy = copy.deepcopy(player_state)
        h_copy = copy.deepcopy(history)
        serial_ms = (time.perf_counter_ns() - serial_start_ns) / 1_000_000

        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, self.timeout_ms / 1000.0)
        start_ns = time.perf_counter_ns()

        try:
            try:
                result = ctx.compiled_fn(gs_copy, ps_copy, h_copy)
            except _SandboxTimeoutError:
                elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
                ctx.consecutive_timeout_count += 1
                # Circuit breaker — fire DISABLED after `consecutive_failures_limit`
                # consecutive timeouts. The 11th call (default limit=10) will short-
                # circuit at the top of the function on the next execute().
                if ctx.consecutive_timeout_count >= self.consecutive_failures_limit:
                    ctx.disabled = True
                return SandboxResult(
                    status=ExecutionStatus.TIMEOUT,
                    serialization_ms=serial_ms,
                    execution_time_ms=elapsed_ms,
                )
            except BaseException as e:  # noqa: BLE001 — must contain SystemExit/KeyboardInterrupt
                # Cancel timer immediately so the signal cannot fire while we
                # compute elapsed_ms (SIGALRM can fire between bytecodes inside
                # an except handler, raising _SandboxTimeoutError a second time).
                signal.setitimer(signal.ITIMER_REAL, 0)
                elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
                return SandboxResult(
                    status=ExecutionStatus.EXCEPTION,
                    serialization_ms=serial_ms,
                    execution_time_ms=elapsed_ms,
                    error_type=type(e).__name__,
                )
        except _SandboxTimeoutError:
            # Safety net: timer fired inside an exception handler before the
            # setitimer(0) call above could execute.
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
            ctx.consecutive_timeout_count += 1
            if ctx.consecutive_timeout_count >= self.consecutive_failures_limit:
                ctx.disabled = True
            return SandboxResult(
                status=ExecutionStatus.TIMEOUT,
                serialization_ms=serial_ms,
                execution_time_ms=elapsed_ms,
            )
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)  # cancel any pending timer
            signal.signal(signal.SIGALRM, old_handler)  # restore prior handler

        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000

        # Return validation — sandbox owns isinstance check only (parameter
        # range validation is ARE's job, per AC-SANDBOX-12).
        if (
            not isinstance(result, Action)
            or inspect.isgenerator(result)
            or inspect.iscoroutine(result)
        ):
            return SandboxResult(
                status=ExecutionStatus.INVALID_RETURN,
                serialization_ms=serial_ms,
                execution_time_ms=elapsed_ms,
            )

        # Success — reset timeout counter (a single good tick clears the streak,
        # per GDD EC-SANDBOX-10).
        ctx.consecutive_timeout_count = 0
        return SandboxResult(
            action=result,
            status=ExecutionStatus.SUCCESS,
            serialization_ms=serial_ms,
            execution_time_ms=elapsed_ms,
        )

    def disable(self, player_id: str) -> None:
        """Manually disable a player's callback.

        Subsequent execute() calls return DISABLED + Hold() without invoking
        the callback. Idempotent (calling twice is a no-op).

        Used by the Tick Engine on COMPILE_ERROR at match start: build the
        FallbackEvent at tick=0, then call disable() so subsequent ticks
        return DISABLED normally per ADR-0012.

        Raises:
            KeyError: if player_id has no compiled context.
        """
        ctx = self._contexts[player_id]  # KeyError surfaces caller bugs
        ctx.disabled = True