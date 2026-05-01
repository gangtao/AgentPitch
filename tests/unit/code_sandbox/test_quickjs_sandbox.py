"""QuickJSSandbox unit tests (ADR-0025).

Tests skip automatically if quickjs is not installed (optional dependency).
"""

from __future__ import annotations

import pytest

quickjs = pytest.importorskip("quickjs")

from src.foundation.sandbox.quickjs_sandbox import QuickJSSandbox
from src.foundation.sandbox.status import ExecutionStatus
from src.foundation.action import Hold, Move, Pass, Shoot, Tackle


VALID_JS = """
function decide(game_state, player_state, history) {
    return { type: "Hold" };
}
"""

SYNTAX_ERROR_JS = "function decide(gs { return null; }"
NO_DECIDE_JS = "var x = 42;"
RUNTIME_ERROR_ON_COMPILE_JS = "throw new Error('kaboom');"
INFINITE_LOOP_JS = "function decide(gs, ps, h) { while(true){} }"

HOLD_JS = """
function decide(game_state, player_state, history) {
    return { type: "Hold" };
}
"""

MOVE_JS = """
function decide(game_state, player_state, history) {
    return { type: "Move", dx: 1.0, dy: -0.5, speed: 0.8 };
}
"""

PASS_JS = """
function decide(game_state, player_state, history) {
    return { type: "Pass", target_pos: [80.0, 30.0], power: 15 };
}
"""

SHOOT_JS = """
function decide(game_state, player_state, history) {
    return { type: "Shoot", angle: 5.0, power: 18 };
}
"""

TACKLE_JS = """
function decide(game_state, player_state, history) {
    return { type: "Tackle", target_player_id: "team_b_2" };
}
"""


# ── Compile tests ─────────────────────────────────────────────────────────

def test_compile_success():
    sb = QuickJSSandbox()
    result = sb.compile("team_a_0", VALID_JS)
    assert result.status == ExecutionStatus.SUCCESS


def test_compile_syntax_error():
    sb = QuickJSSandbox()
    result = sb.compile("team_a_0", SYNTAX_ERROR_JS)
    assert result.status == ExecutionStatus.COMPILE_ERROR


def test_compile_missing_decide():
    sb = QuickJSSandbox()
    result = sb.compile("team_a_0", NO_DECIDE_JS)
    assert result.status == ExecutionStatus.COMPILE_ERROR
    assert result.error_type == "MissingDecideFunction"


def test_compile_runtime_error_in_module():
    sb = QuickJSSandbox()
    result = sb.compile("team_a_0", RUNTIME_ERROR_ON_COMPILE_JS)
    assert result.status == ExecutionStatus.COMPILE_ERROR


def test_compile_replaces_previous_context():
    sb = QuickJSSandbox()
    sb.compile("team_a_0", VALID_JS)
    result = sb.compile("team_a_0", SYNTAX_ERROR_JS)
    assert result.status == ExecutionStatus.COMPILE_ERROR
    exec_result = sb.execute("team_a_0", {}, {}, [])
    assert exec_result.status == ExecutionStatus.COMPILE_ERROR
    assert exec_result.error_type == "NoCompiledContext"


# ── Execute tests ─────────────────────────────────────────────────────────

def test_execute_move():
    sb = QuickJSSandbox()
    sb.compile("p", MOVE_JS)
    result = sb.execute("p", {}, {}, [])
    assert result.status == ExecutionStatus.SUCCESS
    assert isinstance(result.action, Move)
    assert result.action.dx == 1.0
    assert result.action.dy == -0.5
    assert result.action.speed == 0.8
    assert result.execution_time_ms > 0


def test_execute_pass():
    sb = QuickJSSandbox()
    sb.compile("p", PASS_JS)
    result = sb.execute("p", {}, {}, [])
    assert result.status == ExecutionStatus.SUCCESS
    assert isinstance(result.action, Pass)
    assert result.action.target_pos == (80.0, 30.0)
    assert result.action.power == 15


