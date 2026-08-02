import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gtk

from shnx_shell.services.bluetooth import (
    BluetoothState,
    get_bluetooth_state,
)


class BluetoothIndicator(Gtk.Button):
    def __init__(self) -> None:
        super().__init__(label="󰂯")

        self.add_css_class("status-button")
        self.add_css_class("bluetooth-button")

        self._refresh()
        GLib.timeout_add_seconds(15, self._refresh)

    def _refresh(self) -> bool:
        try:
            state = get_bluetooth_state()
        except Exception as error:
            print(f"Bluetooth refresh failed: {error}")
            self.set_label("󰂲")
            self.set_tooltip_text("Bluetooth unavailable")
            return GLib.SOURCE_CONTINUE

        self.set_label(self._get_icon(state))
        self.set_tooltip_text(self._get_tooltip(state))

        return GLib.SOURCE_CONTINUE

    @staticmethod
    def _get_icon(state: BluetoothState) -> str:
        if not state.available or not state.powered:
            return "󰂲"

        if state.connected_devices:
            return "󰂱"

        return "󰂯"

    @staticmethod
    def _get_tooltip(state: BluetoothState) -> str:
        if not state.available:
            return "Bluetooth unavailable"

        if not state.powered:
            return "Bluetooth disabled"

        if not state.connected_devices:
            return "Bluetooth enabled\nNo connected devices"

        devices = "\n".join(state.connected_devices)

        return f"Bluetooth connected\n{devices}"
