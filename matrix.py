#!/usr/bin/env python3
"""
Matrix-style falling characters effect for the terminal.
Press Ctrl+C to stop.
"""
import random
import shutil
import sys
import time

CHARS = "アイウエオカキクケコサシスセソ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_SCREEN = "\033[2J"
MOVE_HOME = "\033[H"
RESET = "\033[0m"

# Pool of colors each drop can be assigned (ANSI foreground codes).
# "head" is the bright leading character, "body" is the dimmer trail.
COLOR_PALETTE = [
    {"head": "\033[1;37m", "body": "\033[32m"},   # classic green
    {"head": "\033[1;37m", "body": "\033[36m"},   # cyan
    {"head": "\033[1;37m", "body": "\033[35m"},   # magenta
    {"head": "\033[1;37m", "body": "\033[33m"},   # yellow
    {"head": "\033[1;37m", "body": "\033[34m"},   # blue
    {"head": "\033[1;37m", "body": "\033[31m"},   # red
]


def move_cursor(row, col):
    # Terminal coordinates are 1-indexed
    return f"\033[{row};{col}H"


def main():
    size = shutil.get_terminal_size((80, 24))
    width, height = size.columns, size.lines
    # Leave the very last row/col untouched — writing to the bottom-right
    # cell is what makes many terminals auto-scroll (adding a line).
    height = max(1, height - 1)
    width = max(1, width - 1)

    # One falling "drop" per column, each with its own speed, position, and color
    drops = [random.randint(-height, 0) for _ in range(width)]
    speeds = [random.choice([1, 1, 2]) for _ in range(width)]
    colors = [random.choice(COLOR_PALETTE) for _ in range(width)]

    out = sys.stdout
    out.write(HIDE_CURSOR + CLEAR_SCREEN)
    out.flush()

    try:
        while True:
            buffer = [HIDE_CURSOR]  # re-assert every frame in case it gets reset
            for col in range(width):
                row = drops[col]
                col_colors = colors[col]

                if 0 <= row < height:
                    ch = random.choice(CHARS)
                    buffer.append(move_cursor(row + 1, col + 1))
                    buffer.append(f"{col_colors['head']}{ch}{RESET}")

                # erase the character above the head so it doesn't leave a trail
                trail_row = row - 1
                if 0 <= trail_row < height:
                    ch = random.choice(CHARS)
                    buffer.append(move_cursor(trail_row + 1, col + 1))
                    buffer.append(f"{col_colors['body']}{ch}{RESET}")

                fade_row = row - 6
                if 0 <= fade_row < height:
                    buffer.append(move_cursor(fade_row + 1, col + 1))
                    buffer.append(" ")

                drops[col] += speeds[col]
                if drops[col] - 6 > height:
                    drops[col] = random.randint(-height, 0)
                    speeds[col] = random.choice([1, 1, 2])
                    colors[col] = random.choice(COLOR_PALETTE)  # new color on respawn

            # park the real cursor somewhere harmless (top-left) after drawing
            buffer.append(move_cursor(1, 1))
            out.write("".join(buffer))
            out.flush()
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        out.write(SHOW_CURSOR + CLEAR_SCREEN + MOVE_HOME)
        out.flush()


if __name__ == "__main__":
    main()
