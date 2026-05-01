"""ExecutionStatus enum — 6 values per ADR-0012.

Note: TR-SB-008's GDD wording lists 5 values (RUNTIME_ERROR variant). ADR-0012
supersedes with 6 values: SUCCESS / EXCEPTION / TIMEOUT / INVALID_RETURN /
DISABLED / COMPILE_ERROR. This module implements the ADR-0012 form.
"""

from __future__ import annotations

from enum import Enum


class ExecutionStatus(Enum):
    """Outcome of one Sandbox.execute() / Sandbox.compile() call.

    Values are lowercase snake_case strings of the member name (per ADR-0012)
    so they serialize cleanly in match log JSONL records.
    """

    SUCCESS = "success"
    EXCEPTION = "exception"
    TIMEOUT = "timeout"
    INVALID_RETURN = "invalid_return"
    DISABLED = "disabled"
    COMPILE_ERROR = "compile_error"
