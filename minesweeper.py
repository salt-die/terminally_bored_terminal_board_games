import numpy as np
from scipy.ndimage import convolve
from itertools import product

ROWS, COLUMNS = 20, 20
KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
MINES = 40

def ask(self):
        y, x = input("Enter coordinate: ")
        return self.labels.find(y), self.labels.find(x)

class MineSweeper:
    GAMEOVER = False
    labels = "abcdefghijklmnoprstuvwxz"

    def __init__(self, mines, *dim):
        self.mines = mines
        self.HEIGHT, self.WIDTH = dim
        self.minefield = np.zeros(dim, dtype=int)
        self.place_mines()
        self.count = np.where(self.minefield==1, -1, convolve(self.minefield, KERNEL,
                                                              mode='constant'))
        self.revealed = np.zeros(dim, dtype=bool)

    def place_mines(self):
        for _ in range(self.mines):
            while True:
                location = np.random.randint(self.HEIGHT), np.random.randint(self.WIDTH)
                if not self.minefield[location]:
                    self.minefield[location] = 1
                    break

    def ask(self):
        x, y = input("Enter row, column: ")
        return self.labels.find(x), self.labels.find(y)

    def show(self):
        view = np.where(self.revealed, self.count, -2)
        print(f'  {" ".join(self.labels[:self.WIDTH])}',
              *(f'{label} {" ".join(" 12345678.X"[value] for value in row)}'
                for label, row in zip(self.labels, view)), sep="\n")

    def reveal(self, location):
        self.revealed[location] = True
        if self.minefield[location]:
            self.GAMEOVER = True
            return
        if not self.count[location]:
            for adjacent in product((-1, 0, 1), repeat=2):
                neighbor = tuple(np.array(location) + adjacent)
                if not (not self.is_inbounds(neighbor) or
                        self.revealed[neighbor] or
                        self.minefield[neighbor]):
                    self.reveal(neighbor)

    def is_inbounds(self, location):
        y, x = location
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    def start(self):
        self.show()
        while not self.GAMEOVER:
            self.reveal(self.ask())
            self.show()
        print("Gameover")

if __name__ == "__main__":
    MineSweeper(MINES, ROWS, COLUMNS).start()