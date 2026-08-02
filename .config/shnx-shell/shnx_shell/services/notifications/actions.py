from shnx_shell.services.notifications.daemon import (
    notification_daemon,
)
from shnx_shell.services.notifications.store import (
    notification_store,
)


CLOSE_REASON_EXPIRED = 1
CLOSE_REASON_DISMISSED = 2
CLOSE_REASON_CLOSED_BY_CALL = 3
CLOSE_REASON_UNDEFINED = 4


def dismiss_notification(
    notification_id: int,
) -> bool:
    removed = notification_store.remove(notification_id)

    if not removed:
        return False

    notification_daemon.emit_notification_closed(
        notification_id,
        CLOSE_REASON_DISMISSED,
    )

    return True


def clear_notifications() -> int:
    notifications = notification_store.get_all()

    if not notifications:
        return 0

    notification_ids = tuple(
        notification.notification_id
        for notification in notifications
    )

    notification_store.clear()

    for notification_id in notification_ids:
        notification_daemon.emit_notification_closed(
            notification_id,
            CLOSE_REASON_DISMISSED,
        )

    return len(notification_ids)


def invoke_notification_action(
    notification_id: int,
    action_key: str,
) -> None:
    notification_daemon.emit_action_invoked(
        notification_id,
        action_key,
    )

def expire_notification(
    notification_id: int,
) -> bool:
    removed = notification_store.remove(notification_id)

    if not removed:
        return False

    notification_daemon.emit_notification_closed(
        notification_id,
        CLOSE_REASON_EXPIRED,
    )

    return True
