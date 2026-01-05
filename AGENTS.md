# AGENTS.md

## Build, Test, and Development Commands

### Environment Setup
```bash
# Using uv (recommended)
cd ~/git/cbm64basic
uv venv .venv
source .venv/bin/activate
uv pip install prompt-toolkit colorama

# Using pip
cd ~/git/cbm64basic
python3 -m venv .venv
source .venv/bin/activate
pip install prompt-toolkit colorama
```

### Running the Application
```bash
# Start interactive BASIC editor
python3 cbm64_editor.py

# Run demo script
./demo.sh

# Run interpreter test suite (built-in tests)
python3 cbm_basic.py
```

### Testing
```bash
# Run all pytest tests
pytest test_basic.py -v

# Run a specific test
pytest test_basic.py::TestBasicFeatures::test_for_next_loop -v

# Run tests and show output
pytest test_basic.py -s

# Run all .bas test programs
pytest test_basic.py::TestBasicPrograms -v
```

### Testing
```bash
# Test a single BASIC program by loading in editor
python3 cbm64_editor.py
> LOAD test_loop.bas
> RUN

# Test specific interpreter functionality
python3 cbm_basic_2.0_final.py  # Runs all built-in test programs

# Unit tests (if added)
python3 -m unittest test_module_name
python3 -m unittest test_module_name.TestClass.test_method
```

### No requirements.txt
This project uses modern Python packaging with `pyproject.toml`. Do not create or use `requirements.txt`. All dependencies are declared in pyproject.toml.

## Code Style Guidelines

### Python Style
- **Python Version**: 3.8+
- **Type Hints**: Use `typing` module (List, Dict, Any, Optional)
- **Naming Conventions**:
  - Classes: PascalCase (`BasicInterpreter`, `CBM64Editor`)
  - Functions/Methods: snake_case (`tokenize`, `handle_print`)
  - Variables: snake_case (`line_num`, `program_lines`)
  - Constants: UPPER_CASE (`COLORS`, `BASIC_KEYWORDS`)
  - Private attributes: underscore prefix (`_internal_var`)

### Imports
Order imports: standard library → third-party → local modules
```python
import sys
import re
from typing import List, Dict

from prompt_toolkit import PromptSession
import colorama

from cbm_basic_2_0_final import BasicInterpreter
```

### Formatting
- Use 4 spaces for indentation (no tabs)
- Line length: maximum 120 characters
- Use type hints for function signatures
- Include docstrings for classes and public methods
- One blank line between functions, two between classes

### Error Handling
```python
try:
    # Code that might fail
    result = some_operation()
except FileNotFoundError:
    print("?FILE NOT FOUND")
except ValueError as e:
    print(f"?VALUE ERROR: {e}")
except Exception as e:
    print(f"?{type(e).__name__.upper()} ERROR")
```

### Project Structure
```
cbm64basic/
├── cbm64_editor.py          # Main editor with syntax highlighting (517 lines)
├── cbm_basic.py            # BASIC V2 interpreter (680+ lines)
├── test_basic.py           # Pytest test suite (38 tests)
├── pyproject.toml           # Dependencies and build config
├── demo.sh                  # Demo script
├── README.md                # Documentation
└── *.bas                    # Test BASIC programs
```

### Testing Pattern
- Test files are BASIC programs (.bas extension)
- Test by loading in editor: `LOAD test_name.bas` then `RUN`
- Interpreter has built-in test suite in `main()` function
- Manual testing through interactive editor is primary method

### Commodore 64 BASIC Specifics
- Keywords must be UPPERCASE in output
- Line numbers are integers (10, 20, 30)
- Strings are double-quoted: `"HELLO WORLD"`
- Variables: A (numeric), A$ (string), A% (integer)
- Error format: `?ERROR_TYPE ERROR` (authentic C64 style)
- Prompt: `READY.` after commands

### Dependencies
Only add dependencies if absolutely necessary. Current deps:
- `prompt-toolkit>=3.0.0` - Terminal input handling
- `colorama>=0.4.6` - Cross-platform ANSI colors

### Adding New Features
1. Implement in `cbm_basic.py` first (interpreter logic)
2. Add syntax highlighting to `cbm64_editor.py` (COLORS dict)
3. Create test `.bas` file for the new feature
4. Test manually through the interactive editor
