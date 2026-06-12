"""Match Log System - Core schemas and logging infrastructure.

This module implements the foundational schemas for match logging:
- TickRecord: Immutable per-tick snapshot of match state
- ActionRecord: Immutable per-player action within a tick
- MatchLog: Central logging coordinator with validation and state management

Design Document: design/gdd/match-log-system.md
Architecture: docs/architecture/architecture.md (MLS section)
Story: production/epics/match-log-system/story-001-tickrecord-schemas-construction.md
"""

from __future__ import annotations
import json
import logging
import os
import re
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

# Tuning knob (default; loaded from config in production)
HISTORY_MAX_TICKS = 10

# Tuning knobs (defaults; loaded from config in production)
MLS_LOG_DIR = "logs/"
MLS_STREAM_WRITE = True

# Module-level constant (cross-system from System Prompt Builder GDD)
SPB_MAX_KEY_EVENTS = 5

# Key event selection tuning knobs
MLS_KEY_EVENT_RECENCY_BIAS = True
_NON_GOAL_PRIORITY = ["fallback", "tackle_success", "shot_on_target", "pass_interception"]

# Match state machine
MatchLogState = Literal["LIVE", "FINALIZED"]

# Validation regex for match_id (path-injection guard per AC-MLS-15)
_MATCH_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

logger = logging.getLogger(__name__)


class MatchAlreadyFinalizedError(Exception):
    """Raised when a record_* method is called after finalize()."""


class MatchNotFinalizedError(Exception):
    """Raised when generate_summary() is called before finalize()."""


@dataclass(frozen=True)
class ActionRecord:
    """Immutable per-player action record within a tick.

    `details` schema varies by action type — see GDD Rule 9.
    """
    player_id: str
    team: str
    action: str          # "move" | "pass" | "shoot" | "tackle" | "hold"
    result: str          # "success" | "fail" | "goal" | "save" | "out_of_bounds"
    details: dict[str, Any]


@dataclass(frozen=True)
class TickRecord:
    """Immutable per-tick snapshot — the simulation's authoritative record.

    Frozen to prevent mid-tick mutation. Constructed by Tick Engine after action
    resolution; passed to MatchLog.record_tick().
    """
    tick: int
    ball_position: tuple[float, float]
    ball_possession: str | None       # "team_a" | "team_b" | None
    score: dict[str, int]             # {"team_a": int, "team_b": int}
    player_positions: dict[str, list[float]]  # {player_id: [x, y]} per Field Renderer cross-GDD amendment
    actions: list[ActionRecord]       # 10 entries (one per player)
    is_key_event: bool
    event_type: str | None            # "goal" | "half_time" | "kick_off" | "fallback" | "exception" | "out_of_bounds" | None


