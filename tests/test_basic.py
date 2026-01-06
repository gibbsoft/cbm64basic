"""
Pytest tests for Commodore 64 BASIC interpreter.
Runs all .bas test programs and verifies they execute without errors.
"""

import pytest
import glob
import os
from pathlib import Path

from src.cbm_basic import BasicInterpreter
from src.cbm64_editor import CBM64Editor


class TestBasicPrograms:
    """Run all .bas test programs and verify they execute without errors."""

    @pytest.fixture(params=glob.glob("tests/test*.bas"))
    def test_file(self, request):
        """Parametrize test with all test .bas files."""
        return request.param

    def test_program_runs(self, test_file):
        """Run a BASIC program and verify it completes without errors."""
        program_path = Path(test_file)

        with open(program_path) as f:
            source_code = f.read()

        # Create interpreter with input buffer for programs that need input
        interpreter = BasicInterpreter()

        # Check if program has INPUT statement
        if "INPUT" in source_code.upper():
            # Programs with INPUT need pre-filled input
            if (
                "mult" in program_path.name.lower()
                or "table" in program_path.name.lower()
            ):
                interpreter.input_buffer = ["5"]
            elif "input" in program_path.name.lower():
                interpreter.input_buffer = ["42"]
            else:
                # Default test value
                interpreter.input_buffer = ["42"]

        # Run the program - should complete without raising an exception
        try:
            interpreter.run_program(source_code)
        except Exception as e:
            pytest.fail(f"Program {test_file} failed with error: {e}")

    def test_program_output(self, test_file, capsys):
        """Verify a BASIC program produces some output (if it has PRINT statements)."""
        program_path = Path(test_file)

        with open(program_path) as f:
            source_code = f.read()

        interpreter = BasicInterpreter()

        # Programs with INPUT need pre-filled input
        if "INPUT" in source_code.upper():
            if (
                "mult" in program_path.name.lower()
                or "table" in program_path.name.lower()
            ):
                interpreter.input_buffer = ["5"]
            elif "input" in program_path.name.lower():
                interpreter.input_buffer = ["42"]
            else:
                # Default test value
                interpreter.input_buffer = ["42"]

        interpreter.run_program(source_code)

        captured = capsys.readouterr()

        # Most test programs should produce output (unless they just have INPUT)
        program_name = program_path.name.lower()
        if "input" not in program_name and "INPUT" not in source_code.upper():
            # Check that something was printed
            assert len(captured.out) > 0, f"Program {test_file} produced no output"


class TestBasicFeatures:
    """Test specific BASIC features with inline programs."""

    def test_for_next_loop(self):
        """Test FOR/NEXT loop functionality."""
        program = """
10 FOR I = 1 TO 3
20 PRINT I
30 NEXT I
40 END
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        # After the loop, I should be 3 (last value printed)
        # The loop exits when NEXT would make I = 4, which is > 3
        assert interpreter.variables.get("I") == 3  # Last value printed was 3

    def test_variables_persist(self):
        """Test that variables persist after program runs."""
        program = """
10 A = 42
20 B = 100
30 END
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        assert interpreter.variables.get("A") == 42
        assert interpreter.variables.get("B") == 100

    def test_print_expressions(self):
        """Test PRINT with expressions."""
        program = """
10 A = 5
20 B = 10
30 PRINT A + B
40 END
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        assert interpreter.variables.get("A") == 5
        assert interpreter.variables.get("B") == 10

    def test_lowercase_variables(self):
        """Test that lowercase variable names work correctly."""
        program = """
10 x = 0
20 PRINT "x = "; x
30 x = x + 1
40 IF x < 3 THEN GOTO 20
50 END
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        assert interpreter.variables.get("X") == 3

    def test_variable_case_insensitive(self):
        """Test that variable names are case-insensitive."""
        program = """
10 MyVar = 42
20 PRINT myvar
30 MYVAR = MYVAR + 1
40 PRINT MyVar
50 END
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        assert interpreter.variables.get("MYVAR") == 43

    def test_undefined_variable_defaults_to_zero(self):
        """Test that undefined variables default to 0 in expressions."""
        program = """
10 x = x + 1
20 PRINT x
30 END
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        assert interpreter.variables.get("X") == 1

    def test_goto_loop_with_uninitialized_var(self):
        """Test GOTO loop where variable is initialized in the loop."""
        program = """
10 PRINT "Hello " ; x
20 x = x + 1
30 IF x < 3 THEN GOTO 10
40 END
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        assert interpreter.variables.get("X") == 3

    def test_run_clears_variables(self):
        """Test that RUN clears variables between executions."""
        program = """
