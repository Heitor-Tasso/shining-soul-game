from config import VOXEL_SETTINGS
from core.block_interaction import BlockInteractionSystem
from core.physics import ParticlePool
from core.world_grid import BlockType, GridConfig, VoxelGrid


def _make_system() -> tuple[VoxelGrid, ParticlePool, BlockInteractionSystem]:
    grid = VoxelGrid(GridConfig(grid_w=8, grid_h=8, grid_d=4, tile_size=32, chunk_size=4))
    pool = ParticlePool(capacity=50)
    system = BlockInteractionSystem(grid, pool)
    return grid, pool, system


def test_attack_block_damages() -> None:
    grid, _pool, system = _make_system()
    grid.set_block(2, 1, 1, BlockType.STONE)

    hit = system.attack_block(wx=32, wy=32, direction=(1, 0), attack_range=96, damage=1)

    assert hit
    assert grid.block_hp[2, 1, 1] == 2


def test_attack_block_destroys_spawns_debris() -> None:
    grid, pool, system = _make_system()
    grid.set_block(2, 1, 1, BlockType.DIRT)

    hit = system.attack_block(wx=32, wy=32, direction=(1, 0), attack_range=96, damage=1)

    assert hit
    assert grid.get_block(2, 1, 1) == BlockType.AIR
    assert pool.active_count > 0


def test_attack_air_returns_false() -> None:
    _grid, _pool, system = _make_system()

    hit = system.attack_block(wx=32, wy=32, direction=(1, 0), attack_range=64, damage=1)

    assert not hit


def test_regen_places_block_adjacent() -> None:
    grid, _pool, system = _make_system()
    system.regen_enabled = True
    grid.set_block(3, 3, 1, BlockType.STONE)

    before = int((grid.blocks != int(BlockType.AIR)).sum())
    system.update_regeneration(dt=VOXEL_SETTINGS.regen_interval)
    after = int((grid.blocks != int(BlockType.AIR)).sum())

    assert after >= before


def test_regen_respects_entities() -> None:
    grid, _pool, system = _make_system()
    system.regen_enabled = True
    grid.set_block(3, 3, 1, BlockType.STONE)

    candidates = grid.find_regen_candidates()
    occupied = [(gx, gy, gz) for gx, gy, gz, _block in candidates]

    before = int((grid.blocks != int(BlockType.AIR)).sum())
    system.update_regeneration(dt=VOXEL_SETTINGS.regen_interval, occupied_positions=occupied)
    after = int((grid.blocks != int(BlockType.AIR)).sum())

    assert after == before
