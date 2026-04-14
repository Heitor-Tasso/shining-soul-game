"""Runtime configuration for Shining Soul Remake.

This module centralizes environment-driven settings and common paths.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
ENV_FILE = ROOT_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


def _env_int(name: str, default: int) -> int:
    """Return an integer value from env, falling back to default."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError:
        return default


@dataclass(frozen=True)
class GameSettings:
    """Container with immutable runtime settings for the game."""

    root_dir: Path
    assets_dir: Path
    screen_width: int
    screen_height: int
    fps: int
    ui_font: str

    @property
    def resolution(self) -> tuple[int, int]:
        """Return pygame window resolution as width and height."""
        return self.screen_width, self.screen_height


@dataclass(frozen=True)
class VoxelSettings:
    """Static configuration for the voxel 2.5D runtime systems."""

    grid_w: int = 128
    grid_h: int = 96
    grid_d: int = 8
    tile_size: int = 32
    chunk_size: int = 16
    max_particles: int = 100
    particle_static_age: float = 120.0
    regen_enabled: bool = True
    regen_interval: float = 600.0


GAME_SETTINGS = GameSettings(
    root_dir=ROOT_DIR,
    assets_dir=ROOT_DIR / "assets",
    screen_width=_env_int("SCREEN_WIDTH", 800),
    screen_height=_env_int("SCREEN_HEIGHT", 600),
    fps=_env_int("FPS", 60),
    ui_font=os.getenv("UI_FONT", "Rosewood Std"),
)

VOXEL_SETTINGS = VoxelSettings()


def asset_path(*parts: str) -> Path:
    """Build an absolute path inside the assets directory."""
    return GAME_SETTINGS.assets_dir.joinpath(*parts)
