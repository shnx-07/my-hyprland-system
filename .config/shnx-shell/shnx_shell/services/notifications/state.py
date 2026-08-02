from dataclasses import dataclass


@dataclass
class NotificationState:
    dnd_enabled: bool = False


_state = NotificationState()


def get_notification_state() -> NotificationState:
    return _state


def is_dnd_enabled() -> bool:
    return _state.dnd_enabled


def set_dnd_enabled(enabled: bool) -> None:
    _state.dnd_enabled = enabled


def toggle_dnd() -> bool:
    _state.dnd_enabled = not _state.dnd_enabled
    return _state.dnd_enabled
