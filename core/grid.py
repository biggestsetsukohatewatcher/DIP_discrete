# core/grid.py
class Grid:
    def __init__(self, width, height, cell_size):
        self.cell_size = cell_size
        self.cols = int(width / cell_size)
        self.rows = int(height / cell_size)

    def world_to_cell(self, x, y):
        return int(x // self.cell_size), int(y // self.cell_size)

    def cell_to_world(self, cx, cy):
        return (
            cx * self.cell_size + self.cell_size / 2,
            cy * self.cell_size + self.cell_size / 2
        )
