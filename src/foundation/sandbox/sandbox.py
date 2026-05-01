"""Backward-compatible shim — imports RestrictedPythonSandbox as Sandbox.

ADR-0024 deprecation window: all consumers currently import ``Sandbox`` from
this module or from the package __init__. This shim keeps them working.
Remove once all consumers migrate to importing from python_sandbox or using
the Protocol from base.
"""

from src.foundation.sandbox.python_sandbox import RestrictedPythonSandbox as Sandbox

__all__ = ["Sandbox"]