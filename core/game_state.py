"""Structured mutable runtime state for the game loop.

This module provides a dataclass-based state container to reduce reliance on
module-level globals and ease incremental migration from legacy code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from entities.models import SkillTree


@dataclass
class PlayerState:
    """Player mutable state used by mechanics and rendering."""

    map_x: float = 400.0
    map_y: float = 300.0
    prev_x: float = 0.0
    prev_y: float = 0.0
    screen_x: float = 0.0
    screen_y: float = 0.0
    status: list = field(default_factory=lambda: [1, 0, 100, 0, "", 0])
    frame_status: list = field(default_factory=lambda: [0, 0, 0, 0])
    attack_rect: Any = 0
    knives: list = field(default_factory=list)


@dataclass
class EnemyState:
    """Enemy collections kept in parallel arrays to preserve legacy behavior."""

    map_x: list[float] = field(default_factory=list)
    map_y: list[float] = field(default_factory=list)
    prev_x: list[float] = field(default_factory=list)
    prev_y: list[float] = field(default_factory=list)
    screen_x: list[float] = field(default_factory=list)
    screen_y: list[float] = field(default_factory=list)
    statuses: list[list] = field(default_factory=list)
    prev_statuses: list[list] = field(default_factory=list)
    frame_statuses: list[list] = field(default_factory=list)
    directions: list[list[int]] = field(default_factory=list)


@dataclass
class CombatConfig:
    """Derived combat values recalculated from progression state."""

    player_speed: int = 4
    enemy_speed: float = 2.0
    knife_speed: int = 20
    player_size: int = 50
    enemy_size: int = 60
    player_hp: int = 100
    enemy_hp: int = 100
    blade_atk: int = 40
    dart_atk: int = 20
    enemy_atk: float = 10.0
    blade_range: int = 80
    enemy_range: int = 75
    blade_cd: int = 20
    dart_cd: int = 27
    blade_stun: int = 15
    dart_stun: int = 15
    knife_size: int = 30
    knife_range: int = 10


@dataclass
class GameState:
    """Top-level mutable game state for gameplay and screen flow."""

    player: PlayerState = field(default_factory=PlayerState)
    enemies: EnemyState = field(default_factory=EnemyState)
    combat: CombatConfig = field(default_factory=CombatConfig)
    skill_tree: SkillTree = field(default_factory=SkillTree)
    game_level: int = 1
    screen_mode: str = "menu"
    map_size: tuple[int, int] = (4000, 3000)
    show_block: list[int] = field(default_factory=list)


def create_initial_state() -> GameState:
    """Create a fresh game state with progression defaults applied."""
    state = GameState()
    recalculate_combat_config(state)
    state.player.status[2] = state.combat.player_hp
    return state


def reset_for_new_game(state: GameState) -> None:
    """Reset full runtime data for a new run."""
    state.player = PlayerState()
    state.enemies = EnemyState()
    state.skill_tree = SkillTree()
    state.combat = CombatConfig()
    state.game_level = 1
    state.screen_mode = "menu"
    state.map_size = (4000, 3000)
    state.show_block.clear()
    recalculate_combat_config(state)
    state.player.status[2] = state.combat.player_hp


def reset_for_new_round(state: GameState) -> None:
    """Prepare state for the next combat round while keeping progression."""
    state.game_level += 1
    state.enemies = EnemyState()
    state.player.attack_rect = 0
    state.player.knives.clear()
    state.show_block.clear()
    recalculate_combat_config(state)


def recalculate_combat_config(state: GameState) -> None:
    """Recompute derived combat values from the current skill tree."""
    skills = state.skill_tree
    cfg = CombatConfig()

    cfg.player_speed = 4 + skills.move_speedup * 2
    cfg.enemy_speed = min(2.0 + 0.08 * max(0, state.game_level - 1), 5.0)
    cfg.player_hp = 100 + skills.max_hp * 30
    cfg.enemy_hp = 100 + 8 * max(0, state.game_level - 1)
    cfg.enemy_atk = 10.0 + 0.5 * max(0, state.game_level - 1)

    cfg.dart_cd = int(27 / (skills.dart_attack_speedup * 0.6 + 1))
    cfg.blade_stun = 30 + skills.blade_stun * 15
    cfg.dart_stun = 15 + skills.dart_stun * 8

    cfg.blade_atk = 40 + skills.blade_powerup * 6
    cfg.dart_atk = 20 + skills.dart_powerup * 5
    cfg.knife_range = 10 + skills.dart_rangeup * 3

    state.combat = cfg
