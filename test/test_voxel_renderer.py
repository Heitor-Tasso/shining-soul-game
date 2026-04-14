import pygame

from core.isometric import IsometricCamera
from core.voxel_renderer import VoxelWorldRenderer
from core.world_grid import BlockType, GridConfig, VoxelGrid


def _make_renderer() -> tuple[VoxelGrid, IsometricCamera, VoxelWorldRenderer]:
    grid = VoxelGrid(GridConfig(grid_w=8, grid_h=8, grid_d=4, tile_size=32, chunk_size=4))
    grid.init_flat_world()
    grid.set_block(3, 3, 1, BlockType.STONE)
    grid.set_block(4, 3, 2, BlockType.WOOD)

    camera = IsometricCamera(800, 600)
    camera.update(player_wx=128, player_wy=128, grid_w=grid.config.grid_w, grid_h=grid.config.grid_h, tile_size=32)

    renderer = VoxelWorldRenderer(grid, camera)
    return grid, camera, renderer


def test_collect_depth_sorted_world_renderables_returns_sorted() -> None:
    _grid, _camera, renderer = _make_renderer()

    renderables = renderer.collect_depth_sorted_world_renderables()
    depths = [item[0] for item in renderables]

    assert renderables
    assert depths == sorted(depths)
    assert renderer.last_world_renderables == len(renderables)


def test_render_world_updates_chunk_counter() -> None:
    _grid, _camera, renderer = _make_renderer()
    screen = pygame.Surface((800, 600), pygame.SRCALPHA)

    renderer.render_world(screen)

    assert renderer.last_rendered_chunks > 0
