import pygame
import pytest

from core.block_interaction import BlockInteractionSystem
from core.debug_controls import DebugControls
from core.isometric import IsometricCamera
from core.physics import ParticlePool
from core.voxel_renderer import VoxelWorldRenderer
from core.world_grid import BlockType, GridConfig, VoxelGrid


class FakeKeys:
    def __init__(self, pressed: set[int] | None = None) -> None:
        self._pressed = pressed or set()

    def __getitem__(self, key_code: int) -> bool:
        return key_code in self._pressed


def _make_controls() -> DebugControls:
    grid = VoxelGrid(GridConfig(grid_w=8, grid_h=8, grid_d=4, tile_size=32, chunk_size=4))
    pool = ParticlePool(capacity=10)
    interaction = BlockInteractionSystem(grid, pool)
    renderer = VoxelWorldRenderer(grid, IsometricCamera(800, 600))
    return DebugControls(grid, pool, interaction, renderer)


def test_tab_cycles_zoom_level() -> None:
    controls = _make_controls()
    original_zoom = controls.zoom_factor

    controls.process_input(FakeKeys({pygame.K_TAB}), FakeKeys())

    assert controls.zoom_factor != original_zoom


def test_tab_requires_key_edge() -> None:
    controls = _make_controls()

    controls.process_input(FakeKeys({pygame.K_TAB}), FakeKeys())
    zoom_after_first_press = controls.zoom_factor
    controls.process_input(FakeKeys({pygame.K_TAB}), FakeKeys({pygame.K_TAB}))

    assert controls.zoom_factor == zoom_after_first_press


def test_t_toggles_profiler_visibility_on_key_edge() -> None:
    controls = _make_controls()

    controls.process_input(FakeKeys({pygame.K_t}), FakeKeys())
    assert controls.show_profiler

    controls.process_input(FakeKeys({pygame.K_t}), FakeKeys({pygame.K_t}))
    assert controls.show_profiler

    controls.process_input(FakeKeys(), FakeKeys({pygame.K_t}))
    controls.process_input(FakeKeys({pygame.K_t}), FakeKeys())
    assert not controls.show_profiler


def test_profile_smoothing_and_clear() -> None:
    controls = _make_controls()

    controls.set_frame_profile({"frame": 10.0, "update": 5.0}, alpha=0.5)
    controls.set_frame_profile({"frame": 14.0, "update": 7.0}, alpha=0.5)

    assert controls._profile_smoothed["frame"] == pytest.approx(12.0)
    assert controls._profile_smoothed["update"] == pytest.approx(6.0)

    controls.clear_frame_profile()
    assert controls._profile_latest == {}
    assert controls._profile_smoothed == {}


def test_fkey_with_short_prev_snapshot_does_not_crash() -> None:
    controls = _make_controls()

    controls.process_input(FakeKeys({pygame.K_F1}), (False,) * 8)

    assert controls.show_grid_overlay


def test_v_toggles_voxel_view_on_key_edge() -> None:
    controls = _make_controls()
    assert not controls.use_voxel_view

    controls.process_input(FakeKeys({pygame.K_v}), FakeKeys())
    assert controls.use_voxel_view

    controls.process_input(FakeKeys({pygame.K_v}), FakeKeys({pygame.K_v}))
    assert controls.use_voxel_view

    controls.process_input(FakeKeys(), FakeKeys({pygame.K_v}))
    controls.process_input(FakeKeys({pygame.K_v}), FakeKeys())
    assert not controls.use_voxel_view


def test_f12_resets_overlay_to_empty_world() -> None:
    controls = _make_controls()
    controls.grid.set_block(2, 2, 1, BlockType.STONE)
    controls.pool.spawn(1.0, 1.0, 1.0, int(BlockType.STONE))

    controls.process_input(FakeKeys({pygame.K_F12}), FakeKeys())

    assert controls.grid.get_surface_z(2, 2) == -1
    assert controls.pool.active_count == 0
