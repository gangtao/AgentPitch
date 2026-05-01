"""Cargo build pipeline for Rust strategies (ADR-0026).

Compiles a Rust source string to a `.wasm` blob via `cargo build
--target wasm32-wasip1 --release`. Caches results by sha256(source)
so re-running the same strategy is a sub-millisecond filesystem read.

This module is host-side only; it does not import wasmtime.
WasmtimeSandbox.compile() calls compile_strategy_rs(...) and then loads
the returned bytes via wasmtime.Module(engine, bytes).

Layout under cache_dir:
    <cache_dir>/<sha>.wasm                  cached compiled output
    <cache_dir>/builds/<sha>/Cargo.toml     copied from cargo template
    <cache_dir>/builds/<sha>/src/lib.rs     the user's Rust source
    <cache_dir>/builds/<sha>/target/...     cargo's target dir
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path
from typing import Optional


WASM_TARGET = "wasm32-wasip1"
DEFAULT_BUILD_TIMEOUT_S = 120
TEMPLATE_DIR = Path(__file__).parent / "cargo_template"
ARTIFACT_RELPATH = Path("target") / WASM_TARGET / "release" / "agent_pitch_strategy.wasm"


class WasmCompileError(Exception):
    """Cargo build of a Rust strategy failed.

    `__str__` includes a tail of cargo's stdout/stderr so the LLM (or human)
    can see compile errors. Per ADR-0026 §11, this is surfaced via
    SandboxResult.error_type by the caller.
    """


class WasmToolchainMissing(Exception):
    """`cargo` not on PATH or the wasm32-wasip1 target is not installed.

    Raised once at first compile attempt. The remediation message names the
    exact rustup commands needed.
    """


def _resolve_cargo() -> str:
    """Locate the cargo executable. Prefers ~/.cargo/bin/cargo (rustup default)
    then falls back to PATH."""
    rustup_cargo = Path.home() / ".cargo" / "bin" / "cargo"
    if rustup_cargo.exists():
        return str(rustup_cargo)
    found = shutil.which("cargo")
    if found:
        return found
    raise WasmToolchainMissing(
        "cargo not found. Install Rust via "
        "https://rustup.rs and run `rustup target add wasm32-wasip1`."
    )


def _ensure_target_installed(cargo_path: str) -> None:
    """Check `wasm32-wasip1` target is present; raise WasmToolchainMissing if not."""
    rustup = Path(cargo_path).parent / "rustup"
    if not rustup.exists():
        # cargo is on PATH but not via rustup — assume target is set up.
        return
    proc = subprocess.run(
        [str(rustup), "target", "list", "--installed"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if WASM_TARGET not in proc.stdout.split():
        raise WasmToolchainMissing(
            f"Rust target {WASM_TARGET!r} not installed. Run: "
            f"`rustup target add {WASM_TARGET}`."
        )


def compile_strategy_rs(
    source: str,
    cache_dir: Path,
    *,
    build_timeout_s: int = DEFAULT_BUILD_TIMEOUT_S,
    cargo_path: Optional[str] = None,
) -> bytes:
    """Compile Rust `source` to `.wasm` bytes, cached by sha256(source).

    First call for a given source: 5-30s cargo build.
    Cache hit: sub-millisecond filesystem read.

    Raises:
        WasmToolchainMissing: cargo or wasm32-wasip1 target not installed.
        WasmCompileError: cargo build failed (stderr tail in message).
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(source.encode("utf-8")).hexdigest()
    cached = cache_dir / f"{sha}.wasm"
    if cached.exists():
        return cached.read_bytes()

    cargo = cargo_path or _resolve_cargo()
    _ensure_target_installed(cargo)

    build_dir = cache_dir / "builds" / sha
    build_src = build_dir / "src"
    build_src.mkdir(parents=True, exist_ok=True)
    shutil.copy(TEMPLATE_DIR / "Cargo.toml", build_dir / "Cargo.toml")
    (build_src / "lib.rs").write_text(source, encoding="utf-8")

    proc = subprocess.run(
        [cargo, "build", "--target", WASM_TARGET, "--release"],
        cwd=build_dir,
        capture_output=True,
        text=True,
        timeout=build_timeout_s,
    )
    if proc.returncode != 0:
        raise WasmCompileError(
            f"cargo build failed (exit {proc.returncode}):\n"
            f"STDOUT: {proc.stdout[-500:]}\n"
            f"STDERR: {proc.stderr[-1500:]}"
        )

    artifact = build_dir / ARTIFACT_RELPATH
    if not artifact.exists():
        raise WasmCompileError(
            f"cargo build succeeded but artifact not found at {artifact}"
        )
    wasm_bytes = artifact.read_bytes()
    cached.write_bytes(wasm_bytes)
    return wasm_bytes
