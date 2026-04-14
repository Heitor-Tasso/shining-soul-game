"""Voxel world grid and terrain generation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import random

import numpy as np
from pygame import Rect


class BlockType(IntEnum):
    """Supported block kinds stored in the voxel grid."""

    AIR = 0
    STONE = 1
    DIRT = 2
    GRASS = 3
    WOOD = 4
    SAND = 5


BLOCK_HP: dict[BlockType, int] = {
    BlockType.STONE: 3,
    BlockType.DIRT: 1,
    BlockType.GRASS: 1,
    BlockType.WOOD: 2,
    BlockType.SAND: 1,
}


@dataclass(frozen=True)
class GridConfig:
    """Static configuration for the world voxel grid."""

    grid_w: int = 128
    grid_h: int = 96
    grid_d: int = 8
    tile_size: int = 32
    chunk_size: int = 16


class VoxelGrid:
    """Mutable voxel world with chunk-dirty tracking for cached rendering."""

    def __init__(self, config: GridConfig | None = None):
        self.config = config or GridConfig()
        c = self.config
        self.blocks = np.zeros((c.grid_w, c.grid_h, c.grid_d), dtype=np.uint8)
        self.block_hp = np.zeros((c.grid_w, c.grid_h, c.grid_d), dtype=np.int16)
        chunks_x = (c.grid_w + c.chunk_size - 1) // c.chunk_size
        chunks_y = (c.grid_h + c.chunk_size - 1) // c.chunk_size
        self.chunks_dirty = np.ones((chunks_x, chunks_y), dtype=bool)

    def _in_bounds(self, gx: int, gy: int, gz: int) -> bool:
        c = self.config
        return 0 <= gx < c.grid_w and 0 <= gy < c.grid_h and 0 <= gz < c.grid_d

    def _mark_chunk_dirty(self, gx: int, gy: int) -> None:
        c = self.config
        cx = gx // c.chunk_size
        cy = gy // c.chunk_size
        if 0 <= cx < self.chunks_dirty.shape[0] and 0 <= cy < self.chunks_dirty.shape[1]:
            self.chunks_dirty[cx, cy] = True

    def _max_hp_for(self, block_type: BlockType) -> int:
        return BLOCK_HP.get(block_type, 0)

    def init_flat_world(self) -> None:
        """Initialize a baseline world with floor grass and stone borders."""
        c = self.config
        self.blocks.fill(0)
        self.block_hp.fill(0)
        self.blocks[:, :, 0] = int(BlockType.GRASS)
        self.block_hp[:, :, 0] = self._max_hp_for(BlockType.GRASS)

        if c.grid_d > 1:
            for gx in range(c.grid_w):
                self.set_block(gx, 0, 1, BlockType.STONE)
                self.set_block(gx, c.grid_h - 1, 1, BlockType.STONE)
            for gy in range(c.grid_h):
                self.set_block(0, gy, 1, BlockType.STONE)
                self.set_block(c.grid_w - 1, gy, 1, BlockType.STONE)

        self.chunks_dirty[:, :] = True

    def init_empty_world(self) -> None:
        """Reset the voxel layer to fully empty, preserving legacy map visuals."""
        self.blocks.fill(0)
        self.block_hp.fill(0)
        self.chunks_dirty[:, :] = True

    def get_block(self, gx: int, gy: int, gz: int) -> BlockType:
        """Return block type at coordinates; outside grid is treated as air."""
        if not self._in_bounds(gx, gy, gz):
            return BlockType.AIR
        return BlockType(int(self.blocks[gx, gy, gz]))

    def set_block(self, gx: int, gy: int, gz: int, block_type: BlockType) -> None:
        """Set block type and hp and invalidate owning chunk."""
        if not self._in_bounds(gx, gy, gz):
            return
        self.blocks[gx, gy, gz] = int(block_type)
        self.block_hp[gx, gy, gz] = self._max_hp_for(block_type)
        self._mark_chunk_dirty(gx, gy)

    def damage_block(self, gx: int, gy: int, gz: int, damage: int = 1) -> tuple[BlockType, bool]:
        """Apply progressive block damage and return (type, destroyed)."""
        if not self._in_bounds(gx, gy, gz):
            return BlockType.AIR, False

        block_type = self.get_block(gx, gy, gz)
        if block_type == BlockType.AIR:
            return BlockType.AIR, False

        if self.block_hp[gx, gy, gz] <= 0:
            self.block_hp[gx, gy, gz] = self._max_hp_for(block_type)

        self.block_hp[gx, gy, gz] -= max(1, int(damage))
        self._mark_chunk_dirty(gx, gy)
        if self.block_hp[gx, gy, gz] <= 0:
            self.blocks[gx, gy, gz] = int(BlockType.AIR)
            self.block_hp[gx, gy, gz] = 0
            return block_type, True
        return block_type, False

    def destroy_block(self, gx: int, gy: int, gz: int) -> BlockType:
        """Force a block removal and return its previous type."""
        old_type = self.get_block(gx, gy, gz)
        if old_type == BlockType.AIR:
            return old_type
        self.set_block(gx, gy, gz, BlockType.AIR)
        return old_type

    def place_block(self, gx: int, gy: int, gz: int, block_type: BlockType) -> bool:
        """Place a block only when target is currently air."""
        if not self._in_bounds(gx, gy, gz):
            return False
        if self.get_block(gx, gy, gz) != BlockType.AIR:
            return False
        self.set_block(gx, gy, gz, block_type)
        return True

    def get_surface_z(self, gx: int, gy: int) -> int:
        """Return highest non-air z index for a grid column, or -1 if empty."""
        c = self.config
        if not (0 <= gx < c.grid_w and 0 <= gy < c.grid_h):
            return -1
        for gz in range(c.grid_d - 1, -1, -1):
            if self.blocks[gx, gy, gz] != int(BlockType.AIR):
                return gz
        return -1

    def get_collision_rects_near(self, wx: float, wy: float, radius: float = 200) -> list[Rect]:
        """Return nearby solid collision rects in world coordinates."""
        c = self.config
        center_gx = int(wx // c.tile_size)
        center_gy = int(wy // c.tile_size)
        delta = int(radius // c.tile_size) + 2

        min_gx = max(0, center_gx - delta)
        max_gx = min(c.grid_w - 1, center_gx + delta)
        min_gy = max(0, center_gy - delta)
        max_gy = min(c.grid_h - 1, center_gy + delta)

        rects: list[Rect] = []
        for gx in range(min_gx, max_gx + 1):
            for gy in range(min_gy, max_gy + 1):
                if self.get_surface_z(gx, gy) >= 1:
                    rects.append(Rect(gx * c.tile_size, gy * c.tile_size, c.tile_size, c.tile_size))
        return rects

    def generate_terrain(self, tree_positions: list[tuple[int, int]]) -> None:
        """Generate baseline terrain, tree pillars and destructible stone clusters."""
        self.init_flat_world()
        c = self.config

        for tree_x, tree_y in tree_positions:
            gx = int(tree_x // c.tile_size)
            gy = int(tree_y // c.tile_size)
            for z in range(1, min(4, c.grid_d)):
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        tx, ty = gx + dx, gy + dy
                        if 0 <= tx < c.grid_w and 0 <= ty < c.grid_h:
                            self.set_block(tx, ty, z, BlockType.WOOD)

        rng = random.Random(1337)
        cluster_count = max(10, min(30, (c.grid_w * c.grid_h) // 512))
        for _ in range(cluster_count):
            cgx = rng.randint(2, c.grid_w - 3)
            cgy = rng.randint(2, c.grid_h - 3)
            cluster_size = rng.randint(2, 5)
            for _ in range(cluster_size):
                ox = rng.randint(-1, 1)
                oy = rng.randint(-1, 1)
                tx, ty = cgx + ox, cgy + oy
                if 0 <= tx < c.grid_w and 0 <= ty < c.grid_h and self.get_surface_z(tx, ty) <= 1:
                    self.set_block(tx, ty, 1, BlockType.STONE)

        dirt_patches = max(20, min(80, (c.grid_w * c.grid_h) // 256))
        for _ in range(dirt_patches):
            px = rng.randint(1, c.grid_w - 2)
            py = rng.randint(1, c.grid_h - 2)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    tx, ty = px + dx, py + dy
                    if 0 <= tx < c.grid_w and 0 <= ty < c.grid_h and self.get_block(tx, ty, 0) == BlockType.GRASS:
                        if rng.random() < 0.6:
                            self.set_block(tx, ty, 0, BlockType.DIRT)

        self.chunks_dirty[:, :] = True

    def get_neighbors(self, gx: int, gy: int, gz: int) -> dict[str, BlockType]:
        """Return block types in six cardinal neighboring directions."""
        return {
            "north": self.get_block(gx, gy - 1, gz),
            "south": self.get_block(gx, gy + 1, gz),
            "east": self.get_block(gx + 1, gy, gz),
            "west": self.get_block(gx - 1, gy, gz),
            "above": self.get_block(gx, gy, gz + 1),
            "below": self.get_block(gx, gy, gz - 1),
        }

    def find_regen_candidates(self) -> list[tuple[int, int, int, BlockType]]:
        """Return air positions adjacent to existing blocks for gradual regrowth."""
        c = self.config
        candidates: list[tuple[int, int, int, BlockType]] = []

        for gx in range(c.grid_w):
            for gy in range(c.grid_h):
                for gz in range(1, c.grid_d):
                    if self.get_block(gx, gy, gz) != BlockType.AIR:
                        continue
                    neighbors = self.get_neighbors(gx, gy, gz)
                    neighbor_types = [
                        block_type
                        for block_type in neighbors.values()
                        if block_type != BlockType.AIR
                    ]
                    if not neighbor_types:
                        continue
                    preferred_type = next((b for b in neighbor_types if b in BLOCK_HP), BlockType.DIRT)
                    candidates.append((gx, gy, gz, preferred_type))
        return candidates
