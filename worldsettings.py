import math
import random

from dataclasses import dataclass
from utils import Vec2


GRID_SIZE = 16
GRID_MAX_OFFSET = 5


# TODO: A little speech about the grid/block here
"""
The world and the grid

The world is a matrix. Each element of the matrix is a tile that can be an ...
"""


class WorldSettings:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        print('World size: {}x{}'.format(self.width, self.height))
        
        grid_width = math.floor((self.width - GRID_SIZE * 2) / GRID_SIZE)
        grid_height = math.floor((self.height - GRID_SIZE * 2) / GRID_SIZE)
        print('Grid generated: {}x{}'.format(grid_width, grid_height))

        grid_offset_x = math.floor((self.width - (grid_width * GRID_SIZE)) / 2)
        grid_offset_y = math.floor((self.height - (grid_height * GRID_SIZE)) / 2)
        grid_offset_x = random.randint(grid_offset_x - GRID_MAX_OFFSET, grid_offset_x + GRID_MAX_OFFSET)
        grid_offset_y = random.randint(grid_offset_y - GRID_MAX_OFFSET, grid_offset_y + GRID_MAX_OFFSET)
        print('Grid offset: {},{}'.format(grid_offset_x, grid_offset_y))
        
        self.grid_settings = GridSettings(GRID_SIZE, grid_width, grid_height, Vec2(grid_offset_x, grid_offset_y))


@dataclass
class GridSettings:
    size: int
    width: int
    height: int
    offset: Vec2
