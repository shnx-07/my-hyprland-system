from dataclasses import dataclass
import re
import shutil
import subprocess


@dataclass(frozen=True)
class BrightnessState:
    percentage: int
    device: str


def _run_brightnessctl(*arguments: str) -> str:
    if shutil.which("brightnessctl") is None:
        raise RuntimeError("brightnessctl is not installed")

    result = subprocess.run(
        ["brightnessctl", *arguments],
        capture_output=True,
        text=True,
        check=True,
        timeout=5,
    )

    return result.stdout.strip()


def get_brightness_state() -> BrightnessState:
    output = _run_brightnessctl(
        "--machine-readable",
        "info",
    )

    line = output.splitlines()[0] if output else ""
    fields = line.split(",")

    if len(fields) < 4:
        raise RuntimeError(
            f"Could not parse brightnessctl output: {output}"
        )

    device = fields[0].strip()
    percentage_match = re.search(r"(\d+)%", fields[3])

    if percentage_match is None:
        raise RuntimeError(
            f"Could not parse brightness percentage: {output}"
        )

    percentage = int(percentage_match.group(1))
    percentage = max(1, min(percentage, 100))

    return BrightnessState(
        percentage=percentage,
        device=device,
    )


def set_brightness(percentage: int) -> None:
    clamped_percentage = max(1, min(int(percentage), 100))

    _run_brightnessctl(
        "set",
        f"{clamped_percentage}%",
    )
