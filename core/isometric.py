"""Isometric projection helpers and camera culling utilities."""

from __future__ import annotations

from dataclasses import dataclass


TILE_W: int = 64
TILE_H: int = 32
Z_STEP: int = 16


def depth_sort_key(gx: float, gy: float, gz: float) -> float:
    """Painter ordering key: larger values should be drawn later."""
    return (gx + gy) + gz * 0.01


@dataclass
class IsometricCamera:
    """Camera that projects cartesian grid coordinates into screen space."""

    screen_w: int
    screen_h: int
    offset_x: float = 0.0
    offset_y: float = 0.0

    def cart_to_iso(self, gx: float, gy: float, gz: float = 0) -> tuple[float, float]:
        """Convert grid coordinates to isometric coordinates (no camera offset)."""
        iso_x = (gx - gy) * (TILE_W / 2)
        iso_y = (gx + gy) * (TILE_H / 2) - gz * Z_STEP
        return iso_x, iso_y

    def grid_to_screen(self, gx: float, gy: float, gz: float = 0) -> tuple[float, float]:
        """Convert grid coordinates directly into screen coordinates."""
        iso_x, iso_y = self.cart_to_iso(gx, gy, gz)
        return iso_x + self.offset_x, iso_y + self.offset_y

    def world_to_screen(
        self,
        wx: float,
        wy: float,
        gz: float = 0,
        tile_size: int = 32,
    ) -> tuple[float, float]:
        """Convert world pixel coordinates to screen coordinates."""
        gx = wx / tile_size
        gy = wy / tile_size
        return self.grid_to_screen(gx, gy, gz)

    def screen_to_grid(self, screen_x: float, screen_y: float, gz: float = 0) -> tuple[float, float]:
        """Inverse conversion from screen coordinates to grid coordinates."""
        iso_x = screen_x - self.offset_x
        iso_y = screen_y - self.offset_y + gz * Z_STEP

        gx = (iso_x / (TILE_W / 2) + iso_y / (TILE_H / 2)) / 2
        gy = (iso_y / (TILE_H / 2) - iso_x / (TILE_W / 2)) / 2
        return gx, gy

    def _world_iso_bounds(self, grid_w: int, grid_h: int) -> tuple[float, float, float, float]:
        corners = [
            self.cart_to_iso(0, 0, 0),
            self.cart_to_iso(grid_w, 0, 0),
            self.cart_to_iso(0, grid_h, 0),
            self.cart_to_iso(grid_w, grid_h, 0),
        ]
        xs = [point[0] for point in corners]
        ys = [point[1] for point in corners]
        return min(xs), max(xs), min(ys), max(ys)

    def update(self, player_wx: float, player_wy: float, grid_w: int, grid_h: int, tile_size: int) -> None:
        """Center camera on player and clamp to world extents."""
        player_gx = player_wx / tile_size
        player_gy = player_wy / tile_size
        player_iso_x, player_iso_y = self.cart_to_iso(player_gx, player_gy, 0)

        desired_x = self.screen_w / 2 - player_iso_x
        desired_y = self.screen_h / 2 - player_iso_y

        min_iso_x, max_iso_x, min_iso_y, max_iso_y = self._world_iso_bounds(grid_w, grid_h)
        min_off_x = self.screen_w - max_iso_x
        max_off_x = -min_iso_x
        min_off_y = self.screen_h - max_iso_y
        max_off_y = -min_iso_y

        if min_off_x > max_off_x:
            self.offset_x = (min_off_x + max_off_x) / 2
        else:
            self.offset_x = max(min_off_x, min(max_off_x, desired_x))

        if min_off_y > max_off_y:
            self.offset_y = (min_off_y + max_off_y) / 2
        else:
            self.offset_y = max(min_off_y, min(max_off_y, desired_y))

    def visible_chunk_range(
        self,
        chunk_size: int,
        chunks_x: int,
        chunks_y: int,
    ) -> tuple[int, int, int, int]:
        """Return inclusive chunk bounds intersecting screen with one-chunk margin."""
        corners = [
            self.screen_to_grid(0, 0),
            self.screen_to_grid(self.screen_w, 0),
            self.screen_to_grid(0, self.screen_h),
            self.screen_to_grid(self.screen_w, self.screen_h),
        ]
        gx_values = [value[0] for value in corners]
        gy_values = [value[1] for value in corners]

        min_gx = int(min(gx_values)) - chunk_size
        max_gx = int(max(gx_values)) + chunk_size
        min_gy = int(min(gy_values)) - chunk_size
        max_gy = int(max(gy_values)) + chunk_size

        min_cx = max(0, min_gx // chunk_size)
        max_cx = min(chunks_x - 1, max_gx // chunk_size)
        min_cy = max(0, min_gy // chunk_size)
        max_cy = min(chunks_y - 1, max_gy // chunk_size)

        return min_cx, min_cy, max_cx, max_cy

    def is_on_screen(self, screen_x: float, screen_y: float, margin: int = 64) -> bool:
        """Fast viewport visibility check with margin."""
        return (
            -margin <= screen_x <= self.screen_w + margin
            and -margin <= screen_y <= self.screen_h + margin
        )
