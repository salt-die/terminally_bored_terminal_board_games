"""
Play Minesweeper in your terminal!
Arrow keys move the cursor, 'space' to reveal, 'f' to set a flag, and 'esc' to exit
"""

import curses
from itertools import product
import numpy as np
from scipy.ndimage import convolve

ROWS, COLUMNS = 20, 40
KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
MINES = 200

class MineSweeper:
    RUNNING = True

    def __init__(self, mines, *dim):
        self.mines = mines
        self.HEIGHT, self.WIDTH = dim
        self.minefield = np.zeros(dim, dtype=int)
        self.place_mines()
        self.count = np.where(self.minefield==1, -1,
                              convolve(self.minefield, KERNEL, mode='constant'))
        self.revealed = np.zeros(dim, dtype=bool)
        self.flags = np.zeros(dim, dtype=bool)

        self.init_scr()
        self.cursor = np.array([self.HEIGHT//2, self.WIDTH//2])

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
        elif key == ord(" ") and not self.flags[tuple(self.cursor)]:
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


    def show(self):
        h, w = self.screen.getmaxyx()
        view = np.where(self.flags, -3, np.where(self.revealed, self.count, -2))

        lines = (f'{" ".join("▢12345678⚑▣X"[value] for value in row)}' for row in view)

        self.screen.clear()

        for i, line in enumerate(lines):
            self.screen.addstr(h//2 - (self.HEIGHT)//2 + i, w//2 - self.WIDTH - 1, line)

        y, x = self.cursor
        self.screen.chgat(h//2 - (self.HEIGHT + 1)//2 + y,
                          w//2 - (self.WIDTH + 1) + 2 * x,
                          1, curses.color_pair(2))

        self.screen.refresh()

    def reveal(self, location):
        self.revealed[location] = True
        if self.minefield[location]:
            self.RUNNING = False
            self.show()
            self.print_centered("You lose!")
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
        self.screen.getch()

    def start(self):
        while self.RUNNING:
            self.show()
            self.ask()

            if (~self.revealed == self.minefield).all():
                self.print_centered("You win!")
                break

        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.flushinp()
        curses.endwin()

if __name__ == "__main__":
    keep_playing = "y"
    while keep_playing == "y":
        MineSweeper(MINES, ROWS, COLUMNS).start()
        keep_playing = input("Play again?: [y]").lower()
