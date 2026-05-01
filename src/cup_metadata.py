"""Cup metadata — core data model and bracket logic for the Strategy Cup feature.

cup.json schema (written inside each cup directory):
{
  "cup_id": "<id>",
  "name": "<display name>",
  "status": "running" | "complete" | "errored",
  "config_name": "<match config name>",
  "bracket_size": 4 | 8 | 16 | 32,
  "created_iso": "<ISO timestamp>",
  "completed_iso": null,
  "winner": null | "<strategy_name>",
  "teams": [
    {"slot": 1, "strategy_name": "<name>"},
    ...
  ],
  "rounds": [
    {
      "round_number": 1,
      "round_name": "Semi-Finals",
      "status": "pending" | "running" | "complete",
      "matches": [
        {
          "match_slot": "R1M1",
          "match_id": "<cup_id>-R1M1" | null,
          "team_a_slot": 1 | null,
          "team_b_slot": 4 | null,
          "status": "pending" | "running" | "complete",
          "result": "team_a" | "team_b" | null,
          "winner_slot": 1 | null,
          "final_score": {"team_a": N, "team_b": N} | null,
          "tiebreak": false
        }
      ]
    }
  ]
}

Directory layout:
  <cups_dir>/
    cup_<cup_id>/
      cup.json
      matches/          (one subdir per match, following standard match layout)
"""
from __future__ import annotations

import json
import os
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROUND_NAMES: dict[int, dict[int, str]] = {
    32: {1: "Round of 32", 2: "Round of 16", 3: "Quarter-Finals", 4: "Semi-Finals", 5: "Final"},
    16: {1: "Round of 16", 2: "Quarter-Finals", 3: "Semi-Finals", 4: "Final"},
     8: {1: "Quarter-Finals", 2: "Semi-Finals", 3: "Final"},
     4: {1: "Semi-Finals", 2: "Final"},
}

CUP_DIR_PREFIX = "cup_"

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def cup_dir(cups_dir: Path, cup_id: str) -> Path:
    """Return the cup directory path: cups_dir / 'cup_<cup_id>'."""
    return cups_dir / f"{CUP_DIR_PREFIX}{cup_id}"


# ---------------------------------------------------------------------------
# I/O (mirrors series_metadata.py patterns exactly)
# ---------------------------------------------------------------------------


def read_cup_json(cup_d: Path) -> dict:
    """Read and return cup.json as dict.

    Raises:
        FileNotFoundError: if cup.json is absent.
        json.JSONDecodeError: if the file is malformed.
    """
    path = cup_d / "cup.json"
    return json.loads(path.read_text(encoding="utf-8"))


def write_cup_json(cup_d: Path, data: dict) -> None:
    """Atomically write cup.json via os.replace.

    Writes to a temporary file first, then renames to the target path so
    concurrent readers never see a partial write.
    """
    target = cup_d / "cup.json"
    tmp = cup_d / "cup.json.tmp"
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, target)


