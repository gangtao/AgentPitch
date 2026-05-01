"""agent-pitch generate-strategy — standalone strategy generation for the UI.

Spawned as a subprocess by ``POST /api/strategies/generate`` so the HTTP
layer stays isolated from simulation modules (ADR-0006). Returns the
generated, sandbox-validated code on stdout — does NOT write to disk.
The HTTP caller forwards the code to the UI; the user picks a final name
and saves via the existing ``POST /api/strategies`` endpoint.

Output schema (single line on stdout):
    {"ok": true,  "code": str, "template_version": str}
    {"ok": false, "error": str}

Exit code: 0 on success, 1 on any failure (the JSON line carries detail).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from src.foundation.code_generation_pipeline.extraction import extract_decide_code
from src.foundation.sandbox import ExecutionStatus, Sandbox
from src.foundation.system_prompt_builder import build_generation_prompt, load_templates
from src.secrets_store import get_api_key


# Reasoning models (gpt-5.x, o1, o3) routinely take 1–3 minutes on complex
# prompts. Old chat models return in seconds. We size for the slow case so
# users with newer models don't see spurious timeouts. Retrying after a real
# timeout is pointless (the next attempt will also be slow), so attempts is
# kept low — the retry exists only to catch transient extract/compile errors,
# not slow LLMs.
_MAX_RETRIES = 2
_LLM_TIMEOUT_S = 180.0  # Per-attempt; total subprocess budget ≈ 360s + overhead.

_log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────
# CLI parsing
# ──────────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agent-pitch generate-strategy",
        description="Generate a single strategy via LLM, sandbox-validate, return the code.",
    )
    p.add_argument("--prompt", required=True, help="User intent — natural-language guidance for the LLM")
    p.add_argument("--provider", required=True, help="Provider name (built-in: openai/anthropic/gemini, or custom)")
    p.add_argument("--model", required=True, help="Provider-specific model id (e.g. gpt-4o, claude-sonnet-4-6)")
    p.add_argument("--data-dir", required=True, help="Path to data directory (used to read .secrets.json)")
    p.add_argument("--language", default="python", choices=["python", "javascript", "rust"],
                   help="Target language for the generated strategy")
    p.add_argument("--provider-type", default=None, help="Provider type for custom providers (e.g., openai_compatible)")
    p.add_argument("--base-url", default=None, help="Custom API endpoint URL for OpenAI-compatible providers")
    return p


# ──────────────────────────────────────────────────────────────────────────
# Key resolution — env var > <data-dir>/.secrets.json (mirrors ADR-0020)
# ──────────────────────────────────────────────────────────────────────────


def _resolve_api_key(provider: str, data_dir: Path) -> Optional[str]:
    """Thin wrapper over the shared `secrets_store.get_api_key` adding a
    diagnostic log line so failures are debuggable from subprocess stderr.

    Precedence (per ADR-0020): env var > <data-dir>/.secrets.json.
    """
    key = get_api_key(data_dir, provider)
    if key:
        _log.info("generate-strategy: %s key resolved", provider)
    else:
        secrets_path = (data_dir / ".secrets.json").resolve()
        _log.info("generate-strategy: %s key NOT resolved (env unset; checked %s, exists=%s)",
                  provider, secrets_path, secrets_path.exists())
    return key


# ──────────────────────────────────────────────────────────────────────────
# Provider calls — direct SDK use, no PAL (PAL requires MatchConfig)
# ──────────────────────────────────────────────────────────────────────────


# Token budget per LLM call. Generous enough for reasoning models that may
# spend a large chunk on internal thinking before emitting the answer.
_MAX_OUTPUT_TOKENS = 8000


def _smoke_inputs() -> tuple:
    """Mock (game_state, player_state, history) matching the prompt template's
    SECTION 2-4 schemas — minimal but typed so the strategy's first call doesn't
    trip on missing keys. Used only by the post-compile smoke test."""
    gs = {
        "tick": 0, "ticks_remaining": 1000, "match_phase": "in_play", "half": 1,
        "score": {"team_a": 0, "team_b": 0},
        "team_phase": {"team_a": "transitioning", "team_b": "transitioning"},
        "ball": {
            "position": (50.0, 30.0), "velocity": (0.0, 0.0),
            "possession": None, "carrier_id": None,
        },
        "players": {
            "team_a_0": {
                "team": "team_a", "role": "GK", "number": 0,
                "position": (5.0, 30.0), "formation_position": (5.0, 30.0),
                "has_ball": False,
            },
        },
        "field": {
            "width": 100.0, "height": 60.0,
            "team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
            "goal_top": 35.0, "goal_bottom": 25.0,
        },
        "my_team": "team_a", "my_player_id": "team_a_0",
    }
    ps = {
        "player_id": "team_a_0", "team": "team_a", "role": "GK", "number": 0,
        "position": (5.0, 30.0), "has_ball": False,
        "formation_position": (5.0, 30.0),
        "formation_zone": {"x": (0.0, 10.0), "y": (20.0, 40.0)},
        "formation_zone_phase": "transitioning",
        "speed": 8, "skill": 10, "strength": 8, "save": 16,
        "discipline": 14, "dribbling": 4, "passing": 10, "shooting": 10,
        "stamina": 15, "current_health": 100.0, "cooldown_remaining": 0,
    }
    return (gs, ps, [])


_ProviderResult = tuple[str, int, int]  # (text, input_tokens, output_tokens)


async def _call_openai(prompt: str, model: str, api_key: str, base_url: str | None = None) -> _ProviderResult:
    """Call OpenAI's chat-completions endpoint (or OpenAI-compatible endpoint).

    Uses ``max_completion_tokens`` (the modern replacement for ``max_tokens``;
    required by gpt-5.x, o1, o3, and other reasoning models — older chat
    models accept it too). No ``temperature`` override: several newer models
    reject anything other than the server default (1.0), and the quality
    delta vs. temperature=0.7 for a one-shot generation is small.

    Args:
        prompt: User prompt to send to the model
        model: Model identifier (e.g., gpt-4o, qwen2.5-coder:7b)
        api_key: API key for authentication
        base_url: Optional custom base URL for OpenAI-compatible APIs (ollama, vllm)
    """
    import openai
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = openai.AsyncOpenAI(**kwargs)
    resp = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=_MAX_OUTPUT_TOKENS,
    )
    if not resp.choices:
        raise RuntimeError("OpenAI returned no choices")
    text = resp.choices[0].message.content or ""
    usage = resp.usage
    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0
    return text, input_tokens, output_tokens


async def _call_anthropic(prompt: str, model: str, api_key: str) -> _ProviderResult:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=api_key)
    resp = await client.messages.create(
        model=model,
        max_tokens=_MAX_OUTPUT_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    # `content` is a list of blocks. Newer models may return a mix of
    # TextBlock + ThinkingBlock + ToolUse — we want only the visible text.
    parts = [getattr(b, "text", "") for b in (resp.content or [])]
    text = "".join(parts)
    if not text.strip():
        # Diagnostic: enumerate block types so we can see what we got instead.
        block_types = [getattr(b, "type", type(b).__name__) for b in (resp.content or [])]
        _log.warning("anthropic returned no visible text; block types: %s", block_types)
    usage = resp.usage
    input_tokens = usage.input_tokens if usage else 0
    output_tokens = usage.output_tokens if usage else 0
    return text, input_tokens, output_tokens


async def _call_gemini(prompt: str, model: str, api_key: str) -> _ProviderResult:
    """Call Google Gemini's API via the genai SDK."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=_MAX_OUTPUT_TOKENS,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned no text")
    usage = getattr(response, "usage_metadata", None)
    input_tokens = getattr(usage, "prompt_token_count", 0) or 0
    output_tokens = getattr(usage, "candidates_token_count", 0) or 0
    return response.text, input_tokens, output_tokens


