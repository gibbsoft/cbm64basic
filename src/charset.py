"""
C64 Character Set Mappings
==========================
PETSCII and Screen Code to Unicode mappings.

The C64 uses two different character encodings:
1. PETSCII - Used by PRINT, CHR$(), INPUT, etc.
2. Screen Codes - Used when POKEing directly to screen RAM (1024-2023)

These are NOT the same! For example:
- PETSCII 65 = 'A' (uppercase A)
- Screen Code 65 = graphic character
"""

PETSCII_TO_UNICODE = {
    # Control characters (0-31) - most are non-printable
    # 13 = carriage return, 17 = cursor down, etc.
    # 32-63: Same as ASCII (space, punctuation, numbers)
    # These pass through unchanged
    # 64-95: Uppercase letters and symbols (similar to ASCII)
    64: "@",
    # 65-90: A-Z (same as ASCII, pass through)
    91: "[",
    92: "£",  # British pound (not backslash!)
    93: "]",
    94: "↑",  # Up arrow
    95: "←",  # Left arrow
    # 96-127: In true PETSCII these are graphic characters, but we leave
    # 97-122 unmapped so ASCII lowercase letters pass through unchanged.
    # This makes the interpreter more practical for modern use.
    # The same graphics are available via codes 192-223.
    96: "─",  # Horizontal line (backtick position)
    123: "┼",  # Cross
    124: "▒",  # Checker
    125: "│",  # Vertical line
    126: "π",  # Pi
    127: "◥",  # Triangle
    # 128-159: Control characters (reverse video toggle, colors, etc.)
    # Non-printable
    # 160-191: Shifted graphics (similar to 96-127 but shifted)
    160: " ",  # Shift-space (non-breaking space)
    161: "▌",  # Left half block
    162: "▄",  # Lower half block
    163: "▔",  # Upper 1/8 block
    164: "▁",  # Lower 1/8 block
    165: "▏",  # Left 1/8 block
    166: "▒",  # Checker
    167: "▕",  # Right 1/8 block
    168: "▒",  # Checker
    169: "▒",  # Checker
    170: "▕",  # Right 1/8 block
    171: "├",  # Left tee
    172: "▗",  # Quadrant
    173: "└",  # Corner
    174: "┐",  # Corner
    175: "▂",  # Lower 1/4 block
    176: "┌",  # Corner
    177: "┴",  # Bottom tee
    178: "┬",  # Top tee
    179: "┤",  # Right tee
    180: "▎",  # Left 1/4 block
    181: "▍",  # Left 3/8 block
    182: "▒",  # Checker
    183: "▒",  # Checker
    184: "▃",  # Lower 3/8 block
    185: "▖",  # Quadrant
    186: "▝",  # Quadrant
    187: "┘",  # Corner
    188: "▘",  # Quadrant
    189: "▚",  # Diagonal quadrants
    190: "▒",  # Checker
    191: "▒",  # Checker
    # 192-223: Shifted graphics (often same as 96-127)
    192: "─",
    193: "♠",
    194: "│",
    195: "─",
    196: "▒",
    197: "▒",
    198: "▒",
    199: "▒",
    200: "▒",
    201: "╮",
    202: "╰",
    203: "╯",
    204: "╲",
    205: "╱",  # Forward diagonal - used in maze
    206: "╲",  # Back diagonal - used in maze
    207: "╱",
    208: "╲",
    209: "●",
    210: "▒",
    211: "♥",
    212: "▒",
    213: "╭",
    214: "╳",
    215: "○",
    216: "♣",
    217: "▒",
    218: "♦",
    219: "┼",
    220: "▒",
    221: "│",
    222: "π",
    223: "◥",
    # 224-254: More graphics
    224: " ",
    225: "▌",
    226: "▄",
    227: "▔",
    228: "▁",
    229: "▏",
    230: "▒",
    231: "▕",
    232: "▒",
    233: "▒",
    234: "▕",
    235: "├",
    236: "▗",
    237: "└",
    238: "┐",
    239: "▂",
    240: "┌",
    241: "┴",
    242: "┬",
    243: "┤",
    244: "▎",
    245: "▍",
    246: "▒",
    247: "▒",
    248: "▃",
    249: "▖",
    250: "▝",
    251: "┘",
    252: "▘",
    253: "▚",
    254: "π",
    255: "▒",
}

