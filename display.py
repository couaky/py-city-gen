import math

from PIL import Image


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