class MatchLog:
    """The simulation's authoritative record. Single instance per match.

    Owned by Tick Engine. Transitions LIVE → FINALIZED on finalize() call.
    Per-tick recording in Story 002. State machine in Story 003.
    """

    def __init__(self, match_id: str) -> None:
        """Initialise an empty MatchLog in LIVE state.

        Args:
            match_id: identifier matching [a-zA-Z0-9_-]+ (AC-MLS-15 path-injection guard).

        Raises:
            ValueError: if match_id contains path separators or special characters.
        """
        if not _MATCH_ID_PATTERN.fullmatch(match_id):
            raise ValueError(
                f"match_id {match_id!r} contains invalid characters; "
                f"must match [a-zA-Z0-9_-]+"
            )
        self.match_id = match_id

        # Internal data structures (GDD Rule 3)
        self._ticks: list[TickRecord] = []
        self._key_events: list[int] = []         # tick indices where is_key_event == True
        self._history_deque: deque[TickRecord] = deque(maxlen=HISTORY_MAX_TICKS)
        self._fallback_events: list[Any] = []    # FallbackEvent shape — typed in Fallback Handler epic
        self._phase_transitions: list[tuple[int, str, str]] = []  # (tick, old_phase, new_phase)
        # Optional team rosters for meta.json — populated by TickEngine via
        # set_strategies_meta(). Per-team strategy provenance recorded per-match.
        self._strategies_meta: dict | None = None
        # Optional per-team strategy source code, populated by TickEngine via
        # set_strategy_codes(). When present, serialize() drops a snapshot at
        # <match_dir>/strategy_<team>.py so the API viewer can serve the exact
        # code that ran in this match (instead of whatever current.py points
        # at globally).
        self._strategy_codes: dict[str, str] | None = None
        self._strategy_languages: dict[str, str] | None = None
        # set_teams_meta(). Used by the browser to display "A #4" instead of
        # the raw player_id. None means rosters weren't published; the UI
        # falls back to deriving numbers from the player_id index.
        self._teams_meta: dict | None = None
        # Optional match-clock parameters (tick_rate, duration_minutes,
        # total_ticks). Published by TickEngine via set_match_meta(). The
        # browser reads these to render MM:SS broadcast-style. None means
        # not published; the UI falls back to a hardcoded tick_rate=10.
        self._match_meta: dict | None = None

        # Per-tick performance data. Each entry is a dict written as a line
        # in perf.jsonl alongside events.jsonl. Populated by TickEngine via
        # record_tick_perf() on each active tick (pause ticks are omitted).
        self._perf_ticks: list[dict] = []

        # State machine (Story 003)
        self._state: MatchLogState = "LIVE"

    def record_tick(self, tick_record: TickRecord) -> None:
        """Append a TickRecord to the match log. Append-only, monotonic.

        EC-MLS-25: tick must be strictly greater than the previous tick.
        Updates _history_deque (Story 004 reads from this).
        Updates _key_events index when tick_record.is_key_event is True.

        Raises:
            ValueError: if tick_record.tick is not strictly greater than the previous tick.
            MatchAlreadyFinalizedError: if state is FINALIZED.
        """
        if self._state != "LIVE":
            raise MatchAlreadyFinalizedError(
                f"record_tick called on FINALIZED match {self.match_id!r}"
            )

        # Monotonicity check (EC-MLS-25)
        if self._ticks:
            prev_tick = self._ticks[-1].tick
            if tick_record.tick <= prev_tick:
                raise ValueError(
                    f"TickRecord tick {tick_record.tick} is non-monotonic: "
                    f"expected > {prev_tick}, got {tick_record.tick}"
                )

        self._ticks.append(tick_record)
        self._history_deque.append(tick_record)

        # Key event index update
        if tick_record.is_key_event:
            self._key_events.append(len(self._ticks) - 1)

    def record_fallback(self, fallback_event: Any) -> None:
        """Append a FallbackEvent to the match log.

        Order-independent with record_tick (EC-MLS-07).
        """
        if self._state != "LIVE":
            raise MatchAlreadyFinalizedError(
                f"record_fallback called on FINALIZED match {self.match_id!r}"
            )
        self._fallback_events.append(fallback_event)

    def record_phase_transition(
        self, tick: int, old_phase: str, new_phase: str
    ) -> None:
        """Append a phase transition record. Stored separately from TickRecord."""
        if self._state != "LIVE":
            raise MatchAlreadyFinalizedError(
                f"record_phase_transition called on FINALIZED match {self.match_id!r}"
            )
        self._phase_transitions.append((tick, old_phase, new_phase))

    def record_tick_perf(self, perf: dict) -> None:
        """Append a per-tick performance record.

        Called once per active tick by TickEngine after are.resolve_tick().
        Silently drops records when FINALIZED so compile-phase overhead
        (tick=0 sandbox compile) doesn't cause state-machine violations.

        Expected shape:
          {
            "tick": int,
            "tick_total_ms": float,   # wall-clock for entire active tick
            "snapshot_ms": float,     # Phase 1 snapshot build time
            "callbacks_ms": float,    # Phase 2+ ARE resolution time
            "players": {              # per-player sandbox timing
              "<player_id>": {
                "lang": str,          # "python" | "javascript" | "rust"
                "exec_ms": float,     # SandboxResult.execution_time_ms
              }, ...
            }
          }
        """
        if self._state != "LIVE":
            return
        self._perf_ticks.append(perf)

    def finalize(self, final_state: dict) -> None:
        """Transition LIVE → FINALIZED. Triggered by Tick Engine at FULL_TIME.

        After finalize:
        - record_* methods raise MatchAlreadyFinalizedError (already enforced in Story 002)
        - generate_summary() becomes available (Story 006 — this story stubs it)
        - Serialization to disk triggered (Story 007 — separate call from Tick Engine)

        EC-MLS-12: second call is a no-op + WARNING. Data not corrupted.
        EC-MLS-11: finalize with no ticks is valid; summary still producible.

        Args:
            final_state: dict from gsm.get_final_state() — populates MatchMetadata.final_score
                         (Story 006 reads this for the summary template)
        """
        if self._state == "FINALIZED":
            logger.warning(
                "finalize called on already-FINALIZED match %s — no-op",
                self.match_id,
            )
            return

        self._final_state = final_state
        self._state = "FINALIZED"

    def generate_summary(self, max_tokens: int = 300) -> str:
        """Produce structured-text match summary for the Post-Match Evolution Pipeline.

        EC-MLS-10: raises MatchNotFinalizedError if state is LIVE.
        EC-MLS-22: KEY EVENTS truncated from least-recent first if over max_tokens.

        Args:
            max_tokens: target token budget. Token estimation: len(text) / 4.

        Returns:
            Structured-text report per GDD Rule 7 template.
        """
        if self._state != "FINALIZED":
            raise MatchNotFinalizedError(
                f"generate_summary called on LIVE match {self.match_id!r} — call finalize() first"
            )

        # --- Compute formulas ---
        T = len(self._ticks)
        team_a_stats = self._compute_team_stats("team_a", T)
        team_b_stats = self._compute_team_stats("team_b", T)

        # --- Render template ---
        final_score = self._final_state.get("final_score", {"team_a": 0, "team_b": 0})
        final_tick = self._ticks[-1].tick if self._ticks else 0

        lines = []
        lines.append(f"MATCH SUMMARY | Tick {final_tick}")
        lines.append("")
        lines.append(f"RESULT: Team A {final_score['team_a']} – {final_score['team_b']} Team B")
        lines.append("")
        lines.append(f"TEAM A:")
        lines.extend(self._render_team_section(team_a_stats))
        lines.append("")
        lines.append(f"TEAM B:")
        lines.extend(self._render_team_section(team_b_stats))
        lines.append("")
        lines.append(f"KEY EVENTS (up to {SPB_MAX_KEY_EVENTS}):")

        # Render key events (with truncation per EC-MLS-22)
        key_event_indices = self.select_key_events(max_events=SPB_MAX_KEY_EVENTS)
        if not key_event_indices:
            lines.append("  (none)")
        else:
            for i in key_event_indices:
                lines.append(f"  {self._render_key_event_line(i)}")

        rendered = "\n".join(lines)

        # EC-MLS-22: truncate KEY EVENTS if over budget
        rendered = self._truncate_to_token_budget(rendered, max_tokens)
        return rendered

    def _compute_team_stats(self, team: str, T: int) -> dict:
        """Compute Formula 2/3/4 stats for one team. Handles all edge cases."""
        # Formula 3: Failure rate
        F_team = sum(1 for fe in self._fallback_events if getattr(fe, "team", None) == team
                     or (isinstance(fe, dict) and fe.get("team") == team))
        if T == 0:
            failure_rate = "N/A"  # EC-MLS-01, EC-MLS-11
        else:
            failure_rate = (F_team / T) * 100.0

        # Formula 2: Possession (computed from _ticks ball_possession field)
        C_total = sum(1 for tr in self._ticks if tr.ball_possession is not None)
        C_team = sum(1 for tr in self._ticks if tr.ball_possession == team)
        if C_total == 0:
            possession = "no_possession_data"  # EC-MLS-10
        elif C_team > C_total:
            possession = "possession_data_anomaly"  # EC-MLS-20
        else:
            possession = (C_team / C_total) * 100.0

        # Formula 4: Pass success rate
        A_pass = 0
        S_pass = 0
        for tr in self._ticks:
            for ar in tr.actions:
                if ar.team == team and ar.action == "pass":
                    A_pass += 1
                    if ar.result == "success":
                        S_pass += 1
        if A_pass == 0:
            pass_success = "N/A"  # EC-MLS-11
        elif S_pass > A_pass:
            pass_success = "anomaly"  # EC-MLS-19 — sentinel; renderer formats specially
        else:
            pass_success = (S_pass / A_pass) * 100.0

        # Tally other stats
        shots = sum(1 for tr in self._ticks for ar in tr.actions if ar.team == team and ar.action == "shoot")
        goals = sum(1 for tr in self._ticks for ar in tr.actions if ar.team == team and ar.action == "shoot" and ar.result == "goal")
        on_target = sum(1 for tr in self._ticks for ar in tr.actions if ar.team == team and ar.action == "shoot" and ar.result in ("goal", "save"))
        tackles = sum(1 for tr in self._ticks for ar in tr.actions if ar.team == team and ar.action == "tackle")
        tackle_success_count = sum(1 for tr in self._ticks for ar in tr.actions if ar.team == team and ar.action == "tackle" and ar.result == "success")
        # Issue #31: offsides conceded by this team. Keyed off the offender's
        # side-channel record (details.offside_offence) so attribution holds
        # regardless of action-name casing conventions.
        offsides = sum(
            1 for tr in self._ticks for ar in tr.actions
            if ar.team == team and ar.details.get("offside_offence")
        )

        return {
            "failure_rate": failure_rate,
            "F_team": F_team,
            "possession": possession,
            "C_team": C_team,
            "A_pass": A_pass,
            "S_pass": S_pass,
            "pass_success": pass_success,
            "shots": shots,
            "goals": goals,
            "on_target": on_target,
            "tackles": tackles,
            "tackle_success": tackle_success_count,
            "offsides": offsides,
        }

    def _render_team_section(self, stats: dict) -> list[str]:
        """Render the per-team stats lines."""
        lines = []
        if stats["pass_success"] == "N/A":
            lines.append(f"  Passes: {stats['A_pass']} attempted, {stats['S_pass']} success (N/A)")
        elif stats["pass_success"] == "anomaly":
            # EC-MLS-19 anomaly
            lines.append(f"  Passes: {stats['A_pass']} attempted, {stats['S_pass']} success (100.0% — data anomaly: success count exceeded attempt count)")
        else:
            lines.append(f"  Passes: {stats['A_pass']} attempted, {stats['S_pass']} success ({stats['pass_success']:.1f}%)")

        lines.append(f"  Shots: {stats['shots']} attempted, {stats['goals']} goals, {stats['on_target']} on target")
        lines.append(f"  Tackles: {stats['tackles']} attempted, {stats['tackle_success']} success")
        # Issue #31: free kicks conceded to the opponent — a high count means
        # attackers are caught beyond the second-last defender at pass moments.
        lines.append(f"  Offsides: {stats.get('offsides', 0)} (free kicks conceded)")

        if stats["possession"] == "no_possession_data":
            lines.append(f"  Possession: no_possession_data")
        elif stats["possession"] == "possession_data_anomaly":
            lines.append(f"  Possession: possession_data_anomaly (raw: C_team={stats.get('C_team', 0)})")
        else:
            lines.append(f"  Possession: {stats['possession']:.1f}%")

        if stats["failure_rate"] == "N/A":
            lines.append(f"  Callback failures: {stats['F_team']} (N/A)")
        else:
            lines.append(f"  Callback failures: {stats['F_team']} ({stats['failure_rate']:.1f}%)")
        return lines

    def _render_key_event_line(self, tick_index: int) -> str:
        """Render a single one-line description for a key event."""
        tr = self._ticks[tick_index]
        et = tr.event_type or "key"
        if et == "goal":
            return f"[{tr.tick}] goal: scored. Score: {tr.score['team_a']}–{tr.score['team_b']}."
        elif et == "fallback":
            return f"[{tr.tick}] fallback: callback substituted."
        elif et == "tackle_success":
            return f"[{tr.tick}] tackle_success: ball won."
        elif et == "shot_on_target":
            return f"[{tr.tick}] shot_on_target: saved by GK."
        elif et == "pass_interception":
            return f"[{tr.tick}] pass_interception: ball stolen mid-pass."
        elif et == "offside":
            # Issue #31: attribute the offence so PMEP can see WHO was
            # caught offside and which team got the free kick.
            for ar in tr.actions:
                d = ar.details if isinstance(ar.details, dict) else {}
                if d.get("offside"):
                    offender = d.get("offender_id", "?")
                    to_team = d.get("restart_team", "?")
                    return (f"[{tr.tick}] offside: {offender} flagged — "
                            f"free kick to {to_team}.")
            return f"[{tr.tick}] offside: free kick conceded."
        else:
            return f"[{tr.tick}] {et}"

    def _truncate_to_token_budget(self, text: str, max_tokens: int) -> str:
        """EC-MLS-22: truncate KEY EVENTS from least-recent first if over budget."""
        estimated = len(text) / 4
        if estimated <= max_tokens:
            return text

        marker = f"KEY EVENTS (up to {SPB_MAX_KEY_EVENTS}):"
        if marker not in text:
            return text  # nothing to truncate
        head, _, events_section = text.partition(marker)
        event_lines = [line for line in events_section.split("\n") if line.startswith("  ")]

        # Truncate events from least-recent (first in chronological-sorted output)
        while event_lines and (len(head + marker + "\n" + "\n".join(event_lines)) / 4) > max_tokens:
            event_lines.pop(0)

        result = head + marker + ("\n" + "\n".join(event_lines) if event_lines else "")
        if not event_lines:
            result += "\n  (key events omitted: summary too long)"
        return result

    def get_history(self) -> list[dict]:
        """Return the rolling history window as ASCI Rule 7 schema dicts.

        Available in both LIVE and FINALIZED states. Tick Engine calls this once
        per tick per player to populate the third argument to decide() callbacks.

        Returns:
            list[dict]: last HISTORY_MAX_TICKS TickRecords as ASCI Rule 7 dicts,
                        oldest first. Empty list if no ticks recorded yet (EC-MLS-13).

        Note: Internal TickRecord fields (ball_possession, is_key_event, event_type,
        player_positions) are stripped per EC-MLS-24. Only ASCI-schema fields are
        emitted — preserves the cross-system contract.
        """
        return [self._tick_record_to_history_dict(tr) for tr in self._history_deque]

    @staticmethod
    def _tick_record_to_history_dict(tr: TickRecord) -> dict:
        """Convert a TickRecord to the ASCI Rule 7 history dict schema.

        ASCI Rule 7 schema:
        - tick: int
        - ball_position: [float, float]
        - score: {"team_a": int, "team_b": int}
        - actions: [{player_id, team, action, result, details}, ...]

        Excluded: ball_possession, is_key_event, event_type, player_positions.
        """
        return {
            "tick": tr.tick,
            "ball_position": list(tr.ball_position),  # tuple → list for JSON-friendly
            "score": dict(tr.score),                   # fresh dict
            "actions": [
                {
                    "player_id": ar.player_id,
                    "team": ar.team,
                    "action": ar.action,
                    "result": ar.result,
                    "details": dict(ar.details),       # fresh dict so callbacks can't mutate
                }
                for ar in tr.actions
            ],
        }

    def select_key_events(self, max_events: int) -> list[int]:
        """Select tick indices for the KEY EVENTS section of generate_summary().

        Goals are cap-exempt — all goal indices always included (Rule 6).
        Non-goal events selected per MLS_KEY_EVENT_RECENCY_BIAS:
          - True (default): by tick number descending (most recent first)
          - False: by event_type priority order (fallback > tackle_success > ...)

        Args:
            max_events: maximum non-goal events to include (SPB_MAX_KEY_EVENTS).
                        Goals are NOT counted against this cap.

        Returns:
            list[int]: tick indices into self._ticks, sorted ascending.

        Performance: O(N_keys) where N_keys == len(self._key_events). Uses the
        secondary index — never scans self._ticks (EC-MLS-05).
        """
        # Partition by goal vs non-goal using the secondary index
        goal_indices = [
            i for i in self._key_events
            if self._ticks[i].event_type == "goal"
        ]
        non_goal_indices = [
            i for i in self._key_events
            if self._ticks[i].event_type != "goal"
        ]

        # Select non-goal events per bias knob
        if MLS_KEY_EVENT_RECENCY_BIAS:
            # By tick number descending (most recent first)
            non_goal_indices.sort(
                key=lambda i: self._ticks[i].tick,
                reverse=True,
            )
        else:
            # By priority type order (then by tick descending within each type)
            non_goal_indices.sort(
                key=lambda i: (
                    _NON_GOAL_PRIORITY.index(self._ticks[i].event_type)
                    if self._ticks[i].event_type in _NON_GOAL_PRIORITY
                    else len(_NON_GOAL_PRIORITY),
                    -self._ticks[i].tick,
                ),
            )

        selected_non_goal = non_goal_indices[:max_events]

        # Combine goals + selected non-goal, sorted ascending for readable rendering
        return sorted(goal_indices + selected_non_goal)

    def serialize(self, log_dir: str = MLS_LOG_DIR) -> Path:
        """Write events.jsonl + meta.json to {log_dir}/match_{match_id}/.

        meta.json is written LAST via atomic temp+rename so an incomplete
        events.jsonl always pairs with an absent meta.json (ADR-0005, EC-MLS-16).

        Returns:
            Path: the directory containing the written files.

        Raises:
            MatchNotFinalizedError: if state is LIVE.
            IOError / OSError: any disk write failure.
        """
        if self._state != "FINALIZED":
            raise MatchNotFinalizedError(
                f"serialize called on LIVE match {self.match_id!r} — call finalize() first"
            )

        match_dir = Path(log_dir) / f"match_{self.match_id}"
        match_dir.mkdir(parents=True, exist_ok=True)

        events_path = match_dir / "events.jsonl"
        meta_path = match_dir / "meta.json"
        meta_tmp_path = match_dir / "meta.json.tmp"

        # EC-MLS-15: overwrite warning
        if events_path.exists():
            logger.warning(
                "events.jsonl already exists at %s (size=%d) — overwriting",
                events_path, events_path.stat().st_size,
            )
        if meta_path.exists():
            logger.warning(
                "meta.json already exists at %s (size=%d) — overwriting; "
                "removing before write so partial-write detection works",
                meta_path, meta_path.stat().st_size,
            )
            meta_path.unlink()

        # Write events.jsonl (line-by-line; raises immediately on IOError per EC-MLS-16)
        with events_path.open("w") as f:
            for i, tr in enumerate(self._ticks):
                line_dict = self._tick_record_to_jsonl_dict(tr, tick_index=i)
                f.write(json.dumps(line_dict) + "\n")
                f.flush()

        # Per-team strategy snapshots — written BEFORE meta.json so that if a
        # consumer sees meta.json (the sentinel for "match complete") the
        # strategy files are guaranteed to be in place. Best-effort: a write
        # error here logs and continues so meta.json still lands and the rest
        # of the match dir is consumable.
        if self._strategy_codes is not None:
            for team_id, code in self._strategy_codes.items():
                lang = (self._strategy_languages or {}).get(team_id, "python")
                _LANG_EXT = {"python": ".py", "javascript": ".js", "rust": ".rs"}
                ext = _LANG_EXT.get(lang, ".py")
                snap_path = match_dir / f"strategy_{team_id}{ext}"
                snap_tmp_path = match_dir / f"strategy_{team_id}{ext}.tmp"
                try:
                    with snap_tmp_path.open("w") as f:
                        f.write(code)
                        f.flush()
                        os.fsync(f.fileno())
                    os.replace(snap_tmp_path, snap_path)
                except OSError:
                    logger.exception(
                        "Failed to write strategy snapshot for %s in %s",
                        team_id, match_dir,
                    )
                    if snap_tmp_path.exists():
                        try:
                            snap_tmp_path.unlink()
                        except OSError:
                            pass

        # Write perf.jsonl (one line per active tick) before meta.json so
        # the sentinel ordering guarantee (meta last) still holds.
        if self._perf_ticks:
            perf_path = match_dir / "perf.jsonl"
            with perf_path.open("w") as f:
                for perf in self._perf_ticks:
                    f.write(json.dumps(perf) + "\n")
                    f.flush()

        # Write meta.json LAST, atomically (ADR-0005 + EC-MLS-16)
        meta_dict = self._build_meta()
        with meta_tmp_path.open("w") as f:
            json.dump(meta_dict, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(meta_tmp_path, meta_path)

        return match_dir

    def _tick_record_to_jsonl_dict(self, tr: TickRecord, tick_index: int) -> dict:
        """Convert TickRecord to JSONL line dict. Handles EC-MLS-17 (non-serializable)."""
        try:
            actions_list = []
            for action_idx, ar in enumerate(tr.actions):
                # EC-MLS-17: per-action details serialization with fallback
                try:
                    details_serialized = json.loads(json.dumps(ar.details))
                except (TypeError, ValueError) as e:
                    logger.error(
                        "Tick %d action %d (%s.%s): details non-serializable (%s) — "
                        "replacing with __SERIALIZATION_ERROR__",
                        tr.tick, action_idx, ar.player_id, ar.action, e,
                    )
                    details_serialized = "__SERIALIZATION_ERROR__"
                actions_list.append({
                    "player_id": ar.player_id,
                    "team": ar.team,
                    "action": ar.action,
                    "result": ar.result,
                    "details": details_serialized,
                })
            return {
                "tick": tr.tick,
                "ball_position": list(tr.ball_position),
                "ball_possession": tr.ball_possession,
                "score": dict(tr.score),
                "player_positions": {pid: list(pos) for pid, pos in tr.player_positions.items()},
                "actions": actions_list,
                "is_key_event": tr.is_key_event,
                "event_type": tr.event_type,
            }
        except Exception:
            logger.exception("Catastrophic serialization failure for tick %d", tr.tick)
            return {
                "tick": tr.tick,
                "ball_position": list(tr.ball_position),
                "score": dict(tr.score),
                "_serialization_error": True,
            }

    def set_teams_meta(self, teams_meta: dict) -> None:
        """Publish team rosters and display data for inclusion in meta.json.

        Expected shape (per team_id key 'team_a' / 'team_b'):
          {
            "team_id": "manchester",   # slug from data/configs/teams/<slug>.yaml
            "name": "Manchester United",  # display name
            "roster": [{"player_id", "name", "number", "role"}, ...],
          }

        Used by the browser to render team and player display names in the
        event log + on player dots. Optional — if not called, meta.json
        omits "teams" and the UI falls back to slot-id-based labels.
        """
        self._teams_meta = teams_meta

    def set_match_meta(self, match_meta: dict) -> None:
        """Publish match-clock parameters for inclusion in meta.json.

        Expected shape:
          {"tick_rate": int, "duration_minutes": int, "total_ticks": int}

        Used by the browser to convert tick numbers to MM:SS broadcast
        time. Optional — if not called, meta.json omits these fields and
        the UI falls back to inferring tick_rate=10 from project default.
        """
        self._match_meta = match_meta

    def set_strategy_codes(
        self,
        strategy_codes: dict[str, str],
        team_languages: dict[str, str] | None = None,
    ) -> None:
        """Publish per-team strategy source code for per-match disk snapshot.

        Expected shape: {"team_a": "<source>", "team_b": "<source>"}.

        team_languages (optional) declares each team's language so serialize()
        writes the snapshot with the correct file extension (.py for python,
        .js for javascript). Defaults to python for both when omitted.

        Optional — if not called, serialize() omits the per-match strategy
        files and the API viewer 404s. Used by the single-match path so the
        match dir is self-contained (no dependency on a global current.py).
        """
        self._strategy_codes = strategy_codes
        self._strategy_languages = team_languages

    def set_strategies_meta(self, strategies_meta: dict) -> None:
        """Publish per-team strategy provenance for inclusion in meta.json.

        Expected shape:
          {"team_a": {"provider": str, "model": str, "name": str, "version": int},
           "team_b": {...}}

        Recorded per-match so the matches list UI can show "openai/gpt-4o vs
        anthropic/claude" instead of "unknown vs unknown". Optional — if not
        called, meta.json omits "strategies" and the API returns "unknown".
        """
        self._strategies_meta = strategies_meta

    def _build_meta(self) -> dict:
        """Build meta.json content."""
        final_score = self._final_state.get("final_score", {"team_a": 0, "team_b": 0})
        final_tick = self._ticks[-1].tick if self._ticks else 0
        meta = {
            "match_id": self.match_id,
            "final_score": final_score,
            "final_tick": final_tick,
            "tick_count": len(self._ticks),
            "key_event_indices": list(self._key_events),
            "fallback_count": len(self._fallback_events),
            "phase_transitions": [
                {"tick": t, "old_phase": old, "new_phase": new}
                for (t, old, new) in self._phase_transitions
            ],
        }
        if self._teams_meta is not None:
            meta["teams"] = self._teams_meta
        if self._match_meta is not None:
            meta.update(self._match_meta)
        if self._strategies_meta is not None:
            meta["strategies"] = self._strategies_meta
        if self._perf_ticks:
            meta["perf_summary"] = self._build_perf_summary()
        return meta

    def _build_perf_summary(self) -> dict:
        """Aggregate per-tick perf data into match-level summary for meta.json."""
        tick_totals = [p["tick_total_ms"] for p in self._perf_ticks]
        callbacks_list = [p["callbacks_ms"] for p in self._perf_ticks]
        snapshot_list = [p["snapshot_ms"] for p in self._perf_ticks]

        # Per-language breakdown: collect serial_ms and exec_ms separately
        lang_serial: dict[str, list[float]] = {}
        lang_exec: dict[str, list[float]] = {}
        for p in self._perf_ticks:
            for pid_data in p.get("players", {}).values():
                lang = pid_data.get("lang", "unknown")
                lang_serial.setdefault(lang, []).append(pid_data.get("serial_ms", 0.0))
                lang_exec.setdefault(lang, []).append(pid_data.get("exec_ms", 0.0))

        def _pct(data: list[float], p: float) -> float:
            if not data:
                return 0.0
            s = sorted(data)
            idx = p / 100.0 * (len(s) - 1)
            lo = int(idx)
            hi = min(lo + 1, len(s) - 1)
            return round(s[lo] + (s[hi] - s[lo]) * (idx - lo), 4)

        def _stats(data: list[float]) -> dict:
            if not data:
                return {"mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0}
            import statistics as _stats_mod
            return {
                "mean": round(_stats_mod.mean(data), 4),
                "p50": _pct(data, 50),
                "p95": _pct(data, 95),
                "p99": _pct(data, 99),
            }

        langs = set(lang_serial) | set(lang_exec)
        summary: dict = {
            "active_ticks": len(self._perf_ticks),
            "tick_total_ms": _stats(tick_totals),
            "snapshot_ms": _stats(snapshot_list),
            "callbacks_ms": _stats(callbacks_list),
            "by_language": {
                lang: {
                    "serial_ms": _stats(lang_serial.get(lang, [])),
                    "exec_ms": _stats(lang_exec.get(lang, [])),
                }
                for lang in langs
            },
        }
        return summary