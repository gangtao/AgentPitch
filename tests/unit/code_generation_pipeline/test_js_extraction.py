"""Tests for JavaScript decide() extraction from LLM responses."""
from __future__ import annotations

from src.foundation.code_generation_pipeline.extraction import extract_decide_code_js


def test_extract_js_from_fenced_block():
    response = """Here's a strategy:
```javascript
function decide(game_state, player_state, history) {
    return {type: "Hold"};
}
```
"""
    code, err = extract_decide_code_js(response)
    assert err is None
    assert "function decide(" in code


def test_extract_js_from_bare_function():
    response = """function decide(game_state, player_state, history) {
    return {type: "Move", dx: 1.0, dy: 0.0, speed: 1.0};
}"""
    code, err = extract_decide_code_js(response)
    assert err is None
    assert "function decide(" in code


def test_extract_js_last_fenced_block():
    response = """```javascript
// wrong block
```

```javascript
function decide(game_state, player_state, history) {
    return {type: "Hold"};
}
```
"""
    code, err = extract_decide_code_js(response)
    assert err is None
    assert "function decide(" in code


def test_extract_js_no_code_block():
    response = "Here is some text with no code."
    code, err = extract_decide_code_js(response)
    assert code is None
    assert err == "no_code_block"


def test_extract_js_no_decide_signature():
    response = """```javascript
function helper() { return 42; }
```"""
    code, err = extract_decide_code_js(response)
    assert code is None
    assert err == "no_decide_signature"


def test_extract_js_strips_whitespace():
    response = """```js

function decide(gs, ps, h) {
    return {type: "Hold"};
}

```"""
    code, err = extract_decide_code_js(response)
    assert err is None
    assert not code.startswith("\n")
    assert not code.endswith("\n")