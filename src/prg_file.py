"""
C64 PRG File Format Handler
===========================
Handles loading and saving of Commodore 64 BASIC programs in PRG format.

PRG file structure:
- Bytes 0-1: Load address (little-endian, typically $0801 = 2049 for BASIC)
- Bytes 2+: Tokenized BASIC program

Each BASIC line is stored as:
- 2 bytes: Pointer to next line (little-endian)
- 2 bytes: Line number (little-endian)
- Tokenized BASIC text (keywords are single-byte tokens $80-$FF)
- 1 byte: $00 (end of line)

Program ends with:
- 2 bytes: $00 $00 (null pointer = end of program)
"""

from typing import Dict, List, Tuple, Optional


# C64 BASIC V2 Token table
# Tokens $80-$CB are BASIC keywords
BASIC_TOKENS = {
    0x80: "END",
    0x81: "FOR",
    0x82: "NEXT",
    0x83: "DATA",
    0x84: "INPUT#",
    0x85: "INPUT",
    0x86: "DIM",
    0x87: "READ",
    0x88: "LET",
    0x89: "GOTO",
    0x8A: "RUN",
    0x8B: "IF",
    0x8C: "RESTORE",
    0x8D: "GOSUB",
    0x8E: "RETURN",
    0x8F: "REM",
    0x90: "STOP",
    0x91: "ON",
    0x92: "WAIT",
    0x93: "LOAD",
    0x94: "SAVE",
    0x95: "VERIFY",
    0x96: "DEF",
    0x97: "POKE",
    0x98: "PRINT#",
    0x99: "PRINT",
    0x9A: "CONT",
    0x9B: "LIST",
    0x9C: "CLR",
    0x9D: "CMD",
    0x9E: "SYS",
    0x9F: "OPEN",
    0xA0: "CLOSE",
    0xA1: "GET",
    0xA2: "NEW",
    0xA3: "TAB(",
    0xA4: "TO",
    0xA5: "FN",
    0xA6: "SPC(",
    0xA7: "THEN",
    0xA8: "NOT",
    0xA9: "STEP",
    0xAA: "+",
    0xAB: "-",
    0xAC: "*",
    0xAD: "/",
    0xAE: "^",
    0xAF: "AND",
    0xB0: "OR",
    0xB1: ">",
    0xB2: "=",
    0xB3: "<",
    0xB4: "SGN",
    0xB5: "INT",
    0xB6: "ABS",
    0xB7: "USR",
    0xB8: "FRE",
    0xB9: "POS",
    0xBA: "SQR",
    0xBB: "RND",
    0xBC: "LOG",
    0xBD: "EXP",
    0xBE: "COS",
    0xBF: "SIN",
    0xC0: "TAN",
    0xC1: "ATN",
    0xC2: "PEEK",
    0xC3: "LEN",
    0xC4: "STR$",
    0xC5: "VAL",
    0xC6: "ASC",
    0xC7: "CHR$",
    0xC8: "LEFT$",
    0xC9: "RIGHT$",
    0xCA: "MID$",
    0xCB: "GO",  # For "GO TO" syntax (rarely used)
}

# Reverse mapping: keyword -> token
KEYWORD_TO_TOKEN = {v: k for k, v in BASIC_TOKENS.items()}

# Default BASIC load address
BASIC_START = 0x0801  # 2049 decimal