# Screen Code to Unicode mapping (for POKE to screen RAM at 1024-2023)
# Screen codes are completely different from PETSCII!
SCREEN_CODE_TO_UNICODE = {
    # 0-31: @, A-Z, and some symbols
    0: "@",
    1: "A",
    2: "B",
    3: "C",
    4: "D",
    5: "E",
    6: "F",
    7: "G",
    8: "H",
    9: "I",
    10: "J",
    11: "K",
    12: "L",
    13: "M",
    14: "N",
    15: "O",
    16: "P",
    17: "Q",
    18: "R",
    19: "S",
    20: "T",
    21: "U",
    22: "V",
    23: "W",
    24: "X",
    25: "Y",
    26: "Z",
    27: "[",
    28: "£",
    29: "]",
    30: "↑",
    31: "←",
    # 32-63: Space, symbols, numbers (same as ASCII)
    32: " ",
    33: "!",
    34: '"',
    35: "#",
    36: "$",
    37: "%",
    38: "&",
    39: "'",
    40: "(",
    41: ")",
    42: "*",
    43: "+",
    44: ",",
    45: "-",
    46: ".",
    47: "/",
    48: "0",
    49: "1",
    50: "2",
    51: "3",
    52: "4",
    53: "5",
    54: "6",
    55: "7",
    56: "8",
    57: "9",
    58: ":",
    59: ";",
    60: "<",
    61: "=",
    62: ">",
    63: "?",
    # 64-95: Graphic characters
    64: "─",  # Horizontal line
    65: "♠",  # Spade
    66: "│",  # Vertical line
    67: "─",
    68: "▒",
    69: "▒",
    70: "▒",
    71: "▒",
    72: "▒",
    73: "╮",
    74: "╰",
    75: "╯",
    76: "╲",
    77: "╱",  # Screen code 77 = forward slash diagonal (M position)
    78: "╲",  # Screen code 78 = back slash diagonal (N position)
    79: "╱",
    80: "╲",
    81: "●",
    82: "▒",
    83: "♥",
    84: "▒",
    85: "╭",
    86: "╳",
    87: "○",
    88: "♣",
    89: "▒",
    90: "♦",
    91: "┼",
    92: "▒",
    93: "│",
    94: "π",
    95: "◥",
    # 96-127: More graphics
    96: " ",
    97: "▌",
    98: "▄",
    99: "▔",
    100: "▁",  # Screen code 100 = lower 1/8 block (used in maze indicator)
    101: "▏",
    102: "▒",
    103: "▕",
    104: "▒",
    105: "▒",
    106: "▕",
    107: "├",
    108: "▗",
    109: "└",
    110: "┐",
    111: "▂",
    112: "┌",
    113: "┴",
    114: "┬",
    115: "┤",
    116: "▎",
    117: "▍",
    118: "▒",
    119: "▒",
    120: "▃",
    121: "▖",
    122: "▝",
    123: "┘",
    124: "▘",
    125: "▚",
    126: "π",
    127: "▒",
    # 128-255: Reverse video versions of 0-127
    # We'll render these the same but could add reverse video support later
    128: "@",
    129: "A",
    130: "B",
    131: "C",
    132: "D",
    133: "E",
    134: "F",  # Screen code 134 = reverse F (used in maze indicator)
    135: "G",
    136: "H",
    137: "I",
    138: "J",
    139: "K",
    140: "L",
    141: "M",
    142: "N",
    143: "O",
    144: "P",
    145: "Q",
    146: "R",
    147: "S",
    148: "T",
    149: "U",
    150: "V",
    151: "W",
    152: "X",
    153: "Y",
    154: "Z",
    155: "[",
    156: "£",
    157: "]",
    158: "↑",
    159: "←",
    160: " ",
    161: "!",
    162: '"',
    163: "#",
    164: "$",
    165: "%",
    166: "&",
    167: "'",
    168: "(",
    169: ")",
    170: "*",
    171: "+",
    172: ",",
    173: "-",
    174: ".",
    175: "/",
    176: "0",
    177: "1",  # Note: 177 in screen code is "1", but maze uses it for checker
    178: "2",
    179: "3",
    180: "4",
    181: "5",
    182: "6",
    183: "7",
    184: "8",
    185: "9",
    186: ":",
    187: ";",
    188: "<",
    189: "=",
    190: ">",
    191: "?",
    192: "─",
    193: "♠",
    194: "│",
    195: "─",
    196: "▒",
    197: "▒",
    198: "▒",
    199: "▒",
    200: "▒",
    201: "╮",
    202: "╰",
    203: "╯",
    204: "╲",
    205: "╱",  # Screen code 205 = forward diagonal (used in maze!)
    206: "╲",  # Screen code 206 = back diagonal (used in maze!)
    207: "╱",
    208: "╲",
    209: "●",
    210: "▒",
    211: "♥",
    212: "▒",
    213: "╭",
    214: "╳",
    215: "○",
    216: "♣",
    217: "▒",
    218: "♦",
    219: "┼",
    220: "▒",
    221: "│",
    222: "π",
    223: "◥",
    224: " ",  # Screen code 224 = reverse space, often used as filled block
    225: "▌",
    226: "▄",
    227: "▔",
    228: "▁",
    229: "▏",
    230: "▒",
    231: "▕",
    232: "▒",
    233: "▒",
    234: "▕",
    235: "├",
    236: "▗",
    237: "└",
    238: "┐",
    239: "▂",
    240: "┌",
    241: "┴",
    242: "┬",
    243: "┤",
    244: "▎",
    245: "▍",
    246: "▒",
    247: "▒",
    248: "▃",
    249: "▖",
    250: "▝",
    251: "┘",
    252: "▘",
    253: "▚",
    254: "π",
    255: "▒",
}

