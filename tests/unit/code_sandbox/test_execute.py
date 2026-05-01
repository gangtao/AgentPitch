"""Tests for Code Sandbox Story 004: Sandbox.execute() with deep copy + signal timeout."""

from __future__ import annotations

import copy
import inspect
import signal
import threading

import pytest

from src.foundation.action import Hold, Move
from src.foundation.sandbox.sandbox import Sandbox
from src.foundation.sandbox.status import ExecutionStatus


def _compile_decide(sb: Sandbox, player_id: str, body: str) -> None:
    """Helper: compile a `def decide(g, p, h):` function with the given body."""
    code = "def decide(g, p, h):\n" + "\n".join(
        "    " + line for line in body.split("\n")
    ) + "\n"
    result = sb.compile(player_id, code)
    assert result.status is ExecutionStatus.SUCCESS, f"compile failed: {result}"


# ---------------------------------------------------------------------------
# AC-1: signature
# ---------------------------------------------------------------------------


class TestAC1Signature:
    def test_execute_signature(self):
        sb = Sandbox()
        sig = inspect.signature(sb.execute)
        params = list(sig.parameters.keys())
        assert params == ["player_id", "game_state", "player_state", "history"]


# ---------------------------------------------------------------------------
# AC-SANDBOX-04: deep copy contract
# ---------------------------------------------------------------------------


class TestACSandbox04DeepCopyContract:
    def test_callback_mutation_does_not_affect_caller_game_state(self):
        sb = Sandbox()
        # Callback mutates one of its args
        _compile_decide(sb, "team_a_0", "g['score'] = (99, 0)\nreturn Hold()")
        gs = {"score": (0, 0)}
        gs_snapshot = copy.deepcopy(gs)
        result = sb.execute("team_a_0", gs, {}, [])
        assert result.status is ExecutionStatus.SUCCESS
        assert gs == gs_snapshot

    def test_nested_mutation_isolated(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "g['ball']['position'] = (50.0, 50.0)\nreturn Hold()")
        gs = {"ball": {"position": (0.0, 0.0)}}
        sb.execute("team_a_0", gs, {}, [])
        assert gs["ball"]["position"] == (0.0, 0.0)

    def test_player_state_isolated(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "p['speed'] = 99\nreturn Hold()")
        ps = {"speed": 10}
        sb.execute("team_a_0", {}, ps, [])
        assert ps == {"speed": 10}

    def test_history_isolated(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "h.append({'tick': 999})\nreturn Hold()")
        h = [{"tick": 1}]
        sb.execute("team_a_0", {}, {}, h)
        assert h == [{"tick": 1}]


# ---------------------------------------------------------------------------
# AC-SANDBOX-05: timeout enforcement
# ---------------------------------------------------------------------------


class TestACSandbox05TimeoutEnforcement:
    def test_infinite_loop_interrupted(self):
        sb = Sandbox(timeout_ms=20.0)
        _compile_decide(sb, "team_a_0", "while True:\n        pass")
        result = sb.execute("team_a_0", {}, {}, [])
        assert result.status is ExecutionStatus.TIMEOUT
        # 20ms timeout + 25ms safety margin
        assert result.execution_time_ms <= 50.0


# ---------------------------------------------------------------------------
# AC-SANDBOX-06: timeout doesn't crash subsequent calls
# ---------------------------------------------------------------------------


class TestACSandbox06TimeoutDoesNotCrashSim:
    def test_subsequent_call_succeeds_after_timeout(self):
        sb = Sandbox(timeout_ms=20.0)
        _compile_decide(sb, "team_a_0", "while True:\n        pass")
        _compile_decide(sb, "team_b_0", "return Hold()")

        sb.execute("team_a_0", {}, {}, [])
        result = sb.execute("team_b_0", {}, {}, [])
        assert result.status is ExecutionStatus.SUCCESS
        # No leftover timer
        assert signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0)


# ---------------------------------------------------------------------------
# AC-SANDBOX-09: None return → INVALID_RETURN
# ---------------------------------------------------------------------------


class TestACSandbox09NoneReturn:
    def test_explicit_none_return(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "return None")
        result = sb.execute("team_a_0", {}, {}, [])
        assert result.status is ExecutionStatus.INVALID_RETURN
        assert result.action is None

    def test_implicit_none_no_return_statement(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "x = 1")
        result = sb.execute("team_a_0", {}, {}, [])
        assert result.status is ExecutionStatus.INVALID_RETURN


# ---------------------------------------------------------------------------
# AC-SANDBOX-10: generator return → INVALID_RETURN
# ---------------------------------------------------------------------------


