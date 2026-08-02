from typing import Any

import gi

gi.require_version("Gio", "2.0")

from gi.repository import Gio, GLib

from shnx_shell.services.notifications.shape import (
    Notification,
    NotificationAction,
)
from shnx_shell.services.notifications.store import notification_store

from shnx_shell.services.notifications.state import (
    is_dnd_enabled,
)


BUS_NAME = "org.freedesktop.Notifications"
OBJECT_PATH = "/org/freedesktop/Notifications"
INTERFACE_NAME = "org.freedesktop.Notifications"


INTERFACE_XML = """
<node>
  <interface name="org.freedesktop.Notifications">
    <method name="GetCapabilities">
      <arg name="capabilities" type="as" direction="out"/>
    </method>

    <method name="Notify">
      <arg name="app_name" type="s" direction="in"/>
      <arg name="replaces_id" type="u" direction="in"/>
      <arg name="app_icon" type="s" direction="in"/>
      <arg name="summary" type="s" direction="in"/>
      <arg name="body" type="s" direction="in"/>
      <arg name="actions" type="as" direction="in"/>
      <arg name="hints" type="a{sv}" direction="in"/>
      <arg name="expire_timeout" type="i" direction="in"/>
      <arg name="id" type="u" direction="out"/>
    </method>

    <method name="CloseNotification">
      <arg name="id" type="u" direction="in"/>
    </method>

    <method name="GetServerInformation">
      <arg name="name" type="s" direction="out"/>
      <arg name="vendor" type="s" direction="out"/>
      <arg name="version" type="s" direction="out"/>
      <arg name="spec_version" type="s" direction="out"/>
    </method>

    <signal name="NotificationClosed">
      <arg name="id" type="u"/>
      <arg name="reason" type="u"/>
    </signal>

    <signal name="ActionInvoked">
      <arg name="id" type="u"/>
      <arg name="action_key" type="s"/>
    </signal>
  </interface>
</node>
"""


