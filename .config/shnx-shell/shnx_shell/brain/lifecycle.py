from shnx_shell.services.notifications.daemon import (
    notification_daemon,
)


def startup() -> None:
    notification_daemon.start()
    print("Shnx Shell lifecycle started")


def shutdown() -> None:
    notification_daemon.stop()
    print("Shnx Shell lifecycle stopped")
