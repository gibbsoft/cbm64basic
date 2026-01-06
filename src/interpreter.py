"""
C64 BASIC Interpreter
=====================
The core BASIC interpreter class implementing Commodore 64 BASIC V2.
"""

import random
import re
from typing import List, Dict, Any, Optional

from src.screen import VirtualScreen
from src.functions import evaluate_function, FUNCTION_HANDLERS
from src.commands import (
    handle_print,
    handle_let,
    handle_assignment,
    handle_goto,
    handle_gosub,
    handle_return,
    handle_if,
    handle_for,
    handle_next,
    handle_data,
    handle_read,
    handle_input,
    handle_get,
    handle_poke,
    handle_screen,
    FKEY_SEQUENCES,
)


class BasicInterpreter:
    # Expose FKEY_SEQUENCES as class attribute for tests
    FKEY_SEQUENCES = FKEY_SEQUENCES

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
        self.screen = VirtualScreen(interpreter=self)

    def tokenize(self, line: str):
        """Convert BASIC line into tokens.

        All tokens are normalized to uppercase EXCEPT string literals,
        which preserve their original case.
        """
        match = re.match(r"^\s*(\d+)\s*(.*)", line)
        if not match:
            return None, []

        line_num = int(match.group(1))
        code = match.group(2).strip()

        tokens = []
        current_token = ""
        in_string = False

        def add_token(token, is_string=False):
            if token:
                tokens.append(token if is_string else token.upper())

        i = 0
        while i < len(code):
            char = code[i]

            if char == '"' and not in_string:
                if current_token:
                    add_token(current_token)
                    current_token = ""
                in_string = True
                current_token += char
            elif char == '"' and in_string:
                current_token += char
                add_token(current_token, is_string=True)
                current_token = ""
                in_string = False
            elif char in "()+-*/=<>," and not in_string:
                if current_token:
                    add_token(current_token)
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
            elif char == ";" and not in_string:
                if current_token:
                    add_token(current_token)
                    current_token = ""
                tokens.append(char)
            elif char.isspace() and not in_string:
                if current_token:
                    add_token(current_token)
                    current_token = ""
            else:
                current_token += char
            i += 1

        if current_token:
            add_token(current_token)

        return line_num, tokens

    def evaluate_expression(self, tokens: List[str]) -> Any:
        """Evaluate mathematical expressions with operator precedence."""
        if not tokens:
            return ""

        # Try function evaluation first
        handled, result = evaluate_function(self, tokens)
        if handled:
            return result

        # Simple string concatenation
        if len(tokens) == 3 and tokens[1] == "+":
            left = self.evaluate_expression([tokens[0]])
            right = self.evaluate_expression([tokens[2]])
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            elif isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right

        # Single token evaluation
        if len(tokens) == 1:
            token = tokens[0]
            if token.startswith('"') and token.endswith('"'):
                return token[1:-1]
            elif token in self.variables:
                return self.variables[token]
            elif token.replace(".", "").replace("-", "").isdigit():
                return float(token) if "." in token else int(token)
            else:
                return 0

        # Complex expression - build and eval
        try:
            values = []
            for token in tokens:
                if token.startswith('"') and token.endswith('"'):
                    values.append(f'"{token[1:-1]}"')
                elif token in self.variables:
                    val = self.variables[token]
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
            expr_str = expr_str.replace(" XOR ", " ^ ").replace(" MOD ", " % ")

            # Replace PEEK calls
            def replace_peek(match):
                return str(self.memory.get(int(match.group(1)), 0))

            expr_str = re.sub(r"PEEK\s*\(\s*(\d+)\s*\)", replace_peek, expr_str)

            # Replace RND calls
            def replace_rnd(match):
                arg = match.group(1).strip()
                if arg == "0":
                    random.seed(0)
                return str(random.random())

            expr_str = re.sub(
                r"RND\s*\(\s*([^\)]*)\s*\)", replace_rnd, expr_str, flags=re.IGNORECASE
            )

            return eval(expr_str)

        except (ValueError, NameError, SyntaxError):
            token = tokens[0]
            if token.startswith('"') and token.endswith('"'):
                return token[1:-1]
            elif token in self.variables:
                return self.variables[token]
            elif token.replace(".", "").replace("-", "").isdigit():
                return float(token) if "." in token else int(token)
            return 0

    def evaluate_condition(self, tokens: List[str]) -> bool:
        """Evaluate IF condition."""
        if len(tokens) < 3:
            return False

        comparison_ops = ["<>", "<=", ">=", "=", "<", ">"]
        op_index = -1
        operator = None
        paren_depth = 0

        for i, token in enumerate(tokens):
            if token == "(":
                paren_depth += 1
            elif token == ")":
                paren_depth -= 1
            elif paren_depth == 0 and token in comparison_ops:
                op_index = i
                operator = token
                break

        if op_index == -1:
            return False

        left_tokens = tokens[:op_index]
        right_tokens = tokens[op_index + 1 :]

        if not left_tokens or not right_tokens:
            return False

        left = self.evaluate_expression(left_tokens)
        right = self.evaluate_expression(right_tokens)

        try:
            left_num, right_num = float(left), float(right)
            match operator:
                case "=":
                    return left_num == right_num
                case "<":
                    return left_num < right_num
                case ">":
                    return left_num > right_num
                case "<=":
                    return left_num <= right_num
                case ">=":
                    return left_num >= right_num
                case "<>":
                    return left_num != right_num
        except (TypeError, ValueError):
            if operator == "=":
                return str(left) == str(right)
            elif operator == "<>":
                return str(left) != str(right)
        return False

    def parse_and_execute(self, line_num: int, tokens: List[str]):
        """Parse and execute a single BASIC line."""
        if not tokens:
            return

        # Handle multi-statement lines (separated by :)
        if ":" in tokens:
            statement_parts = []
            current_statement = []
            for token in tokens:
                if token == ":":
                    if current_statement:
                        statement_parts.append(current_statement)
                    current_statement = []
                else:
                    current_statement.append(token)
            if current_statement:
                statement_parts.append(current_statement)

            stmt_idx = 0
            for_start_idx = {}
            for_stack = []

            while stmt_idx < len(statement_parts):
                statement_tokens = statement_parts[stmt_idx]
                if not statement_tokens:
                    stmt_idx += 1
                    continue

                cmd = statement_tokens[0]

                if cmd == "FOR" and len(statement_tokens) >= 2:
                    var_name = statement_tokens[1]
                    for_start_idx[var_name] = stmt_idx + 1
                    for_stack.append(var_name)

                    if var_name in self.for_loops and self.for_loops[var_name].get(
                        "same_line_body"
                    ):
                        stmt_idx = for_start_idx[var_name]
                        continue

                    if stmt_idx + 1 < len(statement_parts):
                        result = self._execute_statement(line_num, statement_tokens)
                        if var_name in self.for_loops:
                            self.for_loops[var_name]["same_line_body"] = True
                            self.for_loops[var_name]["body_start_idx"] = stmt_idx + 1
                        if result is not None and result != "END_PROGRAM":
                            return result
                        stmt_idx += 1
                        continue

                if cmd == "NEXT":
                    if len(statement_tokens) > 1:
                        next_var = statement_tokens[1]
                    elif for_stack:
                        next_var = for_stack[-1]
                    else:
                        next_var = None

                    if (
                        next_var
                        and next_var in self.for_loops
                        and next_var in for_start_idx
                    ):
                        loop_info = self.for_loops[next_var]
                        current_value = self.variables.get(next_var, 0)
                        new_value = current_value + 1

                        if new_value <= loop_info["end"]:
                            self.variables[next_var] = new_value
                            stmt_idx = for_start_idx[next_var]
                            continue
                        else:
                            del self.for_loops[next_var]
                            if next_var in self.for_loop_returns:
                                del self.for_loop_returns[next_var]
                            if next_var in for_stack:
                                for_stack.remove(next_var)
                            stmt_idx += 1
                            continue

                result = self._execute_statement(line_num, statement_tokens)
                if result is not None and result != "END_PROGRAM":
                    return result
                stmt_idx += 1
            return

        return self._execute_statement(line_num, tokens)

    def _execute_statement(self, line_num: int, tokens: List[str]):
        """Execute a single statement."""
        if not tokens:
            return

        command = tokens[0]

        # Command dispatch using match/case
        match command:
            case "PRINT" | "?":
                handle_print(self, tokens[1:])
            case "LET":
                handle_let(self, tokens[1:])
            case "GOTO":
                return handle_goto(self, tokens)
            case "GOSUB":
                return handle_gosub(self, tokens)
            case "RETURN":
                return handle_return(self, tokens)
            case "IF":
                return handle_if(self, tokens[1:])
            case "FOR":
                handle_for(self, tokens[1:])
            case "NEXT":
                return handle_next(self, tokens[1:])
            case "END" | "STOP":
                return "END_PROGRAM"
            case "REM":
                pass
            case "DATA":
                handle_data(self, tokens[1:])
            case "READ":
                handle_read(self, tokens[1:])
            case "INPUT":
                handle_input(self, tokens[1:])
            case "GET":
                handle_get(self, tokens[1:])
            case "POKE":
                handle_poke(self, tokens[1:])
            case "RESTORE":
                self.data_index = 0
            case "CLEAR":
                self.variables.clear()
                self.memory.clear()
            case "CLR":
                self.variables.clear()
            case "SCREEN":
                handle_screen(self, tokens[1:])
            case _:
                if tokens[0].isdigit() or (len(tokens) >= 2 and tokens[1] == "="):
                    handle_assignment(self, tokens)
                else:
                    raise SyntaxError(f"Unknown command: {command}")

    def run_program(self, source_code: str):
        """Parse and run the BASIC program."""
        lines = source_code.strip().split("\n")

        self.variables = {}
        self.for_loops = {}
        self.for_loop_returns = {}
        self.data_section = []
        self.data_index = 0
        self.program = {}
        self.line_execution_order = []

        for line in lines:
            if line.strip():
                line_num, tokens = self.tokenize(line)
                if line_num is not None:
                    self.program[line_num] = tokens
                    if tokens and tokens[0] == "DATA":
                        handle_data(self, tokens[1:])
                    elif tokens and tokens[0] != "REM":
                        self.line_execution_order.append(line_num)

        self.line_execution_order.sort()
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
