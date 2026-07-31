from datetime import datetime

from shnx_shell.bar.modules.clock import Clock


def test_clock_returns_current_time() -> None:
    clock = Clock()

    assert clock.get_text() == datetime.now().strftime("%H:%M")
