"""Rendering helpers for the legacy game runtime."""

from __future__ import annotations

from pygame import draw

from core.mechanics import direction_to_index, enemy_sprite_size, sprite_mode_index


def character_blit(screen, image_obj, point: tuple[int, int], lock: str, size: tuple[int, int]) -> None:
    """Draw a sprite using a lock anchor strategy."""
    x, y = point
    width, height = size
    if lock == "tl":
        screen.blit(image_obj, (x - width // 2, y - height // 2))
    if lock == "tr":
        right_x, top_y = x + width // 2, y - height // 2
        screen.blit(image_obj, (right_x - image_obj.get_width(), top_y))
    if lock == "dl":
        left_x = x - width // 2
        bottom_y = y + height // 2
        screen.blit(image_obj, (left_x, bottom_y - image_obj.get_height()))
    if lock == "dr":
        right_x = x + width // 2
        bottom_y = y + height // 2
        screen.blit(image_obj, (right_x - image_obj.get_width(), bottom_y - image_obj.get_height()))
    if lock == "mid":
        screen.blit(image_obj, (x - image_obj.get_width() // 2, y - image_obj.get_height() // 2))


def draw_self(
    screen,
    self_pic,
    frame_self_status: list[int],
    self_status: list,
    self_sprite_modes: list[str],
    lock_table,
    screen_self_x: int,
    screen_self_y: int,
    self_frame_delay: int,
) -> None:
    """Draw player sprite and update animation frame counters."""
    if (frame_self_status[0], frame_self_status[1]) != (0, 0):
        direction_index = direction_to_index(frame_self_status)
        mode_index = sprite_mode_index(self_status, "self", self_sprite_modes, [])
        frame_sequence = self_pic[direction_index][mode_index]
        character_blit(
            screen,
            frame_sequence[frame_self_status[3]],
            (screen_self_x, screen_self_y),
            lock_table[direction_index][mode_index],
            (70, 100),
        )
        if frame_self_status[2] == 0:
            frame_self_status[2] += self_frame_delay
            frame_self_status[3] = (frame_self_status[3] + 1) % len(frame_sequence)
    if frame_self_status[2] > 0:
        frame_self_status[2] -= 1


def draw_enemy(
    screen,
    enemy_pic,
    frame_enemy_status,
    enemy_status,
    enemy_sprite_modes,
    enemy_lock,
    screen_enemy_x,
    screen_enemy_y,
    enemy_frame_delay: int,
) -> None:
    """Draw all enemy sprites and progress animation frames."""
    for index in range(len(screen_enemy_x)):
        if (frame_enemy_status[index][0], frame_enemy_status[index][1]) != (0, 0):
            direction_index = direction_to_index(frame_enemy_status[index])
            mode_index = sprite_mode_index(enemy_status[index], "enemy", [], enemy_sprite_modes)
            frame_sequence = enemy_pic[direction_index][mode_index]
            character_blit(
                screen,
                frame_sequence[frame_enemy_status[index][3]],
                (screen_enemy_x[index], screen_enemy_y[index]),
                enemy_lock[direction_index][mode_index],
                enemy_sprite_size(frame_enemy_status[index]) or (130, 130),
            )
            if frame_enemy_status[index][2] == 0:
                frame_enemy_status[index][2] += enemy_frame_delay
                frame_enemy_status[index][3] = (frame_enemy_status[index][3] + 1) % len(frame_sequence)
        if frame_enemy_status[index][2] > 0:
            frame_enemy_status[index][2] -= 1


def draw_single_enemy(
    screen,
    enemy_pic,
    frame_enemy_status,
    enemy_status,
    enemy_sprite_modes,
    enemy_lock,
    screen_enemy_x,
    screen_enemy_y,
    enemy_frame_delay: int,
    index: int,
) -> None:
    """Draw one enemy sprite instance for custom depth ordering flows."""
    if not (0 <= index < len(screen_enemy_x)):
        return

    if (frame_enemy_status[index][0], frame_enemy_status[index][1]) != (0, 0):
        direction_index = direction_to_index(frame_enemy_status[index])
        mode_index = sprite_mode_index(enemy_status[index], "enemy", [], enemy_sprite_modes)
        frame_sequence = enemy_pic[direction_index][mode_index]
        character_blit(
            screen,
            frame_sequence[frame_enemy_status[index][3]],
            (screen_enemy_x[index], screen_enemy_y[index]),
            enemy_lock[direction_index][mode_index],
            enemy_sprite_size(frame_enemy_status[index]) or (130, 130),
        )
        if frame_enemy_status[index][2] == 0:
            frame_enemy_status[index][2] += enemy_frame_delay
            frame_enemy_status[index][3] = (frame_enemy_status[index][3] + 1) % len(frame_sequence)
    if frame_enemy_status[index][2] > 0:
        frame_enemy_status[index][2] -= 1


def draw_knife(screen, self_knife: list[list], self_pic, knife_range: int) -> None:
    """Draw active knife projectiles and remove expired ones."""
    for knife in list(self_knife):
        frame = self_pic[direction_to_index(knife)][11][0]
        character_blit(screen, frame, (int(knife[4]), int(knife[5])), "mid", (50, 50))
        knife[6] += 1
        if knife[6] > knife_range and knife in self_knife:
            self_knife.remove(knife)


def draw_hp_bar(screen, hp_bar_pic, hp_font, self_status: list, self_hp: int) -> None:
    """Render HP bar and numeric health values."""
    screen.blit(hp_bar_pic, (47, 24))
    draw.rect(screen, (16, 248, 216), (94, 30, self_status[2] / 1.0 / self_hp * 120, 12), 0)
    hp_value = hp_font.render("%-5i" % (self_status[2]), True, (0, 0, 0))
    screen.blit(hp_value, (90, 50))
    hp_divider = hp_font.render("/", True, (0, 0, 0))
    screen.blit(hp_divider, (145, 50))
    hp_total = hp_font.render("%-5i" % (self_hp), True, (0, 0, 0))
    screen.blit(hp_total, (180, 50))


def draw_round_label(screen, hp_font, game_level: int) -> None:
    """Render current round label."""
    round_num = hp_font.render("ROUND %i" % (game_level), True, (255, 0, 0))
    screen.blit(round_num, (600, 20))


def draw_blade_block(screen, blade_block_pic, show_block: list[int], self_x: int, self_y: int) -> None:
    """Render transient blade block feedback and decay timers."""
    for index in range(len(show_block)):
        if show_block[index] > 0:
            screen.blit(blade_block_pic, (self_x - 50, self_y - 100))
            show_block[index] -= 1


def draw_particle(
    screen,
    x: float,
    y: float,
    size: float,
    color: tuple[int, int, int],
    alpha: int = 255,
) -> None:
    """Draw one debris particle as a tiny diamond sprite."""
    radius = max(1, int(size))
    points = [
        (int(x), int(y - radius)),
        (int(x + radius), int(y)),
        (int(x), int(y + radius)),
        (int(x - radius), int(y)),
    ]
    if alpha >= 255:
        draw.polygon(screen, color, points)
        return

    # Pygame draw.* ignores per-primitive alpha on display surfaces.
    # Draw to a tiny temporary alpha surface and blit it back.
    from pygame import SRCALPHA, Surface

    pad = radius + 2
    temp = Surface((pad * 2, pad * 2), SRCALPHA)
    shifted = [
        (point_x - int(x) + pad, point_y - int(y) + pad)
        for point_x, point_y in points
    ]
    draw.polygon(temp, (*color, alpha), shifted)
    screen.blit(temp, (int(x) - pad, int(y) - pad))
