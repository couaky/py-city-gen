from avenuesgrid import AvenuesGrid
from heatmap import HeatMap
from worldsettings import WorldSettings
from display import Printer


if __name__ == "__main__":
    world_settings = WorldSettings(256, 256)

    heat_map = HeatMap(world_settings)
    heat_map.generate(7, -0.3, 1.3)

    avenues_grid = AvenuesGrid(world_settings, heat_map)
    avenues_grid.generate()

    printer = Printer(world_settings)
    printer.addheat(heat_map)
    # printer.addgrid()
    printer.addavenues(avenues_grid)

    printer.image.show()
