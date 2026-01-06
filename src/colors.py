"""
C64 Color Handling
==================
ANSI color codes and terminal color support for C64 emulation.
"""

import os
import sys


def _detect_256_color() -> bool:
    """Check if terminal supports 256 colors."""
    term = os.environ.get("TERM", "")
    colorterm = os.environ.get("COLORTERM", "")
    if "256color" in term or "256" in colorterm:
        return True
    if colorterm in ("truecolor", "24bit"):
        return True
    # Common 256-color terminals
    if any(t in term for t in ("xterm", "screen", "tmux", "rxvt", "linux")):
        return True
    return False


# Terminal capability flags
USE_COLORS = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False
USE_256_COLORS = USE_COLORS and _detect_256_color()


# C64 color codes to ANSI 256-color palette mapping
# These are carefully chosen to match the authentic C64 color palette
C64_COLORS_256 = {
    0: 16,  # Black -> 16 (pure black)
    1: 231,  # White -> 231 (pure white)
    2: 124,  # Red -> 124 (dark red, close to C64 red)
    3: 80,  # Cyan -> 80 (medium cyan)
    4: 128,  # Purple -> 128 (dark magenta/purple)
    5: 34,  # Green -> 34 (medium green)
    6: 20,  # Blue -> 20 (dark blue)
    7: 226,  # Yellow -> 226 (bright yellow)
    8: 166,  # Orange -> 166 (dark orange)
    9: 94,  # Brown -> 94 (brown/olive)
    10: 210,  # Light Red -> 210 (salmon/light red)
    11: 239,  # Dark Gray -> 239 (gray 30%)
    12: 246,  # Medium Gray -> 246 (gray 50%)
    13: 120,  # Light Green -> 120 (light green)
    14: 75,  # Light Blue -> 75 (light blue)
    15: 252,  # Light Gray -> 252 (gray 80%)
}

# Fallback to basic 16 ANSI colors for non-256 terminals
C64_COLORS_ANSI = {
    0: 30,  # Black
    1: 97,  # White (bright white)
    2: 31,  # Red
    3: 36,  # Cyan
    4: 35,  # Purple/Magenta
    5: 32,  # Green
    6: 34,  # Blue
    7: 93,  # Yellow (bright yellow)
    8: 33,  # Orange (using yellow/brown)
    9: 33,  # Brown (using yellow)
    10: 91,  # Light Red (bright red)
    11: 90,  # Dark Gray
    12: 37,  # Medium Gray
    13: 92,  # Light Green (bright green)
    14: 94,  # Light Blue (bright blue)
    15: 37,  # Light Gray
}


def get_ansi_color(c64_color: int, is_foreground: bool = True) -> str:
    """Get ANSI escape sequence for a C64 color code.

    Args:
        c64_color: C64 color code (0-15)
        is_foreground: True for foreground color, False for background

    Returns:
        ANSI escape sequence string
    """
    c64_color = c64_color & 0xF  # Ensure 0-15 range

    if USE_256_COLORS:
        color_num = C64_COLORS_256.get(c64_color, 231)  # Default to white
        if is_foreground:
            return f"\x1b[38;5;{color_num}m"
        else:
            return f"\x1b[48;5;{color_num}m"
    else:
        color_code = C64_COLORS_ANSI.get(c64_color, 37)  # Default to white
        if not is_foreground:
            color_code += 10  # Background colors are fg + 10
        return f"\x1b[{color_code}m"


def reset_ansi_color() -> str:
    """Get ANSI escape sequence to reset colors."""
    return "\x1b[0m"
