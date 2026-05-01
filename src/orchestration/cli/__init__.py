"""CLI Orchestrator — agent_pitch run entry point."""
from __future__ import annotations
import argparse
import asyncio
import sys
from pathlib import Path

from src.foundation.config_loader import load_config


def _positive_int(value: str) -> int:
    n = int(value)
    if n <= 0:
        raise argparse.ArgumentTypeError(f"must be positive, got {n}")
    return n


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent_pitch")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--config", required=True)
    run.add_argument("--season-length", type=_positive_int, required=True)
    # Dev-time bypass: use a fixed hand-written strategy for both teams.
    # Skips CGP and PMEP entirely — no LLM calls. The same file is installed
    # as `current.py` for team_a and team_b so the simulation framework can
    # be validated without LLM-introduced variance.
    run.add_argument(
        "--baseline",
        default=None,
        help="Path to a hand-written strategy .py file. Bypasses CGP/PMEP "
             "and uses this file for both teams (no LLM calls).",
    )
    # Per-team baselines: same effect as --baseline but lets you pick a different
    # strategy file per team. Used by the UI (POST /api/matches) when the user
    # picks two different strategies in the Start sub-view. If BOTH are provided,
    # CGP is bypassed; PMEP is also bypassed (treated as a single-match run).
    run.add_argument(
        "--strategy-a",
        default=None,
        help="Path to team_a's strategy file. Use with --strategy-b. Bypasses CGP/PMEP.",
    )
    run.add_argument(
        "--strategy-b",
        default=None,
        help="Path to team_b's strategy file. Use with --strategy-a. Bypasses CGP/PMEP.",
    )
    # Override the config's match_id at runtime. ADR-0021 removed match_id
    # from saved configs — it's per-run, supplied here.
    run.add_argument(
        "--match-id",
        default=None,
        help="Per-run match identifier. Overrides config.match.match_id. "
             "Becomes the output directory name (matches/match_<id>/).",
    )
    run.add_argument(
        "--log-dir",
        default=None,
        help="Override config.output.log_dir at runtime. Used by the HTTP "
             "API to point match output at <DATA_HOME>/matches/ regardless "
             "of what the saved match-config yaml says.",
    )
    run.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override config.match.seed at runtime. Allows running the "
             "same config with a different RNG seed (different match outcome).",
    )
    run.add_argument(
        "--global-defaults",
        default=None,
        help="Path to global-defaults.yaml (the file the Config UI's Game tab "
             "writes to). When provided, any keys in it that match fields on "
             "SimulationConfig are overlaid onto config.simulation at runtime "
             "— so Game-tab edits take effect without re-saving every match "
             "config. Match-level fields (tick_rate, duration, field size, "
             "seed) are NOT overlaid: those stay per-match.",
    )
    run.add_argument(
        "--arena-id",
        default=None,
        help="Optional. When provided, the orchestrator operates in Arena mode "
             "for this series ID. Strategy evolution files are written to "
             "<arena_dir>/series_<arena_id>/strategies/<team>/strategy_v<N>.py "
             "after each PMEP step so the Arena section can diff them.",
    )
    run.add_argument(
        "--arena-dir",
        default=None,
        help="Base arena directory (e.g. data/arena). Required when --arena-id "
             "is set so the CLI can update series.json after each match and write "
             "strategies to the correct series directory.",
    )
    run.add_argument(
        "--provider-a",
        default=None,
        help="Override LLM provider for Team A (e.g. 'openai', 'anthropic'). "
             "Overrides llm-providers.yaml global settings for this team only.",
    )
    run.add_argument(
        "--model-a",
        default=None,
        help="Override LLM model for Team A (e.g. 'gpt-4o'). "
             "Requires --provider-a to be set.",
    )
    run.add_argument(
        "--provider-b",
        default=None,
        help="Override LLM provider for Team B (e.g. 'anthropic'). "
             "Overrides llm-providers.yaml global settings for this team only.",
    )
    run.add_argument(
        "--model-b",
        default=None,
        help="Override LLM model for Team B (e.g. 'claude-sonnet-4-6'). "
             "Requires --provider-b to be set.",
    )
    run.add_argument(
        "--language-a",
        default=None,
        choices=["python", "javascript", "rust"],
        help="Strategy language for Team A CGP generation (default: python).",
    )
    run.add_argument(
        "--language-b",
        default=None,
        choices=["python", "javascript", "rust"],
        help="Strategy language for Team B CGP generation (default: python).",
    )
    return parser


