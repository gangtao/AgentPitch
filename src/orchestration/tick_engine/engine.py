"""Tick Engine — match orchestrator implementing GDD Rules 1-2.

Implements the match orchestrator that constructs all 7 subsystems in dependency
order and coordinates the complete match execution. This story implements only
the class scaffold and composition root. Stories 002+ add compile phase, tick
loop, and match finalization.

Design Document: design/gdd/tick-engine.md
Story: production/epics/tick-engine/story-001-scaffold-composition-root.md
"""

from __future__ import annotations

from pathlib import Path

from src.foundation.config_models import MatchConfig
from src.core.game_state_manager import GameStateManager
from src.core.match_log_system import MatchLog
from src.foundation.sandbox import Sandbox, ExecutionStatus, MatchSandboxes
from src.foundation.sandbox.python_sandbox import RestrictedPythonSandbox
from src.foundation.fallback import FallbackHandler
from src.foundation.fallback.types import FallbackEvent
from src.foundation.action_resolution_engine import ActionResolutionEngine
from src.foundation.formation_and_role_system import compute_anchors
from src.foundation.strategy_storage import read_current
from src.foundation.simulation_utils import hash_01
# PMS and BPS are modules with functions, not classes
import src.core.player_movement_system as pms_mod
import src.core.ball_physics_system as bps_mod


def _parse_strategy_header(strategy_path: Path) -> dict:
    """Extract provenance fields from a strategy file's header comment block.

    Strategy files written by strategy_storage.write_strategy carry a fixed
    header (see _build_header in strategy_storage). We pluck the fields the
    matches-list and live-viewer UIs care about — including `language`, which
    is added 2026-04-26 so the chyron can show JS vs PY for each team.

    Tolerates both Python (`#`) and JavaScript (`//`) comment prefixes.
    Returns an "unknown"-filled dict when the file is missing/unreadable so
    callers don't have to special-case absence.
    """
    blank = {
        "provider": "unknown",
        "model": "unknown",
        "name": "unknown",
        "version": 0,
        "language": "python",
    }
    try:
        text = strategy_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return blank
    fields: dict = {}
    for line in text.splitlines():
        if line.startswith("# "):
            s = line[2:].strip()
        elif line.startswith("// "):
            s = line[3:].strip()
        else:
            break  # header ends at first non-comment line
        if ":" not in s:
            continue
        key, _, value = s.partition(":")
        fields[key.strip()] = value.strip()
    # `generated_by` is "--baseline:<path>" for hand-written strategies, or
    # "code-generation-pipeline" / "post-match-evolution" for LLM ones.
    # For baseline: extract the strategy file basename. For LLM: use the
    # llm_model as the display name (model is what differentiates).
    gen_by = fields.get("generated_by", "")
    if gen_by.startswith("--baseline:"):
        path_str = gen_by.split(":", 1)[1]
        name = Path(path_str).stem  # "baseline" from "data/strategies/baseline.py"
    else:
        name = fields.get("llm_model", "unknown")
    try:
        version = int(fields.get("version", "0"))
    except ValueError:
        version = 0
    # `language` is a 2026-04-26 addition. Legacy headers without it default to
    # python (which is correct for every header that predates the JS sandbox).
    language = fields.get("language", "python")
    return {
        "provider": fields.get("llm_provider", "unknown"),
        "model": fields.get("llm_model", "unknown"),
        "name": name,
        "version": version,
        "language": language,
    }


