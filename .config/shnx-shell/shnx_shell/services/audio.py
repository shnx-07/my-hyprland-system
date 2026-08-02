from dataclasses import dataclass
import re
import shutil
import subprocess


DEFAULT_SINK = "@DEFAULT_AUDIO_SINK@"


@dataclass(frozen=True)
class AudioState:
    volume: int
    muted: bool


def _run_wpctl(*arguments: str) -> str:
    if shutil.which("wpctl") is None:
        raise RuntimeError("wpctl is not installed")

    result = subprocess.run(
        ["wpctl", *arguments],
        capture_output=True,
        text=True,
        check=True,
        timeout=5,
    )

    return result.stdout.strip()


def get_audio_state() -> AudioState:
    output = _run_wpctl(
        "get-volume",
        DEFAULT_SINK,
    )

    match = re.search(
        r"Volume:\s+([0-9]*\.?[0-9]+)",
        output,
    )

    if match is None:
        raise RuntimeError(
            f"Could not parse wpctl output: {output}"
        )

    raw_volume = float(match.group(1))
    volume = round(raw_volume * 100)
    volume = max(0, min(volume, 100))

    muted = "[MUTED]" in output.upper()

    return AudioState(
        volume=volume,
        muted=muted,
    )


def set_volume(volume: int) -> None:
    clamped_volume = max(0, min(int(volume), 100))

    _run_wpctl(
        "set-volume",
        DEFAULT_SINK,
        f"{clamped_volume / 100:.2f}",
    )


def set_muted(muted: bool) -> None:
    _run_wpctl(
        "set-mute",
        DEFAULT_SINK,
        "1" if muted else "0",
    )


def toggle_mute() -> None:
    _run_wpctl(
        "set-mute",
        DEFAULT_SINK,
        "toggle",
    )
