"""Isometric voxel rendering, chunk caching and debug overlays."""

from __future__ import annotations

from collections.abc import Iterable

import pygame

from core.isometric import TILE_H, TILE_W, Z_STEP, IsometricCamera, depth_sort_key
from core.physics import DESPAWN_AGE, Particle
from core.world_grid import BLOCK_HP, BlockType, VoxelGrid

BLOCK_COLORS = {
    BlockType.STONE: (128, 128, 128),
    BlockType.DIRT: (139, 90, 43),
    BlockType.GRASS: (34, 139, 34),
    BlockType.WOOD: (160, 82, 45),
    BlockType.SAND: (210, 180, 120),
}

FACE_SHADING = {
    "top": 1.0,
    "left": 0.7,
    "right": 0.85,
}

DEPTH_SHADE_STEP = 40
CRACK_OVERLAY_ALPHA = 120


def _shade_color(color: tuple[int, int, int], factor: float, shade: int = 0) -> tuple[int, int, int]:
    shaded = []
    for channel in color:
        value = int(channel * factor) - shade
        shaded.append(max(0, min(255, value)))
    return tuple(shaded)


class TileRenderer:
    """Builds and caches per-block tile surfaces."""

    def __init__(self):
        self._surface_cache: dict[tuple[int, int, bool], pygame.Surface] = {}

    def get_tile_surface(self, block_type: int, shade: int = 0, cracked: bool = False) -> pygame.Surface:
        """Return cached isometric tile surface for one block type and style."""
        cache_key = (int(block_type), int(shade), bool(cracked))
        if cache_key in self._surface_cache:
            return self._surface_cache[cache_key]

        tile_surface = pygame.Surface((TILE_W, TILE_H + Z_STEP), pygame.SRCALPHA)
        enum_type = BlockType(int(block_type))
        base_color = BLOCK_COLORS.get(enum_type, (255, 0, 255))

        top_color = _shade_color(base_color, FACE_SHADING["top"], shade)
        left_color = _shade_color(base_color, FACE_SHADING["left"], shade)
        right_color = _shade_color(base_color, FACE_SHADING["right"], shade)

        top_poly = [(TILE_W // 2, 0), (TILE_W, TILE_H // 2), (TILE_W // 2, TILE_H), (0, TILE_H // 2)]
        left_poly = [(0, TILE_H // 2), (TILE_W // 2, TILE_H), (TILE_W // 2, TILE_H + Z_STEP), (0, TILE_H // 2 + Z_STEP)]
        right_poly = [
            (TILE_W // 2, TILE_H),
            (TILE_W, TILE_H // 2),
            (TILE_W, TILE_H // 2 + Z_STEP),
            (TILE_W // 2, TILE_H + Z_STEP),
        ]

        pygame.draw.polygon(tile_surface, left_color, left_poly)
        pygame.draw.polygon(tile_surface, right_color, right_poly)
        pygame.draw.polygon(tile_surface, top_color, top_poly)

        if cracked:
            crack_color = (0, 0, 0, CRACK_OVERLAY_ALPHA)
            pygame.draw.line(tile_surface, crack_color, (TILE_W // 2, 4), (6, TILE_H // 2), 2)
            pygame.draw.line(tile_surface, crack_color, (TILE_W // 2 + 2, 6), (TILE_W - 6, TILE_H // 2 + 2), 2)

        self._surface_cache[cache_key] = tile_surface
        return tile_surface

    def clear_cache(self) -> None:
        """Drop all cached tile surfaces."""
        self._surface_cache.clear()


class ChunkCache:
    """Caches pre-rendered chunk surfaces keyed by chunk coordinate."""

    def __init__(self, grid: VoxelGrid, tile_renderer: TileRenderer):
        self.grid = grid
        self.tile_renderer = tile_renderer
        self._cache: dict[tuple[int, int], pygame.Surface | None] = {}
        self._origins: dict[tuple[int, int], tuple[int, int]] = {}

    def _rebuild_chunk(self, chunk_x: int, chunk_y: int) -> None:
        c = self.grid.config
        start_x = chunk_x * c.chunk_size
        end_x = min(c.grid_w, start_x + c.chunk_size)
        start_y = chunk_y * c.chunk_size
        end_y = min(c.grid_h, start_y + c.chunk_size)

        blocks_to_draw: list[tuple[float, int, int, int, BlockType, bool]] = []
        min_x = 10**9
        min_y = 10**9
        max_x = -10**9
        max_y = -10**9

        for gx in range(start_x, end_x):
            for gy in range(start_y, end_y):
                for gz in range(c.grid_d):
                    block_type = self.grid.get_block(gx, gy, gz)
                    if block_type == BlockType.AIR:
                        continue

                    max_hp = BLOCK_HP.get(block_type, 0)
                    hp = int(self.grid.block_hp[gx, gy, gz])
                    cracked = max_hp > 0 and 0 < hp < max_hp
                    blocks_to_draw.append((depth_sort_key(gx, gy, gz), gx, gy, gz, block_type, cracked))

                    iso_x = int((gx - gy) * (TILE_W / 2)) - TILE_W // 2
                    iso_y = int((gx + gy) * (TILE_H / 2) - gz * Z_STEP)
                    min_x = min(min_x, iso_x)
                    min_y = min(min_y, iso_y)
                    max_x = max(max_x, iso_x + TILE_W)
                    max_y = max(max_y, iso_y + TILE_H + Z_STEP)

        key = (chunk_x, chunk_y)
        if not blocks_to_draw:
            self._cache[key] = None
            self._origins[key] = (0, 0)
            self.grid.chunks_dirty[chunk_x, chunk_y] = False
            return

        width = max(1, max_x - min_x)
        height = max(1, max_y - min_y)
        chunk_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        blocks_to_draw.sort(key=lambda item: item[0])
        for _depth, gx, gy, gz, block_type, cracked in blocks_to_draw:
            blit_x = int((gx - gy) * (TILE_W / 2)) - TILE_W // 2 - min_x
            blit_y = int((gx + gy) * (TILE_H / 2) - gz * Z_STEP) - min_y
            tile = self.tile_renderer.get_tile_surface(int(block_type), shade=0, cracked=cracked)
            chunk_surface.blit(tile, (blit_x, blit_y))

        self._cache[key] = chunk_surface
        self._origins[key] = (min_x, min_y)
        self.grid.chunks_dirty[chunk_x, chunk_y] = False

    def get_chunk_surface(self, chunk_x: int, chunk_y: int) -> pygame.Surface | None:
        """Return chunk surface, rebuilding when marked dirty."""
        key = (chunk_x, chunk_y)
        if key not in self._cache or bool(self.grid.chunks_dirty[chunk_x, chunk_y]):
            self._rebuild_chunk(chunk_x, chunk_y)
        return self._cache.get(key)

    def get_chunk_origin(self, chunk_x: int, chunk_y: int) -> tuple[int, int]:
        """Return world isometric origin used by cached chunk surface."""
        if (chunk_x, chunk_y) not in self._origins:
            self.get_chunk_surface(chunk_x, chunk_y)
        return self._origins.get((chunk_x, chunk_y), (0, 0))

    def invalidate(self, chunk_x: int, chunk_y: int) -> None:
        """Invalidate a single chunk entry."""
        self._cache.pop((chunk_x, chunk_y), None)
        self._origins.pop((chunk_x, chunk_y), None)
        if 0 <= chunk_x < self.grid.chunks_dirty.shape[0] and 0 <= chunk_y < self.grid.chunks_dirty.shape[1]:
            self.grid.chunks_dirty[chunk_x, chunk_y] = True

    def invalidate_all(self) -> None:
        """Invalidate all chunk surfaces."""
        self._cache.clear()
        self._origins.clear()
        self.grid.chunks_dirty[:, :] = True


class VoxelWorldRenderer:
    """Top-level renderer for chunks, particles and optional overlays."""

    def __init__(self, grid: VoxelGrid, camera: IsometricCamera):
        self.grid = grid
        self.camera = camera
        self.tile_renderer = TileRenderer()
        self.chunk_cache = ChunkCache(grid, self.tile_renderer)
        self.last_rendered_chunks = 0
        self.last_world_renderables = 0

    def _visible_chunk_bounds(self) -> tuple[int, int, int, int]:
        chunks_x = self.grid.chunks_dirty.shape[0]
        chunks_y = self.grid.chunks_dirty.shape[1]
        return self.camera.visible_chunk_range(
            self.grid.config.chunk_size,
            chunks_x,
            chunks_y,
        )

    def collect_depth_sorted_world_renderables(self) -> list[tuple[float, str, pygame.Surface, int, int]]:
        """Collect visible world tiles as depth-sorted renderables for global painter pass."""
        min_cx, min_cy, max_cx, max_cy = self._visible_chunk_bounds()
        c = self.grid.config

        renderables: list[tuple[float, str, pygame.Surface, int, int]] = []
        self.last_rendered_chunks = (max_cx - min_cx + 1) * (max_cy - min_cy + 1)

        min_gx = max(0, min_cx * c.chunk_size)
        max_gx = min(c.grid_w - 1, (max_cx + 1) * c.chunk_size - 1)
        min_gy = max(0, min_cy * c.chunk_size)
        max_gy = min(c.grid_h - 1, (max_cy + 1) * c.chunk_size - 1)

        start_diag = min_gx + min_gy
        end_diag = max_gx + max_gy

        # Iterate diagonals to naturally emit renderables in depth_sort_key order.
        for diag in range(start_diag, end_diag + 1):
            diag_renderables: list[tuple[float, str, pygame.Surface, int, int]] = []
            gx_start = max(min_gx, diag - max_gy)
            gx_end = min(max_gx, diag - min_gy)
            for gx in range(gx_start, gx_end + 1):
                gy = diag - gx
                surface_z = self.grid.get_surface_z(gx, gy)
                if surface_z < 0:
                    continue

                for gz in range(surface_z + 1):
                    block_type = self.grid.get_block(gx, gy, gz)
                    if block_type == BlockType.AIR:
                        continue

                    sx, sy = self.camera.grid_to_screen(gx, gy, gz)
                    if not self.camera.is_on_screen(sx, sy + TILE_H, margin=128):
                        continue

                    max_hp = BLOCK_HP.get(block_type, 0)
                    hp = int(self.grid.block_hp[gx, gy, gz])
                    cracked = max_hp > 0 and 0 < hp < max_hp
                    tile = self.tile_renderer.get_tile_surface(int(block_type), shade=0, cracked=cracked)
                    diag_renderables.append(
                        (depth_sort_key(gx, gy, gz), "block", tile, int(sx - TILE_W // 2), int(sy))
                    )

                neighbor_top = max(
                    self.grid.get_surface_z(gx - 1, gy),
                    self.grid.get_surface_z(gx + 1, gy),
                    self.grid.get_surface_z(gx, gy - 1),
                    self.grid.get_surface_z(gx, gy + 1),
                )
                if neighbor_top - surface_z >= 1:
                    for z in range(surface_z, neighbor_top):
                        block_type = self.grid.get_block(gx, gy, z)
                        if block_type == BlockType.AIR:
                            continue
                        sx, sy = self.camera.grid_to_screen(gx, gy, z)
                        if not self.camera.is_on_screen(sx, sy + TILE_H, margin=128):
                            continue
                        shade = min(200, DEPTH_SHADE_STEP * (neighbor_top - z))
                        tile = self.tile_renderer.get_tile_surface(int(block_type), shade=shade, cracked=False)
                        diag_renderables.append(
                            (
                                depth_sort_key(gx, gy, z) + 0.001,
                                "block",
                                tile,
                                int(sx - TILE_W // 2),
                                int(sy),
                            )
                        )

            diag_renderables.sort(key=lambda item: item[0])
            renderables.extend(diag_renderables)

        self.last_world_renderables = len(renderables)
        return renderables

    def render_world(self, screen: pygame.Surface) -> None:
        """Render visible chunk surfaces based on camera culling bounds."""
        min_cx, min_cy, max_cx, max_cy = self._visible_chunk_bounds()

        self.last_rendered_chunks = 0
        for chunk_x in range(min_cx, max_cx + 1):
            for chunk_y in range(min_cy, max_cy + 1):
                chunk_surface = self.chunk_cache.get_chunk_surface(chunk_x, chunk_y)
                if chunk_surface is None:
                    continue
                origin_x, origin_y = self.chunk_cache.get_chunk_origin(chunk_x, chunk_y)
                screen.blit(chunk_surface, (origin_x + self.camera.offset_x, origin_y + self.camera.offset_y))
                self.last_rendered_chunks += 1

        # Secondary pass: darken exposed inner layers where neighbor columns are higher.
        c = self.grid.config
        min_gx = max(0, min_cx * c.chunk_size)
        max_gx = min(c.grid_w - 1, (max_cx + 1) * c.chunk_size - 1)
        min_gy = max(0, min_cy * c.chunk_size)
        max_gy = min(c.grid_h - 1, (max_cy + 1) * c.chunk_size - 1)

        for gx in range(min_gx, max_gx + 1):
            for gy in range(min_gy, max_gy + 1):
                surface_z = self.grid.get_surface_z(gx, gy)
                if surface_z < 0:
                    continue

                neighbor_top = max(
                    self.grid.get_surface_z(gx - 1, gy),
                    self.grid.get_surface_z(gx + 1, gy),
                    self.grid.get_surface_z(gx, gy - 1),
                    self.grid.get_surface_z(gx, gy + 1),
                )
                if neighbor_top - surface_z >= 1:
                    self.render_hole_depth(screen, gx, gy, neighbor_top)

    def render_hole_depth(self, screen: pygame.Surface, gx: int, gy: int, surface_z: int) -> None:
        """Render darker top layers to suggest depth inside exposed pits."""
        current_surface = self.grid.get_surface_z(gx, gy)
        if surface_z <= 0 or current_surface < 0 or surface_z <= current_surface:
            return

        for z in range(surface_z - 1, current_surface - 1, -1):
            block_type = self.grid.get_block(gx, gy, z)
            if block_type == BlockType.AIR:
                continue
            depth = surface_z - z
            sx, sy = self.camera.grid_to_screen(gx, gy, z)
            tile = self.tile_renderer.get_tile_surface(
                int(block_type),
                shade=min(200, DEPTH_SHADE_STEP * depth),
                cracked=False,
            )
            screen.blit(tile, (int(sx - TILE_W // 2), int(sy)))

    def render_particles(self, screen: pygame.Surface, particles: Iterable[Particle]) -> None:
        """Render debris particles in isometric coordinates."""
        ordered = sorted(particles, key=lambda p: depth_sort_key(p.x, p.y, p.z))
        for particle in ordered:
            sx, sy = self.camera.grid_to_screen(particle.x, particle.y, particle.z)
            if not self.camera.is_on_screen(sx, sy, margin=96):
                continue

            color = BLOCK_COLORS.get(BlockType(particle.block_type), (255, 255, 255))
            age_ratio = min(1.0, particle.age / DESPAWN_AGE)
            size = max(1, int(particle.size * (1.0 - age_ratio * 0.6)))
            alpha = 150 if particle.is_static else 255

            particle_surface = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            points = [
                (size + 1, 1),
                (size * 2 + 1, size + 1),
                (size + 1, size * 2 + 1),
                (1, size + 1),
            ]
            pygame.draw.polygon(particle_surface, (*color, alpha), points)
            screen.blit(particle_surface, (int(sx - size), int(sy - size)))

    def render_debug_overlay(
        self,
        screen: pygame.Surface,
        show_grid: bool = False,
        show_chunks: bool = False,
        show_collision: bool = False,
    ) -> None:
        """Render visual diagnostics overlays."""
        if show_grid:
            for gx in range(0, self.grid.config.grid_w, 2):
                for gy in range(0, self.grid.config.grid_h, 2):
                    sx, sy = self.camera.grid_to_screen(gx, gy, 0)
                    if self.camera.is_on_screen(sx, sy, margin=8):
                        diamond = [
                            (sx, sy),
                            (sx + TILE_W / 2, sy + TILE_H / 2),
                            (sx, sy + TILE_H),
                            (sx - TILE_W / 2, sy + TILE_H / 2),
                        ]
                        pygame.draw.lines(screen, (30, 80, 200), True, diamond, 1)

        if show_chunks:
            c = self.grid.config
            for cx in range(self.grid.chunks_dirty.shape[0]):
                for cy in range(self.grid.chunks_dirty.shape[1]):
                    gx0 = cx * c.chunk_size
                    gy0 = cy * c.chunk_size
                    gx1 = min(c.grid_w, gx0 + c.chunk_size)
                    gy1 = min(c.grid_h, gy0 + c.chunk_size)

                    p0 = self.camera.grid_to_screen(gx0, gy0, 0)
                    p1 = self.camera.grid_to_screen(gx1, gy0, 0)
                    p2 = self.camera.grid_to_screen(gx1, gy1, 0)
                    p3 = self.camera.grid_to_screen(gx0, gy1, 0)
                    pygame.draw.lines(screen, (220, 180, 40), True, [p0, p1, p2, p3], 1)

        if show_collision:
            center_gx, center_gy = self.camera.screen_to_grid(self.camera.screen_w / 2, self.camera.screen_h / 2)
            tile = self.grid.config.tile_size
            rects = self.grid.get_collision_rects_near(center_gx * tile, center_gy * tile, radius=300)
            for rect in rects:
                gx = rect.x / tile
                gy = rect.y / tile
                sx, sy = self.camera.grid_to_screen(gx, gy, 1)
                pygame.draw.circle(screen, (255, 0, 0), (int(sx), int(sy + TILE_H * 0.5)), 3)