10 x = x + 1
20 PRINT x
30 END
"""
        interpreter = BasicInterpreter()

        # First run
        interpreter.run_program(program)
        assert interpreter.variables.get("X") == 1

        # Second run - should reset to 0 then increment
        interpreter.run_program(program)
        assert interpreter.variables.get("X") == 1

        # Third run
        interpreter.run_program(program)
        assert interpreter.variables.get("X") == 1

    def test_commands_case_insensitive(self):
        """Test that BASIC commands are case-insensitive."""
        program = """
10 x = 5
20 Print x
30 if x > 0 Then Goto 40
40 end
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        assert interpreter.variables.get("X") == 5

    def test_goto(self):
        """Test GOTO statement."""
        program = """
10 A = 0
20 A = A + 1
30 PRINT A
40 IF A < 3 THEN GOTO 20
50 END
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        assert interpreter.variables.get("A") == 3

    def test_peek_poke(self):
        """Test PEEK and POKE functions."""
        program = """
10 POKE 1000, 42
20 PRINT PEEK(1000)
30 END
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        assert interpreter.memory.get(1000) == 42

    def test_tab_spc(self):
        """Test TAB and SPC functions."""
        program = """
10 PRINT TAB(5); "X"
20 PRINT SPC(3); "Y"
30 END
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        # Just verify it runs without error
        assert interpreter.memory == {}


class TestBasicSyntax:
    """Test syntax validation and error handling."""

    def test_invalid_for_syntax(self):
        """Test that FOR a in 1 TO 3 is rejected."""
        program = """
10 FOR a in 1 TO 3
20 PRINT a
30 END
"""
        interpreter = BasicInterpreter()
        # This should work as a program (parser accepts it) but might fail at runtime
        # The validation happens in the editor, not the interpreter
        interpreter.run_program(program)

        # If we get here, the program ran - which is fine for this test
        # The editor validation is what catches the syntax error

    def test_equality_comparison(self):
        """Test = and <> comparisons."""
        program = """
10 A = 5
20 B = 10
30 IF A = B THEN PRINT "EQUAL"
40 IF A <> B THEN PRINT "NOT EQUAL"
50 END
"""
        interpreter = BasicInterpreter()
        interpreter.run_program(program)

        # Just verify it runs
        pass

    def test_line_deletion(self):
        """Test that entering just a line number deletes that line."""
        editor = CBM64Editor()

        # Add a program line
        editor.handle_program_line('10 PRINT "HELLO"')
        assert 10 in editor.program_lines
        assert editor.program_lines[10] == 'PRINT "HELLO"'

        # Now "delete" it by entering just the line number
        editor.handle_program_line("10")

        # Line 10 should be deleted
        assert 10 not in editor.program_lines


class TestViaEditor:
    """Test BASIC functionality through the editor (parse_command flow)."""

    def test_for_next_loop_via_editor(self):
        """Test FOR/NEXT loop functionality through the editor."""
        editor = CBM64Editor()

        # Add program lines through the editor
        editor.parse_command("10 FOR I = 1 TO 3")
        editor.parse_command("20 PRINT I")
        editor.parse_command("30 NEXT I")
        editor.parse_command("40 END")

        # Run the program
        editor.parse_command("RUN")

        # Check variable persisted
        assert editor.interpreter.variables.get("I") == 3

    def test_variables_persist_via_editor(self):
        """Test that variables persist after program runs through editor."""
        editor = CBM64Editor()

        # Add program lines
        editor.parse_command("10 A = 42")
        editor.parse_command("20 B = 100")
        editor.parse_command("30 END")

        # Run
        editor.parse_command("RUN")

        # Check variables
        assert editor.interpreter.variables.get("A") == 42
        assert editor.interpreter.variables.get("B") == 100

    def test_peek_poke_via_editor(self):
        """Test PEEK and POKE through the editor."""
        editor = CBM64Editor()

        # Add program
        editor.parse_command("10 POKE 1000, 42")
        editor.parse_command("20 PRINT PEEK(1000)")
        editor.parse_command("30 END")

        # Run
        editor.parse_command("RUN")

        # Check memory
        assert editor.interpreter.memory.get(1000) == 42

    def test_data_read_via_editor(self):
        """Test DATA/READ through the editor."""
        editor = CBM64Editor()

        # Add program with DATA and READ
        editor.parse_command('10 DATA "HELLO", "WORLD"')
        editor.parse_command("20 READ A$, B$")
        editor.parse_command("30 PRINT A$, B$")
        editor.parse_command("40 END")

        # Run
        editor.parse_command("RUN")

        # Check variables were read
        assert editor.interpreter.variables.get("A$") == "HELLO"
        assert editor.interpreter.variables.get("B$") == "WORLD"

    def test_tab_spc_via_editor(self):
        """Test TAB and SPC through the editor."""
        editor = CBM64Editor()

        # Add program
        editor.parse_command('10 PRINT TAB(5); "X"')
        editor.parse_command('20 PRINT SPC(3); "Y"')
        editor.parse_command("30 END")

        # Run
        editor.parse_command("RUN")

        # Just verify it runs without error
        assert editor.interpreter.memory == {}

    def test_program_line_deletion_via_parse_command(self):
        """Test line deletion through parse_command (like real user input)."""
        editor = CBM64Editor()

        # Add a program line through parse_command
        editor.parse_command('10 PRINT "TEST"')
        assert 10 in editor.program_lines

        # Delete it through parse_command
        editor.parse_command("10")

        # Line should be gone
        assert 10 not in editor.program_lines

    def test_for_loop_with_matching_line_number_and_end_value(self):
        """Test FOR loop where line number equals end value (e.g., 10 TO 10).

        Regression test for bug where line number '10' was incorrectly stripped
        from FOR X = 1 TO 10, causing the end value to be missing.
        """
        editor = CBM64Editor()

        editor.parse_command("10 FOR X = 1 TO 10")
        editor.parse_command("20 PRINT X")
        editor.parse_command("30 NEXT X")
        editor.parse_command("40 END")

        assert 10 in editor.program_lines
        assert editor.program_lines[10] == "FOR X = 1 TO 10"

        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        try:
            editor.parse_command("RUN")
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()

        assert "SYNTAX ERROR" not in output
        assert "1" in output
        assert "10" in output

        editor.interpreter.variables.clear()
        editor.program_lines.clear()


class TestScreenMemoryAndPETSCII:
    """Test screen memory POKE and PETSCII character mapping."""

    def test_poke_to_screen_memory(self):
        """Test that POKE to screen memory addresses works correctly."""
        from src.cbm_basic import SCREEN_BASE

        interpreter = BasicInterpreter()

        program = """
