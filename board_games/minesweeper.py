"""
Play Minesweeper in your terminal!
Arrow keys move the cursor, 'space' to reveal, 'f' to set a flag, and 'esc' to exit
"""

from itertools import product
import sys

import curses
import numpy as np
from scipy.ndimage import convolve

ROWS, COLUMNS = 20, 40
MINES = 150
KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
ESCAPE = 27


class RecursionLimit:
    def __init__(self, limit):
        self.limit = limit
        self.old_limit = sys.getrecursionlimit()

    def __enter__(self):
        sys.setrecursionlimit(self.limit)

    def __exit__(self, type, value, tb):
        sys.setrecursionlimit(self.old_limit)


class MineSweeper:
    def __init__(self, mines=MINES, height=ROWS, width=COLUMNS):
        self.mines = mines
        self.height, self.width = self.dim = height, width
        self.init_scr()

    def reset(self):
        self.minefield = np.zeros(self.dim, dtype=int)
        self.place_mines()

        self.count = np.where(self.minefield == 1, -1, convolve(self.minefield, KERNEL, mode='constant'))
        self.revealed = np.zeros(self.dim, dtype=bool)
        self.flags = np.zeros(self.dim, dtype=bool)

        self.cursor = np.array([self.height // 2, self.width // 2])
        self.mines_left = self.mines
        self.is_running = True

    def init_scr(self):
        self.screen = curses.initscr()
        self.screen.clear()
        self.screen.keypad(True)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        self.screen.attron(curses.color_pair(1))

    def end_curses(self):
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.flushinp()
        curses.endwin()

    def place_mines(self):
        for _ in range(self.mines):
            while True:
                location = np.random.randint(self.height), np.random.randint(self.width)
                if not self.minefield[location]:
                    self.minefield[location] = 1
                    break

    def get_user_input(self):
        key = self.screen.getch()
        position = tuple(self.cursor)

        if key == ESCAPE:
            self.is_running = False

        elif key == ord("f") and not self.revealed[position]:
            self.flags[position] ^= 1
            self.mines_left += -1 if self.flags[position] else 1

        elif key == ord(" ") and not self.flags[position]:
            with RecursionLimit(self.height * self.width):  # `reveal` could be called at most once for each cell
                self.reveal(position)

        elif key == curses.KEY_LEFT:
            self.cursor +=  0, -1
        elif key == curses.KEY_RIGHT:
            self.cursor +=  0,  1
        elif key == curses.KEY_UP:
            self.cursor += -1,  0
        elif key == curses.KEY_DOWN:
            self.cursor +=  1,  0

        self.cursor %= self.dim

    def show(self, text=""):
        """Display the minefield and print `text` directly below it.
        """
        h, w = self.screen.getmaxyx()
        centered_y = h // 2 - self.height // 2
        centered_x = w // 2 - self.width - 1

        view = np.where(self.flags, -3, np.where(self.revealed, self.count, -2))
        lines = (" ".join(" 12345678⚑■X"[value] for value in row) for row in view)

        self.screen.clear()

        # Minefield
        for i, line in enumerate(lines):
            self.screen.addstr(centered_y + i, centered_x, line)

        # Highlight cursor
        y, x = self.cursor
        self.screen.chgat(centered_y + y, centered_x + 2 * x, 1, curses.color_pair(2))

        # Add `text`
        below_minefield = h // 2 + self.height // 2
        centered_text_x = w // 2 - len(text) // 2
        self.screen.addstr(below_minefield, centered_text_x, text)

        self.screen.refresh()

    def reveal(self, location):
        """
        Reveal `location` on the minefield.  Ends the game if there is a mine at `location`.
        Recurses over `location`'s neighbors if `location` has no neighboring mines.
        """
        self.revealed[location] = True

        if self.minefield[location]:
            self.is_running = False

        elif self.count[location] == 0:
            for adjacent in product((-1, 0, 1), repeat=2):
                neighbor = tuple(np.array(location) + adjacent)
                if self.is_inbounds(neighbor) and not self.revealed[neighbor]:
                    self.reveal(neighbor)

    def is_inbounds(self, location):
        y, x = location
        return 0 <= y < self.height and 0 <= x < self.width

    def new_game(self):
        self.reset()

        while self.is_running:
            self.show(f"Mines: {self.mines_left}")
            self.get_user_input()

            if (~self.revealed == self.minefield).all():
                self.show("You win!")
                break
        else:
            self.revealed = np.ones(self.dim, dtype=bool)
            self.show("You lose!")

        self.screen.getch()

    def run(self):
        while True:
            self.new_game()
            self.show("Play again? [y]")
            if self.screen.getch() not in (ord("y"), ord("Y")):
                break

        self.end_curses()

if __name__ == "__main__":
    MineSweeper().run()
