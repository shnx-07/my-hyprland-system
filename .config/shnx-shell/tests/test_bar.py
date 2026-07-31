from shnx_shell.bar.bar import Bar
from shnx_shell.components.component import Component


class FakeComponent(Component):
    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True


def test_bar_can_start_and_stop() -> None:
    bar = Bar()

    bar.start()
    bar.stop()


def test_bar_has_three_sections() -> None:
    bar = Bar()

    left_item = Component()
    center_item = Component()
    right_item = Component()

    bar.add_left(left_item)
    bar.add_center(center_item)
    bar.add_right(right_item)

    assert bar.left == [left_item]
    assert bar.center == [center_item]
    assert bar.right == [right_item]


def test_bar_starts_and_stops_its_components() -> None:
    bar = Bar()
    component = FakeComponent()

    bar.add_center(component)

    bar.start()
    assert component.started is True

    bar.stop()
    assert component.stopped is True
