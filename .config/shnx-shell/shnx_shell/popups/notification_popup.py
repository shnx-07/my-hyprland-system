import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import GLib, Gtk, Gtk4LayerShell

from shnx_shell.services.notifications.actions import (
    dismiss_notification,
    invoke_notification_action,
)
from shnx_shell.services.notifications.shape import Notification
from shnx_shell.services.notifications.store import notification_store

from collections import deque


DEFAULT_TIMEOUT_MS = 5000


class NotificationPopup(Gtk.ApplicationWindow):
    def __init__(
        self,
        application: Gtk.Application,
    ) -> None:
        super().__init__(application=application)

        self.set_title("Shnx Notification Popup")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_default_size(360, -1)

        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(
            self,
            Gtk4LayerShell.Layer.OVERLAY,
        )

        Gtk4LayerShell.set_anchor(
            self,
            Gtk4LayerShell.Edge.TOP,
            True,
        )
        Gtk4LayerShell.set_anchor(
            self,
            Gtk4LayerShell.Edge.RIGHT,
            True,
        )

        Gtk4LayerShell.set_margin(
            self,
            Gtk4LayerShell.Edge.TOP,
            60,
        )
        Gtk4LayerShell.set_margin(
            self,
            Gtk4LayerShell.Edge.RIGHT,
            12,
        )

        Gtk4LayerShell.set_keyboard_mode(
            self,
            Gtk4LayerShell.KeyboardMode.NONE,
        )

        self.add_css_class("notification-popup-window")

        self._current_notification: Notification | None = None
        self._seen_ids: set[int] = set()
        self._notification_queue: deque[int] = deque()
        self._timeout_source_id: int | None = None

        notification_store.subscribe(
            self._on_store_changed
        )

        self.connect(
            "close-request",
            self._on_close_request,
        )

    def _on_store_changed(self) -> None:
        GLib.idle_add(self._process_store_change)

    def _process_store_change(self) -> bool:
        notifications = notification_store.get_all()

        notifications_by_id = {
            notification.notification_id: notification
            for notification in notifications
        }
        existing_ids = set(notifications_by_id)

        # Store order is newest first. Reverse it so rapid
        # notifications enter the popup queue oldest first.
        for notification in reversed(notifications):
            notification_id = notification.notification_id

            if notification_id in self._seen_ids:
                continue

            self._seen_ids.add(notification_id)

            if notification.suppressed:
                continue

            self._notification_queue.append(notification_id)

        # Remove queued notifications that were dismissed or cleared
        # before their popup had a chance to appear.
        self._notification_queue = deque(
            notification_id
            for notification_id in self._notification_queue
            if notification_id in existing_ids
        )

        if (
            self._current_notification is not None
            and self._current_notification.notification_id
            not in existing_ids
        ):
            self._hide_current_popup()
            return GLib.SOURCE_REMOVE

        if self._current_notification is None:
            self._show_next_notification(
                notifications_by_id
            )

        return GLib.SOURCE_REMOVE


    def _show_next_notification(
        self,
        notifications_by_id: dict[int, Notification] | None = None,
    ) -> None:
        if self._current_notification is not None:
            return

        if notifications_by_id is None:
            notifications_by_id = {
                notification.notification_id: notification
                for notification in notification_store.get_all()
            }

        while self._notification_queue:
            notification_id = self._notification_queue.popleft()

            notification = notifications_by_id.get(notification_id)

            if notification is None:
                continue

            if notification.suppressed:
                continue

            self._show_notification(notification)
            return

    def _show_notification(
        self,
        notification: Notification,
    ) -> None:
        self._cancel_timeout()

        self._current_notification = notification
        self.set_child(
            self._build_notification_card(notification)
        )
        self.present()

        timeout = notification.timeout

        if timeout < 0:
            timeout = DEFAULT_TIMEOUT_MS

        if timeout > 0:
            self._timeout_source_id = GLib.timeout_add(
                timeout,
                self._on_timeout,
                notification.notification_id,
            )

    def _build_notification_card(
        self,
        notification: Notification,
    ) -> Gtk.Box:
        card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )
        card.add_css_class("notification-popup-card")

        header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )
        header.add_css_class("notification-popup-header")

        app_name = notification.app_name.strip()

        app_label = Gtk.Label(
            label=app_name or "Application"
        )
        app_label.set_xalign(0)
        app_label.set_hexpand(True)
        app_label.set_ellipsize(3)
        app_label.add_css_class(
            "notification-popup-app"
        )

        dismiss_button = Gtk.Button(label="󰅖")
        dismiss_button.add_css_class(
            "notification-popup-dismiss"
        )
        dismiss_button.set_tooltip_text(
            "Dismiss notification"
        )
        dismiss_button.connect(
            "clicked",
            self._on_dismiss_clicked,
            notification.notification_id,
        )

        header.append(app_label)
        header.append(dismiss_button)

        summary_label = Gtk.Label(
            label=notification.summary
        )
        summary_label.set_xalign(0)
        summary_label.set_wrap(True)
        summary_label.set_wrap_mode(2)
        summary_label.add_css_class(
            "notification-popup-summary"
        )

        card.append(header)
        card.append(summary_label)

        if notification.body.strip():
            body_label = Gtk.Label(
                label=notification.body
            )
            body_label.set_xalign(0)
            body_label.set_wrap(True)
            body_label.set_wrap_mode(2)
            body_label.set_max_width_chars(48)
            body_label.add_css_class(
                "notification-popup-body"
            )

            card.append(body_label)
        if notification.actions:
            actions_row = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=5,
            )
            actions_row.add_css_class(
                "notification-popup-actions"
            )

            for action in notification.actions:
                action_button = Gtk.Button(
                    label=action.label
                )
                action_button.add_css_class(
                    "notification-popup-action-button"
                )
                action_button.connect(
                    "clicked",
                    self._on_action_clicked,
                    notification.notification_id,
                    action.key,
                )
                actions_row.append(action_button)

            card.append(actions_row)

        return card

    def _on_dismiss_clicked(
        self,
        _button: Gtk.Button,
        notification_id: int,
    ) -> None:
        self._cancel_timeout()
        dismiss_notification(notification_id)


    def _on_action_clicked(
        self,
        _button: Gtk.Button,
        notification_id: int,
        action_key: str,
    ) -> None:
        invoke_notification_action(
            notification_id,
            action_key,
        )

    def _on_timeout(
        self,
        notification_id: int,
    ) -> bool:
        self._timeout_source_id = None

        current = self._current_notification

        if (
            current is None
            or current.notification_id != notification_id
        ):
            return GLib.SOURCE_REMOVE

        self._current_notification = None
        self.set_child(None)
        self.hide()

        GLib.idle_add(self._process_store_change)

        return GLib.SOURCE_REMOVE

    def _hide_current_popup(self) -> None:
        self._cancel_timeout()
        self._current_notification = None
        self.set_child(None)
        self.hide()

        GLib.idle_add(self._process_store_change)

    def _cancel_timeout(self) -> None:
        if self._timeout_source_id is None:
            return

        GLib.source_remove(self._timeout_source_id)
        self._timeout_source_id = None

    def _on_close_request(
        self,
        _window: Gtk.Window,
    ) -> bool:
        self.set_visible(False)
        return True
