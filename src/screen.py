"""
C64 Virtual Screen
==================
Simulates C64 screen memory for PEEK/POKE operations.
"""

import sys

import colorama

from src.constants import (
    SCREEN_BASE,
    SCREEN_COLS,
    SCREEN_ROWS,
    SCREEN_SIZE,
    COLOR_BASE,
    C64_DEFAULT_FG,
    C64_DEFAULT_BG,
)
from src.colors import USE_COLORS, get_ansi_color, reset_ansi_color
from src.charset import screen_code_to_unicode


class VirtualScreen:
    """Simulates C64 screen memory for PEEK/POKE"""

    def __init__(self, interpreter=None):
        self.screen_memory = [32] * SCREEN_SIZE  # Character codes (spaces)
        self.color_memory = [1] * SCREEN_SIZE  # Color codes (default white)
        self.cursor_x = 0
        self.cursor_y = 0
        self.interpreter = interpreter  # Reference to interpreter for auto-render

    def poke(self, addr: int, value: int) -> bool:
        """POKE to screen or color RAM. Returns True if handled."""
        if SCREEN_BASE <= addr < SCREEN_BASE + SCREEN_SIZE:
            self.screen_memory[addr - SCREEN_BASE] = value & 0xFF
            # Auto-render this character
            self._render_char(addr)
            return True
        elif COLOR_BASE <= addr < COLOR_BASE + SCREEN_SIZE:
            offset = addr - COLOR_BASE
            self.color_memory[offset] = value & 0xF
            # Re-render the character with the new color
            self._render_char(SCREEN_BASE + offset)
            return True
        return False

    def _render_char(self, addr: int):
        """Render a single character to terminal at its screen position with color."""
        if not USE_COLORS:
            return
        if SCREEN_BASE <= addr < SCREEN_BASE + SCREEN_SIZE:
            offset = addr - SCREEN_BASE
            row = offset // SCREEN_COLS
            col = offset % SCREEN_COLS
            char_code = self.screen_memory[offset]
            color_code = self.color_memory[offset]
            char = screen_code_to_unicode(char_code)

            # Screen codes 128-255 are reverse video (swap fg/bg)
            # Exception: code 224 (reverse space) renders as solid block in fg color
            is_reverse = char_code >= 128 and char_code != 224

            # Build the escape sequence: position + color + char + reset + hide cursor
            if is_reverse:
                # Reverse video: foreground color becomes background, screen bg becomes foreground
                fg_color = get_ansi_color(C64_DEFAULT_BG, is_foreground=True)
                bg_color = get_ansi_color(color_code, is_foreground=False)
            else:
                fg_color = get_ansi_color(color_code, is_foreground=True)
                bg_color = get_ansi_color(C64_DEFAULT_BG, is_foreground=False)
            reset = reset_ansi_color()

            sys.stdout.write(
                f"\x1b[{row + 1};{col + 1}H{bg_color}{fg_color}{char}{reset}\x1b[?25l"
            )
            sys.stdout.flush()

    def peek(self, addr: int) -> int:
        """PEEK from screen or color RAM. Returns -1 if not screen memory."""
        if SCREEN_BASE <= addr < SCREEN_BASE + SCREEN_SIZE:
            return self.screen_memory[addr - SCREEN_BASE]
        elif COLOR_BASE <= addr < COLOR_BASE + SCREEN_SIZE:
            return self.color_memory[addr - COLOR_BASE]
        return -1

    def clear(self):
        """Clear the screen (fill with spaces) and reset colors"""
        for i in range(SCREEN_SIZE):
            self.screen_memory[i] = 32  # Space character
            self.color_memory[i] = C64_DEFAULT_FG  # Reset to default foreground color
        self.cursor_x = 0
        self.cursor_y = 0
        # Clear terminal screen with C64 background color
        if USE_COLORS:
            bg_color = get_ansi_color(C64_DEFAULT_BG, is_foreground=False)
            sys.stdout.write(
                f"{bg_color}{colorama.ansi.clear_screen()}{colorama.ansi.Cursor.POS(0, 0)}"
            )
            sys.stdout.flush()

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

    def render(self):
        """Render the full screen to terminal with colors."""
        # Get default background color for the screen
        default_bg = get_ansi_color(C64_DEFAULT_BG, is_foreground=False)

        if USE_COLORS:
            # Set background color and clear screen
            print(
                f"{default_bg}{colorama.ansi.clear_screen()}{colorama.ansi.Cursor.POS(0, 0)}",
                end="",
            )
        else:
            print("\n" * SCREEN_ROWS + colorama.ansi.Cursor.POS(0, 0), end="")

        for row in range(SCREEN_ROWS):
            line_parts = []
            for col in range(SCREEN_COLS):
                offset = row * SCREEN_COLS + col
                char_code = self.screen_memory[offset]
                color_code = self.color_memory[offset]
                char = screen_code_to_unicode(char_code)

                if USE_COLORS:
                    # Screen codes 128-255 are reverse video (swap fg/bg)
                    # Exception: code 224 (reverse space) renders as solid block in fg color
                    is_reverse = char_code >= 128 and char_code != 224
                    if is_reverse:
                        fg_color = get_ansi_color(C64_DEFAULT_BG, is_foreground=True)
                        bg_color_char = get_ansi_color(color_code, is_foreground=False)
                        line_parts.append(
                            f"{bg_color_char}{fg_color}{char}{default_bg}"
                        )
                    else:
                        fg_color = get_ansi_color(color_code, is_foreground=True)
                        line_parts.append(f"{fg_color}{char}")
                else:
                    line_parts.append(char)

            if USE_COLORS:
                print("".join(line_parts) + reset_ansi_color())
            else:
                print("".join(line_parts))
