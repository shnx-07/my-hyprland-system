import subprocess


def _run_systemctl(action: str) -> None:
    subprocess.run(
        ["systemctl", action],
        check=True,
        timeout=10,
    )


def lock_session() -> None:
    subprocess.run(
        ["loginctl", "lock-session"],
        check=True,
        timeout=10,
    )


def suspend_system() -> None:
    _run_systemctl("suspend")


def reboot_system() -> None:
    _run_systemctl("reboot")


def power_off_system() -> None:
    _run_systemctl("poweroff")
