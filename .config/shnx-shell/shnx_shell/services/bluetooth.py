from dataclasses import dataclass
import shutil
import subprocess


@dataclass(frozen=True)
class BluetoothState:
    available: bool
    powered: bool
    connected_devices: tuple[str, ...]


def _run_bluetoothctl(*arguments: str) -> str:
    result = subprocess.run(
        ["bluetoothctl", *arguments],
        capture_output=True,
        text=True,
        check=True,
        timeout=5,
    )

    return result.stdout.strip()


def _get_powered_state() -> bool:
    output = _run_bluetoothctl("show")

    for line in output.splitlines():
        stripped = line.strip()

        if stripped.startswith("Powered:"):
            value = stripped.partition(":")[2].strip().lower()
            return value == "yes"

    return False


def _get_connected_devices() -> tuple[str, ...]:
    output = _run_bluetoothctl("devices", "Connected")
    devices: list[str] = []

    for line in output.splitlines():
        stripped = line.strip()

        if not stripped.startswith("Device "):
            continue

        parts = stripped.split(maxsplit=2)

        if len(parts) == 3:
            devices.append(parts[2])

    return tuple(devices)


def get_bluetooth_state() -> BluetoothState:
    if shutil.which("bluetoothctl") is None:
        return BluetoothState(
            available=False,
            powered=False,
            connected_devices=(),
        )

    try:
        powered = _get_powered_state()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return BluetoothState(
            available=False,
            powered=False,
            connected_devices=(),
        )

    if not powered:
        return BluetoothState(
            available=True,
            powered=False,
            connected_devices=(),
        )

    try:
        connected_devices = _get_connected_devices()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        connected_devices = ()

    return BluetoothState(
        available=True,
        powered=True,
        connected_devices=connected_devices,
    )

def set_bluetooth_powered(powered: bool) -> None:
    if shutil.which("bluetoothctl") is None:
        raise RuntimeError("bluetoothctl is not installed")

    state = "on" if powered else "off"

    _run_bluetoothctl(
        "power",
        state,
    )
