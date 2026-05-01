"""Strategy Library — paired source + sidecar I/O for the user library.

Per ADR-0023. Each strategy in `<data-dir>/strategies/` is a pair:
  <name>.py          — Python source the user/LLM wrote
  <name>.meta.json   — sidecar with provider, model, created_by, timestamps

Distinct from `src/foundation/strategy_storage.py`, which owns the per-match
versioned archive (`<log-dir>/strategies/<team>/strategy_v<N>.py`) with its
7-field comment header. The two mechanisms coexist by scope.

Lives at `src/` top level (not `src/foundation/`) so `src/api/` may import it
without violating the ADR-0006 isolation boundary — same precedent as
`src/secrets_store.py`. This module is pure file I/O; no engine code, no
sandbox, no LLM provider.

Atomicity: source written first, then sidecar — both via temp + os.replace.
A partial failure can leave a `.py` without a sidecar (legacy state, tolerated
as `UNKNOWN_META`); the reverse cannot occur and is treated as corruption.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class StrategyLibraryError(Exception):
    """Base class for all strategy library failures."""


class StrategyLibraryNotFoundError(StrategyLibraryError):
    """No `.py` file exists for the requested strategy name."""


class StrategyLibraryWriteError(StrategyLibraryError):
    """Filesystem error during a paired write or delete."""


class InvalidStrategyNameError(StrategyLibraryError):
    """Strategy name failed format validation."""


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

_VALID_CREATED_BY = frozenset({"llm", "manual"})
_LANG_TO_EXT: dict[str, str] = {"python": ".py", "javascript": ".js", "rust": ".rs"}
_EXT_TO_LANG: dict[str, str] = {v: k for k, v in _LANG_TO_EXT.items()}
_VALID_LANGUAGES = frozenset(_LANG_TO_EXT.keys())


@dataclass(frozen=True)
class StrategyLibraryMeta:
    """Sidecar metadata for a user-library strategy file (per ADR-0023).

    `prompt` and `template_version` are populated only when
    `created_by == "llm"`; they are `None` for manual/baseline entries.
    """

    provider: str               # Built-in ('anthropic'|'openai'|'gemini') or custom (e.g., 'ollama', 'vllm')
    model: str                  # e.g. 'claude-sonnet-4-6', 'hand-written', 'unknown'
    created_by: Literal["llm", "manual"]
    created_at: str             # ISO 8601 UTC; "" for unknown/legacy
    last_modified_at: str       # ISO 8601 UTC; "" for unknown/legacy
    prompt: str | None = None
    template_version: str | None = None
    language: str = "python"
    # Generation performance — populated by the generate-strategy pipeline
    generation_latency_ms: float | None = None
    generation_input_tokens: int | None = None
    generation_output_tokens: int | None = None
    strategy_size_bytes: int | None = None


UNKNOWN_META = StrategyLibraryMeta(
    provider="unknown",
    model="unknown",
    created_by="manual",
    created_at="",
    last_modified_at="",
    language="python",
)


def _now_iso() -> str:
    """Current UTC time as ISO 8601 with Z suffix (matches strategy_storage)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def library_dir(data_home: Path | str) -> Path:
    """Return `<data_home>/strategies/`. Pure path arithmetic."""
    return Path(data_home) / "strategies"


def source_path(data_home: Path | str, name: str, language: str = "python") -> Path:
    """Return `<data_home>/strategies/<name>.<ext>`. Validates name."""
    _validate_name(name)
    ext = _LANG_TO_EXT.get(language, ".py")
    return library_dir(data_home) / f"{name}{ext}"


def meta_path(data_home: Path | str, name: str) -> Path:
    """Return `<data_home>/strategies/<name>.meta.json`. Validates name."""
    _validate_name(name)
    return library_dir(data_home) / f"{name}.meta.json"


