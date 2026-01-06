#!/usr/bin/env python3
"""
Commodore 64 BASIC V2 Interpreter
=================================
A Python implementation of Microsoft BASIC 2.0 with Commodore 64 dialect.
Supports: PRINT, LET, GOTO, IF/THEN, FOR/NEXT, GOSUB/RETURN, DATA/READ,
enhanced arithmetic expressions, and proper C64 BASIC V2 syntax.

This module provides backward compatibility by re-exporting from the
refactored submodules.
"""

import colorama

colorama.init(strip=False)

# Re-export constants
from src.constants import (
    SCREEN_BASE,
    SCREEN_COLS,
    SCREEN_ROWS,
    SCREEN_SIZE,
    COLOR_BASE,
    C64_DEFAULT_FG,
    C64_DEFAULT_BG,
)

# Re-export color handling
from src.colors import (
    USE_COLORS,
    USE_256_COLORS,
    C64_COLORS_256,
    C64_COLORS_ANSI,
    get_ansi_color,
    reset_ansi_color,
    _detect_256_color,
)

# Re-export character set mappings
from src.charset import (
    PETSCII_TO_UNICODE,
    SCREEN_CODE_TO_UNICODE,
    petscii_to_unicode,
    screen_code_to_unicode,
)

# Re-export screen class
from src.screen import VirtualScreen

# Re-export interpreter class
from src.interpreter import BasicInterpreter


def main():
    """Main function with comprehensive test suite"""
    print("=" * 50)
    print("COMMODORE 64 BASIC V2 INTERPRETER")
    print("Enhanced with GOSUB/RETURN, DATA/READ, and expressions")
    print("=" * 50)

    test_programs = {
        "basic_test": """
10 PRINT "HELLO WORLD"
20 LET X = 42
30 PRINT X
40 END
""",
        "for_next_test": """
10 FOR I = 1 TO 3
20   PRINT I
30 NEXT I
40 END
""",
        "if_goto_test": """
10 LET X = 5
20 IF X = 5 THEN GOTO 50
30 PRINT "NOT 5"
40 END
50 PRINT "X IS 5"
60 END
""",
        "gosub_return_test": """
10 PRINT "START"
20 GOSUB 100
30 PRINT "BACK FROM SUB"
40 END
100 PRINT "IN SUBROUTINE"
110 RETURN
""",
        "data_read_test": """
10 DATA 1, 2.5, "HELLO", 42
20 READ A, B, C$, D
30 PRINT A, B, C$, D
40 END
""",
        "expression_test": """
10 LET A = 10
20 LET B = 20
30 PRINT "A + B =", A + B
40 PRINT "A * 2 =", A * 2
50 END
""",
        "math_functions_test": """
10 PRINT ABS(-5)
20 PRINT SQR(16)
30 PRINT INT(3.7)
40 PRINT SGN(-10)
50 END
""",
        "string_functions_test": """
10 A$ = "HELLO"
20 B$ = "WORLD"
30 PRINT LEFT$(A$, 3)
40 PRINT RIGHT$(B$, 3)
50 PRINT LEN(A$)
60 END
""",
    }

    for test_name, program in test_programs.items():
        print(f"\n--- TEST: {test_name.replace('_', ' ').title()} ---")
        try:
            interpreter = BasicInterpreter()
            interpreter.run_program(program)
            print(f"\n{test_name} completed successfully")
        except Exception as e:
            print(f"\n{test_name} failed: {e}")

    print("\n" + "=" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    main()
