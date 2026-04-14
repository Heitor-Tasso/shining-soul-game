"""UI screen interaction helpers for menu and level-up states."""

from __future__ import annotations

from pygame import Rect

from entities.models import SkillTree


def levelup_hover_option(mouse_x: int, mouse_y: int, skill_tree: SkillTree) -> int:
    """Return level-up menu option based on mouse hover and skill constraints."""
    if Rect(0, 100, 400, 100).collidepoint(mouse_x, mouse_y):
        return 1
    if Rect(0, 200, 400, 100).collidepoint(mouse_x, mouse_y) and skill_tree.blade_stun < 20:
        return 2
    if Rect(0, 300, 400, 100).collidepoint(mouse_x, mouse_y):
        return 3
    if Rect(0, 400, 400, 100).collidepoint(mouse_x, mouse_y) and skill_tree.blade_block < 15:
        return 4
    if Rect(0, 500, 400, 100).collidepoint(mouse_x, mouse_y) and skill_tree.move_speedup_credit > 0:
        return 5
    if Rect(400, 100, 400, 100).collidepoint(mouse_x, mouse_y):
        return 6
    if Rect(400, 200, 400, 100).collidepoint(mouse_x, mouse_y) and skill_tree.dart_attack_speedup < 10:
        return 7
    if Rect(400, 300, 400, 100).collidepoint(mouse_x, mouse_y) and skill_tree.dart_stun < 20:
        return 8
    if Rect(400, 400, 400, 100).collidepoint(mouse_x, mouse_y):
        return 9
    if Rect(400, 500, 400, 100).collidepoint(mouse_x, mouse_y):
        return 10
    return 0


def apply_levelup_option(option: int, skill_tree: SkillTree) -> bool:
    """Apply selected level-up option and return whether any upgrade happened."""
    if option == 1:
        skill_tree.blade_powerup += 1
        return True
    if option == 2 and skill_tree.blade_stun < 20:
        skill_tree.blade_stun += 1
        return True
    if option == 3:
        skill_tree.blade_lifesteal += 1
        return True
    if option == 4 and skill_tree.blade_block < 15:
        skill_tree.blade_block += 1
        return True
    if option == 5 and skill_tree.move_speedup_credit > 0:
        skill_tree.move_speedup += 1
        skill_tree.move_speedup_credit -= 1
        return True
    if option == 6:
        skill_tree.dart_powerup += 1
        return True
    if option == 7 and skill_tree.dart_attack_speedup < 10:
        skill_tree.dart_attack_speedup += 1
        return True
    if option == 8 and skill_tree.dart_stun < 20:
        skill_tree.dart_stun += 1
        return True
    if option == 9:
        skill_tree.dart_rangeup += 1
        return True
    if option == 10:
        skill_tree.max_hp += 1
        return True
    return False


def menu_hover_option(mouse_x: int, mouse_y: int) -> int:
    """Return menu option index by mouse position."""
    if Rect(200, 200, 400, 100).collidepoint(mouse_x, mouse_y):
        return 1
    if Rect(200, 300, 400, 100).collidepoint(mouse_x, mouse_y):
        return 2
    if Rect(200, 400, 400, 100).collidepoint(mouse_x, mouse_y):
        return 3
    return 0


def gameover_hover_option(mouse_x: int, mouse_y: int) -> int:
    """Return gameover image index based on mouse hover."""
    if Rect(200, 300, 400, 260).collidepoint(mouse_x, mouse_y):
        return 0
    return 1


def help_hover_option(mouse_x: int, mouse_y: int) -> int:
    """Return help screen index based on mouse hover."""
    if Rect(528, 512, 233, 88).collidepoint(mouse_x, mouse_y):
        return 2
    if Rect(78, 512, 233, 88).collidepoint(mouse_x, mouse_y):
        return 0
    return 1


def story_hover_option(mouse_x: int, mouse_y: int) -> int:
    """Return story screen index based on mouse hover."""
    if Rect(518, 513, 233, 88).collidepoint(mouse_x, mouse_y):
        return 1
    return 0


def skill_hover_option(mouse_x: int, mouse_y: int) -> int:
    """Return skill description screen index based on mouse hover."""
    if Rect(518, 512, 233, 88).collidepoint(mouse_x, mouse_y):
        return 1
    return 0
