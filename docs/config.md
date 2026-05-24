# Config

The **Config** section is the central control panel for AgentPitch. It is divided into five tabs — **Game**, **Match**, **Teams**, **LLM**, and **Storage** — each governing a distinct aspect of the simulation.

Navigate to Config from the left sidebar at any time. Changes take effect on the next match start unless otherwise noted. Every tab has **Discard** and **Save** buttons; use **Reset to Defaults** to restore factory values.

---

## Game tab

![Game config](imgs/config/config_game.png)

The Game tab controls global simulation physics and timing constants that apply to every match. These values are loaded from `data/global-defaults.yaml` and saved back there on **Save**.

### A. Match defaults

| Field | Default | Unit | Description |
|-------|---------|------|-------------|
| Tick Rate | `10` | ticks/sec | How many simulation steps run per real second. Higher values increase physics fidelity at the cost of CPU. |
| Duration | `5` | minutes | Length of a match (full 90 minutes = two halves of 45). |
| Field Width | `100` | units | Horizontal span of the pitch. |
| Field Height | `60` | units | Vertical span of the pitch. |
| Goal Height | `7.32` | units | Width of the goal mouth (standard real-world ratio). |
| Default Seed | `42` | integer | Random seed used when a match config does not specify one, ensuring reproducible results. |

### B. Action mechanics

These knobs govern how player actions resolve during each tick.

| Field | Default | Unit | Description |
|-------|---------|------|-------------|
| Action Cooldown | `10` | ticks | Minimum ticks between successive actions per player (1 second at the default tick rate). |
| Pass Max Deviation | `8` | units | Maximum positional error added to a pass at skill = 1. Error scales down as skill rises. |
| Shot Max Angle | `0.3` | radians | Maximum angular deviation for a shot at minimum skill. |
| Tackle Clean Share | `0.55` | fraction | Probability that a successful tackle cleanly wins the ball (vs. a loose deflection). |
| Tackle Blocked Floor | `0.15` | fraction | Minimum deflection probability even on a failed tackle. |
| Tackle Block Speed Min | `1` | u/tick | Minimum speed of a deflected ball after a blocked tackle. |

The Game tab also exposes additional sections (C–F) for goalkeeper physics, stamina, match-flow timing, and formation snap — all scrollable below the visible area.

### C. Goalkeeper / ball physics

Controls how the goalkeeper interacts with shots and how the ball behaves on deflections.

| Field | Default | Description |
|-------|---------|-------------|
| GK Caught Share | `0.60` | Fraction of saves resulting in a clean catch (vs. a parry). |
| GK Block Speed Factor | `0.40` | Speed multiplier applied to the ball on a parried save. |
| Ball Control Range GK | `1.5` | Radius within which the GK can claim the ball. |
| Ball Control Range Outfield | `1.0` | Radius within which outfield players can claim the ball. |

### D. Stamina / health

| Field | Default | Description |
|-------|---------|-------------|
| Health Max | `100` | Maximum health/stamina for each player. |
| Health Drain Factor | `1.0` | Global multiplier on health drain per tick. Increase to make matches more physically demanding. |
| Health Floor | `0.6` | Minimum effectiveness multiplier when a player is exhausted (60% at zero stamina). |

### E. Match-flow timing

| Field | Default | Unit | Description |
|-------|---------|------|-------------|
| Goal Reset Ticks | `30` | ticks | Pause after a goal before kick-off resumes. |
| Half-time Pause Ticks | `60` | ticks | Pause at half-time before the second half begins. |
| Min Player Separation | `1.0` | units | Minimum enforced distance between players to prevent overlap. |

### F. Formation system

| Field | Default | Description |
|-------|---------|-------------|
| Formation Snap | `off` | When enabled, the engine nudges each player toward their dynamic phase-aware formation anchor each tick. Off by default — strategies fully own positioning. Turn on for a system-assisted helper. |

---

## Match tab

![Match list](imgs/config/config_match.png)

The Match tab manages named match configurations. Each configuration is a reusable preset that defines match parameters and references two teams by slug. Configurations are stored as YAML files under `data/configs/`.

Two built-in configurations ship out of the box:

| Name | Teams | Duration | Field |
|------|-------|----------|-------|
| `5v5` | Red Lions (5) vs Blue Sharks (5) | 5 min | 60 × 40 |
| `11v11` | Red Lions vs Blue Sharks | 5 min | 100 × 60 |

Click **+ New Config** to create a new one, or **Edit** to modify an existing one.

### Creating / editing a match config

![Match config form](imgs/config/config_match_glob.png)

Give the configuration a unique **Configuration Name**. Then set the match parameters:

| Field | Description |
|-------|-------------|
| Seed | Random seed for this specific config (overrides the global default). |
| Tick Rate | Ticks per second for this match. |
| Duration | Match length in minutes. |
| Field Width | Pitch width in game units. |
| Field Height | Pitch height in game units. |

### Team selection

![Team selection](imgs/config/config_match_team_selection.png)

Below the match parameters, pick the two teams that will play. **Team A** and **Team B** are dropdowns populated from the team configs managed in the **Teams** tab — pick any pair from the list. Roster sizes and per-player attributes are owned by the team configs themselves; the match config only references them by slug.

