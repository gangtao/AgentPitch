#!/usr/bin/env python3
"""Bundle an AgentPitch match into a self-contained HTML viewer.

Usage:
    python tools/bundle_match.py data/matches/<match_dir>

Output:
    tools/match-viewer-bundled-<match_id>.html
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def parse_match_dir(match_dir: Path) -> dict:
    """Read match_dir and return { meta, ticks, strategies }.

    Raises FileNotFoundError if meta.json or events.jsonl are missing.
    """
    meta_path = match_dir / "meta.json"
    events_path = match_dir / "events.jsonl"

    if not meta_path.exists():
        raise FileNotFoundError(f"meta.json not found in {match_dir}")
    if not events_path.exists():
        raise FileNotFoundError(f"events.jsonl not found in {match_dir}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    ticks = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    strategies: dict[str, str] | None = None
    for path in sorted(match_dir.iterdir()):
        if path.stem == "strategy_team_a":
            strategies = strategies or {}
            strategies["team_a"] = path.read_text(encoding="utf-8")
        elif path.stem == "strategy_team_b":
            strategies = strategies or {}
            strategies["team_b"] = path.read_text(encoding="utf-8")

    return {"meta": meta, "ticks": ticks, "strategies": strategies}


def bundle_match(viewer_html: str, match_data: dict) -> str:
    """Inject match_data as window.BUNDLED_MATCH into viewer_html.

    The script tag is inserted immediately after the opening <body> tag.
    """
    bundled_json = json.dumps(
        {
            "meta": match_data["meta"],
            "ticks": match_data["ticks"],
            "strategies": match_data["strategies"],
        },
        separators=(",", ":"),
        ensure_ascii=False,
    )
    inject = f"<script>window.BUNDLED_MATCH = {bundled_json};</script>"
    return viewer_html.replace("<body>", f"<body>\n{inject}", 1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bundle an AgentPitch match into a self-contained HTML viewer"
    )
    parser.add_argument("match_dir", help="Path to match directory")
    args = parser.parse_args()

    match_dir = Path(args.match_dir).resolve()
    if not match_dir.is_dir():
        print(f"Error: {match_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    viewer_path = Path(__file__).parent / "match-viewer.html"
    if not viewer_path.exists():
        print(f"Error: match-viewer.html not found at {viewer_path}", file=sys.stderr)
        sys.exit(1)

    try:
        match_data = parse_match_dir(match_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    viewer_html = viewer_path.read_text(encoding="utf-8")
    output_html = bundle_match(viewer_html, match_data)

    match_id = match_data["meta"].get("match_id", match_dir.name)
    output_path = Path(__file__).parent / f"match-viewer-bundled-{match_id}.html"
    output_path.write_text(output_html, encoding="utf-8")
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