def test_execute_shoot():
    sb = QuickJSSandbox()
    sb.compile("p", SHOOT_JS)
    result = sb.execute("p", {}, {}, [])
    assert result.status == ExecutionStatus.SUCCESS
    assert isinstance(result.action, Shoot)


def test_execute_tackle():
    sb = QuickJSSandbox()
    sb.compile("p", TACKLE_JS)
    result = sb.execute("p", {}, {}, [])
    assert result.status == ExecutionStatus.SUCCESS
    assert isinstance(result.action, Tackle)
    assert result.action.target_player_id == "team_b_2"


def test_execute_hold():
    sb = QuickJSSandbox()
    sb.compile("p", HOLD_JS)
    result = sb.execute("p", {}, {}, [])
    assert result.status == ExecutionStatus.SUCCESS
    assert isinstance(result.action, Hold)


def test_execute_no_compiled_context():
    sb = QuickJSSandbox()
    result = sb.execute("nobody", {}, {}, [])
    assert result.status == ExecutionStatus.COMPILE_ERROR
    assert result.error_type == "NoCompiledContext"


def test_execute_reads_game_state():
    js = """
function decide(game_state, player_state, history) {
    if (game_state.tick > 100) {
        return { type: "Shoot", angle: 0, power: 10 };
    }
    return { type: "Hold" };
}
"""
    sb = QuickJSSandbox()
    sb.compile("p", js)
    r1 = sb.execute("p", {"tick": 50}, {}, [])
    assert isinstance(r1.action, Hold)
    r2 = sb.execute("p", {"tick": 200}, {}, [])
    assert isinstance(r2.action, Shoot)


def test_execute_invalid_return_becomes_hold():
    js = 'function decide(gs, ps, h) { return 42; }'
    sb = QuickJSSandbox()
    sb.compile("p", js)
    result = sb.execute("p", {}, {}, [])
    assert result.status == ExecutionStatus.SUCCESS
    assert isinstance(result.action, Hold)


def test_execute_null_return_becomes_hold():
    js = 'function decide(gs, ps, h) { return null; }'
    sb = QuickJSSandbox()
    sb.compile("p", js)
    result = sb.execute("p", {}, {}, [])
    assert result.status == ExecutionStatus.SUCCESS
    assert isinstance(result.action, Hold)


def test_execute_exception_contained():
    js = 'function decide(gs, ps, h) { throw new Error("boom"); }'
    sb = QuickJSSandbox()
    sb.compile("p", js)
    result = sb.execute("p", {}, {}, [])
    assert result.status == ExecutionStatus.EXCEPTION
    assert result.error_type == "JSException"
    assert result.execution_time_ms > 0


# ── Timeout + Circuit Breaker ─────────────────────────────────────────────

def test_execute_timeout():
    sb = QuickJSSandbox(timeout_ms=5.0)
    sb.compile("p", INFINITE_LOOP_JS)
    result = sb.execute("p", {}, {}, [])
    assert result.status == ExecutionStatus.TIMEOUT
    assert result.execution_time_ms < 50.0


def test_circuit_breaker_disables_after_limit():
    sb = QuickJSSandbox(timeout_ms=5.0, consecutive_failures_limit=3)
    sb.compile("p", INFINITE_LOOP_JS)
    for _ in range(3):
        r = sb.execute("p", {}, {}, [])
        assert r.status == ExecutionStatus.TIMEOUT
    r = sb.execute("p", {}, {}, [])
    assert r.status == ExecutionStatus.DISABLED
    assert isinstance(r.action, Hold)


def test_successful_execute_resets_timeout_counter():
    sb = QuickJSSandbox(timeout_ms=5.0, consecutive_failures_limit=3)
    sb.compile("p", INFINITE_LOOP_JS)
    sb.execute("p", {}, {}, [])
    sb.execute("p", {}, {}, [])
    sb.compile("p", HOLD_JS)
    r = sb.execute("p", {}, {}, [])
    assert r.status == ExecutionStatus.SUCCESS
    sb.compile("p", INFINITE_LOOP_JS)
    sb.execute("p", {}, {}, [])
    sb.execute("p", {}, {}, [])
    r = sb.execute("p", {}, {}, [])
    assert r.status == ExecutionStatus.TIMEOUT


