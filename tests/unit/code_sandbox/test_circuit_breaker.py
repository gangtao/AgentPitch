"""Tests for Code Sandbox Story 005: circuit breaker + Sandbox.disable()."""

from __future__ import annotations

import pytest

from src.foundation.action import Hold
from src.foundation.sandbox.namespace import make_restricted_globals
from src.foundation.sandbox.result import PlayerSandboxContext
from src.foundation.sandbox.sandbox import Sandbox
from src.foundation.sandbox.status import ExecutionStatus


def _compile_decide(sb: Sandbox, player_id: str, body: str) -> None:
    code = "def decide(g, p, h):\n" + "\n".join(
        "    " + line for line in body.split("\n")
    ) + "\n"
    sb.compile(player_id, code)


def _inject_callable(sb: Sandbox, player_id: str, fn) -> PlayerSandboxContext:
    """Bypass compile() and install a Python callable directly into the context."""
    sb._contexts[player_id] = PlayerSandboxContext(
        compiled_fn=fn,
        module_globals=make_restricted_globals(),
    )
    return sb._contexts[player_id]


# ---------------------------------------------------------------------------
# AC-1: disable() public API
# ---------------------------------------------------------------------------


class TestAC1DisableAPI:
    def test_disable_sets_flag(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "return Hold()")
        sb.disable("team_a_0")
        assert sb._contexts["team_a_0"].disabled is True

    def test_disable_is_idempotent(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "return Hold()")
        sb.disable("team_a_0")
        sb.disable("team_a_0")  # no raise
        assert sb._contexts["team_a_0"].disabled is True

    def test_disable_unknown_player_raises_keyerror(self):
        sb = Sandbox()
        with pytest.raises(KeyError):
            sb.disable("team_c_0")


# ---------------------------------------------------------------------------
# AC-SANDBOX-07: circuit breaker fires at limit
# ---------------------------------------------------------------------------


class TestACSandbox07CircuitBreakerFires:
    def test_disable_triggers_after_exact_limit(self):
        sb = Sandbox(timeout_ms=20.0, consecutive_failures_limit=3)
        _compile_decide(sb, "team_a_0", "while True:\n        pass")
        # 3 consecutive timeouts should trigger DISABLED
        for i in range(3):
            r = sb.execute("team_a_0", {}, {}, [])
            assert r.status is ExecutionStatus.TIMEOUT, f"call {i+1}"
        # After the 3rd timeout, ctx.disabled is True
        assert sb._contexts["team_a_0"].disabled is True
        # 4th call short-circuits to DISABLED — does NOT execute callback
        r4 = sb.execute("team_a_0", {}, {}, [])
        assert r4.status is ExecutionStatus.DISABLED
        assert isinstance(r4.action, Hold)

    def test_callback_not_invoked_after_disabled(self):
        sb = Sandbox(timeout_ms=20.0, consecutive_failures_limit=2)
        # Use injected callable so we can count actual invocations
        call_count = {"n": 0}

        def fn(g, p, h):
            call_count["n"] += 1
            # Spin to force timeout
            while True:
                pass

        _inject_callable(sb, "team_a_0", fn)
        sb.execute("team_a_0", {}, {}, [])
        sb.execute("team_a_0", {}, {}, [])
        assert sb._contexts["team_a_0"].disabled is True
        assert call_count["n"] == 2
        # Subsequent calls do NOT increment
        sb.execute("team_a_0", {}, {}, [])
        sb.execute("team_a_0", {}, {}, [])
        assert call_count["n"] == 2


# ---------------------------------------------------------------------------
# AC-SANDBOX-08: reset on success
# ---------------------------------------------------------------------------


class TestACSandbox08ResetOnSuccess:
    def test_success_resets_counter(self):
        sb = Sandbox(timeout_ms=20.0, consecutive_failures_limit=10)

        # Toggle behaviour via a closure flag
        mode = {"timeout": True}

        def fn(g, p, h):
            if mode["timeout"]:
                while True:
                    pass
            return Hold()

        _inject_callable(sb, "team_a_0", fn)

        # 9 timeouts
        for _ in range(9):
            sb.execute("team_a_0", {}, {}, [])
        assert sb._contexts["team_a_0"].consecutive_timeout_count == 9
        assert sb._contexts["team_a_0"].disabled is False

        # 1 success — resets counter to 0
        mode["timeout"] = False
        r = sb.execute("team_a_0", {}, {}, [])
        assert r.status is ExecutionStatus.SUCCESS
        assert sb._contexts["team_a_0"].consecutive_timeout_count == 0

        # 1 more timeout — counter back to 1, NOT disabled
        mode["timeout"] = True
        sb.execute("team_a_0", {}, {}, [])
        assert sb._contexts["team_a_0"].consecutive_timeout_count == 1
        assert sb._contexts["team_a_0"].disabled is False


# ---------------------------------------------------------------------------
# AC-extra: EXCEPTION does not increment counter
# ---------------------------------------------------------------------------


class TestACExtraExceptionDoesNotIncrement:
    def test_20_exceptions_no_disable(self):
        sb = Sandbox(consecutive_failures_limit=10)

        def fn(g, p, h):
            raise ValueError("boom")

        _inject_callable(sb, "team_a_0", fn)
        for _ in range(20):
            r = sb.execute("team_a_0", {}, {}, [])
            assert r.status is ExecutionStatus.EXCEPTION
        assert sb._contexts["team_a_0"].consecutive_timeout_count == 0
        assert sb._contexts["team_a_0"].disabled is False

    def test_invalid_return_does_not_increment(self):
        sb = Sandbox(consecutive_failures_limit=10)

        def fn(g, p, h):
            return None

        _inject_callable(sb, "team_a_0", fn)
        for _ in range(20):
            r = sb.execute("team_a_0", {}, {}, [])
            assert r.status is ExecutionStatus.INVALID_RETURN
        assert sb._contexts["team_a_0"].consecutive_timeout_count == 0
        assert sb._contexts["team_a_0"].disabled is False


