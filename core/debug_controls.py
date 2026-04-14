"""Runtime debug keybinds and HUD for voxel systems."""

from __future__ import annotations

import pygame

from core.block_interaction import BlockInteractionSystem
from core.physics import ParticlePool
from core.voxel_renderer import VoxelWorldRenderer
from core.world_grid import BlockType, VoxelGrid


class DebugControls:
    """Manage keyboard toggles and quick runtime test actions."""

    def __init__(
        self,
        grid: VoxelGrid,
        pool: ParticlePool,
        interaction: BlockInteractionSystem,
        renderer: VoxelWorldRenderer,
        terrain_tree_positions: list[tuple[int, int]] | None = None,
    ):
        self.grid = grid
        self.pool = pool
        self.interaction = interaction
        self.renderer = renderer
        self.enabled = True

        self.show_grid_overlay = False
        self.show_chunk_borders = False
        self.show_collision_rects = False
        self.show_fps_counter = True
        self.show_particle_count = True
        self.show_profiler = False
        self.show_command_help = True
        self.god_mode = False
        self.instant_destroy = False
        self.physics_paused = False
        self.use_voxel_view = False
        self.selected_block_type = BlockType.STONE
        self.zoom_levels: tuple[float, ...] = (0.75, 1.0, 1.25, 1.5)
        self.zoom_index: int = 1
        self.zoom_factor: float = self.zoom_levels[self.zoom_index]

        self.player_world_x = 0.0
        self.player_world_y = 0.0
        self.player_direction = (1, 0)
        self._terrain_tree_positions = list(terrain_tree_positions or [])
        self._profile_latest: dict[str, float] = {}
        self._profile_smoothed: dict[str, float] = {}

    def set_terrain_seed_positions(self, positions: list[tuple[int, int]]) -> None:
        """Update terrain seed points used for full debug world reset."""
        self._terrain_tree_positions = list(positions)

    def set_player_context(self, world_x: float, world_y: float, direction: tuple[int, int]) -> None:
        """Update player state consumed by debug actions."""
        self.player_world_x = world_x
        self.player_world_y = world_y
        if direction != (0, 0):
            self.player_direction = direction

    def set_frame_profile(self, profile_ms: dict[str, float], alpha: float = 0.25) -> None:
        """Store and smooth per-frame profiling data for HUD display."""
        self._profile_latest = dict(profile_ms)
        for key, value in profile_ms.items():
            previous = self._profile_smoothed.get(key, value)
            self._profile_smoothed[key] = previous * (1.0 - alpha) + value * alpha

    def clear_frame_profile(self) -> None:
        """Clear profiler accumulators, usually on full game reset."""
        self._profile_latest.clear()
        self._profile_smoothed.clear()

    def _place_in_front_of_player(self) -> None:
        gx = int(self.player_world_x // self.grid.config.tile_size)
        gy = int(self.player_world_y // self.grid.config.tile_size)
        tx = gx + self.player_direction[0]
        ty = gy + self.player_direction[1]
        tz = max(1, self.grid.get_surface_z(tx, ty) + 1)
        self.grid.place_block(tx, ty, tz, self.selected_block_type)

    def _destroy_area_around_player(self, radius: int = 3) -> None:
        gx = int(self.player_world_x // self.grid.config.tile_size)
        gy = int(self.player_world_y // self.grid.config.tile_size)
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                tx, ty = gx + dx, gy + dy
                z = self.grid.get_surface_z(tx, ty)
                if z >= 1:
                    self.grid.destroy_block(tx, ty, z)

    def _key_just_pressed(self, key_code: int, keys, prev_keys) -> bool:
        """Return True only on the key-down edge for one frame."""
        def _is_pressed(state, code: int) -> bool:
            if state is None:
                return False
            try:
                return bool(state[code])
            except (IndexError, KeyError, TypeError):
                return False

        return _is_pressed(keys, key_code) and not _is_pressed(prev_keys, key_code)

    def process_input(self, keys, prev_keys) -> None:
        """Handle one-frame debug key actions and toggles."""
        if not self.enabled:
            return

        if self._key_just_pressed(pygame.K_F1, keys, prev_keys):
            self.show_grid_overlay = not self.show_grid_overlay
        if self._key_just_pressed(pygame.K_F2, keys, prev_keys):
            self.show_chunk_borders = not self.show_chunk_borders
        if self._key_just_pressed(pygame.K_F3, keys, prev_keys):
            self.show_collision_rects = not self.show_collision_rects
        if self._key_just_pressed(pygame.K_F4, keys, prev_keys):
            self.show_fps_counter = not self.show_fps_counter
        if self._key_just_pressed(pygame.K_F5, keys, prev_keys):
            self.show_particle_count = not self.show_particle_count
        if self._key_just_pressed(pygame.K_F6, keys, prev_keys):
            self.god_mode = not self.god_mode
        if self._key_just_pressed(pygame.K_F7, keys, prev_keys):
            self.instant_destroy = not self.instant_destroy

        if self._key_just_pressed(pygame.K_F8, keys, prev_keys):
            gx = self.player_world_x / self.grid.config.tile_size
            gy = self.player_world_y / self.grid.config.tile_size
            gz = max(1, self.grid.get_surface_z(int(gx), int(gy)) + 1)
            self.pool.spawn_burst(gx, gy, gz, int(self.selected_block_type), count=5)
        if self._key_just_pressed(pygame.K_F9, keys, prev_keys):
            self.interaction.update_regeneration(dt=10_000.0)
        if self._key_just_pressed(pygame.K_F10, keys, prev_keys):
            self._place_in_front_of_player()
        if self._key_just_pressed(pygame.K_F11, keys, prev_keys):
            self._destroy_area_around_player(radius=3)
        if self._key_just_pressed(pygame.K_F12, keys, prev_keys):
            self.grid.init_empty_world()
            self.renderer.chunk_cache.invalidate_all()
            self.pool.clear_all()

        if self._key_just_pressed(pygame.K_1, keys, prev_keys):
            self.selected_block_type = BlockType.STONE
        if self._key_just_pressed(pygame.K_2, keys, prev_keys):
            self.selected_block_type = BlockType.DIRT
        if self._key_just_pressed(pygame.K_3, keys, prev_keys):
            self.selected_block_type = BlockType.GRASS
        if self._key_just_pressed(pygame.K_4, keys, prev_keys):
            self.selected_block_type = BlockType.WOOD
        if self._key_just_pressed(pygame.K_5, keys, prev_keys):
            self.selected_block_type = BlockType.SAND

        if self._key_just_pressed(pygame.K_g, keys, prev_keys):
            self.interaction.regen_enabled = not self.interaction.regen_enabled
        if self._key_just_pressed(pygame.K_p, keys, prev_keys):
            self.physics_paused = not self.physics_paused
        if self._key_just_pressed(pygame.K_c, keys, prev_keys):
            self.pool.clear_all()
        if self._key_just_pressed(pygame.K_TAB, keys, prev_keys):
            self.zoom_index = (self.zoom_index + 1) % len(self.zoom_levels)
            self.zoom_factor = self.zoom_levels[self.zoom_index]
        if self._key_just_pressed(pygame.K_t, keys, prev_keys):
            self.show_profiler = not self.show_profiler
        if self._key_just_pressed(pygame.K_v, keys, prev_keys):
            self.use_voxel_view = not self.use_voxel_view
        if self._key_just_pressed(pygame.K_h, keys, prev_keys):
            self.show_command_help = not self.show_command_help

    def render_hud(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        """Render debug telemetry in the top-left corner."""
        font_obj = pygame.font.Font(None, 20)
        lines: list[str] = []
        if self.show_fps_counter:
            lines.append(f"FPS: {clock.get_fps():.1f}")
        if self.show_particle_count:
            lines.append(f"Particles: {self.pool.active_count}/{len(self.pool.particles)}")
        lines.append(f"Chunks draw: {self.renderer.last_rendered_chunks}")
        lines.append(f"World draws: {self.renderer.last_world_renderables}")
        lines.append(f"Zoom: {self.zoom_factor:.2f}x")
        lines.append(f"Block type: {self.selected_block_type.name}")
        lines.append(f"View: {'VOXEL' if self.use_voxel_view else 'LEGACY'}")

        if self.show_profiler and self._profile_smoothed:
            p = self._profile_smoothed
            input_ms = p.get("input", 0.0)
            update_ms = p.get("update", 0.0)
            render_ms = p.get("render", 0.0)
            ui_ms = p.get("ui", 0.0)
            present_ms = p.get("present", 0.0)
            frame_ms = p.get("frame", 0.0)
            lines.append(
                f"P ms in:{input_ms:.2f} up:{update_ms:.2f}"
            )
            lines.append(
                f"P ms rd:{render_ms:.2f} ui:{ui_ms:.2f} pr:{present_ms:.2f}"
            )
            lines.append(f"P ms frame:{frame_ms:.2f}")

        flags: list[str] = []
        if self.god_mode:
            flags.append("GOD")
        if self.instant_destroy:
            flags.append("INST")
        if self.physics_paused:
            flags.append("P-Pause")
        if self.interaction.regen_enabled:
            flags.append("Regen")
        if flags:
            lines.append("Flags: " + ", ".join(flags))

        gx = int(self.player_world_x // self.grid.config.tile_size)
        gy = int(self.player_world_y // self.grid.config.tile_size)
        lines.append(f"Player grid: ({gx}, {gy})")

        if self.show_command_help:
            lines.append("Cmds: V view | H help | TAB zoom | T profiler")
            lines.append("F1/F2/F3 overlays | F4/F5 HUD | F6 god | F7 instant")
            lines.append("F8 burst | F9 regen | F10 place | F11 clear | F12 reset")
            lines.append("1..5 bloco | G regen on/off | P pausa fisica | C limpa")

        y = 8
        for text in lines:
            rendered = font_obj.render(text, True, (240, 240, 240))
            screen.blit(rendered, (8, y))
            y += 18