def load_prg(filename: str) -> Dict[int, str]:
    """Load a PRG file and return a dict of line_number -> BASIC text.

    Args:
        filename: Path to the PRG file

    Returns:
        Dictionary mapping line numbers to detokenized BASIC code

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    with open(filename, "rb") as f:
        data = f.read()

    if len(data) < 4:
        raise ValueError("PRG file too short")

    # First 2 bytes are load address (little-endian)
    load_addr = data[0] | (data[1] << 8)

    program_lines = {}
    pos = 2  # Start after load address
    current_addr = load_addr

    while pos < len(data) - 1:
        # Read pointer to next line (2 bytes, little-endian)
        if pos + 2 > len(data):
            break
        next_line_ptr = data[pos] | (data[pos + 1] << 8)

        # If next line pointer is 0, we've reached end of program
        if next_line_ptr == 0:
            break

        pos += 2

        # Read line number (2 bytes, little-endian)
        if pos + 2 > len(data):
            break
        line_num = data[pos] | (data[pos + 1] << 8)
        pos += 2

        # Read tokenized line until null terminator
        line_text = []
        in_string = False
        in_rem = False

        while pos < len(data) and data[pos] != 0:
            byte = data[pos]

            if in_string or in_rem:
                # Inside string or REM - don't interpret tokens
                if byte == 0x22:  # Quote
                    in_string = not in_string
                line_text.append(chr(byte))
            elif byte == 0x22:  # Quote starts string
                in_string = True
                line_text.append('"')
            elif byte >= 0x80 and byte in BASIC_TOKENS:
                # Token
                keyword = BASIC_TOKENS[byte]
                line_text.append(keyword)
                if keyword == "REM":
                    in_rem = True
            else:
                # Regular PETSCII character
                line_text.append(_petscii_to_ascii(byte))

            pos += 1

        # Skip null terminator
        pos += 1

        program_lines[line_num] = "".join(line_text)
        current_addr = next_line_ptr

    return program_lines


def save_prg(program_lines: Dict[int, str], filename: str) -> None:
    """Save a BASIC program to PRG format.

    Args:
        program_lines: Dictionary mapping line numbers to BASIC code
        filename: Path to save the PRG file
    """
    data = bytearray()

    # Write load address (little-endian)
    data.append(BASIC_START & 0xFF)
    data.append((BASIC_START >> 8) & 0xFF)

    current_addr = BASIC_START

    # Process each line in order
    for line_num in sorted(program_lines.keys()):
        line_text = program_lines[line_num]

        # Tokenize the line
        tokenized = _tokenize_line(line_text)

        # Calculate address of next line
        # Format: 2 bytes ptr + 2 bytes line num + tokenized + 1 byte null
        line_length = 2 + 2 + len(tokenized) + 1
        next_addr = current_addr + line_length

        # Write pointer to next line
        data.append(next_addr & 0xFF)
        data.append((next_addr >> 8) & 0xFF)

        # Write line number
        data.append(line_num & 0xFF)
        data.append((line_num >> 8) & 0xFF)

        # Write tokenized line
        data.extend(tokenized)

        # Write null terminator
        data.append(0x00)

        current_addr = next_addr

    # Write end-of-program marker (null pointer)
    data.append(0x00)
    data.append(0x00)

    with open(filename, "wb") as f:
        f.write(data)


def _tokenize_line(line: str) -> bytearray:
    """Tokenize a BASIC line.

    Args:
        line: BASIC line text (without line number)

    Returns:
        Bytearray of tokenized data
    """
    result = bytearray()
    i = 0
    in_string = False
    in_rem = False

    while i < len(line):
        char = line[i]

        if in_string:
            # Inside string - don't tokenize
            result.append(_ascii_to_petscii(char))
            if char == '"':
                in_string = False
            i += 1
            continue

        if in_rem:
            # Inside REM - rest of line is literal
            result.append(_ascii_to_petscii(char))
            i += 1
            continue

        if char == '"':
            in_string = True
            result.append(0x22)
            i += 1
            continue

        # Try to match a keyword (longest match first)
        matched = False
        # Sort keywords by length (descending) to match longest first
        for keyword in sorted(KEYWORD_TO_TOKEN.keys(), key=len, reverse=True):
            if line[i : i + len(keyword)].upper() == keyword:
                result.append(KEYWORD_TO_TOKEN[keyword])
                if keyword == "REM":
                    in_rem = True
                i += len(keyword)
                matched = True
                break

        if not matched:
            # Regular character
            result.append(_ascii_to_petscii(char))
            i += 1

    return result


def _petscii_to_ascii(byte: int) -> str:
    """Convert a PETSCII byte to ASCII character.

    Args:
        byte: PETSCII byte value

    Returns:
        ASCII character string
    """
    # Standard printable ASCII range
    if 32 <= byte <= 127:
        # PETSCII uppercase letters are at 65-90 (same as ASCII)
        # PETSCII lowercase letters are at 193-218
        return chr(byte)

    # PETSCII lowercase (shifted) letters 193-218 -> a-z
    if 193 <= byte <= 218:
        return chr(byte - 128)  # Convert to ASCII lowercase

    # PETSCII uppercase (unshifted) in alternate range 97-122 -> A-Z
    if 97 <= byte <= 122:
        return chr(byte - 32)  # Convert to ASCII uppercase

    # Control characters and special - return as-is or placeholder
    if byte < 32:
        return ""  # Skip control characters

    return chr(byte) if byte < 256 else "?"


def _ascii_to_petscii(char: str) -> int:
    """Convert an ASCII character to PETSCII byte.

    Args:
        char: ASCII character

    Returns:
        PETSCII byte value
    """
    code = ord(char)

    # Standard printable ASCII range
    if 32 <= code <= 127:
        return code

    # Extended characters - pass through
    return code & 0xFF


def is_prg_file(filename: str) -> bool:
    """Check if filename has .prg extension.

    Args:
        filename: Filename to check

    Returns:
        True if filename ends with .prg (case-insensitive)
    """
    return filename.lower().endswith(".prg")
