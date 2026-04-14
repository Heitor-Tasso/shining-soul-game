from core import screens
from entities.models import SkillTree


def test_menu_hover_option_start() -> None:
    assert screens.menu_hover_option(250, 250) == 1


def test_help_hover_option_back_button() -> None:
    assert screens.help_hover_option(530, 520) == 2


def test_gameover_hover_option_outside_button() -> None:
    assert screens.gameover_hover_option(50, 50) == 1


def test_levelup_hover_respects_skill_caps() -> None:
    skill_tree = SkillTree(blade_stun=20)
    option = screens.levelup_hover_option(200, 250, skill_tree)

    assert option == 0


def test_apply_levelup_option_consumes_credit() -> None:
    skill_tree = SkillTree(move_speedup_credit=1)

    applied = screens.apply_levelup_option(5, skill_tree)

    assert applied
    assert skill_tree.move_speedup == 1
    assert skill_tree.move_speedup_credit == 0


def test_apply_levelup_option_invalid_returns_false() -> None:
    skill_tree = SkillTree()

    assert not screens.apply_levelup_option(99, skill_tree)
