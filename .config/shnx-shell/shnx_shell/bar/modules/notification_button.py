import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gtk

from shnx_shell.panels.control_center import ControlCenter
from shnx_shell.services.notifications.store import (
    notification_store,
)


class NotificationButton(Gtk.Button):
    def __init__(self) -> None:
        super().__init__()

        self.add_css_class("status-button")
        self.add_css_class("notification-button")

        self._popover: Gtk.Popover | None = None

        self._bell_label = Gtk.Label(label="󰂚")
        self._bell_label.add_css_class(
            "notification-bell-icon"
        )

        self._badge_label = Gtk.Label()
        self._badge_label.add_css_class(
            "notification-count-badge"
        )
        self._badge_label.set_halign(Gtk.Align.END)
        self._badge_label.set_valign(Gtk.Align.START)
        self._badge_label.set_visible(False)

        overlay = Gtk.Overlay()
        overlay.set_child(self._bell_label)
        overlay.add_overlay(self._badge_label)
        overlay.set_measure_overlay(
            self._badge_label,
            False,
        )

        self.set_child(overlay)

        notification_store.subscribe(
            self._on_store_changed
        )

        self.connect(
            "clicked",
            self._on_clicked,
        )

        self._refresh_button()

    def _on_store_changed(self) -> None:
        GLib.idle_add(self._refresh_button)

    def _refresh_button(self) -> bool:
        unread_count = notification_store.unread_count()
        total_count = notification_store.count()

        if unread_count > 0:
            visible_count = (
                "99+"
                if unread_count > 99
                else str(unread_count)
            )

            self._badge_label.set_label(visible_count)
            self._badge_label.set_visible(True)

            self.add_css_class("notification-unread")

            self.set_tooltip_text(
                f"{unread_count} unread notification"
                if unread_count == 1
                else f"{unread_count} unread notifications"
            )
        else:
            self._badge_label.set_visible(False)
            self.remove_css_class("notification-unread")

            if total_count > 0:
                self.set_tooltip_text(
                    f"{total_count} notification in history"
                    if total_count == 1
                    else f"{total_count} notifications in history"
                )
            else:
                self.set_tooltip_text(
                    "No notifications"
                )

        return GLib.SOURCE_REMOVE

    def _on_clicked(
        self,
        _button: Gtk.Button,
    ) -> None:
        if self._popover is None:
            self._popover = self._build_popover()

        if self._popover.get_visible():
            self._popover.popdown()
            return

        notification_store.mark_all_read()
        self._popover.popup()

    def _build_popover(self) -> Gtk.Popover:
        popover = Gtk.Popover()
        popover.set_parent(self)
        popover.set_autohide(True)
        popover.set_has_arrow(False)
        popover.add_css_class(
            "control-center-popover"
        )
        popover.set_child(ControlCenter())

        return popover
