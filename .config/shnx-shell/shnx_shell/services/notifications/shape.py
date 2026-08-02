from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class NotificationAction:
    key: str
    label: str


@dataclass
class Notification:
    notification_id: int
    app_name: str
    app_icon: str
    summary: str
    body: str
    actions: tuple[NotificationAction, ...]
    hints: dict[str, Any]
    timeout: int
    created_at: datetime = field(
        default_factory=datetime.now
    )
    read: bool = False
    suppressed: bool = False
