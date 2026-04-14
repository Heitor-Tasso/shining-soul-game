"""Camera projection helpers for converting world coordinates to screen coordinates."""

from __future__ import annotations

from typing import Callable

from pygame import Rect


class Camera:
    """Converts map-space coordinates to screen-space coordinates."""

    def __init__(self, resolution: tuple[int, int]) -> None:
        self.resolution = resolution

    def project(
        self,
        player_x: int,
        player_y: int,
        enemy_x: list[int],
        enemy_y: list[int],
        tree_x: list[int],
        tree_y: list[int],
        mapsize: tuple[int, int],
        knife: list[list[float]],
        self_size: int,
        enemy_size: int,
        tree_block_rect_fn: Callable[[int, int], Rect],
    ) -> tuple[
        int,
        int,
        int,
        int,
        int,
        int,
        list[int],
        list[int],
        list[int],
        list[int],
        list[Rect],
        list[list[float]],
    ]:
        """Project world coordinates to screen coordinates for current frame."""
        scr_map_x, scr_map_y = 0, 0
        scr_self_x, scr_self_y = 0, 0
        scr_enemy_x: list[int] = []
        scr_enemy_y: list[int] = []
        scr_tree_x: list[int] = []
        scr_tree_y: list[int] = []
        scr_block: list[Rect] = []

        if player_x < self.resolution[0] // 2:
            scr_self_x = player_x
        elif mapsize[0] - player_x < self.resolution[0] // 2:
            scr_self_x = self.resolution[0] - (mapsize[0] - player_x)
        else:
            scr_self_x = self.resolution[0] // 2

        if player_y < self.resolution[1] // 2:
            scr_self_y = player_y
        elif mapsize[1] - player_y < self.resolution[1] // 2:
            scr_self_y = self.resolution[1] - (mapsize[1] - player_y)
        else:
            scr_self_y = self.resolution[1] // 2

        scr_map_x, scr_map_y = scr_self_x - player_x, scr_self_y - player_y

        for shot in knife:
            shot[4], shot[5] = shot[2] + scr_map_x, shot[3] + scr_map_y

        for index in range(len(tree_x)):
            projected_x = scr_map_x + tree_x[index]
            projected_y = scr_map_y + tree_y[index]
            scr_tree_x.append(projected_x)
            scr_tree_y.append(projected_y)
            scr_block.append(tree_block_rect_fn(projected_x, projected_y))

        for index in range(len(enemy_x)):
            scr_enemy_x.append(scr_map_x + enemy_x[index])
            scr_enemy_y.append(scr_map_y + enemy_y[index])

        return (
            player_x,
            player_y,
            scr_map_x,
            scr_map_y,
            scr_self_x,
            scr_self_y,
            scr_enemy_x,
            scr_enemy_y,
            scr_tree_x,
            scr_tree_y,
            scr_block,
            knife,
        )
