from dataclasses import dataclass
from pathlib import Path


POWER_SUPPLY_PATH = Path("/sys/class/power_supply")


@dataclass(frozen=True)
class BatteryState:
    percentage: int
    status: str
    is_charging: bool


def _find_battery_path() -> Path | None:
    if not POWER_SUPPLY_PATH.exists():
        return None

    for device in POWER_SUPPLY_PATH.iterdir():
        device_type = device / "type"

        try:
            if device_type.read_text(encoding="utf-8").strip() == "Battery":
                return device
        except OSError:
            continue

    return None


def get_battery_state() -> BatteryState | None:
    battery_path = _find_battery_path()

    if battery_path is None:
        return None

    capacity_path = battery_path / "capacity"
    status_path = battery_path / "status"

    try:
        percentage = int(capacity_path.read_text(encoding="utf-8").strip())
        status = status_path.read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return None

    percentage = max(0, min(percentage, 100))

    return BatteryState(
        percentage=percentage,
        status=status,
        is_charging=status.lower() in {"charging", "full"},
    )
