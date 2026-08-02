import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gtk

from shnx_shell.panels.notification_center import NotificationCenter

from shnx_shell.services.system_monitor import (
    CpuTimes,
    calculate_cpu_percentage,
    get_cpu_times,
    get_disk_percentage,
    get_ram_percentage,
)

from shnx_shell.services.notifications.state import (
    is_dnd_enabled,
    set_dnd_enabled,
)

from shnx_shell.services.network import (
    get_network_state,
    get_vpn_state,
    set_wifi_enabled,
)
from shnx_shell.services.bluetooth import (
    get_bluetooth_state,
    set_bluetooth_powered,
)

from shnx_shell.services.night_light import (
    PRESETS,
    NightLightPreset,
    set_night_light_temperature,
)

from shnx_shell.services.audio import (
    get_audio_state,
    set_muted,
    set_volume,
)

from shnx_shell.services.brightness import (
    get_brightness_state,
    set_brightness,
)


class ControlCenter(Gtk.Box):
    def __init__(self) -> None:
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
        )

        self.set_size_request(390, -1)
        self.add_css_class("control-center")

        self.cpu_value_label: Gtk.Label | None = None
        self.ram_value_label: Gtk.Label | None = None
        self.disk_value_label: Gtk.Label | None = None

        self._previous_cpu_times: CpuTimes | None = None
        self.dnd_toggle: Gtk.ToggleButton | None = None

        self.airplane_toggle: Gtk.ToggleButton | None = None

        self._wifi_before_airplane = False
        self._bluetooth_before_airplane = False

        self.night_light_button: Gtk.MenuButton | None = None
        self._night_light_temperature: int | None = None

        self.volume_slider: Gtk.Scale | None = None
        self.volume_icon_button: Gtk.Button | None = None
        self._updating_volume_slider = False

        self.brightness_slider: Gtk.Scale | None = None
        self.brightness_icon_button: Gtk.Button | None = None
        self._updating_brightness_slider = False

        self.append(self._build_metrics_row())
        self.append(self._build_quick_toggles())
        self.append(self._build_slider_section())
        self.append(NotificationCenter())
        self._refresh_metrics()
        GLib.timeout_add_seconds(2, self._refresh_metrics)

    def _build_metrics_row(self) -> Gtk.Box:
        section = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )
        section.set_homogeneous(True)
        section.add_css_class("system-metrics")

        cpu_button, self.cpu_value_label = self._build_metric_button(
            icon="󰻠",
            label="CPU",
            value="--%",
        )

        ram_button, self.ram_value_label = self._build_metric_button(
            icon="󰍛",
            label="RAM",
            value="--%",
        )

        disk_button, self.disk_value_label = self._build_metric_button(
            icon="󰋊",
            label="Disk",
            value="--%",
        )

        section.append(cpu_button)
        section.append(ram_button)
        section.append(disk_button)

        return section


    @staticmethod
    def _build_metric_button(
        icon: str,
        label: str,
        value: str,
    ) -> tuple[Gtk.Button, Gtk.Label]:
        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2,
        )

        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("metric-icon")

        name_label = Gtk.Label(label=label)
        name_label.add_css_class("metric-name")

        value_label = Gtk.Label(label=value)
        value_label.add_css_class("metric-value")

        content.append(icon_label)
        content.append(name_label)
        content.append(value_label)

        button = Gtk.Button()
        button.set_child(content)
        button.add_css_class("metric-button")
        button.set_sensitive(False)

        return button, value_label

    def _refresh_metrics(self) -> bool:
        try:
            current_cpu_times = get_cpu_times()
            ram_percentage = get_ram_percentage()
            disk_percentage = get_disk_percentage()
        except Exception as error:
            print(f"System metrics refresh failed: {error}")
            return GLib.SOURCE_CONTINUE

        if self._previous_cpu_times is None:
            cpu_percentage = 0.0
        else:
            cpu_percentage = calculate_cpu_percentage(
                self._previous_cpu_times,
                current_cpu_times,
            )

        self._previous_cpu_times = current_cpu_times

        if self.cpu_value_label is not None:
            self.cpu_value_label.set_label(
                f"{cpu_percentage:.0f}%"
            )

        if self.ram_value_label is not None:
            self.ram_value_label.set_label(
                f"{ram_percentage:.0f}%"
            )

        if self.disk_value_label is not None:
            self.disk_value_label.set_label(
                f"{disk_percentage:.0f}%"
            )

        return GLib.SOURCE_CONTINUE


    def _build_quick_toggles(self) -> Gtk.Box:
        section = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )
        section.set_homogeneous(True)
        section.add_css_class("quick-toggle-group")

        self.airplane_toggle = self._build_toggle(
            icon="󰀝",
            label="Airplane",
            sensitive=True,
        )
        self.airplane_toggle.set_tooltip_text(
            "Airplane Mode disabled"
        )
        self.airplane_toggle.connect(
            "toggled",
            self._on_airplane_toggled,
        )

        self.dnd_toggle = self._build_toggle(
            icon="󰂛",
            label="DND",
            sensitive=True,
        )
        self.dnd_toggle.set_active(is_dnd_enabled())

        if self.dnd_toggle.get_active():
            self.dnd_toggle.set_tooltip_text(
                "Do Not Disturb enabled"
            )
        else:
            self.dnd_toggle.set_tooltip_text(
                "Do Not Disturb disabled"
            )

        self.dnd_toggle.connect(
            "toggled",
            self._on_dnd_toggled,
        )

        self.night_light_button = self._build_night_light_button()

        vpn_state = get_vpn_state()

        vpn_toggle = self._build_toggle(
            icon="󰦝",
            label="VPN",
            sensitive=vpn_state.available,
        )

        vpn_toggle.set_active(vpn_state.active)

        if not vpn_state.available:
            vpn_toggle.set_tooltip_text(
                "No VPN profile configured"
            )
        elif vpn_state.active:
            vpn_toggle.set_tooltip_text(
                "VPN connected"
            )
        else:
            vpn_toggle.set_tooltip_text(
                "VPN disconnected"
            )

        section.append(self.airplane_toggle)
        section.append(self.dnd_toggle)
        section.append(self.night_light_button)
        section.append(vpn_toggle)

        return section

    @staticmethod
    def _build_toggle(
        icon: str,
        label: str,
        sensitive: bool = False,
    ) -> Gtk.ToggleButton:
        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4,
        )

        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("quick-toggle-icon")

        text_label = Gtk.Label(label=label)
        text_label.add_css_class("quick-toggle-label")

        content.append(icon_label)
        content.append(text_label)

        toggle = Gtk.ToggleButton()
        toggle.set_child(content)
        toggle.add_css_class("quick-toggle")
        toggle.set_sensitive(sensitive)

        return toggle

    def _on_dnd_toggled(
        self,
        toggle: Gtk.ToggleButton,
    ) -> None:
        enabled = toggle.get_active()

        set_dnd_enabled(enabled)

        print(f"DND state changed: {enabled}")

        if enabled:
            toggle.set_tooltip_text(
                "Do Not Disturb enabled"
            )
        else:
            toggle.set_tooltip_text(
                "Do Not Disturb disabled"
            )

    def _on_airplane_toggled(
        self,
        toggle: Gtk.ToggleButton,
    ) -> None:
        enabled = toggle.get_active()

        try:
            if enabled:
                network_state = get_network_state()
                bluetooth_state = get_bluetooth_state()

                self._wifi_before_airplane = (
                    network_state.wifi_enabled
                )
                self._bluetooth_before_airplane = (
                    bluetooth_state.available
                    and bluetooth_state.powered
                )

                if self._wifi_before_airplane:
                    set_wifi_enabled(False)

                if self._bluetooth_before_airplane:
                    set_bluetooth_powered(False)

                toggle.set_tooltip_text(
                    "Airplane Mode enabled"
                )

            else:
                if self._wifi_before_airplane:
                    set_wifi_enabled(True)

                if self._bluetooth_before_airplane:
                    set_bluetooth_powered(True)

                toggle.set_tooltip_text(
                    "Airplane Mode disabled"
                )

        except Exception as error:
            print(f"Airplane Mode failed: {error}")

            toggle.handler_block_by_func(
                self._on_airplane_toggled
            )
            toggle.set_active(not enabled)
            toggle.handler_unblock_by_func(
                self._on_airplane_toggled
            )

            toggle.set_tooltip_text(
                "Airplane Mode unavailable"
            )


    def _build_slider_section(self) -> Gtk.Box:
        section = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
        )
        section.add_css_class("control-slider-section")

        volume_row = self._build_volume_slider_row()
        section.append(volume_row)

        brightness_row = self._build_brightness_slider_row()
        section.append(brightness_row)

        return section


    def _build_volume_slider_row(self) -> Gtk.Box:
        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
        )
        row.add_css_class("control-slider-row")

        self.volume_icon_button = Gtk.Button()
        self.volume_icon_button.add_css_class("control-slider-icon-button")
        self.volume_icon_button.connect(
            "clicked",
            self._on_volume_icon_clicked,
        )

        text_label = Gtk.Label(label="Volume")
        text_label.set_width_chars(10)
        text_label.set_xalign(0)
        text_label.add_css_class("control-slider-label")

        self.volume_slider = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0,
            100,
            1,
        )
        self.volume_slider.set_draw_value(False)
        self.volume_slider.set_hexpand(True)
        self.volume_slider.set_sensitive(True)
        self.volume_slider.add_css_class("control-slider")
        self.volume_slider.connect(
            "value-changed",
            self._on_volume_changed,
        )

        row.append(self.volume_icon_button)
        row.append(text_label)
        row.append(self.volume_slider)

        self._refresh_volume()

        return row
    
    def _build_brightness_slider_row(self) -> Gtk.Box:
        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
        )
        row.add_css_class("control-slider-row")

        self.brightness_icon_button = Gtk.Button(label="󰃠")
        self.brightness_icon_button.add_css_class(
            "control-slider-icon-button"
        )
        self.brightness_icon_button.set_sensitive(False)

        text_label = Gtk.Label(label="Brightness")
        text_label.set_width_chars(10)
        text_label.set_xalign(0)
        text_label.add_css_class("control-slider-label")

        self.brightness_slider = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            1,
            100,
            1,
        )
        self.brightness_slider.set_draw_value(False)
        self.brightness_slider.set_hexpand(True)
        self.brightness_slider.set_sensitive(True)
        self.brightness_slider.add_css_class("control-slider")
        self.brightness_slider.connect(
            "value-changed",
            self._on_brightness_changed,
        )

        row.append(self.brightness_icon_button)
        row.append(text_label)
        row.append(self.brightness_slider)

        self._refresh_brightness()

        return row
    
    def _refresh_volume(self) -> None:
        try:
            state = get_audio_state()
        except Exception as error:
            print(f"Volume refresh failed: {error}")

            if self.volume_slider is not None:
                self.volume_slider.set_sensitive(False)

            if self.volume_icon_button is not None:
                self.volume_icon_button.set_label("󰝟")
                self.volume_icon_button.set_tooltip_text(
                    "Audio unavailable"
                )

            return

        if self.volume_slider is not None:
            self._updating_volume_slider = True
            self.volume_slider.set_value(state.volume)
            self._updating_volume_slider = False

        self._update_volume_icon(
            volume=state.volume,
            muted=state.muted,
        )


    def _update_volume_icon(
        self,
        volume: int,
        muted: bool,
    ) -> None:
        if self.volume_icon_button is None:
            return

        if muted or volume == 0:
            icon = "󰝟"
            tooltip = "Unmute"
        elif volume < 35:
            icon = "󰕿"
            tooltip = f"Volume: {volume}%"
        elif volume < 70:
            icon = "󰖀"
            tooltip = f"Volume: {volume}%"
        else:
            icon = "󰕾"
            tooltip = f"Volume: {volume}%"

        self.volume_icon_button.set_label(icon)
        self.volume_icon_button.set_tooltip_text(tooltip)


    def _on_volume_changed(
        self,
        slider: Gtk.Scale,
    ) -> None:
        if self._updating_volume_slider:
            return

        volume = round(slider.get_value())

        try:
            set_volume(volume)

            state = get_audio_state()

            if state.muted and volume > 0:
                set_muted(False)
                state = get_audio_state()

            self._update_volume_icon(
                volume=state.volume,
                muted=state.muted,
            )

        except Exception as error:
            print(f"Volume change failed: {error}")
            self._refresh_volume()


    def _on_volume_icon_clicked(
        self,
        _button: Gtk.Button,
    ) -> None:
        try:
            state = get_audio_state()
            set_muted(not state.muted)
            self._refresh_volume()

        except Exception as error:
            print(f"Volume mute failed: {error}")

    def _refresh_brightness(self) -> None:
        try:
            state = get_brightness_state()
        except Exception as error:
            print(f"Brightness refresh failed: {error}")

            if self.brightness_slider is not None:
                self.brightness_slider.set_sensitive(False)

            if self.brightness_icon_button is not None:
                self.brightness_icon_button.set_label("󰃞")
                self.brightness_icon_button.set_tooltip_text(
                    "Brightness unavailable"
                )

            return

        if self.brightness_slider is not None:
            self._updating_brightness_slider = True
            self.brightness_slider.set_value(state.percentage)
            self._updating_brightness_slider = False

        self._update_brightness_icon(state.percentage)


    def _update_brightness_icon(
        self,
        percentage: int,
    ) -> None:
        if self.brightness_icon_button is None:
            return

        if percentage < 30:
            icon = "󰃞"
        elif percentage < 70:
            icon = "󰃟"
        else:
            icon = "󰃠"

        self.brightness_icon_button.set_label(icon)
        self.brightness_icon_button.set_tooltip_text(
            f"Brightness: {percentage}%"
        )


    def _on_brightness_changed(
        self,
        slider: Gtk.Scale,
    ) -> None:
        if self._updating_brightness_slider:
            return

        percentage = round(slider.get_value())

        try:
            set_brightness(percentage)
            self._update_brightness_icon(percentage)

        except Exception as error:
            print(f"Brightness change failed: {error}")
            self._refresh_brightness()

    @staticmethod
    def _build_slider_row(
        icon: str,
        label: str,
    ) -> Gtk.Box:
        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
        )
        row.add_css_class("control-slider-row")

        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("control-slider-icon")

        text_label = Gtk.Label(label=label)
        text_label.set_width_chars(10)
        text_label.set_xalign(0)
        text_label.add_css_class("control-slider-label")

        slider = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0,
            100,
            1,
        )
        slider.set_value(50)
        slider.set_draw_value(False)
        slider.set_hexpand(True)
        slider.set_sensitive(False)
        slider.add_css_class("control-slider")

        row.append(icon_label)
        row.append(text_label)
        row.append(slider)

        return row
    
    def _build_night_light_button(self) -> Gtk.MenuButton:
        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4,
        )

        icon_label = Gtk.Label(label="󰖔")
        icon_label.add_css_class("quick-toggle-icon")

        text_label = Gtk.Label(label="Night Light")
        text_label.add_css_class("quick-toggle-label")

        content.append(icon_label)
        content.append(text_label)

        button = Gtk.MenuButton()
        button.set_child(content)
        button.add_css_class("quick-toggle")
        button.set_tooltip_text("Night Light off")

        popover = Gtk.Popover()
        popover.add_css_class("night-light-popover")

        preset_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )
        preset_box.set_margin_top(8)
        preset_box.set_margin_bottom(8)
        preset_box.set_margin_start(8)
        preset_box.set_margin_end(8)

        for preset in PRESETS:
            preset_button = Gtk.Button(
                label=self._format_night_light_preset(preset)
            )
            preset_button.add_css_class("night-light-preset")
            preset_button.connect(
                "clicked",
                self._on_night_light_preset_clicked,
                preset,
                popover,
            )
            preset_box.append(preset_button)

        popover.set_child(preset_box)
        button.set_popover(popover)

        return button


    @staticmethod
    def _format_night_light_preset(
        preset: NightLightPreset,
    ) -> str:
        if preset.temperature is None:
            return preset.name

        return f"{preset.name} — {preset.temperature}K"


    def _on_night_light_preset_clicked(
        self,
        _button: Gtk.Button,
        preset: NightLightPreset,
        popover: Gtk.Popover,
    ) -> None:
        try:
            set_night_light_temperature(preset.temperature)
        except Exception as error:
            print(f"Night Light failed: {error}")

            if self.night_light_button is not None:
                self.night_light_button.set_tooltip_text(
                    "Night Light unavailable"
                )

            return

        self._night_light_temperature = preset.temperature

        if self.night_light_button is not None:
            if preset.temperature is None:
                self.night_light_button.remove_css_class("active")
                self.night_light_button.set_tooltip_text(
                    "Night Light off"
                )
            else:
                self.night_light_button.add_css_class("active")
                self.night_light_button.set_tooltip_text(
                    f"{preset.name} — {preset.temperature}K"
                )

        popover.popdown()

