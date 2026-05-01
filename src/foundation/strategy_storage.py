"""Strategy Storage — pure I/O for LLM-generated strategy code.

One file per team. Plain `.py` files only — no compile/exec, no SQLite, no cache.
Atomic writes via temp+os.replace. Self-healing reads via current.py + version archive.

Per ADR-0008. CGP/PMEP own compilation through the sandbox before they call
write_strategy here; this module never executes the code it stores.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exception hierarchy (per ADR-0008 §9)
# ---------------------------------------------------------------------------


class StrategyStorageError(Exception):
    """Base class for all strategy storage failures."""


class StrategyNotFoundError(StrategyStorageError):
    """No strategy file exists for the requested team."""


class VersionNotFoundError(StrategyStorageError):
    """Specific version requested but not present in the archive."""


class WriteFailedError(StrategyStorageError):
    """Atomic write failed (filesystem error, permission denied, etc.)."""


# ---------------------------------------------------------------------------
# Metadata (caller-owned fields only)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StrategyMetadata:
    """Caller-owned metadata fields for a strategy file write.

    Note: `version` and `timestamp` are NOT in this dataclass — they are
    assigned by `write_strategy` and `_build_header` respectively. This keeps
    callers from setting them inconsistently.
    """

    team_id: str            # "team_a" or "team_b"
    match_number: int       # 0 = pre-season; N = after match N
    llm_provider: str       # "openai" or "anthropic"
    llm_model: str          # e.g. "gpt-4o"
    generated_by: str       # "code-generation-pipeline" or "post-match-evolution"
    language: str = "python"  # "python" | "javascript" | "rust" — default keeps existing call sites valid
    # Generation performance — populated by CGP when LLM response data is available
    generation_latency_ms: float | None = None
    generation_input_tokens: int | None = None
    generation_output_tokens: int | None = None
    strategy_size_bytes: int | None = None


# ---------------------------------------------------------------------------
# Language → file extension and comment prefix
# ---------------------------------------------------------------------------

_LANG_TO_EXT: dict[str, str] = {
    "python": ".py",
    "javascript": ".js",
    "rust": ".rs",
}

_LANG_TO_COMMENT: dict[str, str] = {
    "python": "#",
    "javascript": "//",
    "rust": "//",
}


def _ext_for(language: str) -> str:
    """Return the file extension for a language. Raises on unknown language."""
    try:
        return _LANG_TO_EXT[language]
    except KeyError as e:
        raise ValueError(
            f"Unknown language {language!r}; must be one of {sorted(_LANG_TO_EXT)}"
        ) from e


def _comment_for(language: str) -> str:
    """Return the line-comment prefix for a language. Raises on unknown language."""
    try:
        return _LANG_TO_COMMENT[language]
    except KeyError as e:
        raise ValueError(
            f"Unknown language {language!r}; must be one of {sorted(_LANG_TO_COMMENT)}"
        ) from e


# ---------------------------------------------------------------------------
# Path + version helpers
# ---------------------------------------------------------------------------


def strategy_dir(log_dir: str, team_id: str) -> Path:
    """Return the path to a team's strategy directory. Pure path arithmetic."""
    return Path(log_dir) / "strategies" / team_id


# Matches strategy_v<N>.py, strategy_v<N>.js, or strategy_v<N>.rs — language inferred from extension.
_VERSION_FILENAME_RE = re.compile(r"strategy_v(\d+)\.(py|js|rs)")


def list_versions(log_dir: str, team_id: str) -> list[int]:
    """Return sorted ascending integer versions present in the team's directory.

    Returns [] when the directory does not exist (per AC-SS-08). Files that
    don't match `strategy_v<int>.py` are silently ignored (per AC-SS-15).
    """
    d = strategy_dir(log_dir, team_id)
    if not d.exists():
        return []
    versions: list[int] = []
    for p in d.iterdir():
        m = _VERSION_FILENAME_RE.fullmatch(p.name)
        if m is not None:
            versions.append(int(m.group(1)))
    return sorted(versions)


