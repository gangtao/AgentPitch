"""--knockout flag flips config.simulation.knockout (issue #83)."""
from src.orchestration.cli import _build_parser  # adjust if helper name differs


def test_knockout_flag_parses_true():
    parser = _build_parser()
    args = parser.parse_args([
        "run", "--config", "x.yaml", "--season-length", "1", "--knockout",
    ])
    assert args.knockout is True


def test_knockout_absent_defaults_false():
    parser = _build_parser()
    args = parser.parse_args(["run", "--config", "x.yaml", "--season-length", "1"])
    assert args.knockout is False
