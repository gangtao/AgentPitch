"""Tests for Rust lib.rs extraction from LLM responses (ADR-0026)."""
from __future__ import annotations

from src.foundation.code_generation_pipeline.extraction import extract_decide_code_rust


_VALID_BODY = """use serde::{Deserialize, Serialize};

fn decide_logic(gs: &GameState, ps: &PlayerState, _hist: &[TickRecord]) -> Action {
    Action::Hold
}

#[no_mangle]
pub extern "C" fn decide(ptr: *const u8, len: usize) -> i32 { 0 }
"""


def test_extract_rust_from_fenced_block():
    response = f"""Here's the strategy:
```rust
{_VALID_BODY}
```
"""
    code, err = extract_decide_code_rust(response)
    assert err is None
    assert "fn decide_logic(" in code
    assert 'pub extern "C" fn decide(' in code


def test_extract_rust_from_bare_use_serde():
    response = _VALID_BODY
    code, err = extract_decide_code_rust(response)
    assert err is None
    assert "fn decide_logic(" in code


def test_extract_rust_last_fenced_block():
    response = f"""```rust
// wrong block — has no decide
fn helper() {{}}
```

```rust
{_VALID_BODY}
```
"""
    code, err = extract_decide_code_rust(response)
    assert err is None
    assert "fn decide_logic(" in code


def test_extract_rust_no_code_block():
    response = "Here is some text with no code."
    code, err = extract_decide_code_rust(response)
    assert code is None
    assert err == "no_code_block"


def test_extract_rust_no_decide_logic_signature():
    response = """```rust
use serde::{Deserialize, Serialize};
pub extern "C" fn decide(ptr: *const u8, len: usize) -> i32 { 0 }
```"""
    code, err = extract_decide_code_rust(response)
    assert code is None
    assert err == "no_decide_signature"


def test_extract_rust_no_decide_export_signature():
    response = """```rust
use serde::{Deserialize, Serialize};
fn decide_logic() -> Action { Action::Hold }
```"""
    code, err = extract_decide_code_rust(response)
    assert code is None
    assert err == "no_decide_signature"


def test_extract_rust_strips_whitespace():
    response = f"""```rust

{_VALID_BODY}

```"""
    code, err = extract_decide_code_rust(response)
    assert err is None
    assert not code.startswith("\n")
