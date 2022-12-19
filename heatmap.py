import math
import random

from worldsettings import WorldSettings


class HeatMap:
    """
    HeatMap
    
    A heat map of the size of the world with float values between 0 and 1.

    Values can be read from the heatmap property: a list of list of floats.
    Format of the map: list of rows, start at the top left.

    Ex: read the heat of the 5th elmt of the 2nd line:
    value = heatmap.heatmap[2][5]
    """
    def __init__(self, world_settings: WorldSettings) -> None:
        self.world_settings = world_settings
        self.heatmap: list[list[float]] = [[0 for j in range(world_settings.width)] for i in range(world_settings.height)]

    def generate(self, scale: int, min_heat: float, max_heat: float) -> None:
        """
        Generate heat map with the diamond-square algorithm.
        scale is a positive integer that will be used to define the size of the generated map
        with the following formula 2^scale+1.
        min_heat and max_heat can be any float values but in the end of the generation, all values
        are clamped between 0 and 1.
        Then the map is fitted to the world size with a simple nearest logic.
        """
        size: int = pow(2, scale) + 1
        print("Generate a heat map of size {}".format(size))

        gen_heatmap = [[min_heat for j in range(size)] for i in range(size)]
        middle = int((size - 1) / 2)
        gen_heatmap[middle][middle] = max_heat

        step = int((size - 1) / 2)
        while step > 1:
            half_step = int(step / 2)
            for x in range(half_step, size, step):
                for y in range(half_step, size, step):
                    heats = (
                        gen_heatmap[y - half_step][x - half_step],
                        gen_heatmap[y - half_step][x + half_step],
                        gen_heatmap[y + half_step][x + half_step],
                        gen_heatmap[y + half_step][x - half_step]
                    )
                    gen_heatmap[y][x] = self._compute_func(heats)
            step_offset = 0
            for x in range(0, size, half_step):
                if step_offset == 0:
                    step_offset = half_step
                else:
                    step_offset = 0
                for y in range(step_offset, size, step):
                    heats = [min_heat for i in range(4)]
                    if x >= half_step:
                        heats[0] = gen_heatmap[y][x - half_step]
                    if (x + half_step) < size:
                        heats[1] = gen_heatmap[y][x + half_step]
                    if y >= half_step:
                        heats[2] = gen_heatmap[y - half_step][x]
                    if (y + half_step) < size:
                        heats[3] = gen_heatmap[y + half_step][x]
                    gen_heatmap[y][x] = self._compute_func(heats)
            step = half_step

        for x in range(size):
            for y in range(size):
                gen_heatmap[y][x] = self._clamp(gen_heatmap[y][x], 0, 1)
        
        # Scale to world
        for y in range(self.world_settings.height):
            for x in range(self.world_settings.width):
                nearest_x = math.floor((x / self.world_settings.width) * size)
                nearest_y = math.floor((y / self.world_settings.height) * size)
                self.heatmap[y][x] = gen_heatmap[nearest_y][nearest_x]

    def _clamp(self, val: float, min_val: float, max_val: float) -> float:
        return min(max(val, min_val), max_val)

    def _simple_mean(self, heats: 'tuple[float]') -> float:
        return math.fsum(heats) / len(heats)

    def _rand_in_range(self, heats: 'tuple[float]') -> float:
        if min(heats) == max(heats):
            return heats[0]
        else:
            return random.uniform(min(heats), max(heats))

    def _rand_in_80_range(self, heats: 'tuple[float]') -> float:
        min_val = min(heats)
        max_val = max(heats)
        if min_val == max_val:
            return heats[0]
        else:
            max_val_80 = min_val + 0.8 * (max_val - min_val)
            return random.uniform(min_val, max_val_80)

    def _compute_func(self, heats: 'tuple[float]') -> float:
        return self._rand_in_80_range(heats)