# ---------------------------------------------------------------------------
# AC-3: DISABLED short-circuit
# ---------------------------------------------------------------------------


class TestAC3DisabledShortCircuit:
    def test_disabled_returns_status_action_zero_time(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "return Hold()")
        sb.disable("team_a_0")
        r = sb.execute("team_a_0", {}, {}, [])
        assert r.status is ExecutionStatus.DISABLED
        assert isinstance(r.action, Hold)
        assert r.execution_time_ms == 0.0

    def test_callback_not_invoked_when_disabled(self):
        sb = Sandbox()
        call_count = {"n": 0}

        def fn(g, p, h):
            call_count["n"] += 1
            return Hold()

        ctx = _inject_callable(sb, "team_a_0", fn)
        ctx.disabled = True
        for _ in range(5):
            sb.execute("team_a_0", {}, {}, [])
        assert call_count["n"] == 0


# ---------------------------------------------------------------------------
# AC-SANDBOX-18: fresh sandbox starts clean
# ---------------------------------------------------------------------------


class TestACSandbox18FreshSandboxClean:
    def test_new_sandbox_no_disabled_state(self):
        sb1 = Sandbox(consecutive_failures_limit=2)

        def fn_timeout(g, p, h):
            while True:
                pass

        _inject_callable(sb1, "team_a_0", fn_timeout)
        # Trigger DISABLED
        sb1.execute("team_a_0", {}, {}, [])
        sb1.execute("team_a_0", {}, {}, [])
        assert sb1._contexts["team_a_0"].disabled is True

        # New sandbox — no shared state
        sb2 = Sandbox()
        _compile_decide(sb2, "team_a_0", "return Hold()")
        assert sb2._contexts["team_a_0"].disabled is False
        r = sb2.execute("team_a_0", {}, {}, [])
        assert r.status is ExecutionStatus.SUCCESS

    def test_recompile_resets_disabled_flag(self):
        # Story 003 AC-7: recompile replaces context entirely.
        sb = Sandbox(consecutive_failures_limit=2)

        def fn_timeout(g, p, h):
            while True:
                pass

        _inject_callable(sb, "team_a_0", fn_timeout)
        sb.execute("team_a_0", {}, {}, [])
        sb.execute("team_a_0", {}, {}, [])
        assert sb._contexts["team_a_0"].disabled is True

        # Recompile — fresh context
        _compile_decide(sb, "team_a_0", "return Hold()")
        assert sb._contexts["team_a_0"].disabled is False
        assert sb._contexts["team_a_0"].consecutive_timeout_count == 0


# ---------------------------------------------------------------------------
# AC-extra: Hold() is fresh per call (no shared singleton)
# ---------------------------------------------------------------------------


class TestACExtraHoldFreshPerCall:
    def test_two_disabled_returns_have_distinct_hold_instances(self):
        sb = Sandbox()
        _compile_decide(sb, "team_a_0", "return Hold()")
        sb.disable("team_a_0")
        r1 = sb.execute("team_a_0", {}, {}, [])
        r2 = sb.execute("team_a_0", {}, {}, [])
        assert r1.action is not r2.action  # distinct instances
        assert isinstance(r1.action, Hold) and isinstance(r2.action, Hold)


# ---------------------------------------------------------------------------
# AC-extra: manual disable matches auto disable
# ---------------------------------------------------------------------------


class TestACExtraManualMatchesAuto:
    def test_manual_and_auto_disabled_produce_same_result_shape(self):
        sb_auto = Sandbox(consecutive_failures_limit=2)

        def fn_timeout(g, p, h):
            while True:
                pass

        _inject_callable(sb_auto, "team_a_0", fn_timeout)
        sb_auto.execute("team_a_0", {}, {}, [])
        sb_auto.execute("team_a_0", {}, {}, [])
        r_auto = sb_auto.execute("team_a_0", {}, {}, [])

        sb_manual = Sandbox()
        _compile_decide(sb_manual, "team_a_0", "return Hold()")
        sb_manual.disable("team_a_0")
        r_manual = sb_manual.execute("team_a_0", {}, {}, [])

        assert r_auto.status is r_manual.status is ExecutionStatus.DISABLED
        assert isinstance(r_auto.action, Hold)
        assert isinstance(r_manual.action, Hold)
        assert r_auto.execution_time_ms == r_manual.execution_time_ms == 0.0


# ---------------------------------------------------------------------------
# AC-extra: configurable per-instance limit
# ---------------------------------------------------------------------------


class TestACExtraConfigurableLimit:
    def test_per_instance_limit(self):
        sb_a = Sandbox(timeout_ms=20.0, consecutive_failures_limit=2)
        sb_b = Sandbox(timeout_ms=20.0, consecutive_failures_limit=5)

        def fn(g, p, h):
            while True:
                pass

        _inject_callable(sb_a, "p", fn)
        _inject_callable(sb_b, "p", fn)

        for _ in range(3):
            sb_a.execute("p", {}, {}, [])
            sb_b.execute("p", {}, {}, [])

        assert sb_a._contexts["p"].disabled is True
        assert sb_b._contexts["p"].disabled is False