class NotificationDaemon:
    def __init__(self) -> None:
        node_info = Gio.DBusNodeInfo.new_for_xml(INTERFACE_XML)

        self._interface_info = node_info.interfaces[0]
        self._owner_id: int | None = None
        self._registration_id: int | None = None
        self._connection: Gio.DBusConnection | None = None
        self._next_notification_id = 1

    def start(self) -> None:
        if self._owner_id is not None:
            return

        self._owner_id = Gio.bus_own_name(
            Gio.BusType.SESSION,
            BUS_NAME,
            Gio.BusNameOwnerFlags.NONE,
            self._on_bus_acquired,
            self._on_name_acquired,
            self._on_name_lost,
        )

    def stop(self) -> None:
        if (
            self._connection is not None
            and self._registration_id is not None
        ):
            self._connection.unregister_object(
                self._registration_id
            )

        self._registration_id = None
        self._connection = None

        if self._owner_id is not None:
            Gio.bus_unown_name(self._owner_id)

        self._owner_id = None

    def _on_bus_acquired(
        self,
        connection: Gio.DBusConnection,
        _name: str,
    ) -> None:
        self._connection = connection

        self._registration_id = connection.register_object(
            OBJECT_PATH,
            self._interface_info,
            self._on_method_call,
            None,
            None,
        )

    def _on_name_acquired(
        self,
        _connection: Gio.DBusConnection,
        name: str,
    ) -> None:
        print(f"Notification DBus name acquired: {name}")

    def _on_name_lost(
        self,
        _connection: Gio.DBusConnection | None,
        name: str,
    ) -> None:
        print(f"Notification DBus name lost: {name}")

    def _on_method_call(
        self,
        _connection: Gio.DBusConnection,
        _sender: str,
        _object_path: str,
        _interface_name: str,
        method_name: str,
        parameters: GLib.Variant,
        invocation: Gio.DBusMethodInvocation,
    ) -> None:
        try:
            if method_name == "GetCapabilities":
                self._handle_get_capabilities(invocation)
                return

            if method_name == "GetServerInformation":
                self._handle_get_server_information(invocation)
                return

            if method_name == "Notify":
                self._handle_notify(parameters, invocation)
                return

            if method_name == "CloseNotification":
                self._handle_close_notification(
                    parameters,
                    invocation,
                )
                return

            invocation.return_dbus_error(
                "org.freedesktop.DBus.Error.UnknownMethod",
                f"Unknown method: {method_name}",
            )

        except Exception as error:
            print(f"Notification DBus method failed: {error}")

            invocation.return_dbus_error(
                "org.freedesktop.Notifications.Error.Failed",
                str(error),
            )

    @staticmethod
    def _handle_get_capabilities(
        invocation: Gio.DBusMethodInvocation,
    ) -> None:
        capabilities = [
            "actions",
            "body",
            "body-markup",
            "persistence",
        ]

        invocation.return_value(
            GLib.Variant("(as)", (capabilities,))
        )

    @staticmethod
    def _handle_get_server_information(
        invocation: Gio.DBusMethodInvocation,
    ) -> None:
        invocation.return_value(
            GLib.Variant(
                "(ssss)",
                (
                    "Shnx Shell",
                    "Shnx",
                    "0.1.0",
                    "1.2",
                ),
            )
        )

    def _handle_notify(
        self,
        parameters: GLib.Variant,
        invocation: Gio.DBusMethodInvocation,
    ) -> None:
        (
            app_name,
            replaces_id,
            app_icon,
            summary,
            body,
            raw_actions,
            raw_hints,
            expire_timeout,
        ) = parameters.unpack()

        actions = self._parse_actions(raw_actions)
        hints = self._unpack_hints(raw_hints)

        notification_id = self._resolve_notification_id(
            replaces_id
        )

        dnd_enabled = is_dnd_enabled()

        print(
            f"Notification received: {summary!r}, "
            f"DND={dnd_enabled}"
        )

        notification = Notification(
            notification_id=notification_id,
            app_name=app_name,
            app_icon=app_icon,
            summary=summary,
            body=body,
            actions=actions,
            hints=hints,
            timeout=expire_timeout,
            suppressed=dnd_enabled,
        )

        if replaces_id != 0:
            replaced = notification_store.replace(notification)

            if not replaced:
                notification_store.add(notification)
        else:
            notification_store.add(notification)

        invocation.return_value(
            GLib.Variant("(u)", (notification_id,))
        )

    def _handle_close_notification(
        self,
        parameters: GLib.Variant,
        invocation: Gio.DBusMethodInvocation,
    ) -> None:
        (notification_id,) = parameters.unpack()

        removed = notification_store.remove(notification_id)

        if removed:
            self.emit_notification_closed(
                notification_id,
                reason=3,
            )

        invocation.return_value(None)

    def _resolve_notification_id(
        self,
        replaces_id: int,
    ) -> int:
        if replaces_id != 0:
            existing_ids = {
                notification.notification_id
                for notification in notification_store.get_all()
            }

            if replaces_id in existing_ids:
                return replaces_id

        notification_id = self._next_notification_id
        self._next_notification_id += 1

        return notification_id

    @staticmethod
    def _parse_actions(
        raw_actions: list[str],
    ) -> tuple[NotificationAction, ...]:
        actions: list[NotificationAction] = []

        for index in range(0, len(raw_actions) - 1, 2):
            actions.append(
                NotificationAction(
                    key=raw_actions[index],
                    label=raw_actions[index + 1],
                )
            )

        return tuple(actions)

    @staticmethod
    def _unpack_hints(
        raw_hints: dict[str, Any],
    ) -> dict[str, Any]:
        hints: dict[str, Any] = {}

        for key, value in raw_hints.items():
            if isinstance(value, GLib.Variant):
                hints[key] = value.unpack()
            else:
                hints[key] = value

        return hints

    def emit_notification_closed(
        self,
        notification_id: int,
        reason: int,
    ) -> None:
        if self._connection is None:
            return

        self._connection.emit_signal(
            None,
            OBJECT_PATH,
            INTERFACE_NAME,
            "NotificationClosed",
            GLib.Variant(
                "(uu)",
                (notification_id, reason),
            ),
        )

    def emit_action_invoked(
        self,
        notification_id: int,
        action_key: str,
    ) -> None:
        if self._connection is None:
            return

        self._connection.emit_signal(
            None,
            OBJECT_PATH,
            INTERFACE_NAME,
            "ActionInvoked",
            GLib.Variant(
                "(us)",
                (notification_id, action_key),
            ),
        )


notification_daemon = NotificationDaemon()
