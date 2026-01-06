"""
C64 BASIC Functions
===================
Implementation of BASIC built-in functions (ABS, SQR, CHR$, etc.)
"""

import math
import random
import sys
from typing import Any, List, TYPE_CHECKING

from src.constants import SCREEN_BASE, SCREEN_COLS, SCREEN_ROWS

if TYPE_CHECKING:
    from src.interpreter import BasicInterpreter


def eval_inkey(interpreter: "BasicInterpreter") -> str:
    """Handle INKEY$ - read single key without Enter."""
    if interpreter.input_buffer:
        key = interpreter.input_buffer.pop(0)
        if key:
            print(key)
        return key
    else:
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


def eval_peek(interpreter: "BasicInterpreter", tokens: List[str]) -> int:
    """Handle PEEK function - checks screen memory first, then general memory."""
    addr_tokens = tokens[2:-1]
    addr = int(interpreter.evaluate_expression(addr_tokens))
    screen_val = interpreter.screen.peek(addr)
    if screen_val >= 0:
        return screen_val
    return interpreter.memory.get(addr, 0)


def eval_abs(interpreter: "BasicInterpreter", tokens: List[str]) -> float:
    """Handle ABS function."""
    val = float(interpreter.evaluate_expression(tokens[2:-1]))
    return abs(val)


def eval_sqr(interpreter: "BasicInterpreter", tokens: List[str]) -> float:
    """Handle SQR (square root) function."""
    val = float(interpreter.evaluate_expression(tokens[2:-1]))
    return val**0.5


def eval_int(interpreter: "BasicInterpreter", tokens: List[str]) -> int:
    """Handle INT function."""
    val = float(interpreter.evaluate_expression(tokens[2:-1]))
    return int(val)


def eval_sgn(interpreter: "BasicInterpreter", tokens: List[str]) -> int:
    """Handle SGN (sign) function."""
    val = float(interpreter.evaluate_expression(tokens[2:-1]))
    if val > 0:
        return 1
    elif val < 0:
        return -1
    else:
        return 0


def eval_rnd(interpreter: "BasicInterpreter", tokens: List[str]) -> Any:
    """Handle RND function - returns random number."""
    val = int(interpreter.evaluate_expression(tokens[2:-1])) if tokens[2:-1] else 0
    rnd_val = random.random() if val >= 0 else (random.seed(int(val)) or 0)
    if len(tokens) == 4:
        return rnd_val
    else:
        # RND is part of a larger expression, replace it with the value and re-evaluate
        new_tokens = [str(rnd_val)] + list(tokens[4:])
        return interpreter.evaluate_expression(new_tokens)


def eval_sin(interpreter: "BasicInterpreter", tokens: List[str]) -> float:
    """Handle SIN function."""
    val = float(interpreter.evaluate_expression(tokens[2:-1]))
    return math.sin(val)


def eval_cos(interpreter: "BasicInterpreter", tokens: List[str]) -> float:
    """Handle COS function."""
    val = float(interpreter.evaluate_expression(tokens[2:-1]))
    return math.cos(val)


def eval_tan(interpreter: "BasicInterpreter", tokens: List[str]) -> float:
    """Handle TAN function."""
    val = float(interpreter.evaluate_expression(tokens[2:-1]))
    return math.tan(val)


def eval_atn(interpreter: "BasicInterpreter", tokens: List[str]) -> float:
    """Handle ATN (arctangent) function."""
    val = float(interpreter.evaluate_expression(tokens[2:-1]))
    return math.atan(val)


def eval_exp(interpreter: "BasicInterpreter", tokens: List[str]) -> float:
    """Handle EXP function."""
    val = float(interpreter.evaluate_expression(tokens[2:-1]))
    return math.exp(val)


def eval_log(interpreter: "BasicInterpreter", tokens: List[str]) -> float:
    """Handle LOG (natural logarithm) function."""
    val = float(interpreter.evaluate_expression(tokens[2:-1]))
    return math.log(val)


def eval_left(interpreter: "BasicInterpreter", tokens: List[str]) -> str:
    """Handle LEFT$ function."""
    inner = tokens[2:-1]
    comma_idx = None
    for i, t in enumerate(inner):
        if t == ",":
            comma_idx = i
            break
    if comma_idx is not None:
        str_val = str(interpreter.evaluate_expression(inner[:comma_idx]))
        length = int(interpreter.evaluate_expression(inner[comma_idx + 1 :]))
        return str_val[:length]
    return ""


def eval_right(interpreter: "BasicInterpreter", tokens: List[str]) -> str:
    """Handle RIGHT$ function."""
    inner = tokens[2:-1]
    comma_idx = None
    for i, t in enumerate(inner):
        if t == ",":
            comma_idx = i
            break
    if comma_idx is not None:
        str_val = str(interpreter.evaluate_expression(inner[:comma_idx]))
        length = int(interpreter.evaluate_expression(inner[comma_idx + 1 :]))
        return str_val[-length:] if length <= len(str_val) else str_val
    return ""


