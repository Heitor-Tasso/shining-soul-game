from config import GAME_SETTINGS, asset_path


def test_resolution_has_positive_values() -> None:
    width, height = GAME_SETTINGS.resolution
    assert width > 0
    assert height > 0


def test_asset_path_points_to_assets_directory() -> None:
    path = asset_path("sound", "background.wav")
    assert "assets" in str(path)
