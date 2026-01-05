#!/usr/bin/env python3
"""
Commodore 64 BASIC V2 Interpreter
=================================
A Python implementation of Microsoft BASIC 2.0 with Commodore 64 dialect.
Supports: PRINT, LET, GOTO, IF/THEN, FOR/NEXT, GOSUB/RETURN, DATA/READ,
enhanced arithmetic expressions, and proper C64 BASIC V2 syntax.
"""

import colorama
import math
import random
import re
import sys
from typing import List, Dict, Any, Optional

colorama.init(strip=False)

SCREEN_BASE = 1024  # $0400 in decimal - screen RAM
SCREEN_COLS = 40
SCREEN_ROWS = 25
SCREEN_SIZE = SCREEN_COLS * SCREEN_ROWS  # 1000 bytes
COLOR_BASE = 55296  # $D800 in decimal - color RAM

USE_COLORS = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False


class VirtualScreen:
    """Simulates C64 screen memory for PEEK/POKE"""

    def __init__(self):
        self.screen_memory = [32] * SCREEN_SIZE  # Character codes (spaces)
        self.color_memory = [1] * SCREEN_SIZE  # Color codes (default white)
        self.cursor_x = 0
        self.cursor_y = 0

    def poke(self, addr: int, value: int) -> bool:
        """POKE to screen or color RAM. Returns True if handled."""
        if SCREEN_BASE <= addr < SCREEN_BASE + SCREEN_SIZE:
            self.screen_memory[addr - SCREEN_BASE] = value & 0xFF
            return True
        elif COLOR_BASE <= addr < COLOR_BASE + SCREEN_SIZE:
            self.color_memory[addr - COLOR_BASE] = value & 0xF
            return True
        return False

    def peek(self, addr: int) -> int:
        """PEEK from screen or color RAM. Returns -1 if not screen memory."""
        if SCREEN_BASE <= addr < SCREEN_BASE + SCREEN_SIZE:
            return self.screen_memory[addr - SCREEN_BASE]
        elif COLOR_BASE <= addr < COLOR_BASE + SCREEN_SIZE:
            return self.color_memory[addr - COLOR_BASE]
        return -1

    def clear(self):
        """Clear the screen (fill with spaces/petdog)"""
        for i in range(SCREEN_SIZE):
            self.screen_memory[i] = 32  # Space character
        self.cursor_x = 0
        self.cursor_y = 0

    def cursor_down(self):
        """Move cursor down one row"""
        if self.cursor_y < SCREEN_ROWS - 1:
            self.cursor_y += 1

    def cursor_up(self):
        """Move cursor up one row"""
        if self.cursor_y > 0:
            self.cursor_y -= 1

    def cursor_right(self):
        """Move cursor right one column"""
        if self.cursor_x < SCREEN_COLS - 1:
            self.cursor_x += 1

    def cursor_left(self):
        """Move cursor left one column"""
        if self.cursor_x > 0:
            self.cursor_x -= 1

    def home(self):
        """Move cursor to home position"""
        self.cursor_x = 0
        self.cursor_y = 0


