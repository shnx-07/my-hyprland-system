from gi.repository import Gtk

from shnx_shell.bar.dynamic.clock_section import ClockSection
from shnx_shell.bar.dynamic.media_section import MediaSection


class DynamicIsland(Gtk.Box):
    def __init__(self) -> None:
        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )

        self.set_valign(Gtk.Align.CENTER)
        self.set_vexpand(False)

        self.add_css_class("dynamic-island")

        self.clock_section = ClockSection()
        self.media_section = MediaSection()

        self.add_section(self.clock_section)
        self.add_section(Gtk.Separator())
        self.add_section(self.media_section)

    def add_section(self, widget: Gtk.Widget) -> None:
        self.append(widget)
