from dataclasses import dataclass
from pathlib import Path
import shutil


PROC_STAT_PATH = Path("/proc/stat")
PROC_MEMINFO_PATH = Path("/proc/meminfo")
ROOT_PATH = Path("/")


@dataclass(frozen=True)
class CpuTimes:
    idle: int
    total: int


@dataclass(frozen=True)
class SystemMonitorState:
    cpu_percentage: float
    ram_percentage: float
    disk_percentage: float


def _read_cpu_times() -> CpuTimes:
    first_line = PROC_STAT_PATH.read_text(
        encoding="utf-8",
    ).splitlines()[0]

    parts = first_line.split()

    if not parts or parts[0] != "cpu":
        raise RuntimeError("Unable to read CPU statistics")

    values = [int(value) for value in parts[1:]]

    if len(values) < 4:
        raise RuntimeError("Incomplete CPU statistics")

    idle = values[3]

    if len(values) > 4:
        idle += values[4]

    return CpuTimes(
        idle=idle,
        total=sum(values),
    )


def calculate_cpu_percentage(
    previous: CpuTimes,
    current: CpuTimes,
) -> float:
    total_delta = current.total - previous.total
    idle_delta = current.idle - previous.idle

    if total_delta <= 0:
        return 0.0

    usage = 100.0 * (1.0 - idle_delta / total_delta)

    return max(0.0, min(usage, 100.0))


def get_ram_percentage() -> float:
    values: dict[str, int] = {}

    for line in PROC_MEMINFO_PATH.read_text(
        encoding="utf-8",
    ).splitlines():
        key, separator, raw_value = line.partition(":")

        if not separator:
            continue

        number = raw_value.strip().split()[0]
        values[key] = int(number)

    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", 0)

    if total <= 0:
        return 0.0

    used = total - available
    usage = used / total * 100.0

    return max(0.0, min(usage, 100.0))


def get_disk_percentage() -> float:
    usage = shutil.disk_usage(ROOT_PATH)

    if usage.total <= 0:
        return 0.0

    percentage = usage.used / usage.total * 100.0

    return max(0.0, min(percentage, 100.0))


def get_cpu_times() -> CpuTimes:
    return _read_cpu_times()