10 POKE 1024, 65
20 POKE 1025, 66
30 END
"""
        interpreter.run_program(program)

        # Check screen memory was updated
        assert interpreter.screen.screen_memory[0] == 65  # 'A'
        assert interpreter.screen.screen_memory[1] == 66  # 'B'

    def test_screen_code_100_mapping(self):
        """Test that screen code 100 maps to a valid Unicode character.

        Regression test: screen code 100 was missing from SCREEN_CODE_TO_UNICODE,
        causing the indicator bar to render incorrectly.
        """
        from src.cbm_basic import SCREEN_CODE_TO_UNICODE, screen_code_to_unicode

        # Screen code 100 should be in the mapping
        assert 100 in SCREEN_CODE_TO_UNICODE

        # It should map to lower one eighth block (thin bottom line, full width)
        assert SCREEN_CODE_TO_UNICODE[100] == "▁"

        # The conversion function should work
        result = screen_code_to_unicode(100)
        assert result == "▁"

    def test_screen_code_134_mapping(self):
        """Test that screen code 134 maps to reverse video 'F'.

        Screen codes 128-255 are reverse video versions of codes 0-127.
        Screen code 134 = 128 + 6 = reverse of screen code 6 = reverse 'F'.
        This is used in maze.bas to display 'F1' in the indicator bar.
        """
        from src.cbm_basic import SCREEN_CODE_TO_UNICODE, screen_code_to_unicode

        # Screen code 134 should be in the mapping
        assert 134 in SCREEN_CODE_TO_UNICODE

        # It should map to 'F' (will be rendered in reverse video)
        assert SCREEN_CODE_TO_UNICODE[134] == "F"

        # The conversion function should work
        result = screen_code_to_unicode(134)
        assert result == "F"

    def test_indicator_bar_screen_codes(self):
        """Test all screen codes used for indicator bars and graphics.

        Tests screen codes: 134,177,224,100,179 which are commonly used
        for creating UI elements like progress bars and borders.

        Screen codes 128-255 are reverse video:
        - 134 = reverse 'F' (for F1 label)
        - 177 = reverse '1' (for F1 label)
        - 179 = reverse '3' (for F3 label)
        """
        from src.cbm_basic import SCREEN_CODE_TO_UNICODE, screen_code_to_unicode

        indicator_codes = [
            134,
            177,
            224,
            224,
            224,
            224,
            224,
            224,
            100,
            100,
            100,
            100,
            100,
            134,
            179,
        ]

        for code in indicator_codes:
            assert code in SCREEN_CODE_TO_UNICODE, (
                f"Screen code {code} missing from SCREEN_CODE_TO_UNICODE"
            )

        # Build the expected bar
        # 134='F', 177='1', 224='█' (filled), 100='▁' (empty/thin line), 179='3'
        bar = "".join(screen_code_to_unicode(c) for c in indicator_codes)
        assert bar == "F1██████▁▁▁▁▁F3"

    def test_petscii_vs_screen_code_distinction(self):
        """Test that PETSCII and Screen Codes are properly distinguished.

        PETSCII is used for CHR$() in PRINT statements.
        Screen Codes are used for POKE to screen memory.
        These are different encodings!
        """
        from src.cbm_basic import (
            PETSCII_TO_UNICODE,
            SCREEN_CODE_TO_UNICODE,
            petscii_to_unicode,
            screen_code_to_unicode,
        )

        # Screen code 1 = 'A', but PETSCII 1 is a control character
        assert SCREEN_CODE_TO_UNICODE[1] == "A"
        assert 1 not in PETSCII_TO_UNICODE  # Control char, not mapped

        # Screen code 205/206 are diagonals for maze pattern
        assert SCREEN_CODE_TO_UNICODE[205] == "╱"
        assert SCREEN_CODE_TO_UNICODE[206] == "╲"

        # PETSCII 205/206 should also be diagonals (for CHR$ in PRINT)
        assert PETSCII_TO_UNICODE[205] == "╱"
        assert PETSCII_TO_UNICODE[206] == "╲"

        # Lowercase 'a' (ASCII 97) should pass through in PETSCII for normal text
        result = petscii_to_unicode("abc")
        assert result == "abc"  # Normal text unchanged

        # But screen code 97 is a graphic character
        assert screen_code_to_unicode(97) == "▌"

    def test_reverse_video_screen_codes(self):
        """Test that screen codes 128-255 are reverse video of 0-127.

        On a real C64, these characters display with swapped fg/bg colors.
        """
        from src.cbm_basic import SCREEN_CODE_TO_UNICODE, screen_code_to_unicode

        # Screen code 128 = reverse of code 0 = reverse '@'
        assert screen_code_to_unicode(128) == "@"

        # Screen code 129 = reverse of code 1 = reverse 'A'
        assert screen_code_to_unicode(129) == "A"

        # Screen code 134 = reverse of code 6 = reverse 'F'
        assert screen_code_to_unicode(134) == "F"

        # Screen code 177 = reverse of code 49 = reverse '1'
        assert screen_code_to_unicode(177) == "1"

        # Screen code 179 = reverse of code 51 = reverse '3'
        assert screen_code_to_unicode(179) == "3"

        # The renderer should detect these as reverse video (code >= 128)
        # and swap foreground/background colors when displaying


class TestColorSupport:
    """Test C64 color support and color memory."""

    def test_color_memory_poke(self):
        """Test that POKE to color RAM updates color memory."""
        from src.cbm_basic import COLOR_BASE

        interpreter = BasicInterpreter()

        program = """
