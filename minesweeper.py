"""
Play Minesweeper in your terminal!
Arrow keys move the cursor, 'space' to reveal, 'f' to set a flag, and 'esc' to exit
"""

import curses
from itertools import product
import sys
import numpy as np
from scipy.ndimage import convolve

ROWS, COLUMNS = 20, 40
KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
MINES = 180
RECURSION_LIMIT = max(ROWS * COLUMNS, 1000)

class RecursionLimit:
    def __init__(self, limit):
        self.limit = limit
        self.old_limit = sys.getrecursionlimit()

    def __enter__(self):
        sys.setrecursionlimit(self.limit)

    def __exit__(self, type, value, tb):
        sys.setrecursionlimit(self.old_limit)

class MineSweeper:
    def __init__(self, mines, *dim):
        self.mines = mines
        self.HEIGHT, self.WIDTH = self.dim = dim
        self.init_scr()

    def reset(self):
        self.minefield = np.zeros(self.dim, dtype=int)
        self.place_mines()
        self.count = np.where(self.minefield==1, -1,
                              convolve(self.minefield, KERNEL, mode='constant'))
        self.revealed = np.zeros(self.dim, dtype=bool)
        self.flags = np.zeros(self.dim, dtype=bool)
        self.cursor = np.array([self.HEIGHT//2, self.WIDTH//2])
        self.mines_left = self.mines
        self.RUNNING = True

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
                location = np.random.randint(self.HEIGHT), np.random.randint(self.WIDTH)
                if not self.minefield[location]:
                    self.minefield[location] = 1
                    break

    def ask(self):
        key = self.screen.getch()
        if key == 27:  # Escape
            self.RUNNING = False
        elif key == ord("f") and not self.revealed[tuple(self.cursor)]:
            self.flags[tuple(self.cursor)] = not self.flags[tuple(self.cursor)]
            self.mines_left += (-1)**self.flags[tuple(self.cursor)]
        elif key == ord(" ") and not self.flags[tuple(self.cursor)]:
            with RecursionLimit(RECURSION_LIMIT):
                self.reveal(tuple(self.cursor))
        elif key == curses.KEY_LEFT:
            self.cursor += (0, -1)
        elif key == curses.KEY_RIGHT:
            self.cursor += (0, 1)
        elif key == curses.KEY_UP:
            self.cursor += (-1, 0)
        elif key == curses.KEY_DOWN:
            self.cursor += (1, 0)
        self.cursor %= (self.HEIGHT, self.WIDTH)


    def show(self, center_text, getch=False):
        h, w = self.screen.getmaxyx()
        view = np.where(self.flags, -3, np.where(self.revealed, self.count, -2))

        lines = (f'{" ".join(" 12345678⚑■🗙"[value] for value in row)}' for row in view)

        self.screen.clear()

        for i, line in enumerate(lines):
            self.screen.addstr(h//2 - (self.HEIGHT)//2 + i, w//2 - self.WIDTH - 1, line)

        y, x = self.cursor
        self.screen.chgat(h//2 - (self.HEIGHT + 1)//2 + y,
                          w//2 - (self.WIDTH + 1) + 2 * x,
                          1, curses.color_pair(2))

        self.print_centered(center_text)
        if getch:
            self.screen.getch()

        self.screen.refresh()

    def reveal(self, location):
        self.revealed[location] = True

        if self.minefield[location]:
            self.RUNNING = False
            self.revealed = np.ones((self.HEIGHT, self.WIDTH), dtype=bool)
            self.show("You lose!", getch=True)
            return

        if not self.count[location]:
            for adjacent in product((-1, 0, 1), repeat=2):
                neighbor = tuple(np.array(location) + adjacent)
                if self.is_inbounds(neighbor) and not self.revealed[neighbor]:
                    self.reveal(neighbor)

    def is_inbounds(self, location):
        y, x = location
        return 0 <= y < self.HEIGHT and 0 <= x < self.WIDTH

    def print_centered(self, text):
        h, w = self.screen.getmaxyx()
        self.screen.addstr(h//2 + self.HEIGHT//2 + 1, w//2 - len(text)//2, text)
        self.screen.refresh()

    def game(self):
        while self.RUNNING:
            self.show(f"Mines: {self.mines_left}")
            self.ask()

            if (~self.revealed == self.minefield).all():
                self.show("You win!", getch=True)
                return

    def start(self):
        while True:
            self.reset()
            self.game()
            self.show("Play again? [y]")
            if self.screen.getch() not in (ord("y"), ord("Y")):
                break

        self.end_curses()

if __name__ == "__main__":
    MineSweeper(MINES, ROWS, COLUMNS).start()
