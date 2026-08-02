import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gtk

from shnx_shell.services.notifications.shape import Notification
from shnx_shell.services.notifications.store import notification_store

from shnx_shell.services.notifications.actions import (
    clear_notifications,
    dismiss_notification,
)

from shnx_shell.services.notifications.actions import (
    clear_notifications,
    dismiss_notification,
    invoke_notification_action,
)


class NotificationCenter(Gtk.Box):
    def __init__(self) -> None:
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
        )

        self.add_css_class("notification-center")

        self.clear_button: Gtk.Button | None = None
        self.scroll: Gtk.ScrolledWindow | None = None
        self.notification_list: Gtk.Box | None = None
        self.empty_state: Gtk.Label | None = None

        self.append(self._build_header())
        self.append(self._build_scroll_area())

        notification_store.subscribe(
            self._on_store_changed
        )

        

        self._refresh_notifications()

    def _build_header(self) -> Gtk.Box:
        header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )
        header.add_css_class("notification-header")

        title = Gtk.Label(label="Notifications")
        title.set_xalign(0)
        title.set_hexpand(True)
        title.add_css_class("notification-title")

        self.clear_button = Gtk.Button(label="Clear")
        self.clear_button.add_css_class(
            "notification-clear-button"
        )
        self.clear_button.connect(
            "clicked",
            self._on_clear_clicked,
        )

        header.append(title)
        header.append(self.clear_button)

        return header

    def _build_scroll_area(self) -> Gtk.ScrolledWindow:
        self.empty_state = Gtk.Label(
            label="No notifications"
        )
        self.empty_state.set_hexpand(True)
        self.empty_state.set_vexpand(True)
        self.empty_state.set_halign(Gtk.Align.CENTER)
        self.empty_state.set_valign(Gtk.Align.CENTER)
        self.empty_state.add_css_class(
            "notification-empty-state"
        )

        self.notification_list = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
        )
        self.notification_list.add_css_class(
            "notification-list"
        )

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC,
        )
        self.scroll.set_min_content_height(180)
        self.scroll.set_max_content_height(300)
        self.scroll.set_propagate_natural_height(True)
        self.scroll.add_css_class("notification-scroll")

        return self.scroll

    def _on_store_changed(self) -> None:
        GLib.idle_add(self._refresh_notifications)

    def _refresh_notifications(self) -> bool:
        if (
            self.notification_list is None
            or self.empty_state is None
            or self.scroll is None
        ):
            return GLib.SOURCE_REMOVE

        self._clear_notification_widgets()

        notifications = notification_store.get_all()

        if self.clear_button is not None:
            self.clear_button.set_sensitive(
                bool(notifications)
            )

        if not notifications:
            self.scroll.set_child(self.empty_state)
            return GLib.SOURCE_REMOVE

        for notification in notifications:
            card = self._build_notification_card(
                notification
            )
            self.notification_list.append(card)

        self.scroll.set_child(self.notification_list)

        return GLib.SOURCE_REMOVE

    def _clear_notification_widgets(self) -> None:
        if self.notification_list is None:
            return

        child = self.notification_list.get_first_child()

        while child is not None:
            next_child = child.get_next_sibling()
            self.notification_list.remove(child)
            child = next_child

    def _build_notification_card(
        self,
        notification: Notification,
    ) -> Gtk.Box:
        card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )
        card.add_css_class("notification-card")

        header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )
        header.add_css_class("notification-card-header")

        app_name = notification.app_name.strip()

        app_label = Gtk.Label(
            label=app_name or "Application"
        )
        app_label.set_xalign(0)
        app_label.set_hexpand(True)
        app_label.set_ellipsize(3)
        app_label.add_css_class(
            "notification-app-name"
        )

        if notification.suppressed:
            app_label.set_label(
                f"{app_label.get_label()} · DND"
            )

        time_label = Gtk.Label(
            label=notification.created_at.strftime(
                "%H:%M"
            )
        )
        time_label.add_css_class(
            "notification-time"
        )

        dismiss_button = Gtk.Button(label="󰅖")
        dismiss_button.add_css_class(
            "notification-dismiss-button"
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
        header.append(time_label)
        header.append(dismiss_button)

        summary_label = Gtk.Label(
            label=notification.summary
        )
        summary_label.set_xalign(0)
        summary_label.set_wrap(True)
        summary_label.set_wrap_mode(2)
        summary_label.add_css_class(
            "notification-summary"
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
            body_label.set_selectable(False)
            body_label.add_css_class(
                "notification-body"
            )

            card.append(body_label)

        if notification.actions:
            actions_row = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=6,
            )
            actions_row.add_css_class(
                "notification-actions"
            )

            for action in notification.actions:
                action_button = Gtk.Button(
                    label=action.label
                )
                action_button.add_css_class(
                    "notification-action-button"
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
        dismiss_notification(notification_id)

    def _on_clear_clicked(
        self,
        _button: Gtk.Button,
    ) -> None:
        clear_notifications()

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
