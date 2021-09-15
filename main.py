import math
import random

from PIL import Image


def clamp(val, min_val, max_val):
    return min(max(val, min_val), max_val)

# Map setup
# Need to be n^2+1
size = 129
min_heat = -0.3
max_heat = 1.3

# Heatmap gen with diamond-square
heat_map = [[min_heat for j in range(size)] for i in range(size)]
middle = int((size - 1) / 2)
heat_map[middle][middle] = max_heat

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

step = int((size - 1) / 2)
while step > 1:
    half_step = int(step / 2);
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
    step = half_step;

for x in range(size):
    for y in range(size):
        heat_map[y][x] = clamp(heat_map[y][x], 0, 1)

heat_map_img = Image.new("HSV", (size, size))

heat_map_rgb = []
for line in heat_map:
    for pix in line:
        pix_rgb = math.floor((1.0 - pix) * 170)
        heat_map_rgb.append((pix_rgb, 255, 255))
heat_map_img.putdata(heat_map_rgb)

# Roads generation

DIR_UP = 0
DIR_LEFT = 1
DIR_DOWN = 2
DIR_RIGHT = 3

AVENUE = 255

block_size = 10

def left_of(direction):
    new_dir = direction + 1
    if new_dir > 3:
        new_dir = 0
    return new_dir

def right_of(direction):
    new_dir = direction - 1
    if new_dir < 0:
        new_dir = 3
    return new_dir

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def from_direction(direction):
        if direction == DIR_UP:
            return Vec2(0, 1)
        elif direction == DIR_DOWN:
            return Vec2(0, -1)
        elif direction == DIR_LEFT:
            return Vec2(-1, 0)
        else:
            return Vec2(1, 0)
    def __mul__(self, digit):
        return Vec2(self.x * digit, self.y * digit)
    def __add__(self, other_vec):
        return Vec2(self.x + other_vec.x, self.y + other_vec.y)

class AvenueBuildOrder:
    def __init__(self, orig_x, orig_y, direction):
        self.origin = Vec2(orig_x, orig_y)
        self.direction = direction

def check_in_bounds(position):
    return (position.x >= 0 and position.x < size and position.y >= 0 and position.y < size)

def check_on_edge(position):
    edge = size - 1
    return (position.x == 0 or position.x == edge or position.y == 0 or position.y == edge)

roads_map = [[0 for j in range(size)] for i in range(size)]

center_step = 5
center_x = random.randint(middle - center_step, middle + center_step)
center_y = random.randint(middle - center_step, middle + center_step)

print(f'Choosen centre: {center_x}:{center_y}')

build_orders = []

roads_map[center_y][center_x] = AVENUE

build_orders.append(AvenueBuildOrder(center_x, center_y + 1, DIR_UP))
build_orders.append(AvenueBuildOrder(center_x, center_y - 1, DIR_DOWN))
build_orders.append(AvenueBuildOrder(center_x - 1, center_y, DIR_LEFT))
build_orders.append(AvenueBuildOrder(center_x + 1, center_y, DIR_RIGHT))

while len(build_orders) > 0:
    build_order = build_orders.pop(0)
    if roads_map[build_order.origin.y][build_order.origin.x] == 2:
        continue
    build_direction = Vec2.from_direction(build_order.direction)
    
    for i in range(block_size - 2):
        current_pos = build_order.origin + build_direction * i
        if not check_in_bounds(current_pos):
            break
        roads_map[current_pos.y][current_pos.x] = AVENUE

    target_pos = build_order.origin + build_direction * (block_size - 2)
    if not check_in_bounds(target_pos):
        continue
    elif roads_map[target_pos.y][target_pos.x] == AVENUE:
        continue
    else:
        roads_map[target_pos.y][target_pos.x] = AVENUE
        if not check_on_edge(target_pos):
            forward_pos = target_pos + build_direction
            build_orders.append(AvenueBuildOrder(forward_pos.x, forward_pos.y, build_order.direction))
    
            current_heat = heat_map[target_pos.y][target_pos.x]
            have_left = random.random() <= current_heat
            have_right = random.random() <= current_heat
            
            if have_left:
                left_dir = left_of(build_order.direction)
                left_dir_vec = Vec2.from_direction(left_dir)
                left_start = target_pos + left_dir_vec
                build_orders.append(AvenueBuildOrder(left_start.x, left_start.y, left_dir))
            if have_right:
                right_dir = right_of(build_order.direction)
                right_dir_vec = Vec2.from_direction(right_dir)
                right_start = target_pos + right_dir_vec
                build_orders.append(AvenueBuildOrder(right_start.x, right_start.y, right_dir))
    
roads_map_img = Image.new("RGB", (size, size))

roads_map_rgb = []
for line in roads_map:
    for pix in line:
        roads_map_rgb.append((pix, pix, pix))
roads_map_img.putdata(roads_map_rgb)

complete_map = Image.blend(heat_map_img, roads_map_img, 0.5)
complete_map.show()


# TODO:
# Add streets: from bottom, process avenues left->right bottom->up
# if we have another avenue somewhere upside
# then we can spawn street between the two avenue acording the heat value

# A street is just a vertical strait road between 2 avenues
