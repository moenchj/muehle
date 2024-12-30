
from typing import Dict


class Directions:
    right: int | None
    left: int | None
    up: int | None
    down: int | None

    def __init__(self, left: int | None, right: int | None, up: int | None, down: int | None):
        self.right = right
        self.left = left
        self.up = up
        self.down = down

    def has_neighbor(self, position: int):
        return self.right == position or self.left == position or self.up == position or self.down == position


positions: Dict[int, Directions] = {
    0: Directions(None, 1, None, 9),
    1: Directions(0, 2, None, 4),
    2: Directions(1, None, None, 14),
    3: Directions(4, None, None, 10),
    4: Directions(3, 5, 1, 7),
    5: Directions(4, None, None, 13),
    6: Directions(None, 7, None, 11),
    7: Directions(6, 8, 4, None),
    8: Directions(7, None, None, 12),
    9: Directions(None, 10, 0, 21),
    10: Directions(9, 11, 3, 18),
    11: Directions(10, None, 6, 15),
    12: Directions(None, 13, 8, 17),
    13: Directions(12, 14, 5, 20),
    14: Directions(13, None, 2, 23),
    15: Directions(None, 16, 11, None),
    16: Directions(15, 17, None, 19),
    17: Directions(16, None, 12, None),
    18: Directions(None, 19, 10, None),
    19: Directions(18, 20, 16, 22),
    20: Directions(19, None, 13, None),
    21: Directions(None, 22, 9, None),
    22: Directions(21, 23, 19, None),
    23: Directions(22, None, 14, None),
}
