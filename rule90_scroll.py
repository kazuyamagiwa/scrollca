#!/usr/bin/env python3
"""Infinite scrolling Sierpiński triangle via Rule 90 cellular automaton."""

import shutil
import sys
import time

ALIVE = "█"
DEAD = " "


def get_width():
    """Return terminal width, falling back to 79 if detection fails."""
    try:
        return shutil.get_terminal_size().columns
    except OSError:
        return 79


def initial_row(width):
    """Return the first generation: one alive cell centered in a dead row."""
    row = [DEAD] * width
    row[width // 2] = ALIVE
    return row


def next_generation(row):
    """Compute the next Rule 90 generation with toroidal (wrap-around) edges.

    Rule 90: a cell is ALIVE iff its left and right neighbors differ (XOR).
    """
    width = len(row)
    next_row = []
    for i in range(width):
        left = row[(i - 1) % width]
        right = row[(i + 1) % width]
        # XOR: alive only when left and right neighbors are not equal
        next_row.append(ALIVE if left != right else DEAD)
    return next_row


def generate_rows(width, count, start_row=None):
    """Yield `count` generations starting from `start_row` (or a centered seed)."""
    row = list(start_row) if start_row is not None else initial_row(width)
    for _ in range(count):
        yield row
        row = next_generation(row)


def main():
    """Run the scrolling Rule 90 animation until interrupted."""
    width = get_width()
    row = initial_row(width)

    try:
        while True:
            print("".join(row))
            sys.stdout.flush()
            row = next_generation(row)
            time.sleep(0.05)
    except KeyboardInterrupt:
        # Clear any partial line and exit cleanly without a traceback
        sys.stdout.write("\r\033[K")
        print("\nStopped. Goodbye.")


if __name__ == "__main__":
    main()