def list_cups(cups_dir: Path) -> list[dict]:
    """Scan cups_dir for cup_* subdirectories, return summaries sorted by created_iso desc.

    Each returned dict contains summary fields from cup.json:
    cup_id, name, status, config_name, bracket_size, created_iso, completed_iso, winner.
    Directories missing or with malformed cup.json are silently skipped.

    Returns an empty list if cups_dir does not exist.
    """
    if not cups_dir.exists():
        return []

    results = []
    try:
        for entry in cups_dir.iterdir():
            if not entry.is_dir():
                continue
            if not entry.name.startswith(CUP_DIR_PREFIX):
                continue
            try:
                data = read_cup_json(entry)
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                continue

            summary = {
                "cup_id":       data.get("cup_id", entry.name.removeprefix(CUP_DIR_PREFIX)),
                "name":         data.get("name", ""),
                "status":       data.get("status", ""),
                "config_name":  data.get("config_name", ""),
                "bracket_size": data.get("bracket_size", 0),
                "created_iso":  data.get("created_iso", ""),
                "completed_iso": data.get("completed_iso"),
                "winner":       data.get("winner"),
            }
            results.append(summary)
    except (OSError, PermissionError):
        return []

    results.sort(key=lambda x: x["created_iso"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Bracket generation
# ---------------------------------------------------------------------------


def _bracket_round_count(bracket_size: int) -> int:
    """Return the number of rounds for a given bracket size."""
    # bracket_size must be a power of 2 (4, 8, 16, 32)
    count = 0
    n = bracket_size
    while n > 1:
        n //= 2
        count += 1
    return count


def _seeded_pairings(n: int) -> list[tuple[int, int]]:
    """Return standard single-elimination seeded pairings for n teams.

    Uses the standard bracket seeding algorithm:
    - For 4:  (1,4), (2,3)
    - For 8:  (1,8), (4,5), (3,6), (2,7)
    - For 16: (1,16), (8,9), (7,10), (6,11), (5,12), (4,13), (3,14), (2,15)
    - For 32: similar pattern

    Top seeds in match order: seed 1 first, then seeds n/2 down to 2.
    Each top seed s is paired with its complement n+1-s.
    All slots 1..n appear exactly once.
    """
    slots = _build_slots(n)
    pairs = []
    for i in range(0, len(slots), 2):
        pairs.append((slots[i], slots[i + 1]))
    return pairs


def _build_slots(n: int) -> list[int]:
    """Build the ordered seed list for a bracket of size n.

    Top-half seeds are ordered: [1, n/2, n/2-1, ..., 2]
    (seed 1 first, then seeds from n/2 down to 2).
    Each top seed s is paired with its complement n+1-s (adjacent in the list).

    This gives the standard single-elimination seeding where:
    - The top two seeds can only meet in the Final
    - Seed 1 vs seed n is always Match 1
    """
    # Top half seeds in bracket order: 1, then n//2 down to 2
    top_seeds = [1] + list(reversed(range(2, n // 2 + 1)))
    result: list[int] = []
    for s in top_seeds:
        result.append(s)
        result.append(n + 1 - s)
    return result


def generate_bracket(bracket_size: int, strategies: list[str], cup_id: str) -> dict:
    """Build initial cup.json dict from shuffled strategies.

    Shuffles strategies randomly seeded from cup_id for reproducibility.
    Assigns slot numbers 1..N.
    Builds round 1 with all match slots filled (seed i vs seed N+1-i).
    Future rounds have match slots with team_a_slot=None, team_b_slot=None, match_id=None.

    Args:
        bracket_size: Number of teams (4, 8, 16, or 32).
        strategies: List of strategy names to seed into the bracket.
        cup_id: Unique cup identifier (used for seeding RNG and match IDs).

    Returns:
        Complete cup.json dict (status="running", winner=None).
        Note: the returned dict has `name=''`, `config_name=''`, and `created_iso=None`.
        Caller must set these fields before writing to disk.

    Raises:
        ValueError: if len(strategies) != bracket_size or bracket_size not supported.
    """
    if bracket_size not in ROUND_NAMES:
        raise ValueError(f"Unsupported bracket_size {bracket_size}; must be one of {sorted(ROUND_NAMES)}")
    if len(strategies) != bracket_size:
        raise ValueError(
            f"strategies list length ({len(strategies)}) must equal bracket_size ({bracket_size})"
        )

    # Shuffle strategies with deterministic seed derived from cup_id
    rng = random.Random(cup_id)
    shuffled = list(strategies)
    rng.shuffle(shuffled)

    # Build teams array: slot 1..N maps to shuffled strategy names
    teams = [{"slot": i + 1, "strategy_name": shuffled[i]} for i in range(bracket_size)]

    # Compute seeded pairings for round 1
    pairings = _seeded_pairings(bracket_size)

    num_rounds = _bracket_round_count(bracket_size)
    round_names_map = ROUND_NAMES[bracket_size]

    rounds = []
    for round_num in range(1, num_rounds + 1):
        if round_num == 1:
            matches = []
            for match_idx, (seed_a, seed_b) in enumerate(pairings, start=1):
                match_slot = f"R{round_num}M{match_idx}"
                matches.append({
                    "match_slot": match_slot,
                    "match_id": f"{cup_id}-{match_slot}",
                    "team_a_slot": seed_a,
                    "team_b_slot": seed_b,
                    "status": "pending",
                    "result": None,
                    "winner_slot": None,
                    "final_score": None,
                    "tiebreak": False,
                })
        else:
            # Future rounds: number of matches = bracket_size / 2^round_num
            num_matches = bracket_size // (2 ** round_num)
            matches = []
            for match_idx in range(1, num_matches + 1):
                match_slot = f"R{round_num}M{match_idx}"
                matches.append({
                    "match_slot": match_slot,
                    "match_id": None,
                    "team_a_slot": None,
                    "team_b_slot": None,
                    "status": "pending",
                    "result": None,
                    "winner_slot": None,
                    "final_score": None,
                    "tiebreak": False,
                })

        rounds.append({
            "round_number": round_num,
            "round_name": round_names_map[round_num],
            "status": "pending",
            "matches": matches,
        })

    return {
        "cup_id": cup_id,
        "name": "",
        "status": "running",
        "config_name": "",
        "bracket_size": bracket_size,
        "created_iso": None,
        "completed_iso": None,
        "winner": None,
        "teams": teams,
        "rounds": rounds,
    }


# ---------------------------------------------------------------------------
# Winner propagation
# ---------------------------------------------------------------------------


def propagate_winners(cup_data: dict, completed_round: int) -> dict:
    """After round R completes, fill team_a_slot/team_b_slot in round R+1 matches.

    Winner of R-M(2k-1) becomes team_a of (R+1)-M(k).
    Winner of R-M(2k) becomes team_b of (R+1)-M(k).
    Also fills match_id for next-round matches using pattern: {cup_id}-R{r}M{m}.

    Idempotent: only sets slots that are currently None.

    Args:
        cup_data: The full cup.json dict (modified in-place).
        completed_round: The round number that just completed (1-indexed).

    Returns:
        Modified cup_data dict (caller must write to disk).
    """
    cup_id = cup_data["cup_id"]
    rounds = cup_data["rounds"]

    # Find the completed round and next round by round_number
    completed_round_data = None
    next_round_data = None
    for r in rounds:
        if r["round_number"] == completed_round:
            completed_round_data = r
        elif r["round_number"] == completed_round + 1:
            next_round_data = r

    if completed_round_data is None or next_round_data is None:
        # No next round (this was the final), nothing to propagate
        return cup_data

    completed_matches = completed_round_data["matches"]
    next_matches = next_round_data["matches"]

    # Pair completed matches two-by-two into next-round matches
    # Match k in next round gets winner from matches 2k-1 and 2k of completed round
    for next_match_idx, next_match in enumerate(next_matches):
        k = next_match_idx  # 0-indexed
        src_match_a = completed_matches[2 * k]       # 2k-1 (0-indexed: 2k)
        src_match_b = completed_matches[2 * k + 1]   # 2k   (0-indexed: 2k+1)

        # Fill team_a_slot from winner of match 2k-1
        if next_match["team_a_slot"] is None:
            winner_a = src_match_a.get("winner_slot")
            if winner_a is not None:
                next_match["team_a_slot"] = winner_a

        # Fill team_b_slot from winner of match 2k
        if next_match["team_b_slot"] is None:
            winner_b = src_match_b.get("winner_slot")
            if winner_b is not None:
                next_match["team_b_slot"] = winner_b

        # Fill match_id only once both slots are known and match_id is still None
        if next_match["match_id"] is None:
            if next_match["team_a_slot"] is not None and next_match["team_b_slot"] is not None:
                match_slot = next_match["match_slot"]
                next_match["match_id"] = f"{cup_id}-{match_slot}"

    return cup_data


__all__ = [
    "ROUND_NAMES",
    "CUP_DIR_PREFIX",
    "cup_dir",
    "read_cup_json",
    "write_cup_json",
    "list_cups",
    "generate_bracket",
    "propagate_winners",
]
