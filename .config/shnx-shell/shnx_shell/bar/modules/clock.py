from datetime import datetime

from gi.repository import GLib, Gtk


class Clock(Gtk.Label):
    def __init__(self) -> None:
        super().__init__()

        self._update_time()
        GLib.timeout_add_seconds(1, self._update_time)

    def _update_time(self) -> bool:
        self.set_label(datetime.now().strftime("%H:%M"))
        return GLib.SOURCE_CONTINUE