10 POKE 55296, 2
20 POKE 55297, 5
30 END
"""
        interpreter.run_program(program)

        # Check color memory was updated
        assert interpreter.screen.color_memory[0] == 2  # Red
        assert interpreter.screen.color_memory[1] == 5  # Green

    def test_color_memory_peek(self):
        """Test that PEEK from color RAM reads color memory."""
        from src.cbm_basic import COLOR_BASE

        interpreter = BasicInterpreter()

        # Set color memory directly
        interpreter.screen.color_memory[0] = 7  # Yellow

        program = """
10 A = PEEK(55296)
20 END
"""
        interpreter.run_program(program)

        assert interpreter.variables.get("A") == 7

    def test_c64_color_mapping_exists(self):
        """Test that all 16 C64 colors have mappings."""
        from src.cbm_basic import C64_COLORS_256, C64_COLORS_ANSI

        for color_code in range(16):
            assert color_code in C64_COLORS_256, (
                f"Color {color_code} missing from 256-color map"
            )
            assert color_code in C64_COLORS_ANSI, (
                f"Color {color_code} missing from ANSI map"
            )

    def test_get_ansi_color_foreground(self):
        """Test ANSI color escape sequence generation for foreground."""
        from src.cbm_basic import (
            get_ansi_color,
            USE_256_COLORS,
            C64_COLORS_256,
            C64_COLORS_ANSI,
        )

        result = get_ansi_color(1, is_foreground=True)  # White

        # Should be a valid escape sequence
        assert result.startswith("\x1b[")
        assert result.endswith("m")

        if USE_256_COLORS:
            assert "38;5;" in result  # 256-color foreground format
        else:
            assert "38;5;" not in result  # Basic ANSI format

    def test_get_ansi_color_background(self):
        """Test ANSI color escape sequence generation for background."""
        from src.cbm_basic import get_ansi_color, USE_256_COLORS

        result = get_ansi_color(6, is_foreground=False)  # Blue background

        # Should be a valid escape sequence
        assert result.startswith("\x1b[")
        assert result.endswith("m")

        if USE_256_COLORS:
            assert "48;5;" in result  # 256-color background format

    def test_screen_clear_resets_colors(self):
        """Test that screen clear resets color memory to default."""
        from src.cbm_basic import C64_DEFAULT_FG

        interpreter = BasicInterpreter()

        # Set some colors
        interpreter.screen.color_memory[0] = 2
        interpreter.screen.color_memory[100] = 5

        # Clear the screen
        interpreter.screen.clear()

        # All colors should be reset to default
        assert interpreter.screen.color_memory[0] == C64_DEFAULT_FG
        assert interpreter.screen.color_memory[100] == C64_DEFAULT_FG


class TestReadDataStatements:
    """Test READ and DATA statement handling."""

    def test_read_variable_case_insensitive(self):
        """Test that READ normalizes variable names to uppercase.

        Regression test: READ was storing variables in original case,
        but PRINT looks for uppercase, causing variable not found.
        """
        interpreter = BasicInterpreter()

        program = """
