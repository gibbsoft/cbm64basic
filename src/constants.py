"""
C64 BASIC Constants
===================
Memory addresses, screen dimensions, and other C64-specific constants.
"""

# Screen memory layout
SCREEN_BASE = 1024  # $0400 in decimal - screen RAM
SCREEN_COLS = 40
SCREEN_ROWS = 25
SCREEN_SIZE = SCREEN_COLS * SCREEN_ROWS  # 1000 bytes
COLOR_BASE = 55296  # $D800 in decimal - color RAM

# Default C64 colors: light blue text on blue background
C64_DEFAULT_FG = 14  # Light blue
C64_DEFAULT_BG = 6  # Blue
