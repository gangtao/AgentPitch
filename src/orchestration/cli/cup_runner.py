"""Cup Runner — single-elimination cup tournament orchestrator.

Spawned by POST /api/cups as a detached subprocess. Reads cup.json,
runs each match sequentially via `src.cli run`, writes results back to
cup.json, and emits SSE events to events.jsonl for the browser to consume.

CLI usage:
    python -m src.cli cup-run \\
      --cup-id <id> \\
      --cup-dir <path>   \\
      --config <path>    \\
      --log-dir <path>   \\
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


# ---------------------------------------------------------------------------
# Imports (only stdlib + src.cup_metadata + src.strategy_library)
# ---------------------------------------------------------------------------

from src.cup_metadata import read_cup_json, write_cup_json, propagate_winners


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-pitch cup-run",
        description="Orchestrate a single-elimination cup tournament.",
    )
    parser.add_argument("--cup-id", required=True, help="Cup identifier.")
    parser.add_argument(
        "--cup-dir",
        required=True,
        help="Path to data/cups/cup_<id>/ directory.",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to match config YAML.",
    )
    parser.add_argument(
        "--log-dir",
        required=True,
        help="Path to data/matches/ (where per-match dirs are written).",
    )
    parser.add_argument(
        "--data-dir",
        required=True,
        help="Path to data/ root (for strategy resolution).",
    )
    parser.add_argument(
        "--global-defaults",
        default=None,
        help="Path to global-defaults.yaml (overlaid onto each match config).",
    )
    return parser


def _append_cup_event(cup_dir: Path, event_name: str, data: dict) -> None:
    """Append a typed event line to events.jsonl in the cup directory.

    Mirrors the _append_event pattern used by the arena runner in
    src/orchestration/cli/__init__.py. Appends JSON lines consumed by the
    SSE endpoint so the browser receives live bracket updates.
    """
    line = json.dumps({"event": event_name, "data": data})
    events_path = cup_dir / "events.jsonl"
    with open(events_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()


def _resolve_strategy_path(data_dir: Path, name: str) -> Path:
    """Probe for strategy file in data_dir/strategies/, trying .py/.js/.rs.

    Returns the first match found. Raises FileNotFoundError if none exist.
    """
    for ext in [".py", ".js", ".rs"]:
        p = data_dir / "strategies" / f"{name}{ext}"
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Strategy '{name}' not found in {data_dir / 'strategies'}"
    )


def _slot_to_strategy_name(cup_data: dict, slot: int | None) -> str | None:
    """Look up the strategy name for a given team slot number."""
    if slot is None:
        return None
    for team in cup_data.get("teams", []):
        if team["slot"] == slot:
            return team["strategy_name"]
    return None


def _read_meta_json(log_dir: Path, match_id: str) -> dict | None:
    """Read meta.json from a completed match directory. Returns None on failure."""
    meta_path = log_dir / f"match_{match_id}" / "meta.json"
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"[cup-runner] WARN: could not read meta.json for {match_id}: {exc}", file=sys.stderr)
        return None


def _determine_winner(
    match: dict,
    score_a: int,
    score_b: int,
) -> tuple[str, int, bool]:
    """Determine match result, winner_slot, and tiebreak flag.

    Args:
        match: The match dict from cup.json (contains team_a_slot/team_b_slot).
        score_a: Goals scored by team_a.
        score_b: Goals scored by team_b.

    Returns:
        (result, winner_slot, tiebreak) where result is "team_a" or "team_b".
    """
    match_id = match["match_id"] or ""
    team_a_slot = match["team_a_slot"]
    team_b_slot = match["team_b_slot"]

    if score_a > score_b:
        return "team_a", team_a_slot, False
    elif score_b > score_a:
        return "team_b", team_b_slot, False
    else:
        # Tie: deterministic coin-flip seeded from match_id (hashlib for stable cross-process seed)
        seed = int(hashlib.md5(match_id.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)
        result = rng.choice(["team_a", "team_b"])
        winner_slot = team_a_slot if result == "team_a" else team_b_slot
        return result, winner_slot, True


def _winner_from_meta(match: dict, meta: dict) -> tuple:
    """Resolve a knockout result from meta.json (issue #83).

    Trusts the engine: a shootout winner takes precedence; otherwise the side
    leading the (possibly post-extra-time) final_score wins. Returns
    (result, winner_slot, decided_by). Assumes meta is decisive — knockout
    matches never finish level once extra time + shootout have run.
    """
    team_a_slot = match["team_a_slot"]
    team_b_slot = match["team_b_slot"]
    decided_by = meta.get("decided_by", "regulation")
    shootout = meta.get("shootout")

    if decided_by == "shootout" and isinstance(shootout, dict):
        result = shootout.get("winner", "team_a")
    else:
        fs = meta.get("final_score", {}) or {}
        result = "team_a" if fs.get("team_a", 0) >= fs.get("team_b", 0) else "team_b"
    winner_slot = team_a_slot if result == "team_a" else team_b_slot
    return result, winner_slot, decided_by


# ---------------------------------------------------------------------------
# Main cup orchestration logic
# ---------------------------------------------------------------------------


async def _run_cup(args: argparse.Namespace) -> None:
    """Orchestrate all rounds and matches for the cup."""
    # async for future parallel match dispatch; currently uses blocking subprocess.run
    cup_id = args.cup_id
    cup_dir_path = Path(args.cup_dir)
    config_path = Path(args.config)
    log_dir = Path(args.log_dir)
    data_dir = Path(args.data_dir)

    # Ensure events.jsonl exists (create empty if not present)
    events_path = cup_dir_path / "events.jsonl"
    if not events_path.exists():
        events_path.touch()

    # 1. Read cup.json
    try:
        cup_data = read_cup_json(cup_dir_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"[cup-runner] FATAL: cannot read cup.json: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        # 2. Process each round in order
        for round_data in cup_data["rounds"]:
            round_number = round_data["round_number"]
            round_name = round_data["round_name"]

            # a. Emit cup-round-started
            _append_cup_event(cup_dir_path, "cup-round-started", {
                "cup_id": cup_id,
                "round": round_number,
                "round_name": round_name,
            })
            print(f"[cup-runner] round {round_number} ({round_name}) starting", flush=True)

            # b. Update round status → "running"
            round_data["status"] = "running"
            write_cup_json(cup_dir_path, cup_data)

            # c. For each match in the round (sequential)
            for match in round_data["matches"]:
                match_slot = match["match_slot"]
                match_id = match.get("match_id")
                team_a_slot = match["team_a_slot"]
                team_b_slot = match["team_b_slot"]

                # Resolve strategy names from slot numbers
                strategy_a_name = _slot_to_strategy_name(cup_data, team_a_slot)
                strategy_b_name = _slot_to_strategy_name(cup_data, team_b_slot)

                # i. Emit cup-match-started
                _append_cup_event(cup_dir_path, "cup-match-started", {
                    "cup_id": cup_id,
                    "round": round_number,
                    "match_slot": match_slot,
                    "match_id": match_id,
                    "team_a": strategy_a_name,
                    "team_b": strategy_b_name,
                })
                print(
                    f"[cup-runner]   match {match_slot}: {strategy_a_name} vs {strategy_b_name} "
                    f"(match_id={match_id})",
                    flush=True,
                )

                # ii. Update match status → "running"
                match["status"] = "running"
                write_cup_json(cup_dir_path, cup_data)

                # iii. Resolve strategy file paths
                match_failed = False
                strategy_a_path: Path | None = None
                strategy_b_path: Path | None = None

                try:
                    strategy_a_path = _resolve_strategy_path(data_dir, strategy_a_name or "")
                    strategy_b_path = _resolve_strategy_path(data_dir, strategy_b_name or "")
                except FileNotFoundError as exc:
                    print(
                        f"[cup-runner]   ERROR: strategy file not found for {match_slot}: {exc}",
                        file=sys.stderr,
                    )
                    match_failed = True

                # iv. Spawn match subprocess
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
                        "--knockout",          # issue #83 — cups are single-elimination
                    ]
                    if args.global_defaults:
                        cmd.extend(["--global-defaults", args.global_defaults])
                    try:
                        result_proc = subprocess.run(
                            cmd,
                            check=False,
                            timeout=600,
                        )
                        if result_proc.returncode != 0:
                            print(
                                f"[cup-runner]   WARN: subprocess exited {result_proc.returncode} "
                                f"for {match_slot}",
                                file=sys.stderr,
                            )
                    except subprocess.TimeoutExpired:
                        print(
                            f"[cup-runner]   ERROR: match {match_slot} timed out after 600s",
                            file=sys.stderr,
                        )
                        match_failed = True

                # v. Read meta.json — always attempt after subprocess finishes (even on timeout,
                #    the match may have written meta.json before the deadline)
                if match_id is not None:
                    meta = _read_meta_json(log_dir, match_id)

                # vi. Determine winner
                decided_by = "regulation"
                shootout_meta = None
                if meta is not None:
                    final_score = meta.get("final_score", {})
                    score_a = final_score.get("team_a", 0)
                    score_b = final_score.get("team_b", 0)
                    # Issue #83 — knockout matches are decisive in meta.json
                    # (ET leader or shootout winner). Trust it; the coin-flip
                    # below is only for a missing/unreadable meta.json.
                    result, winner_slot, decided_by = _winner_from_meta(match, meta)
                    shootout_meta = meta.get("shootout")
                    tiebreak = decided_by != "regulation"
                else:
                    # No meta.json: coin-flip tiebreak
                    print(
                        f"[cup-runner]   WARN: no meta.json for {match_slot}, using coin-flip",
                        file=sys.stderr,
                    )
                    match_id_str = match.get("match_id") or ""
                    seed = int(hashlib.md5(match_id_str.encode()).hexdigest()[:8], 16)
                    rng = random.Random(seed)
                    result = rng.choice(["team_a", "team_b"])
                    winner_slot = team_a_slot if result == "team_a" else team_b_slot
                    tiebreak = True
                    decided_by = "coin_flip"
                    shootout_meta = None
                    score_a, score_b = 0, 0

                winner_strategy = _slot_to_strategy_name(cup_data, winner_slot)

                # vii. Update match in cup.json
                match["status"] = "complete"
                match["result"] = result
                match["winner_slot"] = winner_slot
                match["final_score"] = {"team_a": score_a, "team_b": score_b}
                match["tiebreak"] = tiebreak
                match["decided_by"] = decided_by
                match["shootout"] = shootout_meta

                # viii. Emit cup-match-completed
                _append_cup_event(cup_dir_path, "cup-match-completed", {
                    "cup_id": cup_id,
                    "round": round_number,
                    "match_slot": match_slot,
                    "winner_slot": winner_slot,
                    "winner_strategy": winner_strategy,
                    "score": {"team_a": score_a, "team_b": score_b},
                    "tiebreak": tiebreak,
                    "decided_by": decided_by,
                    "shootout": shootout_meta,
                })
                write_cup_json(cup_dir_path, cup_data)
                print(
                    f"[cup-runner]   match {match_slot} complete: "
                    f"winner={winner_strategy} (slot {winner_slot}) "
                    f"score={score_a}-{score_b} tiebreak={tiebreak}",
                    flush=True,
                )

            # d. Mark round status = "complete"
            round_data["status"] = "complete"

            # e. Propagate winners to next round
            propagate_winners(cup_data, round_number)

            # f. Write cup.json
            write_cup_json(cup_dir_path, cup_data)

            # g. Emit cup-round-completed
            _append_cup_event(cup_dir_path, "cup-round-completed", {
                "cup_id": cup_id,
                "round": round_number,
            })
            print(f"[cup-runner] round {round_number} ({round_name}) complete", flush=True)

        # 3. Set cup.json status="complete"
        # Determine the overall cup winner from the final round's single match
        final_round = cup_data["rounds"][-1]
        final_match = final_round["matches"][0] if final_round["matches"] else None
        overall_winner_slot = final_match["winner_slot"] if final_match else None
        overall_winner_strategy = _slot_to_strategy_name(cup_data, overall_winner_slot)

        cup_data["status"] = "complete"
        cup_data["winner"] = overall_winner_strategy
        cup_data["completed_iso"] = _dt.datetime.now(_dt.timezone.utc).isoformat()

        # 4. Write cup.json
        write_cup_json(cup_dir_path, cup_data)

        # 5. Emit cup-completed
        _append_cup_event(cup_dir_path, "cup-completed", {
            "cup_id": cup_id,
            "winner_slot": overall_winner_slot,
            "winner_strategy": overall_winner_strategy,
        })
        print(
            f"[cup-runner] cup {cup_id} complete — winner: {overall_winner_strategy} "
            f"(slot {overall_winner_slot})",
            flush=True,
        )

    except Exception as exc:  # noqa: BLE001
        # Unrecoverable error: set errored status, emit event, exit 1
        print(f"[cup-runner] FATAL: unrecoverable error: {type(exc).__name__}: {exc}", file=sys.stderr)
        try:
            cup_data["status"] = "errored"
            write_cup_json(cup_dir_path, cup_data)
            _append_cup_event(cup_dir_path, "cup-errored", {
                "cup_id": cup_id,
                "error": str(exc),
            })
        except Exception as write_exc:
            print(f"[cup-runner] FATAL: could not write errored state: {write_exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Entry point for `agent-pitch cup-run`."""
    parser = _build_parser()
    # Strip the 'cup-run' subcommand word if dispatched via src.cli
    # (sys.argv will be ['<prog>', 'cup-run', ...] — we skip argv[0] and argv[1])
    if len(sys.argv) >= 2 and sys.argv[1] == "cup-run":
        sys.argv = [sys.argv[0]] + sys.argv[2:]
    args = parser.parse_args()
    asyncio.run(_run_cup(args))


__all__ = ["main", "_run_cup", "_build_parser", "_append_cup_event", "_determine_winner", "_winner_from_meta"]
