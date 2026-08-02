import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from shnx_shell.services.system import (
    lock_session,
    power_off_system,
    reboot_system,
    suspend_system,
)


class PowerButton(Gtk.Button):
    def __init__(self) -> None:
        super().__init__(label="󰐥")

        self.add_css_class("status-button")
        self.add_css_class("power-button")
        self.set_tooltip_text("Power menu")

        self.connect(
            "clicked",
            self._on_clicked,
        )

    def _on_clicked(
        self,
        _button: Gtk.Button,
    ) -> None:
        popover = Gtk.Popover()
        popover.set_parent(self)
        popover.set_autohide(True)
        popover.add_css_class("power-popover")

        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )
        content.set_margin_top(8)
        content.set_margin_bottom(8)
        content.set_margin_start(8)
        content.set_margin_end(8)

        lock_button = Gtk.Button(label="Lock")
        suspend_button = Gtk.Button(label="Suspend")
        reboot_button = Gtk.Button(label="Reboot")
        power_off_button = Gtk.Button(label="Power Off")

        lock_button.add_css_class("power-menu-item")
        suspend_button.add_css_class("power-menu-item")
        reboot_button.add_css_class("power-menu-item")
        power_off_button.add_css_class("power-menu-item")
        power_off_button.add_css_class("power-menu-danger")

        lock_button.connect(
            "clicked",
            self._on_lock_clicked,
            popover,
        )
        suspend_button.connect(
            "clicked",
            self._on_suspend_clicked,
            popover,
        )
        reboot_button.connect(
            "clicked",
            self._on_reboot_clicked,
            popover,
        )
        power_off_button.connect(
            "clicked",
            self._on_power_off_clicked,
            popover,
        )

        content.append(lock_button)
        content.append(suspend_button)
        content.append(reboot_button)
        content.append(power_off_button)

        popover.set_child(content)
        popover.popup()

    def _on_lock_clicked(
        self,
        _button: Gtk.Button,
        popover: Gtk.Popover,
    ) -> None:
        popover.popdown()

        try:
            lock_session()
        except Exception as error:
            print(f"Lock failed: {error}")

    def _on_suspend_clicked(
        self,
        _button: Gtk.Button,
        popover: Gtk.Popover,
    ) -> None:
        popover.popdown()

        try:
            suspend_system()
        except Exception as error:
            print(f"Suspend failed: {error}")

    def _on_reboot_clicked(
        self,
        _button: Gtk.Button,
        popover: Gtk.Popover,
    ) -> None:
        popover.popdown()

        try:
            reboot_system()
        except Exception as error:
            print(f"Reboot failed: {error}")

    def _on_power_off_clicked(
        self,
        _button: Gtk.Button,
        popover: Gtk.Popover,
    ) -> None:
        popover.popdown()

        try:
            power_off_system()
        except Exception as error:
            print(f"Power off failed: {error}")
