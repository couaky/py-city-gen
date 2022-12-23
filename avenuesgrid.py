from dataclasses import dataclass
import math
import random

from heatmap import HeatMap
from utils import Vec2, Vec2Direction
from worldsettings import WorldSettings


class AvenuesGrid:
    """
    AvenuesGrid

    Represents the avenues aligned to the grid.

    Each vertex of the grid has an id and can be an avenue intersection.
    Id starts at 0 for the top left vertex and is assigned following the left-right, top-bottom order.

    The intersections are stored in the intersections property, which is a dict of Id->AvenueIntersection.
    If the dict has a key for the id of a given vertex, there is an intersection at this vertex.
    The AvenueIntersection describe the junctions with the next intersection in the 4 directions.
    """
    @dataclass
    class AvenueBuildOrder:
        intersection_coord: Vec2
        from_direction: Vec2Direction

    def __init__(self, world_settings: WorldSettings, heatmap: HeatMap) -> None:
        self.world_settings = world_settings
        self.heatmap = heatmap
        self.heat_factor = 1.3
        self.intersections: dict[int, AvenueIntersection] = dict()

    def from_grid_to_index(self, position: Vec2) -> int:
        """Returns the index in self.intersections for the given position of a vertex in the grid"""
        vertices_x_count = self.world_settings.grid_settings.width + 1
        vertices_y_count = self.world_settings.grid_settings.height + 1
        if position.x < 0 or position.x >= vertices_x_count or position.y < 0 or position.y >= vertices_y_count:
            raise ValueError(f"Vertex in grid out of bound {position.x}:{position.y}")
        return position.y * vertices_x_count + position.x

    def generate(self) -> None:
        """
        Generates the avenues and fillup the intersections dict.

        See the avenues generation process in the README for more details.
        """
        av_build_orders = self._generate_main_avenues()
        self._generate_avenues(av_build_orders)

    def _create_or_update_intersection(self, position: Vec2, from_directions: "list[Vec2Direction]") -> None:
        index = self.from_grid_to_index(position)
        intersection = self.intersections[index] if index in self.intersections else AvenueIntersection()

        for from_direction in from_directions:
            if from_direction == Vec2Direction.UP:
                intersection.bottomjunction = True
            elif from_direction == Vec2Direction.RIGHT:
                intersection.leftjunction = True
            elif from_direction == Vec2Direction.DOWN:
                intersection.upjunction = True
            elif from_direction == Vec2Direction.LEFT:
                intersection.rightjunction = True

        self.intersections[index] = intersection

    def _generate_main_avenues(self) -> "list[AvenueBuildOrder]":
        center = Vec2(math.floor(self.world_settings.grid_settings.width / 2),
                      math.floor(self.world_settings.grid_settings.height / 2))
        print(f"Grid center: {center.x}:{center.y}")
        self._create_or_update_intersection(center, [Vec2Direction.UP, Vec2Direction.RIGHT, Vec2Direction.DOWN, Vec2Direction.LEFT])

        main_av_build_orders: "list[AvenuesGrid.AvenueBuildOrder]" = []
        main_av_build_orders.append(AvenuesGrid.AvenueBuildOrder(center + Vec2.from_direction(Vec2Direction.UP), Vec2Direction.UP))
        main_av_build_orders.append(AvenuesGrid.AvenueBuildOrder(center + Vec2.from_direction(Vec2Direction.DOWN), Vec2Direction.DOWN))
        main_av_build_orders.append(AvenuesGrid.AvenueBuildOrder(center + Vec2.from_direction(Vec2Direction.LEFT), Vec2Direction.LEFT))
        main_av_build_orders.append(AvenuesGrid.AvenueBuildOrder(center + Vec2.from_direction(Vec2Direction.RIGHT), Vec2Direction.RIGHT))

        av_build_orders: "list[AvenuesGrid.AvenueBuildOrder]" = []

        while len(main_av_build_orders) > 0:
            build_order = main_av_build_orders.pop(0)
            position = build_order.intersection_coord
            direction = build_order.from_direction

            # Branch left and right decision
            worldpos = self.world_settings.from_grid_to_world(position)
            current_heat = self.heatmap.heatmap[worldpos.y][worldpos.x]
            have_left = random.random() <= current_heat * self.heat_factor
            have_right = random.random() <= current_heat * self.heat_factor

            junctions_from_direction = [direction, Vec2.reverse(direction)]

            if have_left:
                left_dir = Vec2.left_of(direction)
                junctions_from_direction.append(Vec2.reverse(left_dir))
                av_build_orders.append(AvenuesGrid.AvenueBuildOrder(position + Vec2.from_direction(left_dir), left_dir))
            if have_right:
                right_dir = Vec2.right_of(direction)
                junctions_from_direction.append(Vec2.reverse(right_dir))
                av_build_orders.append(AvenuesGrid.AvenueBuildOrder(position + Vec2.from_direction(right_dir), right_dir))

            self._create_or_update_intersection(position, junctions_from_direction)

            if not (position.x == 0 or position.x == self.world_settings.grid_settings.width or position.y == 0 or position.y == self.world_settings.grid_settings.height):
                # if not on edge, continue the build process
                main_av_build_orders.append(AvenuesGrid.AvenueBuildOrder(position + Vec2.from_direction(direction), direction))

        return av_build_orders

    def _is_out(self, position: Vec2) -> bool:
        return position.x < 0 or position.x > self.world_settings.grid_settings.width or position.y < 0 or position.y > self.world_settings.grid_settings.height

    def _get_best_build_direction(self, build_directions: "list[Vec2Direction]", position: Vec2) -> Vec2Direction:
        # In case of same distance: priority
        #   - high heat
        #   - another avenue
        #   - map edge
        best_distances = [[build_direction, None, None] for build_direction in build_directions]
        for best_distance in best_distances:
            build_dir = Vec2.from_direction(best_distance[0])
            current_dist = 1
            current_pos = position + build_dir
            while not self._is_out(current_pos):
                world_pos = self.world_settings.from_grid_to_world(current_pos)
                index = self.from_grid_to_index(current_pos)
                if self.heatmap.heatmap[world_pos.y][world_pos.x] > 0:
                    best_distance[1] = 1
                    best_distance[2] = current_dist
                    break
                if index in self.intersections:
                    best_distance[1] = 2
                    best_distance[2] = current_dist
                    break
                current_dist += 1
                current_pos += build_dir
            if best_distance[2] is None:
                best_distance[1] = 3
                best_distance[2] = current_dist

        return sorted(best_distances, key=lambda dist: (dist[2], dist[1]))[0][0]

    def _generate_avenues(self, av_build_orders: "list[AvenueBuildOrder]") -> None:
        while len(av_build_orders) > 0:
            build_order = av_build_orders.pop(0)
            position = build_order.intersection_coord
            if self._is_out(position):
                continue
            direction = build_order.from_direction
            index = self.from_grid_to_index(position)
            intersection_exists = index in self.intersections

            if intersection_exists:
                # Just update the junction, no need to generate new build order, it was already been done before
                self._create_or_update_intersection(position, [direction])
            else:
                # Create the new intersection and generate build orders
                junctions_directions = [direction]
                worldpos = self.world_settings.from_grid_to_world(position)
                current_heat = self.heatmap.heatmap[worldpos.y][worldpos.x]
                all_build_directions = [direction, Vec2.left_of(direction), Vec2.right_of(direction)]

                if current_heat > 0:
                    selected_build_directions = [build_dir for build_dir in all_build_directions if random.random() <= current_heat * self.heat_factor]
                    if len(selected_build_directions) == 0:
                        selected_build_directions.append(random.choice(all_build_directions))
                    for build_dir in selected_build_directions:
                        junctions_directions.append(Vec2.reverse(build_dir))
                        av_build_orders.append(AvenuesGrid.AvenueBuildOrder(
                            position + Vec2.from_direction(build_dir),
                            build_dir
                        ))
                else:
                    build_dir = self._get_best_build_direction(all_build_directions, position)
                    junctions_directions.append(Vec2.reverse(build_dir))
                    av_build_orders.append(AvenuesGrid.AvenueBuildOrder(
                        position + Vec2.from_direction(build_dir),
                        build_dir
                    ))

                self._create_or_update_intersection(position, junctions_directions)


@dataclass
class AvenueIntersection:
    """
    AvenueIntersection

    Describe the junctions with the direct other intersections in the 4 directions.
    """
    upjunction: bool = False
    rightjunction: bool = False
    bottomjunction: bool = False
    leftjunction: bool = False