class BasicInterpreter:
    def __init__(self, prompt_func=None):
        self.variables: Dict[str, Any] = {}
        self.program: Dict[int, List[str]] = {}
        self.current_line: Optional[int] = None
        self.data_section: List[str] = []
        self.data_index: int = 0
        self.call_stack: List[int] = []
        self.line_execution_order: List[int] = []
        self.for_loops: Dict[str, Dict[str, Any]] = {}
        self.for_loop_returns: Dict[str, int] = {}
        self.input_buffer: List[str] = []
        self.prompt_func = prompt_func or (lambda: input())
        self.memory: Dict[int, int] = {}
        self.screen = VirtualScreen()

    def tokenize(self, line: str):
        """Convert BASIC line into tokens"""
        match = re.match(r"^\s*(\d+)\s*(.*)", line)
        if not match:
            return None, []

        line_num = int(match.group(1))
        code = match.group(2).strip()

        tokens = []
        current_token = ""
        in_string = False

        i = 0
        while i < len(code):
            char = code[i]

            if char == '"' and not in_string:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                in_string = True
                current_token += char
            elif char == '"' and in_string:
                current_token += char
                tokens.append(current_token)
                current_token = ""
                in_string = False
            elif char in "()+-*/=<>," and not in_string:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""

                if i + 1 < len(code):
                    two_char_op = char + code[i + 1]
                    if two_char_op in ["<=", ">=", "<>"]:
                        tokens.append(two_char_op)
                        i += 1
                    else:
                        tokens.append(char)
                else:
                    tokens.append(char)
            elif char in ";" and not in_string:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(char)
            elif char.isspace() and not in_string:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char

            i += 1

        if current_token:
            tokens.append(current_token)

        return line_num, tokens

    def evaluate_expression(self, tokens: List[str]) -> Any:
        """Evaluate mathematical expressions with operator precedence"""
        if not tokens:
            return ""

        func_name = tokens[0].upper() if tokens else ""

        # Handle INKEY$ (read single key without Enter) - must check before single-token fallback
        if func_name == "INKEY$":
            if self.input_buffer:
                key = self.input_buffer.pop(0)
                if key:
                    print(key)
                return key
            else:
                import sys
                import termios

                if sys.stdin.isatty():
                    old_settings = termios.tcgetattr(sys.stdin)
                    try:
                        termios.tcflush(sys.stdin, termios.TCIFLUSH)
                        ch = sys.stdin.read(1)
                        if ch:
                            print(ch)
                        return ch if ch else ""
                    except OSError:
                        return ""
                    finally:
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                else:
                    try:
                        ch = sys.stdin.read(1)
                        return ch if ch else ""
                    except OSError:
                        return ""

        if (
            len(tokens) >= 4
            and func_name == "PEEK"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            addr_tokens = tokens[2:-1]
            addr = int(self.evaluate_expression(addr_tokens))
            screen_val = self.screen.peek(addr)
            if screen_val >= 0:
                return screen_val
            return self.memory.get(addr, 0)

        if (
            len(tokens) >= 4
            and func_name == "ABS"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = float(self.evaluate_expression(tokens[2:-1]))
            return abs(val)

        if (
            len(tokens) >= 4
            and func_name == "SQR"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = float(self.evaluate_expression(tokens[2:-1]))
            return val**0.5

        if (
            len(tokens) >= 4
            and func_name == "INT"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = float(self.evaluate_expression(tokens[2:-1]))
            return int(val)

        if (
            len(tokens) >= 4
            and func_name == "SGN"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = float(self.evaluate_expression(tokens[2:-1]))
            if val > 0:
                return 1
            elif val < 0:
                return -1
            else:
                return 0

        if (
            len(tokens) >= 4
            and func_name == "RND"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = int(self.evaluate_expression(tokens[2:-1]))
            if val == 0:
                return random.random()
            elif val > 0:
                return int(val * random.random()) + 1
            else:
                return int(val * random.random()) - 1

        if (
            len(tokens) >= 4
            and func_name == "SIN"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = float(self.evaluate_expression(tokens[2:-1]))
            return math.sin(val)

        if (
            len(tokens) >= 4
            and func_name == "COS"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = float(self.evaluate_expression(tokens[2:-1]))
            return math.cos(val)

        if (
            len(tokens) >= 4
            and func_name == "TAN"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = float(self.evaluate_expression(tokens[2:-1]))
            return math.tan(val)

        if (
            len(tokens) >= 4
            and func_name == "ATN"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = float(self.evaluate_expression(tokens[2:-1]))
            return math.atan(val)

        if (
            len(tokens) >= 4
            and func_name == "EXP"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = float(self.evaluate_expression(tokens[2:-1]))
            return math.exp(val)

        if (
            len(tokens) >= 4
            and func_name == "LOG"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = float(self.evaluate_expression(tokens[2:-1]))
            return math.log(val)

        if (
            len(tokens) >= 4
            and func_name == "LEFT$"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            inner = tokens[2:-1]
            comma_idx = None
            for i, t in enumerate(inner):
                if t == ",":
                    comma_idx = i
                    break
            if comma_idx is not None:
                str_val = str(self.evaluate_expression(inner[:comma_idx]))
                length = int(self.evaluate_expression(inner[comma_idx + 1 :]))
                return str_val[:length]
            return ""

        if (
            len(tokens) >= 4
            and func_name == "RIGHT$"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            inner = tokens[2:-1]
            comma_idx = None
            for i, t in enumerate(inner):
                if t == ",":
                    comma_idx = i
                    break
            if comma_idx is not None:
                str_val = str(self.evaluate_expression(inner[:comma_idx]))
                length = int(self.evaluate_expression(inner[comma_idx + 1 :]))
                return str_val[-length:] if length <= len(str_val) else str_val
            return ""

        if (
            len(tokens) >= 4
            and func_name == "MID$"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            inner = tokens[2:-1]
            commas = []
            for i, t in enumerate(inner):
                if t == ",":
                    commas.append(i)
            if len(commas) >= 1:
                str_val = str(self.evaluate_expression(inner[: commas[0]]))
                start = int(
                    self.evaluate_expression(
                        inner[commas[0] + 1 : commas[1] if len(commas) > 1 else None]
                    )
                )
                if len(commas) > 1:
                    length = int(self.evaluate_expression(inner[commas[1] + 1 :]))
                    return str_val[start - 1 : start - 1 + length]
                else:
                    return str_val[start - 1 :]
            return ""

        if (
            len(tokens) >= 4
            and func_name == "LEN"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            str_val = str(self.evaluate_expression(tokens[2:-1]))
            return len(str_val)

        if (
            len(tokens) >= 4
            and func_name == "VAL"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            str_val = str(self.evaluate_expression(tokens[2:-1]))
            try:
                if "." in str_val:
                    return float(str_val)
                return int(str_val)
            except ValueError:
                return 0

        if (
            len(tokens) >= 4
            and func_name == "STR$"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = self.evaluate_expression(tokens[2:-1])
            return str(val)

        if (
            len(tokens) >= 4
            and func_name == "CHR$"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            val = int(self.evaluate_expression(tokens[2:-1]))
            chr_val = val % 256

            if chr_val == 147:  # Clear screen / Home cursor
                self.screen.clear()
                return ""
            elif chr_val == 17:  # Cursor down
                self.screen.cursor_down()
                return ""
            elif chr_val == 145:  # Cursor up
                self.screen.cursor_up()
                return ""
            elif chr_val == 29:  # Cursor right
                self.screen.cursor_right()
                return ""
            elif chr_val == 157:  # Cursor left
                self.screen.cursor_left()
                return ""
            elif chr_val == 19:  # Home cursor
                self.screen.home()
                return ""
            elif chr_val == 18:  # Reverse on
                return ""
            elif chr_val == 146:  # Reverse off
                return ""
            else:
                return chr(chr_val)

        # Handle SCREEN$ (read character from screen memory)
        if (
            len(tokens) >= 4
            and func_name == "SCREEN$"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            inner = tokens[2:-1]
            if len(inner) >= 3:
                row = int(self.evaluate_expression([inner[0]]))
                col = int(self.evaluate_expression([inner[2]]))
                if 0 <= row < SCREEN_ROWS and 0 <= col < SCREEN_COLS:
                    addr = SCREEN_BASE + row * SCREEN_COLS + col
                    char_code = self.screen.peek(addr)
                    if char_code >= 0:
                        return chr(char_code)
            return " "

        if (
            len(tokens) >= 4
            and func_name == "ASC"
            and tokens[1] == "("
            and tokens[-1] == ")"
        ):
            str_val = str(self.evaluate_expression(tokens[2:-1]))
            return ord(str_val[0]) if str_val else 0

        if len(tokens) == 3 and tokens[1] == "+":
            left = self.evaluate_expression([tokens[0]])
            right = self.evaluate_expression([tokens[2]])
            if isinstance(left, str) and isinstance(right, str):
                return left + right

        if len(tokens) == 1:
            token = tokens[0]
            if token.startswith('"') and token.endswith('"'):
                return token[1:-1]
            elif token.upper() in self.variables:
                return self.variables[token.upper()]
            elif token.replace(".", "").replace("-", "").isdigit():
                return float(token) if "." in token else int(token)
            else:
                return token

        try:
            values = []
            for token in tokens:
                if token.startswith('"') and token.endswith('"'):
                    values.append(f'"{token[1:-1]}"')
                elif token.upper() in self.variables:
                    val = self.variables[token.upper()]
                    if isinstance(val, str):
                        values.append(f'"{val}"')
                    else:
                        values.append(str(val))
                elif token.replace(".", "").replace("-", "").isdigit():
                    values.append(token)
                else:
                    values.append(token)

            expr_str = " ".join(values)
            expr_str = expr_str.replace(" AND ", " and ").replace(" OR ", " or ")
            expr_str = expr_str.replace(" XOR ", " ^ ")
            expr_str = expr_str.replace(" MOD ", " % ")

            peek_pattern = r"PEEK\s*\(\s*(\d+)\s*\)"

            def replace_peek(match):
                addr = int(match.group(1))
                return str(self.memory.get(addr, 0))

            expr_str = re.sub(peek_pattern, replace_peek, expr_str)

            result = eval(expr_str)
            return result

        except (ValueError, NameError, SyntaxError):
            token = tokens[0]
            if token.startswith('"') and token.endswith('"'):
                return token[1:-1]
            elif token in self.variables:
                return self.variables[token]
            elif token.replace(".", "").replace("-", "").isdigit():
                return float(token) if "." in token else int(token)
            else:
                return token

    def parse_and_execute(self, line_num: int, tokens: List[str]):
        """Parse and execute a single BASIC line"""
        if not tokens:
            return

        command = tokens[0].upper()

        if command == "PRINT" or command == "?":
            self.handle_print(tokens[1:])
        elif command == "LET":
            self.handle_let(tokens[1:])
        elif command == "GOTO":
            return self.handle_goto(tokens)
        elif command == "GOSUB":
            return self.handle_gosub(tokens)
        elif command == "RETURN":
            return self.handle_return()
        elif command == "IF":
            return self.handle_if(tokens[1:])
        elif command == "FOR":
            return self.handle_for(tokens[1:])
        elif command == "NEXT":
            return self.handle_next(tokens[1:])
        elif command == "END":
            return "END_PROGRAM"
        elif command == "REM":
            pass
        elif command == "DATA":
            self.handle_data(tokens[1:])
        elif command == "READ":
            self.handle_read(tokens[1:])
        elif command == "INPUT":
            self.handle_input(tokens[1:])
        elif command == "GET":
            self.handle_get(tokens[1:])
        elif command == "POKE":
            self.handle_poke(tokens[1:])
        elif command == "STOP":
            return "END_PROGRAM"
        elif command == "RESTORE":
            self.data_index = 0
        elif command == "CLEAR":
            self.variables.clear()
            self.memory.clear()
        elif command == "CLR":
            self.variables.clear()
        elif command == "SCREEN":
            self.handle_screen()
        else:
            self.handle_assignment(tokens)

    def handle_print(self, tokens: List[str]):
        """Handle PRINT statement with Commodore 64 syntax"""
        if not tokens:
            print()
            return

        output = []

        suppress_newline = tokens and tokens[-1] == ";"
        if suppress_newline:
            tokens = tokens[:-1]

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token == ",":
                output.append("\t")
                i += 1
                continue
            elif token == ";":
                i += 1
                continue

            group_tokens = []
            while i < len(tokens) and tokens[i] not in [",", ";"]:
                group_tokens.append(tokens[i])
                i += 1

            if group_tokens:
                result = self.evaluate_expression(group_tokens)
                output.append(str(result))

        print("".join(output), end="" if suppress_newline else "\n", flush=True)

    def handle_let(self, tokens: List[str]):
        """Handle LET statement"""
        equals_index = None
        for i, token in enumerate(tokens):
            if token == "=":
                equals_index = i
                break

        if equals_index is not None and equals_index >= 1:
            var_name = tokens[0]
            value = self.evaluate_expression(tokens[equals_index + 1 :])
            self.variables[var_name] = value

    def handle_assignment(self, tokens: List[str]):
        """Handle direct assignment like 'X = 5'"""
        if len(tokens) >= 3 and tokens[1] == "=":
            var_name = tokens[0]
            value = self.evaluate_expression(tokens[2:])
            self.variables[var_name] = value

    def handle_goto(self, tokens: List[str]):
        """Handle GOTO statement"""
        if len(tokens) >= 2 and tokens[1].isdigit():
            target_line = int(tokens[1])
            self.current_line = target_line
            return target_line
        return None

    def handle_gosub(self, tokens: List[str]):
        """Handle GOSUB statement"""
        if len(tokens) >= 2 and tokens[1].isdigit():
            target_line = int(tokens[1])
            if self.current_line is not None:
                current_index = self.line_execution_order.index(self.current_line)
                return_line = (
                    self.line_execution_order[current_index + 1]
                    if current_index + 1 < len(self.line_execution_order)
                    else None
                )
            else:
                return_line = None
            if return_line is not None:
                self.call_stack.append(return_line)
            self.current_line = target_line
            return target_line
        return None

    def handle_return(self):
        """Handle RETURN statement"""
        if self.call_stack:
            return_line = self.call_stack.pop()
            if return_line:
                self.current_line = return_line
                return return_line
        return None

    def handle_if(self, tokens: List[str]):
        """Handle IF statement with THEN"""
        then_index = None
        for i, token in enumerate(tokens):
            if token.upper() == "THEN":
                then_index = i
                break

        if then_index is not None:
            condition_tokens = tokens[:then_index]
            then_tokens = tokens[then_index + 1 :]

            condition_result = self.evaluate_condition(condition_tokens)

            if condition_result:
                if then_tokens:
                    if len(then_tokens) >= 2 and then_tokens[0].upper() == "GOTO":
                        if then_tokens[1].isdigit():
                            target_line = int(then_tokens[1])
                            self.current_line = target_line
                            return target_line
                    else:
                        line_num = (
                            self.current_line if self.current_line is not None else 0
                        )
                        result = self.parse_and_execute(line_num, then_tokens)
                        return result
        return None

    def evaluate_condition(self, tokens: List[str]) -> bool:
        """Evaluate IF condition"""
        if len(tokens) >= 3:
            left = self.evaluate_expression([tokens[0]])
            operator = tokens[1]
            right = self.evaluate_expression([tokens[2]])

            try:
                left_num = float(left)
                right_num = float(right)

                if operator == "=":
                    return left_num == right_num
                elif operator == "<":
                    return left_num < right_num
                elif operator == ">":
                    return left_num > right_num
                elif operator == "<=":
                    return left_num <= right_num
                elif operator == ">=":
                    return left_num >= right_num
                elif operator == "<>":
                    return left_num != right_num
            except (TypeError, ValueError):
                if operator == "=":
                    return str(left) == str(right)
                elif operator == "<>":
                    return str(left) != str(right)
        return False

    def handle_for(self, tokens: List[str]):
        """Handle FOR statement"""
        if len(tokens) >= 5 and tokens[1] == "=" and tokens[3].upper() == "TO":
            var_name = tokens[0].upper()  # Normalize to uppercase
            start_value = int(self.evaluate_expression([tokens[2]]))
            end_value = int(self.evaluate_expression([tokens[4]]))

            if var_name not in self.for_loops:
                self.variables[var_name] = start_value

            self.for_loops[var_name] = {
                "line": self.current_line,
                "end": end_value,
                "start": start_value,
            }

            try:
                if self.current_line is not None:
                    current_index = self.line_execution_order.index(self.current_line)
                    if current_index + 1 < len(self.line_execution_order):
                        self.for_loop_returns[var_name] = self.line_execution_order[
                            current_index + 1
                        ]
            except ValueError:
                pass
        else:
            print(f"?SYNTAX ERROR IN {self.current_line}")

    def handle_next(self, tokens: List[str]):
        """Handle NEXT statement"""
        if tokens:
            var_name = tokens[0].upper()  # Normalize to uppercase
            if var_name in self.for_loops:
                loop_info = self.for_loops[var_name]
                current_value = self.variables.get(var_name, 0)
                new_value = current_value + 1

                if new_value <= loop_info["end"]:
                    self.variables[var_name] = new_value
                    return_line = self.for_loop_returns.get(
                        var_name, loop_info["line"] + 10
                    )
                    self.current_line = return_line
                    return return_line
                else:
                    del self.for_loops[var_name]
                    if var_name in self.for_loop_returns:
                        del self.for_loop_returns[var_name]
        return None

    def handle_data(self, tokens: List[str]):
        """Handle DATA statement"""
        for token in tokens:
            if token == ",":
                continue
            if token.startswith('"') and token.endswith('"'):
                self.data_section.append(token[1:-1])
            else:
                self.data_section.append(token)

    def handle_read(self, tokens: List[str]):
        """Handle READ statement"""
        if not tokens:
            return

        var_names = []
        for token in tokens:
            if token != ",":
                var_names.append(token)

        for var_name in var_names:
            if self.data_index < len(self.data_section):
                value = self.data_section[self.data_index]
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass

                self.variables[var_name] = value
                self.data_index += 1

    def handle_input(self, tokens: List[str]):
        """Handle INPUT statement"""
        if not tokens:
            return

        prompt = "? "
        var_names = []

        i = 0
        while i < len(tokens):
            if tokens[i].startswith('"') and tokens[i].endswith('"'):
                prompt = tokens[i][1:-1] + " "
                i += 1
                if i < len(tokens) and tokens[i] == ";":
                    i += 1
                break
            else:
                break

        for j in range(i, len(tokens)):
            if tokens[j] not in [";", ","]:
                var_names.append(tokens[j])

        for var_name in var_names:
            print(prompt, end="", flush=True)
            try:
                if self.input_buffer:
                    user_input = self.input_buffer.pop(0)
                    print(user_input)
                else:
                    user_input = self.prompt_func()
                try:
                    value = int(user_input)
                except ValueError:
                    try:
                        value = float(user_input)
                    except ValueError:
                        value = user_input
                self.variables[var_name] = value
            except EOFError:
                print()
                break

    def handle_get(self, tokens: List[str]):
        """Handle GET statement - read single keypress"""
        if not tokens:
            return

        var_name = tokens[0]

        if self.input_buffer:
            key = self.input_buffer.pop(0)
            print(key)
            self.variables[var_name] = key
        else:
            try:
                import sys
                import termios

                if not sys.stdin.isatty():
                    self.variables[var_name] = ""
                    return

                old_settings = termios.tcgetattr(sys.stdin)
                try:
                    new_settings = termios.tcgetattr(sys.stdin)
                    new_settings[3] = new_settings[3] & ~(termios.ICANON | termios.ECHO)
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)
                    termios.tcflush(sys.stdin, termios.TCIFLUSH)
                    ch = sys.stdin.read(1)
                    if ch:
                        print(ch)
                        self.variables[var_name] = ch
                    else:
                        self.variables[var_name] = ""
                except OSError:
                    self.variables[var_name] = ""
                finally:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except (ImportError, OSError):
                self.variables[var_name] = ""

    def handle_screen(self):
        """Display the virtual screen with ANSI colors (or plain text if no TTY)"""
        C64_TO_FOREGROUND = {
            0: colorama.Fore.BLACK,
            1: colorama.Fore.WHITE,
            2: colorama.Fore.RED,
            3: colorama.Fore.CYAN,
            4: colorama.Fore.MAGENTA,
            5: colorama.Fore.GREEN,
            6: colorama.Fore.BLUE,
            7: colorama.Fore.YELLOW,
            8: colorama.Fore.YELLOW,  # orange -> yellow
            9: colorama.Fore.LIGHTYELLOW_EX,  # brown -> bright yellow
            10: colorama.Fore.LIGHTRED_EX,  # light red -> red
            11: colorama.Fore.LIGHTBLACK_EX,  # dark gray -> bright black
            12: colorama.Fore.WHITE,  # gray 2 -> white
            13: colorama.Fore.LIGHTGREEN_EX,  # light green -> bright green
            14: colorama.Fore.LIGHTBLUE_EX,  # light blue -> bright blue
            15: colorama.Fore.WHITE,  # gray 3 -> white
        }

        if USE_COLORS:
            print(colorama.ansi.clear_screen() + colorama.ansi.Cursor.POS(0, 0), end="")
        else:
            print("\n" * SCREEN_ROWS + colorama.ansi.Cursor.POS(0, 0), end="")

        for row in range(SCREEN_ROWS):
            line_parts = []
            current_color = 1
            run_chars = []

            for col in range(SCREEN_COLS):
                addr = SCREEN_BASE + row * SCREEN_COLS + col
                char_code = self.screen.peek(addr)
                color_addr = COLOR_BASE + row * SCREEN_COLS + col
                color_code = self.screen.peek(color_addr)

                if char_code < 0:
                    char_code = 32
                if color_code < 0:
                    color_code = 1

                char = chr(char_code) if 32 <= char_code <= 126 else " "

                if USE_COLORS and color_code != current_color:
                    if run_chars:
                        color = C64_TO_FOREGROUND.get(
                            current_color, colorama.Fore.WHITE
                        )
                        line_parts.append(color + "".join(run_chars))
                        run_chars = []
                    current_color = color_code

                run_chars.append(char)

            if run_chars:
                if USE_COLORS:
                    color = C64_TO_FOREGROUND.get(current_color, colorama.Fore.WHITE)
                    line_parts.append(color + "".join(run_chars))
                else:
                    line_parts.append("".join(run_chars))

            output = "".join(line_parts)
            if USE_COLORS:
                output += colorama.Style.RESET_ALL
            print(output)

    def handle_peek(self, tokens: List[str]):
        """Handle PEEK function - checks screen memory first, then general memory"""
        if tokens:
            addr = int(self.evaluate_expression(tokens))
            screen_val = self.screen.peek(addr)
            if screen_val >= 0:
                return screen_val
            return self.memory.get(addr, 0)
        return 0

    def handle_poke(self, tokens: List[str]):
        """Handle POKE statement - tries screen memory first, then general memory"""
        if len(tokens) >= 3:
            try:
                comma_idx = tokens.index(",")
                # Check if tokens start with 'POKE'
                if tokens[0].upper() == "POKE" and comma_idx > 1:
                    addr_tokens = tokens[1:comma_idx]
                else:
                    addr_tokens = tokens[:comma_idx]
                value_tokens = tokens[comma_idx + 1 :]
                addr = int(self.evaluate_expression(addr_tokens))
                value = int(self.evaluate_expression(value_tokens))
            except (ValueError, IndexError):
                addr = 0
                value = 0
            value = max(0, min(255, value))

            if not self.screen.poke(addr, value):
                self.memory[addr] = value

    def run_program(self, source_code: str):
        """Parse and run the BASIC program"""
        lines = source_code.strip().split("\n")

        self.for_loops = {}
        self.for_loop_returns = {}
        self.data_section = []
        self.data_index = 0

        for line in lines:
            if line.strip():
                line_num, tokens = self.tokenize(line)
                if line_num is not None:
                    self.program[line_num] = tokens
                    if tokens and tokens[0].upper() == "DATA":
                        self.handle_data(tokens[1:])
                    elif tokens and tokens[0].upper() != "REM":
                        self.line_execution_order.append(line_num)

        self.current_line = None

        while True:
            if self.current_line is None:
                if not self.line_execution_order:
                    break
                self.current_line = self.line_execution_order[0]

            if self.current_line not in self.program:
                break

            tokens = self.program[self.current_line]
            result = self.parse_and_execute(self.current_line, tokens)

            if result == "END_PROGRAM":
                break

            if result is not None:
                # Control flow change (GOTO, GOSUB, FOR/NEXT loop)
                self.current_line = result
                continue

            try:
                current_index = self.line_execution_order.index(self.current_line)
                if current_index + 1 < len(self.line_execution_order):
                    self.current_line = self.line_execution_order[current_index + 1]
                else:
                    break
            except ValueError:
                if self.current_line is not None:
                    next_lines = [
                        ln for ln in self.line_execution_order if ln > self.current_line
                    ]
                    if next_lines:
                        self.current_line = min(next_lines)
                        continue
                break


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
