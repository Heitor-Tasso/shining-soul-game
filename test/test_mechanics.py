from core import mechanics


class FakeRect:
    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def colliderect(self, other: "FakeRect") -> bool:
        return not (
            self.x + self.w <= other.x
            or other.x + other.w <= self.x
            or self.y + self.h <= other.y
            or other.y + other.h <= self.y
        )


def test_direction_to_index_maps_diagonal() -> None:
    assert mechanics.direction_to_index([1, -1]) == 1


def test_sprite_mode_index_for_self_blade_move() -> None:
    self_modes = ["blade", "bladeatk", "bladecharge", "bladedamage", "bladedead", "blademove"]
    status = [1, 0, 100, 0, "move", 0]

    assert mechanics.sprite_mode_index(status, "self", self_modes, []) == 5


def test_is_all_clear_true_when_empty() -> None:
    assert mechanics.is_all_clear([])


def test_enemy_sprite_size_horizontal() -> None:
    assert mechanics.enemy_sprite_size([1, 0, 0, 0]) == (130, 61)


def test_ai_move_diagonal_keeps_int_coordinates() -> None:
    next_x, next_y = mechanics.ai_move(0, 0, 100, 100, 10, [1, 1])

    assert isinstance(next_x, int)
    assert isinstance(next_y, int)
    assert next_x > 100
    assert next_y > 100


def test_generate_enemies_returns_expected_count(monkeypatch) -> None:
    values = iter([1000, 1000, 1500, 1200, 1800, 400])

    def fake_randint(_a: int, _b: int) -> int:
        return next(values)

    monkeypatch.setattr(mechanics, "randint", fake_randint)
    enemy_x, enemy_y = mechanics.generate_enemies(
        map_self_x=400,
        map_self_y=300,
        map_block_rects=[],
        game_level=1,
        map_size=(2000, 2000),
        enemy_size=60,
        self_size=50,
    )

    assert len(enemy_x) == 3
    assert len(enemy_y) == 3
