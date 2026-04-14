from entities.models import SkillTree


def test_skill_tree_defaults() -> None:
    skill_tree = SkillTree()

    assert skill_tree.blade_powerup == 0
    assert skill_tree.blade_stun == 0
    assert skill_tree.blade_lifesteal == 0
    assert skill_tree.blade_block == 0
    assert skill_tree.dart_powerup == 0
    assert skill_tree.dart_attack_speedup == 0
    assert skill_tree.dart_stun == 0
    assert skill_tree.dart_rangeup == 0
    assert skill_tree.move_speedup == 0
    assert skill_tree.move_speedup_credit == 0
    assert skill_tree.max_hp == 0


def test_skill_tree_can_update_progression() -> None:
    skill_tree = SkillTree()
    skill_tree.blade_powerup += 1
    skill_tree.move_speedup_credit += 2

    assert skill_tree.blade_powerup == 1
    assert skill_tree.move_speedup_credit == 2
