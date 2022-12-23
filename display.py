import math

from PIL import Image

from avenuesgrid import AvenuesGrid
from worldsettings import WorldSettings
from heatmap import HeatMap
from utils import Vec2


class Printer:
    def __init__(self, world_settings: WorldSettings) -> None:
        self.world_settings = world_settings
        self.image = None

    def _blend_to_image(self, new_image) -> None:
        if self.image is not None:
            self.image = Image.blend(self.image, new_image, 0.5)
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

        self._blend_to_image(heat_map_img)

    def addgrid(self) -> None:
        grid_img = Image.new("RGB", (self.world_settings.width, self.world_settings.height))
        grid_rgb = [(0, 0, 0) for i in range(self.world_settings.width * self.world_settings.height)]
        for j in range(self.world_settings.grid_settings.height + 1):
            for i in range(self.world_settings.grid_settings.width + 1):
                index = (j * self.world_settings.grid_settings.cellsize + self.world_settings.grid_settings.offset.y) * self.world_settings.width + (i * self.world_settings.grid_settings.cellsize + self.world_settings.grid_settings.offset.x)
                grid_rgb[index] = (0, 0, 255)
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
        junctions_color = (255, 0, 0)
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
