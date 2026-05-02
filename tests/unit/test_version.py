"""Smoke test: the installed package exposes a non-empty version string."""
from __future__ import annotations

import importlib.metadata
import re


def test_package_version_is_set():
    version = importlib.metadata.version("agent-pitch")
    assert version, "importlib.metadata returned an empty version"


def test_package_version_looks_like_semver():
    version = importlib.metadata.version("agent-pitch")
    # Accepts plain semver (0.1.0) and setuptools-scm dev suffixes (0.1.0.dev3+gabcdef)
    assert re.match(r"^\d+\.\d+", version), (
        f"Version {version!r} does not start with MAJOR.MINOR"
    )
