"""CGP fenced-block extractor — GDD Rule 7 (Code extraction and normalization)."""

from __future__ import annotations
import re

# Match a fenced code block. Optional language tag (python, py, python3, etc.)
# on the opening fence. DOTALL: . matches newlines so the body can span lines.
_FENCED_BLOCK_RE = re.compile(
    r"```(?:[a-zA-Z0-9_+-]*)\n(.*?)```",
    re.DOTALL,
)

# Fallback: locate `def decide(` and grab everything from that line to the
# end of the response. Used when the LLM ignored the "wrap in fences"
# instruction (some Claude / GPT-5 responses do this with reasoning prefaces).
_BARE_DECIDE_RE = re.compile(
    r"^def decide\(.*",  # match start of a line; body extracted via slicing below
    re.MULTILINE,
)

_BARE_JS_DECIDE_RE = re.compile(
    r"^function decide\(",
    re.MULTILINE,
)

# Rust full-source extraction. The strategy is the entire lib.rs (boilerplate
# + decide_logic), so the verification anchor is `fn decide_logic(` (the only
# part the LLM is supposed to author) plus the `decide` no_mangle export.
_BARE_RUST_USE_RE = re.compile(
    r"^use serde::",
    re.MULTILINE,
)


def extract_decide_code(response_text: str) -> tuple[str | None, str | None]:
    """GDD Rule 7 — extract LAST fenced block; verify `def decide(` substring.

    Falls back to plain-text extraction if no fence is found but a bare
    ``def decide(`` line exists at column 0 — handles LLMs that ignore
    the "wrap in fences" instruction.

    Returns:
        (code_str, None)        on success
        (None, failure_reason)  reason in {"no_code_block", "no_decide_signature"}
    """
    matches = _FENCED_BLOCK_RE.findall(response_text)

    if matches:
        raw = matches[-1]  # Step 2: LAST match (per Rule 7 + EC-CGP-01)
    else:
        # Fallback path: look for a bare `def decide(` at column 0. Take
        # everything from there to the end of the response. Trailing prose
        # AFTER the function body would still be invalid Python and fail at
        # sandbox-compile, which produces a clearer error.
        m = _BARE_DECIDE_RE.search(response_text)
        if m is None:
            return (None, "no_code_block")
        raw = response_text[m.start():]

    # Step 3: strip surrounding blank lines (NOT per-line indentation)
    code = raw.rstrip()
    while code.startswith("\n"):
        code = code[1:]

    # Step 5: substring check for `def decide(` (with open paren — not just `def decide`)
    if "def decide(" not in code:
        return (None, "no_decide_signature")

    return (code, None)


def extract_decide_code_js(response_text: str) -> tuple[str | None, str | None]:
    """Extract JavaScript decide() function from LLM response.

    Same strategy as extract_decide_code: last fenced block, then bare
    function fallback. Verifies `function decide(` substring.

    Returns:
        (code_str, None)        on success
        (None, failure_reason)  reason in {"no_code_block", "no_decide_signature"}
    """
    matches = _FENCED_BLOCK_RE.findall(response_text)

    if matches:
        raw = matches[-1]
    else:
        m = _BARE_JS_DECIDE_RE.search(response_text)
        if m is None:
            return (None, "no_code_block")
        raw = response_text[m.start():]

    code = raw.rstrip()
    while code.startswith("\n"):
        code = code[1:]

    if "function decide(" not in code:
        return (None, "no_decide_signature")

    return (code, None)


def extract_decide_code_rust(response_text: str) -> tuple[str | None, str | None]:
    """Extract Rust lib.rs source from LLM response.

    The Rust strategy is the whole crate body (boilerplate + decide_logic).
    Verification: the source must contain both `fn decide_logic(` (the LLM-
    authored slot) and the `pub extern \"C\" fn decide(` ABI export so the
    runtime can call it.

    Returns:
        (code_str, None)        on success
        (None, failure_reason)  reason in {"no_code_block", "no_decide_signature"}
    """
    matches = _FENCED_BLOCK_RE.findall(response_text)

    if matches:
        raw = matches[-1]
    else:
        m = _BARE_RUST_USE_RE.search(response_text)
        if m is None:
            return (None, "no_code_block")
        raw = response_text[m.start():]

    code = raw.rstrip()
    while code.startswith("\n"):
        code = code[1:]

    if "fn decide_logic(" not in code or "pub extern \"C\" fn decide(" not in code:
        return (None, "no_decide_signature")

    return (code, None)