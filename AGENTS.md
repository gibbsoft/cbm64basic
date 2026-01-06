# AGENTS.md

Instructions for AI coding agents working on this project.

## Build, Test, and Development Commands

### Environment Setup
```bash
# Using uv (recommended)
cd ~/git/gsl/cbm64basic
uv venv .venv
source .venv/bin/activate
uv pip install -e .

# Using pip
cd ~/git/gsl/cbm64basic
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Running the Application
```bash
# Start interactive BASIC editor
python3 -m src.cbm64_editor

# Run interpreter test suite (built-in tests)
python3 -m src.cbm_basic
```

### Testing
```bash
# Run all pytest tests (96 tests)
pytest tests/test_basic.py -v

# Run a specific test
pytest tests/test_basic.py::TestBasicFeatures::test_for_next_loop -v

# Run tests and show output
pytest tests/test_basic.py -s

# Run all .bas test programs
pytest tests/test_basic.py::TestBasicPrograms -v
```

### No requirements.txt
This project uses modern Python packaging with `pyproject.toml`. Do not create or use `requirements.txt`. All dependencies are declared in pyproject.toml.

## Code Style Guidelines

### Core Principles

1. **PEP 8 Compliant** - Follow Python's official style guide
2. **Small Files** - Keep each module under 500 lines for easier AI editing and maintenance
3. **Single Responsibility** - Each module should have one clear purpose
4. **Modern Python** - Use Python 3.10+ features (match/case, type hints, etc.)

### Python Version
- **Minimum**: Python 3.10 (for match/case support)
- **Target**: Python 3.12

### File Size Guidelines
- **Target**: Under 500 lines per module
- **Maximum**: 600 lines (refactor if approaching this limit)
- **Rationale**: Smaller files are easier for AI agents to read, understand, and modify

### Type Hints
Use modern type hint syntax:
```python
# Good - modern syntax (Python 3.10+)
def process(items: list[str]) -> dict[str, int]:
    ...

def get_value(key: str) -> int | None:
    ...

# Avoid - old typing module syntax
from typing import List, Dict, Optional
def process(items: List[str]) -> Dict[str, int]:
    ...
```

### Naming Conventions
- Classes: `PascalCase` (`BasicInterpreter`, `VirtualScreen`)
- Functions/Methods: `snake_case` (`tokenize`, `handle_print`)
- Variables: `snake_case` (`line_num`, `current_token`)
- Constants: `UPPER_CASE` (`SCREEN_BASE`, `FKEY_SEQUENCES`)
- Private attributes: `_underscore_prefix` (`_execute_statement`)

### Imports
Order: standard library → third-party → local modules
```python
import math
import re
import sys
from typing import Any, TYPE_CHECKING

import colorama
from prompt_toolkit import PromptSession

from src.constants import SCREEN_BASE, SCREEN_COLS
from src.screen import VirtualScreen
```

### Dispatch Patterns

**Prefer dict dispatch over long if/elif chains:**
```python
# Good - dict dispatch
FUNCTION_HANDLERS = {
    "ABS": eval_abs,
    "SQR": eval_sqr,
    "INT": eval_int,
}

def evaluate(func_name: str, tokens: list[str]) -> Any:
    handler = FUNCTION_HANDLERS.get(func_name)
    if handler:
        return handler(tokens)
    return None
```

**Use match/case for command dispatch:**
```python
# Good - match/case (Python 3.10+)
match command:
    case "PRINT" | "?":
        handle_print(tokens)
    case "GOTO":
        return handle_goto(tokens)
    case "END" | "STOP":
        return "END_PROGRAM"
    case _:
        raise SyntaxError(f"Unknown: {command}")
```

### Formatting
- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 100 characters (prefer 88 for Black compatibility)
- **Blank lines**: One between functions, two between classes
- **Docstrings**: Required for classes and public functions

### Project Structure
```
src/
├── constants.py       16 lines  - Memory addresses, screen dimensions
├── colors.py          99 lines  - ANSI terminal color support
├── charset.py        455 lines  - PETSCII/screen code Unicode mappings
├── screen.py         169 lines  - VirtualScreen class
├── functions.py      326 lines  - BASIC functions (dict dispatch)
├── commands.py       434 lines  - Statement handlers
├── interpreter.py    456 lines  - Core interpreter (match/case dispatch)
├── cbm_basic.py      134 lines  - Re-export module for compatibility
├── prg_file.py       358 lines  - PRG file format load/save
└── cbm64_editor.py   823 lines  - Interactive editor (consider splitting)
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `constants.py` | Memory addresses, screen dimensions, default colors |
| `colors.py` | ANSI color codes, 256-color support, terminal detection |
| `charset.py` | PETSCII ↔ Unicode, screen codes ↔ Unicode mappings |
| `screen.py` | `VirtualScreen` class for PEEK/POKE screen memory |
| `functions.py` | BASIC function evaluators (ABS, CHR$, LEFT$, etc.) |
| `commands.py` | Statement handlers (PRINT, GOTO, FOR, INPUT, etc.) |
| `interpreter.py` | `BasicInterpreter` class, tokenizer, expression eval |
| `cbm_basic.py` | Re-exports all public APIs for backward compatibility |
| `prg_file.py` | Load/save tokenized PRG files |
| `cbm64_editor.py` | Interactive editor with syntax highlighting |

### Adding New Features

1. **Identify the right module** based on responsibilities above
2. **Check file size** - if module is near 500 lines, consider splitting first
3. **Add to dispatch table** if it's a new function or command
4. **Write tests** in `tests/test_basic.py`
5. **Update re-exports** in `cbm_basic.py` if adding public API

### Example: Adding a New BASIC Function

```python
# In src/functions.py

def eval_new_func(interpreter: "BasicInterpreter", tokens: list[str]) -> Any:
    """Handle NEW_FUNC - description of what it does."""
    val = interpreter.evaluate_expression(tokens[2:-1])
    return some_operation(val)

# Add to dispatch table
FUNCTION_HANDLERS = {
    # ... existing entries ...
    "NEW_FUNC": eval_new_func,
}
```

### Commodore 64 BASIC Specifics
- Keywords are UPPERCASE in output
- Line numbers are integers (10, 20, 30)
- Strings are double-quoted: `"HELLO WORLD"`
- Variables: `A` (numeric), `A$` (string), `A%` (integer)
- Error format: `?ERROR_TYPE ERROR` (authentic C64 style)
- Prompt: `READY.` after commands

### Dependencies
Only add dependencies if absolutely necessary. Current deps:
- `prompt-toolkit>=3.0.0` - Terminal input handling
- `colorama>=0.4.6` - Cross-platform ANSI colors

### Testing Requirements
- All changes must pass existing tests: `pytest tests/test_basic.py -v`
- New features should include tests
- Test count should not decrease (currently 96 tests)