# ── Disable ───────────────────────────────────────────────────────────────

def test_disable():
    sb = QuickJSSandbox()
    sb.compile("p", HOLD_JS)
    sb.disable("p")
    result = sb.execute("p", {}, {}, [])
    assert result.status == ExecutionStatus.DISABLED
    assert isinstance(result.action, Hold)


def test_disable_missing_player_raises():
    sb = QuickJSSandbox()
    with pytest.raises(KeyError):
        sb.disable("nobody")


# ── Cross-player isolation ────────────────────────────────────────────────

def test_cross_player_isolation():
    sb = QuickJSSandbox()
    js_a = """
var leaked = "secret";
Object.prototype.injected = true;
function decide(gs, ps, h) { return { type: "Hold" }; }
"""
    js_b = """
function decide(gs, ps, h) {
    var leakSeen = (typeof leaked !== "undefined");
    var protoPolluted = (({}).injected === true);
    return {
        type: "Move",
        dx: leakSeen ? 1.0 : 0.0,
        dy: protoPolluted ? 1.0 : 0.0,
        speed: 1.0
    };
}
"""
    sb.compile("a", js_a)
    sb.execute("a", {}, {}, [])
    sb.compile("b", js_b)
    result = sb.execute("b", {}, {}, [])
    assert isinstance(result.action, Move)
    assert result.action.dx == 0.0, "leaked var visible across contexts"
    assert result.action.dy == 0.0, "prototype pollution across contexts"


# ── Cross-tick state persistence (CR-5) ───────────────────────────────────

def test_cross_tick_state_persistence():
    js = """
var counter = 0;
function decide(gs, ps, h) {
    counter++;
    return { type: "Move", dx: counter, dy: 0, speed: 1.0 };
}
"""
    sb = QuickJSSandbox()
    sb.compile("p", js)
    r1 = sb.execute("p", {}, {}, [])
    r2 = sb.execute("p", {}, {}, [])
    r3 = sb.execute("p", {}, {}, [])
    assert r1.action.dx == 1.0
    assert r2.action.dx == 2.0
    assert r3.action.dx == 3.0


# ── Blocked globals ───────────────────────────────────────────────────────

def test_blocked_globals():
    js = """
function decide(gs, ps, h) {
    var evalBlocked = false;
    try { eval("1+1"); } catch(e) { evalBlocked = true; }
    var fnBlocked = false;
    try { new Function("return 1")(); } catch(e) { fnBlocked = true; }
    return {
        type: "Move",
        dx: (typeof Date === "undefined") ? 1.0 : 0.0,
        dy: evalBlocked ? 1.0 : 0.0,
        speed: fnBlocked ? 1.0 : 0.0
    };
}
"""
    sb = QuickJSSandbox()
    sb.compile("p", js)
    result = sb.execute("p", {}, {}, [])
    assert isinstance(result.action, Move)
    assert result.action.dx == 1.0, "Date should be blocked"
    assert result.action.dy == 1.0, "eval should be blocked"
    assert result.action.speed == 1.0, "Function constructor should be blocked"


# ── Math exposure ─────────────────────────────────────────────────────────

def test_math_available():
    js = """
function decide(gs, ps, h) {
    return { type: "Move", dx: Math.sqrt(4), dy: Math.floor(Math.PI), speed: 1.0 };
}
"""
    sb = QuickJSSandbox()
    sb.compile("p", js)
    result = sb.execute("p", {}, {}, [])
    assert result.action.dx == 2.0
    assert result.action.dy == 3.0


# ── Language property ─────────────────────────────────────────────────────

def test_language_property():
    sb = QuickJSSandbox()
    assert sb.language == "javascript"