To create, edit, or delete teams, switch to the **Teams** tab (next section).

Click **Save** to write the configuration to disk. Click **Back to list** (top-right) to return without saving.

---

## Teams tab

![Teams list](imgs/config/config_teams.png)

The Teams tab manages named team configurations. Each team is a reusable roster that can be referenced from any match config. Team configs are stored as YAML files under `data/configs/teams/<slug>.yaml`.

Four built-in teams ship out of the box:

| Slug | Display name | Size |
|------|--------------|------|
| `red` | Red Lions | 11 |
| `blue` | Blue Sharks | 11 |
| `red5` | Red Lions (5) | 5 |
| `blue5` | Blue Sharks (5) | 5 |

Each row in the list shows the slug, display name, and roster size. Use **Edit** to open the team in the editor, **Delete** to remove it (refused with an inline error if any match config still references the slug), or **+ New team** to create a new one.

### Creating / editing a team

![Teams editor](imgs/config/config_teams_edit.png)

| Field | Description |
|-------|-------------|
| Team ID (slug) | Filename stem. Must match `^[a-z0-9_-]+$`. Read-only when editing an existing team. |
| Display name | 1–64 character free-text name shown in the live and replay viewers, match list, and cup pages. |

Below the team header, the roster grid lists 5–11 players. Use **+ Add Player** to grow the squad and the × button to remove a row (disabled when only five players remain).

Each player row has:

| Column | Range | Description |
|--------|-------|-------------|
| Name | up to 64 chars | Display name shown above the dot in the live viewer and in the event feed. Blank → defaults to `Player {N}`. |
| # | 0–99 | Jersey number. Blank → auto-numbered from the row index at match start. |
| Role | GK / DEF / MID / FWD | Position on the pitch. Exactly one GK per team. |
| SPD (Speed) | 1–20 | Movement speed per tick. |
| SKL (Skill) | 1–20 | Reduces error on passes and shots. |
| STR (Strength) | 1–20 | Tackle success rate and physical duels. |
| SAV (Save) | 0–20 | Goalkeeper-only. Save success probability. Disabled and shows `—` for outfield rows. |
| DIS (Discipline) | 1–20 | Reduces chance of conceding fouls. |
| DRB (Dribbling) | 1–20 | Ball retention while moving. |
| PAS (Passing) | 1–20 | Pass accuracy. Blank → falls back to SKL. |
| SHO (Shooting) | 1–20 | Shot power and accuracy. Blank → falls back to SKL. |
| STA (Stamina) | 1–20 | Rate of health drain. Blank → defaults to 10. |

Leaving any numeric field blank falls back to the role-based default from `ROLE_DEFAULTS` (GK=10 skill, DEF=8 skill, MID=16 skill, FWD=14 skill, etc.), so the bundled teams ship with only `name` and `role` per player and rely on those defaults.

Click **Save** to write the team to disk. Click **Back to list** (top-right) to return without saving.

---

## LLM tab

![LLM config](imgs/config/config_llm.png)

The LLM tab configures the AI providers that generate and evolve player strategies. Each provider panel exposes:

| Field | Description |
|-------|-------------|
| API Key | Secret key for authentication. Stored in the secrets file, never in YAML. Use **Reveal** to view, **Clear** to remove. |
| URL | Base endpoint for the provider's API. |
| Model | Which model to use for code generation (selected from a dropdown of known models). |
| Connection Test | Validates the key and endpoint with a live API call. Status shows **OK** (green), **Not tested** (amber), or an error. |

Built-in providers configured out of the box:

| Provider | Default Model | Endpoint |
|----------|--------------|----------|
| OpenAI | `gpt-4o` | `https://api.openai.com/v1` |
| Anthropic | `claude-sonnet-4-6` | `https://api.anthropic.com` |
| Gemini | `gemini-2.0-flash` | `https://generativelanguage.googleapis.com` |
| DeepSeek | `deepseek-v4-flash` | `https://api.deepseek.com` |
| OpenRouter | `ai21/jamba-large-1.7` | `https://openrouter.ai/api/v1` |
| Ollama | `qwen2.5-coder:7b` | `http://localhost:11434/v1/` (local) |

### Custom providers

![Custom provider](imgs/config/config_llm_customer_config.png)

Click **+ Add Custom Provider** at the bottom of the LLM tab to add any OpenAI-compatible endpoint (e.g. vLLM, LM Studio, Azure OpenAI). Custom providers have the same fields as built-in ones and include a **Remove** button to delete them.

API keys are resolved in this priority order: UI field → environment variable → secrets file.

---

## Storage tab

The Storage tab sets the **data home** directory — the root folder where AgentPitch persists strategies, match configs, logs, and provider settings.

| Field | Default | Description |
|-------|---------|-------------|
| Data Home | `./data` | Absolute or `~`-relative path to the data directory. The path must exist and be writable, or its parent must be writable so AgentPitch can create it. Paths with `..` components are rejected. |

Changes to Data Home take effect after the next server restart.