def _load_team_baseline(team_id: str, baseline_path: str) -> tuple[str, dict]:
    """Read a baseline strategy file and return its code + provenance meta.

    Per ADR-0023: provenance comes from the `<name>.meta.json` sidecar that
    sits alongside `<name>.py` in `<data-dir>/strategies/`. Falls back to
    `provider="unknown"` only when no sidecar exists (legacy library files
    saved before ADR-0023).

    No disk writes — for single-match / per-team-baseline mode, the engine
    receives the code directly via TickEngine.run_match(team_codes=...) and
    MatchLog.serialize() snapshots it into <match_dir>/strategy_<team>.py.
    The global <log_dir>/strategies/ archive is only used by season/PMEP.

    Returns:
        (code, meta) where meta matches the shape published via
        MatchLog.set_strategies_meta() — keys: provider, model, name, version.
    """

    src_path = Path(baseline_path)
    code = src_path.read_text(encoding="utf-8")

    # Sidecar lookup: <baseline_path-without-ext>.meta.json next to the source.
    # Use src.strategy_library so a malformed sidecar surfaces here rather than
    # silently degrading to "unknown".
    from src.strategy_library import StrategyLibraryError, read_meta, UNKNOWN_META

    name = src_path.stem
    data_home = src_path.parent.parent  # <data-dir>/strategies/<name>.<ext> → <data-dir>
    try:
        sidecar = read_meta(data_home, name)
    except StrategyLibraryError as e:
        print(
            f"  [BASELINE] {team_id}: WARN sidecar unreadable for {baseline_path}: {e}",
            flush=True,
        )
        sidecar = UNKNOWN_META

    # Language: prefer file extension (always present), fall back to sidecar
    # (which itself defaults to python). The extension is the source of truth
    # because the file with that extension is what the LLM produced and what
    # the sandbox factory will dispatch on.
    if src_path.suffix == ".js":
        language = "javascript"
    elif src_path.suffix == ".rs":
        language = "rust"
    elif src_path.suffix == ".py":
        language = "python"
    else:
        language = sidecar.language

    meta = {
        "provider": sidecar.provider,
        "model":    sidecar.model,
        "name":     name,
        "version":  0,
        "language": language,
    }
    print(
        f"  [BASELINE] {team_id}: loaded {baseline_path} "
        f"(provider={meta['provider']}, model={meta['model']}, language={language})",
        flush=True,
    )
    return code, meta, language


