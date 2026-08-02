from collections.abc import Callable

from shnx_shell.services.notifications.shape import Notification


StoreCallback = Callable[[], None]


class NotificationStore:
    def __init__(self) -> None:
        self._notifications: list[Notification] = []
        self._callbacks: list[StoreCallback] = []

    def get_all(self) -> tuple[Notification, ...]:
        return tuple(self._notifications)

    def add(self, notification: Notification) -> None:
        self._notifications.insert(0, notification)
        self._emit_changed()

    def replace(self, notification: Notification) -> bool:
        for index, current in enumerate(self._notifications):
            if current.notification_id == notification.notification_id:
                self._notifications[index] = notification
                self._emit_changed()
                return True

        return False

    def remove(self, notification_id: int) -> bool:
        for index, notification in enumerate(self._notifications):
            if notification.notification_id == notification_id:
                del self._notifications[index]
                self._emit_changed()
                return True

        return False

    def clear(self) -> None:
        if not self._notifications:
            return

        self._notifications.clear()
        self._emit_changed()

    def count(self) -> int:
        return len(self._notifications)


    def unread_count(self) -> int:
        return sum(
            1
            for notification in self._notifications
            if not notification.read
        )

    def mark_all_read(self) -> None:
        changed = False

        for notification in self._notifications:
            if notification.read:
                continue

            notification.read = True
            changed = True

        if changed:
            self._emit_changed()

    def subscribe(self, callback: StoreCallback) -> None:
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unsubscribe(self, callback: StoreCallback) -> None:
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _emit_changed(self) -> None:
        for callback in tuple(self._callbacks):
            callback()


notification_store = NotificationStore()