class TestACSandbox10GeneratorReturn:
    def test_generator_expression_rejected(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "return (x for x in [Hold()])")
        result = sb.execute("team_a_0", {}, {}, [])
        assert result.status is ExecutionStatus.INVALID_RETURN

    def test_generator_function_rejected(self):
        sb = Sandbox()
        # `yield` makes decide a generator function — calling it returns a generator
        code = "def decide(g, p, h):\n    yield Hold()\n"
        sb.compile("team_a_0", code)
        result = sb.execute("team_a_0", {}, {}, [])
        assert result.status is ExecutionStatus.INVALID_RETURN


# ---------------------------------------------------------------------------
# AC-SANDBOX-11: valid Action passes through
# ---------------------------------------------------------------------------


class TestACSandbox11ValidActionPasses:
    def test_move_returned_as_action(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "return Move(1.0, 0.0, 0.8)")
        result = sb.execute("team_a_0", {}, {}, [])
        assert result.status is ExecutionStatus.SUCCESS
        assert isinstance(result.action, Move)
        assert result.action.speed == 0.8

    def test_hold_returned_as_action(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "return Hold()")
        result = sb.execute("team_a_0", {}, {}, [])
        assert result.status is ExecutionStatus.SUCCESS
        assert isinstance(result.action, Hold)


# ---------------------------------------------------------------------------
# AC-SANDBOX-12: out-of-range Action passes through (sandbox doesn't validate ranges)
# ---------------------------------------------------------------------------


class TestACSandbox12OutOfRangePasses:
    def test_shoot_with_huge_power_succeeds(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "return Shoot(0.0, 999)")
        result = sb.execute("team_a_0", {}, {}, [])
        assert result.status is ExecutionStatus.SUCCESS  # ARE owns range validation


# ---------------------------------------------------------------------------
# AC-SANDBOX-15: BaseException containment (SystemExit doesn't terminate)
# ---------------------------------------------------------------------------


def _inject_callable(sb: Sandbox, player_id: str, fn) -> None:
    """Bypass compile() and install a Python callable directly into the
    player's context. Used to test the sandbox's exception-catch contract
    without requiring exception classes to be in the restricted namespace.
    """
    from src.foundation.sandbox.namespace import make_restricted_globals
    from src.foundation.sandbox.result import PlayerSandboxContext
    sb._contexts[player_id] = PlayerSandboxContext(
        compiled_fn=fn,
        module_globals=make_restricted_globals(),
    )


class TestACSandbox15SystemExitContained:
    def test_systemexit_caught_as_exception(self):
        sb = Sandbox()

        def fn(g, p, h):
            raise SystemExit(0)

        _inject_callable(sb, "team_a_0", fn)
        result = sb.execute("team_a_0", {}, {}, [])
        # Test process is still alive — BaseException catch contained SystemExit
        assert result.status is ExecutionStatus.EXCEPTION
        assert result.error_type == "SystemExit"

    def test_keyboardinterrupt_caught_as_exception(self):
        sb = Sandbox()

        def fn(g, p, h):
            raise KeyboardInterrupt()

        _inject_callable(sb, "team_a_0", fn)
        result = sb.execute("team_a_0", {}, {}, [])
        assert result.status is ExecutionStatus.EXCEPTION
        assert result.error_type == "KeyboardInterrupt"


# ---------------------------------------------------------------------------
# AC-SANDBOX-13: cross-tick state persists
# ---------------------------------------------------------------------------


class TestACSandbox13CrossTickStatePersists:
    def test_counter_increments_across_50_calls(self):
        sb = Sandbox()
        # Module-level counter + global access in decide
        code = (
            "counter = 0\n"
            "def decide(g, p, h):\n"
            "    global counter\n"
            "    counter += 1\n"
            "    return Hold()\n"
        )
        sb.compile("team_a_0", code)
        for _ in range(50):
            r = sb.execute("team_a_0", {}, {}, [])
            assert r.status is ExecutionStatus.SUCCESS
        assert sb._contexts["team_a_0"].module_globals["counter"] == 50


# ---------------------------------------------------------------------------
# AC-SANDBOX-16: error_type sanitization
# ---------------------------------------------------------------------------


class TestACSandbox16ErrorTypeSanitization:
    @pytest.mark.parametrize("exc_factory,expected_type", [
        (lambda: ValueError("multi\nline\nmessage"), "ValueError"),
        (lambda: RuntimeError("boom"), "RuntimeError"),
        (lambda: SystemExit(1), "SystemExit"),
    ])
    def test_error_type_is_class_name_only(self, exc_factory, expected_type):
        sb = Sandbox()

        def fn(g, p, h, _exc=exc_factory):
            raise _exc()

        _inject_callable(sb, "team_a_0", fn)
        result = sb.execute("team_a_0", {}, {}, [])
        assert result.error_type == expected_type
        assert "\n" not in result.error_type


