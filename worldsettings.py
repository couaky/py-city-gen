import math
import random
from dataclasses import dataclass

from utils import Vec2


"""
The world and the grid

The world is a matrix. Each element of the matrix is a tile that can be of different type.

The grid is the base shape of the city.
Avenues (main roads) follow the edges of the grid.
Blocks (buildings with smaller roads, usually surronded by avenues) are aligned with grid cells.

Each grid cell is a square of size GRID_CELL_SIZE.
Avenues are 2 tiles wide and overlap 2 cells.

Grid size (number of cells) depends of the world size. There are enough cells to fit the world with a margin of GRID_CELL_SIZE.
The grid is centered and a random offset +/-GRID_MAX_OFFSET is added in both axis.

Coordinates are: X for horizontal, Y for vertical, origin at top left, Y is bottom oriented, X is right oriented.
Matrices usually represented with a list of list of element as a list of row (matrix[y][x]).
"""


GRID_CELL_SIZE = 16
GRID_MAX_OFFSET = 5


class WorldSettings:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        print(f"World size: {self.width}x{self.height}")
        
        grid_width = math.floor((self.width - GRID_CELL_SIZE * 2) / GRID_CELL_SIZE)
        grid_height = math.floor((self.height - GRID_CELL_SIZE * 2) / GRID_CELL_SIZE)
        print(f"Grid generated: {grid_width}x{grid_height}")

        grid_offset_x = math.floor((self.width - (grid_width * GRID_CELL_SIZE)) / 2)
        grid_offset_y = math.floor((self.height - (grid_height * GRID_CELL_SIZE)) / 2)
        grid_offset_x = random.randint(grid_offset_x - GRID_MAX_OFFSET, grid_offset_x + GRID_MAX_OFFSET)
        grid_offset_y = random.randint(grid_offset_y - GRID_MAX_OFFSET, grid_offset_y + GRID_MAX_OFFSET)
        print(f"Grid offset: {grid_offset_x},{grid_offset_y}")
        
        self.grid_settings = GridSettings(GRID_CELL_SIZE, grid_width, grid_height, Vec2(grid_offset_x, grid_offset_y))

    def from_grid_to_world(self, vertex: Vec2) -> Vec2:
        """Convert coords of a vertex in the grid into a coords in the world"""
        new_x = vertex.x * self.grid_settings.cellsize + self.grid_settings.offset.x
        new_y = vertex.y * self.grid_settings.cellsize + self.grid_settings.offset.y
        return Vec2(new_x, new_y)

@dataclass
class GridSettings:
    cellsize: int
    width: int
    height: int
    offset: Vec2
