from core.game_state import create_initial_state, recalculate_combat_config, reset_for_new_game, reset_for_new_round


def test_create_initial_state_sets_player_hp_from_combat() -> None:
    state = create_initial_state()

    assert state.player.status[2] == state.combat.player_hp


def test_recalculate_combat_config_applies_skills_and_level() -> None:
    state = create_initial_state()
    state.game_level = 4
    state.skill_tree.move_speedup = 2
    state.skill_tree.max_hp = 1
    state.skill_tree.blade_powerup = 1

    recalculate_combat_config(state)

    assert state.combat.player_speed == 8
    assert state.combat.player_hp == 130
    assert state.combat.blade_atk == 46
    assert state.combat.enemy_hp == 124


def test_reset_for_new_round_advances_level_and_clears_round_data() -> None:
    state = create_initial_state()
    state.enemies.map_x = [10.0]
    state.player.attack_rect = object()
    state.player.knives = [[1, 0, 1, 1, 0, 0, 0, 0]]

    reset_for_new_round(state)

    assert state.game_level == 2
    assert state.enemies.map_x == []
    assert state.player.attack_rect == 0
    assert state.player.knives == []


def test_reset_for_new_game_resets_progression() -> None:
    state = create_initial_state()
    state.game_level = 8
    state.screen_mode = "mainloop"
    state.skill_tree.blade_powerup = 10

    reset_for_new_game(state)

    assert state.game_level == 1
    assert state.screen_mode == "menu"
    assert state.skill_tree.blade_powerup == 0
    assert state.player.status[2] == state.combat.player_hp
