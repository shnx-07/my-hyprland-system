from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")


from gi.repository import Gdk, Gio, Gtk

from shnx_shell.bar.bar import Bar

from shnx_shell.brain.lifecycle import (
    shutdown,
    startup,
)

from shnx_shell.popups.notification_popup import (
    NotificationPopup,
)

class ShnxApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id="com.shnx.shell",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

        self._bar: Bar | None = None
        self._notification_popup: NotificationPopup | None = None

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)
        self._load_css()
        startup()

    def do_activate(self) -> None:
        if self._bar is None:
            self._bar = Bar(self)

        if self._notification_popup is None:
            self._notification_popup = NotificationPopup(self)

        self._bar.present()

    def do_shutdown(self) -> None:
        shutdown()
        Gtk.Application.do_shutdown(self)

    def _load_css(self) -> None:
        css_path = (
            Path(__file__).resolve().parent.parent
            / "styles"
            / "main.css"
        )

        provider = Gtk.CssProvider()
        provider.load_from_path(str(css_path))

        display = Gdk.Display.get_default()

        if display is None:
            raise RuntimeError("No GTK display is available")

        Gtk.StyleContext.add_provider_for_display(
            display,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )


def run() -> int:
    app = ShnxApplication()
    return app.run(None)
