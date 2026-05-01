"""CGP module constants — configuration values for the generation pipeline.

Per GDD Tuning Knobs section. These values control retry behavior and
context length management across the entire pipeline.
"""

from __future__ import annotations

#: Maximum number of generation attempts before raising GenerationFailedError
CGP_MAX_RETRIES: int = 3

#: Token limit for prompt construction (prevents context overflow)
CGP_CONTEXT_LIMIT_TOKENS: int = 16_000