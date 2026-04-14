"""Resource loading helpers for game runtime.

These functions keep asset I/O out of the core game loop module.
"""

from __future__ import annotations

from dataclasses import dataclass
from glob import glob
from pathlib import Path
from typing import Any

from pygame import image, mixer

from config import asset_path
from utils.assets import globfolder


DIRECTION_TO_INDEX = {
    "up": 0,
    "upright": 1,
    "right": 2,
    "downright": 3,
    "down": 4,
    "downleft": 5,
    "left": 6,
    "upleft": 7,
}


@dataclass(frozen=True)
class SoundAssets:
    """Container for all game sound effects."""

    get_damage: Any
    hit: Any
    knife: Any
    levelup: Any
    blade: Any
    yes: Any
    block: Any
    enemy_dead: Any


@dataclass(frozen=True)
class UiAssets:
    """Container for static UI images and scene backgrounds."""

    game_map: Any
    tree: Any
    ball: Any
    hp_bar: Any
    blade_block: Any
    menu: list[Any]
    help: list[Any]
    story: list[Any]
    levelup: list[Any]
    gameover: list[Any]
    skill: list[Any]


@dataclass(frozen=True)
class CharacterAssets:
    """Container for player and enemy sprite sheets and lock metadata."""

    self_modes: list[str]
    enemy_modes: list[str]
    self_sprites: list[list[list[Any]]]
    self_locks: list[list[str]]
    enemy_sprites: list[list[list[Any]]]
    enemy_locks: list[list[str]]


@dataclass(frozen=True)
class ResourceBundle:
    """Aggregated resource bundle used by the legacy runtime."""

    sounds: SoundAssets
    ui: UiAssets
    characters: CharacterAssets


def _load_scene_images(folder: str, prefix: str, count: int) -> list[Any]:
    """Load ordered sequence of images from an assets subfolder."""
    loaded: list[Any] = []
    for index in range(count):
        loaded.append(image.load(asset_path(folder, f"{prefix}{index}.png")))
    return loaded


def load_sound_assets() -> SoundAssets:
    """Load all wav files used by runtime audio effects."""
    return SoundAssets(
        get_damage=mixer.Sound(asset_path("sound", "getdamage.wav")),
        hit=mixer.Sound(asset_path("sound", "hit.wav")),
        knife=mixer.Sound(asset_path("sound", "knife.wav")),
        levelup=mixer.Sound(asset_path("sound", "levelup.wav")),
        blade=mixer.Sound(asset_path("sound", "blade.wav")),
        yes=mixer.Sound(asset_path("sound", "yes.wav")),
        block=mixer.Sound(asset_path("sound", "block.wav")),
        enemy_dead=mixer.Sound(asset_path("sound", "enemydead.wav")),
    )


def load_ui_assets() -> UiAssets:
    """Load non-character images (menu, map, overlays and screens)."""
    return UiAssets(
        game_map=image.load(asset_path("mapbase.png")).convert_alpha(),
        tree=image.load(asset_path("tree.png")).convert_alpha(),
        ball=image.load(asset_path("ball.png")).convert_alpha(),
        hp_bar=image.load(asset_path("hpbar.png")).convert_alpha(),
        blade_block=image.load(asset_path("block.png")).convert_alpha(),
        menu=_load_scene_images("menu", "menu", 4),
        help=_load_scene_images("help", "help", 3),
        story=_load_scene_images("story", "story", 2),
        levelup=_load_scene_images("levelup", "levelup", 11),
        gameover=_load_scene_images("gameover", "gameover", 2),
        skill=_load_scene_images("skill", "skill", 2),
    )


def _build_direction_tables(root_folder: str) -> tuple[list[list[list[Any]]], list[list[str]]]:
    """Build sprite and lock tables using direction-named folders."""
    direction_folders = globfolder(asset_path(root_folder))
    sprite_table: list[list[list[Any]]] = [0] * 8
    lock_table: list[list[str]] = [0] * 8

    for direction_folder in direction_folders:
        direction_name = Path(direction_folder).name
        if direction_name not in DIRECTION_TO_INDEX:
            continue
        direction_index = DIRECTION_TO_INDEX[direction_name]
        sprite_table[direction_index] = globfolder(direction_folder)
        lock_table[direction_index] = globfolder(direction_folder)

    for x in range(len(sprite_table)):
        for y in range(len(sprite_table[x])):
            sprite_table[x][y] = glob(f"{sprite_table[x][y]}/*.png")
            lock_table[x][y] = Path(lock_table[x][y], "lock.txt").read_text().strip()

    for x in range(len(sprite_table)):
        for y in range(len(sprite_table[x])):
            for z in range(len(sprite_table[x][y])):
                sprite_table[x][y][z] = image.load(sprite_table[x][y][z]).convert_alpha()

    return sprite_table, lock_table


def load_character_assets() -> CharacterAssets:
    """Load player and enemy directional sprite tables."""
    self_sprites, self_locks = _build_direction_tables("ninja")
    enemy_sprites, enemy_locks = _build_direction_tables("enemy")

    self_modes = [
        "blade",
        "bladeatk",
        "bladecharge",
        "bladedamage",
        "bladedead",
        "blademove",
        "dart",
        "dartatk",
        "dartdamage",
        "dartdead",
        "dartmove",
        "knife",
    ]
    enemy_modes = ["atk", "damage", "move", "preatk"]

    return CharacterAssets(
        self_modes=self_modes,
        enemy_modes=enemy_modes,
        self_sprites=self_sprites,
        self_locks=self_locks,
        enemy_sprites=enemy_sprites,
        enemy_locks=enemy_locks,
    )


def load_resource_bundle() -> ResourceBundle:
    """Load and return all runtime resources used by the legacy game."""
    return ResourceBundle(
        sounds=load_sound_assets(),
        ui=load_ui_assets(),
        characters=load_character_assets(),
    )
