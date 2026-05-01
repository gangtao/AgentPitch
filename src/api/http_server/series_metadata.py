"""Helper functions for reading/writing Arena series metadata.

series.json schema (written alongside each series directory):
{
  "series_id": "<id>",
  "format": "3-match" | "5-match",
  "status": "running" | "complete" | "errored" | "tied",
  "config_name": "<name>",
  "started_iso": "<ISO timestamp>",
  "completed_iso": null,
  "matches": [
    {
      "match_number": 1,
      "match_id": "<id>",
      "result": "team_a" | "team_b" | "tie",
      "final_score": {"team_a": N, "team_b": N}
    }
  ],
  "score": {"team_a": 0, "team_b": 0, "ties": 0}
}

Directory layout:
  <arena_dir>/
    series_<series_id>/
      series.json
      events.jsonl          (lifecycle events for SSE streaming)
      strategies/
        team_a/
          strategy_v1.py
          strategy_v2.py
          ...
        team_b/
          strategy_v1.py
          ...
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

SERIES_DIR_PREFIX = "series_"


def series_dir(arena_dir: Path, series_id: str) -> Path:
    """Return the series directory path: arena_dir / 'series_<series_id>'."""
    return arena_dir / f"{SERIES_DIR_PREFIX}{series_id}"


def read_series_json(series_d: Path) -> dict:
    """Read and return series.json as dict.

    Raises:
        FileNotFoundError: if series.json is absent.
        json.JSONDecodeError: if the file is malformed.
    """
    path = series_d / "series.json"
    return json.loads(path.read_text(encoding="utf-8"))


def write_series_json(series_d: Path, data: dict) -> None:
    """Atomically write series.json via os.replace.

    Writes to a temporary file first, then renames to the target path so
    concurrent readers never see a partial write.
    """
    target = series_d / "series.json"
    tmp = series_d / "series.json.tmp"
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, target)


def list_series(arena_dir: Path) -> List[dict]:
    """Scan arena_dir for series_* subdirectories, return summaries sorted by started_iso desc.

    Each returned dict contains the summary fields from series.json:
    series_id, format, status, config_name, started_iso, completed_iso, score.
    Directories missing or with malformed series.json are silently skipped.

    Returns an empty list if arena_dir does not exist.
    """
    if not arena_dir.exists():
        return []

    results = []
    try:
        for entry in arena_dir.iterdir():
            if not entry.is_dir():
                continue
            if not entry.name.startswith(SERIES_DIR_PREFIX):
                continue
            try:
                data = read_series_json(entry)
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                continue

            summary = {
                "series_id":    data.get("series_id", entry.name.removeprefix(SERIES_DIR_PREFIX)),
                "format":       data.get("format", ""),
                "status":       data.get("status", ""),
                "config_name":  data.get("config_name", ""),
                "started_iso":  data.get("started_iso", ""),
                "completed_iso": data.get("completed_iso"),
                "score":        data.get("score", {"team_a": 0, "team_b": 0, "ties": 0}),
                "models":       data.get("models", {}),
            }
            results.append(summary)
    except (OSError, PermissionError):
        return []

    results.sort(key=lambda x: x["started_iso"], reverse=True)
    return results
