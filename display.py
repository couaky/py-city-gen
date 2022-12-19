import math

from PIL import Image

from worldsettings import WorldSettings
from heatmap import HeatMap

def heat(data, size):
    heat_map_img = Image.new("HSV", (size, size))

    heat_map_rgb = []
    for line in data:
        for pix in line:
            pix_rgb = math.floor((1.0 - pix) * 170)
            heat_map_rgb.append((pix_rgb, 255, 255))
    heat_map_img.putdata(heat_map_rgb)

    return heat_map_img

def roads(data, size):
    roads_map_img = Image.new("RGB", (size, size))

    roads_map_rgb = []
    for line in data:
        for pix in line:
            roads_map_rgb.append((pix, pix, pix))
    roads_map_img.putdata(roads_map_rgb)

    return roads_map_img

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
                index = (j * self.world_settings.grid_settings.size + self.world_settings.grid_settings.offset.y) * self.world_settings.width + (i * self.world_settings.grid_settings.size + self.world_settings.grid_settings.offset.x)
                grid_rgb[index] = (255, 255, 255)
        grid_img.putdata(grid_rgb)

        self._blend_to_image(grid_img)
