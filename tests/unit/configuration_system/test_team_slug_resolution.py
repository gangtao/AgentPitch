"""Tests for the team-slug resolution path in load_config."""
from __future__ import annotations

import os

import pytest

from src.foundation.config_errors import ConfigError
from src.foundation.config_loader import load_config


def _write(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)


MIN_TEAM_BODY = """\
team_id: {slug}
name: {name}
players:
  - name: Alex
    role: GK
    save: 16
  - role: DEF
  - role: DEF
  - role: MID
  - role: FWD
"""


def _seed_teams(tmp_path, *, a_slug="red", a_name="Red", b_slug="blue", b_name="Blue"):
    configs = tmp_path / "configs"
    teams = configs / "teams"
    _write(teams / f"{a_slug}.yaml", MIN_TEAM_BODY.format(slug=a_slug, name=a_name))
    _write(teams / f"{b_slug}.yaml", MIN_TEAM_BODY.format(slug=b_slug, name=b_name))
    return configs


def _write_match(configs_dir, body):
    path = configs_dir / "match.yaml"
    _write(path, body)
    return str(path)


def test_resolves_slugs_to_team_configs(tmp_path):
    configs = _seed_teams(tmp_path)
    match_yaml = f"""\
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 5
  field_width: 60.0
  field_height: 40.0
output:
  log_dir: {tmp_path / 'logs'}
team_a: red
team_b: blue
"""
    cfg = load_config(_write_match(configs, match_yaml))

    assert cfg.team_a.team_id == "red"
    assert cfg.team_a.name == "Red"
    assert cfg.team_b.team_id == "blue"
    assert cfg.team_b.name == "Blue"
    assert cfg.team_a.players[0].player_id == "team_a_0"
    assert cfg.team_a.players[0].name == "Alex"
    assert cfg.team_b.players[1].name == "Player 2"  # defaulted


def test_missing_team_file_errors(tmp_path):
    configs = _seed_teams(tmp_path)
    match_yaml = f"""\
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 5
  field_width: 60.0
  field_height: 40.0
output:
  log_dir: {tmp_path / 'logs'}
team_a: missing
team_b: blue
"""
    with pytest.raises(ConfigError) as excinfo:
        load_config(_write_match(configs, match_yaml))
    assert "missing" in str(excinfo.value) and "teams" in str(excinfo.value)


def test_slug_filename_mismatch_errors(tmp_path):
    configs = _seed_teams(tmp_path)
    # Overwrite red.yaml with mismatching team_id
    _write(configs / "teams" / "red.yaml", MIN_TEAM_BODY.format(slug="rouge", name="Red"))
    match_yaml = f"""\
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 5
  field_width: 60.0
  field_height: 40.0
output:
  log_dir: {tmp_path / 'logs'}
team_a: red
team_b: blue
"""
    with pytest.raises(ConfigError) as excinfo:
        load_config(_write_match(configs, match_yaml))
    msg = str(excinfo.value)
    assert "red" in msg and "rouge" in msg


def test_inline_dict_rejected_with_migration_hint(tmp_path):
    configs = _seed_teams(tmp_path)
    match_yaml = f"""\
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 5
  field_width: 60.0
  field_height: 40.0
output:
  log_dir: {tmp_path / 'logs'}
team_a:
  players:
    - role: GK
team_b: blue
"""
    with pytest.raises(ConfigError) as excinfo:
        load_config(_write_match(configs, match_yaml))
    assert "slug" in str(excinfo.value).lower()
    assert "teams" in str(excinfo.value)


def test_non_string_non_dict_rejected(tmp_path):
    configs = _seed_teams(tmp_path)
    match_yaml = f"""\
match:
  seed: 42
  tick_rate: 10
  duration_minutes: 5
  field_width: 60.0
  field_height: 40.0
output:
  log_dir: {tmp_path / 'logs'}
team_a: 42
team_b: blue
"""
    with pytest.raises(ConfigError):
        load_config(_write_match(configs, match_yaml))