def _validate_name(name: str) -> None:
    if not isinstance(name, str) or not _NAME_RE.fullmatch(name):
        raise InvalidStrategyNameError(
            f"Invalid strategy name {name!r}: must match {_NAME_RE.pattern}"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_meta(meta: StrategyLibraryMeta) -> None:
    # Provider can be any string (built-in or custom) — validate basic constraints only
    if not isinstance(meta.provider, str) or not meta.provider or len(meta.provider) > 64:
        raise StrategyLibraryError(
            f"Invalid provider {meta.provider!r}: must be a non-empty string (max 64 chars)"
        )
    if meta.created_by not in _VALID_CREATED_BY:
        raise StrategyLibraryError(
            f"Invalid created_by {meta.created_by!r}; must be one of {sorted(_VALID_CREATED_BY)}"
        )
    if meta.language not in _VALID_LANGUAGES:
        raise StrategyLibraryError(
            f"Invalid language {meta.language!r}; must be one of {sorted(_VALID_LANGUAGES)}"
        )
    if not isinstance(meta.model, str) or not meta.model:
        raise StrategyLibraryError("model must be a non-empty string")
    # `template_version` is required when LLM-generated — it is always known
    # at generation time (SPB stamps it). `prompt` is optional even for LLM:
    # the generation endpoint accepts an empty prompt (USER INTENT fallback in
    # the template), and the sidecar should mirror that — empty/missing prompt
    # is a valid LLM strategy. (Per ADR-0023 amendment 2026-04-26.)
    if meta.created_by == "llm":
        if not meta.template_version:
            raise StrategyLibraryError("LLM-generated strategy must include `template_version`")


# ---------------------------------------------------------------------------
# JSON (de)serialization
# ---------------------------------------------------------------------------


def _meta_to_json_bytes(meta: StrategyLibraryMeta) -> bytes:
    """Serialize meta to indented JSON bytes. Drops None fields for cleanliness."""
    raw = asdict(meta)
    raw = {k: v for k, v in raw.items() if v is not None}
    return (json.dumps(raw, indent=2, sort_keys=False) + "\n").encode("utf-8")


def _meta_from_json(data: dict) -> StrategyLibraryMeta:
    """Build StrategyLibraryMeta from a parsed JSON dict.

    Tolerates extra/unknown keys by ignoring them. Required fields missing →
    `StrategyLibraryError`.
    """
    required = ("provider", "model", "created_by", "created_at", "last_modified_at")
    missing = [k for k in required if k not in data]
    if missing:
        raise StrategyLibraryError(
            f"Sidecar missing required fields: {missing}"
        )
    return StrategyLibraryMeta(
        provider=data["provider"],
        model=data["model"],
        created_by=data["created_by"],
        created_at=data["created_at"],
        last_modified_at=data["last_modified_at"],
        prompt=data.get("prompt"),
        template_version=data.get("template_version"),
        language=data.get("language", "python"),
        generation_latency_ms=data.get("generation_latency_ms"),
        generation_input_tokens=data.get("generation_input_tokens"),
        generation_output_tokens=data.get("generation_output_tokens"),
        strategy_size_bytes=data.get("strategy_size_bytes"),
    )


# ---------------------------------------------------------------------------
# Atomic file primitives
# ---------------------------------------------------------------------------


def _atomic_write_bytes(target: Path, payload: bytes) -> None:
    """Write `payload` to `target` atomically via temp + os.replace.

    Caller is responsible for parent directory existence.
    """
    tmp = target.with_suffix(target.suffix + ".tmp")
    try:
        with open(tmp, "wb") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)
    except OSError as e:
        # Best-effort cleanup; ignore secondary errors.
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        raise StrategyLibraryWriteError(f"atomic write failed for {target}: {e}") from e


def _atomic_write_text(target: Path, text: str) -> None:
    _atomic_write_bytes(target, text.encode("utf-8"))


# ---------------------------------------------------------------------------
# Public API — write / read / delete / list
# ---------------------------------------------------------------------------


def write_strategy(
    data_home: Path | str,
    name: str,
    source: str,
    meta: StrategyLibraryMeta,
) -> StrategyLibraryMeta:
    """Atomic paired write: `<name>.py` then `<name>.meta.json`.

    Source written first so that a sidecar without a corresponding source
    file cannot occur. The reverse (source without sidecar) is tolerated by
    readers as legacy state.

    Returns the meta as written (caller-provided meta unchanged).
    """
    _validate_meta(meta)

    src = source_path(data_home, name, language=meta.language)
    md = meta_path(data_home, name)

    try:
        src.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise StrategyLibraryWriteError(
            f"failed to create {src.parent}: {e}"
        ) from e

    _atomic_write_text(src, source)
    _atomic_write_bytes(md, _meta_to_json_bytes(meta))
    return meta


def read_strategy(
    data_home: Path | str,
    name: str,
) -> tuple[str, StrategyLibraryMeta]:
    """Return `(source, meta)`.

    Raises `StrategyLibraryNotFoundError` if the `.py` file is absent.
    Returns `UNKNOWN_META` for the meta when the sidecar is missing
    (legacy state).
    """
    meta = read_meta(data_home, name)
    src = source_path(data_home, name, language=meta.language)
    if not src.exists():
        raise StrategyLibraryNotFoundError(f"Strategy '{name}' not found at {src}")

    try:
        source = src.read_text(encoding="utf-8")
    except OSError as e:
        raise StrategyLibraryError(f"failed to read {src}: {e}") from e

    return source, meta