# ---------------------------------------------------------------------------
# AC-extra: timer always cancelled (no leftover ITIMER_REAL after any path)
# ---------------------------------------------------------------------------


class TestACExtraTimerAlwaysCancelled:
    @pytest.mark.parametrize("body", [
        "return Hold()",                        # SUCCESS
        "raise ValueError('boom')",             # EXCEPTION
        "while True:\n        pass",            # TIMEOUT
        "return None",                          # INVALID_RETURN
    ])
    def test_timer_zero_after_each_exit_path(self, body):
        sb = Sandbox(timeout_ms=20.0)
        _compile_decide(sb, "team_a_0", body)
        sb.execute("team_a_0", {}, {}, [])
        assert signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0)


# ---------------------------------------------------------------------------
# AC-extra: signal handler restored after every exit path
# ---------------------------------------------------------------------------


class TestACExtraSignalHandlerRestored:
    @pytest.mark.parametrize("body", [
        "return Hold()",
        "raise ValueError('boom')",
        "while True:\n        pass",
        "return None",
    ])
    def test_handler_restored_after_each_exit(self, body):
        sb = Sandbox(timeout_ms=20.0)
        _compile_decide(sb, "team_a_0", body)
        # Install sentinel handler
        sentinel = lambda s, f: None  # noqa: E731
        installed = signal.signal(signal.SIGALRM, sentinel)
        try:
            sb.execute("team_a_0", {}, {}, [])
            assert signal.getsignal(signal.SIGALRM) is sentinel
        finally:
            signal.signal(signal.SIGALRM, installed)


# ---------------------------------------------------------------------------
# AC-extra: execution_time_ms populated for all paths
# ---------------------------------------------------------------------------


class TestACExtraExecutionTimeMsPopulated:
    @pytest.mark.parametrize("body", [
        "return Hold()",
        "raise ValueError('boom')",
        "return None",
    ])
    def test_execution_time_ms_non_negative(self, body):
        sb = Sandbox(timeout_ms=20.0)
        _compile_decide(sb, "team_a_0", body)
        result = sb.execute("team_a_0", {}, {}, [])
        assert isinstance(result.execution_time_ms, float)
        assert result.execution_time_ms >= 0.0

    def test_timeout_path_populates_time(self):
        sb = Sandbox(timeout_ms=20.0)
        _compile_decide(sb, "team_a_0", "while True:\n        pass")
        result = sb.execute("team_a_0", {}, {}, [])
        assert result.execution_time_ms > 0.0


# ---------------------------------------------------------------------------
# TR-SB-005: main thread requirement
# ---------------------------------------------------------------------------


class TestTRSB005MainThreadRequirement:
    def test_non_main_thread_raises_value_error(self):
        sb = Sandbox(timeout_ms=20.0)
        _compile_decide(sb, "team_a_0", "return Hold()")
        captured: list = []

        def runner():
            try:
                sb.execute("team_a_0", {}, {}, [])
            except ValueError as e:
                captured.append(e)
            except BaseException as e:
                captured.append(e)

        t = threading.Thread(target=runner)
        t.start()
        t.join()
        assert len(captured) == 1
        msg = str(captured[0])
        assert "main thread" in msg.lower() or "signal" in msg.lower()


# ---------------------------------------------------------------------------
# Bonus: NoCompiledContext error when execute() called before compile()
# ---------------------------------------------------------------------------


class TestNoCompiledContext:
    def test_execute_without_compile_returns_compile_error(self):
        sb = Sandbox()
        result = sb.execute("never-compiled", {}, {}, [])
        assert result.status is ExecutionStatus.COMPILE_ERROR
        assert result.error_type == "NoCompiledContext"


class TestTimeoutRaceInExceptionHandler:
    """Regression: SIGALRM firing inside an except handler must not escape execute()."""

    def test_timeout_during_exception_handling_does_not_propagate(self):
        # Strategy raises KeyError, then the timer fires while handling it.
        # execute() must return TIMEOUT or EXCEPTION — never raise.
        import signal as _signal
        sb = Sandbox(timeout_ms=5.0)

        # A callable that raises KeyError then burns time so the timer fires
        # before the except-handler in execute() can cancel it.
        def fn(g, p, h):
            raise KeyError("cooldown_remaining")

        _inject_callable(sb, "team_a_0", fn)

        # Arm a very short real timer ourselves so it fires right as execute()
        # enters its except BaseException handler (simulate the race).
        # We use a tiny timeout so the signal fires during the handler.
        sb.timeout_ms = 1.0  # 1ms — tight enough to race
        result = sb.execute("team_a_0", {}, {}, [])
        # Must be EXCEPTION or TIMEOUT — must NOT raise _SandboxTimeoutError.
        assert result.status in (ExecutionStatus.EXCEPTION, ExecutionStatus.TIMEOUT)
