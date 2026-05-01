"""Sandbox performance benchmarks — issue #31.

Measures compile() and execute() latency (p50/p95/p99) for every available
sandbox implementation (Python, JavaScript/QuickJS, Rust/Wasmtime).

Run with:
    python tests/performance/bench_sandbox.py

Flags:
    --iterations N     execute() reps per sandbox (default 200)
    --compile-reps N   compile() reps (default 50)
    --output PATH      write markdown report to file (default: stdout)
    --sandbox py|js|wasm  restrict to one sandbox (default: all available)

Sandboxes are skipped if their runtime dependency is missing (quickjs,
wasmtime/cargo) — the script never errors on an optional absence.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

# Ensure project root is on sys.path so `from src...` imports work when the
# script is run directly (python tests/performance/bench_sandbox.py).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# ── Strategy source fixtures ───────────────────────────────────────────────

PYTHON_HOLD = """\
def decide(game_state, player_state, history):
    return Hold()
"""

PYTHON_REALISTIC = """\
def decide(game_state, player_state, history):
    ball = game_state["ball"]
    my_pos = player_state["position"]
    has_ball = player_state["has_ball"]
    on_cooldown = player_state["cooldown_remaining"] > 0

    if has_ball and not on_cooldown:
        opp_team = "team_b" if player_state["team"] == "team_a" else "team_a"
        field = game_state["field"]
        opp_goal_x = field[opp_team + "_goal_x"]
        goal_y = (field["goal_top"] + field["goal_bottom"]) / 2.0

        dx = opp_goal_x - my_pos[0]
        dy = goal_y - my_pos[1]
        m = (dx * dx + dy * dy) ** 0.5
        if m > 1e-6:
            dx, dy = dx / m, dy / m

        dist_to_goal = m
        if dist_to_goal < 15.0:
            return Shoot(angle=0.0, power=20)

        players = game_state["players"]
        best = None
        best_d = 6.0
        for pid, p in players.items():
            if p["team"] != player_state["team"] or pid == player_state["player_id"]:
                continue
            d = ((p["position"][0] - my_pos[0]) ** 2 + (p["position"][1] - my_pos[1]) ** 2) ** 0.5
            opp_d_check = min(
                ((q["position"][0] - p["position"][0]) ** 2 + (q["position"][1] - p["position"][1]) ** 2) ** 0.5
                for q in players.values() if q["team"] != player_state["team"]
            )
            if opp_d_check > 3.0 and d < best_d:
                best_d = d
                best = p["position"]
        if best is not None:
            return Pass(target_pos=best, power=14)

        return Move(dx=dx, dy=dy, speed=1.0)

    return Hold()
