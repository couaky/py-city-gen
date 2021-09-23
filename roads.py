import random

'''
Block size details

   |        |
  -+--------+-
   |        |
   <-------->
   block size
(include both left and right avenues)

build order position is just next to the cross in the build direction
build to the next cross and return the position of the new cross, ready to generate new build orders

'''

DIR_UP = 0
DIR_LEFT = 1
DIR_DOWN = 2
DIR_RIGHT = 3

AVENUE = 255

block_size = 10
heat_factor = 1.3

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

def buildAvenueSegment(build_order, roads_map, size):
    '''
    Build an avenue segment.
    Return None if no further build is required or the start of next build orders.
    '''
    if roads_map[build_order.origin.y][build_order.origin.x] == AVENUE:
        return None

    build_direction = Vec2.from_direction(build_order.direction)
    for i in range(block_size - 2):
        current_pos = build_order.origin + build_direction * i
        if not check_in_bounds(current_pos, size):
            break
        roads_map[current_pos.y][current_pos.x] = AVENUE

    target_pos = build_order.origin + build_direction * (block_size - 2)
    if not check_in_bounds(target_pos, size):
        return None
    elif roads_map[target_pos.y][target_pos.x] == AVENUE:
        return None

    roads_map[target_pos.y][target_pos.x] = AVENUE
    if check_on_edge(target_pos, size):
        return None

    return target_pos

def addAvenueBuildOrder(build_dir, position, av_build_orders):
    build_dir_vec = Vec2.from_direction(build_dir)
    build_start = position + build_dir_vec
    av_build_orders.append(AvenueBuildOrder(build_start.x, build_start.y, build_dir))

def generateMainAvenues(size, roads_map, heat_map, center_x, center_y):
    roads_map[center_y][center_x] = AVENUE

    main_av_build_orders = []
    av_build_orders = []

    main_av_build_orders.append(AvenueBuildOrder(center_x, center_y + 1, DIR_UP))
    main_av_build_orders.append(AvenueBuildOrder(center_x, center_y - 1, DIR_DOWN))
    main_av_build_orders.append(AvenueBuildOrder(center_x - 1, center_y, DIR_LEFT))
    main_av_build_orders.append(AvenueBuildOrder(center_x + 1, center_y, DIR_RIGHT))

    while len(main_av_build_orders) > 0:
        build_order = main_av_build_orders.pop(0)
        target_pos = buildAvenueSegment(build_order, roads_map, size)

        if target_pos is not None:
            build_direction = Vec2.from_direction(build_order.direction)
            forward_pos = target_pos + build_direction
            main_av_build_orders.append(AvenueBuildOrder(forward_pos.x, forward_pos.y, build_order.direction))

            current_heat = heat_map[target_pos.y][target_pos.x]
            have_left = random.random() <= current_heat * heat_factor
            have_right = random.random() <= current_heat * heat_factor

            if have_left:
                left_dir = left_of(build_order.direction)
                addAvenueBuildOrder(left_dir, target_pos, av_build_orders)
            if have_right:
                right_dir = right_of(build_order.direction)
                addAvenueBuildOrder(right_dir, target_pos, av_build_orders)

    return av_build_orders

def getBestBuildDirection(build_directions, init_position, roads_map, heat_map, size):
    # In case of same distance: priority
    #   - high heat
    #   - another avenue
    #   - map edge
    best_distances = [[build_direction, None, None] for build_direction in build_directions]
    for best_distance in best_distances:
        build_dir_vec = Vec2.from_direction(best_distance[0])
        current_dist = 1
        current_pos = init_position + build_dir_vec * (block_size - 1)
        while check_in_bounds(current_pos, size) and not check_on_edge(current_pos, size):
            if heat_map[current_pos.y][current_pos.x] > 0:
                best_distance[1] = 1
                best_distance[2] = current_dist
                break
            if roads_map[current_pos.y][current_pos.x] == AVENUE:
                best_distance[1] = 2
                best_distance[2] = current_dist
                break
            current_dist += 1
            current_pos += build_dir_vec * (block_size - 1)
        if best_distance[2] is None:
            best_distance[1] = 3
            best_distance[2] = current_dist

    return sorted(best_distances, key=lambda dist: (dist[2], dist[1]))[0][0]

def generateAvenues(size, av_build_orders, roads_map, heat_map):
    while len(av_build_orders) > 0:
        build_order = av_build_orders.pop(0)
        target_pos = buildAvenueSegment(build_order, roads_map, size)

        if target_pos is not None:
            current_heat = heat_map[target_pos.y][target_pos.x]
            all_build_directions = [build_order.direction, left_of(build_order.direction), right_of(build_order.direction)]
            if current_heat > 0:
                selected_build_directions = [build_dir for build_dir in all_build_directions if random.random() <= current_heat * heat_factor]
                if len(selected_build_directions) == 0:
                    selected_build_directions.append(random.choice(all_build_directions))
                for build_dir in selected_build_directions:
                    addAvenueBuildOrder(build_dir, target_pos, av_build_orders)
            else:
                build_dir = getBestBuildDirection(all_build_directions, target_pos, roads_map, heat_map, size)
                addAvenueBuildOrder(build_dir, target_pos, av_build_orders)

def generate(size, middle, heat_map):
    roads_map = [[0 for j in range(size)] for i in range(size)]

    center_step = 5
    center_x = random.randint(middle - center_step, middle + center_step)
    center_y = random.randint(middle - center_step, middle + center_step)

    print(f'Choosen center: {center_x}:{center_y}')

    av_build_orders = generateMainAvenues(size, roads_map, heat_map, center_x, center_y)
    generateAvenues(size, av_build_orders, roads_map, heat_map)
    
    return roads_map
