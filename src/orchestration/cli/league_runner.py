"""League Runner — round-robin league orchestrator.

Spawned by POST /api/leagues as a detached subprocess. Reads league.json,
runs each matchday sequentially, writes results + standings back, emits SSE
events to events.jsonl for the browser.

CLI usage:
    python -m src.cli league-run \\
      --league-id <id> \\
      --league-dir <path> \\
      --config <path> \\
      --log-dir <path> \\
      --data-dir <path>
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as _dt
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

from src.league_metadata import (
    read_league_json,
    write_league_json,
    compute_standings,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-pitch league-run",
        description="Orchestrate a round-robin league tournament.",
    )
    parser.add_argument("--league-id", required=True)
    parser.add_argument("--league-dir", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--log-dir", required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--global-defaults", default=None)
    return parser


def _append_league_event(league_dir: Path, event_name: str, data: dict) -> None:
    """Append a typed event line to events.jsonl in the league directory.

    Mirrors the _append_event pattern used by the arena runner in
    src/orchestration/cli/__init__.py. Appends JSON lines consumed by the
    SSE endpoint so the browser receives live standings and match updates.
    """
    line = json.dumps({"event": event_name, "data": data})
    events_path = league_dir / "events.jsonl"
    with open(events_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()


def _resolve_strategy_path(data_dir: Path, name: str) -> Path:
    """Probe for strategy file in data_dir/strategies/, trying .py/.js/.rs."""
    for ext in [".py", ".js", ".rs"]:
        p = data_dir / "strategies" / f"{name}{ext}"
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Strategy '{name}' not found in {data_dir / 'strategies'}"
    )


def _slot_to_strategy_name(league_data: dict, slot: int | None) -> str | None:
    """Look up the strategy name for a given team slot number."""
    if slot is None:
        return None
    for team in league_data.get("teams", []):
        if team["slot"] == slot:
            return team["strategy_name"]
    return None


def _read_meta_json(log_dir: Path, match_id: str) -> dict | None:
    """Read meta.json from a completed match directory. Returns None on failure."""
    meta_path = log_dir / f"match_{match_id}" / "meta.json"
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"[league-runner] WARN: could not read meta.json for {match_id}: {exc}", file=sys.stderr)
        return None


def _determine_result(score_a: int, score_b: int) -> tuple[str, int, int]:
    """Return (result, score_a, score_b).

    result is 'team_a', 'team_b', or 'draw'. Draws are real outcomes — no coin-flip.
    """
    if score_a > score_b:
        return "team_a", score_a, score_b
    elif score_b > score_a:
        return "team_b", score_a, score_b
    else:
        return "draw", score_a, score_b


async def _run_league(args: argparse.Namespace) -> None:
    """Orchestrate all matchdays for the league."""
    league_id = args.league_id
    league_dir_path = Path(args.league_dir)
    config_path = Path(args.config)
    log_dir = Path(args.log_dir)
    data_dir = Path(args.data_dir)

    events_path = league_dir_path / "events.jsonl"
    if not events_path.exists():
        events_path.touch()

    try:
        league_data = read_league_json(league_dir_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"[league-runner] FATAL: cannot read league.json: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        _append_league_event(league_dir_path, "league-started", {"league_id": league_id})

        for matchday in league_data["matchdays"]:
            matchday_number = matchday["matchday_number"]
            match_count = len(matchday["matches"])

            _append_league_event(league_dir_path, "league-matchday-started", {
                "league_id": league_id,
                "matchday_number": matchday_number,
                "match_count": match_count,
            })
            print(f"[league-runner] matchday {matchday_number} starting ({match_count} matches)", flush=True)

            matchday["status"] = "running"
            write_league_json(league_dir_path, league_data)

            for match in matchday["matches"]:
                match_slot = match["match_slot"]
                match_id = match["match_id"]
                a_slot = match["team_a_slot"]
                b_slot = match["team_b_slot"]
                strategy_a = _slot_to_strategy_name(league_data, a_slot)
                strategy_b = _slot_to_strategy_name(league_data, b_slot)

                _append_league_event(league_dir_path, "league-match-started", {
                    "league_id": league_id,
                    "matchday_number": matchday_number,
                    "match_slot": match_slot,
                    "match_id": match_id,
                    "team_a": strategy_a,
                    "team_b": strategy_b,
                })
                print(f"[league-runner]   {match_slot}: {strategy_a} vs {strategy_b}", flush=True)

                match["status"] = "running"
                write_league_json(league_dir_path, league_data)

                match_failed = False
                strategy_a_path = None
                strategy_b_path = None
                try:
                    strategy_a_path = _resolve_strategy_path(data_dir, strategy_a or "")
                    strategy_b_path = _resolve_strategy_path(data_dir, strategy_b or "")
                except FileNotFoundError as exc:
                    print(f"[league-runner]   ERROR: strategy not found for {match_slot}: {exc}", file=sys.stderr)
                    match_failed = True

                meta = None
                if not match_failed and match_id is not None:
                    cmd = [
                        sys.executable, "-m", "src.cli", "run",
                        "--config", str(config_path),
                        "--season-length", "1",
                        "--match-id", match_id,
                        "--strategy-a", str(strategy_a_path),
                        "--strategy-b", str(strategy_b_path),
                        "--log-dir", str(log_dir),
                    ]
                    if args.global_defaults:
                        cmd.extend(["--global-defaults", args.global_defaults])
                    try:
                        result_proc = subprocess.run(cmd, check=False, timeout=600)
                        if result_proc.returncode != 0:
                            print(
                                f"[league-runner]   WARN: subprocess exited {result_proc.returncode} for {match_slot}",
                                file=sys.stderr,
                            )
                    except subprocess.TimeoutExpired:
                        print(f"[league-runner]   ERROR: {match_slot} timed out", file=sys.stderr)
                        match_failed = True

                # Always attempt meta read even after timeout — the match may have written
                # meta.json before the deadline. coin-flip fallback handles None.
                if match_id is not None:
                    meta = _read_meta_json(log_dir, match_id)

                if meta is not None:
                    final_score = meta.get("final_score", {})
                    sa = final_score.get("team_a", 0)
                    sb = final_score.get("team_b", 0)
                    result, sa, sb = _determine_result(sa, sb)
                else:
                    # Fallback: coin-flip when meta.json is missing (subprocess crash)
                    print(f"[league-runner]   WARN: no meta.json for {match_slot}, using coin-flip", file=sys.stderr)
                    seed = int(hashlib.md5((match_id or "").encode()).hexdigest()[:8], 16)
                    rng = random.Random(seed)
                    result = rng.choice(["team_a", "team_b"])
                    sa, sb = 0, 0

                match["status"] = "complete"
                match["result"] = result
                match["final_score"] = {"team_a": sa, "team_b": sb}

                _append_league_event(league_dir_path, "league-match-completed", {
                    "league_id": league_id,
                    "matchday_number": matchday_number,
                    "match_slot": match_slot,
                    "result": result,
                    "score": {"team_a": sa, "team_b": sb},
                })
                write_league_json(league_dir_path, league_data)
                print(f"[league-runner]   {match_slot} done: {result} ({sa}-{sb})", flush=True)

            # After all matches in matchday: recompute standings
            updated_standings = compute_standings(league_data)
            league_data["standings"] = updated_standings
            matchday["status"] = "complete"
            write_league_json(league_dir_path, league_data)

            _append_league_event(league_dir_path, "league-matchday-completed", {
                "league_id": league_id,
                "matchday_number": matchday_number,
                "standings": updated_standings,
            })
            print(f"[league-runner] matchday {matchday_number} complete", flush=True)

        # All matchdays done — set champion
        final_standings = league_data["standings"]
        champion = final_standings[0]["strategy_name"] if final_standings else None

        league_data["status"] = "complete"
        league_data["champion"] = champion
        league_data["completed_iso"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
        write_league_json(league_dir_path, league_data)

        _append_league_event(league_dir_path, "league-completed", {
            "league_id": league_id,
            "champion_strategy": champion,
            "standings": final_standings,
        })
        print(f"[league-runner] league {league_id} complete — champion: {champion}", flush=True)

    except Exception as exc:  # noqa: BLE001
        print(f"[league-runner] FATAL: {type(exc).__name__}: {exc}", file=sys.stderr)
        try:
            league_data["status"] = "errored"
            write_league_json(league_dir_path, league_data)
            _append_league_event(league_dir_path, "league-errored", {
                "league_id": league_id,
                "error": str(exc),
            })
        except Exception as write_exc:
            print(f"[league-runner] FATAL: could not write errored state: {write_exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Entry point for `agent-pitch league-run`."""
    parser = _build_parser()
    if len(sys.argv) >= 2 and sys.argv[1] == "league-run":
        sys.argv = [sys.argv[0]] + sys.argv[2:]
    args = parser.parse_args()
    asyncio.run(_run_league(args))


__all__ = ["main", "_run_league", "_determine_result", "_append_league_event"]