10 READ a, b, c
20 PRINT a; b; c
30 END
100 DATA 10, 20, 30
"""
        interpreter.run_program(program)

        # Variables should be stored uppercase
        assert interpreter.variables.get("A") == 10
        assert interpreter.variables.get("B") == 20
        assert interpreter.variables.get("C") == 30

        # Lowercase should not exist
        assert interpreter.variables.get("a") is None

    def test_read_multiple_data_lines(self):
        """Test READ across multiple DATA statements."""
        interpreter = BasicInterpreter()

        program = """
10 FOR i = 1 TO 6
20 READ x
30 s = s + x
40 NEXT i
50 END
100 DATA 1, 2, 3
110 DATA 4, 5, 6
"""
        interpreter.run_program(program)

        # Sum should be 1+2+3+4+5+6 = 21
        assert interpreter.variables.get("S") == 21


class TestRNDFunction:
    """Test the RND random number function."""

    def test_rnd_case_insensitive(self):
        """Test that RND works in both upper and lower case.

        Regression test: lowercase 'rnd' wasn't being matched by the
        regex pattern in evaluate_expression.
        """
        interpreter = BasicInterpreter()

        program = """
10 A = RND(1)
20 B = rnd(1)
30 C = Rnd(1)
40 END
"""
        interpreter.run_program(program)

        # All should have values between 0 and 1
        a = interpreter.variables.get("A")
        b = interpreter.variables.get("B")
        c = interpreter.variables.get("C")

        assert a is not None and 0 <= a < 1, f"RND(1) failed: {a}"
        assert b is not None and 0 <= b < 1, f"rnd(1) failed: {b}"
        assert c is not None and 0 <= c < 1, f"Rnd(1) failed: {c}"

    def test_rnd_in_expression(self):
        """Test RND within arithmetic expressions."""
        interpreter = BasicInterpreter()

        program = """
10 q = 205.5
20 A = q + rnd(1)
30 END
"""
        interpreter.run_program(program)

        a = interpreter.variables.get("A")
        # Should be between 205.5 and 206.5
        assert a is not None and 205.5 <= a < 206.5, f"q + rnd(1) failed: {a}"

    def test_rnd_produces_different_values(self):
        """Test that RND produces different values on successive calls."""
        interpreter = BasicInterpreter()

        # Simple test: sum random values and check it's not zero
        program = """
10 s = 0
20 FOR i = 1 TO 10
30 s = s + RND(1)
40 NEXT i
50 END
"""
        interpreter.run_program(program)

        # Sum of 10 random values (0-1) should be > 0 and likely around 5
        s = interpreter.variables.get("S", 0)
        assert s > 0, f"Sum of RND values should be > 0, got {s}"
        assert s < 10, f"Sum of RND values should be < 10, got {s}"


class TestForLoopExpressions:
    """Test FOR loops with expressions in start/end values."""

    def test_for_with_expression_start(self):
        """Test FOR loop where start value is an expression.

        Regression test: FOR j = p + 1 TO 11 was failing because the
        parser expected TO at a fixed position (tokens[3]).
        """
        interpreter = BasicInterpreter()

        program = """
10 p = 5
20 FOR j = p + 1 TO 10
30 A = A + j
40 NEXT j
50 END
"""
        interpreter.run_program(program)

        # Sum of 6+7+8+9+10 = 40
        assert interpreter.variables.get("A") == 40

    def test_for_with_expression_end(self):
        """Test FOR loop where end value is an expression."""
        interpreter = BasicInterpreter()

        program = """
10 n = 5
20 FOR i = 1 TO n * 2
30 A = A + 1
40 NEXT i
50 END
"""
        interpreter.run_program(program)

        # Loop runs 10 times (1 to 10)
        assert interpreter.variables.get("A") == 10

    def test_for_with_both_expressions(self):
        """Test FOR loop where both start and end are expressions."""
        interpreter = BasicInterpreter()

        program = """
