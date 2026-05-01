"""WasmtimeSandbox — Rust strategies via wasmtime + wasm32-wasip1 (ADR-0026).

Implements the Sandbox Protocol (ADR-0024) for Rust strategies. Each player
gets a fresh wasmtime.Store + Instance. Strategy is compiled once via cargo
(see wasm_compile.py), then executed per tick by marshalling game state
through MessagePack into the wasm linear memory.

Spike-verified API surface (2026-04-26 re-run, wasmtime 44.0.0):
  - Engine epoch interruption: cfg.epoch_interruption = True; daemon thread
    calls engine.increment_epoch() every 1ms; per-call deadline armed via
    store.set_epoch_deadline(n).
  - Store/instance per player (linear-memory isolation).
  - Memory.write(store, bytes, start) and Memory.read(store, start, stop).
  - Linker.define_wasi() + restrictive WasiConfig() (no inherit / preopen).
  - Host-injected, seeded random_u64 (splitmix64) for determinism.

Required runtime exports from the user's Rust strategy (see cargo_template/
src/lib.rs.in for the reference shape):
  alloc_buf(len) -> ptr
  dealloc_buf(ptr, len)
  decide(ptr, len) -> i32 status
  return_ptr() -> i32
  return_len() -> i32

macOS note (Risk §15 in ADR-0026): wasmtime's Cranelift backend JITs into
RWX pages. Apple-shipped Python (Xcode CLT) is signed under Hardened Runtime
*without* the `com.apple.security.cs.allow-jit` entitlement; the kernel
SIGKILLs the process the moment any wasm function executes. Use Homebrew,
python.org, or pyenv-built Python (all ad-hoc signed → no Hardened Runtime).
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import msgpack
import wasmtime

from src.foundation.action import Action, Hold
from src.foundation.sandbox.result import SandboxResult
from src.foundation.sandbox.status import ExecutionStatus
from src.foundation.sandbox.wasm_compile import (
    WasmCompileError,
    WasmToolchainMissing,
    compile_strategy_rs,
)


DEFAULT_CACHE_DIR = Path.home() / ".cache" / "agent-pitch" / "wasm"
EPOCH_TICK_INTERVAL_S = 0.001  # 1ms ticks → ~1ms timeout granularity


# ── Engine + epoch ticker (process-wide singletons) ───────────────────────

_engine_lock = threading.Lock()
_engine: Optional[wasmtime.Engine] = None
_ticker_thread: Optional[threading.Thread] = None
_ticker_stop = threading.Event()


def _epoch_ticker_loop(engine: wasmtime.Engine) -> None:
    """Daemon thread: increments engine epoch every EPOCH_TICK_INTERVAL_S.

    Per ADR-0026: enables per-call timeout via Store.set_epoch_deadline().
    Wasmtime documents Engine.increment_epoch() as thread-safe.
    """
    while not _ticker_stop.is_set():
        time.sleep(EPOCH_TICK_INTERVAL_S)
        engine.increment_epoch()


def _get_engine() -> wasmtime.Engine:
    """Lazy-init the process-wide Engine + epoch-tick daemon thread."""
    global _engine, _ticker_thread
    with _engine_lock:
        if _engine is None:
            cfg = wasmtime.Config()
            cfg.epoch_interruption = True
            _engine = wasmtime.Engine(cfg)
            _ticker_thread = threading.Thread(
                target=_epoch_ticker_loop,
                args=(_engine,),
                daemon=True,
                name="wasmtime-epoch-ticker",
            )
            _ticker_thread.start()
        return _engine


# ── Per-player state ──────────────────────────────────────────────────────


@dataclass
class _WasmPlayerContext:
    """Per-player wasmtime state. Sibling of PlayerSandboxContext (Python)."""

    store: wasmtime.Store
    instance: wasmtime.Instance
    memory: wasmtime.Memory
    decide_fn: wasmtime.Func
    alloc_fn: wasmtime.Func
    dealloc_fn: wasmtime.Func
    return_ptr_fn: wasmtime.Func
    return_len_fn: wasmtime.Func
    rng_state: int = 0
    consecutive_timeout_count: int = 0
    disabled: bool = False


def _splitmix64_step(state: int) -> tuple[int, int]:
    """Advance splitmix64 and return (new_state, output_as_signed_i64)."""
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    out = z ^ (z >> 31)
    if out >= 2**63:
        out -= 2**64
    return state, out


# ── Sandbox impl ──────────────────────────────────────────────────────────


class WasmtimeSandbox:
    """Sandbox Protocol implementation for Rust strategies (ADR-0026).

    `compile()` cargo-builds the user's Rust source to `.wasm` (cached by
    sha256(source) under `cache_dir`), then instantiates a fresh wasmtime
    Store + Instance per player. `execute()` marshals state via MessagePack,
    calls the wasm `decide` export under an epoch deadline, and decodes the
    returned tagged Action via `Action.from_tagged()`.
    """

    def __init__(
        self,
        timeout_ms: float = 5.0,
        consecutive_failures_limit: int = 10,
        cache_dir: Optional[Path] = None,
        rng_seed: int = 0xCAFEBABE,
    ) -> None:
        self.timeout_ms = timeout_ms
        self.consecutive_failures_limit = consecutive_failures_limit
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self._rng_seed = rng_seed
        self._contexts: dict[str, _WasmPlayerContext] = {}

    @property
    def language(self) -> str:
        return "rust"

    # ── compile ──────────────────────────────────────────────────────────

    def compile(self, player_id: str, source: str) -> SandboxResult:
        """Cargo-build the source, instantiate per-player Store + Instance."""
        self._contexts.pop(player_id, None)

        try:
            wasm_bytes = compile_strategy_rs(source, self.cache_dir)
        except WasmToolchainMissing as e:
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type="WasmToolchainMissing",
                error_message=str(e),
            )
        except WasmCompileError as e:
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type="WasmCompileError",
                error_message=str(e),
            )
        except Exception as e:
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type=type(e).__name__,
                error_message=str(e),
            )

        try:
            ctx = self._instantiate(wasm_bytes, player_id)
        except KeyError as e:
            # Missing required export (alloc_buf / decide / etc.)
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type="MissingWasmExport",
                error_message=str(e),
            )
        except Exception as e:
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type=type(e).__name__,
                error_message=str(e),
            )

        self._contexts[player_id] = ctx
        return SandboxResult(status=ExecutionStatus.SUCCESS)

    def _instantiate(self, wasm_bytes: bytes, player_id: str) -> _WasmPlayerContext:
        """Build a fresh Store + Instance with WASI + host.random_u64 wired in."""
        engine = _get_engine()
        module = wasmtime.Module(engine, wasm_bytes)
        store = wasmtime.Store(engine)
        # Disabled until armed per-call.
        store.set_epoch_deadline(2**31 - 1)

        # Per-player RNG state, seeded from sandbox seed + player_id hash.
        rng_state = (self._rng_seed ^ (hash(player_id) & 0xFFFFFFFFFFFFFFFF)) \
            & 0xFFFFFFFFFFFFFFFF

        # Closure captures the ctx-to-be; we set rng_state via a small holder
        # so `host_random_u64` can mutate it independently of ctx assembly order.
        rng_holder = [rng_state]

        def host_random_u64(*_args: Any) -> int:
            new_state, out = _splitmix64_step(rng_holder[0])
            rng_holder[0] = new_state
            return out

        linker = wasmtime.Linker(engine)
        # Rust's wasm32-wasip1 target auto-links 4 WASI runtime helpers
        # (environ_get, environ_sizes_get, fd_write, proc_exit) for std-library
        # support. Provide them via define_wasi + a restrictive WasiConfig
        # (no inherit, no preopen) → net capability zero (no fs/net/clock/env).
        linker.define_wasi()
        wasi_cfg = wasmtime.WasiConfig()
        store.set_wasi(wasi_cfg)

        linker.define_func(
            "host", "random_u64",
            wasmtime.FuncType([], [wasmtime.ValType.i64()]),
            host_random_u64,
        )
        instance = linker.instantiate(store, module)
        exports = instance.exports(store)

        ctx = _WasmPlayerContext(
            store=store,
            instance=instance,
            memory=exports["memory"],
            decide_fn=exports["decide"],
            alloc_fn=exports["alloc_buf"],
            dealloc_fn=exports["dealloc_buf"],
            return_ptr_fn=exports["return_ptr"],
            return_len_fn=exports["return_len"],
            rng_state=rng_state,
        )
        # Bind the holder so future calls update both ctx.rng_state and the
        # closure's view consistently.
        ctx._rng_holder = rng_holder  # type: ignore[attr-defined]
        return ctx

    # ── execute ──────────────────────────────────────────────────────────

    def execute(
        self,
        player_id: str,
        game_state,
        player_state,
        history,
    ) -> SandboxResult:
        """Marshal state via msgpack, call decide() under an epoch deadline."""
        ctx = self._contexts.get(player_id)
        if ctx is None:
            return SandboxResult(
                status=ExecutionStatus.COMPILE_ERROR,
                error_type="NoCompiledContext",
            )
        if ctx.disabled:
            return SandboxResult(
                status=ExecutionStatus.DISABLED,
                action=Hold(),
                execution_time_ms=0.0,
            )

        serial_start_ns = time.perf_counter_ns()
        try:
            payload = msgpack.dumps(
                (game_state, player_state, history),
                use_bin_type=True,
            )
        except Exception as e:
            return SandboxResult(
                status=ExecutionStatus.EXCEPTION,
                error_type=type(e).__name__,
            )
        serial_ms = (time.perf_counter_ns() - serial_start_ns) / 1_000_000

        start_ns = time.perf_counter_ns()
        try:
            # Arm epoch deadline before ANY wasm call. The epoch ticker
            # thread advances the engine epoch between execute() calls;
            # without this reset the stale deadline from the previous call
            # would cause alloc_fn to trap immediately.
            epoch_ticks = max(1, int(self.timeout_ms))
            ctx.store.set_epoch_deadline(epoch_ticks)

            in_ptr = int(ctx.alloc_fn(ctx.store, len(payload)))
            ctx.memory.write(ctx.store, payload, in_ptr)

            status = int(ctx.decide_fn(ctx.store, in_ptr, len(payload)))

            if status != 0:
                # Strategy returned a non-success status (decode error etc.)
                _safe_dealloc(ctx, in_ptr, len(payload))
                elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
                return SandboxResult(
                    status=ExecutionStatus.EXCEPTION,
                    execution_time_ms=elapsed_ms,
                    error_type="StrategyReturnedError",
                )

            out_ptr = int(ctx.return_ptr_fn(ctx.store))
            out_len = int(ctx.return_len_fn(ctx.store))
            out_bytes = bytes(
                ctx.memory.read(ctx.store, out_ptr, out_ptr + out_len)
            )
            _safe_dealloc(ctx, in_ptr, len(payload))
            _safe_dealloc(ctx, out_ptr, out_len)

        except wasmtime.Trap as e:
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
            err = str(e).lower()
            if "epoch" in err or "interrupt" in err:
                ctx.consecutive_timeout_count += 1
                if ctx.consecutive_timeout_count >= self.consecutive_failures_limit:
                    ctx.disabled = True
                return SandboxResult(
                    status=ExecutionStatus.TIMEOUT,
                    serialization_ms=serial_ms,
                    execution_time_ms=elapsed_ms,
                )
            return SandboxResult(
                status=ExecutionStatus.EXCEPTION,
                serialization_ms=serial_ms,
                execution_time_ms=elapsed_ms,
                error_type="WasmTrap",
            )
        except wasmtime.WasmtimeError as e:
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
            return SandboxResult(
                status=ExecutionStatus.EXCEPTION,
                serialization_ms=serial_ms,
                execution_time_ms=elapsed_ms,
                error_type="WasmtimeError",
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
            return SandboxResult(
                status=ExecutionStatus.EXCEPTION,
                serialization_ms=serial_ms,
                execution_time_ms=elapsed_ms,
                error_type=type(e).__name__,
            )

        # Sync rng_state from holder back to ctx for inspection / determinism.
        ctx.rng_state = ctx._rng_holder[0]  # type: ignore[attr-defined]

        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000

        try:
            tagged = msgpack.loads(out_bytes, raw=False)
        except Exception:
            tagged = None

        if not isinstance(tagged, dict):
            action = Hold()
        else:
            action = Action.from_tagged(tagged)

        ctx.consecutive_timeout_count = 0
        return SandboxResult(
            action=action,
            status=ExecutionStatus.SUCCESS,
            serialization_ms=serial_ms,
            execution_time_ms=elapsed_ms,
        )

    # ── disable ──────────────────────────────────────────────────────────

    def disable(self, player_id: str) -> None:
        """Manually disable a player's strategy. No-op if compile never succeeded."""
        ctx = self._contexts.get(player_id)
        if ctx is not None:
            ctx.disabled = True


def _safe_dealloc(ctx: _WasmPlayerContext, ptr: int, length: int) -> None:
    """Call dealloc_buf and swallow any trap — we're already in a cleanup path."""
    try:
        ctx.dealloc_fn(ctx.store, ptr, length)
    except Exception:
        pass
