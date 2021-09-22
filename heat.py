import math
import random


def clamp(val, min_val, max_val):
    return min(max(val, min_val), max_val)

def simple_mean(heats):
    return math.fsum(heats) / len(heats)

def rand_in_range(heats):
    if min(heats) == max(heats):
        return heats[0]
    else:
        return random.uniform(min(heats), max(heats))

def rand_in_80_range(heats):
    min_val = min(heats)
    max_val = max(heats)
    if min_val == max_val:
        return heats[0]
    else:
        max_val_80 = min_val + 0.8 * (max_val - min_val)
        return random.uniform(min_val, max_val_80)

def compute_func(heats):
    return rand_in_80_range(heats)

def generate(size, min_heat, max_heat):
    # Heatmap gen with diamond-square
    heat_map = [[min_heat for j in range(size)] for i in range(size)]
    middle = int((size - 1) / 2)
    heat_map[middle][middle] = max_heat

    step = int((size - 1) / 2)
    while step > 1:
        half_step = int(step / 2)
        for x in range(half_step, size, step):
            for y in range(half_step, size, step):
                heats = (
                    heat_map[y - half_step][x - half_step],
                    heat_map[y - half_step][x + half_step],
                    heat_map[y + half_step][x + half_step],
                    heat_map[y + half_step][x - half_step]
                )
                heat_map[y][x] = compute_func(heats)
        step_offset = 0
        for x in range(0, size, half_step):
            if step_offset == 0:
                step_offset = half_step
            else:
                step_offset = 0
            for y in range(step_offset, size, step):
                heats = [min_heat for i in range(4)]
                if x >= half_step:
                    heats[0] = heat_map[y][x - half_step]
                if (x + half_step) < size:
                    heats[1] = heat_map[y][x + half_step]
                if y >= half_step:
                    heats[2] = heat_map[y - half_step][x]
                if (y + half_step) < size:
                    heats[3] = heat_map[y + half_step][x]
                heat_map[y][x] = compute_func(heats)
        step = half_step

    for x in range(size):
        for y in range(size):
            heat_map[y][x] = clamp(heat_map[y][x], 0, 1)

    return heat_map
