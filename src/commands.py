"""
C64 BASIC Commands
==================
Implementation of BASIC statement handlers (PRINT, GOTO, FOR, etc.)
"""

import sys
from typing import List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.interpreter import BasicInterpreter


# Terminal escape sequences for function keys (common variants)
# Maps escape sequence -> C64 PETSCII code
FKEY_SEQUENCES = {
    # xterm/vt220 style
    "\x1b[11~": chr(133),  # F1
    "\x1b[12~": chr(137),  # F2
    "\x1b[13~": chr(134),  # F3
    "\x1b[14~": chr(138),  # F4
    "\x1b[15~": chr(135),  # F5
    "\x1b[17~": chr(139),  # F6
    "\x1b[18~": chr(136),  # F7
    "\x1b[19~": chr(140),  # F8
    # vt100/xterm alternate style
    "\x1bOP": chr(133),  # F1
    "\x1bOQ": chr(137),  # F2
    "\x1bOR": chr(134),  # F3
    "\x1bOS": chr(138),  # F4
    # Linux console style
    "\x1b[[A": chr(133),  # F1
    "\x1b[[B": chr(137),  # F2
    "\x1b[[C": chr(134),  # F3
    "\x1b[[D": chr(138),  # F4
    "\x1b[[E": chr(135),  # F5
    # Arrow keys -> C64 cursor keys (PETSCII)
    "\x1b[A": chr(145),  # Up -> CRSR UP
    "\x1b[B": chr(17),  # Down -> CRSR DOWN
    "\x1b[C": chr(29),  # Right -> CRSR RIGHT
    "\x1b[D": chr(157),  # Left -> CRSR LEFT
    # Home/End
    "\x1b[H": chr(19),  # Home -> HOME
    "\x1b[F": chr(147),  # End -> CLR (clear screen)
    "\x1b[1~": chr(19),  # Home (alternate)
    "\x1b[4~": chr(147),  # End (alternate)
}


def handle_print(interpreter: "BasicInterpreter", tokens: List[str]) -> None:
    """Handle PRINT statement with Commodore 64 syntax."""
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
            result = interpreter.evaluate_expression(group_tokens)
            output.append(str(result))

    print("".join(output), end="" if suppress_newline else "\n", flush=True)


def handle_let(interpreter: "BasicInterpreter", tokens: List[str]) -> None:
    """Handle LET statement."""
    equals_index = None
    for i, token in enumerate(tokens):
        if token == "=":
            equals_index = i
            break

    if equals_index is not None and equals_index >= 1:
        var_name = tokens[0]
        value = interpreter.evaluate_expression(tokens[equals_index + 1 :])
        interpreter.variables[var_name] = value


def handle_assignment(interpreter: "BasicInterpreter", tokens: List[str]) -> None:
    """Handle direct assignment like 'X = 5'."""
    if len(tokens) >= 3 and tokens[1] == "=":
        var_name = tokens[0]
        value = interpreter.evaluate_expression(tokens[2:])
        interpreter.variables[var_name] = value


def handle_goto(interpreter: "BasicInterpreter", tokens: List[str]) -> int | None:
    """Handle GOTO statement."""
    if len(tokens) >= 2 and tokens[1].isdigit():
        target_line = int(tokens[1])
        interpreter.current_line = target_line
        return target_line
    return None


def handle_gosub(interpreter: "BasicInterpreter", tokens: List[str]) -> int | None:
    """Handle GOSUB statement."""
    if len(tokens) >= 2 and tokens[1].isdigit():
        target_line = int(tokens[1])
        if interpreter.current_line is not None:
            current_index = interpreter.line_execution_order.index(
                interpreter.current_line
            )
            return_line = (
                interpreter.line_execution_order[current_index + 1]
                if current_index + 1 < len(interpreter.line_execution_order)
                else None
            )
        else:
            return_line = None
        if return_line is not None:
            interpreter.call_stack.append(return_line)
        interpreter.current_line = target_line
        return target_line
    return None


