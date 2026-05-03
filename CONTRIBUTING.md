# Contributing to AgentPitch

Thank you for your interest in contributing! This guide covers how to set up your environment, run tests, and submit changes.

## Prerequisites

- Python 3.11+
- Rust toolchain (for Wasmtime/WASM sandbox support)

## Setup

```bash
# Clone the repo
git clone https://github.com/gangtao/AgentPitch.git
cd AgentPitch

# Install with all sandbox backends and dev dependencies
pip install -e '.[all,dev]'

# Install Rust WASM target (required for .rs strategy tests)
rustup target add wasm32-wasip1
```

## Running tests

```bash
make test          # run the full test suite
make test-cov      # run tests with coverage report (≥80% required)

# Run a single test file
pytest tests/unit/test_player_id_format.py
```

All tests must pass before submitting a PR. The CI pipeline runs `pytest` automatically on every push and pull request.

## Project structure

```
src/
  foundation/       core engine: sandboxes, LLM abstraction, code generation
  core/             game state manager, movement & physics
  orchestration/    tick engine (composition root)
  api/              FastAPI HTTP server + browser UI
  cli.py            CLI entry point
tests/
  unit/             fast, no I/O, no LLM calls
  integration/      may touch filesystem
  performance/      benchmark smoke tests
data/
  global-defaults.yaml   simulation constants
  llm-providers.yaml     LLM provider configuration
```

## Architecture notes

- **Layer boundary**: `src/api/` must not import from `src/foundation/`. See [docs/design.md](docs/design.md) for details.
- **Player IDs**: always strings in `"{team_id}_{index}"` format (e.g. `"team_a_0"`). Never integers.
- **Sandboxes**: strategy file extension selects the sandbox — `.py`, `.js`, `.rs`.

## Submitting a pull request

1. Fork the repo and create a branch from `main`.
2. Make your changes and add tests where appropriate.
3. Ensure `make test` passes locally.
4. Open a PR against `main` with a clear description of what and why.

## Reporting issues

Open an issue on GitHub with steps to reproduce, expected behavior, and actual behavior. Include your Python version and OS.

## Code style

- Follow existing patterns in the codebase.
- Keep functions small and focused.
- Avoid adding comments that describe *what* the code does — only add them when the *why* is non-obvious.