class TickEngine:
    """GDD Rule 1 — match orchestrator. Single public method run_match()."""

    def run_match(
        self,
        config: MatchConfig,
        *,
        team_codes: dict[str, str] | None = None,
        team_meta: dict | None = None,
        team_languages: dict[str, str] | None = None,
    ) -> MatchLog:
        """GDD Rule 2 — construct all 7 subsystems in dependency order, then run match.

        Args:
            config: Complete match configuration containing teams, match parameters, and output settings.
            team_codes: Optional explicit strategy code per team ({"team_a": "...", "team_b": "..."}).
                When supplied, bypasses ``read_current(log_dir, team_id)`` so single-match runs
                don't need to write to the global ``<log_dir>/strategies/`` archive. None preserves
                the season/PMEP behavior of reading the latest ``current.py`` from disk.
            team_meta: Optional explicit provenance dict per team for ``meta.json``
                ({"team_a": {"provider", "model", "name", "version"}, "team_b": {...}}).
                Same semantics as team_codes — supplied for explicit-strategy runs, None falls
                back to parsing the on-disk ``current.py`` header.

        Returns:
            MatchLog instance ready for match execution.
        """
        # Rule 2: subsystem construction in dependency order

        # 1. GameStateManager requires both config and anchors
        anchors = compute_anchors(config)
        gsm = GameStateManager(config, anchors)

        # 2. MatchLog requires match_id (from story analysis - not config param)
        log = MatchLog(match_id=config.match.match_id)

        # 3. Sandbox — per-team dispatch via MatchSandboxes so mixed-language
        # matches work (Python team_a + JavaScript team_b, etc). Each team's
        # sandbox is constructed once; players are registered to it below.
        if team_languages is None:
            team_languages = {"team_a": "python", "team_b": "python"}
        team_sandboxes: dict[str, object] = {}
        for team_id, lang in team_languages.items():
            if lang == "javascript":
                from src.foundation.sandbox.quickjs_sandbox import QuickJSSandbox
                team_sandboxes[team_id] = QuickJSSandbox()
            elif lang == "rust":
                from src.foundation.sandbox.wasm_sandbox import WasmtimeSandbox
                team_sandboxes[team_id] = WasmtimeSandbox()
            else:
                team_sandboxes[team_id] = RestrictedPythonSandbox()
        sb = MatchSandboxes()

        # 4. FallbackHandler
        fh = FallbackHandler()

        # 5. PMS - module with functions, not class
        pms = pms_mod

        # 6. BPS - module with functions, not class
        bps = bps_mod

        # 7. ActionResolutionEngine receives (gsm, pms, bps, sb, fh) in order
        are = ActionResolutionEngine(gsm, pms, bps, sb, fh)

        # Compile phase (GDD Rule 3) — after subsystem construction, before tick loop
        log_dir = Path(config.output.log_dir)
        if team_codes is None:
            team_codes = {
                "team_a": read_current(log_dir, "team_a"),
                "team_b": read_current(log_dir, "team_b"),
            }

        # Player IDs derived from actual roster sizes (not hardcoded 5/team)
        # so 5v5, 6v6, 11v11 etc. all work. Fall back to 5/team for mock
        # configs (unit tests where MagicMock.team_a.players returns len 0).
        def _roster_size(team_cfg, default=5):
            try:
                n = len(team_cfg.players)
                return n if n > 0 else default
            except (TypeError, AttributeError):
                return default
        all_player_ids = (
            [f"team_a_{i}" for i in range(_roster_size(config.team_a))]
            + [f"team_b_{i}" for i in range(_roster_size(config.team_b))]
        )
        for pid in all_player_ids:
            team_id = "team_a" if pid.startswith("team_a") else "team_b"
            sb.register(pid, team_sandboxes[team_id])
            code = team_codes[team_id]
            result = sb.compile(pid, code)
            if result.status == ExecutionStatus.COMPILE_ERROR:
                sb.disable(pid)
                team_cfg = config.team_a if team_id == "team_a" else config.team_b
                log.record_fallback(FallbackEvent(
                    event_type="fallback",
                    tick=0,
                    player_id=pid,
                    team=team_id,
                    llm_provider=team_cfg.llm_provider,
                    failure_status="COMPILE_ERROR",
                    error_type=result.error_type or "Unknown",
                    execution_time_ms=0.0,
                    substituted_action="Hold",
                    fallback_substituted=True,
                ))

        # Rule 11: derive kickoff teams from hash_01
        seed = config.match.seed
        kickoff_team = "team_a" if hash_01(seed, 0, "kickoff") < 0.5 else "team_b"
        second_half_kickoff_team = "team_b" if kickoff_team == "team_a" else "team_a"

        # Initialize instance state for phase transitions
        self._goal_pause_remaining = 0
        self._halftime_pause_remaining = 0
        self._conceding_team = None
        self._second_half_kickoff_team = second_half_kickoff_team

        # Publish team rosters into the match log so meta.json includes
        # numbers + roles. Browser uses this to display "A #4" labels.
        if hasattr(log, "set_teams_meta"):
            try:
                teams_meta: dict = {}
                for team_id, team_cfg in (("team_a", config.team_a), ("team_b", config.team_b)):
                    roster = []
                    for i, p in enumerate(team_cfg.players):
                        roster.append({
                            "player_id": f"{team_id}_{i}",
                            "name": p.name,
                            "number": p.number if getattr(p, "number", 0) > 0 else (i + 1),
                            "role": p.role,
                        })
                    teams_meta[team_id] = {
                        "team_id": team_cfg.team_id,
                        "name": team_cfg.name,
                        "roster": roster,
                    }
                log.set_teams_meta(teams_meta)
            except Exception:
                pass  # tolerant of mock variations

        # Publish match-clock parameters so the browser can render MM:SS
        # broadcast-style. Without these, the UI would have to hardcode
        # tick_rate=10 and infer total_ticks from the last emitted tick.
        if hasattr(log, "set_match_meta"):
            try:
                log.set_match_meta({
                    "tick_rate": config.match.tick_rate,
                    "duration_minutes": config.match.duration_minutes,
                    "total_ticks": config.match.tick_rate * config.match.duration_minutes * 60,
                    # Include the actual seed used so the live viewer can show
                    # it (instead of inferring from match_id pattern matching).
                    "seed": config.match.seed,
                    # Field dimensions — needed by the broadcast viewer to map
                    # engine-coords → canvas pixels correctly. Without these
                    # the viewer falls back to a hardcoded 100×60 and a 5v5
                    # 60×40 pitch renders with wrong proportions / off-screen
                    # players. (Bug fixed 2026-04-25.)
                    "field_width": config.match.field_width,
                    "field_height": config.match.field_height,
                    # Goal mouth height (m). Viewer derives goal y-extent as
                    # field_height/2 ± goal_height/2 — without this it would
                    # fall back to a 10m-tall slot centered on a hardcoded 60m
                    # field, putting goals off-pitch on small configs.
                    "goal_height": config.match.goal_height,
                })
            except Exception:
                pass  # tolerant of mock variations

        # Publish per-team strategy provenance so the matches list can show
        # "openai/gpt-4o vs anthropic/claude" instead of "unknown vs unknown".
        # Two sources, in priority order:
        #   1. team_meta kwarg (explicit-strategy / single-match mode) — caller
        #      hands us the provenance dict directly, no disk read.
        #   2. Fallback: parse the comment header of the installed current.py
        #      under <log_dir>/strategies/<team>/ (season/PMEP path where the
        #      pipeline wrote the file via strategy_storage.write_strategy).
        if hasattr(log, "set_strategies_meta"):
            try:
                if team_meta is not None:
                    log.set_strategies_meta(dict(team_meta))
                else:
                    from src.foundation.strategy_storage import strategy_dir as _strategy_dir
                    strategies_meta: dict = {}
                    for team_id in ("team_a", "team_b"):
                        team_dir = _strategy_dir(config.output.log_dir, team_id)
                        # Language-agnostic discovery: a team archive holds either
                        # current.py or current.js (never both). Prefer .py for
                        # backward-compat, fall back to .js.
                        current_path = team_dir / "current.py"
                        if not current_path.exists():
                            js_path = team_dir / "current.js"
                            if js_path.exists():
                                current_path = js_path
                        strategies_meta[team_id] = _parse_strategy_header(current_path)
                    log.set_strategies_meta(strategies_meta)
            except Exception:
                pass  # tolerant — header parsing must never break engine init

        # Hand the compiled-and-ready strategy code to the log so serialize()
        # can drop a per-match snapshot at <match_dir>/strategy_<team>.py.
        # Without this the API viewer would have to fall back on a global
        # current.py (which gets overwritten between runs and shows the wrong
        # code when browsing past matches).
        if hasattr(log, "set_strategy_codes"):
            try:
                log.set_strategy_codes(dict(team_codes), team_languages=dict(team_languages))
            except TypeError:
                # Backward-compat: older MatchLog without team_languages kwarg
                log.set_strategy_codes(dict(team_codes))
            except Exception:
                pass  # tolerant of mock variations

        # Rule 4: start match
        gsm.start_match()
        self._setup_kickoff(gsm, log, kickoff_team)  # STUB — Story 006 implements
        log.record_phase_transition(0, "pre_match", "kick_off")

        # Rule 5: main tick loop
        while gsm.tick < gsm.total_ticks:
            phase = gsm.get_phase()
            # Accept both lowercase and uppercase phase strings for compatibility
            phase_lower = phase.lower() if isinstance(phase, str) else phase
            if phase_lower in ("goal_scored", "half_time"):
                self._handle_pause_tick(gsm, log, config)  # STUB — Story 006
            elif phase_lower in ("kick_off", "in_play"):
                self._handle_active_tick(gsm, log, are, config)  # STUB — Story 004
            else:
                break
            gsm.advance_tick()

        # Story 007 — finalize match before returning
        if hasattr(gsm, "get_final_state"):
            final_state = gsm.get_final_state()
            if hasattr(log, "finalize"):
                try:
                    log.finalize(final_state)
                except TypeError:
                    log.finalize()  # accepts no args
        elif hasattr(log, "finalize"):
            # Construct basic final state from gsm attributes
            final_state = {
                "final_score": getattr(gsm.state, "score", {"team_a": 0, "team_b": 0}),
                "final_tick": getattr(gsm.state, "tick", 0),
                "final_phase": getattr(gsm.state, "phase", "UNKNOWN")
            }
            try:
                log.finalize(final_state)
            except TypeError:
                log.finalize()  # accepts no args
            except Exception:
                pass  # tolerant of mock variations

        # Persist match data to disk so downstream consumers (HTTP server,
        # CLI orchestrator's next-match PMEP step) can read events.jsonl +
        # meta.json. Without this, the browser layer sees nothing and live
        # LLM seasons produce no observable history. Closes tech-debt #2.
        if hasattr(log, "serialize"):
            try:
                log.serialize(config.output.log_dir)
            except Exception:
                # Tolerant of mock variations in unit tests; real MatchLog
                # raises only on disk I/O failures, which the caller can
                # observe via missing files.
                pass

        return log

    def _setup_kickoff(self, gsm, log, kickoff_team):
        """GDD Rule 10 — reset all 10 players to anchors, ball to center, kickoff player gets possession."""
        # Defensive check for stub test compatibility
        if gsm is None:
            return

        import math

        # Get field dimensions from GSM
        field_w = gsm.state.field_width
        field_h = gsm.state.field_height

        # Derive from actual GSM player roster (supports 5v5, 11v11, etc.).
        # Fall back to hardcoded 5v5 when _anchors is missing/empty (mock
        # GSMs in unit tests don't populate it).
        try:
            all_pids = sorted(gsm.state._anchors.keys())
            if not all_pids:
                raise ValueError("empty anchors")
        except (AttributeError, TypeError, ValueError):
            all_pids = (
                [f"team_a_{i}" for i in range(5)]
                + [f"team_b_{i}" for i in range(5)]
            )

        # Reset all players to anchors
        for pid in all_pids:
            anchor = gsm.state._anchors[pid]
            gsm.apply_move(pid, anchor)

        # Center the ball, at rest
        center = (field_w / 2, field_h / 2)
        gsm.update_ball_position(center)
        gsm.update_ball_velocity((0.0, 0.0))

        # Clear ball carrier
        gsm.transfer_possession(gsm.state.ball["carrier_id"], None)

        # Find kickoff player: closest-to-center anchor on kickoff_team,
        # EXCLUDING the GK (per FIFA Law 8 — keepers don't take kickoffs).
        # Falls back to including GK only if filtering leaves zero candidates
        # (degenerate config / mock fixtures with no role info).
        if kickoff_team is None:
            kickoff_team = "team_a"  # Default fallback
        team_pids = [pid for pid in all_pids if pid.startswith(kickoff_team)]

        def role_for(pid):
            try:
                return gsm.state.players[pid].get("role")
            except (KeyError, TypeError, AttributeError):
                return None

        non_gk_pids = [pid for pid in team_pids if role_for(pid) != "GK"]
        candidates = non_gk_pids if non_gk_pids else team_pids

        def dist_to_center(pid):
            a = gsm.state._anchors[pid]
            return math.sqrt((a[0] - center[0])**2 + (a[1] - center[1])**2)

        kickoff_pid = min(candidates, key=dist_to_center)
        gsm.transfer_possession(None, kickoff_pid)
        # Per FIFA Law 8 (added 2026-04-22): override anchor positions to
        # legal kickoff state — kicker at center, others in own half +
        # outside center circle. Defensive guards inside the GSM helper
        # make this a silent no-op for mock-based unit tests.
        if hasattr(gsm, "_apply_kickoff_positions"):
            gsm._apply_kickoff_positions(kickoff_pid)
        gsm.set_phase("KICK_OFF")

    def _handle_active_tick(self, gsm, log, are, config):
        """Handle tick in active phases (kick_off, in_play).

        GDD Rule 6 implementation:
        1. Get history from log
        2. Capture score before ARE resolution
        3. Call ARE.resolve_tick() to get action records
        4. Process any fallback events
        5. Capture score after and classify event type
        6. Construct TickRecord with all required fields
        7. Log the tick record
        """
        import time as _time
        from src.core.match_log_system import TickRecord, ActionRecord

        history = log.get_history()

        # Phase 1: snapshot build (timed separately for perf breakdown)
        _t0_tick = _time.perf_counter_ns()
        snap_before = gsm.build_tick_snapshot()
        _snapshot_ms = (_time.perf_counter_ns() - _t0_tick) / 1_000_000
        score_before = snap_before["score"]

        _t0_are = _time.perf_counter_ns()
        are_result = are.resolve_tick(gsm.tick, history)
        _callbacks_ms = (_time.perf_counter_ns() - _t0_are) / 1_000_000

        # Adapt for ARE's actual return shape (current = dict; GDD spec = tuple)
        if isinstance(are_result, tuple):
            action_records, fallback_events = are_result
        else:
            action_records = are_result
            fallback_events = []

        # Record fallback events before tick record (AC-TE-08)
        for fe in fallback_events:
            log.record_fallback(fe)

        # Get snapshot for after state
        snap_after = gsm.build_tick_snapshot()
        score_after = snap_after["score"]
        ball_position = snap_after["ball"]["position"]
        ball_possession = snap_after["ball"]["possession"]

        event_type = self._classify_event(action_records, fallback_events, score_before, score_after)

        # Build player positions dict for TickRecord
        # Skip ARE-injected synthetic "system" key (engine.py:577, 643 use it
        # for ball-pickup/goal events that have no responsible player).
        # build_player_state would KeyError on it.
        player_positions = {}
        for player_id in action_records.keys():
            if player_id == "system":
                continue
            player_state = gsm.build_player_state(player_id)
            pos = player_state["position"]
            player_positions[player_id] = [pos[0], pos[1]]  # tuple to list

        # Convert action_records dict values to ActionRecord objects.
        # The synthetic "system" record (emitted by ARE Phase 7 for OOB
        # restarts and no-GK auto-goals) is preserved with team="system"
        # so the Event Log can render it. Was previously skipped, which
        # silently dropped OOB rows from the per-tick log (the classifier
        # still saw them, so event_type="oob" appeared in meta — but the
        # row had no detail in events.jsonl). Fixed 2026-04-23.
        action_record_objects = []
        for player_id, action_dict in action_records.items():
            if player_id == "system":
                action_record = ActionRecord(
                    player_id="system",
                    team="system",
                    action=action_dict.get("action", "Hold"),
                    result=action_dict.get("result", "ok"),
                    details=action_dict.copy(),
                )
                action_record_objects.append(action_record)
                continue
            player_state = gsm.build_player_state(player_id)
            action_record = ActionRecord(
                player_id=player_id,
                team=player_state["team"],
                action=action_dict.get("action", "Hold"),
                result=action_dict.get("result", "ok"),
                details=action_dict.copy()  # Include all fields as details
            )
            action_record_objects.append(action_record)

        tick_record = TickRecord(
            tick=gsm.tick,
            ball_position=ball_position,
            ball_possession=ball_possession,
            score=score_after,
            player_positions=player_positions,
            actions=action_record_objects,
            is_key_event=(event_type is not None),
            event_type=event_type,
        )
        log.record_tick(tick_record)

        # Collect per-player sandbox timing from MatchSandboxes and record
        # into the match log for perf.jsonl + meta.json perf_summary.
        if hasattr(are, "sandbox") and hasattr(are.sandbox, "drain_exec_times"):
            _tick_total_ms = (_time.perf_counter_ns() - _t0_tick) / 1_000_000
            exec_times = are.sandbox.drain_exec_times()
            perf_players = {
                pid: {
                    "lang": are.sandbox.language_for(pid),
                    "serial_ms": t["serial_ms"],
                    "exec_ms": t["exec_ms"],
                }
                for pid, t in exec_times.items()
            }
            if hasattr(log, "record_tick_perf"):
                log.record_tick_perf({
                    "tick": gsm.tick,
                    "tick_total_ms": round(_tick_total_ms, 4),
                    "snapshot_ms": round(_snapshot_ms, 4),
                    "callbacks_ms": round(_callbacks_ms, 4),
                    "players": perf_players,
                })

        self._check_phase_transitions(score_before, score_after, gsm, log, config)

    def _classify_event(self, action_records, fallback_events, score_before, score_after):
        """GDD Rule 12 — event_type priority classification.

        Expanded 2026-04-22 per playtest #2 feedback. Refined per ADR-0018
        (2026-04-22): tackle/save outcomes are now 3-state and the
        "inaccurate" pass label was dropped (continuous deviation now).

        Priority order (first match wins):
        1. Score delta → "goal"
        2. Fallback present → "fallback"
        3. Any Tackle:
           - cooldown_blocked → "tackle_cooldown_blocked"
           - controlled       → "tackle_controlled"   (was: "tackle_success")
           - blocked          → "tackle_blocked"      (NEW: deflection)
           - else             → "tackle"
        4. Any Shoot:
           - cooldown_blocked → "shot_cooldown_blocked"
           - save             → "shot_on_target"
           - else             → "shot"
        5. Any Pass:
           - cooldown_blocked → "pass_cooldown_blocked"
           - else             → "pass"
        6. Any Dribble → "dribble"
        7. Any BallControl → "ball_control"
        8. None
        """
        if score_after != score_before:
            return "goal"
        if len(fallback_events) > 0:
            return "fallback"

        recs = list(action_records.values())

        # OOB — added 2026-04-22 alongside ADR-0018. Surfaces when ARE Phase 7
        # detected an out-of-bounds (side line / end line outside goal mouth).
        # Sits above per-action priorities because OOB ends the play.
        for rec in recs:
            if rec.get("out_of_bounds"):
                return "oob"

        # Tackle takes priority among normal actions (it's a contested moment)
        for rec in recs:
            if rec.get("action") == "Tackle":
                result = rec.get("result")
                if result == "cooldown_blocked":  # ADR-0015
                    return "tackle_cooldown_blocked"
                if result == "controlled":  # ADR-0018 clean take
                    return "tackle_controlled"
                if result == "blocked":  # ADR-0018 deflection
                    return "tackle_blocked"
                return "tackle"

        # Shoot — surface every shot
        for rec in recs:
            if rec.get("action") == "Shoot":
                if rec.get("result") == "cooldown_blocked":  # ADR-0015
                    return "shot_cooldown_blocked"
                if rec.get("result") == "save":
                    return "shot_on_target"
                return "shot"

        # Pass — single state now (continuous deviation, no "inaccurate" label)
        for rec in recs:
            if rec.get("action") == "Pass":
                if rec.get("result") == "cooldown_blocked":  # ADR-0015
                    return "pass_cooldown_blocked"
                return "pass"

        # Dribble — Phase 4 contests are recorded as `dribble_result` merged
        # into the carrier's existing Move record (the carrier's `action`
        # stays "Move"; the contest outcome is the side-channel field).
        # Was looking for `action == "Dribble"` which was never emitted.
        for rec in recs:
            if rec.get("dribble_result"):
                if rec["dribble_result"] == "success":
                    return "dribble_success"
                if rec["dribble_result"] == "failed":
                    return "dribble_failed"
                return "dribble"

        # Ball control — emitted by ARE Phase 7 when a loose ball is collected
        for rec in recs:
            if rec.get("action") == "BallControl":
                return "ball_control"

        return None

    def _handle_pause_tick(self, gsm, log, config):
        """GDD Rule 8 — pause tick: decrement counter; on zero, transition to KICK_OFF or FULL_TIME."""
        # Defensive check for stub test compatibility
        if gsm is None:
            return

        phase = gsm.get_phase()
        phase_lower = phase.lower() if isinstance(phase, str) else phase

        if phase_lower == "goal_scored":
            self._goal_pause_remaining -= 1
            if self._goal_pause_remaining <= 0:
                if gsm.tick >= gsm.total_ticks:
                    gsm.set_phase("FULL_TIME")
                    log.record_phase_transition(gsm.tick, "goal_scored", "full_time")
                else:
                    self._setup_kickoff(gsm, log, getattr(self, "_conceding_team", "team_a"))
                    log.record_phase_transition(gsm.tick, "goal_scored", "kick_off")
        elif phase_lower == "half_time":
            self._halftime_pause_remaining -= 1
            if self._halftime_pause_remaining <= 0:
                if gsm.tick >= gsm.total_ticks:
                    gsm.set_phase("FULL_TIME")
                    log.record_phase_transition(gsm.tick, "half_time", "full_time")
                    return
                gsm.swap_attack_direction()
                # Half-time fully restores every player's health (added
                # 2026-04-23). Matches real soccer's 15-min break.
                if hasattr(gsm, "restore_all_health"):
                    gsm.restore_all_health()
                self._setup_kickoff(gsm, log, self._second_half_kickoff_team)
                log.record_phase_transition(gsm.tick, "half_time", "kick_off")

    def _check_phase_transitions(self, score_before, score_after, gsm, log, config):
        """GDD Rule 7 — priority: goal → half-time → full-time. Then Rule 9: KICK_OFF → IN_PLAY."""
        # Rule 7 priority 1: goal
        if score_after != score_before:
            gsm.set_phase("GOAL_SCORED")
            log.record_phase_transition(gsm.tick, "in_play", "goal_scored")
            # Get pause length from config (with default fallback)
            pause = config.simulation.goal_reset_ticks
            self._goal_pause_remaining = pause
            self._conceding_team = self._infer_conceding_team(score_before, score_after)
            return  # do not check other transitions this tick

        def _phase_eq(actual, target_lower):
            """Compare phase case-insensitively."""
            return isinstance(actual, str) and actual.lower() == target_lower

        # Rule 7 priority 2: half-time
        if gsm.tick == gsm.half_1_end_tick and _phase_eq(gsm.get_phase(), "in_play"):
            gsm.set_phase("HALF_TIME")
            log.record_phase_transition(gsm.tick, "in_play", "half_time")
            pause = config.simulation.half_time_pause_ticks
            self._halftime_pause_remaining = pause

        # Rule 7 priority 3: full-time
        if gsm.tick >= gsm.total_ticks and _phase_eq(gsm.get_phase(), "in_play"):
            gsm.set_phase("FULL_TIME")
            log.record_phase_transition(gsm.tick, "in_play", "full_time")

        # Rule 9: KICK_OFF tick → IN_PLAY after transition checks
        if _phase_eq(gsm.get_phase(), "kick_off"):
            gsm.set_phase("IN_PLAY")
            log.record_phase_transition(gsm.tick, "kick_off", "in_play")

    def _infer_conceding_team(self, score_before, score_after):
        """Determine which team conceded based on score delta."""
        # Score may be tuple (team_a, team_b) or dict {"team_a": N, "team_b": N}
        if isinstance(score_before, dict):
            if score_after.get("team_a", 0) > score_before.get("team_a", 0):
                return "team_b"
            return "team_a"
        # Tuple
        if score_after[0] > score_before[0]:
            return "team_b"
        return "team_a"