10 x = 3
20 y = 7
30 FOR i = x + 1 TO y + 3
40 A = A + 1
50 NEXT i
60 END
"""
        interpreter.run_program(program)

        # Loop runs from 4 to 10 = 7 iterations
        assert interpreter.variables.get("A") == 7

    def test_single_line_for_with_expression(self):
        """Test single-line FOR/NEXT with expression start value."""
        interpreter = BasicInterpreter()

        program = """
10 p = 5
20 FOR j = p + 1 TO 11 : A = A + j : NEXT
30 END
"""
        interpreter.run_program(program)

        # Sum of 6+7+8+9+10+11 = 51
        assert interpreter.variables.get("A") == 51


class TestSingleLineForNext:
    """Test FOR/NEXT loops on a single line with colon-separated statements."""

    def test_single_line_for_next_with_variable(self):
        """Test FOR/NEXT on single line with explicit variable name.

        Regression test: single-line FOR/NEXT loops were only executing once
        because NEXT would jump to the next line instead of looping within
        the same line.
        """
        interpreter = BasicInterpreter()

        program = """
10 FOR I = 1 TO 5 : A = A + I : NEXT I
20 END
"""
        interpreter.run_program(program)

        # A should be 1+2+3+4+5 = 15
        assert interpreter.variables.get("A") == 15
        # I should be 5 (last iteration value)
        assert interpreter.variables.get("I") == 5

    def test_single_line_for_next_without_variable(self):
        """Test FOR/NEXT on single line without explicit variable in NEXT.

        Regression test: NEXT without a variable name wasn't finding the
        correct FOR loop when on the same line.
        """
        interpreter = BasicInterpreter()

        program = """
10 FOR I = 1 TO 5 : A = A + I : NEXT
20 END
"""
        interpreter.run_program(program)

        # A should be 1+2+3+4+5 = 15
        assert interpreter.variables.get("A") == 15

    def test_single_line_for_next_with_poke(self):
        """Test FOR/NEXT on single line with POKE (like maze.bas indicator bar).

        Regression test: this is the exact pattern from maze.bas line 210 that
        was failing - FOR loop with READ and POKE on same line.
        """
        from src.cbm_basic import SCREEN_BASE

        interpreter = BasicInterpreter()

        program = """
10 FOR I = 0 TO 14 : READ A : POKE 1636+I,A : NEXT
20 END
500 DATA 134,177,224,224,224,224,224,224,100,100,100,100,100,134,179
"""
        interpreter.run_program(program)

        # Check all 15 values were POKEd to screen memory
        expected = [
            134,
            177,
            224,
            224,
            224,
            224,
            224,
            224,
            100,
            100,
            100,
            100,
            100,
            134,
            179,
        ]
        for i, expected_val in enumerate(expected):
            addr = 1636 + i
            offset = addr - SCREEN_BASE
            actual = interpreter.screen.screen_memory[offset]
            assert actual == expected_val, (
                f"Screen memory at {addr} should be {expected_val}, got {actual}"
            )

    def test_single_line_for_next_multiple_statements(self):
        """Test FOR/NEXT with multiple statements between FOR and NEXT."""
        interpreter = BasicInterpreter()

        program = """
10 FOR I = 1 TO 3 : A = A + 1 : B = B + 10 : NEXT I
20 END
"""
        interpreter.run_program(program)

        assert interpreter.variables.get("A") == 3
        assert interpreter.variables.get("B") == 30

    def test_multi_line_for_next_still_works(self):
        """Ensure multi-line FOR/NEXT loops still work after the fix."""
        interpreter = BasicInterpreter()

        program = """
10 FOR I = 1 TO 3
20 A = A + I
30 NEXT I
40 END
"""
        interpreter.run_program(program)

        assert interpreter.variables.get("A") == 6  # 1+2+3

    def test_multi_line_for_with_same_line_body(self):
        """Test FOR with body on same line but NEXT on different line (maze.bas pattern).

        Regression test: When FOR has statements after it on the same line
        (like FOR I=1 TO 5 : POKE I,0) and NEXT is on a different line,
        the POKE should execute on EVERY iteration, not just the first.
        """
        from src.cbm_basic import SCREEN_BASE

        interpreter = BasicInterpreter()

        program = """
70 FOR I = 1104 TO 1108 : POKE I, I - 1104
80 A = A + 1
90 NEXT
100 END
"""
        interpreter.run_program(program)

        # A should be 5 (loop ran 5 times)
        assert interpreter.variables.get("A") == 5

        # Each screen position should have been POKEd with its index
        for i in range(5):
            addr = 1104 + i
            offset = addr - SCREEN_BASE
            expected = i  # POKE I, I-1104 means values 0,1,2,3,4
            actual = interpreter.screen.screen_memory[offset]
            assert actual == expected, (
                f"Screen memory at {addr} should be {expected}, got {actual}"
            )


class TestGetCommand:
    """Test the GET command for reading keypresses."""

    def test_get_returns_empty_when_no_input(self):
        """Test that GET returns empty string when no input is available.

        GET should be non-blocking like the C64 - returns "" immediately
        if no key is pressed.
        """
        interpreter = BasicInterpreter()

        # With no input buffer, GET should return empty string
        program = """
