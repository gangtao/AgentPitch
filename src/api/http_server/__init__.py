"""HTTP server entry point and console script."""
import argparse
import sys

from src.api.http_server.app import create_app


def serve_main():
    """Console entry point for agent_pitch serve command."""
    parser = argparse.ArgumentParser(prog="agent_pitch serve")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8765, help="Server port")
    # --data-dir is the canonical flag (server owns the data root). All
    # subdirs derive from it: <data-dir>/configs/, /strategies/, /matches/,
    # /arena/, /llm-providers.yaml, /.secrets.json.
    # --log-dir kept as a deprecated alias for backward compatibility.
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Data root directory. All subdirs (configs/, strategies/, matches/, arena/) "
             "live under this path. Default: ./data. The UI Storage tab is read-only — "
             "this flag is the only way to change the data root.",
    )
    parser.add_argument(
        "--log-dir",
        default=None,
        help="DEPRECATED: alias for --data-dir. Use --data-dir instead.",
    )
    args = parser.parse_args()

    # Resolve effective data directory: --data-dir wins; --log-dir is a
    # backward-compat alias; default is ./data.
    if args.data_dir is not None:
        data_dir = args.data_dir
    elif args.log_dir is not None:
        data_dir = args.log_dir
        print(
            "[agent_pitch serve] WARNING: --log-dir is deprecated; use --data-dir instead.",
            file=sys.stderr,
        )
    else:
        data_dir = "./data"

    try:
        app = create_app(log_dir=data_dir)
    except RuntimeError as e:
        print(f"[agent_pitch serve] {e}", file=sys.stderr)
        sys.exit(1)

    import uvicorn
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


__all__ = ["create_app", "serve_main"]