def handle_return(interpreter: "BasicInterpreter", tokens: List[str]) -> int | None:
    """Handle RETURN statement."""
    if interpreter.call_stack:
        return_line = interpreter.call_stack.pop()
        if return_line:
            interpreter.current_line = return_line
            return return_line
    return None


def handle_if(interpreter: "BasicInterpreter", tokens: List[str]) -> Any:
    """Handle IF statement with THEN."""
    then_index = None
    for i, token in enumerate(tokens):
        if token == "THEN":
            then_index = i
            break

    if then_index is not None:
        condition_tokens = tokens[:then_index]
        then_tokens = tokens[then_index + 1 :]
        condition_result = interpreter.evaluate_condition(condition_tokens)

        if condition_result:
            if then_tokens:
                if len(then_tokens) >= 2 and then_tokens[0] == "GOTO":
                    if then_tokens[1].isdigit():
                        target_line = int(then_tokens[1])
                        interpreter.current_line = target_line
                        return target_line
                else:
                    line_num = (
                        interpreter.current_line
                        if interpreter.current_line is not None
                        else 0
                    )
                    return interpreter.parse_and_execute(line_num, then_tokens)
    return None


def handle_for(interpreter: "BasicInterpreter", tokens: List[str]) -> None:
    """Handle FOR statement: FOR var = start TO end [STEP step]."""
    try:
        eq_pos = tokens.index("=")
    except ValueError:
        print(f"?SYNTAX ERROR IN {interpreter.current_line}")
        return

    to_pos = None
    for i, tok in enumerate(tokens):
        if tok == "TO":
            to_pos = i
            break

    if to_pos is None or eq_pos < 1:
        print(f"?SYNTAX ERROR IN {interpreter.current_line}")
        return

    var_name = tokens[0]
    start_tokens = tokens[eq_pos + 1 : to_pos]
    end_tokens = tokens[to_pos + 1 :]

    # Handle optional STEP
    step_pos = None
    for i, tok in enumerate(end_tokens):
        if tok == "STEP":
            step_pos = i
            break

    if step_pos is not None:
        end_tokens = end_tokens[:step_pos]

    if not start_tokens or not end_tokens:
        print(f"?SYNTAX ERROR IN {interpreter.current_line}")
        return

    start_value = int(interpreter.evaluate_expression(start_tokens))
    end_value = int(interpreter.evaluate_expression(end_tokens))

    if var_name not in interpreter.for_loops:
        interpreter.variables[var_name] = start_value

    interpreter.for_loops[var_name] = {
        "line": interpreter.current_line,
        "end": end_value,
        "start": start_value,
        "same_line_body": False,
    }

    try:
        if interpreter.current_line is not None:
            current_index = interpreter.line_execution_order.index(
                interpreter.current_line
            )
            if current_index + 1 < len(interpreter.line_execution_order):
                interpreter.for_loop_returns[var_name] = (
                    interpreter.line_execution_order[current_index + 1]
                )
    except ValueError:
        pass


def handle_next(interpreter: "BasicInterpreter", tokens: List[str]) -> int | None:
    """Handle NEXT statement."""
    if tokens:
        var_name = tokens[0]
    elif interpreter.for_loops:
        var_name = list(interpreter.for_loops.keys())[-1]
    else:
        return None

    if var_name in interpreter.for_loops:
        loop_info = interpreter.for_loops[var_name]
        current_value = interpreter.variables.get(var_name, 0)
        new_value = current_value + 1

        if new_value <= loop_info["end"]:
            interpreter.variables[var_name] = new_value
            if loop_info.get("same_line_body"):
                return_line = loop_info["line"]
            else:
                return_line = interpreter.for_loop_returns.get(
                    var_name, loop_info["line"] + 10
                )
            interpreter.current_line = return_line
            return return_line
        else:
            del interpreter.for_loops[var_name]
            if var_name in interpreter.for_loop_returns:
                del interpreter.for_loop_returns[var_name]
    return None


