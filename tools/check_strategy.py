#!/usr/bin/env python3
"""Compile-check a Python decide() strategy in the RestrictedPython sandbox.

Usage: python3 tools/check_strategy.py data/strategies/<file>.py
Exit 0 + "OK" on success; exit 1 + error detail on failure.
"""
import sys

from src.foundation.sandbox.python_sandbox import RestrictedPythonSandbox
from src.foundation.sandbox.status import ExecutionStatus


def main() -> int:
    path = sys.argv[1]
    with open(path) as f:
        code = f.read()
    sb = RestrictedPythonSandbox()
    res = sb.compile("team_a_0", code)
    if res.status == ExecutionStatus.SUCCESS:
        print(f"OK: {path} compiled cleanly")
        return 0
    print(f"FAIL: {path}")
    print(f"  status={res.status}")
    print(f"  error_type={res.error_type}")
    print(f"  error_message={res.error_message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
