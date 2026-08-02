from dataclasses import dataclass
import shutil
import subprocess


@dataclass(frozen=True)
class NightLightPreset:
    name: str
    temperature: int | None


PRESETS: tuple[NightLightPreset, ...] = (
    NightLightPreset("Off", None),
    NightLightPreset("Warm", 3000),
    NightLightPreset("Comfortable", 4000),
    NightLightPreset("Mild", 5000),
)


def _run_hyprctl(*arguments: str) -> None:
    if shutil.which("hyprctl") is None:
        raise RuntimeError("hyprctl is not installed")

    subprocess.run(
        ["hyprctl", "hyprsunset", *arguments],
        capture_output=True,
        text=True,
        check=True,
        timeout=5,
    )


def set_night_light_temperature(
    temperature: int | None,
) -> None:
    if temperature is None:
        _run_hyprctl("identity")
        return

    if temperature not in {3000, 4000, 5000}:
        raise ValueError(
            f"Unsupported Night Light temperature: {temperature}"
        )

    _run_hyprctl(
        "temperature",
        str(temperature),
    )
