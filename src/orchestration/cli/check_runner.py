"""Match Checker — zero-shot dead-zone validation gate (issue #71).

Scans one or more completed match directories and flags any team that held a
meaningful share of possession yet logged near-zero shots — the symptom of the
positional dead zone in generated `decide()` strategies. Lets the FIFA
match-day pipeline catch the bug automatically (exit code 1) before a report is
published, instead of by manual inspection every match day.

CLI usage:
    agent-pitch check-match --match-dir data/matches/match_<id> [...]
    agent-pitch check-match --match-dir data/matches      # scans match_*/ under it

Reuses the existing per-team stat computation (`compute_match_stats`) rather
than re-deriving shots/possession from raw events.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.api.http_server.match_stats import compute_match_stats
from src.strategy.dead_zone_check import (
    DEFAULT_POSSESSION_MIN,
    DEFAULT_SHOTS_MAX,
    detect_dead_zone,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-pitch check-match",
        description="Flag teams with high possession but near-zero shots "
                    "(the zero-shot dead zone, issue #71).",
    )
    parser.add_argument(
        "--match-dir",
        action="append",
        required=True,
        metavar="PATH",
        help="A match directory (containing events.jsonl + meta.json), or a "
             "parent directory whose match_*/ subdirectories are all scanned. "
             "Repeatable.",
    )
    parser.add_argument(
        "--possession-min",
        type=float,
        default=DEFAULT_POSSESSION_MIN,
        help=f"Minimum possession %% to consider a team in control "
             f"(default: {DEFAULT_POSSESSION_MIN}).",
    )
    parser.add_argument(
        "--shots-max",
        type=int,
        default=DEFAULT_SHOTS_MAX,
        help=f"Flag a team at or below this shot count (default: {DEFAULT_SHOTS_MAX}).",
    )
    return parser


def _resolve_match_dirs(raw_dirs: list[str]) -> list[Path]:
    """Expand each --match-dir argument into concrete match directories.

    A path is treated as a single match dir when it directly contains
    events.jsonl; otherwise its match_*/ subdirectories are scanned (so a
    parent like data/matches can be passed). Results are de-duplicated and
    sorted for deterministic output.
    """
    resolved: list[Path] = []
    for raw in raw_dirs:
        p = Path(raw)
        if (p / "events.jsonl").exists():
            resolved.append(p)
        else:
            resolved.extend(sorted(d for d in p.glob("match_*") if d.is_dir()))
    # De-dup while preserving order.
    seen: set[Path] = set()
    unique: list[Path] = []
    for d in resolved:
        if d not in seen:
            seen.add(d)
            unique.append(d)
    return unique


def check_match_dir(
    match_dir: Path,
    *,
    possession_min: float = DEFAULT_POSSESSION_MIN,
    shots_max: int = DEFAULT_SHOTS_MAX,
) -> list[dict]:
    """Compute stats for one match dir and return any dead-zone flags.

    Raises FileNotFoundError if events.jsonl or meta.json is missing, and
    json.JSONDecodeError on malformed meta — callers decide how to surface
    those. Returns the (possibly empty) list from detect_dead_zone.
    """
    events_path = match_dir / "events.jsonl"
    meta_path = match_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    events = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    stats = compute_match_stats(events, meta)
    return detect_dead_zone(
        stats["teams"], possession_min=possession_min, shots_max=shots_max
    )


def run(args: argparse.Namespace) -> int:
    """Check every resolved match dir; return a process exit code.

    0 = no dead zone found in any match; 1 = at least one team flagged or a
    match dir could not be read. Pure (no sys.exit) so it's unit-testable.
    """
    match_dirs = _resolve_match_dirs(args.match_dir)
    if not match_dirs:
        print("[check-match] no match directories found", file=sys.stderr)
        return 1

    any_flagged = False
    any_error = False
    for match_dir in match_dirs:
        try:
            flags = check_match_dir(
                match_dir,
                possession_min=args.possession_min,
                shots_max=args.shots_max,
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
            print(f"[check-match] {match_dir.name}: SKIP unreadable ({exc})",
                  file=sys.stderr)
            any_error = True
            continue

        if not flags:
            print(f"[check-match] {match_dir.name}: OK")
            continue

        any_flagged = True
        for f in flags:
            print(
                f"[check-match] {match_dir.name}: DEAD ZONE — {f['name']} "
                f"({f['slot']}) had {f['possession_pct']:.1f}% possession but "
                f"only {f['shots']} shot(s)"
            )

    if any_flagged:
        print(f"[check-match] FAIL — dead zone detected "
              f"(possession>={args.possession_min}, shots<={args.shots_max})")
    elif not any_error:
        print("[check-match] PASS — no dead zone detected")
    return 1 if (any_flagged or any_error) else 0


def main() -> None:
    """Entry point for `agent-pitch check-match`."""
    parser = _build_parser()
    # Strip the 'check-match' subcommand word if dispatched via src.cli
    # (sys.argv will be ['<prog>', 'check-match', ...]).
    if len(sys.argv) >= 2 and sys.argv[1] == "check-match":
        sys.argv = [sys.argv[0]] + sys.argv[2:]
    args = parser.parse_args()
    sys.exit(run(args))


__all__ = ["main", "run", "check_match_dir", "_resolve_match_dirs", "_build_parser"]
