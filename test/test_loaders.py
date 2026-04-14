from pathlib import Path

from utils import loaders


def test_loader_direction_map_has_all_expected_directions() -> None:
    expected = {
        "up",
        "upright",
        "right",
        "downright",
        "down",
        "downleft",
        "left",
        "upleft",
    }

    assert set(loaders.DIRECTION_TO_INDEX.keys()) == expected
    assert len(loaders.DIRECTION_TO_INDEX) == 8


def test_load_scene_images_builds_expected_sequence(monkeypatch) -> None:
    loaded_paths: list[Path] = []

    def fake_asset_path(*parts: str) -> Path:
        return Path("/tmp").joinpath(*parts)

    def fake_load(path: Path) -> Path:
        loaded_paths.append(path)
        return path

    monkeypatch.setattr(loaders, "asset_path", fake_asset_path)
    monkeypatch.setattr(loaders.image, "load", fake_load)

    images = loaders._load_scene_images("menu", "menu", 3)

    assert images == loaded_paths
    assert [path.as_posix() for path in loaded_paths] == [
        "/tmp/menu/menu0.png",
        "/tmp/menu/menu1.png",
        "/tmp/menu/menu2.png",
    ]


def test_load_sound_assets_uses_expected_file_names(monkeypatch) -> None:
    captured: list[Path] = []

    def fake_asset_path(*parts: str) -> Path:
        return Path("/tmp").joinpath(*parts)

    def fake_sound(path: Path) -> str:
        captured.append(path)
        return path.as_posix()

    monkeypatch.setattr(loaders, "asset_path", fake_asset_path)
    monkeypatch.setattr(loaders.mixer, "Sound", fake_sound)

    sounds = loaders.load_sound_assets()

    assert sounds.get_damage.endswith("getdamage.wav")
    assert sounds.enemy_dead.endswith("enemydead.wav")
    assert len(captured) == 8
