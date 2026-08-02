import os
import socket
import threading

import gi

gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import GLib, Gtk, Gtk4LayerShell
from shnx_shell.launcher.app_loader import find_app_icon
from shnx_shell.bar.dynamic.dynamic_island import DynamicIsland
from shnx_shell.bar.modules.wifi_indicator import WifiIndicator
from shnx_shell.bar.modules.battery_indicator import BatteryIndicator
from shnx_shell.bar.modules.bluetooth_indicator import BluetoothIndicator
from shnx_shell.bar.modules.notification_button import NotificationButton
from shnx_shell.bar.modules.power_button import PowerButton
from shnx_shell.services.hyprland import (
    get_active_window_class,
    get_active_workspace,
    get_open_workspaces,
    switch_workspace,
)


class Bar(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)

        bar_height = 48

        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(
            self,
            Gtk4LayerShell.Layer.TOP,
        )

        Gtk4LayerShell.set_anchor(
            self,
            Gtk4LayerShell.Edge.TOP,
            True,
        )
        Gtk4LayerShell.set_anchor(
            self,
            Gtk4LayerShell.Edge.LEFT,
            True,
        )
        Gtk4LayerShell.set_anchor(
            self,
            Gtk4LayerShell.Edge.RIGHT,
            True,
        )

        Gtk4LayerShell.set_exclusive_zone(
            self,
            bar_height,
        )

        self.set_default_size(0, bar_height)
        self.set_title("Shnx Shell")
        self.connect("close-request", self._on_close_request)

        root = Gtk.CenterBox()
        #Left side button
        self.workspace_group: Gtk.Box | None = None
        self._workspace_state: tuple[tuple[int, ...], int] | None = None

        #right side button 
        

        left = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )

        center = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )

        right = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )

        #left side
        left.append(self._build_left_section())
        center.append(DynamicIsland())
        center.set_valign(Gtk.Align.CENTER)
        center.set_vexpand(False)

        #right side
        right.append(self._build_right_section())


        root.set_start_widget(left)
        root.set_center_widget(center)
        root.set_end_widget(right)

        self.set_child(root)
        self._start_hyprland_listener()


    def _on_close_request(self, _window: Gtk.Window) -> bool:
        application = self.get_application()

        if application is not None:
            application.quit()

        return False


    #--------------------------------------------------------
    #                    LEFT SIDE
    #--------------------------------------------------------

    def _build_left_section(self) -> Gtk.Box:
        section = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
        )

        section.set_valign(Gtk.Align.CENTER)
        section.add_css_class("bar-left-section")

        arch_button = Gtk.Button(label="")
        arch_button.add_css_class("bar-action-button")
        arch_button.add_css_class("arch-button")

        self.workspace_group = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=2,
        )

        self.workspace_group.add_css_class("workspace-group")
        self._refresh_workspaces()

        self.active_app_image = Gtk.Image.new_from_icon_name("utilities-terminal-symbolic")

        self.active_app_button = Gtk.Button()
        self.active_app_button.set_child(self.active_app_image)
        self.active_app_button.add_css_class("bar-action-button")
        self.active_app_button.add_css_class("active-app-button")

        self._refresh_active_app()

        section.append(arch_button)
        section.append(self.workspace_group)
        section.append(self.active_app_button)

        return section

    def _refresh_workspaces(self) -> bool:
        if self.workspace_group is None:
            return GLib.SOURCE_REMOVE

        try:
            open_workspaces = tuple(get_open_workspaces())
            active_workspace = get_active_workspace()
        except Exception as error:
            print(f"Workspace refresh failed: {error}")
            return GLib.SOURCE_REMOVE

        state = (open_workspaces, active_workspace)

        if state == self._workspace_state:
            return GLib.SOURCE_REMOVE

        child = self.workspace_group.get_first_child()

        while child is not None:
            next_child = child.get_next_sibling()
            self.workspace_group.remove(child)
            child = next_child

        for workspace_id in open_workspaces:
            workspace = Gtk.Button(label=str(workspace_id))
            workspace.add_css_class("workspace-item")

            if workspace_id == active_workspace:
                workspace.add_css_class("workspace-active")

            workspace.connect(
                "clicked",
                self._on_workspace_clicked,
                workspace_id,
            )

            self.workspace_group.append(workspace)

        self._workspace_state = state
        return GLib.SOURCE_REMOVE


    def _start_hyprland_listener(self) -> None:
        thread = threading.Thread(
            target=self._listen_for_hyprland_events,
            daemon=True,
        )
        thread.start()


    def _listen_for_hyprland_events(self) -> None:
        runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
        instance = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")

        if runtime_dir is None or instance is None:
            print("Hyprland environment variables are unavailable")
            return

        socket_path = (
            f"{runtime_dir}/hypr/{instance}/.socket2.sock"
        )

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as event_socket:
                event_socket.connect(socket_path)

                buffer = ""

                while True:
                    data = event_socket.recv(4096)

                    if not data:
                        return

                    buffer += data.decode("utf-8", errors="replace")

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        self._handle_hyprland_event(line)

        except OSError as error:
            print(f"Hyprland event listener failed: {error}")


    def _handle_hyprland_event(self, event: str) -> None:
        refresh_events = (
            "workspace>>",
            "workspacev2>>",
            "focusedmon>>",
            "focusedmonv2>>",
            "createworkspace>>",
            "createworkspacev2>>",
            "destroyworkspace>>",
            "destroyworkspacev2>>",
            "moveworkspace>>",
            "moveworkspacev2>>",
            "renameworkspace>>",
        )

        if event.startswith(refresh_events):
            GLib.idle_add(self._refresh_workspaces)

        if event.startswith(("activewindow>>", "activewindowv2>>")):
            GLib.idle_add(self._refresh_active_app)


    def _on_workspace_clicked(
        self,
        _button: Gtk.Button,
        workspace_id: int,
    ) -> None:
        try:
            switch_workspace(workspace_id)
        except Exception as error:
            print(f"Workspace switch failed: {error}")


    

    def _refresh_active_app(self) -> bool:
        try:
            app_class = get_active_window_class()
        except Exception as error:
            print(f"Active app refresh failed: {error}")
            return GLib.SOURCE_REMOVE

        icon_name = find_app_icon(app_class)

        self.active_app_image.set_from_icon_name(icon_name)
        self.active_app_button.set_tooltip_text(app_class)

        return GLib.SOURCE_REMOVE

    #--------------------------------------------------------
    #                    RIGHT SIDE
    #--------------------------------------------------------

    def _build_right_section(self) -> Gtk.Box:
        section = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )

        section.set_valign(Gtk.Align.CENTER)
        section.add_css_class("bar-right-section")

        


        section.append(BatteryIndicator())
        section.append(WifiIndicator())
        section.append(BluetoothIndicator())
        section.append(NotificationButton())
        section.append(PowerButton())

        return section

