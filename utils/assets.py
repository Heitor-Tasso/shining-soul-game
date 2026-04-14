"""Asset discovery utilities."""

from __future__ import annotations

from pathlib import Path


def globfolder(path: str | Path) -> list[str]:
    """Return all direct subdirectories of a path as normalized strings."""
    base_path = Path(path)
    return sorted(
        entry.as_posix()
        for entry in base_path.iterdir()
        if entry.is_dir()
    )