def _build_header(version: int, metadata: StrategyMetadata) -> str:
    """Build the comment header for a strategy file.

    Format is fixed (per ADR-0008 §5) so a `diff` between two versions only
    changes data, never whitespace. Timestamp is assigned here in UTC ISO 8601.
    Comment prefix and file extension follow `metadata.language` so JavaScript
    strategies render as valid `//`-commented `.js` files.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    c = _comment_for(metadata.language)
    ext = _ext_for(metadata.language)
    header = (
        f"{c} strategy_v{version}{ext}\n"
        f"{c} team_id:      {metadata.team_id}\n"
        f"{c} version:      {version}\n"
        f"{c} match_number: {metadata.match_number}\n"
        f"{c} language:     {metadata.language}\n"
        f"{c} timestamp:    {ts}\n"
        f"{c} llm_provider: {metadata.llm_provider}\n"
        f"{c} llm_model:    {metadata.llm_model}\n"
        f"{c} generated_by: {metadata.generated_by}\n"
    )
    if metadata.generation_latency_ms is not None:
        header += f"{c} latency_ms:   {metadata.generation_latency_ms:.0f}\n"
    if metadata.generation_input_tokens is not None:
        header += f"{c} input_tokens: {metadata.generation_input_tokens}\n"
    if metadata.generation_output_tokens is not None:
        header += f"{c} output_tokens:{metadata.generation_output_tokens}\n"
    if metadata.strategy_size_bytes is not None:
        header += f"{c} size_bytes:   {metadata.strategy_size_bytes}\n"
    return header + "\n"


# ---------------------------------------------------------------------------
# Story 002 — atomic write
# ---------------------------------------------------------------------------


def write_strategy(
    log_dir: str,
    team_id: str,
    code: str,
    metadata: StrategyMetadata,
) -> int:
    """Atomically write a new strategy version + update current.py pointer.

    Returns the version number written. Sequential per directory scan; gaps
    in existing version numbers are preserved (next = max + 1).

    Sequence (per ADR-0008):
      1. Determine next_version = max(list_versions) + 1 (0 if empty)
      2. mkdir -p the team's strategy directory
      3. Write `header + code` to `strategy_v<N>.py.tmp`
      4. Atomic os.replace temp → `strategy_v<N>.py`
      5. shutil.copy2 versioned file → `current.py`

    Raises:
        ValueError: metadata.team_id != team_id arg (catches arg-swap bugs)
        WriteFailedError: any OSError during the sequence — original chained via __cause__
    """
    if metadata.team_id != team_id:
        raise ValueError(
            f"team_id mismatch: arg={team_id!r}, metadata={metadata.team_id!r}"
        )

    ext = _ext_for(metadata.language)

    d = strategy_dir(log_dir, team_id)

    # Language-mismatch guard: a single team's archive is one language for life.
    # Refuse to mix `.py` and `.js` versions in the same directory.
    if d.exists():
        for p in d.iterdir():
            m = _VERSION_FILENAME_RE.fullmatch(p.name)
            if m is not None and m.group(2) != ext.lstrip("."):
                raise ValueError(
                    f"language mismatch for {team_id}: existing {p.name} cannot "
                    f"coexist with new {metadata.language} (.{ext.lstrip('.')}) version"
                )

    next_version = max(list_versions(log_dir, team_id), default=0) + 1

    try:
        d.mkdir(parents=True, exist_ok=True)
        header = _build_header(next_version, metadata)
        body = header + code

        temp_file = d / f"strategy_v{next_version}{ext}.tmp"
        versioned_file = d / f"strategy_v{next_version}{ext}"
        current_file = d / f"current{ext}"

        # 1. Write to temp file
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(body)

        # 2. Atomic rename — POSIX guarantees atomicity at the filesystem level
        os.replace(temp_file, versioned_file)

        # 3. Update current.py pointer (best-effort; self-healing read recovers)
        shutil.copy2(versioned_file, current_file)
    except OSError as e:
        raise WriteFailedError(
            f"write_strategy failed for {team_id} v{next_version}: {e}"
        ) from e

    return next_version


# ---------------------------------------------------------------------------
# Story 003 — read paths (current with self-healing; specific version)
# ---------------------------------------------------------------------------


def _find_versioned_file(d: Path, version: int) -> Path | None:
    """Return strategy_v<version>.{py,js} if it exists, else None.

    A team directory only ever holds one language (enforced by `write_strategy`),
    so at most one extension matches.
    """
    for ext in _LANG_TO_EXT.values():
        candidate = d / f"strategy_v{version}{ext}"
        if candidate.exists():
            return candidate
    return None


def _find_current_file(d: Path) -> Path | None:
    """Return the existing current.{py,js} file, else None."""
    for ext in _LANG_TO_EXT.values():
        candidate = d / f"current{ext}"
        if candidate.exists():
            return candidate
    return None


def read_version(log_dir: str, team_id: str, version: int) -> str:
    """Return the content of strategy_v<version>.{py,js} for the given team.

    Raises VersionNotFoundError if no file with either extension exists. Does
    NOT auto-repair — the caller (e.g. Code Viewer Panel) wants to know about
    missing versions.
    """
    d = strategy_dir(log_dir, team_id)
    versioned_file = _find_versioned_file(d, version)
    if versioned_file is None:
        raise VersionNotFoundError(
            f"strategy_v{version}.(py|js) not found for {team_id}"
        )
    return versioned_file.read_text(encoding="utf-8")


def read_current(log_dir: str, team_id: str) -> str:
    """Return the content of current.{py,js} for the given team, self-healing if needed.

    Self-healing cases:
      - current.* missing but strategy_v<N>.* exists → copy from highest version
      - current.* present but stale (content != highest strategy_v<N>.*) → repair

    Both repair paths log a WARNING with the team_id and version. The extension
    is taken from whichever versioned file exists — a team directory only ever
    holds one language (enforced by `write_strategy`).

    Raises StrategyNotFoundError if neither current.* nor any strategy_v<N>.* exists.
    """
    d = strategy_dir(log_dir, team_id)
    current_file = _find_current_file(d)
    versions = list_versions(log_dir, team_id)

    # Case 1: nothing exists
    if current_file is None and not versions:
        raise StrategyNotFoundError(f"No strategy found for {team_id}")

    # Case 2: current.* missing but versioned files exist → repair using same ext
    if current_file is None:
        highest = max(versions)
        src = _find_versioned_file(d, highest)
        # _find_versioned_file is guaranteed non-None because list_versions saw it.
        assert src is not None
        current_file = d / f"current{src.suffix}"
        shutil.copy2(src, current_file)
        _log.warning(
            "%s repaired from strategy_v%d%s for %s",
            current_file.name, highest, src.suffix, team_id,
        )
        return current_file.read_text(encoding="utf-8")

    # Case 3: current.* exists — verify it matches the highest version
    current_content = current_file.read_text(encoding="utf-8")
    if versions:
        highest = max(versions)
        highest_file = _find_versioned_file(d, highest)
        assert highest_file is not None
        highest_content = highest_file.read_text(encoding="utf-8")
        if current_content != highest_content:
            shutil.copy2(highest_file, current_file)
            _log.warning(
                "%s repaired from strategy_v%d%s for %s (content mismatch)",
                current_file.name, highest, highest_file.suffix, team_id,
            )
            return highest_content

    # Case 4: healthy fast path — no I/O beyond the read above
    return current_content
