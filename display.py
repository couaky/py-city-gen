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

    def addheat(self, heatmap: HeatMap) -> None:
        heat_map_img = Image.new("HSV", (self.world_settings.width, self.world_settings.height))

        heat_map_rgb = []
        for line in heatmap.heatmap:
            for pix in line:
                pix_rgb = math.floor((1.0 - pix) * 170)
                heat_map_rgb.append((pix_rgb, 255, 255))
        heat_map_img.putdata(heat_map_rgb)

        if self.image is not None:
            self.image = Image.blend(self.image, heat_map_img, 0.5)
        else:
            self.image = heat_map_img