def eval_mid(interpreter: "BasicInterpreter", tokens: List[str]) -> str:
    """Handle MID$ function."""
    inner = tokens[2:-1]
    commas = []
    for i, t in enumerate(inner):
        if t == ",":
            commas.append(i)
    if len(commas) >= 1:
        str_val = str(interpreter.evaluate_expression(inner[: commas[0]]))
        start = int(
            interpreter.evaluate_expression(
                inner[commas[0] + 1 : commas[1] if len(commas) > 1 else None]
            )
        )
        if len(commas) > 1:
            length = int(interpreter.evaluate_expression(inner[commas[1] + 1 :]))
            return str_val[start - 1 : start - 1 + length]
        else:
            return str_val[start - 1 :]
    return ""


def eval_len(interpreter: "BasicInterpreter", tokens: List[str]) -> int:
    """Handle LEN function."""
    str_val = str(interpreter.evaluate_expression(tokens[2:-1]))
    return len(str_val)


def eval_val(interpreter: "BasicInterpreter", tokens: List[str]) -> Any:
    """Handle VAL function - convert string to number."""
    str_val = str(interpreter.evaluate_expression(tokens[2:-1]))
    try:
        if "." in str_val:
            return float(str_val)
        return int(str_val)
    except ValueError:
        return 0


def eval_str(interpreter: "BasicInterpreter", tokens: List[str]) -> str:
    """Handle STR$ function - convert number to string."""
    val = interpreter.evaluate_expression(tokens[2:-1])
    return str(val)


def eval_chr(interpreter: "BasicInterpreter", tokens: List[str]) -> str:
    """Handle CHR$ function - convert code to character."""
    val = int(interpreter.evaluate_expression(tokens[2:-1]))
    chr_val = val % 256

    if chr_val == 147:  # Clear screen / Home cursor
        interpreter.screen.clear()
        return ""
    elif chr_val == 17:  # Cursor down
        interpreter.screen.cursor_down()
        return ""
    elif chr_val == 145:  # Cursor up
        interpreter.screen.cursor_up()
        return ""
    elif chr_val == 29:  # Cursor right
        interpreter.screen.cursor_right()
        return ""
    elif chr_val == 157:  # Cursor left
        interpreter.screen.cursor_left()
        return ""
    elif chr_val == 19:  # Home cursor
        interpreter.screen.home()
        return ""
    elif chr_val == 18:  # Reverse on
        return ""
    elif chr_val == 146:  # Reverse off
        return ""
    else:
        return chr(chr_val)


def eval_screen(interpreter: "BasicInterpreter", tokens: List[str]) -> str:
    """Handle SCREEN$ function - read character from screen memory."""
    inner = tokens[2:-1]
    if len(inner) >= 3:
        row = int(interpreter.evaluate_expression([inner[0]]))
        col = int(interpreter.evaluate_expression([inner[2]]))
        if 0 <= row < SCREEN_ROWS and 0 <= col < SCREEN_COLS:
            addr = SCREEN_BASE + row * SCREEN_COLS + col
            char_code = interpreter.screen.peek(addr)
            if char_code >= 0:
                return chr(char_code)
    return " "


def eval_asc(interpreter: "BasicInterpreter", tokens: List[str]) -> int:
    """Handle ASC function - convert character to code."""
    str_val = str(interpreter.evaluate_expression(tokens[2:-1]))
    return ord(str_val[0]) if str_val else 0


def is_function_call(func_name: str, tokens: List[str]) -> bool:
    """Check if tokens represent a function call: FUNC(...)"""
    return (
        len(tokens) >= 4
        and tokens[0] == func_name
        and tokens[1] == "("
        and tokens[-1] == ")"
    )


# Function dispatch table
FUNCTION_HANDLERS = {
    "PEEK": eval_peek,
    "ABS": eval_abs,
    "SQR": eval_sqr,
    "INT": eval_int,
    "SGN": eval_sgn,
    "RND": eval_rnd,
    "SIN": eval_sin,
    "COS": eval_cos,
    "TAN": eval_tan,
    "ATN": eval_atn,
    "EXP": eval_exp,
    "LOG": eval_log,
    "LEFT$": eval_left,
    "RIGHT$": eval_right,
    "MID$": eval_mid,
    "LEN": eval_len,
    "VAL": eval_val,
    "STR$": eval_str,
    "CHR$": eval_chr,
    "SCREEN$": eval_screen,
    "ASC": eval_asc,
}


def evaluate_function(
    interpreter: "BasicInterpreter", tokens: List[str]
) -> tuple[bool, Any]:
    """Evaluate a BASIC function if tokens match a known function pattern.

    Returns tuple (handled, result) where handled is True if a function was matched.
    """
    if not tokens:
        return False, None

    func_name = tokens[0]  # Already uppercase from tokenizer

    # Handle INKEY$ (special case - no parentheses)
    if func_name == "INKEY$":
        return True, eval_inkey(interpreter)

    # Special case for RND which can be part of larger expression
    if func_name == "RND" and len(tokens) >= 4 and tokens[1] == "(":
        return True, eval_rnd(interpreter, tokens)

    # Check for function call pattern: FUNC(...)
    if not is_function_call(func_name, tokens):
        return False, None

    # Dispatch via lookup table
    handler = FUNCTION_HANDLERS.get(func_name)
    if handler:
        return True, handler(interpreter, tokens)

    return False, None
