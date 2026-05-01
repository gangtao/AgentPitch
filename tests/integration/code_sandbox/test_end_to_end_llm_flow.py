"""Integration tests for Code Sandbox Story 006: end-to-end LLM-style flow.

Validates the integrated `compile()` → `execute()` → DISABLED flow on
representative strategies that mimic LLM-generated `decide()` callbacks.

Uses real `Sandbox`, real `RestrictedPython`, real `signal.setitimer`,
real Action classes — no mocks except for collecting status coverage in AC-INT-10.

Per ADR-0001 Day-1 spike validation criteria + ADR-0012 status enum coverage.
"""

from __future__ import annotations

import pytest

from src.foundation.action import Action, Hold, Move, Pass, Shoot, Tackle
from src.foundation.sandbox.result import PlayerSandboxContext, SandboxResult
from src.foundation.sandbox.sandbox import Sandbox
from src.foundation.sandbox.namespace import make_restricted_globals
from src.foundation.sandbox.status import ExecutionStatus


# Module-level status-coverage collector for AC-INT-10
_OBSERVED_STATUSES: set = set()


def _observe(result: SandboxResult) -> SandboxResult:
    """Record observed ExecutionStatus and pass through."""
    _OBSERVED_STATUSES.add(result.status)
    return result


# ---------------------------------------------------------------------------
# Realistic strategy fixtures (mimic CGP-generated code)
# ---------------------------------------------------------------------------


# Uses list comprehension + filter + sorted + has_ball check
REALISTIC_STRATEGY = """
last_ball_x = 0.0

def decide(game_state, player_state, history):
    global last_ball_x
    ball = game_state['ball']
    last_ball_x = ball['position'][0]

    teammates = [p for p in game_state['players'] if p['team'] == player_state['team']]
    opponents = [p for p in game_state['players'] if p['team'] != player_state['team']]

    if player_state['has_ball']:
        return Pass((80.0, 30.0), 15)

    # Find closest opponent without lambda (RestrictedPython-safe)
    closest_dist = 999.0
    for opp in opponents:
        dx = opp['position'][0] - player_state['position'][0]
        adx = abs(dx)
        if adx < closest_dist:
            closest_dist = adx

    if closest_dist < 5.0:
        return Hold()
    return Move(1.0, 0.0, 0.7)
"""

# Module-level dict accumulating per-tick state
STATEFUL_STRATEGY = """
ball_history = []

def decide(game_state, player_state, history):
    global ball_history
    pos = game_state['ball']['position']
    ball_history = ball_history + [pos]
    return Hold()
"""

# Uses sorted + enumerate + zip + Tackle
DEFENSIVE_STRATEGY = """
def decide(game_state, player_state, history):
    opponents = [p for p in game_state['players'] if p['team'] != player_state['team']]
    sorted_opps = sorted(opponents, key=None)  # sort by dict identity (deterministic on same data)
    indexed = list(enumerate(sorted_opps))
    ranks = list(zip(range(len(sorted_opps)), sorted_opps))

    if len(opponents) > 0:
        return Tackle('team_b_0')
    return Hold()
"""

# Cross-tick counter
COUNTER_STRATEGY = """
tick_counter = 0

def decide(game_state, player_state, history):
    global tick_counter
    tick_counter += 1
    return Hold()
"""

# Mutator (for AC-INT-5 deep copy test)
MUTATOR_STRATEGY = """
def decide(game_state, player_state, history):
    game_state['ball']['position'] = [99.0, 99.0]
    return Hold()
"""

# Player-A vs Player-B markers (for AC-INT-7 isolation test)
MARKER_A_STRATEGY = """
marker = 'a'
counter = 0

def decide(game_state, player_state, history):
    global counter
    counter += 1
    return Hold()
"""

