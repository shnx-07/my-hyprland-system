from gi.repository import Gtk

from shnx_shell.bar.modules.clock import Clock


class ClockSection(Gtk.Box):
    def __init__(self) -> None:
        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
        )

        self.add_css_class("dynamic-section")
        self.add_css_class("clock-section")

        self.append(Clock())
