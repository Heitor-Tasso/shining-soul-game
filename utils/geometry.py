"""Geometry and movement helper functions used by the game loop."""

from __future__ import annotations

from pygame import Rect


def note(value: int) -> int:
    """Normalize a numeric signal into -1, 0, or 1."""
    if value == 0:
        return 0
    return abs(value) // value


def dist(x1: float, y1: float, x2: float, y2: float) -> float:
    """Return Euclidean distance between two points."""
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def remove(items: list, unit: object) -> list:
    """Return a shallow copy of list with the given element removed when present."""
    copied = items[:]
    if unit in copied:
        del copied[copied.index(unit)]
    return copied


def midpointrect(x: float, y: float, width: int, height: int) -> Rect:
    """Create a pygame rect from center coordinates."""
    return Rect(x - width // 2, y - height // 2, width, height)


def treeblockrect(x: int, y: int) -> Rect:
    """Return collision rect for one tree sprite anchored by top-left position."""
    return Rect(x + 135, y + 170, 99, 88)


def collideanyrect(rect: Rect, rect_list: list[Rect]) -> bool:
    """Check whether rect collides with any other rect in rect_list."""
    for other in rect_list:
        if rect.colliderect(other) and rect != other:
            return True
    return False


def getdirect(enemy_x: int, enemy_y: int, self_x: int, self_y: int) -> list[list[int]]:
    """Return preferred and fallback movement directions for enemy AI."""
    direction = [note(self_x - enemy_x), note(self_y - enemy_y)]
    if abs(self_x - enemy_x) < 51:
        direction[0] = 0
    if abs(self_y - enemy_y) < 51:
        direction[1] = 0

    if direction[0] == 0:
        return [direction] + [[-1, direction[1]], [1, direction[1]]]
    if direction[1] == 0:
        return [direction] + [[direction[0], 1], [direction[0], -1]]
    return [direction] + [[0, direction[1]], [direction[0], 0]]


def backtorange(x: int, y: int, size: int, mapsize: tuple[int, int]) -> tuple[int, int]:
    """Clamp an object center to map boundaries."""
    if x < size // 2:
        x = size // 2
    if x + size // 2 > mapsize[0]:
        x = mapsize[0] - size // 2
    if y < size // 2:
        y = size // 2
    if y + size // 2 > mapsize[1]:
        y = mapsize[1] - size // 2
    return x, y
