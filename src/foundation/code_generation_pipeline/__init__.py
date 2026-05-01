"""Code Generation Pipeline (CGP) — Feature-layer module for LLM strategy generation.

Orchestrates SPB → PAL → sandbox.compile → strategy_storage.
Provides exception classes and configuration constants for the pipeline.
"""

from src.foundation.code_generation_pipeline.types import (
    GenerationFailedError,
    PromptContextOverflowError,
)
from src.foundation.code_generation_pipeline.constants import (
    CGP_MAX_RETRIES,
    CGP_CONTEXT_LIMIT_TOKENS,
)
from src.foundation.code_generation_pipeline.extraction import (
    extract_decide_code,
)
from src.foundation.code_generation_pipeline.generate import (
    generate_strategy,
)

__all__ = [
    "GenerationFailedError",
    "PromptContextOverflowError",
    "CGP_MAX_RETRIES",
    "CGP_CONTEXT_LIMIT_TOKENS",
    "extract_decide_code",
    "generate_strategy",
]