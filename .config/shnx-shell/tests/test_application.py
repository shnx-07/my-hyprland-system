from shnx_shell.brain.application import run


def test_run_returns_zero() -> None:
    assert run() == 0
