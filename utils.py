from enum import IntEnum


class Vec2Direction(IntEnum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3


class Vec2:
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y

    @classmethod
    def from_direction(cls, direction: Vec2Direction) -> "Vec2":
        if direction == Vec2Direction.UP:
            return Vec2(0, -1)
        elif direction == Vec2Direction.DOWN:
            return Vec2(0, 1)
        elif direction == Vec2Direction.LEFT:
            return Vec2(-1, 0)
        else:
            return Vec2(1, 0)

    @classmethod
    def left_of(cls, direction: Vec2Direction) -> Vec2Direction:
        new_dir = direction + 1
        if new_dir > Vec2Direction.RIGHT:
            new_dir = Vec2Direction.UP
        return new_dir

    @classmethod
    def right_of(cls, direction: Vec2Direction) -> Vec2Direction:
        new_dir = direction - 1
        if new_dir < Vec2Direction.UP:
            new_dir = Vec2Direction.RIGHT
        return new_dir

    @classmethod
    def reverse(cls, direction: Vec2Direction) -> Vec2Direction:
        return (direction + 2) % (Vec2Direction.RIGHT + 1)

    def __mul__(self, digit: int):
        return Vec2(self.x * digit, self.y * digit)

    def __add__(self, other_vec: "Vec2"):
        return Vec2(self.x + other_vec.x, self.y + other_vec.y)
