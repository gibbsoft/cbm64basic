#!/usr/bin/env python3
"""
Commodore 64 BASIC Editor - SIMPLIFIED WITH PROMPT_TOOLKIT
====================================================
A retro-style editor with improved input handling using prompt_toolkit.
"""

import sys
import time
import importlib.util
import re
from pathlib import Path
from typing import Dict
import os

try:
    import termios
except ImportError:
    termios = None

# prompt_toolkit imports
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText, HTML
from prompt_toolkit import print_formatted_text
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.validation import Validator, ValidationError
import colorama

# Initialize colorama with strip=False to preserve ANSI codes
colorama.init(strip=False)

# Import BASIC interpreter
BASIC_PATH = Path(__file__).parent / "cbm_basic.py"
spec = importlib.util.spec_from_file_location("cbm_basic", str(BASIC_PATH))
if spec is not None and spec.loader is not None:
    cbm_basic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cbm_basic)
    BasicInterpreter = cbm_basic.BasicInterpreter


class BasicLineValidator(Validator):
    """Validates BASIC program lines and returns errors with positions"""

    def validate(self, document):
        text = document.text.strip()

        # Skip empty lines
        if not text:
            return

        # Check if it's a numbered line
        parts = text.split(None, 1)
        if not parts[0].isdigit():
            return  # Not a program line, let other validators handle it

        line_num = int(parts[0])
        code = parts[1] if len(parts) > 1 else ""

        # Line number only means delete - this is valid
        if not code:
            return

        # Tokenize the line using the interpreter
        temp_interp = BasicInterpreter()
        full_line = f"{line_num} {code}"
        parsed_num, tokens = temp_interp.tokenize(full_line)

        if not tokens:
            raise ValidationError(cursor_position=len(text), message="?SYNTAX ERROR")

        command = tokens[0].upper()

        # Check FOR syntax - must use = not in
        if command == "FOR":
            if len(tokens) < 5:
                raise ValidationError(
                    cursor_position=len(text), message="?SYNTAX ERROR"
                )
            # Check for "IN" (should be "=")
            # tokens format: ['FOR', 'varname', '=', 'start', 'TO', 'end']
            if tokens[2].upper() == "IN":
                # Find position of "IN" in the original text
                pos = code.find("in")
                if pos == -1:
                    pos = code.find("IN")
                if pos != -1:
                    raise ValidationError(
                        cursor_position=len(str(line_num)) + 2 + pos,
                        message="?USE = NOT IN",
                    )

        # Check for invalid line number usage (commands that should be immediate)
        immediate_commands = [
            "LIST",
            "RUN",
            "NEW",
            "LOAD",
            "SAVE",
            "CLR",
            "CONT",
            "DELETE",
            "RENUM",
            "AUTO",
            "CLS",
            "HELP",
            "BYE",
        ]
        if command in immediate_commands:
            raise ValidationError(
                cursor_position=len(str(line_num)) + 1,
                message=f"?SYNTAX ERROR IN {line_num}",
            )


# Prompt_toolkit style names for syntax highlighting
COLORS = {
    "lineno": "ansiyellow",  # Orange/Yellow
    "keyword": "ansiblue",  # Blue
    "number": "ansiyellow",  # Yellow
    "string": "ansigreen",  # Green
    "variable": "ansicyan",  # Cyan
    "operator": "ansiwhite",  # White
    "comment": "ansigray",  # Gray
    "error": "ansired bold blink",  # Flashing red for error
    "reset": "",  # No style
}

BASIC_KEYWORDS = {
    "?",
    "PRINT",
    "LET",
    "GOTO",
    "GOSUB",
    "RETURN",
    "IF",
    "THEN",
    "ELSE",
    "FOR",
    "NEXT",
    "TO",
    "STEP",
    "REM",
    "DATA",
    "READ",
    "INPUT",
    "END",
    "STOP",
    "NEW",
    "LIST",
    "LOAD",
    "SAVE",
    "CLR",
    "CONT",
    "DEL",
    "EDIT",
    "AUTO",
    "CLS",
    "RUN",
    "BYE",
    "HELP",
    "NOT",
    "AND",
    "OR",
    "XOR",
    "DEF",
    "FN",
    "DIM",
    "POKE",
    "PEEK",
    "SYS",
    "OPEN",
    "CLOSE",
    "GET",
    "PUT",
    "WAIT",
    "VERIFY",
    "COLLECT",
    "COPY",
    "SCRATCH",
    "BACKUP",
    "DIRECTORY",
    "PEEK",
    "POKE",
    "TAB",
    "SPC",
}


def format_basic_line(line_num: int, code: str) -> str:
    """Format BASIC line: uppercase keywords, normalize whitespace"""

    # Create temporary interpreter to access tokenizer
    temp_interp = BasicInterpreter()

    # Tokenize line
    full_line = f"{line_num} {code}"
    _, tokens = temp_interp.tokenize(full_line)

    if not tokens:
        return code

    formatted_parts = []

    for token in tokens:
        if token == str(line_num):
            continue

        if token.upper() in BASIC_KEYWORDS:
            formatted_parts.append(token.upper())
        else:
            formatted_parts.append(token)

    return " ".join(formatted_parts)


