"""
"""

import os
#import time
import numpy as np

TERMX, TERMY = os.get_terminal_size()

def center(*lines):
    """
    Center lines in terminal.
    """
    for line in lines:
        yield line.center(TERMX)

def print_line(line):
    """
    Print line centered in terminal.
    """
    print(*center(line))


class Reversi:
    """
    """
    current_move = None
    current_player = 0

    def __init__(self, height=8, width=8):
        self.height, self.width = min(height, 35), min(width, 35)
        self.labely = "1234567890abcdefghijklmnoprstuvwxyz"[:self.height]
        self.labelx = "1234567890abcdefghijklmnoprstuvwxyz"[:self.width]
        self.board = np.zeros((self.height, self.width), dtype=int)

        #Starting position
        self.board[self.height//2 - 1:self.height//2 + 1,
                   self.width//2 - 1: self.width//2 + 1] = np.array([[1, 2], [2, 1]])

    def print_board(self):
        """
        Print our current board state.
        """
        os.system("clear || cls")  # Clears the terminal

        labels = f"  {'   '.join(self.labelx)}"
        header = f"  ╭──{'─┬──' * (self.width - 1)}─╮"
        gutter = f"  ├──{'─┼──' * (self.width - 1)}─┤\n".join(
          f"{y_label} │ {' │ '.join(' ●○'[value] for value in row)} │\n"
          for y_label, row in zip(self.labely, self.board)).split("\n")[:-1]
        footer = f"  ╰──{'─┴──' * (self.width - 1)}─╯"

        print("\n" * ((TERMY - self.height * 2 - 5) // 2))  # Vertical Buffer
        print(*center(labels, header, *gutter, footer), sep="\n")

    def is_move_valid(self):
        """
        Returns True if self.current_move is a valid move or 'q'.
        """
        if self.current_move is None:
            return False

        if self.current_move == 'q':
            return True

        if len(self.current_move) != 2 or any((self.current_move[0] not in self.labelx,
                                               self.current_move[1] not in self.labely)):
            print_line("Please enter valid coordinate!")
            return False

        self.current_move = (self.labely.find(self.current_move[1]),
                             self.labelx.find(self.current_move[0]))

        if self.board[self.current_move]:
            print_line("Not a valid move!")
            return False

        return True

    def get_move(self):
        """
        Sets a players input to self.current_move.
        """
        print_line(f"{'●○'[self.current_player]}'s move, enter coordinate or 'q' to quit:\n")
        self.current_move = input("".center(TERMX // 2)).lower()

    def animate_move(self):
        """
        """
        pass

    def update_board(self):
        """
        """
        self.board[self.current_move] = self.current_player + 1

    def start(self):
        """
        The main game loop.
        """
        for _ in range(self.width * self.height):
            self.current_move = None

            self.print_board()

            while not self.is_move_valid():
                self.get_move()

            if self.current_move == "q":
                break

            #self.animate_move()

            self.update_board()

            self.current_player = not self.current_player


if __name__ == "__main__":
    try:
        COLUMNS = int(input("Number of columns (max 35): "))
        if COLUMNS > 35:  # Not enough labels -- add more if you want more COLUMNS.
            raise ValueError
    except ValueError:
        COLUMNS = 8

    try:
        ROWS = int(input("Number of rows: "))
        if ROWS > 35:
            raise ValueError
    except ValueError:
        ROWS = 8

    Reversi(ROWS, COLUMNS).start()
