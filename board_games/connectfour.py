"""
Just a tiny text-based ConnectFour game.
"""
import os
import time

import numpy as np

TERMX, TERMY = os.get_terminal_size()
ANIMATION_DELAY = .1

def print_lines(*lines):
    """Print `lines` centered in terminal.
    """
    for line in lines:
        print(line.center(TERMX))


class ConnectFour:
    """
    ConnectFour! The first player to connect four checkers in a row wins!
    """
    def __init__(self, height=6, width=7):
        self._to_bin = 2 ** np.arange(height * (width + 2), dtype=object)

        self.height, self.width = height, min(width, 35)
        self.labels = "1234567890abcdefghijklmnoprstuvwxyz"[:self.width]
        self.board = np.zeros((self.height, self.width + 2), dtype=int)

    @property
    def current_player(self):
        return np.count_nonzero(self.board) % 2 + 1

    def print_board(self):
        """Print our current board state.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

        header = f"╷{'╷'.join(self.labels)}╷"
        gutter = (f"│{'│'.join(' ●○'[value] for value in row[:-2])}│" for row in self.board[::-1])
        footer = f"╰{'─┴' * (self.width - 1)}─╯"

        print("\n" * ((TERMY - self.height - 5) // 2))  # Vertical Buffer
        print_lines(header, *gutter, footer)

    def is_valid_move(self, move: str) -> bool:
        """Return True if move is valid.
        """
        if move == 'q':
            return True

        if not (len(move) == 1 and move in self.labels):
            print_lines("Please input a valid column!")
            return False

        # Check that a move is possible in given column.
        column = self.labels.find(move)
        if np.count_nonzero(self.board[:, column]) < self.height:
            return True

        print_lines("No moves possible in that column!")
        return False

    def get_valid_move(self) -> str:
        player = "●○"[self.current_player - 1]
        while True:
            print_lines(f"{player}'s move, enter column or 'q' to quit:\n")
            move = input("".center(TERMX // 2)).lower()
            if self.is_valid_move(move):
                return move

    def play_move(self, column: int):
        """Drop a checker into a column.
        """
        player = self.current_player
        final_row = np.count_nonzero(self.board[:, column])
        board = self.board

        for row in range(self.height - 1, final_row, -1):
            board[row, column] = player
            self.print_board()
            board[row, column] = 0
            time.sleep(ANIMATION_DELAY)

        board[final_row, column] = player

    def is_winner(self, player):
        """Return True if a player has won.
        """
        key = (self.board == player).flatten() @ self._to_bin
        w = self.width + 2
        return any(
            key
            & key >> offset
            & key >> 2 * offset
            & key >> 3 * offset
            for offset in (1, w - 1, w, w + 1)
        )

    def run(self):
        for _ in range(self.width * self.height):
            player = self.current_player

            self.print_board()

            move = self.get_valid_move()

            if move == "q":
                break

            column = self.labels.find(move)

            self.play_move(column)

            if self.is_winner(player):
                self.print_board()
                print_lines(f"{'●○'[player - 1]} wins!")
                break

        else:
            self.print_board()
            print_lines("It's a draw!")


if __name__ == "__main__":
    ConnectFour().run()