def colorize_basic_line(line_num: int, code: str) -> FormattedText:
    """Apply syntax highlighting to a BASIC line"""

    # Create temporary interpreter to access tokenizer
    temp_interp = BasicInterpreter()

    # Tokenize line
    full_line = f"{line_num} {code}"
    _, tokens = temp_interp.tokenize(full_line)

    result = []

    # Add colored line number
    result.append((COLORS["lineno"], str(line_num)))
    result.append(("", " "))

    for token in tokens:
        if token == str(line_num):
            continue

        token_upper = token.upper()

        if token_upper == "REM":
            # Everything after REM is a comment
            result.append((COLORS["comment"], token_upper))
        elif token_upper in BASIC_KEYWORDS:
            result.append((COLORS["keyword"], token_upper))
        elif token.startswith('"') and token.endswith('"'):
            result.append((COLORS["string"], token))
        elif token.replace(".", "").replace("-", "").isdigit() or (
            token.replace(".", "").isdigit() and token[0] == "-"
        ):
            result.append((COLORS["number"], token))
        elif token in ["+", "-", "*", "/", "=", "<", ">", "<=", ">=", "<>"]:
            result.append((COLORS["operator"], token))
        elif token in [";", ","]:
            result.append(("", token))
        else:
            result.append((COLORS["variable"], token))

        result.append(("", " "))

    return FormattedText(result)


