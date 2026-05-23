"""FastAPI application for agent_pitch HTTP server."""
from __future__ import annotations
import asyncio
import json
import math
import os
import sys
import shutil
import time
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI, Query, Path as PathParam, HTTPException
import re
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal, Optional
from pydantic import ValidationError

# GameConfig, StorageConfig, and LLM models are API-layer-local (HTTP validation only) per ADR-0006:
# the API must NOT import from src/foundation/. The constraints mirror
# fields in foundation/config_models.py but live here independently.
from src.api.http_server.game_config import GameConfig
from src.api.http_server.storage_config import StorageConfig, validate_data_home
from src.api.http_server.llm_config import LLMConfigPayload, TestConnectionRequest
from src.api.http_server.match_config_payload import MatchConfigPayload
from src.api.http_server.team_config_payload import TeamConfigPayload
from src.api.http_server.start_match_payload import StartMatchPayload
from src.api.http_server.strategy_payload import StrategyPayload
from src.api.http_server.strategy_create_payload import StrategyCreatePayload, StrategyGeneratePayload
from src.api.http_server.series_payload import StartSeriesPayload
from src.api.http_server.series_metadata import (
    series_dir as _series_dir,
    read_series_json as _read_series_json,
    write_series_json as _write_series_json,
    list_series as _list_series,
)
from src.api.http_server.cup_payload import StartCupPayload, team_names_for_match
from src.cup_metadata import (
    cup_dir as _cup_dir,
    read_cup_json as _read_cup_json,
    write_cup_json as _write_cup_json,
    list_cups as _list_cups,
    generate_bracket as _generate_bracket,
)
from src.api.http_server.league_payload import StartLeaguePayload
from src.league_metadata import (
    league_dir as _league_dir,
    read_league_json as _read_league_json,
    write_league_json as _write_league_json,
    list_leagues as _list_leagues,
    generate_schedule as _generate_schedule,
)
from src.secrets_store import (
    load_secrets, save_secrets, get_api_key, get_key_status
)
# Strategy library lives at src/ top-level (not src/foundation/) so the API
# may import it without violating the ADR-0006 boundary — same precedent as
# src.secrets_store. Pure file I/O only; no engine code.
from src.strategy_library import (
    StrategyLibraryError,
    StrategyLibraryNotFoundError,
    StrategyLibraryMeta,
    UNKNOWN_META,
    InvalidStrategyNameError,
    delete_strategy as lib_delete_strategy,
    library_dir as lib_library_dir,
    list_strategies as lib_list_strategies,
    meta_path as lib_meta_path,
    read_strategy as lib_read_strategy,
    read_meta as lib_read_meta,
    source_path as lib_source_path,
    update_meta as lib_update_meta,
    update_source as lib_update_source,
    write_strategy as lib_write_strategy,
)


from src.api.http_server.match_stats import compute_match_stats

_STATIC_DIR = Path(__file__).parent / "static"


def _meta_to_dict(meta: StrategyLibraryMeta) -> dict:
    """Render a StrategyLibraryMeta into a JSON-friendly dict for HTTP responses.

    Drops `None` optional fields (prompt, template_version) so manual entries
    don't surface dangling nulls in the UI.
    """
    out = {
        "provider":         meta.provider,
        "model":            meta.model,
        "created_by":       meta.created_by,
        "created_at":       meta.created_at,
        "last_modified_at": meta.last_modified_at,
        "language":         meta.language,
    }
    if meta.prompt is not None:
        out["prompt"] = meta.prompt
    if meta.template_version is not None:
        out["template_version"] = meta.template_version
    if meta.generation_latency_ms is not None:
        out["generation_latency_ms"] = meta.generation_latency_ms
    if meta.generation_input_tokens is not None:
        out["generation_input_tokens"] = meta.generation_input_tokens
    if meta.generation_output_tokens is not None:
        out["generation_output_tokens"] = meta.generation_output_tokens
    return out


