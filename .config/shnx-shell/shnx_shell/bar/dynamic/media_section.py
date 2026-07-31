from gi.repository import Gtk


class MediaSection(Gtk.Box):
    def __init__(self) -> None:
        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
        )

        self.add_css_class("dynamic-section")
        self.append(Gtk.Label(label="Media"))