def read_meta(
    data_home: Path | str,
    name: str,
) -> StrategyLibraryMeta:
    """Return the sidecar meta, or `UNKNOWN_META` if it is missing.

    A malformed sidecar (invalid JSON, missing required fields) raises
    `StrategyLibraryError` — the caller chose to write it, so corruption
    should surface rather than silently degrade.
    """
    md = meta_path(data_home, name)
    if not md.exists():
        return UNKNOWN_META
    try:
        raw = json.loads(md.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise StrategyLibraryError(f"sidecar unreadable at {md}: {e}") from e
    if not isinstance(raw, dict):
        raise StrategyLibraryError(f"sidecar at {md} is not a JSON object")
    return _meta_from_json(raw)


def update_source(
    data_home: Path | str,
    name: str,
    source: str,
) -> None:
    """Atomically rewrite the `.py` source for an existing strategy.

    Sidecar untouched — caller is expected to follow with `update_meta()`
    to bump `last_modified_at`. Raises `StrategyLibraryNotFoundError` if
    the source `.py` is missing.
    """
    meta = read_meta(data_home, name)
    src = source_path(data_home, name, language=meta.language)
    if not src.exists():
        raise StrategyLibraryNotFoundError(
            f"cannot update source — strategy '{name}' not found at {src}"
        )
    try:
        src.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise StrategyLibraryWriteError(
            f"failed to create {src.parent}: {e}"
        ) from e
    _atomic_write_text(src, source)


def update_meta(
    data_home: Path | str,
    name: str,
    **fields,
) -> StrategyLibraryMeta:
    """Read-modify-write the sidecar for an existing strategy.

    Used by PUT to bump `last_modified_at` while preserving everything else.
    If no sidecar exists (legacy file edited for the first time), writes a
    fresh `UNKNOWN_META`-ish sidecar with the requested overrides.

    Raises `StrategyLibraryNotFoundError` if the source `.py` is missing —
    we never write a sidecar for a non-existent strategy.
    """
    existing = read_meta(data_home, name)
    src = source_path(data_home, name, language=existing.language)
    if not src.exists():
        raise StrategyLibraryNotFoundError(
            f"cannot update meta — source missing at {src}"
        )

    md = meta_path(data_home, name)
    if not md.exists():
        # Legacy file: synthesize a sensible base before overrides.
        now = _now_iso()
        existing = StrategyLibraryMeta(
            provider="unknown",
            model="unknown",
            created_by="manual",
            created_at=now,
            last_modified_at=now,
        )

    updated = replace(existing, **fields)
    _validate_meta(updated)
    _atomic_write_bytes(md, _meta_to_json_bytes(updated))
    return updated


def delete_strategy(data_home: Path | str, name: str) -> None:
    """Remove both `<name>.py` and `<name>.meta.json`.

    Missing sidecar is tolerated. Missing source raises
    `StrategyLibraryNotFoundError` (callers expect 404 semantics).
    """
    meta = read_meta(data_home, name)
    src = source_path(data_home, name, language=meta.language)
    md = meta_path(data_home, name)

    if not src.exists():
        raise StrategyLibraryNotFoundError(f"Strategy '{name}' not found at {src}")

    try:
        src.unlink()
    except OSError as e:
        raise StrategyLibraryWriteError(f"failed to delete {src}: {e}") from e

    if md.exists():
        try:
            md.unlink()
        except OSError as e:
            # Source already gone; surface the sidecar failure but the strategy
            # is effectively deleted (next write re-creates the sidecar).
            raise StrategyLibraryWriteError(f"failed to delete {md}: {e}") from e


def list_strategies(
    data_home: Path | str,
) -> list[tuple[str, StrategyLibraryMeta]]:
    """Return `[(name, meta), …]` for every `.py` in the library.

    One `os.scandir` pass; pairs each `.py` with its sidecar (or
    `UNKNOWN_META` when absent). Names with invalid characters are skipped.
    Order is unspecified — callers sort as they need.
    """
    d = library_dir(data_home)
    if not d.exists():
        return []

    out: list[tuple[str, StrategyLibraryMeta]] = []
    for entry in d.iterdir():
        if not entry.is_file() or entry.suffix not in _EXT_TO_LANG:
            continue
        stem = entry.stem
        if not _NAME_RE.fullmatch(stem):
            continue
        try:
            meta = read_meta(data_home, stem)
        except StrategyLibraryError:
            meta = UNKNOWN_META
        # Infer language from extension when sidecar is missing/legacy
        if meta.language == "python" and entry.suffix == ".js":
            meta = replace(meta, language="javascript")
        elif meta.language == "python" and entry.suffix == ".rs":
            meta = replace(meta, language="rust")
        out.append((stem, meta))
    return out


__all__ = [
    "StrategyLibraryError",
    "StrategyLibraryNotFoundError",
    "StrategyLibraryWriteError",
    "InvalidStrategyNameError",
    "StrategyLibraryMeta",
    "UNKNOWN_META",
    "_LANG_TO_EXT",
    "_EXT_TO_LANG",
    "library_dir",
    "source_path",
    "meta_path",
    "write_strategy",
    "read_strategy",
    "read_meta",
    "update_source",
    "update_meta",
    "delete_strategy",
    "list_strategies",
]