"""

JS_HOLD = """\
function decide(game_state, player_state, history) {
    return { type: "Hold" };
}
"""

JS_REALISTIC = """\
function decide(game_state, player_state, history) {
    const ball = game_state.ball;
    const myPos = player_state.position;
    const hasBall = player_state.has_ball;
    const onCooldown = player_state.cooldown_remaining > 0;

    if (hasBall && !onCooldown) {
        const myTeam = player_state.team;
        const oppTeam = (myTeam === "team_a") ? "team_b" : "team_a";
        const field = game_state.field;
        const oppGoalX = field[oppTeam + "_goal_x"];
        const goalY = (field.goal_top + field.goal_bottom) / 2.0;

        const dx = oppGoalX - myPos[0];
        const dy = goalY - myPos[1];
        const m = Math.sqrt(dx * dx + dy * dy);

        if (m < 15.0) {
            return { type: "Shoot", angle: 0.0, power: 20 };
        }

        const players = game_state.players;
        let best = null;
        let bestD = 6.0;
        for (const [pid, p] of Object.entries(players)) {
            if (p.team !== myTeam || pid === player_state.player_id) continue;
            const pd = Math.sqrt(
                Math.pow(p.position[0] - myPos[0], 2) +
                Math.pow(p.position[1] - myPos[1], 2)
            );
            const oppNear = Math.min(
                ...Object.values(players)
                    .filter(q => q.team !== myTeam)
                    .map(q => Math.sqrt(
                        Math.pow(q.position[0] - p.position[0], 2) +
                        Math.pow(q.position[1] - p.position[1], 2)
                    ))
            );
            if (oppNear > 3.0 && pd < bestD) {
                bestD = pd;
                best = p.position;
            }
        }
        if (best !== null) {
            return { type: "Pass", target_pos: best, power: 14 };
        }

        const ndx = m > 1e-6 ? dx / m : 1.0;
        const ndy = m > 1e-6 ? dy / m : 0.0;
        return { type: "Move", dx: ndx, dy: ndy, speed: 1.0 };
    }

    return { type: "Hold" };
}
"""

# Rust strategy for Wasm sandbox — full source using the project's ABI.
# Must match the cargo_template/src/lib.rs.in shape (rmp_serde, serde derives).
# The `decide_logic` below always returns Hold.
_CARGO_TEMPLATE_LIB = Path(__file__).resolve().parents[2] / \
    "src" / "foundation" / "sandbox" / "cargo_template" / "src" / "lib.rs.in"
RUST_HOLD: str = _CARGO_TEMPLATE_LIB.read_text(encoding="utf-8") \
    if _CARGO_TEMPLATE_LIB.exists() else ""


# ── Realistic game state fixture ──────────────────────────────────────────

def _make_players_5v5() -> dict[str, Any]:
    roles = ["GK", "DEF", "MID", "MID", "FWD"]
    players: dict[str, Any] = {}
    for team, gx in [("team_a", 0.0), ("team_b", 100.0)]:
        for i, role in enumerate(roles):
            pid = f"{team}_{i}"
            x = gx + (10.0 if team == "team_a" else -10.0) + i * 5.0
            players[pid] = {
                "team": team,
                "player_id": pid,
                "number": i + 1,
                "role": role,
                "position": [x, 34.0 + i * 3.0],
                "formation_position": [x, 34.0 + i * 3.0],
                "has_ball": False,
                "speed": 12,
                "skill": 12,
                "strength": 10,
                "save": 14 if role == "GK" else 6,
                "discipline": 10,
                "dribbling": 10,
                "passing": 12,
                "shooting": 12,
                "stamina": 14,
                "current_health": 100.0,
                "cooldown_remaining": 0,
                "formation_zone_phase": "in_play",
            }
    # Give team_a_2 (MID) the ball for carrier-path exercises.
    players["team_a_2"]["has_ball"] = True
    return players


def make_game_state() -> dict[str, Any]:
    players = _make_players_5v5()
    return {
        "tick": 150,
        "ticks_remaining": 1350,
        "match_phase": "in_play",
        "half": 1,
        "score": {"team_a": 0, "team_b": 0},
        "team_phase": {"team_a": "attacking", "team_b": "defending"},
        "ball": {
            "position": [55.0, 34.0],
            "velocity": [0.2, 0.1],
            "carrier_id": "team_a_2",
            "possession": "team_a",
        },
        "players": players,
        "field": {
            "width": 100.0,
            "height": 68.0,
            "team_a_goal_x": 0.0,
            "team_b_goal_x": 100.0,
            "goal_top": 43.16,
            "goal_bottom": 24.84,
        },
    }


def make_player_state(pid: str = "team_a_2") -> dict[str, Any]:
    gs = make_game_state()
    ps = dict(gs["players"][pid])
    ps["my_player_id"] = pid
    ps["my_team"] = ps["team"]
    return ps


def make_history() -> list[dict]:
    return [{"tick": 149, "action": {"type": "Move", "dx": 1.0, "dy": 0.0, "speed": 1.0}}]


# ── Percentile helper ─────────────────────────────────────────────────────

def percentiles(data: list[float]) -> dict[str, float]:
    s = sorted(data)
    n = len(s)
    if n == 0:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "mean": 0.0}

    def pct(p: float) -> float:
        idx = p / 100.0 * (n - 1)
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        return s[lo] + (s[hi] - s[lo]) * (idx - lo)

    return {
        "p50": round(pct(50), 4),
        "p95": round(pct(95), 4),
        "p99": round(pct(99), 4),
        "mean": round(statistics.mean(s), 4),
    }


# ── Benchmark runners ─────────────────────────────────────────────────────

def bench_python(compile_reps: int, execute_reps: int) -> dict[str, Any]:
    from src.foundation.sandbox.python_sandbox import RestrictedPythonSandbox

    sandbox = RestrictedPythonSandbox(timeout_ms=50.0)
    gs = make_game_state()
    ps = make_player_state()
    hist = make_history()

    # --- compile benchmarks ---
    compile_times: dict[str, list[float]] = {"hold": [], "realistic": []}
    for source, label in [(PYTHON_HOLD, "hold"), (PYTHON_REALISTIC, "realistic")]:
        for _ in range(compile_reps):
            t0 = time.perf_counter_ns()
            sandbox.compile("team_a_0", source)
            compile_times[label].append((time.perf_counter_ns() - t0) / 1_000_000)

    # Prime context with realistic strategy for execute benchmark
    sandbox.compile("team_a_0", PYTHON_REALISTIC)

    # --- execute benchmarks ---
    execute_times: dict[str, list[float]] = {"realistic": []}
    for _ in range(execute_reps):
        r = sandbox.execute("team_a_0", gs, ps, hist)
        execute_times["realistic"].append(r.execution_time_ms)

    return {
        "compile": {k: percentiles(v) for k, v in compile_times.items()},
        "execute": {k: percentiles(v) for k, v in execute_times.items()},
    }


def bench_js(compile_reps: int, execute_reps: int) -> dict[str, Any] | None:
    try:
        import quickjs  # noqa: F401
    except ImportError:
        return None

    from src.foundation.sandbox.quickjs_sandbox import QuickJSSandbox

    sandbox = QuickJSSandbox(timeout_ms=50.0)
    gs = make_game_state()
    ps = make_player_state()
    hist = make_history()

    compile_times: dict[str, list[float]] = {"hold": [], "realistic": []}
    for source, label in [(JS_HOLD, "hold"), (JS_REALISTIC, "realistic")]:
        for _ in range(compile_reps):
            t0 = time.perf_counter_ns()
            sandbox.compile("team_a_0", source)
            compile_times[label].append((time.perf_counter_ns() - t0) / 1_000_000)

    sandbox.compile("team_a_0", JS_REALISTIC)

    execute_times: dict[str, list[float]] = {"realistic": []}
    for _ in range(execute_reps):
        t0 = time.perf_counter_ns()
        sandbox.execute("team_a_0", gs, ps, hist)
        elapsed = (time.perf_counter_ns() - t0) / 1_000_000
        execute_times["realistic"].append(elapsed)

    # Measure JSON marshalling overhead separately (the gs+ps+hist serialisation
    # that happens inside QuickJSSandbox.execute before eval).
    marshal_times: list[float] = []
    for _ in range(execute_reps):
        t0 = time.perf_counter_ns()
        json.dumps([gs, ps, hist])
        marshal_times.append((time.perf_counter_ns() - t0) / 1_000_000)

    return {
        "compile": {k: percentiles(v) for k, v in compile_times.items()},
        "execute": {k: percentiles(v) for k, v in execute_times.items()},
        "json_marshal": percentiles(marshal_times),
    }


def bench_wasm(compile_reps: int, execute_reps: int) -> dict[str, Any] | None:
    try:
        import wasmtime  # noqa: F401
    except ImportError:
        return None

    # Check cargo toolchain
    import shutil
    if shutil.which("cargo") is None:
        return {"skipped": "cargo toolchain not found"}

    if not RUST_HOLD:
        return {"skipped": "cargo_template/src/lib.rs.in not found"}

    from src.foundation.sandbox.wasm_sandbox import WasmtimeSandbox
    import tempfile

    sandbox = WasmtimeSandbox(timeout_ms=50.0, cache_dir=Path(tempfile.mkdtemp()))
    gs = make_game_state()
    ps = make_player_state()
    hist = make_history()

    compile_times: list[float] = []
    for i in range(compile_reps):
        t0 = time.perf_counter_ns()
        r = sandbox.compile("team_a_0", RUST_HOLD)
        elapsed = (time.perf_counter_ns() - t0) / 1_000_000
        if r.status.name == "SUCCESS":
            compile_times.append(elapsed)
        elif i == 0:
            # Compilation failed — report the error and skip
            return {"skipped": f"compile failed: {r.error_type}"}

    if not compile_times:
        return {"skipped": "all compile attempts failed"}

    # Prime for execute
    r = sandbox.compile("team_a_0", RUST_HOLD)
    if r.status.name != "SUCCESS":
        return {"skipped": f"compile priming failed: {r.error_type}"}

    execute_times: list[float] = []
    for _ in range(execute_reps):
        r = sandbox.execute("team_a_0", gs, ps, hist)
        execute_times.append(r.execution_time_ms)

    # Msgpack marshal overhead
    try:
        import msgpack
        marshal_times: list[float] = []
        for _ in range(execute_reps):
            t0 = time.perf_counter_ns()
            msgpack.dumps((gs, ps, hist), use_bin_type=True)
            marshal_times.append((time.perf_counter_ns() - t0) / 1_000_000)
    except ImportError:
        marshal_times = []

    result: dict[str, Any] = {
        "compile": {"hold": percentiles(compile_times)},
        "execute": {"realistic": percentiles(execute_times)},
    }
    if marshal_times:
        result["msgpack_marshal"] = percentiles(marshal_times)
    return result


# ── Report generation ─────────────────────────────────────────────────────

def _fmt_row(label: str, stats: dict[str, float]) -> str:
    return (
        f"| {label:<35} | {stats['mean']:>8.4f} | {stats['p50']:>8.4f} | "
        f"{stats['p95']:>8.4f} | {stats['p99']:>8.4f} |"
    )


def generate_report(
    py: dict[str, Any],
    js: dict[str, Any] | None,
    wasm: dict[str, Any] | None,
    iterations: int,
    compile_reps: int,
) -> str:
    lines: list[str] = []

    lines.append("# Sandbox Performance Benchmark Report")
    lines.append("")
    lines.append(f"*Iterations: execute={iterations}, compile={compile_reps}*  ")
    lines.append(f"*All times in milliseconds (ms).*")
    lines.append("")

    # --- compile table ---
    lines.append("## compile() Latency")
    lines.append("")
    lines.append(f"| {'Strategy':<35} | {'mean':>8} | {'p50':>8} | {'p95':>8} | {'p99':>8} |")
    lines.append(f"|{'-'*37}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}|")

    lines.append(_fmt_row("Python / hold", py["compile"]["hold"]))
    lines.append(_fmt_row("Python / realistic", py["compile"]["realistic"]))

    if js and "compile" in js:
        lines.append(_fmt_row("JS (QuickJS) / hold", js["compile"]["hold"]))
        lines.append(_fmt_row("JS (QuickJS) / realistic", js["compile"]["realistic"]))
    elif js and "skipped" in js:
        lines.append(f"| JS (QuickJS) — skipped: {js['skipped']:<27} | — | — | — | — |")
    else:
        lines.append("| JS (QuickJS) — not installed                     | — | — | — | — |")

    if wasm and "compile" in wasm:
        lines.append(_fmt_row("Wasm (Rust) / hold", wasm["compile"]["hold"]))
    elif wasm and "skipped" in wasm:
        lines.append(f"| Wasm (Rust) — skipped: {wasm['skipped']:<30} | — | — | — | — |")
    else:
        lines.append("| Wasm (Rust) — not installed                      | — | — | — | — |")

    lines.append("")

    # --- execute table ---
    lines.append("## execute() Latency")
    lines.append("")
    lines.append(f"| {'Strategy':<35} | {'mean':>8} | {'p50':>8} | {'p95':>8} | {'p99':>8} |")
    lines.append(f"|{'-'*37}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}|")

    lines.append(_fmt_row("Python / realistic", py["execute"]["realistic"]))

    if js and "execute" in js:
        lines.append(_fmt_row("JS (QuickJS) / realistic", js["execute"]["realistic"]))
    elif js is None:
        lines.append("| JS (QuickJS) — not installed                     | — | — | — | — |")
    else:
        lines.append(f"| JS (QuickJS) — skipped: {js.get('skipped','?'):<29} | — | — | — | — |")

    if wasm and "execute" in wasm:
        lines.append(_fmt_row("Wasm (Rust) / realistic", wasm["execute"]["realistic"]))
    elif wasm is None:
        lines.append("| Wasm (Rust) — not installed                      | — | — | — | — |")
    else:
        lines.append(f"| Wasm (Rust) — skipped: {wasm.get('skipped','?'):<30} | — | — | — | — |")

    lines.append("")

    # --- marshalling overhead ---
    lines.append("## Serialisation Overhead")
    lines.append("")
    lines.append(f"| {'Operation':<35} | {'mean':>8} | {'p50':>8} | {'p95':>8} | {'p99':>8} |")
    lines.append(f"|{'-'*37}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}|")

    if js and "json_marshal" in js:
        lines.append(_fmt_row("JSON serialise (JS bridge)", js["json_marshal"]))
    if wasm and "msgpack_marshal" in wasm:
        lines.append(_fmt_row("MessagePack serialise (Wasm bridge)", wasm["msgpack_marshal"]))

    if (not js or "json_marshal" not in js) and (not wasm or "msgpack_marshal" not in wasm):
        lines.append("| *No serialisation data available*                | — | — | — | — |")

    lines.append("")

    # --- overhead analysis ---
    lines.append("## Overhead Analysis")
    lines.append("")

    py_exec_mean = py["execute"]["realistic"]["mean"]
    hotspots: list[tuple[float, str]] = []

    if js and "execute" in js:
        js_exec_mean = js["execute"]["realistic"]["mean"]
        overhead_pct = ((js_exec_mean - py_exec_mean) / max(py_exec_mean, 1e-9)) * 100
        hotspots.append((abs(overhead_pct), f"JS vs Python execute(): {overhead_pct:+.1f}%"))
        if "json_marshal" in js:
            marshal_mean = js["json_marshal"]["mean"]
            marshal_pct = (marshal_mean / max(js_exec_mean, 1e-9)) * 100
            hotspots.append((marshal_pct, f"JSON marshalling in JS execute(): {marshal_pct:.1f}% of total"))

    if wasm and "execute" in wasm:
        wasm_exec_mean = wasm["execute"]["realistic"]["mean"]
        overhead_pct = ((wasm_exec_mean - py_exec_mean) / max(py_exec_mean, 1e-9)) * 100
        hotspots.append((abs(overhead_pct), f"Wasm vs Python execute(): {overhead_pct:+.1f}%"))
        if "msgpack_marshal" in wasm:
            marshal_mean = wasm["msgpack_marshal"]["mean"]
            marshal_pct = (marshal_mean / max(wasm_exec_mean, 1e-9)) * 100
            hotspots.append((marshal_pct, f"MessagePack marshalling in Wasm execute(): {marshal_pct:.1f}% of total"))

    if hotspots:
        hotspots.sort(reverse=True)
        lines.append("### Top hotspots (by magnitude)")
        lines.append("")
        for rank, (_, desc) in enumerate(hotspots[:3], 1):
            lines.append(f"{rank}. {desc}")
        lines.append("")

    lines.append("### Recommendations")
    lines.append("")

    if js and "execute" in js and "json_marshal" in js:
        js_exec_mean = js["execute"]["realistic"]["mean"]
        marshal_mean = js["json_marshal"]["mean"]
        marshal_share = marshal_mean / max(js_exec_mean, 1e-9)
        if marshal_share > 0.30:
            lines.append(
                "- **JS sandbox**: JSON marshalling accounts for "
                f"{marshal_share*100:.0f}% of execute() time. "
                "Consider caching serialised game state across players "
                "on the same tick (all 5 team_a players share the same gs)."
            )
        else:
            lines.append(
                f"- **JS sandbox**: JSON overhead is {marshal_share*100:.0f}% — "
                "acceptable. No marshalling optimisation needed at current load."
            )

    if js and "compile" in js:
        py_compile_mean = py["compile"]["realistic"]["mean"]
        js_compile_mean = js["compile"]["realistic"]["mean"]
        if js_compile_mean > py_compile_mean * 2:
            lines.append(
                "- **JS compile**: significantly slower than Python compile. "
                "QuickJS context creation dominates. Pre-creating and pooling "
                "contexts across recompiles would reduce this cost."
            )

    lines.append(
        "- **Baseline tracking**: re-run this script after sandbox changes "
        "and compare against this report to catch regressions."
    )
    lines.append("")

    lines.append("---")
    lines.append("*Generated by `tests/performance/bench_sandbox.py` (issue #31)*")
    return "\n".join(lines)


# ── CLI entry point ───────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Sandbox performance benchmarks")
    parser.add_argument("--iterations", type=int, default=200,
                        help="execute() repetitions per sandbox (default: 200)")
    parser.add_argument("--compile-reps", type=int, default=50,
                        help="compile() repetitions (default: 50)")
    parser.add_argument("--output", type=str, default="-",
                        help="output file path (default: stdout)")
    parser.add_argument("--sandbox", choices=["py", "js", "wasm", "all"], default="all",
                        help="restrict to one sandbox (default: all)")
    args = parser.parse_args()

    run_py = args.sandbox in ("py", "all")
    run_js = args.sandbox in ("js", "all")
    run_wasm = args.sandbox in ("wasm", "all")

    print("Running sandbox benchmarks…", file=sys.stderr)

    py_results: dict[str, Any] = {}
    if run_py:
        print("  • Python sandbox…", file=sys.stderr)
        py_results = bench_python(args.compile_reps, args.iterations)

    js_results: dict[str, Any] | None = None
    if run_js:
        print("  • JavaScript (QuickJS) sandbox…", file=sys.stderr)
        js_results = bench_js(args.compile_reps, args.iterations)
        if js_results is None:
            print("    (quickjs not installed — skipped)", file=sys.stderr)

    wasm_results: dict[str, Any] | None = None
    if run_wasm:
        print("  • Wasm (Rust/Wasmtime) sandbox…", file=sys.stderr)
        wasm_results = bench_wasm(args.compile_reps, args.iterations)
        if wasm_results is None:
            print("    (wasmtime not installed — skipped)", file=sys.stderr)
        elif "skipped" in wasm_results:
            print(f"    (skipped: {wasm_results['skipped']})", file=sys.stderr)

    if not py_results:
        # Minimal stub so report generation still works when py was skipped
        py_results = {
            "compile": {"hold": percentiles([]), "realistic": percentiles([])},
            "execute": {"realistic": percentiles([])},
        }

    report = generate_report(
        py_results, js_results, wasm_results,
        args.iterations, args.compile_reps,
    )

    if args.output == "-":
        print(report)
    else:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