async def _run_season(
    config_path: str,
    season_length: int,
    config,
    baseline_path: str | None = None,
    strategy_a_path: str | None = None,
    strategy_b_path: str | None = None,
    language_a: str | None = None,
    language_b: str | None = None,
    arena_id: str | None = None,
    arena_dir: str | None = None,
) -> None:
    """GDD Rules 4-5 — pre-season CGP + abort policy.

    When `baseline_path` is provided, CGP and PMEP are bypassed: the file is
    installed as v1 for both teams once, and the same strategy is used for
    every match in the season (no evolution). This is for framework testing
    without LLM-introduced variance.

    When BOTH `strategy_a_path` and `strategy_b_path` are provided (UI-driven
    single match start), CGP is bypassed: each team uses its specified file.
    PMEP is also bypassed (this code path is for one-off matches, not seasons).
    """
    per_team_baselines = (strategy_a_path is not None and strategy_b_path is not None)
    bypass_pmep = baseline_path is not None or per_team_baselines

    # Arena mode: resolve the series directory used for series.json updates and
    # for strategy file writes (so they land in arena/series_{id}/strategies/
    # instead of matches/strategies/).
    import json as _json
    import os as _os
    import datetime as _dt
    arena_s_dir: Path | None = None
    strategy_log_dir: Path | None = None
    if arena_id and arena_dir:
        arena_s_dir = Path(arena_dir) / f"series_{arena_id}"
        strategy_log_dir = arena_s_dir

    # Explicit-strategy modes hand the engine the code + provenance directly
    # so single-match runs don't write to <log_dir>/strategies/. Stays None
    # for the LLM/season path (TickEngine falls back to read_current()).
    explicit_team_codes: dict[str, str] | None = None
    explicit_team_meta: dict | None = None
    explicit_team_languages: dict[str, str] | None = None

    if per_team_baselines:
        print(f"[season] per-team baseline mode — A={strategy_a_path}, B={strategy_b_path}", flush=True)
        code_a, meta_a, lang_a = _load_team_baseline("team_a", strategy_a_path)
        code_b, meta_b, lang_b = _load_team_baseline("team_b", strategy_b_path)
        explicit_team_codes = {"team_a": code_a, "team_b": code_b}
        explicit_team_meta = {"team_a": meta_a, "team_b": meta_b}
        explicit_team_languages = {"team_a": lang_a, "team_b": lang_b}
    elif baseline_path is not None:
        # Baseline bypass — no LLM calls, no template loading needed.
        print(f"[season] baseline mode — loading {baseline_path} for both teams", flush=True)
        code_a, meta_a, lang_a = _load_team_baseline("team_a", baseline_path)
        code_b, meta_b, lang_b = _load_team_baseline("team_b", baseline_path)
        explicit_team_codes = {"team_a": code_a, "team_b": code_b}
        explicit_team_meta = {"team_a": meta_a, "team_b": meta_b}
        explicit_team_languages = {"team_a": lang_a, "team_b": lang_b}
    else:
        from src.foundation.code_generation_pipeline import generate_strategy
        from src.foundation.system_prompt_builder import load_templates

        # SPB requires its template cache populated before CGP/PMEP run any prompt build.
        # Failure here aborts before any LLM call (atomic — cache is left empty on error).
        load_templates()

        print("[season] generating initial strategies...", flush=True)
        lang_a = language_a or "python"
        lang_b = language_b or "python"
        cgp_results = await asyncio.gather(
            generate_strategy(config, "team_a", language=lang_a,
                              strategy_log_dir=strategy_log_dir),
            generate_strategy(config, "team_b", language=lang_b,
                              strategy_log_dir=strategy_log_dir),
            return_exceptions=True,
        )
        team_ids = ["team_a", "team_b"]
        any_failed = False
        for team_id, result in zip(team_ids, cgp_results):
            if isinstance(result, Exception):
                print(f"[CGP-ERROR] {team_id}: {type(result).__name__}: {result}", file=sys.stderr)
                any_failed = True
            else:
                team_cfg = config.team_a if team_id == "team_a" else config.team_b
                provider = team_cfg.llm_provider
                print(f"  [CGP] {team_id}: strategy_v1.py written ({provider})", flush=True)

        if any_failed:
            sys.exit(1)

        # Track languages for TickEngine so the correct sandbox is selected per team.
        explicit_team_languages = {"team_a": lang_a, "team_b": lang_b}

    def _append_event(event_name: str, data: dict) -> None:
        """Append a typed event line to events.jsonl in the series dir."""
        if arena_s_dir is None:
            return
        line = _json.dumps({"event": event_name, "data": data})
        events_path = arena_s_dir / "events.jsonl"
        with open(events_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def _update_series_json(match_number: int, match_id: str, final_score_dict: dict) -> None:
        """Append match result to series.json after each match."""
        if arena_s_dir is None:
            return
        path = arena_s_dir / "series.json"
        try:
            data = _json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, _json.JSONDecodeError):
            return
        a, b = final_score_dict.get("team_a", 0), final_score_dict.get("team_b", 0)
        result = "team_a" if a > b else ("team_b" if b > a else "tie")
        data.setdefault("matches", []).append({
            "match_number": match_number,
            "match_id": match_id,
            "result": result,
            "final_score": final_score_dict,
        })
        data.setdefault("score", {"team_a": 0, "team_b": 0, "ties": 0})
        if result == "team_a":
            data["score"]["team_a"] = data["score"].get("team_a", 0) + 1
        elif result == "team_b":
            data["score"]["team_b"] = data["score"].get("team_b", 0) + 1
        else:
            data["score"]["ties"] = data["score"].get("ties", 0) + 1
        tmp = arena_s_dir / "series.json.tmp"
        tmp.write_text(_json.dumps(data, indent=2), encoding="utf-8")
        _os.replace(tmp, path)

    def _finalize_series_json(score_dict: dict) -> None:
        """Set final status on series.json at season end."""
        if arena_s_dir is None:
            return
        path = arena_s_dir / "series.json"
        try:
            data = _json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, _json.JSONDecodeError):
            return
        a, b = score_dict.get("team_a", 0), score_dict.get("team_b", 0)
        status = "team_a" if a > b else ("team_b" if b > a else "tied")
        data["status"] = "complete"
        data["winner"] = status
        data["completed_iso"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
        tmp = arena_s_dir / "series.json.tmp"
        tmp.write_text(_json.dumps(data, indent=2), encoding="utf-8")
        _os.replace(tmp, path)

    # Story 003: season loop + match execution (Rules 6, 8, 13)
    from src.orchestration.tick_engine import TickEngine

    for match_number in range(1, season_length + 1):
        print(f"[season] match {match_number}/{season_length} starting", flush=True)
        # Arena mode: each match gets a unique ID; regular mode: reuse config match_id.
        if arena_id:
            per_match_id = f"{arena_id}-m{match_number}"
        elif args_match_id := config.match.match_id:
            per_match_id = args_match_id
        else:
            per_match_id = _dt.datetime.now(_dt.timezone.utc).strftime("match-%Y%m%d-%H%M%S")
        match_config = config.model_copy(
            update={"match": config.match.model_copy(update={"match_id": per_match_id})}
        )

        # In arena mode, pre-read strategies from the series dir and pass them
        # directly so TickEngine doesn't try to read from matches/strategies/.
        # This also keeps match events.jsonl/meta.json in data/matches/ so the
        # normal match viewer can find them.
        run_team_codes = explicit_team_codes
        run_team_meta = explicit_team_meta
        run_team_languages = explicit_team_languages
        if strategy_log_dir is not None and explicit_team_codes is None:
            from src.foundation.strategy_storage import read_current as _read_current, strategy_dir as _strategy_dir
            from src.orchestration.tick_engine.engine import _parse_strategy_header as _parse_header
            run_team_codes = {
                "team_a": _read_current(strategy_log_dir, "team_a"),
                "team_b": _read_current(strategy_log_dir, "team_b"),
            }
            # Parse provenance headers so the match list shows provider/model
            # instead of "unknown vs unknown".
            run_team_meta = {}
            for _tid in ("team_a", "team_b"):
                _team_dir = _strategy_dir(strategy_log_dir, _tid)
                _cur = next(
                    (p for ext in (".py", ".js", ".rs")
                     if (p := _team_dir / f"current{ext}").exists()),
                    _team_dir / "current.py",  # fallback → _parse_header returns blank
                )
                run_team_meta[_tid] = _parse_header(_cur)
            # Derive language from header or file extension.
            if run_team_languages is None:
                run_team_languages = {
                    _tid: run_team_meta[_tid].get("language", "python")
                    for _tid in ("team_a", "team_b")
                }

        # Emit match-started event so UI updates immediately.
        _append_event("match-started", {
            "match_number": match_number,
            "season_length": season_length,
            "match_id": per_match_id,
            "started_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        })

        match_log = TickEngine().run_match(  # sync, blocking
            match_config,
            team_codes=run_team_codes,
            team_meta=run_team_meta,
            team_languages=run_team_languages,
        )

        # Read final score defensively from match_log.
        final_score_dict = {"team_a": 0, "team_b": 0}
        try:
            if hasattr(match_log, '_final_state') and 'final_score' in match_log._final_state:
                final_score_dict = match_log._final_state['final_score']
        except Exception:
            pass

        a, b = final_score_dict.get("team_a", 0), final_score_dict.get("team_b", 0)

        # Update series.json and emit match-completed BEFORE PMEP runs.
        _update_series_json(match_number, per_match_id, final_score_dict)
        _append_event("match-completed", {
            "match_number": match_number,
            "match_id": per_match_id,
            "final_score": final_score_dict,
            "completed_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        })
        print(f"[season] match {match_number}/{season_length} complete | team_a {a} - team_b {b}", flush=True)

        if bypass_pmep:
            # Baseline mode (either --baseline or --strategy-a/--strategy-b):
            # no PMEP, no evolution. Strategy stays stable.
            print(f"[season] match {match_number}/{season_length} (baseline — no evolution)", flush=True)
        elif match_number >= season_length:
            # Last match — no next match to evolve for, skip PMEP.
            print(f"[season] match {match_number}/{season_length} complete — final match, no evolution needed", flush=True)
        else:
            print(f"[season] match {match_number}/{season_length} evolving...", flush=True)
            _append_event("pmep-running", {
                "match_number": match_number,
                "started_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            })

            # Story 004: PMEP gather + result inspection
            from src.foundation.post_match_evolution_pipeline import evolve_strategy, EvolutionFailedError
            from src.foundation.strategy_storage import WriteFailedError

            # Pass `config` (not match_config) to PMEP so data_home derivation
            # still points at data/ (where llm-providers.yaml lives). Strategy
            # reads/writes use strategy_log_dir directly.
            _lang_a = (run_team_languages or {}).get("team_a", "python")
            _lang_b = (run_team_languages or {}).get("team_b", "python")
            pmep_results = await asyncio.gather(
                evolve_strategy(config, "team_a", match_log, match_number,
                                strategy_log_dir=strategy_log_dir,
                                on_event=_append_event,
                                language=_lang_a),
                evolve_strategy(config, "team_b", match_log, match_number,
                                strategy_log_dir=strategy_log_dir,
                                on_event=_append_event,
                                language=_lang_b),
                return_exceptions=True,
            )
            team_ids = ["team_a", "team_b"]
            failure_count = 0
            for team_id, result in zip(team_ids, pmep_results):
                if isinstance(result, EvolutionFailedError):
                    print(f"[PMEP-ERROR] {team_id}: EvolutionFailedError ({result.last_failure})", file=sys.stderr)
                    print(f"  [PMEP] {team_id}: FAILED ({result.last_failure}) — running prior strategy", flush=True)
                    failure_count += 1
                elif isinstance(result, WriteFailedError):
                    print(f"[PMEP-ERROR] {team_id}: WriteFailedError ({result})", file=sys.stderr)
                    print(f"  [PMEP] {team_id}: FAILED (write_error) — running prior strategy", flush=True)
                    failure_count += 1
                elif isinstance(result, Exception):
                    # Unexpected — propagate
                    raise result
                else:
                    next_version = match_number + 1
                    print(f"  [PMEP] {team_id}: strategy_v{next_version}.py written", flush=True)

            if failure_count == 2:
                print("[PMEP-ERROR] both teams failed evolution — possible systemic issue", file=sys.stderr)

    # Finalize series.json with winner/status (arena mode only).
    if arena_s_dir is not None:
        series_score = {"team_a": 0, "team_b": 0}
        try:
            data = _json.loads((arena_s_dir / "series.json").read_text(encoding="utf-8"))
            series_score = data.get("score", series_score)
        except Exception:
            pass
        _finalize_series_json(series_score)

    # Story 005: closure line
    print(f"[season] season complete | {season_length} matches played", flush=True)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.command != "run":
        parser.error("only 'run' command is supported")
        return
    try:
        config = load_config(args.config)
    except Exception as exc:
        print(f"[agent_pitch] config load failed: {exc}", file=sys.stderr)
        sys.exit(1)

    # Apply --match-id override if supplied. The config is frozen=True
    # (Pydantic), so we construct a new MatchParams + new MatchConfig with
    # the override applied. Per ADR-0021, match_id is per-run and supplied
    # at start time, not persisted in the saved config.
    if args.match_id is not None:
        new_match = config.match.model_copy(update={"match_id": args.match_id})
        config = config.model_copy(update={"match": new_match})

    # Apply --log-dir override (HTTP API supplies <DATA_HOME>/matches/).
    if args.log_dir is not None:
        new_output = config.output.model_copy(update={"log_dir": args.log_dir})
        config = config.model_copy(update={"output": new_output})

    # Apply --seed override (UI Start sub-view's seed_override field).
    # The match section of MatchConfig is frozen, so model_copy a new one.
    if args.seed is not None:
        new_match = config.match.model_copy(update={"seed": args.seed})
        config = config.model_copy(update={"match": new_match})
        print(f"[cli] --seed override applied: config.match.seed = {args.seed}", flush=True)
    else:
        print(f"[cli] using config seed: {config.match.seed}", flush=True)

    # Apply --global-defaults overlay. The Config UI's Game tab writes to
    # this YAML; we read the simulation-relevant subset and overlay it onto
    # config.simulation so Game-tab edits take effect without each saved
    # match config carrying its own copy. Match-level fields stay per-match.
    if args.global_defaults is not None:
        import yaml as _yaml
        from pydantic import ValidationError as _ValidationError
        gd_path = Path(args.global_defaults)
        if gd_path.exists():
            try:
                gd_data = _yaml.safe_load(gd_path.read_text()) or {}
            except (_yaml.YAMLError, OSError) as exc:
                print(f"[cli] --global-defaults parse failed (ignored): {exc}", file=sys.stderr)
                gd_data = {}
            sim_fields = set(type(config.simulation).model_fields.keys())
            overrides = {k: v for k, v in gd_data.items() if k in sim_fields}
            if overrides:
                try:
                    # Construct a new SimulationConfig (rather than model_copy
                    # with `update=`) so Pydantic re-runs field validators.
                    # model_copy(update=...) bypasses validation in v2 — a
                    # bad value (e.g. goal_reset_ticks=9999) would silently
                    # land in the runtime config without this.
                    SimulationCls = type(config.simulation)
                    merged_sim_data = {**config.simulation.model_dump(), **overrides}
                    new_sim = SimulationCls(**merged_sim_data)
                    config = config.model_copy(update={"simulation": new_sim})
                    print(f"[cli] --global-defaults applied: {len(overrides)} simulation overrides "
                          f"({sorted(overrides.keys())})", flush=True)
                except (_ValidationError, TypeError, ValueError) as exc:
                    # Bad values in global-defaults shouldn't kill the match —
                    # log and fall back to whatever simulation values the
                    # match config already had (or SimulationConfig defaults).
                    print(f"[cli] --global-defaults overlay rejected (kept current simulation): {exc}",
                          file=sys.stderr)
        else:
            print(f"[cli] --global-defaults path does not exist: {gd_path}", file=sys.stderr)

    # Arena mode: log the series ID so the arena events.jsonl can be correlated.
    # The actual strategy-file-copy behaviour (writing strategy_v<N>.py to the
    # arena series strategies dir) is a follow-up task; this flag is accepted
    # and forwarded so the subprocess contract is stable.
    if args.arena_id is not None:
        print(f"[cli] arena mode: series_id={args.arena_id}", flush=True)

    # Per-team provider/model overrides (from Arena New-series form).
    # These override the global llm-providers.yaml via the deprecated
    # llm_provider/llm_model TeamConfig fields — which get_team_llm_settings()
    # still honours when explicitly set (ADR-0021 graceful migration path).
    if args.provider_a is not None or args.provider_b is not None:
        from src.secrets_store import get_api_key as _get_api_key
        _data_home = Path(config.output.log_dir).parent

    if args.provider_a is not None:
        _api_key_a = _get_api_key(_data_home, args.provider_a) or ""
        new_team_a = config.team_a.model_copy(
            update={"llm_provider": args.provider_a,
                    "llm_model": args.model_a or config.team_a.llm_model,
                    "api_key": _api_key_a}
        )
        config = config.model_copy(update={"team_a": new_team_a})
        print(f"[cli] --provider-a override: {args.provider_a}/{args.model_a}", flush=True)
    if args.provider_b is not None:
        _api_key_b = _get_api_key(_data_home, args.provider_b) or ""
        new_team_b = config.team_b.model_copy(
            update={"llm_provider": args.provider_b,
                    "llm_model": args.model_b or config.team_b.llm_model,
                    "api_key": _api_key_b}
        )
        config = config.model_copy(update={"team_b": new_team_b})
        print(f"[cli] --provider-b override: {args.provider_b}/{args.model_b}", flush=True)

    # Per-team strategies must be both-or-neither
    if (args.strategy_a is None) != (args.strategy_b is None):
        parser.error("--strategy-a and --strategy-b must be used together")

    try:
        asyncio.run(_run_season(
            args.config, args.season_length, config,
            baseline_path=args.baseline,
            strategy_a_path=args.strategy_a,
            strategy_b_path=args.strategy_b,
            language_a=args.language_a,
            language_b=args.language_b,
            arena_id=args.arena_id,
            arena_dir=args.arena_dir,
        ))
    except KeyboardInterrupt:
        print("[agent_pitch] Season aborted.", file=sys.stdout)
        sys.exit(130)


__all__ = ["main", "_run_season", "_build_parser"]