"""System Prompt Builder package.

Re-exports the public surface defined across this subpackage.
"""

from src.foundation.system_prompt_builder.build import (
    build_evolution_prompt,
    build_generation_prompt,
)
from src.foundation.system_prompt_builder.helpers import (
    SPB_MAX_KEY_EVENTS,
    SPB_TOKEN_CHARS_RATIO,
    SPB_WARN_TOKEN_THRESHOLD,
    estimate_tokens,
    warn_if_over_threshold,
)
from src.foundation.system_prompt_builder.templates import (
    TemplateLoadError,
    TemplateRenderError,
    get_template,
    load_templates,
)
from src.foundation.system_prompt_builder.types import PromptMode, PromptResult

__all__ = [
    "PromptMode",
    "PromptResult",
    "TemplateLoadError",
    "TemplateRenderError",
    "load_templates",
    "get_template",
    "estimate_tokens",
    "warn_if_over_threshold",
    "SPB_WARN_TOKEN_THRESHOLD",
    "SPB_MAX_KEY_EVENTS",
    "SPB_TOKEN_CHARS_RATIO",
    "build_generation_prompt",
    "build_evolution_prompt",
]
