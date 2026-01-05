# CBM64 BASIC

A Commodore 64 BASIC V2 interpreter and editor with syntax highlighting.

## Project Structure

```
cbm64basic/
├── src/
│   ├── __init__.py
│   ├── cbm_basic.py          # BASIC V2 interpreter
│   └── cbm64_editor.py       # Main editor with syntax highlighting
├── tests/
│   ├── __init__.py
│   ├── test_basic.py         # Pytest test suite
│   └── test*.bas             # Test BASIC programs
├── examples/
│   ├── demo_program.bas      # Syntax highlighting demo
│   ├── session.bas           # Complete editing session example
│   └── *.bas                 # Example programs
├── docs/
├── pyproject.toml            # Python project configuration
└── demo.sh                   # Demo script
```

## Features

### Syntax Highlighting
- **Keywords** (blue): PRINT, LET, GOTO, GOSUB, RETURN, IF/THEN/ELSE, FOR/NEXT, etc.
- **Line Numbers** (orange): 10, 20, 30...
- **Strings** (green): "Hello World"
- **Variables** (cyan): A$, B%, C, D
- **Numbers** (yellow): 42, 3.14
- **Comments** (gray): REM This is a comment
- **Operators** (white): +, -, *, /, =, <, >, etc.

### Editor Commands

#### Immediate Mode
- `LIST` - List program with syntax highlighting
- `RUN` - Execute program
- `NEW` - Clear program
- `LOAD` - Load from file
- `SAVE` - Save to file
- `CLR` - Clear variables
- `HELP` - Show help
- `BYE` - Exit

#### Program Mode
- `<number> <code>` - Add/change line (e.g., `10 PRINT "HELLO"`)
- `<number>` - Delete line (e.g., `20`)

### Auto-Formatting
All lines are automatically formatted on entry:
- Keywords converted to UPPERCASE
- Proper spacing around operators
- Whitespace normalized

## Setup

### Using uv (recommended):
```bash
cd cbm64basic
uv venv .venv
source .venv/bin/activate
uv pip install .
python3 -m src.cbm64_editor
```

### Without uv:
```bash
cd cbm64basic
python3 -m venv .venv
source .venv/bin/activate
pip install prompt-toolkit colorama
python3 -m src.cbm64_editor
```

## Example Session

```
**** COMMODORE BASIC V2 ****
 64K RAM SYSTEM  38911 BASIC BYTES FREE
============================================================

READY.
 10 FOR I=1 TO 3
 20 PRINT I
 30 NEXT I
LIST
 10 FOR I = 1 TO 3
 20 PRINT I
 30 NEXT I

READY.
RUN
1
2
3
READY.

BYE
GOODBYE!
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run a specific test
pytest tests/test_basic.py::TestBasicFeatures::test_for_next_loop -v
```

## Dependencies

- **prompt-toolkit** - Advanced terminal input handling
- **colorama** - Cross-platform ANSI color support

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.
