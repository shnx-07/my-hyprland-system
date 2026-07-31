import json
import subprocess


def get_open_workspaces() -> list[int]:
    result = subprocess.run(
        ["hyprctl", "-j", "workspaces"],
        capture_output=True,
        text=True,
        check=True,
    )

    workspaces = json.loads(result.stdout)

    return sorted(
        workspace["id"]
        for workspace in workspaces
        if workspace["id"] > 0
    )


def get_active_workspace() -> int:
    result = subprocess.run(
        ["hyprctl", "-j", "activeworkspace"],
        capture_output=True,
        text=True,
        check=True,
    )

    workspace = json.loads(result.stdout)

    return workspace["id"]

def switch_workspace(workspace_id: int) -> None:
    command = f'hl.dsp.focus({{ workspace = "{workspace_id}" }})'

    subprocess.run(
        ["hyprctl", "dispatch", command],
        check=True,
    )

def get_active_window_class() -> str:
    result = subprocess.run(
        ["hyprctl", "-j", "activewindow"],
        capture_output=True,
        text=True,
        check=True,
    )

    window = json.loads(result.stdout)

    return window.get("class") or window.get("initialClass") or "unknown"
