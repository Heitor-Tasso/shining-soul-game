"""Core gameplay mechanics extracted from the legacy runtime.

The functions in this module are intentionally side-effect free where possible,
so the legacy game loop can keep its behavior while reducing global coupling.
"""

from __future__ import annotations

from random import randint

from utils.geometry import collideanyrect, getdirect, midpointrect, remove

DIRECTION_TO_INDEX: dict[str, int] = {
    "up": 0,
    "upright": 1,
    "right": 2,
    "downright": 3,
    "down": 4,
    "downleft": 5,
    "left": 6,
    "upleft": 7,
}


def choose_direction(
    direction_candidates: list[list[int]],
    self_x: int,
    self_y: int,
    enemy_x: int,
    enemy_y: int,
    enemy_x_list: list[int],
    enemy_y_list: list[int],
    block_rects: list,
    enemy_size: int,
    enemy_speed: float,
) -> list[int]:
    """Return the first valid direction candidate for enemy movement."""
    directions = direction_candidates[:]
    enemy_rects = [
        midpointrect(enemy_x_list[i], enemy_y_list[i], enemy_size, enemy_size)
        for i in range(len(enemy_x_list))
    ]

    for index in range(3):
        origin_x, origin_y = enemy_x, enemy_y
        next_x, next_y = ai_move(
            self_x,
            self_y,
            enemy_x,
            enemy_y,
            enemy_speed,
            directions[index],
        )
        has_collision = collideanyrect(
            midpointrect(next_x, next_y, enemy_size, enemy_size),
            remove(enemy_rects + block_rects, midpointrect(origin_x, origin_y, enemy_size, enemy_size)),
        )
        if has_collision:
            directions[index] = [0, 0]

    for direction in directions:
        if direction != [0, 0]:
            return direction
    return [0, 0]


def ai_move(
    self_x: int,
    self_y: int,
    enemy_x: int,
    enemy_y: int,
    enemy_speed: float,
    direction: list[int],
) -> tuple[int, int]:
    """Move enemy coordinates based on direction while preserving diagonal speed."""
    _ = self_x, self_y
    if abs(direction[0]) == abs(direction[1]) == 1:
        enemy_x += int(enemy_speed * direction[0] / (2 ** 0.5))
        enemy_y += int(enemy_speed * direction[1] / (2 ** 0.5))
    elif direction[0] == 0:
        enemy_y += int(enemy_speed * direction[1])
    elif direction[1] == 0:
        enemy_x += int(enemy_speed * direction[0])
    return enemy_x, enemy_y


def move_self(
    map_self_x: int,
    map_self_y: int,
    enemy_x_list: list[int],
    enemy_y_list: list[int],
    enemy_size: int,
    block_rects: list,
    self_size: int,
    self_speed: float,
    up_pressed: bool,
    down_pressed: bool,
    right_pressed: bool,
    left_pressed: bool,
) -> tuple[int, int, int, int]:
    """Move player and return updated coordinates and direction vector."""
    origin_x, origin_y = map_self_x, map_self_y
    direction_x, direction_y = 0, 0

    if up_pressed:
        direction_y = -1
    if down_pressed:
        direction_y = 1
    if right_pressed:
        direction_x = 1
    if left_pressed:
        direction_x = -1

    if abs(direction_x) == abs(direction_y) == 1:
        map_self_x += int(direction_x * self_speed / (2 ** 0.5))
        map_self_y += int(direction_y * self_speed / (2 ** 0.5))
    else:
        map_self_x += int(direction_x * self_speed)
        map_self_y += int(direction_y * self_speed)

    enemy_rects = [
        midpointrect(enemy_x_list[i], enemy_y_list[i], enemy_size, enemy_size)
        for i in range(len(enemy_x_list))
    ]
    if collideanyrect(midpointrect(map_self_x, map_self_y, self_size, self_size), enemy_rects + block_rects):
        return origin_x, origin_y, direction_x, direction_y
    return map_self_x, map_self_y, direction_x, direction_y


