from core import rendering


class FakeImage:
    def __init__(self, width: int = 20, height: int = 10) -> None:
        self._width = width
        self._height = height

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height


class FakeScreen:
    def __init__(self) -> None:
        self.calls: list[tuple[object, tuple[int, int]]] = []

    def blit(self, image_obj, position: tuple[int, int]) -> None:
        self.calls.append((image_obj, position))


def test_character_blit_with_mid_lock_centers_image() -> None:
    screen = FakeScreen()
    image = FakeImage(width=20, height=10)

    rendering.character_blit(screen, image, (100, 50), "mid", (0, 0))

    assert screen.calls[-1][1] == (90, 45)


def test_draw_blade_block_decrements_timers() -> None:
    screen = FakeScreen()
    image = FakeImage()
    show_block = [2, 0]

    rendering.draw_blade_block(screen, image, show_block, 300, 200)

    assert show_block == [1, 0]
    assert len(screen.calls) == 1


def test_draw_round_label_renders_expected_text() -> None:
    screen = FakeScreen()

    class FakeFont:
        def render(self, text: str, antialias: bool, color: tuple[int, int, int]) -> str:
            _ = antialias, color
            return text

    rendering.draw_round_label(screen, FakeFont(), 7)

    assert screen.calls[-1][0] == "ROUND 7"
