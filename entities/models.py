"""Basic entity models shared by game systems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CombatStats:
    """Combat-related values for an actor."""

    hp: int
    attack: int
    stun_frames: int


@dataclass
class SkillTree:
    """Persistent skill progression values."""

    blade_powerup: int = 0
    blade_stun: int = 0
    blade_lifesteal: int = 0
    blade_block: int = 0
    dart_powerup: int = 0
    dart_attack_speedup: int = 0
    dart_stun: int = 0
    dart_rangeup: int = 0
    move_speedup: int = 0
    move_speedup_credit: int = 0
    max_hp: int = 0