def direct_get_attacked(
    self_x: int,
    self_y: int,
    self_size: int,
    enemy_x: int,
    enemy_y: int,
    enemy_size: int,
) -> list[int] | bool:
    """Return attack direction from enemy to player if inside attack range."""
    if midpointrect(self_x, self_y, self_size, self_size).colliderect(
        midpointrect(enemy_x, enemy_y, 3 * enemy_size, 3 * enemy_size)
    ):
        collisions: list[list[int]] = []
        for x in range(3):
            for y in range(3):
                if midpointrect(
                    enemy_x + (x - 1) * enemy_size,
                    enemy_y + (y - 1) * enemy_size,
                    enemy_size,
                    enemy_size,
                ).colliderect(midpointrect(self_x, self_y, self_size, self_size)):
                    collisions.append([x - 1, y - 1])
        return collisions[0]
    return False


def direction_to_index(status: list[int]) -> int:
    """Convert a direction vector to legacy sprite index."""
    name = ""
    if status[1] == 1:
        name += "down"
    elif status[1] == -1:
        name += "up"
    if status[0] == 1:
        name += "right"
    elif status[0] == -1:
        name += "left"

    if name not in DIRECTION_TO_INDEX:
        raise ValueError(f"Invalid direction vector for sprite index: {status}")
    return DIRECTION_TO_INDEX[name]


def sprite_mode_index(
    status: list,
    character_type: str,
    self_sprite_modes: list[str],
    enemy_sprite_modes: list[str],
) -> int:
    """Convert status tuple into sprite mode index for player or enemy."""
    if character_type == "self":
        mode_name = "blade" if status[5] == 0 else "dart"
        mode_name += status[4]
        return self_sprite_modes.index(mode_name)
    return enemy_sprite_modes.index(status[4])


def enemy_sprite_size(status: list[int]) -> tuple[int, int] | None:
    """Return enemy sprite dimensions based on current direction."""
    if (status[0], status[1]) != (0, 0):
        if status[1] == 0:
            return (130, 61)
        if status[0] == 0:
            return (110, 127)
        return (130, 130)
    return None


def is_all_clear(enemy_x_list: list[int]) -> bool:
    """Return True when no enemies remain alive in current round."""
    return len(enemy_x_list) == 0


def generate_enemies(
    map_self_x: int,
    map_self_y: int,
    map_block_rects: list,
    game_level: int,
    map_size: tuple[int, int],
    enemy_size: int,
    self_size: int,
) -> tuple[list[int], list[int]]:
    """Generate enemy coordinates for the round with collision constraints."""
    enemy_count = 2 + game_level
    enemy_x: list[int] = []
    enemy_y: list[int] = []

    while True:
        candidate_x, candidate_y = randint(0, map_size[0]), randint(0, map_size[1])
        score = 0

        for rect in map_block_rects:
            if not midpointrect(candidate_x, candidate_y, enemy_size, enemy_size).colliderect(rect):
                score += 1

        for index in range(len(enemy_x)):
            if not midpointrect(candidate_x, candidate_y, enemy_size, enemy_size).colliderect(
                midpointrect(enemy_x[index], enemy_y[index], enemy_size, enemy_size)
            ):
                score += 1

        if not midpointrect(candidate_x, candidate_y, enemy_size, enemy_size).colliderect(
            midpointrect(map_self_x, map_self_y, self_size, self_size)
        ):
            score += 1

        if score == len(map_block_rects) + len(enemy_x) + 1 and (
            abs(candidate_x - map_self_x) > 400 or abs(candidate_y - map_self_y) > 300
        ):
            enemy_x.append(candidate_x)
            enemy_y.append(candidate_y)

        if len(enemy_x) == enemy_count:
            return enemy_x, enemy_y


def fallback_directions(enemy_x: int, enemy_y: int, self_x: int, self_y: int) -> list[list[int]]:
    """Proxy wrapper to keep legacy behavior from geometry.getdirect."""
    return getdirect(enemy_x, enemy_y, self_x, self_y)
