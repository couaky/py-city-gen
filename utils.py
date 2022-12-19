class Vec2:
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y

    @classmethod
    def from_direction(cls, direction: int) -> 'Vec2':
        if direction == Vec2.UP:
            return Vec2(0, 1)
        elif direction == Vec2.DOWN:
            return Vec2(0, -1)
        elif direction == Vec2.LEFT:
            return Vec2(-1, 0)
        else:
            return Vec2(1, 0)

    def __mul__(self, digit: int):
        return Vec2(self.x * digit, self.y * digit)

    def __add__(self, other_vec: 'Vec2'):
        return Vec2(self.x + other_vec.x, self.y + other_vec.y)