MARKER_B_STRATEGY = """
counter = 0

def decide(game_state, player_state, history):
    global counter
    counter += 1
    return Hold()
"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_game_state(tick: int = 0):
    return {
        "tick": tick,
        "ball": {"position": [50.0, 30.0], "velocity": [0.0, 0.0]},
        "players": [
            {"id": "team_a_0", "team": "team_a", "position": [10.0, 30.0]},
            {"id": "team_b_0", "team": "team_b", "position": [90.0, 30.0]},
        ],
    }


def _make_player_state(team: str = "team_a", has_ball: bool = False):
    return {
        "id": f"{team}_0",
        "team": team,
        "position": [10.0, 30.0] if team == "team_a" else [90.0, 30.0],
        "has_ball": has_ball,
    }


def _inject_callable(sb: Sandbox, player_id: str, fn):
    sb._contexts[player_id] = PlayerSandboxContext(
        compiled_fn=fn,
        module_globals=make_restricted_globals(),
    )


# ---------------------------------------------------------------------------
# AC-INT-1: realistic strategy compiles + executes 100 ticks
# ---------------------------------------------------------------------------


class TestACINT1RealisticStrategyRuns100Ticks:
    def test_realistic_strategy_runs_100_ticks(self):
        sb = Sandbox()
        compile_result = sb.compile("team_a_0", REALISTIC_STRATEGY)
        _observe(compile_result)
        assert compile_result.status is ExecutionStatus.SUCCESS

        for tick in range(100):
            r = _observe(sb.execute(
                "team_a_0",
                _make_game_state(tick),
                _make_player_state(),
                [],
            ))
            assert r.status is ExecutionStatus.SUCCESS
            assert isinstance(r.action, (Move, Pass, Hold))

        # Cross-tick state survived
        assert sb._contexts["team_a_0"].module_globals["last_ball_x"] == 50.0


# ---------------------------------------------------------------------------
# AC-INT-2: namespace blocks open / __import__ / class traversal
# ---------------------------------------------------------------------------


class TestACINT2NamespaceBlocksDangerousAccess:
    def test_open_call_blocked(self):
        sb = Sandbox()
        code = "def decide(g, p, h):\n    f = open('/etc/passwd')\n    return Hold()\n"
        compile_result = sb.compile("team_a_0", code)
        _observe(compile_result)
        if compile_result.status is ExecutionStatus.COMPILE_ERROR:
            return  # rejected at compile time — ✓
        # Or rejected at runtime
        r = _observe(sb.execute("team_a_0", {}, {}, []))
        assert r.status is ExecutionStatus.EXCEPTION

    def test_dunder_import_call_rejected_at_compile(self):
        sb = Sandbox()
        code = "def decide(g, p, h):\n    __import__('os').getcwd()\n    return Hold()\n"
        result = sb.compile("team_a_0", code)
        _observe(result)
        # RestrictedPython rejects names starting with _ at compile time
        assert result.status is ExecutionStatus.COMPILE_ERROR

    def test_class_traversal_escape_rejected(self):
        sb = Sandbox()
        code = (
            "def decide(g, p, h):\n"
            "    subs = ().__class__.__bases__[0].__subclasses__()\n"
            "    return Hold()\n"
        )
        result = sb.compile("team_a_0", code)
        _observe(result)
        # `.__class__` etc. start with `_` — rejected at compile
        assert result.status is ExecutionStatus.COMPILE_ERROR

    def test_type_mro_traversal_rejected(self):
        sb = Sandbox()
        code = "def decide(g, p, h):\n    type(1).__mro__\n    return Hold()\n"
        result = sb.compile("team_a_0", code)
        _observe(result)
        # `.__mro__` starts with `_` — rejected at compile
        assert result.status is ExecutionStatus.COMPILE_ERROR

    def test_simulation_continues_after_blocked_attempts(self):
        # After a series of blocked attempts on player A, player B's healthy
        # callback still works.
        sb = Sandbox()
        for bad_code in (
            "def decide(g, p, h):\n    f = open('/etc/passwd')\n    return Hold()\n",
            "def decide(g, p, h):\n    __import__('os')\n    return Hold()\n",
        ):
            sb.compile("team_a_0", bad_code)

        sb.compile("team_b_0", "def decide(g, p, h):\n    return Hold()\n")
        r = _observe(sb.execute("team_b_0", {}, {}, []))
        assert r.status is ExecutionStatus.SUCCESS


# ---------------------------------------------------------------------------
# AC-INT-3: timeout interrupt + recovery on next call
# ---------------------------------------------------------------------------


class TestACINT3TimeoutAndRecovery:
    def test_infinite_loop_interrupted(self):
        sb = Sandbox(timeout_ms=20.0)
        sb.compile("team_a_0", "def decide(g, p, h):\n    while True:\n        pass\n")
        r = _observe(sb.execute("team_a_0", {}, {}, []))
        assert r.status is ExecutionStatus.TIMEOUT
        assert r.execution_time_ms <= 50.0  # 20ms + safety margin

    def test_recovery_on_next_call_for_different_player(self):
        sb = Sandbox(timeout_ms=20.0)
        sb.compile("team_a_0", "def decide(g, p, h):\n    while True:\n        pass\n")
        sb.compile("team_b_0", "def decide(g, p, h):\n    return Hold()\n")
        sb.execute("team_a_0", {}, {}, [])  # times out
        r = _observe(sb.execute("team_b_0", {}, {}, []))  # healthy
        assert r.status is ExecutionStatus.SUCCESS


# ---------------------------------------------------------------------------
# AC-INT-4: circuit breaker fires + recompile reset
# ---------------------------------------------------------------------------


class TestACINT4CircuitBreakerAndRecompile:
    def test_circuit_breaker_fires_at_limit_10(self):
        sb = Sandbox(timeout_ms=20.0, consecutive_failures_limit=10)
        sb.compile("team_a_0", "def decide(g, p, h):\n    while True:\n        pass\n")
        for i in range(10):
            r = sb.execute("team_a_0", {}, {}, [])
            assert r.status is ExecutionStatus.TIMEOUT, f"call {i+1}"
        assert sb._contexts["team_a_0"].disabled is True
        r11 = _observe(sb.execute("team_a_0", {}, {}, []))
        assert r11.status is ExecutionStatus.DISABLED
        assert isinstance(r11.action, Hold)

    def test_recompile_resets_disabled(self):
        sb = Sandbox(timeout_ms=20.0, consecutive_failures_limit=2)
        sb.compile("team_a_0", "def decide(g, p, h):\n    while True:\n        pass\n")
        sb.execute("team_a_0", {}, {}, [])
        sb.execute("team_a_0", {}, {}, [])
        assert sb._contexts["team_a_0"].disabled is True
        # Recompile with healthy code
        sb.compile("team_a_0", "def decide(g, p, h):\n    return Hold()\n")
        assert sb._contexts["team_a_0"].disabled is False
        r = _observe(sb.execute("team_a_0", {}, {}, []))
        assert r.status is ExecutionStatus.SUCCESS


# ---------------------------------------------------------------------------
# AC-INT-5: deep copy isolates mutation
# ---------------------------------------------------------------------------


class TestACINT5DeepCopyIsolates:
    def test_mutator_does_not_affect_original_game_state(self):
        sb = Sandbox()
        sb.compile("team_a_0", MUTATOR_STRATEGY)
        gs = _make_game_state()
        original_position = list(gs["ball"]["position"])
        r = _observe(sb.execute("team_a_0", gs, _make_player_state(), []))
        assert r.status is ExecutionStatus.SUCCESS
        # Original game_state untouched
        assert gs["ball"]["position"] == original_position


# ---------------------------------------------------------------------------
# AC-INT-6: cross-tick counter persists 100 calls
# ---------------------------------------------------------------------------


class TestACINT6CrossTickCounter:
    def test_counter_increments_across_100_ticks(self):
        sb = Sandbox()
        sb.compile("team_a_0", COUNTER_STRATEGY)
        for _ in range(100):
            sb.execute("team_a_0", _make_game_state(), _make_player_state(), [])
        assert sb._contexts["team_a_0"].module_globals["tick_counter"] == 100


# ---------------------------------------------------------------------------
# AC-INT-7: multi-player isolation
# ---------------------------------------------------------------------------


class TestACINT7MultiPlayerIsolation:
    def test_two_players_have_independent_module_globals(self):
        sb = Sandbox()
        sb.compile("team_a_0", MARKER_A_STRATEGY)
        sb.compile("team_b_0", MARKER_B_STRATEGY)

        # Interleaved 50-tick run
        for tick in range(50):
            sb.execute("team_a_0", _make_game_state(tick), _make_player_state("team_a"), [])
            sb.execute("team_b_0", _make_game_state(tick), _make_player_state("team_b"), [])

        # Player A has 'marker' field; player B does not
        assert sb._contexts["team_a_0"].module_globals.get("marker") == "a"
        assert "marker" not in sb._contexts["team_b_0"].module_globals
        # Both counters incremented independently
        assert sb._contexts["team_a_0"].module_globals["counter"] == 50
        assert sb._contexts["team_b_0"].module_globals["counter"] == 50


# ---------------------------------------------------------------------------
# AC-INT-8: COMPILE_ERROR + manual disable + execute
# ---------------------------------------------------------------------------


class TestACINT8CompileErrorThenManualDisable:
    def test_full_workflow(self):
        sb = Sandbox()
        # Bad code → COMPILE_ERROR
        bad_result = _observe(sb.compile("team_a_0", "def decide(:\n"))
        assert bad_result.status is ExecutionStatus.COMPILE_ERROR

        # Per Story 005 AC-1: disable() requires an existing context (which the
        # failed compile DOES create per Story 003 AC-7). Verify it doesn't raise.
        sb.disable("team_a_0")  # should succeed — context exists
        assert sb._contexts["team_a_0"].disabled is True

        # Subsequent execute returns DISABLED + Hold (compiled_fn is None
        # but the disabled check short-circuits before that matters)
        r = _observe(sb.execute("team_a_0", {}, {}, []))
        assert r.status is ExecutionStatus.DISABLED
        assert isinstance(r.action, Hold)


# ---------------------------------------------------------------------------
# AC-INT-9: determinism across two Sandbox instances
# ---------------------------------------------------------------------------


class TestACINT9Determinism:
    def test_two_sandboxes_same_inputs_same_outputs(self):
        sb1 = Sandbox()
        sb2 = Sandbox()
        sb1.compile("team_a_0", REALISTIC_STRATEGY)
        sb2.compile("team_a_0", REALISTIC_STRATEGY)

        for tick in range(20):
            gs = _make_game_state(tick)
            ps = _make_player_state()
            r1 = sb1.execute("team_a_0", gs, ps, [])
            r2 = sb2.execute("team_a_0", _make_game_state(tick), _make_player_state(), [])
            # Same status + same action (excluding wall-clock-dependent execution_time_ms)
            assert r1.status is r2.status
            assert r1.action == r2.action  # frozen dataclass __eq__
            assert r1.error_type == r2.error_type


# ---------------------------------------------------------------------------
# AC-INT-10: all 6 ExecutionStatus values produced across the suite
# ---------------------------------------------------------------------------


class TestACINT10StatusCoverage:
    def test_all_six_statuses_produced(self):
        # Produce each status explicitly so this test is self-contained.
        sb = Sandbox(timeout_ms=20.0, consecutive_failures_limit=1)

        # SUCCESS
        sb.compile("p_success", "def decide(g, p, h):\n    return Hold()\n")
        _observe(sb.execute("p_success", {}, {}, []))

        # COMPILE_ERROR
        _observe(sb.compile("p_compile_err", "def decide(:\n"))

        # EXCEPTION (use injected callable since exception names aren't in namespace)
        def fn_raise(g, p, h):
            raise ValueError("boom")
        _inject_callable(sb, "p_exception", fn_raise)
        _observe(sb.execute("p_exception", {}, {}, []))

        # INVALID_RETURN
        sb.compile("p_invalid", "def decide(g, p, h):\n    return None\n")
        _observe(sb.execute("p_invalid", {}, {}, []))

        # TIMEOUT
        sb.compile("p_timeout", "def decide(g, p, h):\n    while True:\n        pass\n")
        _observe(sb.execute("p_timeout", {}, {}, []))

        # DISABLED — limit=1, so the next call after the timeout above will be DISABLED
        # but we used a different player. Disable manually for clarity:
        sb.disable("p_timeout")
        _observe(sb.execute("p_timeout", {}, {}, []))

        # All 6 statuses observed
        assert _OBSERVED_STATUSES.issuperset({
            ExecutionStatus.SUCCESS,
            ExecutionStatus.COMPILE_ERROR,
            ExecutionStatus.EXCEPTION,
            ExecutionStatus.INVALID_RETURN,
            ExecutionStatus.TIMEOUT,
            ExecutionStatus.DISABLED,
        })


# ---------------------------------------------------------------------------
# Bonus: realistic strategies smoke-compile
# ---------------------------------------------------------------------------


class TestBonusRealisticStrategiesCompile:
    @pytest.mark.parametrize("name,code", [
        ("realistic", REALISTIC_STRATEGY),
        ("stateful", STATEFUL_STRATEGY),
        ("counter", COUNTER_STRATEGY),
        ("mutator", MUTATOR_STRATEGY),
        ("marker_a", MARKER_A_STRATEGY),
        ("marker_b", MARKER_B_STRATEGY),
    ])
    def test_strategy_compiles(self, name, code):
        sb = Sandbox()
        result = sb.compile("p_test", code)
        assert result.status is ExecutionStatus.SUCCESS, (
            f"{name} failed: {result.error_type}"
        )

    def test_stateful_strategy_accumulates(self):
        sb = Sandbox()
        sb.compile("team_a_0", STATEFUL_STRATEGY)
        for _ in range(5):
            sb.execute("team_a_0", _make_game_state(), _make_player_state(), [])
        assert len(sb._contexts["team_a_0"].module_globals["ball_history"]) == 5
