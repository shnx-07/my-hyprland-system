from configparser import ConfigParser
from pathlib import Path


DESKTOP_DIRS = (
    Path.home() / ".local/share/applications",
    Path("/usr/local/share/applications"),
    Path("/usr/share/applications"),
)


def find_app_icon(app_class: str) -> str:
    normalized_class = app_class.strip().lower()

    for directory in DESKTOP_DIRS:
        if not directory.exists():
            continue

        for desktop_file in directory.glob("*.desktop"):
            parser = ConfigParser(interpolation=None)
            parser.optionxform = str

            try:
                parser.read(desktop_file, encoding="utf-8")
            except (OSError, UnicodeError):
                continue

            if not parser.has_section("Desktop Entry"):
                continue

            entry = parser["Desktop Entry"]

            candidates = {
                desktop_file.stem.lower(),
                entry.get("Name", "").lower(),
                entry.get("StartupWMClass", "").lower(),
            }

            if normalized_class not in candidates:
                continue

            icon = entry.get("Icon", "").strip()

            if icon:
                return icon

    return "application-x-executable-symbolic"
