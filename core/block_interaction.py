"""Block damage, destruction and regeneration logic for voxel terrain."""

from __future__ import annotations

from collections.abc import Iterable
import random

from config import VOXEL_SETTINGS
from core.physics import ParticlePool
from core.world_grid import BLOCK_HP, BlockType, VoxelGrid


class BlockInteractionSystem:
    """Runtime system handling attacks against voxels and terrain regrowth."""

    def __init__(self, grid: VoxelGrid, particle_pool: ParticlePool):
        self.grid = grid
        self.pool = particle_pool
        self._regen_timer: float = 0.0
        self._regen_queue: list[tuple[int, int, int, BlockType]] = []
        self._damaged: dict[tuple[int, int, int], int] = {}
        self.regen_enabled: bool = VOXEL_SETTINGS.regen_enabled

    def _world_to_grid(self, wx: float, wy: float) -> tuple[int, int]:
        tile_size = self.grid.config.tile_size
        return int(wx // tile_size), int(wy // tile_size)

    def attack_block(
        self,
        wx: float,
        wy: float,
        direction: tuple[int, int],
        attack_range: int,
        damage: int = 1,
    ) -> bool:
        """Damage the first solid block along the attack direction ray."""
        dx, dy = direction
        if dx == 0 and dy == 0:
            return False

        start_gx, start_gy = self._world_to_grid(wx, wy)
        steps = max(1, int(attack_range // self.grid.config.tile_size))

        for step in range(1, steps + 1):
            target_gx = start_gx + dx * step
            target_gy = start_gy + dy * step
            target_gz = self.grid.get_surface_z(target_gx, target_gy)
            if target_gz < 0:
                continue

            block_type, destroyed = self.grid.damage_block(target_gx, target_gy, target_gz, damage)
            if block_type == BlockType.AIR:
                continue

            if destroyed:
                self.pool.spawn_burst(target_gx + 0.5, target_gy + 0.5, target_gz + 0.25, int(block_type), count=4)
                self._damaged.pop((target_gx, target_gy, target_gz), None)
            else:
                self.deform_block(target_gx, target_gy, target_gz)
            return True

        return False

    def projectile_hit_block(self, wx: float, wy: float) -> bool:
        """Damage one block at the projectile world position."""
        gx, gy = self._world_to_grid(wx, wy)
        gz = self.grid.get_surface_z(gx, gy)
        if gz < 0:
            return False

        block_type, destroyed = self.grid.damage_block(gx, gy, gz, damage=1)
        if block_type == BlockType.AIR:
            return False

        if destroyed:
            self.pool.spawn_burst(gx + 0.5, gy + 0.5, gz + 0.25, int(block_type), count=3)
            self._damaged.pop((gx, gy, gz), None)
        else:
            self.deform_block(gx, gy, gz)
        return True

    def deform_block(self, gx: int, gy: int, gz: int) -> None:
        """Track damaged blocks for crack overlays in the renderer."""
        block_type = self.grid.get_block(gx, gy, gz)
        if block_type == BlockType.AIR:
            self._damaged.pop((gx, gy, gz), None)
            return

        max_hp = BLOCK_HP.get(block_type, 0)
        hp = int(self.grid.block_hp[gx, gy, gz])
        if max_hp > 0 and 0 < hp < max_hp:
            self._damaged[(gx, gy, gz)] = hp

    def update_regeneration(
        self,
        dt: float = 1.0,
        occupied_positions: Iterable[tuple[int, int, int]] | None = None,
    ) -> None:
        """Regrow terrain at a slow cadence using adjacency candidates."""
        if not self.regen_enabled:
            return

        self._regen_timer += dt
        if self._regen_timer < VOXEL_SETTINGS.regen_interval:
            return

        self._regen_timer = 0.0
        blocked = set(occupied_positions or ())
        candidates = [
            candidate
            for candidate in self.grid.find_regen_candidates()
            if (candidate[0], candidate[1], candidate[2]) not in blocked
        ]
        if not candidates:
            return

        sample_count = random.randint(1, min(3, len(candidates)))
        for gx, gy, gz, block_type in random.sample(candidates, sample_count):
            if self.grid.place_block(gx, gy, gz, block_type):
                self._damaged.pop((gx, gy, gz), None)

    def get_damaged_blocks(self) -> list[tuple[int, int, int, int]]:
        """Return damaged block coordinates with remaining HP."""
        return [
            (gx, gy, gz, hp)
            for (gx, gy, gz), hp in self._damaged.items()
            if self.grid.get_block(gx, gy, gz) != BlockType.AIR
        ]
