# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Agent Pitch is an LLM-powered soccer simulation where each player is an AI agent that writes its own `decide()` callback in Python, JavaScript, or Rust. Strategies are generated and evolved between matches by calling LLM APIs; all generated code runs inside language-specific sandboxes.

## Commands

```bash
# Install with all sandbox backends (JS via QuickJS, WASM via Wasmtime)
make install          # pip install -e '.[all]'

# Run tests
make test             # pytest
make test-cov         # pytest --cov
pytest tests/unit/test_player_id_format.py   # run a single test file

# Start the HTTP server + browser UI (port 8765)
make serve            # agent-pitch serve --data-dir ./data

# Docker
make docker-build && make docker-up   # build + run via docker compose
make docker-image && make docker-run  # build + run standalone image
```

The CLI entry point `agent-pitch` dispatches to:
- `agent-pitch run` — execute a season of matches
- `agent-pitch serve` — start the FastAPI HTTP server
- `agent-pitch generate-strategy` — generate one strategy via LLM (used by the UI subprocess)
- `agent-pitch cup-run` / `agent-pitch league-run` — tournament orchestration

## Architecture

### Data flow (per match)

```
Config (YAML/API) → MatchConfig
  → Code Generation Pipeline (CGP): LLM generates decide() code
  → Sandbox: compile + cache the decide() callback
  → Tick Engine: runs ticks until match ends
      each tick: GameStateManager.build_tick_snapshot()
               → Sandbox.execute() → Action
               → ActionResolutionEngine.resolve()
               → PlayerMovementSystem / BallPhysicsSystem mutate state
               → MatchLog records tick
  → Post-Match Evolution Pipeline (PMEP): LLM evolves strategy based on match log
```

### Layer boundaries (ADR-0006)

The `src/api/` layer must **not** import from `src/foundation/`. API-layer Pydantic models (in `src/api/http_server/`) mirror `src/foundation/config_models.py` independently. Cross-layer exceptions: `src/secrets_store.py` and `src/strategy_library.py` (pure file I/O, no engine code).

### Key modules

| Path | Responsibility |
|------|---------------|
| `src/foundation/action.py` | `Action` base class + `Move`, `Pass`, `Shoot`, `Tackle`, `Hold` frozen dataclasses returned by every `decide()` |
| `src/foundation/decide_contract.py` | Signature verification and reference invocation harness for `decide(game_state, player_state, history)` callbacks |
| `src/foundation/game_state_schema.py` | `GameStateDict` TypedDict + runtime validator; player IDs are `str` in format `{team_id}_{index}` (ADR-0004) |
| `src/foundation/sandbox/` | `SandboxFactory` dispatches `.py` → `RestrictedPythonSandbox`, `.js` → `QuickJSSandbox`, `.rs` → `WasmtimeSandbox` |
| `src/foundation/provider_abstraction/` | `PAL` — single async `generate()` entry point for all LLM calls; adapters for OpenAI, Anthropic, Gemini |
| `src/foundation/code_generation_pipeline/` | CGP: builds prompt → calls PAL → extracts code → compiles in sandbox (retry loop) |
| `src/foundation/post_match_evolution_pipeline/` | PMEP: reads prior strategy + match log → builds evolution prompt → calls PAL → compiles (retry loop) |
| `src/foundation/system_prompt_builder/` | Jinja2 templates for generation and evolution prompts |
| `src/foundation/action_resolution_engine/` | Translates `Action` instances into physics mutations |
| `src/core/game_state_manager.py` | Holds authoritative match state; builds per-tick snapshots |
| `src/core/player_movement_system.py` / `ball_physics_system.py` | Stateless functions that mutate game state |
| `src/orchestration/tick_engine/` | Composition root: constructs all 7 subsystems, runs tick loop |
| `src/api/http_server/app.py` | FastAPI app; spawns CLI subprocesses for strategy generation, cup-run, league-run |
| `data/global-defaults.yaml` | Default simulation constants (field size, tick rate, physics knobs) |

### Player ID convention (ADR-0004)

All player IDs are strings with format `"{team_id}_{index}"` — e.g. `"team_a_0"`, `"team_b_3"`. Never integers. `team_id` is always `"team_a"` or `"team_b"`.

### Sandbox multi-language support

Strategy files use their extension to select a sandbox: `.py` (always available), `.js` (requires `quickjs` optional dep), `.rs` (requires `wasmtime` optional dep — compiles Rust to WASM per match). The `[all]` extras group installs both optional backends.

### pytest layout

- `tests/unit/` — fast, no I/O, no LLM calls
- `tests/integration/` — may touch file system
- `tests/performance/` — benchmark smoke tests
- `tests/conftest.py` — shared fixtures (`all_player_ids`, `team_a_ids`, `team_b_ids`)
- `pythonpath = ["."]` is set in `pyproject.toml` so `from tests.unit.x import ...` resolves from repo root