# Corrections to screen codes for proper C64 graphics rendering
# Note: Screen codes 128-255 are reverse video versions of 0-127
# Screen code 134 = reverse "F", screen code 179 = reverse "3"
# These are correctly mapped in the main dict above (to "F" and "3")
# and will display in reverse video based on color attributes.
# The overrides below are only for codes that ARE graphical characters:
SCREEN_CODE_TO_UNICODE[100] = (
    "▁"  # Lower one eighth block (thin bottom line, full width)
)
SCREEN_CODE_TO_UNICODE[224] = (
    "█"  # Full block / solid (used for filled part of indicator bar)
)


def petscii_to_unicode(chars: str) -> str:
    """Convert PETSCII character codes to Unicode glyphs.

    Used for CHR$() output in PRINT statements.
    PETSCII is the C64's character encoding for I/O operations.
    """
    result = []
    for char in chars:
        code = ord(char)
        if code in PETSCII_TO_UNICODE:
            result.append(PETSCII_TO_UNICODE[code])
        elif 32 <= code < 128:
            # Standard ASCII printable range - pass through unchanged
            result.append(char)
        else:
            # Control characters or unmapped - pass through
            result.append(char)
    return "".join(result)


def screen_code_to_unicode(code: int) -> str:
    """Convert a C64 screen code to Unicode glyph.

    Used for rendering characters POKEd to screen RAM (1024-2023).
    Screen codes are different from PETSCII!
    """
    if code in SCREEN_CODE_TO_UNICODE:
        return SCREEN_CODE_TO_UNICODE[code]
    elif 32 <= code < 128:
        # Fallback: treat as ASCII for basic characters
        return chr(code)
    else:
        # Unknown code - return space
        return " "
