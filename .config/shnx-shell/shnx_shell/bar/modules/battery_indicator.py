import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gtk

from shnx_shell.services.battery import BatteryState, get_battery_state


class BatteryIndicator(Gtk.Button):
    def __init__(self) -> None:
        super().__init__(label="󰁹")

        self.add_css_class("status-button")
        self.add_css_class("battery-button")

        self._refresh()
        GLib.timeout_add_seconds(30, self._refresh)

    def _refresh(self) -> bool:
        try:
            state = get_battery_state()
        except Exception as error:
            print(f"Battery refresh failed: {error}")
            self.set_label("󰂑")
            self.set_tooltip_text("Battery unavailable")
            return GLib.SOURCE_CONTINUE

        if state is None:
            self.set_label("󰂑")
            self.set_tooltip_text("Battery unavailable")
            return GLib.SOURCE_CONTINUE

        self.set_label(self._get_icon(state))
        self.set_tooltip_text(
            f"Battery: {state.percentage}%\n"
            f"Status: {state.status}"
        )

        return GLib.SOURCE_CONTINUE

    @staticmethod
    def _get_icon(state: BatteryState) -> str:
        if state.is_charging:
            return "󰂄"

        percentage = state.percentage

        if percentage >= 90:
            return "󰁹"
        if percentage >= 80:
            return "󰂂"
        if percentage >= 70:
            return "󰂁"
        if percentage >= 60:
            return "󰂀"
        if percentage >= 50:
            return "󰁿"
        if percentage >= 40:
            return "󰁾"
        if percentage >= 30:
            return "󰁽"
        if percentage >= 20:
            return "󰁼"
        if percentage >= 10:
            return "󰁻"

        return "󰂎"
