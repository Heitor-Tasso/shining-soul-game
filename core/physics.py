"""Simple particle physics with object pooling for voxel debris effects."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random

from core.world_grid import VoxelGrid

GRAVITY: float = -9.8
BOUNCE_DAMPING: float = 0.3
FRICTION: float = 0.7
STATIC_AGE: float = 120.0
DESPAWN_AGE: float = 600.0


@dataclass
class Particle:
    """Single debris element updated by the particle pool."""

    active: bool = False
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0
    age: float = 0.0
    is_static: bool = False
    block_type: int = 0
    size: float = 4.0
    rotation: float = 0.0


class ParticlePool:
    """Fixed-size particle allocator that avoids per-frame object churn."""

    def __init__(self, capacity: int = 100):
        self.particles = [Particle() for _ in range(capacity)]
        self._free_indices = list(range(capacity))
        self.active_count = 0

    def _deactivate(self, index: int) -> None:
        particle = self.particles[index]
        if not particle.active:
            return
        particle.active = False
        particle.is_static = False
        particle.age = 0.0
        particle.vx = 0.0
        particle.vy = 0.0
        particle.vz = 0.0
        self._free_indices.append(index)
        self.active_count -= 1

    def spawn(self, x: float, y: float, z: float, block_type: int) -> Particle | None:
        """Activate one particle from the pool, or return None when exhausted."""
        if not self._free_indices:
            return None

        index = self._free_indices.pop()
        particle = self.particles[index]

        angle = random.uniform(0.0, 2.0 * math.pi)
        speed_xy = random.uniform(0.5, 1.5)
        particle.active = True
        particle.x = float(x)
        particle.y = float(y)
        particle.z = float(z)
        particle.vx = math.cos(angle) * speed_xy
        particle.vy = math.sin(angle) * speed_xy
        particle.vz = random.uniform(1.0, 2.5)
        particle.age = 0.0
        particle.is_static = False
        particle.block_type = int(block_type)
        particle.size = random.uniform(3.0, 5.0)
        particle.rotation = random.uniform(0.0, 360.0)
        self.active_count += 1
        return particle

    def spawn_burst(self, x: float, y: float, z: float, block_type: int, count: int = 4) -> int:
        """Spawn a small burst of 3-5 particles around one impact point."""
        target = random.randint(max(1, count - 1), count + 1)
        spawned = 0
        for _ in range(target):
            particle = self.spawn(
                x + random.uniform(-0.2, 0.2),
                y + random.uniform(-0.2, 0.2),
                z,
                block_type,
            )
            if particle is not None:
                spawned += 1
        return spawned

    def update(self, grid: VoxelGrid | None = None) -> None:
        """Advance all active particles one simulation step."""
        for index, particle in enumerate(self.particles):
            if not particle.active:
                continue

            particle.age += 1.0
            if not particle.is_static:
                particle.vz += GRAVITY / 60.0
                particle.x += particle.vx
                particle.y += particle.vy
                particle.z += particle.vz

                floor_z = 0.0
                if grid is not None:
                    floor_query = grid.get_surface_z(int(particle.x), int(particle.y))
                    if floor_query >= 0:
                        floor_z = float(floor_query)

                if particle.z <= floor_z:
                    particle.z = floor_z
                    if abs(particle.vz) > 0.02:
                        particle.vz *= -BOUNCE_DAMPING
                        particle.vx *= FRICTION
                        particle.vy *= FRICTION
                    else:
                        particle.vz = 0.0

                if particle.age >= STATIC_AGE:
                    particle.is_static = True
                    particle.vx = 0.0
                    particle.vy = 0.0
                    particle.vz = 0.0

                particle.rotation = (particle.rotation + 8.0) % 360.0

            if particle.age >= DESPAWN_AGE:
                self._deactivate(index)

    def active_particles(self) -> list[Particle]:
        """Return active particles for rendering."""
        return [particle for particle in self.particles if particle.active]

    def clear_all(self) -> None:
        """Deactivate all particles and fully reset allocator state."""
        for particle in self.particles:
            particle.active = False
            particle.is_static = False
            particle.age = 0.0
        self._free_indices = list(range(len(self.particles)))
        self.active_count = 0

    def clear_non_static(self) -> None:
        """Deactivate only moving particles and keep static debris as decoration."""
        for index, particle in enumerate(self.particles):
            if particle.active and not particle.is_static:
                self._deactivate(index)
