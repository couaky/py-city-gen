from dataclasses import dataclass
from enum import IntEnum

from avenuesgrid import AvenuesGrid
from utils import Vec2
from worldsettings import WorldSettings


class StreetsBlocks:
    """
    Streets Blocks

    Represents the pattern of the streets inside a block.

    Each cell of the grid is a potential city block if it's next to at least one avenues.
    Id starts at 0 for the top left cell and is assigned following the left-right, top-bottom order.

    The streets patterns are stored in the streets_patterns property, which is a dict of Id->StreetsPattern.
    If the dict has a key for the id of a given block, there are streets at this block.
    """
    def __init__(self, world_settings: WorldSettings, avenues_grid: AvenuesGrid) -> None:
        self.world_settings = world_settings
        self.avenues_grid = avenues_grid
        self.streets_patterns: dict[int, StreetsPattern] = dict()

    def from_grid_to_index(self, position: Vec2) -> int:
        """Returns the index in self.streets_patterns for the given position of a cell in the grid"""
        vertices_x_count = self.world_settings.grid_settings.width
        vertices_y_count = self.world_settings.grid_settings.height
        if position.x < 0 or position.x >= vertices_x_count or position.y < 0 or position.y >= vertices_y_count:
            raise ValueError(f"Cell in grid out of bound {position.x}:{position.y}")
        return position.y * vertices_x_count + position.x

    def generate(self) -> None:
        """
        Generates the streets patterns and fillup the streets_patterns dict.
        """
        grid_width = self.world_settings.grid_settings.width
        grid_height = self.world_settings.grid_settings.height
        for y in range(grid_height):
            for x in range(grid_width):
                grid_coord = Vec2(x, y)
                avenues = self._get_avenues(grid_coord)
                street_pattern = None
                if avenues[0] and avenues[2]:
                    street_pattern = StreetsPattern(StreetsPattern.StreetPattern.VERTICAL)
                elif avenues[1] and avenues[3]:
                    street_pattern = StreetsPattern(StreetsPattern.StreetPattern.HORIZONTAL)
                elif avenues[0] and avenues[1]:
                    street_pattern = StreetsPattern(StreetsPattern.StreetPattern.L_TOP_RIGHT)
                elif avenues[1] and avenues[2]:
                    street_pattern = StreetsPattern(StreetsPattern.StreetPattern.L_RIGHT_BOTTOM)
                elif avenues[2] and avenues[3]:
                    street_pattern = StreetsPattern(StreetsPattern.StreetPattern.L_BOTTOM_LEFT)
                elif avenues[3] and avenues[0]:
                    street_pattern = StreetsPattern(StreetsPattern.StreetPattern.L_LEFT_TOP)
                if street_pattern is not None:
                    self.streets_patterns[self.from_grid_to_index(grid_coord)] = street_pattern

    def _get_avenues(self, grid_coord: Vec2) -> "tuple[bool, bool, bool, bool]":
        """Returns a tuple of booleans if cell is surronded by avenues (up, right, bottom, left)"""
        avenues = [False, False, False, False]
        up_left_index = self.avenues_grid.from_grid_to_index(grid_coord)
        if up_left_index in self.avenues_grid.intersections:
            up_left_intersection = self.avenues_grid.intersections[up_left_index]
            avenues[0] = up_left_intersection.rightjunction
            avenues[3] = up_left_intersection.bottomjunction
        bottom_right_index = self.avenues_grid.from_grid_to_index(grid_coord + Vec2(1, 1))
        if bottom_right_index in self.avenues_grid.intersections:
            bottom_right_intersection = self.avenues_grid.intersections[bottom_right_index]
            avenues[1] = bottom_right_intersection.upjunction
            avenues[2] = bottom_right_intersection.leftjunction
        return tuple(avenues)


@dataclass
class StreetsPattern:
    class StreetPattern(IntEnum):
        VERTICAL = 0
        HORIZONTAL = 1
        L_TOP_RIGHT = 2
        L_RIGHT_BOTTOM = 3
        L_BOTTOM_LEFT = 4
        L_LEFT_TOP = 5
    street_pattern: StreetPattern
