import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gtk

from shnx_shell.services.network import NetworkState, get_network_state


class WifiIndicator(Gtk.Button):
    def __init__(self) -> None:
        super().__init__(label="󰖩")

        self.add_css_class("status-button")
        self.add_css_class("wifi-button")

        self._refresh()
        GLib.timeout_add_seconds(15, self._refresh)

    def _refresh(self) -> bool:
        try:
            state = get_network_state()
        except Exception as error:
            print(f"Wi-Fi refresh failed: {error}")
            self.set_label("󰖪")
            self.set_tooltip_text("Wi-Fi unavailable")
            return GLib.SOURCE_CONTINUE

        self.set_label(self._get_icon(state))
        self.set_tooltip_text(self._get_tooltip(state))

        return GLib.SOURCE_CONTINUE

    @staticmethod
    def _get_icon(state: NetworkState) -> str:
        if not state.wifi_enabled:
            return "󰖪"

        if not state.connected:
            return "󰖪"

        return "󰖩"

    @staticmethod
    def _get_tooltip(state: NetworkState) -> str:
        if not state.wifi_enabled:
            return "Wi-Fi disabled"

        if not state.connected:
            return "Wi-Fi enabled\nNot connected"

        return (
            "Wi-Fi connected\n"
            f"{state.ssid or 'Unknown network'}"
        )
