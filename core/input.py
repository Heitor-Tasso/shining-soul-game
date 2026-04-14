"""Input helpers for pygame loop."""

from __future__ import annotations

from dataclasses import dataclass

from pygame import key, mouse


@dataclass(frozen=True)
class InputState:
    """Keyboard and mouse snapshot for a frame."""

    keys: object
    mouse_buttons: tuple[bool, bool, bool]
    previous_mouse_buttons: tuple[bool, bool, bool]


def read_input(previous_mouse_buttons: tuple[bool, bool, bool]) -> InputState:
    """Capture keyboard and mouse states for the current frame."""
    return InputState(
        keys=key.get_pressed(),
        mouse_buttons=mouse.get_pressed(),
        previous_mouse_buttons=previous_mouse_buttons,
    )
