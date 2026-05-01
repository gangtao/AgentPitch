"""SandboxResult and PlayerSandboxContext — per-call value objects.

Both are mutable plain dataclasses (not Pydantic, not frozen) — they live on
the per-tick hot path (~540,000 calls/match) and the circuit breaker writes
to PlayerSandboxContext.disabled. Per ADR-0001 + ADR-0012.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from src.foundation.action import Action
from src.foundation.sandbox.status import ExecutionStatus


@dataclass
class SandboxResult:
    """Envelope returned by Sandbox.compile() / Sandbox.execute().

    Per AC-SANDBOX-16: `error_type` contains only the exception class name
    (no traceback, no implementation details). Sanitization at construction
    site is enforced by Story 004 (execute); this dataclass enforces the
    schema (str | None) only.

    Timing split (both in ms, 0.0 when not applicable):
      serialization_ms — data-prep cost before the runtime sees the inputs:
                         deepcopy (Python), json.dumps (JS), msgpack.dumps (Wasm).
      execution_time_ms — runtime cost: compiled_fn() call (Python),
                          ctx.eval() (JS), wasm alloc+execute+read+dealloc (Wasm).
    The two fields are comparable across sandbox types; their sum is the total
    cost of one execute() call.
    """

    status: ExecutionStatus
    action: Optional[Action] = None
    serialization_ms: float = 0.0
    execution_time_ms: float = 0.0
    error_type: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class PlayerSandboxContext:
    """Per-player runtime state held by the Sandbox across calls.

    `compiled_fn` is set by Sandbox.compile(); `module_globals` carries
    cross-tick persistent state for that player's module; the circuit-breaker
    fields (`consecutive_timeout_count`, `disabled`) are mutated by Sandbox.execute()
    + Sandbox.disable() in Stories 004 and 005.
    """

    compiled_fn: Optional[Callable] = None
    module_globals: dict = field(default_factory=dict)
    consecutive_timeout_count: int = 0
    disabled: bool = False
