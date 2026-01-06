# CBM64 BASIC

A Commodore 64 BASIC V2 interpreter and editor with syntax highlighting.

## Project Structure

```
cbm64basic/
├── src/
│   ├── __init__.py
│   ├── cbm_basic.py          # Re-export module (backward compatibility)
│   ├── cbm64_editor.py       # Main editor with syntax highlighting
│   ├── interpreter.py        # Core BASIC interpreter
│   ├── commands.py           # Statement handlers (PRINT, GOTO, FOR, etc.)
│   ├── functions.py          # BASIC functions (ABS, CHR$, LEFT$, etc.)
│   ├── screen.py             # Virtual screen memory emulation
│   ├── charset.py            # PETSCII and screen code mappings
│   ├── colors.py             # ANSI terminal color support
│   ├── constants.py          # Memory addresses and dimensions
│   └── prg_file.py           # PRG file format support
├── tests/
│   ├── __init__.py
│   ├── test_basic.py         # Pytest test suite (96 tests)
│   └── test*.bas             # Test BASIC programs
├── examples/
│   ├── demo_program.bas      # Syntax highlighting demo
│   ├── session.bas           # Complete editing session example
│   └── *.bas                 # Example programs
├── pyproject.toml            # Python project configuration
├── CONTRIBUTING.md           # Contribution guidelines
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

#### Immediate Mode Commands
- `LIST` - List program with syntax highlighting
- `RUN` - Execute program
- `NEW` - Clear current program
- `CLR` - Clear all variables
- `LOAD` - Load program from file (prompts for filename)
- `SAVE` - Save program to file (prompts for filename)
- `EDIT n` - Edit line number n (see below)
- `HELP` - Show help
- `BYE` - Exit BASIC

#### Program Mode
- `<number> <code>` - Add/change line (e.g., `10 PRINT "HELLO"`)
- `<number>` - Delete line (e.g., `20`)

### EDIT Command
Use `EDIT n` to edit an existing line. The line is displayed for editing with the current content pre-filled.

```
READY.
10 FOR I = 1 TO 10
20 PRINT I
30 NEXT I
EDIT 20
 20 PRINT I     <- cursor here, edit then press RETURN
```

On pressing RETURN, the edited line is validated. If valid, it's accepted; if invalid, an error is shown and the line is not updated.

### Multi-Line Paste Support
You can paste multi-line BASIC code directly into the editor. Each line is processed individually:

```
READY.
5 ? CHR$(147)
10 FOR Y = 0 TO 10
20 FOR X = 0 TO 10
30 ? "." ; CHR$(29) ;
40 NEXT X
50 ? CHR$(19)
60 NEXT Y
70 END
LIST
  5 ? CHR$ ( 147 )
 10 FOR Y = 0 TO 10
 20 FOR X = 0 TO 10
 30 ? "." ; CHR$ ( 29 ) ;
 40 NEXT X
 50 ? CHR$ ( 19 )
 60 NEXT Y
 70 END
```

### Auto-Formatting
All lines are automatically formatted on entry:
- Keywords converted to UPPERCASE
- Proper spacing around operators
- Whitespace normalized

### LOAD and SAVE
The `LOAD` and `SAVE` commands do not accept filename parameters. They prompt for input:

```
READY.
LOAD
FILENAME? program.bas
SEARCHING FOR *
LOADING

SAVE
FILENAME? program.bas
WRITING *
OK
```

### Program Execution Order
Lines are executed in numerical order by line number, regardless of the order they were entered. This matches authentic C64 BASIC behavior:

```
READY.
120 PRINT "This runs second"
100 PRINT "This runs first"
110 PRINT "This runs third"
RUN
This runs first
This runs second
This runs third
```

### Case Sensitivity
- Commands are case-insensitive: `PRINT`, `print`, and `Print` all work
- Variables are case-insensitive: `X`, `x`, and `X` all refer to the same variable
- Variable names are stored in uppercase internally

### Undefined Variables
Undefined variables default to 0 in expressions, matching C64 BASIC behavior:

```
READY.
10 x = x + 1
20 PRINT x
30 END
RUN
1
```

### Syntax Validation
Lines are validated when entered. Invalid syntax is rejected with an error message positioned at the problem:

```
READY.
10 FOR X IN 1 TO 10
        █  ?USE = NOT IN
```

Only syntactically valid lines are stored in the program.

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

### GOTO Loop Example
```
READY.
10 PRINT "Hello " ; x
20 x = x + 1
30 IF x < 5 THEN GOTO 10
40 END
RUN
Hello 0
Hello 1
Hello 2
Hello 3
Hello 4
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
