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


def main():
    """Run the scrolling Rule 90 animation until interrupted."""
    width = get_width()

    # First generation: all dead except one alive cell in the exact center
    row = [DEAD] * width
    row[width // 2] = ALIVE

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