async def _call_provider(
    provider: str,
    model: str,
    api_key: str,
    prompt: str,
    provider_type: str | None = None,
    base_url: str | None = None,
) -> _ProviderResult:
    """Route to the appropriate provider SDK.

    For custom providers with provider_type="openai_compatible", uses the
    OpenAI SDK with a custom base_url.
    """
    # Custom providers with explicit type
    if provider_type == "openai_compatible":
        return await _call_openai(prompt, model, api_key, base_url=base_url)

    # Built-in providers
    if provider == "openai":
        return await _call_openai(prompt, model, api_key, base_url=base_url)
    if provider == "anthropic":
        return await _call_anthropic(prompt, model, api_key)
    if provider == "gemini":
        return await _call_gemini(prompt, model, api_key)

    # Fallback: unknown provider but no explicit type — try OpenAI-compatible
    # (allows custom providers without requiring --provider-type)
    if base_url:
        return await _call_openai(prompt, model, api_key, base_url=base_url)

    raise ValueError(f"Unknown provider: {provider} (use --provider-type and --base-url for custom providers)")


# ──────────────────────────────────────────────────────────────────────────
# Generation pipeline
# ──────────────────────────────────────────────────────────────────────────


async def _generate(args: argparse.Namespace) -> dict:
    data_dir = Path(args.data_dir)
    api_key = _resolve_api_key(args.provider, data_dir)
    if not api_key:
        return {"ok": False, "error": f"No API key configured for {args.provider} (set env var or save in UI)"}

    # Build the prompt — load templates first (idempotent).
    load_templates()
    prompt_result = build_generation_prompt(user_intent=args.prompt, language=args.language)

    # Retry loop — same shape as CGP, simpler classification.
    last_err = "no attempts made"
    total_latency_ms: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    for attempt in range(1, _MAX_RETRIES + 1):
        _log.info("generate-strategy: attempt %d/%d (provider=%s model=%s base_url=%s)",
                  attempt, _MAX_RETRIES, args.provider, args.model, args.base_url or "default")
        import time as _time
        _t0 = _time.perf_counter()
        try:
            response_text, input_tokens, output_tokens = await asyncio.wait_for(
                _call_provider(
                    args.provider,
                    args.model,
                    api_key,
                    prompt_result.text,
                    provider_type=args.provider_type,
                    base_url=args.base_url,
                ),
                timeout=_LLM_TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            last_err = f"LLM call timed out after {_LLM_TIMEOUT_S}s"
            continue
        except Exception as exc:  # noqa: BLE001 — surface any provider error
            last_err = f"{type(exc).__name__}: {exc}"
            continue
        total_latency_ms += (_time.perf_counter() - _t0) * 1000.0
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens

        if not response_text.strip():
            last_err = "LLM returned empty response"
            continue

        if args.language == "javascript":
            from src.foundation.code_generation_pipeline.extraction import extract_decide_code_js
            code, extract_err = extract_decide_code_js(response_text)
        elif args.language == "rust":
            from src.foundation.code_generation_pipeline.extraction import extract_decide_code_rust
            code, extract_err = extract_decide_code_rust(response_text)
        else:
            code, extract_err = extract_decide_code(response_text)
        if extract_err is not None or code is None:
            last_err = f"extract_failed: {extract_err}"
            # Log the head + tail of the raw response so subsequent failures
            # are debuggable from the API's stderr passthrough. Truncate
            # generously — full response can be many KB.
            head = response_text[:300].replace("\n", " ")
            tail = response_text[-200:].replace("\n", " ")
            _log.warning("extract_failed: response head=%r ... tail=%r (len=%d)",
                         head, tail, len(response_text))
            continue

        if args.language == "javascript":
            from src.foundation.sandbox.quickjs_sandbox import QuickJSSandbox
            sandbox = QuickJSSandbox()
        elif args.language == "rust":
            from src.foundation.sandbox.wasm_sandbox import WasmtimeSandbox
            sandbox = WasmtimeSandbox()
        else:
            sandbox = Sandbox()
        compile_result = sandbox.compile("standalone", code)
        if compile_result.status != ExecutionStatus.SUCCESS:
            last_err = f"compile_error: {compile_result.error_type or 'unknown'}"
            continue

        # Smoke-execute with mock data. Catches runtime issues (e.g., bare
        # `import math`) that compile cleanly under RestrictedPython but blow
        # up on first call — without this check, every tick at match time
        # would silently substitute Hold() and the strategy looks frozen.
        smoke_result = sandbox.execute("standalone", *_smoke_inputs())
        if smoke_result.status != ExecutionStatus.SUCCESS:
            last_err = (
                f"runtime_error: {smoke_result.error_type or 'unknown'} on smoke-test "
                f"(common cause: forbidden import or use of restricted builtin)"
            )
            continue

        # Success — return the code; the API caller decides where to save it.
        return {
            "ok": True,
            "code": code,
            "template_version": prompt_result.template_version,
            "language": args.language,
            "latency_ms": round(total_latency_ms, 1),
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "strategy_size_bytes": len(code.encode("utf-8")),
        }

    return {"ok": False, "error": f"Generation failed after {_MAX_RETRIES} attempts. Last: {last_err}"}


# ──────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────


def main() -> None:
    """Console entry point. Reads sys.argv[2:] (the dispatcher already stripped 'generate-strategy')."""
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    parser = _build_parser()
    args = parser.parse_args(sys.argv[2:])
    try:
        result = asyncio.run(_generate(args))
    except Exception as exc:  # noqa: BLE001 — defensive: ensure JSON always emitted
        result = {"ok": False, "error": f"unexpected: {type(exc).__name__}: {exc}"}
    print(json.dumps(result))
    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
