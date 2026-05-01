"""SPB Jinja2 template loader + cache + version extraction.

Per ADR-0007 adapter-cache pattern: load once at process startup,
read-only for the lifetime of the process. Mid-process template edits are
NOT picked up — researchers must restart (per GDD EC-SPB-06).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from jinja2 import Environment, Template
from jinja2 import exceptions as jinja_exceptions

from src.foundation.system_prompt_builder.types import PromptMode


class TemplateLoadError(Exception):
    """Raised when a template file cannot be parsed at startup. Blocks process start."""


class TemplateRenderError(Exception):
    """Raised when a template renders to empty/whitespace-only output for valid input."""


@dataclass(frozen=True)
class _LoadedTemplate:
    template: Template
    version: str


_TEMPLATE_FILES: Dict[PromptMode, str] = {
    PromptMode.GENERATION: "generation.jinja2",
    PromptMode.GENERATION_JS: "generation-js.jinja2",
    PromptMode.GENERATION_RUST: "generation-rust.jinja2",
    PromptMode.EVOLUTION: "evolution.jinja2",
    PromptMode.EVOLUTION_JS: "evolution-js.jinja2",
    PromptMode.EVOLUTION_RUST: "evolution-rust.jinja2",
}

# Prompt files ship inside the package so loading does not depend on cwd.
# Override via the asset_dir argument when researchers want to test custom prompts.
_DEFAULT_PROMPT_DIR = Path(__file__).parent / "prompt_files"

_VERSION_PATTERN = re.compile(r"\{#\s*version:\s*(\S+)\s*#\}")

_template_cache: Dict[PromptMode, _LoadedTemplate] = {}


def _make_dummy_context() -> dict:
    """Minimal context for the load-time test render.

    Generation v2.5 uses one substitution (`user_intent`); evolution v2.0
    uses two (`prev_strategy`, `match_summary`). Every kwarg is passed to
    every template — Jinja silently ignores ones the template doesn't
    reference, so this single dict satisfies both load-time renders.
    `user_intent` is empty so the load-time render exercises the
    fallback branch (catches a regression that breaks the {% else %}).
    """
    return {
        "user_intent": "",
        "prev_strategy": "def decide(g, p, h): return Hold()",
        "match_summary": "summary text",
    }


def load_templates(asset_dir: str | Path | None = None) -> None:
    """Parse the Jinja2 templates and populate _template_cache.

    Defaults to the package-shipped prompts at
    ``src/foundation/system_prompt_builder/prompt_files/``. Pass ``asset_dir``
    to load alternate templates (e.g., researcher experiments).

    Test-renders each template with dummy data at load time so syntactic and
    vacuous-render errors fire here (not mid-match). Atomic — if either
    template fails, the cache is left unchanged.

    Raises:
        TemplateLoadError: file missing, invalid Jinja2 syntax, missing version comment.
        TemplateRenderError: test render produces empty/whitespace-only output.
    """
    base = Path(asset_dir) if asset_dir is not None else _DEFAULT_PROMPT_DIR
    env = Environment(autoescape=False)  # plain text — no HTML escaping
    new_cache: Dict[PromptMode, _LoadedTemplate] = {}

    for mode, filename in _TEMPLATE_FILES.items():
        path = base / filename
        if not path.exists():
            raise TemplateLoadError(f"Template not found: {path}")
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as e:
            raise TemplateLoadError(f"Cannot read template {path}: {e}") from e

        version_match = _VERSION_PATTERN.search(source)
        if version_match is None:
            raise TemplateLoadError(
                f"Template {path} missing required {{# version: X #}} comment"
            )
        version = version_match.group(1)

        try:
            template = env.from_string(source)
        except jinja_exceptions.TemplateError as e:
            raise TemplateLoadError(
                f"Template {path} has invalid Jinja2 syntax: {e}"
            ) from e

        # Test render with dummy data — catches vacuous templates + render-time errors
        try:
            test_output = template.render(**_make_dummy_context())
        except jinja_exceptions.TemplateError as e:
            raise TemplateLoadError(
                f"Template {path} render failed at load time: {e}"
            ) from e
        if not test_output.strip():
            raise TemplateRenderError(f"Template {path} renders to empty output")

        new_cache[mode] = _LoadedTemplate(template=template, version=version)

    # Atomic replace — only commit cache if all templates loaded successfully
    _template_cache.clear()
    _template_cache.update(new_cache)


def get_template(mode: PromptMode) -> _LoadedTemplate:
    """Look up a template by mode. Requires `load_templates()` was called."""
    if mode not in _template_cache:
        raise RuntimeError(
            f"Template cache is empty for {mode}; call load_templates() at process start"
        )
    return _template_cache[mode]
