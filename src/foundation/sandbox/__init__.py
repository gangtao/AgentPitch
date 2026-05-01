"""Code Sandbox package — safe LLM code compilation and execution.

Re-exports the public surface defined across this subpackage.

During the ADR-0024 deprecation window, the ``Sandbox`` name resolves to the
concrete ``RestrictedPythonSandbox`` class (via the shim in sandbox.py) so
existing ``Sandbox()`` constructor calls keep working. Import the Protocol
from ``src.foundation.sandbox.base.Sandbox`` when you need the abstract type.
"""

from src.foundation.sandbox.factory import SandboxFactory, UnknownStrategyLanguage
from src.foundation.sandbox.match_sandboxes import MatchSandboxes
from src.foundation.sandbox.python_sandbox import RestrictedPythonSandbox
from src.foundation.sandbox.result import PlayerSandboxContext, SandboxResult
from src.foundation.sandbox.sandbox import Sandbox
from src.foundation.sandbox.status import ExecutionStatus

try:
    from src.foundation.sandbox.quickjs_sandbox import QuickJSSandbox
except ImportError:
    QuickJSSandbox = None  # type: ignore[assignment,misc]

__all__ = [
    "ExecutionStatus",
    "MatchSandboxes",
    "PlayerSandboxContext",
    "QuickJSSandbox",
    "RestrictedPythonSandbox",
    "Sandbox",
    "SandboxFactory",
    "SandboxResult",
    "UnknownStrategyLanguage",
]