def handle_data(interpreter: "BasicInterpreter", tokens: List[str]) -> None:
    """Handle DATA statement."""
    for token in tokens:
        if token == ",":
            continue
        if token.startswith('"') and token.endswith('"'):
            interpreter.data_section.append(token[1:-1])
        else:
            interpreter.data_section.append(token)


def handle_read(interpreter: "BasicInterpreter", tokens: List[str]) -> None:
    """Handle READ statement."""
    if not tokens:
        return

    var_names = [token for token in tokens if token != ","]

    for var_name in var_names:
        if interpreter.data_index < len(interpreter.data_section):
            value = interpreter.data_section[interpreter.data_index]
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
            interpreter.variables[var_name] = value
            interpreter.data_index += 1


def handle_input(interpreter: "BasicInterpreter", tokens: List[str]) -> None:
    """Handle INPUT statement."""
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
            if interpreter.input_buffer:
                user_input = interpreter.input_buffer.pop(0)
                print(user_input)
            else:
                user_input = interpreter.prompt_func()
            try:
                value = int(user_input)
            except ValueError:
                try:
                    value = float(user_input)
                except ValueError:
                    value = user_input
            interpreter.variables[var_name] = value
        except EOFError:
            print()
            break


def _read_escape_sequence(first_char: str) -> str:
    """Read and translate a terminal escape sequence to C64 PETSCII."""
    import select

    seq = first_char
    for _ in range(7):
        if select.select([sys.stdin], [], [], 0.05)[0]:
            seq += sys.stdin.read(1)
            if seq in FKEY_SEQUENCES:
                return FKEY_SEQUENCES[seq]
        else:
            break

    if seq in FKEY_SEQUENCES:
        return FKEY_SEQUENCES[seq]
    return ""


def handle_get(interpreter: "BasicInterpreter", tokens: List[str]) -> None:
    """Handle GET statement - non-blocking read of single keypress."""
    if not tokens:
        return

    var_name = tokens[0]

    if interpreter.input_buffer:
        key = interpreter.input_buffer.pop(0)
        if isinstance(key, str) and key.isalpha():
            key = key.upper()
        interpreter.variables[var_name] = key
    else:
        try:
            import select
            import termios

            if not sys.stdin.isatty():
                interpreter.variables[var_name] = ""
                return

            old_settings = termios.tcgetattr(sys.stdin)
            try:
                new_settings = termios.tcgetattr(sys.stdin)
                new_settings[3] = new_settings[3] & ~(termios.ICANON | termios.ECHO)
                new_settings[6][termios.VMIN] = 0
                new_settings[6][termios.VTIME] = 0
                termios.tcsetattr(sys.stdin, termios.TCSANOW, new_settings)

                if select.select([sys.stdin], [], [], 0)[0]:
                    ch = sys.stdin.read(1)
                    if ch == "\x03":
                        raise KeyboardInterrupt
                    if ch == "\x1b":
                        ch = _read_escape_sequence(ch)
                    elif ch.isalpha():
                        ch = ch.upper()
                    interpreter.variables[var_name] = ch
                else:
                    interpreter.variables[var_name] = ""
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        except (ImportError, OSError):
            interpreter.variables[var_name] = ""


def handle_poke(interpreter: "BasicInterpreter", tokens: List[str]) -> None:
    """Handle POKE statement - tries screen memory first, then general memory."""
    if len(tokens) >= 3:
        try:
            comma_idx = tokens.index(",")
            if tokens[0] == "POKE" and comma_idx > 1:
                addr_tokens = tokens[1:comma_idx]
            else:
                addr_tokens = tokens[:comma_idx]
            value_tokens = tokens[comma_idx + 1 :]
            addr = int(interpreter.evaluate_expression(addr_tokens))
            value = int(interpreter.evaluate_expression(value_tokens))
        except (ValueError, IndexError):
            addr = 0
            value = 0
        value = max(0, min(255, value))

        if not interpreter.screen.poke(addr, value):
            interpreter.memory[addr] = value


def handle_screen(interpreter: "BasicInterpreter", tokens: List[str]) -> None:
    """Display the virtual screen with ANSI colors."""
    interpreter.screen.render()
