from dataclasses import dataclass
import shutil
import subprocess


@dataclass(frozen=True)
class NetworkState:
    wifi_enabled: bool
    connected: bool
    ssid: str | None


@dataclass(frozen=True)
class VpnState:
    available_profiles: tuple[str, ...]
    active_profiles: tuple[str, ...]

    @property
    def available(self) -> bool:
        return bool(self.available_profiles)

    @property
    def active(self) -> bool:
        return bool(self.active_profiles)


def _run_nmcli(*arguments: str) -> str:
    result = subprocess.run(
        ["nmcli", *arguments],
        capture_output=True,
        text=True,
        check=True,
        timeout=5,
    )

    return result.stdout.strip()


def _unescape_nmcli(value: str) -> str:
    return (
        value.replace(r"\:", ":")
        .replace(r"\\", "\\")
    )


def _parse_connection_type_line(
    line: str,
) -> tuple[str, str] | None:
    """
    Parse an nmcli NAME:TYPE line.

    rpartition() is used because a connection name may itself contain
    escaped colons, while the connection type is always the final field.
    """
    name, separator, connection_type = line.rpartition(":")

    if not separator:
        return None

    cleaned_name = _unescape_nmcli(name).strip()
    cleaned_type = connection_type.strip().lower()

    if not cleaned_name or not cleaned_type:
        return None

    return cleaned_name, cleaned_type


def _is_vpn_connection_type(connection_type: str) -> bool:
    return connection_type in {
        "vpn",
        "wireguard",
    }


def get_network_state() -> NetworkState:
    if shutil.which("nmcli") is None:
        raise RuntimeError("nmcli is not installed")

    radio_state = _run_nmcli(
        "--terse",
        "--fields",
        "WIFI",
        "radio",
    ).lower()

    wifi_enabled = radio_state == "enabled"

    if not wifi_enabled:
        return NetworkState(
            wifi_enabled=False,
            connected=False,
            ssid=None,
        )

    wifi_list = _run_nmcli(
        "--terse",
        "--fields",
        "ACTIVE,SSID",
        "device",
        "wifi",
        "list",
    )

    for line in wifi_list.splitlines():
        active, separator, ssid = line.partition(":")

        if separator and active == "yes":
            cleaned_ssid = _unescape_nmcli(ssid).strip()

            return NetworkState(
                wifi_enabled=True,
                connected=True,
                ssid=cleaned_ssid or None,
            )

    return NetworkState(
        wifi_enabled=True,
        connected=False,
        ssid=None,
    )


def get_vpn_state() -> VpnState:
    if shutil.which("nmcli") is None:
        raise RuntimeError("nmcli is not installed")

    saved_connections = _run_nmcli(
        "--terse",
        "--fields",
        "NAME,TYPE",
        "connection",
        "show",
    )

    active_connections = _run_nmcli(
        "--terse",
        "--fields",
        "NAME,TYPE",
        "connection",
        "show",
        "--active",
    )

    available_profiles: list[str] = []
    active_profiles: list[str] = []

    for line in saved_connections.splitlines():
        parsed = _parse_connection_type_line(line)

        if parsed is None:
            continue

        name, connection_type = parsed

        if _is_vpn_connection_type(connection_type):
            available_profiles.append(name)

    for line in active_connections.splitlines():
        parsed = _parse_connection_type_line(line)

        if parsed is None:
            continue

        name, connection_type = parsed

        if _is_vpn_connection_type(connection_type):
            active_profiles.append(name)

    return VpnState(
        available_profiles=tuple(available_profiles),
        active_profiles=tuple(active_profiles),
    )


def set_wifi_enabled(enabled: bool) -> None:
    if shutil.which("nmcli") is None:
        raise RuntimeError("nmcli is not installed")

    state = "on" if enabled else "off"

    _run_nmcli(
        "radio",
        "wifi",
        state,
    )
