"""Unified entry point for the `agent-pitch` console script.

Dispatches `agent-pitch run ...` to the CLI orchestrator and `agent-pitch serve ...`
to the HTTP server. Each subcommand keeps its own argparse parser so `--help`
output remains specific to the chosen subcommand.

Wired up by `[project.scripts]` in pyproject.toml. The two existing entry
functions (`src.orchestration.cli:main` and `src.api.http_server:serve_main`)
remain importable for direct use.
"""

from __future__ import annotations

import sys


_USAGE = "usage: agent-pitch {run|serve|generate-strategy|cup-run|league-run} [options]"


def main() -> None:
    if len(sys.argv) < 2:
        print(_USAGE, file=sys.stderr)
        sys.exit(2)

    cmd = sys.argv[1]

    if cmd == "run":
        # orchestration.cli.main expects the "run" subcommand to remain in argv
        # (its argparse defines a `run` subparser). Pass through unchanged.
        from src.orchestration.cli import main as run_main
        run_main()
    elif cmd == "serve":
        # serve_main parses options only — strip the "serve" word from argv so
        # its parser doesn't see it as an unknown positional.
        from src.api.http_server import serve_main
        sys.argv = [f"{sys.argv[0]} serve"] + sys.argv[2:]
        serve_main()
    elif cmd == "generate-strategy":
        # Spawned by POST /api/strategies/generate. The CLI module reads
        # sys.argv[2:] directly, so leave the subcommand word in argv[1].
        from src.orchestration.cli.generate_strategy import main as gen_main
        gen_main()
    elif cmd == "cup-run":
        # Spawned by POST /api/cups to orchestrate a single-elimination cup.
        # cup_runner.main() strips 'cup-run' from argv before its own argparse.
        from src.orchestration.cli.cup_runner import main as cup_run_main
        cup_run_main()
    elif cmd == "league-run":
        # league_runner.main() strips 'league-run' from argv before its own argparse.
        from src.orchestration.cli.league_runner import main as league_run_main
        league_run_main()
    elif cmd in ("-h", "--help"):
        print(_USAGE)
        print()
        print("Subcommands:")
        print("  run                 Execute a season of matches (CGP -> TickEngine -> PMEP)")
        print("  serve               Start the FastAPI HTTP server for the browser frontend")
        print("  generate-strategy   Generate one strategy via LLM (used by the UI subprocess)")
        print("  cup-run             Orchestrate a single-elimination cup tournament")
        print("  league-run          Orchestrate a round-robin league tournament")
        sys.exit(0)
    else:
        print(f"agent-pitch: unknown command {cmd!r}", file=sys.stderr)
        print(_USAGE, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
