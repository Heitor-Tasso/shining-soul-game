from core.world_grid import BlockType, GridConfig, VoxelGrid


def _make_grid() -> VoxelGrid:
    return VoxelGrid(GridConfig(grid_w=8, grid_h=8, grid_d=4, tile_size=32, chunk_size=4))


def test_init_flat_world_fills_floor_with_grass() -> None:
    grid = _make_grid()
    grid.init_flat_world()

    assert grid.get_block(3, 3, 0) == BlockType.GRASS
    assert grid.get_surface_z(3, 3) >= 0


def test_init_empty_world_clears_all_blocks() -> None:
    grid = _make_grid()
    grid.init_flat_world()

    grid.init_empty_world()

    assert grid.get_surface_z(3, 3) == -1


def test_get_block_out_of_bounds_returns_air() -> None:
    grid = _make_grid()

    assert grid.get_block(-1, 0, 0) == BlockType.AIR
    assert grid.get_block(0, 99, 0) == BlockType.AIR


def test_destroy_block_returns_old_type_and_sets_air() -> None:
    grid = _make_grid()
    grid.set_block(2, 2, 1, BlockType.STONE)

    old_type = grid.destroy_block(2, 2, 1)

    assert old_type == BlockType.STONE
    assert grid.get_block(2, 2, 1) == BlockType.AIR


def test_damage_block_progressive() -> None:
    grid = _make_grid()
    grid.set_block(2, 2, 1, BlockType.STONE)

    block_type, destroyed = grid.damage_block(2, 2, 1, damage=1)

    assert block_type == BlockType.STONE
    assert not destroyed
    assert grid.block_hp[2, 2, 1] == 2


def test_damage_block_destroys_at_zero_hp() -> None:
    grid = _make_grid()
    grid.set_block(1, 1, 1, BlockType.DIRT)

    block_type, destroyed = grid.damage_block(1, 1, 1, damage=1)

    assert block_type == BlockType.DIRT
    assert destroyed
    assert grid.get_block(1, 1, 1) == BlockType.AIR


def test_place_block_only_on_air() -> None:
    grid = _make_grid()
    placed_first = grid.place_block(1, 1, 1, BlockType.WOOD)
    placed_second = grid.place_block(1, 1, 1, BlockType.STONE)

    assert placed_first
    assert not placed_second
    assert grid.get_block(1, 1, 1) == BlockType.WOOD


def test_get_surface_z() -> None:
    grid = _make_grid()
    grid.set_block(3, 3, 1, BlockType.STONE)
    grid.set_block(3, 3, 2, BlockType.WOOD)

    assert grid.get_surface_z(3, 3) == 2


def test_collision_rects_near_returns_only_nearby() -> None:
    grid = _make_grid()
    grid.set_block(1, 1, 1, BlockType.STONE)
    grid.set_block(7, 7, 1, BlockType.STONE)

    rects = grid.get_collision_rects_near(32, 32, radius=80)
    positions = {(rect.x, rect.y) for rect in rects}

    assert (32, 32) in positions
    assert (224, 224) not in positions


def test_chunk_dirty_on_modification() -> None:
    grid = _make_grid()
    grid.chunks_dirty[:, :] = False

    grid.set_block(6, 6, 1, BlockType.STONE)

    assert grid.chunks_dirty[1, 1]
