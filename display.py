import math

from PIL import Image

from avenuesgrid import AvenuesGrid
from worldsettings import WorldSettings
from heatmap import HeatMap
from streetsblocks import StreetsBlocks, StreetsPattern
from utils import Vec2


class Printer:
    def __init__(self, world_settings: WorldSettings) -> None:
        self.world_settings = world_settings
        self.image: Image = None

    def _is_black(self, color: "tuple(int, int, int)") -> bool:
        return color[0] == 0 and color[1] == 0 and color[2] == 0

    def _mix_color(self, colorA: "tuple(int, int, int)", colorB: "tuple(int, int, int)") -> "tuple(int, int, int)":
        return tuple(math.floor(chan[0] * 0.25 + chan[1] * 0.75) for chan in zip(colorA, colorB))

    def _blend_to_image(self, new_image: Image) -> None:
        if self.image is not None:
            # self.image = Image.blend(self.image, new_image, 0.5)
            bottom_data = list(self.image.getdata())
            top_data = list(new_image.getdata())
            new_data = []
            for pixels in zip(bottom_data, top_data):
                new_data.append(pixels[0] if self._is_black(pixels[1]) else self._mix_color(pixels[0], pixels[1]))
            self.image = Image.new("RGB", (self.world_settings.width, self.world_settings.height))
            self.image.putdata(new_data)
        else:
            self.image = new_image

    def addheat(self, heatmap: HeatMap) -> None:
        heat_map_img = Image.new("HSV", (self.world_settings.width, self.world_settings.height))

        heat_map_rgb = []
        for line in heatmap.heatmap:
            for pix in line:
                pix_rgb = math.floor((1.0 - pix) * 170)
                heat_map_rgb.append((pix_rgb, 255, 255))
        heat_map_img.putdata(heat_map_rgb)

        self._blend_to_image(Image.eval(heat_map_img.convert("RGB"), lambda val: math.floor(val * 0.5)))

    def addgrid(self) -> None:
        grid_img = Image.new("RGB", (self.world_settings.width, self.world_settings.height))
        grid_rgb = [(0, 0, 0) for i in range(self.world_settings.width * self.world_settings.height)]
        for j in range(self.world_settings.grid_settings.height + 1):
            for i in range(self.world_settings.grid_settings.width + 1):
                index = (j * self.world_settings.grid_settings.cellsize + self.world_settings.grid_settings.offset.y) * self.world_settings.width + (i * self.world_settings.grid_settings.cellsize + self.world_settings.grid_settings.offset.x)
                grid_rgb[index] = (100, 100, 100)
        grid_img.putdata(grid_rgb)

        self._blend_to_image(grid_img)

    def _draw_rectangle(self, topleft: Vec2, bottomright: Vec2, data_rgb: "list[tuple[int, int, int]]", color: "tuple[int, int, int]") -> None:
        for j in range(topleft.y, bottomright.y + 1):
            for i in range(topleft.x, bottomright.x + 1):
                data_rgb[j * self.world_settings.width + i] = color

    def addavenues(self, avenues_grid: AvenuesGrid) -> None:
        avenues_img = Image.new("RGB", (self.world_settings.width, self.world_settings.height))
        avenues_rgb = [(0, 0, 0) for i in range(self.world_settings.width * self.world_settings.height)]
        intersections_color = (255, 255, 255)
        junctions_color = (200, 200, 200)
        vertices_x_count = self.world_settings.grid_settings.width + 1  # There is one more vertices than the number of cell in a grid
        vertices_y_count = self.world_settings.grid_settings.height + 1
        for j in range(vertices_y_count):
            for i in range(vertices_x_count):
                index = j * vertices_x_count + i
                if index not in avenues_grid.intersections:
                    continue
                intersection = avenues_grid.intersections[index]
                world_coords = self.world_settings.from_grid_to_world(Vec2(i, j))
                is_top = j == 0
                is_right = i == vertices_x_count - 1
                is_bottom = j == vertices_y_count - 1
                is_left = i == 0
                # Draw the intersection (4 tiles)
                avenues_rgb[world_coords.y * self.world_settings.width + world_coords.x] = intersections_color
                avenues_rgb[(world_coords.y - 1) * self.world_settings.width + world_coords.x] = intersections_color
                avenues_rgb[world_coords.y * self.world_settings.width + (world_coords.x - 1)] = intersections_color
                avenues_rgb[(world_coords.y - 1) * self.world_settings.width + (world_coords.x - 1)] = intersections_color
                # Draw right and bottom junctions if exist
                if intersection.rightjunction:
                    if is_right:
                        self._draw_rectangle(
                            Vec2(world_coords.x + 1, world_coords.y - 1),
                            Vec2(self.world_settings.width - 1, world_coords.y),
                            avenues_rgb, junctions_color)
                    else:
                        self._draw_rectangle(
                            Vec2(world_coords.x + 1, world_coords.y - 1),
                            Vec2(world_coords.x + self.world_settings.grid_settings.cellsize - 2, world_coords.y),
                            avenues_rgb, junctions_color)
                if intersection.bottomjunction:
                    if is_bottom:
                        self._draw_rectangle(
                            Vec2(world_coords.x - 1, world_coords.y + 1),
                            Vec2(world_coords.x, self.world_settings.height - 1),
                            avenues_rgb, junctions_color)
                    else:
                        self._draw_rectangle(
                            Vec2(world_coords.x - 1, world_coords.y + 1),
                            Vec2(world_coords.x, world_coords.y + self.world_settings.grid_settings.cellsize - 2),
                            avenues_rgb, junctions_color)
                # Draw up and left junctions only for most left and most upper edges
                if is_top and intersection.upjunction:
                    self._draw_rectangle(
                            Vec2(world_coords.x - 1, 0),
                            Vec2(world_coords.x, world_coords.y - 2),
                            avenues_rgb, junctions_color)
                if is_left and intersection.leftjunction:
                    self._draw_rectangle(
                            Vec2(0, world_coords.y - 1),
                            Vec2(world_coords.x - 2, world_coords.y),
                            avenues_rgb, junctions_color)

        avenues_img.putdata(avenues_rgb)

        self._blend_to_image(avenues_img)

    def addstreets(self, streets_blocks: StreetsBlocks) -> None:
        streets_img = Image.new("RGB", (self.world_settings.width, self.world_settings.height))
        streets_rgb = [(0, 0, 0) for i in range(self.world_settings.width * self.world_settings.height)]
        streets_color = (155, 155, 155)
        cell_x_count = self.world_settings.grid_settings.width
        cell_y_count = self.world_settings.grid_settings.height
        street_count = math.floor((self.world_settings.grid_settings.cellsize - 1) / 3)
        for j in range(cell_y_count):
            for i in range(cell_x_count):
                cell_coord = Vec2(i, j)
                cell_index = streets_blocks.from_grid_to_index(cell_coord)
                if cell_index in streets_blocks.streets_patterns:
                    streets_pattern = streets_blocks.streets_patterns[cell_index]
                    world_coord = self.world_settings.from_grid_to_world(cell_coord)
                    if streets_pattern.street_pattern == StreetsPattern.StreetPattern.VERTICAL:
                        for street_index in range(street_count - 1):
                            self._draw_rectangle(
                                world_coord + Vec2((street_index + 1) * 3, 1),
                                world_coord + Vec2((street_index + 1) * 3, self.world_settings.grid_settings.cellsize - 2),
                                streets_rgb,
                                streets_color
                            )
                    elif streets_pattern.street_pattern == StreetsPattern.StreetPattern.HORIZONTAL:
                        for street_index in range(street_count - 1):
                            self._draw_rectangle(
                                world_coord + Vec2(1, (street_index + 1) * 3),
                                world_coord + Vec2(self.world_settings.grid_settings.cellsize - 2, (street_index + 1) * 3),
                                streets_rgb,
                                streets_color
                            )
                    elif streets_pattern.street_pattern == StreetsPattern.StreetPattern.L_TOP_RIGHT:
                        for street_index in range(street_count - 1):
                            self._draw_rectangle(
                                world_coord + Vec2((street_index + 1) * 3, 1),
                                world_coord + Vec2((street_index + 1) * 3, (self.world_settings.grid_settings.cellsize - 1) - (street_index + 1) * 3),
                                streets_rgb,
                                streets_color
                            )
                            self._draw_rectangle(
                                world_coord + Vec2(self.world_settings.grid_settings.cellsize - (street_index + 1) * 3, (street_index + 1) * 3),
                                world_coord + Vec2(self.world_settings.grid_settings.cellsize - 2, (street_index + 1) * 3),
                                streets_rgb,
                                streets_color
                            )
                    elif streets_pattern.street_pattern == StreetsPattern.StreetPattern.L_RIGHT_BOTTOM:
                        for street_index in range(street_count - 1):
                            self._draw_rectangle(
                                world_coord + Vec2((street_index + 1) * 3, (street_index + 1) * 3),
                                world_coord + Vec2(self.world_settings.grid_settings.cellsize - 2, (street_index + 1) * 3),
                                streets_rgb,
                                streets_color
                            )
                            self._draw_rectangle(
                                world_coord + Vec2((street_index + 1) * 3, (street_index + 1) * 3 + 1),
                                world_coord + Vec2((street_index + 1) * 3, self.world_settings.grid_settings.cellsize - 2),
                                streets_rgb,
                                streets_color
                            )
                    elif streets_pattern.street_pattern == StreetsPattern.StreetPattern.L_BOTTOM_LEFT:
                        for street_index in range(street_count - 1):
                            self._draw_rectangle(
                                world_coord + Vec2((street_index + 1) * 3, (self.world_settings.grid_settings.cellsize - 1) - (street_index + 1) * 3),
                                world_coord + Vec2((street_index + 1) * 3, self.world_settings.grid_settings.cellsize - 2),
                                streets_rgb,
                                streets_color
                            )
                            self._draw_rectangle(
                                world_coord + Vec2(1, (street_index + 1) * 3),
                                world_coord + Vec2((self.world_settings.grid_settings.cellsize - 2) - (street_index + 1) * 3, (street_index + 1) * 3),
                                streets_rgb,
                                streets_color
                            )
                    elif streets_pattern.street_pattern == StreetsPattern.StreetPattern.L_LEFT_TOP:
                        for street_index in range(street_count - 1):
                            self._draw_rectangle(
                                world_coord + Vec2(1, (street_index + 1) * 3),
                                world_coord + Vec2((street_index + 1) * 3, (street_index + 1) * 3),
                                streets_rgb,
                                streets_color
                            )
                            self._draw_rectangle(
                                world_coord + Vec2((street_index + 1) * 3, 1),
                                world_coord + Vec2((street_index + 1) * 3, (street_index + 1) * 3 - 1),
                                streets_rgb,
                                streets_color
                            )
        streets_img.putdata(streets_rgb)
        self._blend_to_image(streets_img)