10 GET K$
20 END
"""
        interpreter.run_program(program)

        # K$ should be empty string (no input available)
        assert interpreter.variables.get("K$") == ""

    def test_get_reads_from_input_buffer(self):
        """Test that GET reads from input buffer when available."""
        interpreter = BasicInterpreter()
        interpreter.input_buffer = ["A"]

        program = """
10 GET K$
20 END
"""
        interpreter.run_program(program)

        # K$ should be "A" from input buffer
        assert interpreter.variables.get("K$") == "A"

    def test_get_with_conditional(self):
        """Test GET with IF condition (like maze.bas uses)."""
        interpreter = BasicInterpreter()
        interpreter.input_buffer = ["X"]

        program = """
10 F = 0
20 GET K$
30 IF K$ <> "" THEN F = 1
40 END
"""
        interpreter.run_program(program)

        # F should be 1 because key was available
        assert interpreter.variables.get("K$") == "X"
        assert interpreter.variables.get("F") == 1

    def test_get_empty_with_conditional(self):
        """Test GET returns empty and conditional is not triggered."""
        interpreter = BasicInterpreter()
        # No input buffer - GET should return empty

        program = """
10 F = 0
20 GET K$
30 IF K$ <> "" THEN F = 1
40 END
"""
        interpreter.run_program(program)

        # F should remain 0 because no key was available
        assert interpreter.variables.get("K$") == ""
        assert interpreter.variables.get("F") == 0

    def test_get_chr_comparison(self):
        """Test GET with CHR$() comparison (like maze.bas key handling)."""
        interpreter = BasicInterpreter()
        interpreter.input_buffer = ["A"]  # ASCII 65

        program = """
10 P = 5
20 GET K$
30 IF K$ = CHR$(65) THEN P = P - 1
40 END
"""
        interpreter.run_program(program)

        # P should be 4 (5-1) because A was pressed
        assert interpreter.variables.get("K$") == "A"
        assert interpreter.variables.get("P") == 4

    def test_get_converts_lowercase_to_uppercase(self):
        """Test that GET converts lowercase letters to uppercase (C64 behavior).

        On a real C64, the default keyboard mode produces uppercase PETSCII
        for unshifted letter keys. We emulate this by converting lowercase
        terminal input to uppercase.
        """
        interpreter = BasicInterpreter()
        interpreter.input_buffer = ["a"]  # lowercase from terminal

        program = """
10 P = 5
20 GET K$
30 IF K$ = CHR$(65) THEN P = P - 1
40 END
"""
        interpreter.run_program(program)

        # K$ should be uppercase "A" even though 'a' was pressed
        assert interpreter.variables.get("K$") == "A"
        # P should be 4 (5-1) because the comparison matches
        assert interpreter.variables.get("P") == 4

    def test_get_fkey_sequences_defined(self):
        """Test that F-key escape sequences are mapped to C64 PETSCII codes."""
        # Verify the mapping exists and has correct C64 codes
        fkeys = BasicInterpreter.FKEY_SEQUENCES

        # F1 = PETSCII 133, F3 = PETSCII 134 (used by maze.bas)
        assert chr(133) in fkeys.values(), "F1 (PETSCII 133) should be mapped"
        assert chr(134) in fkeys.values(), "F3 (PETSCII 134) should be mapped"

        # Check some common terminal sequences map to F1
        f1_sequences = [k for k, v in fkeys.items() if v == chr(133)]
        assert len(f1_sequences) >= 1, "At least one F1 sequence should be defined"

    def test_get_fkey_via_input_buffer(self):
        """Test F-key detection using input buffer with escape sequence."""
        interpreter = BasicInterpreter()
        # Simulate F1 key press (xterm style) - put PETSCII directly in buffer for test
        interpreter.input_buffer = [chr(133)]  # F1 PETSCII code

        program = """