def _now_iso() -> str:
    """Current UTC time as ISO 8601 with Z suffix (matches strategy_library)."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# SSE streaming constants
SSE_POLL_MS = 100
SSE_LIVE_TIMEOUT_S = 300

# Storage subdirs computation cache (time_bucket = int(time.time() / 30))
_SUBDIR_CACHE = {}


def _find_latest_match(log_dir: Path):
    """Returns (match_dir, meta_dict, meta_file_mtime) or None if no valid match."""
    if not log_dir.exists():
        return None
    candidates = []
    for sub in log_dir.iterdir():
        if not sub.is_dir():
            continue
        meta_path = sub / "meta.json"
        if not meta_path.exists():
            continue
        candidates.append((os.path.getmtime(meta_path), sub.name, sub, meta_path))
    if not candidates:
        return None
    # Sort by mtime desc, tie-break by lexicographic dir name desc
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    _, _, sub, meta_path = candidates[0]
    return (sub, json.loads(meta_path.read_text()), os.path.getmtime(meta_path))


def _resolve_match_dir(matches_dir: Path, match_id):
    """Returns Optional[Tuple[Path, Optional[dict]]]. (Untyped to keep
    Python 3.9 compat without the typing.Optional dance.)"""
    """Resolve the match directory + meta for live-viewer endpoints.

    If `match_id` is supplied, look at `<matches_dir>/match_<id>/`:
      - If meta.json present → return (dir, meta)
      - If only events.jsonl → return (dir, None)  ← in-progress
      - Else → return None
    If `match_id` is None, fall back to "most recent" (in-progress preferred,
    then latest completed by mtime).
    """
    if match_id:
        candidate = matches_dir / f"match_{match_id}"
        if not candidate.is_dir():
            return None
        meta_path = candidate / "meta.json"
        if meta_path.exists():
            return (candidate, json.loads(meta_path.read_text()))
        if (candidate / "events.jsonl").exists():
            return (candidate, None)  # in-progress
        return None

    # No match_id: prefer in-progress over latest completed.
    selected = _select_match_for_streaming(matches_dir)
    if selected is None:
        return None
    match_dir, _in_progress = selected
    meta_path = match_dir / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else None
    return (match_dir, meta)


def _sanitize_floats(obj):
    """Replace NaN/Infinity with None so JSON serialization succeeds."""
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    if isinstance(obj, dict):
        return {k: _sanitize_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_floats(v) for v in obj]
    return obj


def _read_events_jsonl(match_dir: Path):
    """Read all lines from events.jsonl, parse as JSON, return list."""
    path = match_dir / "events.jsonl"
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    return [_sanitize_floats(json.loads(line)) for line in lines if line.strip()]


def _select_match_for_streaming(log_dir: Path):
    """Returns (match_dir, in_progress: bool) or None.

    Prefers in-progress matches (events.jsonl exists, meta.json absent)
    over completed matches for SSE streaming endpoints.
    """
    if not log_dir.exists():
        return None
    in_progress = []
    completed = []
    for sub in log_dir.iterdir():
        if not sub.is_dir():
            continue
        events_path = sub / "events.jsonl"
        meta_path = sub / "meta.json"
        if events_path.exists() and not meta_path.exists():
            in_progress.append((os.path.getmtime(events_path), sub))
        elif meta_path.exists():
            completed.append((os.path.getmtime(meta_path), sub))
    if in_progress:
        in_progress.sort(reverse=True)
        return (in_progress[0][1], True)
    if completed:
        completed.sort(reverse=True)
        return (completed[0][1], False)
    return None


async def _stream_ticks(match_dir: Path, in_progress: bool, key_events_only: bool = False):
    """Generator yielding SSE-formatted bytes."""
    events_path = match_dir / "events.jsonl"
    meta_path = match_dir / "meta.json"

    # Open file and stream existing lines
    pos = 0
    buffer = b""
    started = asyncio.get_running_loop().time()

    while True:
        # Read any new bytes from the file
        if events_path.exists():
            with open(events_path, "rb") as f:
                f.seek(pos)
                new_bytes = f.read()
                pos = f.tell()
            buffer += new_bytes
            # Process complete lines
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                line_str = line.decode("utf-8", errors="replace").strip()
                if not line_str:
                    continue
                # Filter for key events if needed
                if key_events_only:
                    try:
                        rec = json.loads(line_str)
                        if not rec.get("is_key_event"):
                            continue
                    except Exception:
                        continue
                yield f"data: {line_str}\n\n".encode("utf-8")

        # Check if match is complete
        if meta_path.exists():
            meta_text = meta_path.read_text()
            yield f"event: match_complete\ndata: {meta_text}\n\n".encode("utf-8")
            return

        if not in_progress:
            # Completed match was selected at start but no meta yet — should not happen normally
            return

        # Timeout check
        if asyncio.get_running_loop().time() - started > SSE_LIVE_TIMEOUT_S:
            yield b'event: error\ndata: {"error": "stream_timeout"}\n\n'
            return

        await asyncio.sleep(SSE_POLL_MS / 1000)


def _load_storage_config(data_home: Path) -> dict:
    """Return the server's process-scoped data_home.

    Per the simplified architecture (2026-04-24), the data directory is
    fixed at server startup via `agent-pitch serve --data-dir <path>`.
    The UI Storage tab is read-only; the storage-settings.yaml mechanism
    is removed. The arg `data_home` here IS the server's data dir.
    """
    return {"data_home": str(data_home)}


def _compute_subdir_stats(data_home: Path) -> dict:
    """Compute subdirectory statistics with 30s cache."""
    time_bucket = int(time.time() / 30)
    cache_key = (str(data_home), time_bucket)

    if cache_key in _SUBDIR_CACHE:
        return _SUBDIR_CACHE[cache_key]

    # Clean old cache entries (keep only current bucket)
    _SUBDIR_CACHE.clear()

    subdirs = {}
    standard_subdirs = ["matches", "strategies", "configs", "arena", "cups", "leagues"]

    for subdir_name in standard_subdirs:
        subdir_path = data_home / subdir_name
        if subdir_path.exists() and subdir_path.is_dir():
            try:
                # Count entries and total size
                entries = list(subdir_path.rglob("*"))
                file_entries = [e for e in entries if e.is_file()]
                entry_count = len(file_entries)
                total_size = sum(e.stat().st_size for e in file_entries)
                size_mb = round(total_size / (1024 * 1024), 1)

                subdirs[f"{subdir_name}/"] = {
                    "entries": entry_count,
                    "size_mb": size_mb
                }
            except (OSError, PermissionError):
                # Skip directories we can't read
                subdirs[f"{subdir_name}/"] = {"entries": 0, "size_mb": 0.0}
        else:
            subdirs[f"{subdir_name}/"] = {"entries": 0, "size_mb": 0.0}

    # Add special files
    special_files = [
        "global-defaults.yaml",
        "llm-providers.yaml",
        ".secrets.json"
    ]

    for file_name in special_files:
        file_path = data_home / file_name
        if file_path.exists() and file_path.is_file():
            try:
                size_bytes = file_path.stat().st_size
                size_mb = round(size_bytes / (1024 * 1024), 3)
                subdirs[file_name] = {
                    "entries": 1,
                    "size_mb": size_mb
                }
            except (OSError, PermissionError):
                subdirs[file_name] = {"entries": 0, "size_mb": 0.0}
        else:
            # Show as missing but tracked
            subdirs[file_name] = {"entries": 0, "size_mb": 0.0}

    # Cache result
    _SUBDIR_CACHE[cache_key] = subdirs
    return subdirs


def _load_match_configs(data_home: Path) -> list:
    """Load all match configurations and return summary list."""
    configs_dir = data_home / "configs"

    if not configs_dir.exists():
        return []

    configs = []

    try:
        for config_file in configs_dir.glob("*.yaml"):
            if not config_file.is_file():
                continue

            try:
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f)

                if not data or not isinstance(data, dict):
                    continue

                # Extract basic info
                name = config_file.stem
                mtime = config_file.stat().st_mtime
                modified_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(mtime))

                # Create summary from config data
                summary = _create_config_summary(data)

                configs.append({
                    "name": name,
                    "modified_iso": modified_iso,
                    "summary": summary
                })

            except (yaml.YAMLError, OSError, KeyError):
                # Skip malformed or unreadable configs
                continue

    except (OSError, PermissionError):
        # Can't read configs directory
        return []

    # Sort by mtime descending
    configs.sort(key=lambda x: x["modified_iso"], reverse=True)
    return configs


def _create_config_summary(data: dict) -> dict:
    """Create summary object from config data."""
    try:
        match_data = data.get("match", {})
        team_a_data = data.get("team_a", {})
        team_b_data = data.get("team_b", {})

        # Extract basic params (defaults match GameConfig — see game_config.py)
        tick_rate = match_data.get("tick_rate", 10)
        duration_min = match_data.get("duration_minutes", 5)
        field_w = match_data.get("field_width", 100.0)
        field_h = match_data.get("field_height", 60.0)

        # Count players per team
        team_a_players = len(team_a_data.get("players", []))
        team_b_players = len(team_b_data.get("players", []))
        players_per_team = max(team_a_players, team_b_players)

        # Derive formations
        team_a_formation = _derive_formation(team_a_data.get("players", []))
        team_b_formation = _derive_formation(team_b_data.get("players", []))

        return {
            "tick_rate": tick_rate,
            "duration_min": duration_min,
            "field_w": field_w,
            "field_h": field_h,
            "formation": {
                "team_a": team_a_formation,
                "team_b": team_b_formation
            },
            "player_count": {
                "team_a": team_a_players,
                "team_b": team_b_players
            },
            "players_per_team": players_per_team
            # in_use_by is not implemented yet - would require checking active matches
        }

    except (KeyError, TypeError, ValueError):
        # Fallback summary for malformed configs (defaults match GameConfig)
        return {
            "tick_rate": 10,
            "duration_min": 5,
            "field_w": 100.0,
            "field_h": 60.0,
            "formation": {
                "team_a": "unknown",
                "team_b": "unknown"
            },
            "player_count": {
                "team_a": 0,
                "team_b": 0
            },
            "players_per_team": 0
        }


def _derive_formation(players: list) -> str:
    """Derive formation string from player list."""
    if not players:
        return "0-0-0"

    role_counts = {"GK": 0, "DEF": 0, "MID": 0, "FWD": 0}

    for player in players:
        role = player.get("role")
        if role in role_counts:
            role_counts[role] += 1

    # Standard formation notation (excluding GK)
    return f"{role_counts['DEF']}-{role_counts['MID']}-{role_counts['FWD']}"


def _strip_deprecated_llm_fields(data: dict) -> dict:
    """Remove deprecated llm_provider/llm_model fields from config data."""
    cleaned = data.copy()

    # Remove from team configs
    for team_key in ["team_a", "team_b"]:
        if team_key in cleaned:
            team_data = cleaned[team_key].copy()
            team_data.pop("llm_provider", None)
            team_data.pop("llm_model", None)
            cleaned[team_key] = team_data

    # Remove from root level if present
    cleaned.pop("llm_provider", None)
    cleaned.pop("llm_model", None)

    return cleaned


def _get_disk_usage(path: Path) -> dict:
    """Get disk usage statistics for the given path."""
    try:
        # Use shutil.disk_usage for cross-platform compatibility
        total, used, free = shutil.disk_usage(path)
        return {
            "total_bytes": total,
            "free_bytes": free
        }
    except (OSError, AttributeError):
        # Fallback values if disk_usage fails
        return {
            "total_bytes": 0,
            "free_bytes": 0
        }


# ───────────────────────────────────────────────────────────────────
# First-run seed data
# ───────────────────────────────────────────────────────────────────
# Project-rooted source for the canonical baseline strategy. Resolved relative
# to this file so it works regardless of the cwd the server is launched from.
# Layout: src/api/http_server/app.py → ../../../strategy/baseline.py
# (Moved from playtest/strategies/ 2026-04-25: tracked location keeps the
# canonical source in git, and seeding from a non-gitignored path means
# fresh clones always have a working baseline.)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_BASELINE_SOURCE_PATH = _PROJECT_ROOT / "src" / "strategy" / "baseline.py"


def _player(role: str, speed: int, skill: int, strength: int, save: int = 0) -> dict:
    """Compact player factory for the seed configs.

    `save` is GK-only (engine validator forces non-GK players to save=0).
    Other tactical attrs (discipline / dribbling / passing / shooting / stamina)
    fall to schema defaults — the user can edit later in the roster table.
    """
    p = {"role": role, "speed": speed, "skill": skill, "strength": strength}
    if save:
        p["save"] = save
    return p


def _seed_5v5_config() -> dict:
    """5v5 with 2-1-1 (1 GK + 2 DEF + 1 MID + 1 FWD = 5 players per team).

    Standard 5-a-side roster split. The GK counts as one of the 5 — formation
    notation excludes GK by convention, hence "2-1-1" not "1-2-1-1".
    """
    def team():
        return {"players": [
            _player("GK",  speed=8,  skill=10, strength=8,  save=16),
            _player("DEF", speed=12, skill=12, strength=14),
            _player("DEF", speed=12, skill=12, strength=14),
            _player("MID", speed=14, skill=14, strength=12),
            _player("FWD", speed=16, skill=14, strength=10),
        ]}
    return {
        "match": {
            "seed": 42,
            "tick_rate": 10,
            "duration_minutes": 5,
            "field_width": 60.0,   # smaller pitch for 5v5
            "field_height": 40.0,
        },
        # output is required by the engine's MatchConfig schema. The CLI
        # always overrides it via --log-dir at match-start, but load_config
        # validates the YAML BEFORE the override applies — so the file must
        # have a value here. Use ./logs as a stable placeholder.
        "output": {"log_dir": "./logs"},
        # simulation intentionally omitted — overlaid from global-defaults
        # at run time via --global-defaults.
        "team_a": team(),
        "team_b": team(),
    }


def _seed_11v11_config() -> dict:
    """11v11 with 4-4-2 (1 GK + 4 DEF + 4 MID + 2 FWD = 11 players per team).

    Classic FIFA full-side formation. Field uses standard pitch proportions.
    """
    def team():
        return {"players": [
            _player("GK",  speed=8,  skill=10, strength=8,  save=16),
            *[_player("DEF", speed=12, skill=12, strength=14) for _ in range(4)],
            *[_player("MID", speed=14, skill=14, strength=12) for _ in range(4)],
            *[_player("FWD", speed=16, skill=14, strength=10) for _ in range(2)],
        ]}
    return {
        "match": {
            "seed": 42,
            "tick_rate": 10,
            "duration_minutes": 5,
            "field_width": 100.0,
            "field_height": 60.0,
        },
        # output is required by the engine's MatchConfig schema (see _seed_5v5_config).
        "output": {"log_dir": "./logs"},
        "team_a": team(),
        "team_b": team(),
    }


def _seed_default_data(data_home: Path) -> None:
    """Write default match configs + baseline strategy to data_home if missing.

    Idempotent — existing files are NEVER overwritten so user edits survive
    a server restart. Tolerant of read-only filesystems and missing project
    sources (silently skips on OSError).

    Files created:
      <data_home>/configs/5v5.yaml   — 5v5 with 2-1-1 formation
      <data_home>/configs/11v11.yaml — 11v11 with 4-4-2 formation
      <data_home>/strategies/baseline.py — copy of src/strategy/baseline.py
    """
    seeds = [
        (data_home / "configs" / "5v5.yaml",   lambda: yaml.safe_dump(_seed_5v5_config(),   default_flow_style=False)),
        (data_home / "configs" / "11v11.yaml", lambda: yaml.safe_dump(_seed_11v11_config(), default_flow_style=False)),
    ]
    try:
        for path, builder in seeds:
            if path.exists():
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(builder())
            print(f"[seed] wrote {path}", flush=True)

        baseline_dst = data_home / "strategies" / "baseline.py"
        if not baseline_dst.exists() and _BASELINE_SOURCE_PATH.exists():
            baseline_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(_BASELINE_SOURCE_PATH, baseline_dst)
            print(f"[seed] wrote {baseline_dst}", flush=True)

        # Per ADR-0023, every library strategy gets a sidecar. Seed one for the
        # bundled baseline so a fresh data-dir doesn't show "unknown" provenance.
        baseline_meta = data_home / "strategies" / "baseline.meta.json"
        if baseline_dst.exists() and not baseline_meta.exists():
            now = _now_iso()
            baseline_meta.write_text(
                json.dumps(
                    {
                        "provider":         "baseline",
                        "model":            "hand-written",
                        "created_by":       "manual",
                        "created_at":       now,
                        "last_modified_at": now,
                    },
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )
            print(f"[seed] wrote {baseline_meta}", flush=True)
    except OSError as exc:
        # Read-only filesystem, permission denied, etc. — log and continue.
        # The server can still operate; the user just won't have the seeded
        # presets and will need to create configs manually.
        print(f"[seed] WARN: could not seed default data ({exc})", flush=True)


def create_app(log_dir: str = "./logs", seed_defaults: bool = True) -> FastAPI:
    """Create FastAPI application instance.

    Args:
        log_dir: Directory for match logs (stored in app.state.log_dir)

    Returns:
        Configured FastAPI application

    Raises:
        RuntimeError: If static/index.html not found
    """
    if not (_STATIC_DIR / "index.html").exists():
        raise RuntimeError(f"static/index.html not found at {_STATIC_DIR / 'index.html'}")

    @asynccontextmanager
    async def _lifespan(application: FastAPI):
        yield
        # Shutdown: terminate all tracked subprocesses so SSE streams unblock
        # and uvicorn can exit cleanly on the first Ctrl+C.
        for entry in list(getattr(application.state, "running_matches", {}).values()):
            proc = entry.get("popen") if isinstance(entry, dict) else entry
            if proc is not None:
                try:
                    proc.terminate()
                except OSError:
                    pass
        for entry in list(getattr(application.state, "running_series", {}).values()):
            proc = entry.get("popen") if isinstance(entry, dict) else entry
            if proc is not None:
                try:
                    proc.terminate()
                except OSError:
                    pass
        for entry in list(getattr(application.state, "running_cups", {}).values()):
            proc = entry.get("popen") if isinstance(entry, dict) else entry
            if proc is not None:
                try:
                    proc.terminate()
                except OSError:
                    pass
        for entry in list(getattr(application.state, "running_leagues", {}).values()):
            proc = entry.get("popen") if isinstance(entry, dict) else entry
            if proc is not None:
                try:
                    proc.terminate()
                except OSError:
                    pass

    app = FastAPI(title="agent_pitch HTTP Server", lifespan=_lifespan)
    app.state.log_dir = Path(log_dir)
    # Live-viewer endpoints look in <data_dir>/matches/ for completed match
    # dirs (events.jsonl + meta.json). Pre-resolve so endpoint handlers don't
    # repeat the path concat.
    app.state.matches_dir = app.state.log_dir / "matches"

    # Arena section data lives under <data_dir>/arena/. Each series gets its
    # own subdirectory: arena/series_<series_id>/series.json + events.jsonl.
    app.state.arena_dir = app.state.log_dir / "arena"

    # In-memory registry of subprocess Popen handles for active matches.
    # Keyed by match_id. POST /api/matches inserts on spawn; the new
    # GET /api/matches/<id>/status endpoint reads from here to answer
    # "is the engine still running, did it crash, or did it complete?".
    # Lost on server restart (best-effort); meta.json on disk is the
    # canonical "completed" signal regardless.
    app.state.running_matches = {}

    # In-memory registry of subprocess Popen handles for active series.
    # Keyed by series_id. POST /api/arena inserts on spawn.
    # Lost on server restart (best-effort); series.json on disk is the
    # canonical state signal regardless.
    app.state.running_series = {}

    # In-memory registry of subprocess Popen handles for active cups.
    # Keyed by cup_id. POST /api/cups inserts on spawn.
    # Lost on server restart (best-effort); cup.json on disk is the
    # canonical state signal regardless.
    app.state.running_cups = {}

    # Strategy Cup data lives under <data_dir>/cups/. Each cup gets its
    # own subdirectory: cups/cup_<cup_id>/cup.json + events.jsonl.
    app.state.cups_dir = app.state.log_dir / "cups"

    # In-memory registry of subprocess Popen handles for active leagues.
    # Keyed by league_id. POST /api/leagues inserts on spawn.
    # Lost on server restart (best-effort); league.json on disk is the
    # canonical state signal regardless.
    app.state.running_leagues = {}

    # Strategy League data lives under <data_dir>/leagues/. Each league gets
    # its own subdirectory: leagues/league_<league_id>/league.json + events.jsonl.
    app.state.leagues_dir = app.state.log_dir / "leagues"

    # Idempotently seed two default match configs (5v5 / 11v11) and the
    # baseline strategy on first run so a brand-new install has something
    # the user can immediately pick from the Match config + Strategies lists.
    # Existing files are never overwritten — safe to re-run on every start.
    # Tests pass seed_defaults=False so they don't pollute their tmp dirs
    # with files unrelated to what they're asserting.
    if seed_defaults:
        _seed_default_data(app.state.log_dir)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8765", "http://127.0.0.1:8765",
            "http://localhost:8000", "http://127.0.0.1:8000",  # legacy
        ],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    # Mount /static directory for browser frontend assets (Browser layer).
    # No-cache headers via middleware below — local-dev convenience: when
    # we ship a CSS/JS fix, the browser picks it up on next reload without
    # the user having to hard-refresh / clear cache. The viewer payload is
    # tiny so the cost of always-revalidate is negligible here.
    from fastapi.staticfiles import StaticFiles
    from starlette.middleware.base import BaseHTTPMiddleware

    class _NoCacheStatic(BaseHTTPMiddleware):
        """Force `Cache-Control: no-store` on every /static response.

        Browsers were silently serving stale cached app.css / app.js after
        bug fixes (a CSS overlap fix took 5+ rounds because the browser kept
        showing the pre-fix layout). Disabling cache means a normal reload
        always picks up the latest. Acceptable for local dev; for prod
        deployment we'd switch to versioned filenames + long-cache.
        """
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            if request.url.path.startswith("/static/") or request.url.path == "/":
                response.headers["Cache-Control"] = "no-store, max-age=0"
                # Strip validators so the browser can't 304 us back to a
                # cached copy. MutableHeaders supports `del` not `pop()`.
                if "etag" in response.headers:
                    del response.headers["etag"]
                if "last-modified" in response.headers:
                    del response.headers["last-modified"]
            return response
    app.add_middleware(_NoCacheStatic)
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @app.get("/")
    async def root():
        """Serve index.html from static directory."""
        return FileResponse(_STATIC_DIR / "index.html", media_type="text/html")

    @app.get("/api/health")
    async def health():
        """Health check endpoint - returns status, version, and timestamp."""
        import time
        import importlib.metadata

        try:
            version = importlib.metadata.version("agent-pitch")
        except importlib.metadata.PackageNotFoundError:
            version = "0.0.0.dev0"  # fallback when package is not installed

        return JSONResponse({
            "status": "ok",      # backward compat with test_ac_http_01
            "ok": True,
            "version": version,
            "timestamp": int(time.time())
        })

    @app.get("/api/match")
    async def get_match(match_id: Optional[str] = Query(None, pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Get match metadata. Optional `?match_id=<id>` selects a specific
        match; otherwise prefers the in-progress match, falling back to the
        latest completed one."""
        resolved = _resolve_match_dir(app.state.matches_dir, match_id)
        if resolved is None:
            # If a specific match_id was requested but the dir doesn't exist
            # yet, return 202 + "starting" stub. The engine subprocess is
            # likely still spinning up (CGP / file creation) — the viewer
            # should poll until events.jsonl appears.
            if match_id:
                return JSONResponse(
                    status_code=202,
                    content={"match_id": match_id,
                             "status": "starting",
                             "in_progress": True,
                             "total_ticks": 0,
                             "tick_rate": 10},
                )
            return JSONResponse(
                status_code=404,
                content={"error": "no_match_found",
                         "detail": f"No match found (id={match_id or 'latest'})"},
            )
        match_dir, meta = resolved
        if meta is None:
            # In-progress: synthesize minimal meta so the viewer can show name + load ticks
            return {"match_id": match_dir.name.removeprefix("match_"),
                    "in_progress": True,
                    "total_ticks": 0,
                    "tick_rate": 10}
        response = dict(meta)
        meta_path = match_dir / "meta.json"
        response["meta_file_mtime"] = os.path.getmtime(meta_path)
        response["data_dir"] = str(app.state.log_dir)
        return response

    @app.get("/api/match/ticks")
    async def get_ticks(
        match_id: Optional[str] = Query(None, pattern=r"^[A-Za-z0-9_-]{1,128}$"),
        offset: int = Query(0, ge=0),
        limit: int = Query(500, ge=1, le=10000),
    ):
        """Get paginated tick records from events.jsonl."""
        resolved = _resolve_match_dir(app.state.matches_dir, match_id)
        if resolved is None:
            return JSONResponse(status_code=404, content={"error": "no_match_found",
                                                          "detail": f"No match (id={match_id or 'latest'})"})
        match_dir, meta = resolved
        ticks = _read_events_jsonl(match_dir)
        total = (meta or {}).get("total_ticks", len(ticks))
        page = ticks[offset:offset + limit]
        return {"total_ticks": total, "offset": offset, "limit": limit, "ticks": page}

    @app.get("/api/match/key-events")
    async def get_key_events(match_id: Optional[str] = Query(None, pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Get full list of tick records where is_key_event==true."""
        resolved = _resolve_match_dir(app.state.matches_dir, match_id)
        if resolved is None:
            return JSONResponse(status_code=404, content={"error": "no_match_found",
                                                          "detail": f"No match (id={match_id or 'latest'})"})
        match_dir, _ = resolved
        ticks = _read_events_jsonl(match_dir)
        key_events = [t for t in ticks if t.get("is_key_event") is True]
        return {"total_key_events": len(key_events), "key_events": key_events}

    @app.get("/api/match/stats")
    async def get_match_stats(match_id: Optional[str] = Query(None, pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Compute and return post-match statistics for a completed match.

        Scans events.jsonl on-demand to produce per-team and per-player stats.
        Returns 404 if match not found, 409 if match is still in progress.
        """
        resolved = _resolve_match_dir(app.state.matches_dir, match_id)
        if resolved is None:
            return JSONResponse(
                status_code=404,
                content={"error": "no_match_found",
                         "detail": f"No match (id={match_id or 'latest'})"},
            )
        match_dir, meta = resolved
        if meta is None:
            return JSONResponse(
                status_code=409,
                content={"error": "match_in_progress",
                         "detail": "Stats only available after match completion"},
            )
        ticks = _read_events_jsonl(match_dir)
        stats = compute_match_stats(ticks, meta)
        return JSONResponse(stats)

    @app.get("/api/strategy/{team_id}")
    async def get_strategy(
        team_id: Literal["team_a", "team_b"],
        match_id: Optional[str] = Query(None, pattern=r"^[A-Za-z0-9_-]{1,128}$"),
    ):
        """Get strategy source code for a team in a specific match.

        Reads the per-match snapshot at <matches_dir>/match_<id>/strategy_<team>.py
        written by MatchLog.serialize(). When match_id is omitted, falls back
        to the most recent match (in-progress preferred, then latest completed)
        — same selection rule as the live-viewer endpoints.
        """
        resolved = _resolve_match_dir(app.state.matches_dir, match_id)
        if resolved is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "no_match_found",
                    "detail": f"No match (id={match_id or 'latest'})",
                },
            )
        match_dir, _meta = resolved
        # Try .py / .js / .rs — match could be Python, JavaScript, or Rust per team.
        strategy_path = None
        for ext in (".py", ".js", ".rs"):
            candidate = match_dir / f"strategy_{team_id}{ext}"
            if candidate.exists():
                strategy_path = candidate
                break
        if strategy_path is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "resource_not_found",
                    "detail": (
                        f"Strategy snapshot not found for {team_id} in "
                        f"{match_dir.name}/strategy_{team_id}.[py|js|rs]"
                    ),
                },
            )
        _EXT_TO_LANG = {".js": "javascript", ".rs": "rust", ".py": "python"}
        language = _EXT_TO_LANG.get(strategy_path.suffix, "python")
        return {"team_id": team_id, "source": strategy_path.read_text(), "language": language}

    @app.get("/api/match/ticks/stream")
    async def stream_ticks():
        """Stream all tick events via Server-Sent Events."""
        log_dir = app.state.log_dir
        selected = _select_match_for_streaming(app.state.matches_dir)
        if selected is None:
            return JSONResponse(status_code=404, content={"error": "no_match_data", "detail": "no events.jsonl found"})
        match_dir, in_progress = selected
        return StreamingResponse(_stream_ticks(match_dir, in_progress), media_type="text/event-stream")

    @app.get("/api/match/key-events/stream")
    async def stream_key_events():
        """Stream only key events via Server-Sent Events."""
        log_dir = app.state.log_dir
        selected = _select_match_for_streaming(app.state.matches_dir)
        if selected is None:
            return JSONResponse(status_code=404, content={"error": "no_match_data", "detail": "no events.jsonl found"})
        match_dir, in_progress = selected
        return StreamingResponse(_stream_ticks(match_dir, in_progress, key_events_only=True), media_type="text/event-stream")

    @app.get("/api/config")
    async def get_config():
        """Get combined configuration snapshot for all Config tabs."""
        log_dir = app.state.log_dir

        # Load storage settings to determine actual data_home
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        # Load Game tab values from global-defaults.yaml
        game_config = _load_game_config(data_home)

        # Compute subdirectory stats and disk usage
        subdirs = _compute_subdir_stats(data_home)
        disk_usage = _get_disk_usage(data_home)

        # Load LLM provider config and status
        llm_config = _load_llm_config(data_home)

        # Load match configs
        match_configs = _load_match_configs(data_home)

        return JSONResponse({
            "game": game_config.model_dump(),
            "llm": llm_config,
            "storage": {
                "data_home": str(data_home),
                "subdirs": subdirs,
                "free_bytes": disk_usage["free_bytes"]
            },
            "match": {
                "configs": match_configs
            }
        })

    @app.put("/api/config/game")
    async def put_config_game(payload: GameConfig):
        """Save Game tab configuration values."""
        log_dir = app.state.log_dir
        data_home = log_dir  # Use log_dir as DATA_HOME for now

        try:
            # Atomic write using temporary file + os.replace pattern
            config_path = data_home / "global-defaults.yaml"
            temp_path = data_home / "global-defaults.yaml.tmp"

            # Ensure data_home directory exists
            data_home.mkdir(parents=True, exist_ok=True)

            # Write to temporary file
            with open(temp_path, 'w') as f:
                yaml.safe_dump(payload.model_dump(), f, default_flow_style=False)

            # Atomic replace
            os.replace(temp_path, config_path)

            return JSONResponse({
                "updated_fields": list(payload.model_dump().keys()),
                "timestamp": time.time()
            })

        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            raise HTTPException(status_code=500, detail=f"File write error: {str(e)}")

    @app.put("/api/config/storage")
    async def put_config_storage(payload: StorageConfig):
        """Storage tab is read-only as of 2026-04-24.

        The data directory is fixed at server startup via
        `agent-pitch serve --data-dir <path>`. To change it, restart the server
        with a different flag value. The UI Storage tab displays the current
        value but does not allow editing.
        """
        raise HTTPException(
            status_code=405,
            detail=(
                "Storage data_home is read-only via the API. Restart the "
                "server with `agent-pitch serve --data-dir <path>` to change it."
            ),
        )

    @app.put("/api/config/llm")
    async def put_config_llm(payload: LLMConfigPayload):
        """Save LLM tab configuration values."""
        log_dir = app.state.log_dir

        # Load storage settings to determine actual data_home
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        try:
            # Separate provider configs (URL/model) from secrets (keys)
            provider_configs = {}
            secrets_updates = {}

            for provider_config in payload.providers:
                entry = {
                    "url": provider_config.url,
                    "model": provider_config.model
                }
                # Include type field for custom providers
                if provider_config.type:
                    entry["type"] = provider_config.type
                provider_configs[provider_config.name] = entry

                # Handle key updates
                if provider_config.key is not None:  # Explicit key provided
                    if provider_config.key == "":  # Empty string = clear
                        secrets_updates[provider_config.name] = None  # Will be removed
                    else:
                        secrets_updates[provider_config.name] = {"api_key": provider_config.key}
                # If key is None (omitted), preserve existing secret

            # Write provider configs to yaml file
            providers_path = data_home / "llm-providers.yaml"
            temp_providers_path = data_home / "llm-providers.yaml.tmp"

            data_home.mkdir(parents=True, exist_ok=True)

            with open(temp_providers_path, 'w') as f:
                yaml.safe_dump(provider_configs, f, default_flow_style=False)

            # Update secrets if any changes
            if secrets_updates:
                current_secrets = load_secrets(data_home)

                for provider, secret_data in secrets_updates.items():
                    if secret_data is None:
                        current_secrets.pop(provider, None)  # Remove
                    else:
                        current_secrets[provider] = secret_data  # Set/update

                save_secrets(data_home, current_secrets)

            # Atomic replace for provider config
            os.replace(temp_providers_path, providers_path)

            return JSONResponse({
                "providers_updated": list(provider_configs.keys()),
                "secrets_updated": list(secrets_updates.keys()),
                "timestamp": time.time()
            })

        except Exception as e:
            # Clean up temp files
            if temp_providers_path.exists():
                temp_providers_path.unlink(missing_ok=True)
            raise HTTPException(status_code=500, detail=f"Configuration write error: {str(e)}")

    @app.post("/api/config/llm/test")
    async def test_llm_connection(payload: TestConnectionRequest):
        """Test LLM provider connection."""
        log_dir = app.state.log_dir

        # Load storage settings to determine actual data_home
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        try:
            import time as test_time

            # Resolve the key to test:
            #   1. Explicit `key` in request body — lets the UI test an unsaved
            #      key the user just typed (ADR-0020 amendment 2026-04-25).
            #   2. Otherwise fall back to env var > secrets file.
            inline_key = (payload.key or "").strip()
            api_key = inline_key or get_api_key(data_home, payload.provider)
            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "no_key", "detail": f"No API key configured for {payload.provider}"}
                )

            start_time = test_time.time()

            # Use the provider's models-list endpoint as the connection test:
            # validates auth, costs zero tokens, decouples the test from any
            # specific model being available, and gives us the dropdown
            # content for the UI in the same round-trip.
            if payload.provider == "openai":
                models = await _list_openai_chat_models(api_key)
            elif payload.provider == "anthropic":
                models = await _list_anthropic_models(api_key)
            elif payload.provider == "gemini":
                models = await _list_gemini_models(api_key)
            elif payload.type == "openai_compatible":
                # Custom provider using OpenAI-compatible API
                if not payload.url:
                    raise HTTPException(
                        status_code=400,
                        detail="URL required for custom provider test"
                    )
                models = await _list_openai_chat_models(api_key, base_url=payload.url)
            else:
                raise HTTPException(status_code=422, detail=f"Unsupported provider: {payload.provider}")

            latency_ms = int((test_time.time() - start_time) * 1000)

            return JSONResponse({
                "ok": True,
                "latency_ms": latency_ms,
                "timestamp": test_time.time(),
                "models": models,
            })

        except HTTPException:
            raise  # Re-raise HTTP errors as-is
        except Exception as e:
            # Provider call failed - return 200 with ok: false per spec
            return JSONResponse({
                "ok": False,
                "error": str(e),
                "timestamp": test_time.time()
            })

    @app.get("/api/config/match")
    async def get_match_configs():
        """Get list of match configurations."""
        log_dir = app.state.log_dir

        # Load storage settings to determine actual data_home
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        match_configs = _load_match_configs(data_home)
        return JSONResponse(match_configs)

    @app.get("/api/config/match/{name}")
    async def get_match_config(name: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,64}$")):
        """Get single match configuration."""
        log_dir = app.state.log_dir

        # Load storage settings to determine actual data_home
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        config_path = data_home / "configs" / f"{name}.yaml"

        if not config_path.exists():
            raise HTTPException(status_code=404, detail=f"Match config '{name}' not found")

        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)

            if not data or not isinstance(data, dict):
                raise HTTPException(status_code=422, detail=f"Invalid YAML in config '{name}'")

            # Strip any deprecated llm_provider/llm_model fields before validation
            data = _strip_deprecated_llm_fields(data)

            # Validate against MatchConfigPayload schema
            validated = MatchConfigPayload(**data)
            return JSONResponse(validated.model_dump())

        except yaml.YAMLError as e:
            raise HTTPException(status_code=422, detail=f"YAML parse error: {str(e)}")
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=f"Schema validation error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File read error: {str(e)}")

    @app.put("/api/config/match/{name}")
    async def put_match_config(name: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,64}$"), payload: MatchConfigPayload = ...):
        """Write/update match configuration."""
        log_dir = app.state.log_dir

        # Load storage settings to determine actual data_home
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        configs_dir = data_home / "configs"
        config_path = configs_dir / f"{name}.yaml"
        temp_path = configs_dir / f"{name}.yaml.tmp"

        # Check if this is a new file
        is_new = not config_path.exists()

        try:
            # Ensure configs directory exists
            configs_dir.mkdir(parents=True, exist_ok=True)

            # Write to temporary file. exclude_none drops `simulation` when
            # the UI omits it — saved match YAMLs no longer carry simulation
            # values; they're always merged in from the global Game tab at
            # match-start time.
            data = payload.model_dump(exclude_none=True)
            # Auto-fill `output` if UI omitted it. The engine's MatchConfig
            # requires output (load_config fails fast if missing), but the UI
            # never edits it because the API always passes --log-dir at
            # match-start. Use a deterministic placeholder so the saved YAML
            # remains loadable by direct CLI users too.
            if "output" not in data:
                data["output"] = {"log_dir": str(data_home / "matches")}
            with open(temp_path, 'w') as f:
                yaml.safe_dump(data, f, default_flow_style=False)

            # Atomic replace
            os.replace(temp_path, config_path)

            # Get modification time
            mtime = config_path.stat().st_mtime
            modified_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(mtime))

            return JSONResponse({
                "name": name,
                "modified_iso": modified_iso,
                "created": is_new
            })

        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            raise HTTPException(status_code=500, detail=f"File write error: {str(e)}")

    @app.delete("/api/config/match/{name}")
    async def delete_match_config(name: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,64}$")):
        """Remove match configuration."""
        log_dir = app.state.log_dir

        # Load storage settings to determine actual data_home
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        config_path = data_home / "configs" / f"{name}.yaml"

        # Idempotent delete - no error if file doesn't exist
        try:
            if config_path.exists():
                config_path.unlink()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File deletion error: {str(e)}")

        return Response(status_code=204)

    @app.get("/api/config/teams")
    async def list_teams():
        """List all team configs as {slug: TeamConfigPayload-shaped dict}."""
        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])
        teams_dir = data_home / "configs" / "teams"

        out: dict = {}
        if not teams_dir.exists():
            return JSONResponse({"teams": out})

        for path in sorted(teams_dir.glob("*.yaml")):
            slug = path.stem
            try:
                with open(path, "r") as f:
                    data = yaml.safe_load(f) or {}
                out[slug] = data
            except Exception:
                # Tolerate malformed team files — skip them in the list
                continue
        return JSONResponse({"teams": out})

    @app.get("/api/config/teams/{slug}")
    async def get_team(slug: str = PathParam(..., pattern=r"^[a-z0-9_-]+$")):
        """Get a single team config by slug."""
        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        path = data_home / "configs" / "teams" / f"{slug}.yaml"
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"team {slug} not found")

        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}
            return JSONResponse(data)
        except yaml.YAMLError as e:
            raise HTTPException(status_code=422, detail=f"YAML parse error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File read error: {str(e)}")

    @app.put("/api/config/teams/{slug}")
    async def put_team(
        slug: str = PathParam(..., pattern=r"^[a-z0-9_-]+$"),
        payload: TeamConfigPayload = ...,
    ):
        """Create or update a team config."""
        if payload.team_id != slug:
            raise HTTPException(status_code=400, detail="team_id must match URL slug")

        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        teams_dir = data_home / "configs" / "teams"
        teams_dir.mkdir(parents=True, exist_ok=True)
        config_path = teams_dir / f"{slug}.yaml"
        temp_path = teams_dir / f"{slug}.yaml.tmp"

        is_new = not config_path.exists()
        try:
            data = payload.model_dump(exclude_none=True)
            with open(temp_path, "w") as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
            os.replace(temp_path, config_path)
            mtime = config_path.stat().st_mtime
            modified_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime))
            return JSONResponse({"slug": slug, "modified_iso": modified_iso, "created": is_new})
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            raise HTTPException(status_code=500, detail=f"File write error: {str(e)}")

    @app.delete("/api/config/teams/{slug}")
    async def delete_team(slug: str = PathParam(..., pattern=r"^[a-z0-9_-]+$")):
        """Delete a team config. Refuses if any match config references this slug."""
        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        teams_dir = data_home / "configs" / "teams"
        config_path = teams_dir / f"{slug}.yaml"
        if not config_path.exists():
            raise HTTPException(status_code=404, detail=f"team {slug} not found")

        # Refuse delete if any match config references this slug
        configs_dir = data_home / "configs"
        for match_path in configs_dir.glob("*.yaml"):
            try:
                with open(match_path, "r") as f:
                    match_data = yaml.safe_load(f) or {}
            except Exception:
                continue
            if match_data.get("team_a") == slug or match_data.get("team_b") == slug:
                raise HTTPException(
                    status_code=409,
                    detail=f"team {slug} is referenced by match config {match_path.stem}",
                )

        try:
            config_path.unlink()
            return JSONResponse({"slug": slug, "deleted": True})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File delete error: {str(e)}")

    @app.get("/api/matches")
    async def get_matches():
        """Get list of past matches with metadata, sorted by date descending."""
        log_dir = app.state.log_dir

        # Load storage settings to determine actual data_home
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        matches_dir = data_home / "matches"
        if not matches_dir.exists():
            return JSONResponse([])

        matches = []
        try:
            for match_dir in matches_dir.iterdir():
                if not match_dir.is_dir():
                    continue

                meta_path = match_dir / "meta.json"
                # Skip in-progress matches (events.jsonl present, meta.json absent)
                if not meta_path.exists():
                    continue

                try:
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)

                    # Extract required fields with fallbacks
                    match_id = meta.get("match_id", match_dir.name)
                    final_score = meta.get("final_score", {"team_a": 0, "team_b": 0})

                    # Calculate duration from tick count and estimated tick rate
                    tick_count = meta.get("tick_count", meta.get("final_tick", 0))
                    tick_rate = 10  # Default tick rate from app.js
                    duration_sec = max(0, tick_count // tick_rate)

                    # Get modification time for sorting
                    mtime = meta_path.stat().st_mtime
                    date_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(mtime))

                    # Extract team models and strategies (best effort)
                    teams = meta.get("teams", {})
                    team_a_count = len(teams.get("team_a", []))
                    team_b_count = len(teams.get("team_b", []))

                    # Prefer meta.seed (engine writes it as of 2026-04-24).
                    # Legacy matches without it fall back to extracting from
                    # the match_id (only works when id contains "seedN").
                    if isinstance(meta.get("seed"), int):
                        seed = meta["seed"]
                    else:
                        seed_match = re.search(r'seed(\d+)', match_id)
                        seed = int(seed_match.group(1)) if seed_match else 0

                    # Default config name from match_id or fallback
                    config_name = match_id.split('_seed')[0] if '_seed' in match_id else match_id

                    # `strategies` was added 2026-04-25 — older meta.json
                    # files lack it. Fall back to "unknown" so legacy matches
                    # stay listed (instead of disappearing from the UI).
                    strats_meta = meta.get("strategies", {}) or {}
                    def _team_strat_field(team_id: str, field: str) -> str:
                        team = strats_meta.get(team_id) or {}
                        return team.get(field, "unknown")

                    match_data = {
                        "match_id": match_id,
                        "final_score": final_score,
                        "date_iso": date_iso,
                        "config_name": config_name,
                        "seed": seed,
                        "duration_sec": duration_sec,
                        # `models` here is provider/model display: e.g.
                        # "openai/gpt-4o", "anthropic/claude-sonnet-4-6",
                        # or "baseline" (for the seeded baseline.py).
                        # Per ADR-0023, library-strategy provenance comes
                        # from the sidecar via _load_team_baseline.
                        "models": {
                            "team_a": _format_model(_team_strat_field("team_a", "provider"),
                                                   _team_strat_field("team_a", "model")),
                            "team_b": _format_model(_team_strat_field("team_b", "provider"),
                                                   _team_strat_field("team_b", "model")),
                        },
                        # `strategies` here is the strategy NAME (e.g.
                        # "baseline" or the LLM model name for generated
                        # strategies — see _parse_strategy_header).
                        "strategies": {
                            "team_a": _team_strat_field("team_a", "name"),
                            "team_b": _team_strat_field("team_b", "name"),
                        },
                    }

                    matches.append((mtime, match_data))

                except (json.JSONDecodeError, KeyError, OSError) as e:
                    # Skip malformed meta.json files
                    continue

        except (OSError, PermissionError):
            # Can't read matches directory
            return JSONResponse([])

        # Sort by mtime descending, extract match data
        matches.sort(key=lambda x: x[0], reverse=True)
        return JSONResponse([match[1] for match in matches])

    @app.get("/api/matches/{match_id}/status")
    async def get_match_status(match_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Report the runtime state of a match's engine subprocess.

        Answers "is the engine still running, did it crash, did it finish?"
        — gives the UI something better than guessing from "events.jsonl
        exists yet" timeouts.

        State machine:
          completed — meta.json exists; engine wrote final results.
          running   — Popen tracked AND poll() is None (process alive).
          exited    — Popen tracked AND poll() returned exit code AND no
                      meta.json on disk (subprocess died without finishing).
          unknown   — no Popen tracked AND no meta.json. Either the server
                      restarted (lost in-memory tracking) or the match_id
                      was never started by this server.

        Progress: when events.jsonl exists but meta.json doesn't yet, returns
        the latest tick from the tail of events.jsonl + the total expected
        from the saved match config so the UI can render "tick 1234 / 3000".
        """
        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        # Construct directly — _resolve_match_dir returns None when the dir
        # doesn't exist yet, but for status polling we need stable paths to
        # check (the dir may appear at any moment as the engine starts up).
        match_dir = data_home / "matches" / f"match_{match_id}"
        meta_path = match_dir / "meta.json"
        events_path = match_dir / "events.jsonl"
        entry = app.state.running_matches.get(match_id)

        # Compute progress (current_tick / total_ticks / elapsed) if we can.
        progress = None
        if events_path.exists():
            current_tick = _tail_last_tick(events_path)
            total_ticks = (entry or {}).get("total_ticks", 0)
            elapsed_sec = int(time.time() - entry["started_at"]) if entry else None
            progress = {
                "current_tick": current_tick,
                "total_ticks": total_ticks,
                "percent": (round(100 * current_tick / total_ticks) if total_ticks > 0 else 0),
                "elapsed_sec": elapsed_sec,
            }

        # Decide state — meta.json wins (canonical "done" signal).
        if meta_path.exists():
            state = "completed"
            # Only drop the registry slot once the subprocess has ACTUALLY
            # exited. The engine writes meta.json before PMEP (post-match
            # evolution) finishes, and PMEP can run for several minutes.
            # If we reap on meta.json existence alone, we lose the true
            # exit code and subsequent polls report state="unknown" — which
            # makes failed-PMEP debugging impossible.
            if entry:
                rc = entry["popen"].poll()
                exit_code = rc                              # may still be None (PMEP running)
                if rc is not None:
                    # Process actually exited — safe to free the registry
                    # slot. wait() with a tiny timeout is just to reap any
                    # remaining zombie state without blocking.
                    try:
                        entry["popen"].wait(timeout=0.1)
                    except Exception:
                        pass
                    app.state.running_matches.pop(match_id, None)
            else:
                exit_code = None
        elif entry is None:
            state = "unknown"
            exit_code = None
        else:
            rc = entry["popen"].poll()
            if rc is None:
                state = "running"
                exit_code = None
            else:
                state = "exited"
                exit_code = rc
                # Subprocess died without writing meta.json — drop from
                # registry so a re-spawn with the same id can re-track.
                app.state.running_matches.pop(match_id, None)

        # Top-level elapsed_sec — available the moment the process is tracked,
        # not only after events.jsonl exists. Lets the UI show a live wait
        # timer during the pre-events.jsonl warm-up window (engine init,
        # CGP, etc.), instead of an empty "elapsed " string.
        elapsed_sec = int(time.time() - entry["started_at"]) if entry else None

        return JSONResponse({
            "match_id": match_id,
            "state": state,
            "pid": (entry or {}).get("pid") if entry else None,
            "started_at": (entry or {}).get("started_at") if entry else None,
            "elapsed_sec": elapsed_sec,
            "exit_code": exit_code,
            "progress": progress,
            "completed": state == "completed",
        })

    @app.delete("/api/matches/{match_id}")
    async def delete_match(match_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Delete a match and its log directory."""
        log_dir = app.state.log_dir

        # Load storage settings to determine actual data_home
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        # Match dirs are stored as `matches/match_<id>/` (engine-side convention).
        # The match_id passed in by the UI is the bare id (no `match_` prefix).
        match_dir = data_home / "matches" / f"match_{match_id}"

        if not match_dir.exists():
            raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found")

        if not match_dir.is_dir():
            raise HTTPException(status_code=400, detail=f"'{match_id}' is not a valid match directory")

        try:
            shutil.rmtree(match_dir)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete match: {str(e)}")

        return Response(status_code=204)

    @app.get("/api/strategies")
    async def get_strategies():
        """List library strategies with sidecar metadata (ADR-0023).

        Each entry includes the basic file stats plus a `meta` object carrying
        provider/model/created_by/timestamps. Legacy files without a sidecar
        return `meta: {provider: "unknown", ...}`.

        Sorted by modification time descending so the freshest strategies
        surface first in the UI.
        """
        log_dir = app.state.log_dir

        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        try:
            entries = lib_list_strategies(data_home)
        except OSError:
            return JSONResponse([])

        strategies = []
        for name, meta in entries:
            try:
                strategy_file = lib_source_path(data_home, name, language=meta.language)
                stat = strategy_file.stat()
                size_bytes = stat.st_size
                mtime = stat.st_mtime
                modified_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(mtime))
                try:
                    with open(strategy_file, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for _ in f)
                except (UnicodeDecodeError, OSError):
                    line_count = 0
            except (OSError, PermissionError, InvalidStrategyNameError):
                continue

            strategies.append({
                "name":         name,
                "size_bytes":   size_bytes,
                "line_count":   line_count,
                "modified_iso": modified_iso,
                "language":     meta.language,
                "meta":         _meta_to_dict(meta),
                "_mtime":       mtime,  # internal sort key
            })

        strategies.sort(key=lambda x: x["_mtime"], reverse=True)
        for s in strategies:
            s.pop("_mtime", None)
        return JSONResponse(strategies)

    @app.get("/api/strategies/llm-template")
    async def get_llm_template(mode: str = "generation"):
        """Return the raw Jinja2 prompt template for inspection in the UI.

        Lets researchers see what schema/sandbox/zone context the LLM
        receives when generating a strategy. The user-typed prompt in the
        New Strategy LLM mode is supplemental to this template.

        ADR-0006 (API ↛ simulation): the path is resolved from ``__file__``
        rather than imported from ``src.foundation.system_prompt_builder``,
        because the API process must not load simulation modules. The file
        layout (``src/foundation/system_prompt_builder/prompt_files/``) is
        the contract; if SPB ever moves the templates, update this map.

        NOTE: must be declared BEFORE /api/strategies/{name} — FastAPI
        matches in declaration order and "llm-template" satisfies the
        {name} regex.
        """
        # Per-mode filename map mirrors SPB's _TEMPLATE_FILES (kept in sync
        # by file layout, not by import — see ADR-0006 note above).
        template_filenames = {
            "generation":      "generation.jinja2",
            "generation-js":   "generation-js.jinja2",
            "generation-rust": "generation-rust.jinja2",
            "evolution":       "evolution.jinja2",
        }
        filename = template_filenames.get(mode)
        if filename is None:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown mode '{mode}'. Use 'generation', 'generation-js', 'generation-rust', or 'evolution'.",
            )

        # src/api/http_server/app.py → up 2 levels = src/ → into foundation/...
        prompt_dir = Path(__file__).resolve().parents[2] / "foundation" / "system_prompt_builder" / "prompt_files"
        path = prompt_dir / filename
        if not path.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Template missing on disk: {path}",
            )

        try:
            content = path.read_text(encoding="utf-8")
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Cannot read template: {e}")

        # {# version: X #} extraction — same regex SPB's loader uses.
        version_match = re.search(r"\{#\s*version:\s*(\S+)\s*#\}", content)
        version = version_match.group(1) if version_match else "unknown"

        return JSONResponse({
            "mode": mode,
            "filename": path.name,
            "version": version,
            "content": content,
            "size_bytes": len(content.encode("utf-8")),
        })

    @app.get("/api/strategies/{name}")
    async def get_strategy_source(name: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,64}$")):
        """Get the full source for a single strategy plus sidecar metadata."""
        log_dir = app.state.log_dir

        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        try:
            source_content, meta = lib_read_strategy(data_home, name)
        except InvalidStrategyNameError as e:
            print(f"[strategies] GET {name!r}: 400 invalid name — {e}", file=sys.stderr, flush=True)
            raise HTTPException(status_code=400, detail="Invalid strategy name format")
        except StrategyLibraryNotFoundError:
            print(f"[strategies] GET {name!r}: 404 not found", file=sys.stderr, flush=True)
            raise HTTPException(status_code=404, detail=f"Strategy '{name}' not found")
        except StrategyLibraryError as e:
            print(f"[strategies] GET {name!r}: 500 read error — {e}", file=sys.stderr, flush=True)
            raise HTTPException(status_code=500, detail=str(e))

        try:
            stat = lib_source_path(data_home, name, language=meta.language).stat()
            size_bytes = stat.st_size
            modified_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(stat.st_mtime))
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Failed to stat strategy file: {e}")

        line_count = len(source_content.splitlines())

        return JSONResponse({
            "name":         name,
            "source":       source_content,
            "size_bytes":   size_bytes,
            "line_count":   line_count,
            "modified_iso": modified_iso,
            "language":     meta.language,
            "meta":         _meta_to_dict(meta),
        })

    @app.delete("/api/strategies/{name}")
    async def delete_strategy(name: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,64}$")):
        """Delete a strategy: removes both `<name>.py` and `<name>.meta.json`."""
        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        try:
            lib_delete_strategy(data_home, name)
        except InvalidStrategyNameError as e:
            print(f"[strategies] DELETE {name!r}: 400 invalid name — {e}", file=sys.stderr, flush=True)
            raise HTTPException(status_code=400, detail="Invalid strategy name format")
        except StrategyLibraryNotFoundError:
            print(f"[strategies] DELETE {name!r}: 404 not found", file=sys.stderr, flush=True)
            raise HTTPException(status_code=404, detail=f"Strategy '{name}' not found")
        except StrategyLibraryError as e:
            print(f"[strategies] DELETE {name!r}: 500 delete error — {e}", file=sys.stderr, flush=True)
            raise HTTPException(status_code=500, detail=f"Failed to delete strategy: {e}")

        return Response(status_code=204)

    @app.post("/api/strategies")
    async def create_strategy(payload: StrategyCreatePayload):
        """Create a new strategy with paired sidecar (ADR-0023).

        Writes `<name>.py` and `<name>.meta.json` atomically. When `meta` is
        omitted, defaults to a manual entry (provider="manual",
        model="hand-written"). Server stamps `created_at` and
        `last_modified_at`.
        """
        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        language = payload.language

        # 409 Conflict if either side of the pair already exists.
        try:
            existing_src = lib_source_path(data_home, payload.name, language=language)
        except InvalidStrategyNameError as e:
            print(f"[strategies] POST {payload.name!r}: 400 invalid name — {e}", file=sys.stderr, flush=True)
            raise HTTPException(status_code=400, detail="Invalid strategy name format")
        if existing_src.exists():
            print(f"[strategies] POST {payload.name!r}: 409 already exists", file=sys.stderr, flush=True)
            raise HTTPException(status_code=409, detail=f"Strategy '{payload.name}' already exists")

        # Default blank-template body when source omitted (preserves existing behavior).
        if payload.source is not None:
            source_content = payload.source
        elif language == "javascript":
            source_content = f'// Strategy: {payload.name}\n\nfunction decide(game_state, player_state, history) {{\n    // Return one of: {{type:"Hold"}}, {{type:"Move",dx,dy,speed}}, {{type:"Pass",target_pos,power}}, {{type:"Shoot",angle,power}}, {{type:"Tackle",target_player_id}}\n    return {{type: "Hold"}};\n}}'
        elif language == "rust":
            # Rust skeleton: full lib.rs since the user/LLM authors the
            # whole crate (boilerplate + decide_logic). Pulled from the
            # cargo template so this stays in sync with what compiles.
            from pathlib import Path as _Path
            _tpl = (
                _Path(__file__).resolve().parents[2]
                / "foundation" / "sandbox" / "cargo_template" / "src" / "lib.rs.in"
            )
            source_content = (
                f"// Strategy: {payload.name}\n" + _tpl.read_text(encoding="utf-8")
            )
        else:
            source_content = f'\"\"\"Strategy: {payload.name}\"\"\"\n\ndef decide(game_state, player_state, history):\n    \"\"\"Return one of: Hold(), Move(direction), Pass(target_id), Shoot(), Tackle(target_id).\"\"\"\n    return Hold()\n'

        # Build the sidecar from payload.meta (or manual defaults).
        now = _now_iso()
        size_bytes = len(source_content.encode("utf-8"))
        if payload.meta is not None:
            meta = StrategyLibraryMeta(
                provider=payload.meta.provider,
                model=payload.meta.model,
                created_by=payload.meta.created_by,
                created_at=now,
                last_modified_at=now,
                prompt=payload.meta.prompt,
                template_version=payload.meta.template_version,
                language=language,
                generation_latency_ms=payload.meta.generation_latency_ms,
                generation_input_tokens=payload.meta.generation_input_tokens,
                generation_output_tokens=payload.meta.generation_output_tokens,
                strategy_size_bytes=size_bytes,
            )
        else:
            meta = StrategyLibraryMeta(
                provider="manual",
                model="hand-written",
                created_by="manual",
                created_at=now,
                last_modified_at=now,
                language=language,
                strategy_size_bytes=size_bytes,
            )

        try:
            written_meta = lib_write_strategy(data_home, payload.name, source_content, meta)
        except StrategyLibraryError as e:
            # Print the full meta the client sent so the failure can be traced
            # without re-running the request. Most common cause: LLM-marked
            # strategy posted with empty `prompt` or missing `template_version`.
            print(
                f"[strategies] POST {payload.name!r}: 400 sidecar validation — {e}\n"
                f"  meta provider={meta.provider!r} model={meta.model!r} "
                f"created_by={meta.created_by!r} "
                f"prompt_len={len(meta.prompt or '')} "
                f"template_version={meta.template_version!r}",
                file=sys.stderr, flush=True,
            )
            raise HTTPException(status_code=400, detail=str(e))

        try:
            stat = lib_source_path(data_home, payload.name, language=language).stat()
            size_bytes = stat.st_size
            modified_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(stat.st_mtime))
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Failed to stat strategy file: {e}")

        line_count = len(source_content.splitlines())

        return JSONResponse(
            status_code=201,
            content={
                "name":         payload.name,
                "modified_iso": modified_iso,
                "size_bytes":   size_bytes,
                "line_count":   line_count,
                "language":     language,
                "meta":         _meta_to_dict(written_meta),
            },
        )

    @app.post("/api/strategies/generate")
    async def generate_strategy(payload: StrategyGeneratePayload):
        """Generate a strategy via the `agent-pitch generate-strategy` subprocess.

        ADR-0006 boundary: HTTP server cannot import simulation modules
        (SPB / sandbox / providers all live in src/foundation). The CLI
        subcommand encapsulates that pipeline; we spawn it, wait for the
        single-line JSON stdout, and forward the code to the caller.

        The subprocess does NOT save — the user picks a final name in the
        post-generate UI panel and saves via POST /api/strategies. This
        endpoint just produces validated code.
        """
        import asyncio as _asyncio

        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        if not payload.provider or not payload.model:
            raise HTTPException(
                status_code=400,
                detail="provider and model are required for LLM generation",
            )

        # Spawn the CLI subprocess. Inherits env so OPENAI_API_KEY /
        # ANTHROPIC_API_KEY propagate; CLI also reads <data-dir>/.secrets.json
        # as a fallback (mirrors ADR-0020 precedence).
        cmd = [
            sys.executable, "-m", "src.cli", "generate-strategy",
            "--prompt", payload.prompt,
            "--provider", payload.provider,
            "--model", payload.model,
            "--data-dir", str(data_home),
        ]
        if payload.language != "python":
            cmd.extend(["--language", payload.language])
        # Pass provider type and base_url for custom providers (ollama, vllm, etc.)
        if payload.provider_type:
            cmd.extend(["--provider-type", payload.provider_type])
        if payload.base_url:
            cmd.extend(["--base-url", payload.base_url])

        try:
            proc = await _asyncio.create_subprocess_exec(
                *cmd,
                stdout=_asyncio.subprocess.PIPE,
                stderr=_asyncio.subprocess.PIPE,
            )
            try:
                # Subprocess does up to 2 attempts × 180s LLM timeout = 360s
                # of LLM time, plus extraction/sandbox overhead. 400s gives a
                # ~40s buffer. Reasoning models (gpt-5.x, o1, o3) account for
                # most of the budget; older chat models return in seconds.
                stdout_b, stderr_b = await _asyncio.wait_for(proc.communicate(), timeout=400.0)
            except _asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                raise HTTPException(
                    status_code=504,
                    detail="LLM generation timed out (>400s — reasoning models can be slow; try a faster model like gpt-4o)",
                )
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"agent-pitch CLI not found: {exc}",
            )

        stdout_text = stdout_b.decode("utf-8", errors="replace").strip()
        # CLI emits exactly one JSON line on stdout. Last line is canonical;
        # earlier lines (if any — e.g. logs leaking past stderr redirect) are noise.
        json_line = stdout_text.splitlines()[-1] if stdout_text else ""
        try:
            result = json.loads(json_line)
        except json.JSONDecodeError:
            stderr_text = stderr_b.decode("utf-8", errors="replace")
            raise HTTPException(
                status_code=500,
                detail=f"Subprocess produced no valid JSON. stderr: {stderr_text[:500]}",
            )

        if not result.get("ok"):
            stderr_text = stderr_b.decode("utf-8", errors="replace").strip()
            # Tail of stderr (last 4 lines) often carries the diagnostic context
            # that explains the failure — e.g. which secrets path was checked.
            tail = "\n".join(stderr_text.splitlines()[-4:]) if stderr_text else ""
            return JSONResponse(
                status_code=502,
                content={
                    "ok": False,
                    "error": result.get("error", "Unknown generation error"),
                    "diagnostic": tail,
                },
            )

        # Return provider/model so the frontend can echo them into the
        # subsequent POST /api/strategies and produce a truthful sidecar.
        return JSONResponse({
            "ok":               True,
            "code":             result["code"],
            "template_version": result.get("template_version"),
            "provider":         payload.provider,
            "model":            payload.model,
            "prompt":           payload.prompt,
            "latency_ms":       result.get("latency_ms"),
            "input_tokens":     result.get("input_tokens"),
            "output_tokens":    result.get("output_tokens"),
        })

    @app.put("/api/strategies/{name}")
    async def put_strategy(name: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,64}$"), payload: StrategyPayload = ...):
        """Create or update a strategy.

        For an existing strategy: preserves the sidecar's
        provider/model/created_by/created_at/prompt/template_version and
        only bumps `last_modified_at` (per ADR-0023 — `created_by` does not
        flip from `llm` to `edited` on PUT).

        For a new strategy: creates a manual sidecar with default fields.
        Legacy files (no sidecar) are upgraded to a synthesized
        `unknown`-provider sidecar on first PUT.
        """
        if not payload.source:
            print(f"[strategies] PUT {name!r}: 422 missing source field", file=sys.stderr, flush=True)
            raise HTTPException(status_code=422, detail="Missing source field")

        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        try:
            existing_meta = lib_read_meta(data_home, name)
        except (InvalidStrategyNameError, StrategyLibraryError):
            existing_meta = UNKNOWN_META

        try:
            src_path = lib_source_path(data_home, name, language=existing_meta.language)
        except InvalidStrategyNameError as e:
            print(f"[strategies] PUT {name!r}: 400 invalid name — {e}", file=sys.stderr, flush=True)
            raise HTTPException(status_code=400, detail="Invalid strategy name format")

        existed = src_path.exists()
        now = _now_iso()

        if not existed:
            # PUT-as-create: manual sidecar with defaults.
            new_meta = StrategyLibraryMeta(
                provider="manual",
                model="hand-written",
                created_by="manual",
                created_at=now,
                last_modified_at=now,
                language=existing_meta.language,
            )
            try:
                written = lib_write_strategy(data_home, name, payload.source, new_meta)
            except StrategyLibraryError as e:
                print(f"[strategies] PUT {name!r}: 500 write error — {e}", file=sys.stderr, flush=True)
                raise HTTPException(status_code=500, detail=f"Failed to write strategy file: {e}")
        else:
            # Existing strategy: write the new source first (atomic), then
            # update the sidecar to bump last_modified_at while preserving
            # everything else. update_meta() synthesizes a sidecar for legacy
            # files that don't have one yet.
            try:
                lib_update_source(data_home, name, payload.source)
                written = lib_update_meta(data_home, name, last_modified_at=now)
            except StrategyLibraryError as e:
                print(f"[strategies] PUT {name!r}: 500 write error — {e}", file=sys.stderr, flush=True)
                raise HTTPException(status_code=500, detail=f"Failed to write strategy file: {e}")

        try:
            stat = src_path.stat()
            size_bytes = stat.st_size
            modified_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(stat.st_mtime))
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Failed to stat strategy file: {e}")

        line_count = len(payload.source.splitlines())

        return JSONResponse({
            "name":         name,
            "modified_iso": modified_iso,
            "size_bytes":   size_bytes,
            "line_count":   line_count,
            "meta":         _meta_to_dict(written),
        })

    # ─────────────────────────────────────────────────────────────────
    # Arena endpoints — series lifecycle (GET/POST/DELETE /api/arena)
    # ─────────────────────────────────────────────────────────────────

    def _timestamp_compact() -> str:
        """UTC timestamp for series IDs, e.g. '20260423-1432'."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")

    async def _stream_series_events(series_d: Path, series_id: str):
        """Generator yielding SSE-formatted bytes for a series events.jsonl.

        Tails <series_d>/events.jsonl for lifecycle events. Each line must be a
        JSON object with 'event' and 'data' fields. Streams existing lines first
        (catch-up mode), then polls for new lines. Times out after 30 minutes.

        Subprocess exit detection: if the series subprocess has exited with a
        non-zero return code and series.json still says 'running', this generator
        marks series.json as 'errored' so the UI gets immediate feedback rather
        than waiting for the 30-minute timeout.
        """
        events_path = series_d / "events.jsonl"

        pos = 0
        buffer = b""
        started = asyncio.get_running_loop().time()
        SERIES_SSE_TIMEOUT_S = 1800  # 30 minutes

        while True:
            if events_path.exists():
                with open(events_path, "rb") as f:
                    f.seek(pos)
                    new_bytes = f.read()
                    pos = f.tell()
                buffer += new_bytes
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str:
                        continue
                    # Each events.jsonl line is {"event": "<name>", "data": {...}}.
                    # Emit as a named SSE event so JS addEventListener() fires.
                    try:
                        parsed = json.loads(line_str)
                        evt_name = parsed.get("event", "message")
                        evt_data = json.dumps(parsed.get("data", {}))
                        yield f"event: {evt_name}\ndata: {evt_data}\n\n".encode("utf-8")
                    except (json.JSONDecodeError, AttributeError):
                        yield f"data: {line_str}\n\n".encode("utf-8")

            # Check if series is finished (status != "running")
            try:
                series_data = _read_series_json(series_d)
                status = series_data.get("status", "running")
                if status != "running":
                    completed_text = json.dumps(series_data)
                    sse_event = "series-errored" if status == "errored" else "series-completed"
                    yield f"event: {sse_event}\ndata: {completed_text}\n\n".encode("utf-8")
                    return
            except (FileNotFoundError, json.JSONDecodeError):
                series_data = None

            # Detect subprocess death: if the process exited non-zero and the
            # series is still "running", mark it errored immediately.
            if series_data is None or series_data.get("status") == "running":
                entry = app.state.running_series.get(series_id)
                if entry is not None:
                    rc = entry["popen"].poll()
                    if rc is not None and rc != 0:
                        try:
                            current = _read_series_json(series_d)
                        except (FileNotFoundError, json.JSONDecodeError):
                            current = {}
                        if current.get("status") == "running":
                            import datetime as _dt
                            current["status"] = "errored"
                            current["completed_iso"] = _dt.datetime.now(
                                _dt.timezone.utc).isoformat()
                            _write_series_json(series_d, current)
                        app.state.running_series.pop(series_id, None)
                        errored_text = json.dumps(current)
                        yield f"event: series-errored\ndata: {errored_text}\n\n".encode("utf-8")
                        return

            if asyncio.get_running_loop().time() - started > SERIES_SSE_TIMEOUT_S:
                yield b'event: error\ndata: {"error": "stream_timeout"}\n\n'
                return

            await asyncio.sleep(SSE_POLL_MS / 1000)

    @app.get("/api/arena")
    async def list_arena_series():
        """List all Arena series, sorted by started_iso descending.

        Returns a summary list — each item contains:
        series_id, format, status, config_name, started_iso, completed_iso, score.
        Returns an empty list when no arena dir or no series exist.
        """
        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])
        arena_dir = data_home / "arena"
        return JSONResponse(_list_series(arena_dir))

    @app.get("/api/arena/{series_id}/diff/{team}/{match_n}")
    async def get_series_strategy_diff(
        series_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$"),
        team: str = PathParam(...),
        match_n: int = PathParam(..., ge=1),
    ):
        """Compute unified diff between consecutive strategy versions for a team.

        strategy_v(N) lives at arena/series_<id>/strategies/<team>/strategy_v{N}.py.
        strategy_v(N-1) is the previous version (empty string for N=1, i.e. no prior).

        Returns: { team, from_version: N-1, to_version: N, diff_text: str }
        404 if series or strategy file not found.
        422 if team is not 'team_a' or 'team_b'.
        """
        import difflib

        if team not in ("team_a", "team_b"):
            raise HTTPException(status_code=422, detail=f"team must be 'team_a' or 'team_b', got {team!r}")

        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])
        arena_dir = data_home / "arena"
        s_dir = _series_dir(arena_dir, series_id)

        if not s_dir.is_dir():
            raise HTTPException(status_code=404, detail=f"Series '{series_id}' not found")

        strat_dir = s_dir / "strategies" / team
        _EXTS = (".py", ".js", ".rs")
        current_path = next(
            (strat_dir / f"strategy_v{match_n}{ext}" for ext in _EXTS
             if (strat_dir / f"strategy_v{match_n}{ext}").exists()),
            None,
        )
        if current_path is None:
            raise HTTPException(
                status_code=404,
                detail=f"Strategy file strategy_v{match_n} not found for {team} in series '{series_id}'",
            )

        current_lines = current_path.read_text(encoding="utf-8").splitlines(keepends=True)

        from_version = match_n - 1
        if from_version == 0:
            prev_lines = []
            prev_name = "(none)"
        else:
            prev_path = next(
                (strat_dir / f"strategy_v{from_version}{ext}" for ext in _EXTS
                 if (strat_dir / f"strategy_v{from_version}{ext}").exists()),
                None,
            )
            if prev_path is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Prior strategy file strategy_v{from_version} not found for {team} in series '{series_id}'",
                )
            prev_lines = prev_path.read_text(encoding="utf-8").splitlines(keepends=True)
            prev_name = prev_path.name

        diff_lines = list(difflib.unified_diff(
            prev_lines,
            current_lines,
            fromfile=prev_name,
            tofile=current_path.name,
        ))
        diff_text = "".join(diff_lines)

        return JSONResponse({
            "team":         team,
            "from_version": from_version,
            "to_version":   match_n,
            "diff_text":    diff_text,
        })

    @app.get("/api/arena/{series_id}/stream")
    async def stream_series_events(series_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Stream Arena series lifecycle events via Server-Sent Events.

        Tails <arena_dir>/series_<id>/events.jsonl. Streams existing lines
        first (catch-up), then polls for new entries. Each SSE data payload is
        a raw JSON object from events.jsonl. Sends a 'series_complete' event
        when series.json.status leaves 'running'. Times out after 30 minutes.
        """
        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])
        arena_dir = data_home / "arena"
        s_dir = _series_dir(arena_dir, series_id)

        if not s_dir.is_dir():
            return JSONResponse(
                status_code=404,
                content={"error": "series_not_found", "detail": f"Series '{series_id}' not found"},
            )

        return StreamingResponse(_stream_series_events(s_dir, series_id), media_type="text/event-stream")

    @app.get("/api/arena/{series_id}")
    async def get_arena_series(series_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Get full series detail including the matches array.

        Returns the raw series.json dict.
        404 if the series directory or series.json is not found.
        """
        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])
        arena_dir = data_home / "arena"
        s_dir = _series_dir(arena_dir, series_id)

        if not s_dir.is_dir():
            raise HTTPException(status_code=404, detail=f"Series '{series_id}' not found")

        try:
            data = _read_series_json(s_dir)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"series.json not found for series '{series_id}'")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Malformed series.json: {e}")

        return JSONResponse(data)

    @app.post("/api/arena")
    async def start_series(payload: StartSeriesPayload):
        """Start a new Arena series by spawning agent-pitch run as a background subprocess.

        Per ADR-0006 the API layer cannot import simulation modules — we shell
        out to the CLI with --arena-id so the orchestrator handles PMEP and
        strategy evolution across the series matches.

        Steps:
        1. Validate config_name exists on disk.
        2. Generate series_id (timestamp-based).
        3. Create arena/series_<id>/ directory + initial series.json.
        4. Spawn subprocess: agent-pitch run --season-length N --arena-id <id>.
        5. Return 201 { series_id }.
        """
        import subprocess

        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        config_path = data_home / "configs" / f"{payload.config_name}.yaml"
        if not config_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Match config '{payload.config_name}' not found",
            )

        # Determine season length from format
        season_length = 3 if payload.format == "3-match" else 5

        # Generate a unique series ID
        series_id = f"series-{_timestamp_compact()}"

        arena_dir = data_home / "arena"
        arena_dir.mkdir(parents=True, exist_ok=True)
        matches_dir = data_home / "matches"
        matches_dir.mkdir(parents=True, exist_ok=True)

        s_dir = _series_dir(arena_dir, series_id)
        # Guard against the (extremely unlikely) collision of two series in the
        # same minute: bump the ID with a counter suffix.
        collision_guard = 0
        while s_dir.exists() and collision_guard < 60:
            collision_guard += 1
            s_dir = arena_dir / f"series_{series_id}-{collision_guard}"
            # Also update series_id to match the directory we'll actually use
            series_id = f"{series_id}-{collision_guard}" if collision_guard == 1 else series_id.rsplit("-", 1)[0] + f"-{collision_guard}"

        s_dir.mkdir(parents=True, exist_ok=True)

        # Build human-readable model labels for series.json display
        def _model_label(provider: "str | None", model: "str | None") -> str:
            if provider and model:
                return f"{provider}/{model}"
            if provider:
                return provider
            return "global config"

        initial_series_json = {
            "series_id":     series_id,
            "format":        payload.format,
            "status":        "running",
            "config_name":   payload.config_name,
            "started_iso":   _now_iso(),
            "completed_iso": None,
            "matches":       [],
            "score":         {"team_a": 0, "team_b": 0, "ties": 0},
            "models": {
                "team_a": _model_label(payload.team_a_provider, payload.team_a_model),
                "team_b": _model_label(payload.team_b_provider, payload.team_b_model),
                "team_a_language": payload.team_a_language or "python",
                "team_b_language": payload.team_b_language or "python",
            },
        }
        _write_series_json(s_dir, initial_series_json)

        cmd = [
            sys.executable, "-m", "src.cli", "run",
            "--config", str(config_path),
            "--season-length", str(season_length),
            "--arena-id", series_id,
            "--arena-dir", str(arena_dir),
            "--log-dir", str(matches_dir),
        ]
        if payload.team_a_provider:
            cmd.extend(["--provider-a", payload.team_a_provider])
        if payload.team_a_model:
            cmd.extend(["--model-a", payload.team_a_model])
        if payload.team_b_provider:
            cmd.extend(["--provider-b", payload.team_b_provider])
        if payload.team_b_model:
            cmd.extend(["--model-b", payload.team_b_model])
        if payload.team_a_language:
            cmd.extend(["--language-a", payload.team_a_language])
        if payload.team_b_language:
            cmd.extend(["--language-b", payload.team_b_language])
        global_defaults_path = data_home / "global-defaults.yaml"
        if global_defaults_path.exists():
            cmd.extend(["--global-defaults", str(global_defaults_path)])

        print(f"[start_series] spawning series={series_id}: {' '.join(cmd)}", flush=True)

        try:
            popen = subprocess.Popen(
                cmd,
                stdout=None,   # inherit
                stderr=None,   # inherit
                start_new_session=True,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to spawn series subprocess: {e}",
            )

        app.state.running_series[series_id] = {
            "popen":      popen,
            "pid":        popen.pid,
            "started_at": time.time(),
        }

        return JSONResponse(
            status_code=201,
            content={"series_id": series_id},
        )

    @app.delete("/api/arena/{series_id}")
    async def delete_arena_series(
        series_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$"),
        cascade: bool = Query(False),
    ):
        """Delete an Arena series directory and optionally its associated match dirs.

        Query param:
          cascade=false (default) — only delete the series_<id>/ directory.
          cascade=true — also delete data_home/matches/match_<match_id>/ for
                         every match listed in series.json. Missing match dirs
                         are silently skipped.

        Returns 204 No Content on success.
        404 if the series directory does not exist.
        """
        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])
        arena_dir = data_home / "arena"
        s_dir = _series_dir(arena_dir, series_id)

        if not s_dir.is_dir():
            raise HTTPException(status_code=404, detail=f"Series '{series_id}' not found")

        if cascade:
            try:
                series_data = _read_series_json(s_dir)
                for match_entry in series_data.get("matches", []):
                    mid = match_entry.get("match_id")
                    if not mid:
                        continue
                    match_dir = data_home / "matches" / f"match_{mid}"
                    if match_dir.is_dir():
                        try:
                            shutil.rmtree(match_dir)
                        except OSError:
                            pass  # best-effort; log but don't abort
            except (FileNotFoundError, json.JSONDecodeError):
                pass  # no series.json or malformed — skip cascade

        try:
            shutil.rmtree(s_dir)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete series: {e}")

        return Response(status_code=204)

    @app.post("/api/matches")
    async def start_match(payload: StartMatchPayload):
        """Start a new match by spawning agent-pitch CLI as a background subprocess.

        Per ADR-0006 the API layer cannot import simulation modules — instead
        we shell out to the CLI which now accepts --match-id / --strategy-a /
        --strategy-b flags (added 2026-04-24).
        """
        import subprocess
        import sys as _sys

        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        # Validate referenced files exist
        config_path = data_home / "configs" / f"{payload.config_name}.yaml"
        if not config_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Match config '{payload.config_name}' not found",
            )

        # Resolve strategy paths via the library so the correct extension
        # (.py or .js) is used based on each strategy's recorded language.
        def _resolve_strategy(name: str) -> Path:
            try:
                meta = lib_read_meta(data_home, name)
            except (InvalidStrategyNameError, StrategyLibraryError):
                meta = UNKNOWN_META
            return lib_source_path(data_home, name, language=meta.language)

        strategy_a_path = _resolve_strategy(payload.strategy_a)
        strategy_b_path = _resolve_strategy(payload.strategy_b)
        if not strategy_a_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Strategy '{payload.strategy_a}' not found",
            )
        if not strategy_b_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Strategy '{payload.strategy_b}' not found",
            )

        # Refuse if a match dir with this id already exists
        match_dir = data_home / "matches" / f"match_{payload.match_id}"
        if match_dir.exists():
            raise HTTPException(
                status_code=409,
                detail=f"Match id '{payload.match_id}' already exists",
            )

        # Build the CLI command. --log-dir overrides the saved config's
        # output.log_dir so the match writes to <DATA_HOME>/matches/match_<id>/
        # (where GET /api/matches looks) regardless of what the yaml says.
        matches_dir = data_home / "matches"
        matches_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            _sys.executable, "-m", "src.cli", "run",
            "--config", str(config_path),
            "--season-length", "1",
            "--match-id", payload.match_id,
            "--strategy-a", str(strategy_a_path),
            "--strategy-b", str(strategy_b_path),
            "--log-dir", str(matches_dir),
        ]
        # Append --seed only when the UI explicitly supplied an override.
        if payload.seed_override is not None:
            cmd.extend(["--seed", str(payload.seed_override)])
        # Always pass --global-defaults if the file exists. The CLI overlays
        # any simulation-related keys onto config.simulation at runtime so
        # Game-tab edits take effect without each saved match config carrying
        # its own copy of those fields.
        global_defaults_path = data_home / "global-defaults.yaml"
        if global_defaults_path.exists():
            cmd.extend(["--global-defaults", str(global_defaults_path)])
        # Debug log the spawn command so the user can verify what reaches
        # the orchestrator (especially seed override behavior).
        print(f"[start_match] spawning: {' '.join(cmd)}", flush=True)

        # Spawn detached so the match runs in the background. Inherit stdout/stderr
        # so the user can follow progress in the server's terminal (matches the
        # behavior of `agent-pitch run` when invoked directly).
        try:
            popen = subprocess.Popen(
                cmd,
                stdout=None,  # inherit
                stderr=None,  # inherit
                start_new_session=True,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to spawn match subprocess: {e}",
            )

        # Estimate total ticks so the status endpoint can compute progress
        # without re-reading the YAML each poll. tick_rate * duration_min * 60.
        try:
            with open(config_path, 'r') as f:
                cfg_data = yaml.safe_load(f) or {}
            mp = cfg_data.get("match", {}) or {}
            total_ticks = int(mp.get("tick_rate", 10)) * int(mp.get("duration_minutes", 5)) * 60
        except Exception:
            total_ticks = 0

        # Track for /api/matches/<id>/status. started_at is wall-clock so the
        # UI can show "elapsed: 2m 34s".
        app.state.running_matches[payload.match_id] = {
            "popen": popen,
            "pid": popen.pid,
            "started_at": time.time(),
            "total_ticks": total_ticks,
        }

        return JSONResponse(
            status_code=202,
            content={"match_id": payload.match_id, "status": "starting", "pid": popen.pid},
        )

    # ─────────────────────────────────────────────────────────────────
    # Strategy Cup endpoints — cup lifecycle (GET/POST/DELETE /api/cups)
    # ─────────────────────────────────────────────────────────────────

    async def _stream_cup_events(cup_d: Path, cup_id: str):
        """Generator yielding SSE-formatted bytes for a cup events.jsonl.

        Tails <cup_d>/events.jsonl for lifecycle events. Each line must be a
        JSON object with 'event' and 'data' fields. Streams existing lines first
        (catch-up mode), then polls for new lines. Times out after 60 minutes.

        Subprocess exit detection: if the cup subprocess has exited with a
        non-zero return code and cup.json still says 'running', this generator
        marks cup.json as 'errored' so the UI gets immediate feedback rather
        than waiting for the timeout.
        """
        events_path = cup_d / "events.jsonl"

        pos = 0
        buffer = b""
        started = asyncio.get_running_loop().time()
        CUP_SSE_TIMEOUT_S = 3600  # 60 minutes (cups can take longer than series)

        while True:
            if events_path.exists():
                with open(events_path, "rb") as f:
                    f.seek(pos)
                    new_bytes = f.read()
                    pos = f.tell()
                buffer += new_bytes
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str:
                        continue
                    try:
                        parsed = json.loads(line_str)
                        evt_name = parsed.get("event", "message")
                        evt_data = json.dumps(parsed.get("data", {}))
                        yield f"event: {evt_name}\ndata: {evt_data}\n\n".encode("utf-8")
                    except (json.JSONDecodeError, AttributeError):
                        yield f"data: {line_str}\n\n".encode("utf-8")

            # Check if cup is finished (status != "running")
            try:
                cup_data = _read_cup_json(cup_d)
                status = cup_data.get("status", "running")
                if status != "running":
                    completed_text = json.dumps(cup_data)
                    sse_event = "cup-errored" if status == "errored" else "cup-completed"
                    yield f"event: {sse_event}\ndata: {completed_text}\n\n".encode("utf-8")
                    return
            except (FileNotFoundError, json.JSONDecodeError):
                cup_data = None

            # Detect subprocess death: if the process exited non-zero and the
            # cup is still "running", mark it errored immediately.
            if cup_data is None or cup_data.get("status") == "running":
                entry = app.state.running_cups.get(cup_id)
                if entry is not None:
                    rc = entry["popen"].poll()
                    if rc is not None and rc != 0:
                        try:
                            current = _read_cup_json(cup_d)
                        except (FileNotFoundError, json.JSONDecodeError):
                            current = {}
                        if current.get("status") == "running":
                            import datetime as _dt
                            current["status"] = "errored"
                            current["completed_iso"] = _dt.datetime.now(
                                _dt.timezone.utc).isoformat()
                            _write_cup_json(cup_d, current)
                        app.state.running_cups.pop(cup_id, None)
                        errored_text = json.dumps(current)
                        yield f"event: cup-errored\ndata: {errored_text}\n\n".encode("utf-8")
                        return

            if asyncio.get_running_loop().time() - started > CUP_SSE_TIMEOUT_S:
                yield b'event: error\ndata: {"error": "stream_timeout"}\n\n'
                return

            await asyncio.sleep(SSE_POLL_MS / 1000)

    @app.get("/api/cups")
    async def list_cups_endpoint():
        """List all Strategy Cup tournaments, sorted by created_iso descending.

        Returns a summary list — each item contains:
        cup_id, name, status, config_name, bracket_size, created_iso, completed_iso, winner.
        Returns an empty list when no cups dir or no cups exist.
        """
        cups = _list_cups(app.state.cups_dir)
        return JSONResponse(cups)

    @app.get("/api/cups/{cup_id}")
    async def get_cup(cup_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Get full cup detail including bracket and rounds.

        Returns the raw cup.json dict.
        404 if the cup directory or cup.json is not found.
        """
        cup_d = _cup_dir(app.state.cups_dir, cup_id)
        if not cup_d.exists():
            raise HTTPException(status_code=404, detail=f"Cup '{cup_id}' not found")
        try:
            data = _read_cup_json(cup_d)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Cup '{cup_id}' not found")
        matches_dir = app.state.matches_dir
        for round_entry in data.get("rounds", []):
            for match in round_entry.get("matches", []):
                match_id = match.get("match_id")
                if not match_id:
                    continue
                match_dir = matches_dir / f"match_{match_id}"
                names = team_names_for_match(match_dir)
                match["team_a_name"] = names["team_a"]
                match["team_b_name"] = names["team_b"]
        return JSONResponse(data)

    @app.get("/api/cups/{cup_id}/stream")
    async def stream_cup_events(cup_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Stream Strategy Cup lifecycle events via Server-Sent Events.

        Tails <cups_dir>/cup_<id>/events.jsonl. Streams existing lines first
        (catch-up), then polls for new entries. Each SSE data payload is a raw
        JSON object from events.jsonl. Sends a 'cup-completed' or 'cup-errored'
        event when cup.json status leaves 'running'. Times out after 60 minutes.
        """
        cup_d = _cup_dir(app.state.cups_dir, cup_id)
        if not cup_d.is_dir():
            return JSONResponse(
                status_code=404,
                content={"error": "cup_not_found", "detail": f"Cup '{cup_id}' not found"},
            )
        return StreamingResponse(_stream_cup_events(cup_d, cup_id), media_type="text/event-stream")

    @app.post("/api/cups", status_code=201)
    async def start_cup(payload: StartCupPayload):
        """Start a new Strategy Cup tournament by spawning a background subprocess.

        Per ADR-0006 the API layer cannot import simulation modules — we shell
        out to the CLI with --cup-id so the orchestrator handles bracket
        progression and all match execution.

        Steps:
        1. Validate config_name exists on disk.
        2. Validate all strategy files exist.
        3. Generate cup_id (timestamp-based + random suffix).
        4. Create cups/cup_<id>/ directory + initial cup.json via generate_bracket().
        5. Create empty events.jsonl.
        6. Spawn subprocess: src.cli cup-run --cup-id ...
        7. Return 201 { cup_id }.
        """
        import subprocess
        import uuid as _uuid

        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        # 1. Validate config_name exists
        config_path = data_home / "configs" / f"{payload.config_name}.yaml"
        if not config_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Match config '{payload.config_name}' not found",
            )

        # 2. Validate all strategy files exist (probe .py / .js / .rs)
        strategies_dir = data_home / "strategies"
        _EXTS = (".py", ".js", ".rs")
        for strategy_name in payload.strategies:
            found = any(
                (strategies_dir / f"{strategy_name}{ext}").exists()
                for ext in _EXTS
            )
            if not found:
                raise HTTPException(
                    status_code=404,
                    detail=f"Strategy '{strategy_name}' not found",
                )

        # 3. Generate unique cup_id: timestamp + 6-char uuid fragment
        ts = _timestamp_compact()
        uid = _uuid.uuid4().hex[:6]
        cup_id = f"cup-{ts}-{uid}"

        cups_dir = app.state.cups_dir
        cups_dir.mkdir(parents=True, exist_ok=True)
        matches_dir = data_home / "matches"
        matches_dir.mkdir(parents=True, exist_ok=True)

        cup_d = _cup_dir(cups_dir, cup_id)
        cup_d.mkdir(parents=True, exist_ok=True)

        # 5. Build initial cup.json using generate_bracket, then fill in meta fields
        cup_data = _generate_bracket(payload.bracket_size, list(payload.strategies), cup_id)
        cup_data["name"] = payload.name
        cup_data["config_name"] = payload.config_name
        cup_data["created_iso"] = _now_iso()

        # 6. Write cup.json
        _write_cup_json(cup_d, cup_data)

        # 7. Create empty events.jsonl
        (cup_d / "events.jsonl").write_text("", encoding="utf-8")

        # 8. Spawn subprocess
        cmd = [
            sys.executable, "-m", "src.cli", "cup-run",
            "--cup-id", cup_id,
            "--cup-dir", str(cup_d),
            "--config", str(config_path),
            "--log-dir", str(matches_dir),
            "--data-dir", str(data_home),
        ]
        global_defaults_path = data_home / "global-defaults.yaml"
        if global_defaults_path.exists():
            cmd.extend(["--global-defaults", str(global_defaults_path)])

        print(f"[start_cup] spawning cup={cup_id}: {' '.join(cmd)}", flush=True)

        try:
            popen = subprocess.Popen(
                cmd,
                stdout=None,   # inherit
                stderr=None,   # inherit
                start_new_session=True,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to spawn cup subprocess: {e}",
            )

        # 9. Register in running_cups
        app.state.running_cups[cup_id] = {
            "popen":      popen,
            "pid":        popen.pid,
            "started_at": time.time(),
        }

        # 10. Return cup_id
        return JSONResponse(
            status_code=201,
            content={"cup_id": cup_id},
        )

    @app.delete("/api/cups/{cup_id}")
    async def delete_cup(
        cup_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$"),
        cascade: bool = Query(False),
    ):
        """Delete a Strategy Cup directory and optionally its associated match dirs.

        Query param:
          cascade=false (default) — only delete the cup_<id>/ directory.
          cascade=true — also delete data_home/matches/match_<match_id>/ for
                         every match listed in cup.json. Missing match dirs
                         are silently skipped.

        Returns 204 No Content on success.
        404 if the cup directory does not exist.
        """
        cup_d = _cup_dir(app.state.cups_dir, cup_id)
        if not cup_d.is_dir():
            raise HTTPException(status_code=404, detail=f"Cup '{cup_id}' not found")

        # Terminate running subprocess if any
        entry = app.state.running_cups.pop(cup_id, None)
        if entry is not None:
            proc = entry.get("popen")
            if proc is not None:
                try:
                    proc.terminate()
                except OSError:
                    pass

        if cascade:
            log_dir = app.state.log_dir
            storage_settings = _load_storage_config(log_dir)
            data_home = Path(storage_settings["data_home"])
            try:
                cup_data = _read_cup_json(cup_d)
                for round_entry in cup_data.get("rounds", []):
                    for match_entry in round_entry.get("matches", []):
                        mid = match_entry.get("match_id")
                        if not mid:
                            continue
                        match_dir = data_home / "matches" / f"match_{mid}"
                        if match_dir.is_dir():
                            try:
                                shutil.rmtree(match_dir)
                            except OSError:
                                pass  # best-effort; don't abort
            except (FileNotFoundError, json.JSONDecodeError):
                pass  # no cup.json or malformed — skip cascade

        try:
            shutil.rmtree(cup_d)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete cup: {e}")

        return Response(status_code=204)

    @app.post("/api/cups/{cup_id}/rerun")
    async def rerun_cup(cup_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Create a new cup with the same settings as an existing cup.

        Reads the original cup.json, then calls start_cup with the same
        name, config_name, bracket_size, and strategies. Returns the new cup_id.
        Does NOT restart the original cup in-place.

        404 if the original cup does not exist or cup.json cannot be read.
        """
        cup_d = _cup_dir(app.state.cups_dir, cup_id)
        if not cup_d.is_dir():
            raise HTTPException(status_code=404, detail=f"Cup '{cup_id}' not found")
        try:
            cup_data = _read_cup_json(cup_d)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Cup '{cup_id}' cup.json unreadable")

        # Reconstruct the original strategies list in slot order
        teams = cup_data.get("teams", [])
        teams_sorted = sorted(teams, key=lambda t: t.get("slot", 0))
        try:
            strategies = [t["strategy_name"] for t in teams_sorted]
        except (KeyError, TypeError) as e:
            raise HTTPException(status_code=422, detail=f"Malformed cup.json: {e}")

        new_payload = StartCupPayload(
            name=cup_data.get("name", ""),
            config_name=cup_data.get("config_name", ""),
            bracket_size=cup_data.get("bracket_size", len(strategies)),
            strategies=strategies,
        )
        return await start_cup(new_payload)

    # ── Strategy League endpoints ──────────────────────────────────────────

    async def _stream_league_events(league_d: Path, league_id: str):
        """Generator yielding SSE-formatted bytes for a league events.jsonl.

        Tails <league_d>/events.jsonl for lifecycle events. Streams existing
        lines first (catch-up mode), then polls for new lines. Times out after
        60 minutes. Mirrors _stream_cup_events pattern (ADR-0011).
        """
        events_path = league_d / "events.jsonl"
        LEAGUE_SSE_TIMEOUT_S = 3600

        pos = 0
        buffer = b""
        started = asyncio.get_running_loop().time()

        while True:
            if events_path.exists():
                with open(events_path, "rb") as f:
                    f.seek(pos)
                    new_bytes = f.read()
                    pos = f.tell()
                buffer += new_bytes
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str:
                        continue
                    try:
                        parsed = json.loads(line_str)
                        evt_name = parsed.get("event", "message")
                        evt_data = json.dumps(parsed.get("data", {}))
                        yield f"event: {evt_name}\ndata: {evt_data}\n\n".encode("utf-8")
                    except (json.JSONDecodeError, AttributeError):
                        yield f"data: {line_str}\n\n".encode("utf-8")

            try:
                league_data = _read_league_json(league_d)
                status = league_data.get("status", "running")
            except Exception:
                league_data = None
                status = "running"

            if league_data is not None and status != "running":
                completed_text = json.dumps(league_data)
                sse_event = "league-errored" if status == "errored" else "league-completed"
                yield f"event: {sse_event}\ndata: {completed_text}\n\n".encode("utf-8")
                break

            # Detect subprocess death: if the process exited non-zero and the
            # league is still "running", mark it errored immediately.
            if league_data is None or league_data.get("status") == "running":
                entry = app.state.running_leagues.get(league_id)
                if entry is not None:
                    rc = entry["popen"].poll()
                    if rc is not None and rc != 0:
                        try:
                            current = _read_league_json(league_d)
                        except (FileNotFoundError, json.JSONDecodeError):
                            current = {}
                        if current.get("status") == "running":
                            import datetime as _dt
                            current["status"] = "errored"
                            current["completed_iso"] = _dt.datetime.now(
                                _dt.timezone.utc).isoformat()
                            _write_league_json(league_d, current)
                        app.state.running_leagues.pop(league_id, None)
                        errored_text = json.dumps(current)
                        yield f"event: league-errored\ndata: {errored_text}\n\n".encode("utf-8")
                        break

            if asyncio.get_running_loop().time() - started > LEAGUE_SSE_TIMEOUT_S:
                yield b'event: error\ndata: {"error": "stream_timeout"}\n\n'
                return

            await asyncio.sleep(SSE_POLL_MS / 1000)

    @app.get("/api/leagues")
    async def list_leagues_endpoint():
        """List all Strategy League tournaments, sorted by created_iso descending.

        Returns a summary list — each item contains:
        league_id, name, status, config_name, num_rounds, team_count,
        created_iso, completed_iso, champion.
        Returns an empty list when no leagues dir or no leagues exist.
        """
        leagues = _list_leagues(app.state.leagues_dir)
        return JSONResponse(leagues)

    @app.get("/api/leagues/{league_id}")
    async def get_league(league_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Get full league detail including matchdays and standings.

        Returns the raw league.json dict.
        404 if the league directory or league.json is not found.
        """
        league_d = _league_dir(app.state.leagues_dir, league_id)
        if not league_d.exists():
            raise HTTPException(status_code=404, detail=f"League '{league_id}' not found")
        try:
            data = _read_league_json(league_d)
        except Exception:
            raise HTTPException(status_code=404, detail=f"League '{league_id}' not found")
        return JSONResponse(data)

    @app.get("/api/leagues/{league_id}/stream")
    async def stream_league_events(league_id: str = PathParam(..., pattern=r"^[A-Za-z0-9_-]{1,128}$")):
        """Stream Strategy League lifecycle events via Server-Sent Events.

        Tails <leagues_dir>/league_<id>/events.jsonl. Streams existing lines
        first (catch-up), then polls for new entries. Each SSE data payload is
        a raw JSON object from events.jsonl. Sends 'league-completed' or
        'league-errored' terminal event when status leaves 'running'.
        Times out after 60 minutes.
        """
        league_d = _league_dir(app.state.leagues_dir, league_id)
        if not league_d.is_dir():
            return JSONResponse(
                status_code=404,
                content={"error": "league_not_found", "detail": f"League '{league_id}' not found"},
            )
        return StreamingResponse(
            _stream_league_events(league_d, league_id),
            media_type="text/event-stream",
        )

    @app.post("/api/leagues", status_code=201)
    async def start_league(payload: StartLeaguePayload):
        """Start a new Strategy League tournament by spawning a background subprocess.

        Per ADR-0006 the API layer cannot import simulation modules — we shell
        out to the CLI with --league-id so the orchestrator handles matchday
        progression and all match execution.

        Steps:
        1. Validate config_name exists on disk.
        2. Validate all strategy files exist.
        3. Generate league_id (timestamp-based + random suffix).
        4. Create leagues/league_<id>/ directory + initial league.json via generate_schedule().
        5. Create empty events.jsonl.
        6. Spawn subprocess: src.cli league-run --league-id ...
        7. Return 201 { league_id }.
        """
        import subprocess
        import uuid as _uuid

        log_dir = app.state.log_dir
        storage_settings = _load_storage_config(log_dir)
        data_home = Path(storage_settings["data_home"])

        # 1. Validate config_name
        config_path = data_home / "configs" / f"{payload.config_name}.yaml"
        if not config_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Match config '{payload.config_name}' not found",
            )

        # 2. Validate strategy files
        strategies_dir = data_home / "strategies"
        _EXTS = (".py", ".js", ".rs")
        for strategy_name in payload.strategies:
            found = any(
                (strategies_dir / f"{strategy_name}{ext}").exists()
                for ext in _EXTS
            )
            if not found:
                raise HTTPException(
                    status_code=404,
                    detail=f"Strategy '{strategy_name}' not found",
                )

        # 3. Generate unique league_id
        ts = _timestamp_compact()
        uid = _uuid.uuid4().hex[:6]
        league_id = f"league-{ts}-{uid}"

        leagues_dir = app.state.leagues_dir
        leagues_dir.mkdir(parents=True, exist_ok=True)
        matches_dir = data_home / "matches"
        matches_dir.mkdir(parents=True, exist_ok=True)

        league_d = _league_dir(leagues_dir, league_id)
        league_d.mkdir(parents=True, exist_ok=True)

        # 4. Build initial league.json
        league_data = _generate_schedule(
            len(payload.strategies),
            list(payload.strategies),
            league_id,
            num_rounds=payload.num_rounds,
        )
        league_data["name"] = payload.name
        league_data["config_name"] = payload.config_name
        league_data["created_iso"] = _now_iso()

        _write_league_json(league_d, league_data)
        (league_d / "events.jsonl").write_text("", encoding="utf-8")

        # 5. Spawn subprocess
        cmd = [
            sys.executable, "-m", "src.cli", "league-run",
            "--league-id", league_id,
            "--league-dir", str(league_d),
            "--config", str(config_path),
            "--log-dir", str(matches_dir),
            "--data-dir", str(data_home),
        ]
        global_defaults_path = data_home / "global-defaults.yaml"
        if global_defaults_path.exists():
            cmd.extend(["--global-defaults", str(global_defaults_path)])

        print(f"[start_league] spawning league={league_id}: {' '.join(cmd)}", flush=True)

        try:
            popen = subprocess.Popen(
                cmd,
                stdout=None,
                stderr=None,
                start_new_session=True,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to spawn league subprocess: {e}")

        app.state.running_leagues[league_id] = {
            "popen":      popen,
            "pid":        popen.pid,
            "started_at": time.time(),
        }

        return JSONResponse(status_code=201, content={"league_id": league_id})

    return app


def _load_llm_config(data_home: Path) -> dict:
    """Load LLM configuration including provider settings and key status."""
    providers_path = data_home / "llm-providers.yaml"

    # Load provider configs (URLs and models)
    provider_configs = {}
    if providers_path.exists():
        try:
            with open(providers_path, 'r') as f:
                data = yaml.safe_load(f) or {}
                if isinstance(data, dict):
                    provider_configs = data
        except (yaml.YAMLError, FileNotFoundError):
            pass  # Use empty config

    # Default providers with their settings
    BUILTIN_PROVIDERS = {"openai", "anthropic", "gemini"}
    default_providers = {
        "openai": {
            "url": "https://api.openai.com/v1",
            "model": "gpt-4o"
        },
        "anthropic": {
            "url": "https://api.anthropic.com",
            "model": "claude-sonnet-4-6"
        },
        "gemini": {
            "url": "https://generativelanguage.googleapis.com",
            "model": "gemini-2.0-flash"
        }
    }

    # Build provider list with key status
    providers = []

    # Built-in providers (always present)
    for provider_name in ["openai", "anthropic", "gemini"]:
        config = provider_configs.get(provider_name, default_providers[provider_name])
        key_status = get_key_status(data_home, provider_name)

        providers.append({
            "name": provider_name,
            "url": config.get("url", default_providers[provider_name]["url"]),
            "model": config.get("model", default_providers[provider_name]["model"]),
            "key_status": key_status,
            "builtin": True
        })

    # Custom providers (from YAML, any key not in BUILTIN_PROVIDERS)
    for name, config in provider_configs.items():
        if name in BUILTIN_PROVIDERS:
            continue
        if not isinstance(config, dict):
            continue
        key_status = get_key_status(data_home, name)
        providers.append({
            "name": name,
            "url": config.get("url", ""),
            "model": config.get("model", ""),
            "type": config.get("type", "openai_compatible"),
            "key_status": key_status,
            "builtin": False
        })

    # Determine active provider - for now, just return the first one with a key
    active = None
    for provider in providers:
        if provider["key_status"] != "unset":
            active = {"provider": provider["name"], "model": provider["model"]}
            break

    return {
        "providers": providers,
        "active": active
    }


# OpenAI's /v1/models returns all model types (not just chat):
#   - Embeddings: text-embedding-3-small, text-embedding-3-large
#   - Audio STT: whisper-1
#   - Image gen: dall-e-2, dall-e-3
#   - Moderation: text-moderation-*, omni-moderation-*
#   - Fine-tunes: ft:gpt-*
#   - Legacy base models: babbage-002, davinci-002
# Allowlist only the families that support chat completions for strategy generation.
# When a new chat family launches (e.g. "o4-", "gpt-6-"), append it here.
_OPENAI_CHAT_MODEL_PREFIXES: tuple[str, ...] = (
    "gpt-",      # GPT-3.5, GPT-4, GPT-4o, GPT-5 series (excludes non-chat via substring filter)
    "o1",        # o1-preview, o1-mini (deprecated but may still be accessible)
    "o3",        # o3-mini (deprecated but may still be accessible)
    "chatgpt-",  # ChatGPT snapshots
)

# After the prefix allowlist, drop IDs containing these substrings — they
# share a chat-family prefix (mostly "gpt-") but serve different purposes:
#   image       → gpt-image-1, gpt-image-1.5 (DALL-E image generation)
#   tts         → gpt-4o-mini-tts (text-to-speech synthesis)
#   transcribe  → gpt-4o-transcribe, gpt-4o-mini-transcribe (audio transcription/STT)
#   realtime    → gpt-4o-realtime-preview (WebSocket Realtime API, not REST chat)
#   moderation  → text-moderation-*, omni-moderation-* (content moderation)
#   embedding   → text-embedding-* (defensive; future gpt-embedding-* models)
#   codex       → gpt-5.x-codex (Responses API only, not chat completions)
#   audio       → gpt-4o-audio-preview, gpt-audio-mini (audio I/O models — 16x cost, not for text-only)
_OPENAI_NON_CHAT_SUBSTRINGS: tuple[str, ...] = (
    "image",
    "tts",
    "transcribe",
    "realtime",
    "moderation",
    "embedding",
    "codex",  # Codex models use /v1/responses, not /v1/chat/completions
    "audio",  # Audio I/O models (gpt-4o-audio-preview, gpt-audio-mini) — not suitable for text-only strategy gen
)

# Exact model IDs to exclude — models that pass the prefix allowlist but aren't
# suitable for chat completions (Responses API only models, etc.).
# Add new IDs here when they start appearing in /v1/models but shouldn't be offered
# for strategy generation.
_OPENAI_NON_CHAT_EXACT_IDS: tuple[str, ...] = (
    # Responses API only models (not compatible with /v1/chat/completions):
    "gpt-5-pro",                   # Responses API only
    "gpt-5.4-pro",                 # Responses API only
    "gpt-5.5-pro",                 # Responses API only
    # Note: gpt-audio-* models now caught by "audio" substring filter above
    # Note: babbage-002, davinci-002 don't start with "gpt-" so already excluded by prefix filter
)


def _filter_openai_chat_models(model_ids: list[str]) -> list[str]:
    """Keep ids matching a chat-family prefix and not flagged as non-chat.

    Sorts descending so newer IDs (gpt-4o-* > gpt-4-* > gpt-3.5-*) surface
    above legacy ones. Stable across calls.
    """
    chat = [
        m for m in model_ids
        if m.startswith(_OPENAI_CHAT_MODEL_PREFIXES)
        and not any(sub in m for sub in _OPENAI_NON_CHAT_SUBSTRINGS)
        and m not in _OPENAI_NON_CHAT_EXACT_IDS
    ]
    return sorted(chat, reverse=True)


async def _list_openai_chat_models(api_key: str, base_url: str | None = None) -> list[str]:
    """List OpenAI chat-capable models for the given key.

    Args:
        api_key: OpenAI API key
        base_url: Optional custom API endpoint (for OpenAI-compatible providers)

    Doubles as the connection test: a successful call proves auth without
    spending tokens. Raises Exception on any failure with a user-readable
    message; the API endpoint surfaces it as ``{ok: false, error: ...}``.

    For custom providers (base_url set), skips the chat-model prefix filter
    since custom servers have different model naming conventions.
    """
    try:
        import openai
        import asyncio

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        client = openai.AsyncOpenAI(**client_kwargs)
        page = await asyncio.wait_for(client.models.list(), timeout=10.0)
        all_ids = [m.id for m in page.data]

        if base_url:
            # Custom provider: return all models, no filtering
            if not all_ids:
                return ["(no models found)"]
            return sorted(all_ids)
        else:
            # Official OpenAI: filter to chat models
            chat_models = _filter_openai_chat_models(all_ids)
            if not chat_models:
                raise Exception("OpenAI returned no chat-capable models for this key")
            return chat_models

    except ImportError:
        raise Exception("OpenAI SDK not installed")
    except asyncio.TimeoutError:
        raise Exception("API call timed out")
    except openai.AuthenticationError:
        raise Exception("Invalid API key")
    except openai.PermissionDeniedError:
        raise Exception("API key lacks permissions")
    except openai.RateLimitError:
        raise Exception("Rate limit exceeded")
    except Exception as e:
        if "api key" in str(e).lower():
            raise Exception("Authentication failed")
        raise Exception(f"API error: {str(e)}")


async def _list_anthropic_models(api_key: str) -> list[str]:
    """List Anthropic models for the given key.

    Anthropic's model list is short and pre-curated to chat models, so no
    filtering is needed. Doubles as the connection test (see OpenAI note).
    """
    try:
        import anthropic
        import asyncio

        client = anthropic.AsyncAnthropic(api_key=api_key)
        page = await asyncio.wait_for(client.models.list(), timeout=10.0)
        models = [m.id for m in page.data]
        if not models:
            raise Exception("Anthropic returned no models for this key")
        return models

    except ImportError:
        raise Exception("Anthropic SDK not installed")
    except asyncio.TimeoutError:
        raise Exception("Anthropic API call timed out")
    except anthropic.AuthenticationError:
        raise Exception("Invalid Anthropic API key")
    except anthropic.PermissionDeniedError:
        raise Exception("Anthropic API key lacks permissions")
    except anthropic.RateLimitError:
        raise Exception("Anthropic rate limit exceeded")
    except Exception as e:
        if "api key" in str(e).lower():
            raise Exception("Anthropic authentication failed")
        raise Exception(f"Anthropic API error: {str(e)}")


async def _list_gemini_models(api_key: str) -> list[str]:
    """List Google Gemini models for the given key.

    Doubles as the connection test (see OpenAI note). Returns models that
    support generateContent and are text/chat models (excludes image/video
    generation models like Nano Banana and Veo).
    """
    try:
        import asyncio
        from google import genai

        client = genai.Client(api_key=api_key)

        # Get the async pager by awaiting list(), then iterate over it
        pager = await asyncio.wait_for(
            client.aio.models.list(),
            timeout=10.0
        )

        # Substrings that identify non-chat models (image/video/audio generation)
        # image  → gemini-*-image-* (official names)
        # video  → defensive catch-all
        # imagen → legacy image models (deprecated June 2026)
        # veo    → video generation (Veo 2, Veo 3, etc.)
        # banana → "Nano Banana" codename for Gemini image models
        # lyria  → music/audio generation (Lyria 3, Lyria 3 Pro, etc.)
        non_chat_substrings = ("image", "video", "imagen", "veo", "banana", "lyria")

        models = []
        all_models_raw = []  # Debug: track all models before filtering
        async for model in pager:
            model_name = model.name.replace("models/", "")
            all_models_raw.append({
                'name': model_name,
                'actions': list(model.supported_actions or [])
            })

            # Filter to models that support generateContent action
            if "generateContent" in (model.supported_actions or []):
                # Exclude image/video generation models
                if any(sub in model_name.lower() for sub in non_chat_substrings):
                    continue

                models.append(model_name)

        # Debug logging to help diagnose model filtering issues
        import sys
        print(f"[DEBUG] Gemini API returned {len(all_models_raw)} total models", file=sys.stderr)
        print(f"[DEBUG] After filtering: {len(models)} chat models", file=sys.stderr)
        if len(all_models_raw) <= 5:
            print(f"[DEBUG] All models: {all_models_raw}", file=sys.stderr)

        if not models:
            raise Exception("Gemini returned no generative models for this key")

        # Sort descending (newer models first)
        return sorted(models, reverse=True)

    except ImportError:
        raise Exception("Google GenAI SDK not installed")
    except asyncio.TimeoutError:
        raise Exception("Gemini API call timed out")
    except Exception as e:
        error_str = str(e).lower()
        if "api key" in error_str or "authentication" in error_str or "401" in error_str:
            raise Exception("Invalid Gemini API key")
        if "403" in error_str or "permission" in error_str:
            raise Exception("Gemini API key lacks permissions")
        if "429" in error_str or "quota" in error_str:
            raise Exception("Gemini rate limit exceeded")
        raise Exception(f"Gemini API error: {str(e)}")


def _tail_last_tick(events_path: Path) -> int:
    """Return the `tick` field of the last complete record in events.jsonl.

    Reads only the trailing 4 KiB to stay cheap even when events.jsonl is
    multi-megabyte. Returns 0 if the file is empty / unreadable / has no
    valid trailing JSON record. Used by /api/matches/<id>/status to render
    "tick 1234 / 3000" progress while a match is mid-flight.
    """
    try:
        size = events_path.stat().st_size
        if size == 0:
            return 0
        seek_to = max(0, size - 4096)
        with open(events_path, "rb") as f:
            f.seek(seek_to)
            tail = f.read().decode("utf-8", errors="replace")
        lines = tail.splitlines()
        # When we seeked past byte 0, the first line is almost certainly a
        # partial fragment of a record that started before our window. Drop
        # it so a partial-but-parseable JSON object can't be returned with a
        # truncated tick value.
        if seek_to > 0 and lines:
            lines = lines[1:]
        # Walk backwards until we find a parseable JSON line (handles a
        # half-written final line during active append).
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = rec.get("tick")
            if isinstance(t, int):
                return t
            return 0
    except OSError:
        pass
    return 0


def _format_model(provider: str, model: str) -> str:
    """Render a strategy's provider+model into a single display string for
    the matches list. Matches the engine's _parse_strategy_header output:
      ("baseline", "hand-written") → "baseline"
      ("openai",   "gpt-4o")        → "openai/gpt-4o"
      ("unknown",  "unknown")       → "unknown"   (legacy meta.json)
    """
    if not provider or provider == "unknown":
        return "unknown"
    if provider == "baseline":
        return "baseline"
    return f"{provider}/{model}" if model and model != "unknown" else provider


def _load_game_config(data_home: Path) -> GameConfig:
    """Load GameConfig from global-defaults.yaml.

    On first call (file missing), writes the Pydantic defaults to disk so:
      - the file is discoverable by the user the moment they open Config UI
      - the CLI's --global-defaults overlay always finds something to apply
      - subsequent saves are "edits" rather than "first creates"
    """
    config_path = data_home / "global-defaults.yaml"

    if not config_path.exists():
        # Auto-create the file with Pydantic defaults on first load.
        defaults = GameConfig()
        try:
            data_home.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                yaml.safe_dump(defaults.model_dump(), f, default_flow_style=False)
        except OSError:
            # Read-only filesystem or similar — fall back to in-memory defaults
            # without crashing the request. The user can still see and edit
            # the values; the next successful PUT will create the file.
            pass
        return defaults

    try:
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f) or {}
        # Create GameConfig with loaded data, falling back to defaults for missing fields
        return GameConfig(**data)
    except (yaml.YAMLError, ValidationError, FileNotFoundError):
        # Return defaults if file is malformed or missing
        return GameConfig()