import json
import os
from typing import List

import numpy as np
from numpy import random

from manager import save_manager


class ShasserCoulerGrid:
    def __init__(self, rows: int = 0, cols: int = 0):
        super().__init__()
        self.rows = rows
        self.cols = cols

        self.grid = [[False for j in range(self.cols)] for i in range(self.rows)]

        self.initialized = False

    def init(self):
        self.clear()
        self.initialized = True

    def delete(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        save_manager.delete(folder_path, "shassercouler_grid.json")

        self.clear()
        self.initialized = False

    def clear(self):
        self.grid = [[False for j in range(self.cols)] for i in range(self.rows)]

    def load(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        data = save_manager.load(folder_path, "shassercouler_grid.json")
        if data == "":
            return

        self.deserialize(data)
        self.initialized = True

    def save(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        save_manager.save(folder_path, "shassercouler_grid.json", self.serialize())

    def serialize(self) -> str:
        data = {
            "rows": self.rows,
            "cols": self.cols,
            "grid": self.grid,
        }
        return json.dumps(data, indent=4)

    def deserialize(self, data: str):
        json_data = json.loads(data)
        self.rows = json_data["rows"]
        self.cols = json_data["cols"]
        self.grid = json_data["grid"]

    def reveal(self, row: int = 0, col: int = 0, invert: bool = False) -> bool:
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False

        self.grid[row][col] = not invert
        return True

    def reveal_from_string(self, cell: str = "", invert: bool = False) -> bool:
        if len(cell) > 3:
            return False

        row = cell[0]
        col = cell[1:]
        row_int = ord(row.upper()) - ord("A")
        col_int = int(col) - 1

        return self.reveal(row_int, col_int, invert)

    def random_reveal(self, n_roll) -> List[np.ndarray]:
        # Get available cells
        false_cells = [(i, j) for i in range(self.rows) for j in range(self.cols) if not self.grid[i][j]]

        n_roll = min(len(false_cells), n_roll)

        rng = random.Generator(random.MT19937())
        selected_cells = rng.choice(np.array(false_cells), size=n_roll, replace=False)
        if n_roll == 1:
            selected_cells = [selected_cells]

        for i, j in selected_cells:
            self.reveal(i, j)

        return selected_cells

    def get_cell(self, row: int = 0, col: int = 0) -> str:
        return f"{chr(row + ord('A'))}{col + 1}"

    def format_discord(self) -> str:
        discord_str = ""
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                discord_str += f"{int(self.grid[i][j])} "
            discord_str += "\n"
        return discord_str
