from core.isometric import IsometricCamera, depth_sort_key


def test_cart_to_iso_origin() -> None:
    camera = IsometricCamera(800, 600)

    assert camera.cart_to_iso(0, 0, 0) == (0.0, 0.0)


def test_cart_to_iso_roundtrip() -> None:
    camera = IsometricCamera(800, 600)
    gx, gy = 12.25, 7.5

    sx, sy = camera.grid_to_screen(gx, gy, gz=0)
    out_gx, out_gy = camera.screen_to_grid(sx, sy, gz=0)

    assert abs(out_gx - gx) < 1e-6
    assert abs(out_gy - gy) < 1e-6


def test_depth_sort_key_ordering() -> None:
    north = depth_sort_key(1, 1, 0)
    south = depth_sort_key(2, 2, 0)
    upper = depth_sort_key(2, 2, 2)

    assert south > north
    assert upper > south


def test_visible_chunk_range_culling() -> None:
    camera = IsometricCamera(800, 600)
    camera.update(player_wx=400, player_wy=300, grid_w=128, grid_h=96, tile_size=32)

    min_cx, min_cy, max_cx, max_cy = camera.visible_chunk_range(chunk_size=16, chunks_x=8, chunks_y=6)

    assert 0 <= min_cx <= max_cx < 8
    assert 0 <= min_cy <= max_cy < 6


def test_world_to_screen_consistency() -> None:
    camera = IsometricCamera(800, 600)
    wx, wy = 96.0, 64.0

    a = camera.world_to_screen(wx, wy, tile_size=32)
    b = camera.grid_to_screen(wx / 32.0, wy / 32.0)

    assert a == b