class CBM64Editor:
    def __init__(self):
        self.program_lines: Dict[int, str] = {}
        self.program_running = False
        self.program_interrupted = False
        self.last_executed_line = None

        # Setup prompt_toolkit session
        self.session = PromptSession()

        # Create interpreter separately - don't inject prompt_func initially
        self.interpreter = BasicInterpreter()

    def boot_banner(self):
        """Display authentic Commodore 64 boot banner"""
        print("=" * 64)
        print("**** COMMODORE BASIC V2 ****")
        print(" 64K RAM SYSTEM  38911 BASIC BYTES FREE")
        print("=" * 64)
        print()
        time.sleep(0.5)

    def show_prompt(self):
        """Display the appropriate prompt"""
        print("READY.")
        print()

    def parse_command(self, command: str):
        """Parse and execute a single command - returns True if READY should be shown"""
        command = command.strip()

        if not command:
            return False

        parts = command.split()
        if parts and parts[0].isdigit():
            # Validate the program line first
            validator = BasicLineValidator()
            try:
                from prompt_toolkit.document import Document

                validator.validate(Document(text=command))
            except ValidationError as e:
                print(f"?{e.message}")
                return False  # Don't show READY, line was rejected

            self.handle_program_line(command)
            return False  # Don't show READY after program lines
        else:
            self.handle_immediate_command(command)
            return True  # Show READY after immediate commands

    def handle_program_line(self, line: str):
        """Handle a numbered program line - returns True if READY should be shown"""
        parts = line.split(" ", 1)
        if len(parts) >= 2:
            line_num = int(parts[0])
            code = parts[1].strip()

            # Format line
            formatted_code = format_basic_line(line_num, code)

            # Check for immediate mode commands in program lines
            command_part = formatted_code.split()[0] if formatted_code else ""
            if command_part.upper() in [
                "LIST",
                "RUN",
                "NEW",
                "LOAD",
                "SAVE",
                "CLR",
                "CONT",
                "DELETE",
                "RENUM",
                "AUTO",
                "CLS",
            ]:
                # Move cursor up one line, clear it, and show error
                sys.stdout.write("\033[F\033[2K")
                sys.stdout.flush()
                print_formatted_text(
                    FormattedText([("ansired", f"?SYNTAX ERROR IN {line_num}")])
                )
            else:
                # Store formatted version
                self.program_lines[line_num] = formatted_code
                # Move cursor up one line, clear it, and print formatted version
                sys.stdout.write("\033[F\033[2K")
                sys.stdout.flush()
                print_formatted_text(colorize_basic_line(line_num, formatted_code))
        else:
            # Just a line number - delete line
            line_num = int(parts[0])
            if line_num in self.program_lines:
                del self.program_lines[line_num]
                print(f"{line_num} DELETED")

    def handle_immediate_command(self, command: str):
        """Handle immediate mode commands"""
        cmd_upper = command.upper()

        if cmd_upper == "LIST":
            self.list_program()
        elif cmd_upper == "RUN":
            self.run_program()
        elif cmd_upper == "NEW":
            self.new_program()
        elif cmd_upper == "LOAD":
            self.load_program()
        elif cmd_upper == "SAVE":
            self.save_program()
        elif cmd_upper == "CLR":
            self.clear_variables()
        elif cmd_upper == "HELP":
            self.show_help()
        elif cmd_upper == "BYE":
            print("GOODBYE!")
            sys.exit(0)
        else:
            self.execute_immediate(command)

    def list_program(self):
        """LIST command - display current program with syntax highlighting"""
        if not self.program_lines:
            print()
            return

        for line_num in sorted(self.program_lines.keys()):
            code = self.program_lines[line_num]
            print_formatted_text(colorize_basic_line(line_num, code))
        print()

    def run_program(self):
        """RUN command - execute the current program"""
        if not self.program_lines:
            print("?NO PROGRAM NAME ERROR")
            return

        program_source = ""
        for line_num in sorted(self.program_lines.keys()):
            program_source += f"{line_num} {self.program_lines[line_num]}\n"
        program_source += "999 END"

        print()
        try:
            # Don't pre-fill input buffer - let GET actually read from stdin
            self.interpreter.prompt_func = lambda: input()
            self.interpreter.run_program(program_source)
            # Reset back to None (for immediate mode)
            self.interpreter.prompt_func = None
        except Exception as e:
            print(f"?{type(e).__name__.upper()} ERROR")

    def new_program(self):
        """NEW command - clear current program"""
        self.program_lines.clear()

    def load_program(self):
        """LOAD command"""
        if sys.stdin.isatty():
            filename = self.session.prompt("FILENAME? ").strip()
        else:
            print("FILENAME? ", end="", flush=True)
            filename = input().strip()

        if not filename:
            filename = "program.bas"

        try:
            with open(filename, "r") as f:
                self.program_lines.clear()
                for line in f:
                    line = line.strip()
                    if line and line[0].isdigit():
                        parts = line.split(" ", 1)
                        if len(parts) >= 2:
                            line_num = int(parts[0])
                            code = parts[1].strip()
                            self.program_lines[line_num] = code
                print("SEARCHING FOR *")
                print("LOADING")
        except FileNotFoundError:
            print("?FILE NOT FOUND")

    def save_program(self):
        """SAVE command"""
        if sys.stdin.isatty():
            filename = self.session.prompt("FILENAME? ").strip()
        else:
            print("FILENAME? ", end="", flush=True)
            filename = input().strip()

        if not filename:
            filename = "program.bas"

        try:
            with open(filename, "w") as f:
                for line_num in sorted(self.program_lines.keys()):
                    f.write(f"{line_num} {self.program_lines[line_num]}\n")
                print("WRITING *")
                print("OK")
        except Exception as e:
            print(f"?{type(e).__name__.upper()} ERROR")

    def clear_variables(self):
        """CLR command"""
        self.interpreter.variables.clear()

    def execute_immediate(self, command: str):
        """Execute a command in immediate mode"""
        temp_program = f"10 {command}\n20 END"

        try:
            self.interpreter.run_program(temp_program)
        except Exception:
            print("?SYNTAX ERROR")

    def show_help(self):
        """HELP command"""
        print("COMMODORE 64 BASIC V2 HELP")
        print("===========================")
        print("IMMEDIATE MODE COMMANDS:")
        print("  LIST          - List current program")
        print("  RUN           - Execute current program")
        print("  NEW           - Clear current program")
        print("  CLR           - Clear all variables")
        print("  HELP          - Show this help")
        print("  BYE           - Exit BASIC")
        print()
        print("PROGRAM MODE:")
        print("  <number> <code>  - Add/change program line")
        print("  <number>         - Delete program line")
        print()

    def run(self):
        """Main editor loop"""
        self.boot_banner()
        self.show_prompt()  # Show first READY

        # Create validator for BASIC lines
        validator = BasicLineValidator()

        while True:
            try:
                # Try to use prompt_toolkit if available and in terminal
                if sys.stdin.isatty():
                    try:
                        command = self.session.prompt(
                            "",
                            validator=validator,
                            validate_while_typing=False,
                        )
                        # No validation error, accept the line
                        show_ready = self.parse_command(command)
                        if show_ready:
                            self.show_prompt()
                    except ValidationError as ve:
                        # Validation error - don't accept the line
                        # Show error message with flashing glyph at problem position
                        print()  # New line
                        # Create error display with flashing glyph at cursor position
                        error_pos = ve.cursor_position
                        error_line = " " * error_pos + " \033[5m█\033[0m  " + ve.message
                        print(error_line, flush=True)
                        # Don't show READY, let user edit
                else:
                    # Fall back to regular input for non-interactive
                    command = input("")

                    show_ready = self.parse_command(command)
                    if show_ready:
                        self.show_prompt()
            except KeyboardInterrupt:
                print()
                self.program_interrupted = True
                print("BREAK")
            except EOFError:
                print()
                print("GOODBYE!")
                break
            except Exception as e:
                print(f"?{type(e).__name__.upper()} ERROR")


def main():
    """Main entry point"""
    editor = CBM64Editor()
    editor.run()


if __name__ == "__main__":
    main()