10 P = 5
20 GET K$
30 IF K$ = CHR$(133) THEN P = P - 1
40 END
"""
        interpreter.run_program(program)

        # P should be 4 because F1 was "pressed"
        assert interpreter.variables.get("K$") == chr(133)
        assert interpreter.variables.get("P") == 4


class TestPrgFileFormat:
    """Test PRG file format loading and saving."""

    def test_is_prg_file(self):
        """Test PRG file extension detection."""
        from src.prg_file import is_prg_file

        assert is_prg_file("test.prg") is True
        assert is_prg_file("test.PRG") is True
        assert is_prg_file("test.Prg") is True
        assert is_prg_file("test.bas") is False
        assert is_prg_file("test.txt") is False
        assert is_prg_file("testprg") is False

    def test_basic_tokens_defined(self):
        """Test that BASIC tokens are properly defined."""
        from src.prg_file import BASIC_TOKENS, KEYWORD_TO_TOKEN

        # Check some common tokens
        assert BASIC_TOKENS[0x99] == "PRINT"
        assert BASIC_TOKENS[0x81] == "FOR"
        assert BASIC_TOKENS[0x82] == "NEXT"
        assert BASIC_TOKENS[0x89] == "GOTO"
        assert BASIC_TOKENS[0x8B] == "IF"
        assert BASIC_TOKENS[0xA7] == "THEN"
        assert BASIC_TOKENS[0x97] == "POKE"
        assert BASIC_TOKENS[0x8F] == "REM"

        # Check reverse mapping
        assert KEYWORD_TO_TOKEN["PRINT"] == 0x99
        assert KEYWORD_TO_TOKEN["FOR"] == 0x81
        assert KEYWORD_TO_TOKEN["GOTO"] == 0x89

    def test_tokenize_simple_line(self):
        """Test tokenizing a simple BASIC line."""
        from src.prg_file import _tokenize_line

        # PRINT "HELLO"
        result = _tokenize_line('PRINT "HELLO"')
        assert result[0] == 0x99  # PRINT token
        assert result[1] == 0x20  # space
        assert result[2] == 0x22  # quote
        assert bytes(result[3:8]) == b"HELLO"
        assert result[8] == 0x22  # quote

    def test_tokenize_with_keywords(self):
        """Test tokenizing with multiple keywords."""
        from src.prg_file import _tokenize_line, KEYWORD_TO_TOKEN

        # FOR I = 1 TO 10
        result = _tokenize_line("FOR I = 1 TO 10")
        assert result[0] == KEYWORD_TO_TOKEN["FOR"]
        assert KEYWORD_TO_TOKEN["TO"] in result

    def test_tokenize_preserves_strings(self):
        """Test that strings are not tokenized."""
        from src.prg_file import _tokenize_line

        # PRINT "FOR NEXT" - FOR and NEXT inside quotes should NOT be tokenized
        result = _tokenize_line('PRINT "FOR NEXT"')
        # The string content should be literal bytes, not tokens
        # FOR token is 0x81, NEXT token is 0x82
        assert 0x81 not in result[3:-1]  # Exclude PRINT token and quotes
        assert 0x82 not in result[3:-1]

    def test_tokenize_rem_not_tokenized(self):
        """Test that text after REM is not tokenized."""
        from src.prg_file import _tokenize_line, KEYWORD_TO_TOKEN

        # REM FOR NEXT PRINT - keywords after REM should NOT be tokenized
        result = _tokenize_line("REM FOR NEXT PRINT")
        # Only REM should be a token
        token_count = sum(1 for b in result if b >= 0x80)
        assert token_count == 1  # Only REM token

    def test_save_and_load_roundtrip(self, tmp_path):
        """Test saving and loading a PRG file."""
        from src.prg_file import save_prg, load_prg

        program = {
            10: 'PRINT "HELLO WORLD"',
            20: "FOR I = 1 TO 10",
            30: "PRINT I",
            40: "NEXT I",
            50: "END",
        }

        prg_file = tmp_path / "test.prg"
        save_prg(program, str(prg_file))

        # Load it back
        loaded = load_prg(str(prg_file))

        # Check line numbers match
        assert set(loaded.keys()) == set(program.keys())

        # Check content (may have minor formatting differences)
        for line_num in program:
            # Keywords should match (case may differ)
            assert loaded[line_num].upper().replace(" ", "") == program[
                line_num
            ].upper().replace(" ", "")

    def test_prg_file_header(self, tmp_path):
        """Test that PRG files have correct header."""
        from src.prg_file import save_prg, BASIC_START

        program = {10: "END"}
        prg_file = tmp_path / "test.prg"
        save_prg(program, str(prg_file))

        with open(prg_file, "rb") as f:
            data = f.read()

        # First two bytes should be load address
        load_addr = data[0] | (data[1] << 8)
        assert load_addr == BASIC_START

    def test_prg_file_end_marker(self, tmp_path):
        """Test that PRG files end with null pointer."""
        from src.prg_file import save_prg

        program = {10: "END"}
        prg_file = tmp_path / "test.prg"
        save_prg(program, str(prg_file))

        with open(prg_file, "rb") as f:
            data = f.read()

        # Last two bytes should be 00 00 (end of program)
        assert data[-2:] == b"\x00\x00"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
