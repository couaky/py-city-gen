import random


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

def check_in_bounds(position, size):
    return (position.x >= 0 and position.x < size and position.y >= 0 and position.y < size)

def check_on_edge(position, size):
    edge = size - 1
    return (position.x == 0 or position.x == edge or position.y == 0 or position.y == edge)

def buildMainAvenues():
    # TODO: HERE !
    pass

def generate(size, middle, heat_map):
    roads_map = [[0 for j in range(size)] for i in range(size)]

    center_step = 5
    center_x = random.randint(middle - center_step, middle + center_step)
    center_y = random.randint(middle - center_step, middle + center_step)

    print(f'Choosen center: {center_x}:{center_y}')

    main_av_build_orders = []
    av_build_orders = []

    roads_map[center_y][center_x] = AVENUE

    main_av_build_orders.append(AvenueBuildOrder(center_x, center_y + 1, DIR_UP))
    main_av_build_orders.append(AvenueBuildOrder(center_x, center_y - 1, DIR_DOWN))
    main_av_build_orders.append(AvenueBuildOrder(center_x - 1, center_y, DIR_LEFT))
    main_av_build_orders.append(AvenueBuildOrder(center_x + 1, center_y, DIR_RIGHT))

    while len(main_av_build_orders) > 0:
        build_order = main_av_build_orders.pop(0)
        if roads_map[build_order.origin.y][build_order.origin.x] == AVENUE:
            continue
        build_direction = Vec2.from_direction(build_order.direction)

        for i in range(block_size - 2):
            current_pos = build_order.origin + build_direction * i
            if not check_in_bounds(current_pos, size):
                break
            roads_map[current_pos.y][current_pos.x] = AVENUE

        target_pos = build_order.origin + build_direction * (block_size - 2)
        if not check_in_bounds(target_pos, size):
            continue
        elif roads_map[target_pos.y][target_pos.x] == AVENUE:
            continue
        else:
            roads_map[target_pos.y][target_pos.x] = AVENUE
            if not check_on_edge(target_pos, size):
                forward_pos = target_pos + build_direction
                main_av_build_orders.append(AvenueBuildOrder(forward_pos.x, forward_pos.y, build_order.direction))

                current_heat = heat_map[target_pos.y][target_pos.x]
                have_left = random.random() <= current_heat
                have_right = random.random() <= current_heat

                if have_left:
                    left_dir = left_of(build_order.direction)
                    left_dir_vec = Vec2.from_direction(left_dir)
                    left_start = target_pos + left_dir_vec
                    av_build_orders.append(AvenueBuildOrder(left_start.x, left_start.y, left_dir))
                if have_right:
                    right_dir = right_of(build_order.direction)
                    right_dir_vec = Vec2.from_direction(right_dir)
                    right_start = target_pos + right_dir_vec
                    av_build_orders.append(AvenueBuildOrder(right_start.x, right_start.y, right_dir))
    return roads_map
