import json
from pathlib import Path

from notifications import Notification, NotificationDaemon


class TestDaemon(NotificationDaemon):
    def __init__(self, log_file: str) -> None:
        super().__init__()
        self._log_file = Path(log_file)

    def on_notify(self, notification: Notification) -> None:
        self._log_file.write_text(
            json.dumps(
                {
                    "app_name": notification.app_name,
                    "summary": notification.summary,
                    "body": notification.body,
                    "actions": notification.actions,
                    "expire_timeout": notification.expire_timeout,
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
