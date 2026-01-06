# Contributing to CBM64 BASIC

Thank you for your interest in contributing! This document outlines our coding standards and development practices.

## Code Style

### Core Principles

1. **PEP 8 Compliant** - Follow [Python's official style guide](https://peps.python.org/pep-0008/)
2. **Small Files** - Keep each module under 500 lines
3. **Single Responsibility** - Each module should have one clear purpose
4. **Modern Python** - Use Python 3.10+ features

### Why Small Files?

We target **under 500 lines per module** because:
- Easier to understand at a glance
- Faster for AI coding assistants to process
- Simpler to test and maintain
- Encourages better separation of concerns

If a file approaches 500 lines, consider splitting it.

### Python Version

- **Minimum**: Python 3.10 (required for `match`/`case`)
- **Target**: Python 3.12

### Type Hints

Use modern syntax (Python 3.10+):

```python
# Preferred
def process(items: list[str]) -> dict[str, int]:
    ...

def get_value(key: str) -> int | None:
    ...

# Avoid
from typing import List, Dict, Optional
def process(items: List[str]) -> Dict[str, int]:
    ...
```

### Dispatch Patterns

**Use dict dispatch for function/handler lookups:**

```python
HANDLERS = {
    "ABS": eval_abs,
    "SQR": eval_sqr,
    "INT": eval_int,
}

def evaluate(name: str, args):
    handler = HANDLERS.get(name)
    return handler(args) if handler else None
```

**Use `match`/`case` for command dispatch:**

```python
match command:
    case "PRINT" | "?":
        handle_print(tokens)
    case "GOTO":
        return handle_goto(tokens)
    case _:
        raise SyntaxError(f"Unknown: {command}")
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `BasicInterpreter` |
| Functions | snake_case | `handle_print` |
| Variables | snake_case | `line_num` |
| Constants | UPPER_CASE | `SCREEN_BASE` |
| Private | _prefix | `_execute_statement` |

### Formatting

- **Indentation**: 4 spaces (no tabs)
- **Line length**: 100 characters max (88 preferred for Black compatibility)
- **Blank lines**: One between functions, two between classes
- **Docstrings**: Required for classes and public functions

### Import Order

1. Standard library
2. Third-party packages
3. Local modules

```python
import math
import sys

import colorama
from prompt_toolkit import PromptSession

from src.constants import SCREEN_BASE
from src.screen import VirtualScreen
```

## Project Structure

```
src/
├── constants.py      - Memory addresses, dimensions
├── colors.py         - ANSI terminal colors
├── charset.py        - PETSCII/screen code mappings
├── screen.py         - VirtualScreen class
├── functions.py      - BASIC functions (dict dispatch)
├── commands.py       - Statement handlers
├── interpreter.py    - Core interpreter (match/case)
├── cbm_basic.py      - Re-export module
├── prg_file.py       - PRG file format
└── cbm64_editor.py   - Interactive editor
```

## Development Workflow

### Setup

```bash
# Clone and setup
git clone <repo>
cd cbm64basic
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Running Tests

```bash
# All tests (96 tests)
pytest tests/test_basic.py -v

# Specific test
pytest tests/test_basic.py::TestBasicFeatures::test_for_next_loop -v
```

### Adding a New BASIC Function

1. Add handler in `src/functions.py`:
   ```python
   def eval_myfunc(interpreter, tokens: list[str]) -> Any:
       """Handle MYFUNC - description."""
       val = interpreter.evaluate_expression(tokens[2:-1])
       return result
   ```

2. Add to dispatch table:
   ```python
   FUNCTION_HANDLERS = {
       # ... existing ...
       "MYFUNC": eval_myfunc,
   }
   ```

3. Add tests in `tests/test_basic.py`

4. Run tests: `pytest tests/test_basic.py -v`

### Adding a New Statement

1. Add handler in `src/commands.py`:
   ```python
   def handle_mycommand(interpreter, tokens: list[str]) -> None:
       """Handle MYCOMMAND statement."""
       # implementation
   ```

2. Add case in `src/interpreter.py` `_execute_statement()`:
   ```python
   case "MYCOMMAND":
       handle_mycommand(self, tokens[1:])
   ```

3. Add tests and run test suite

## Pull Request Guidelines

1. **All tests must pass** - Run `pytest tests/test_basic.py -v`
2. **No decrease in test count** - Currently 96 tests
3. **Follow code style** - PEP 8, small files, modern Python
4. **Update docs** if adding new features
5. **One feature per PR** - Keep changes focused

## C64 BASIC Specifics

When implementing BASIC features, follow authentic C64 behavior:
- Keywords output as UPPERCASE
- Error format: `?ERROR_TYPE ERROR`
- Prompt: `READY.`
- Variables: `A` (numeric), `A$` (string), `A%` (integer)
- Line numbers: integers (10, 20, 30...)

## Questions?

Open an issue for questions about contributing or code style.
