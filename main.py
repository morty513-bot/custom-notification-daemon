#!/usr/bin/env python3

import asyncio

from notifications import Notification, NotificationDaemon, run_daemon
from renderer import OverlayRenderer, NotificationRenderer


class RendererNotificationDaemon(NotificationDaemon):
    def __init__(self, renderer: NotificationRenderer) -> None:
        super().__init__()
        self._renderer = renderer
        self._renderer.set_handlers(self._on_action, self._on_closed)

    def get_server_information(self) -> tuple[str, str, str, str]:
        return ("notify-gtk", "local", "0.1", "1.2")

    def on_notify(self, notification: Notification) -> None:
        self._renderer.show(notification)

    def on_close_notification(self, id: int) -> None:
        self._renderer.close(id)

    def _on_action(self, notification_id: int, action_key: str) -> None:
        self.emit_action_invoked(notification_id, action_key)

    def _on_closed(self, notification_id: int, reason: int) -> None:
        self.emit_notification_closed(notification_id, reason)


if __name__ == "__main__":
    asyncio.run(run_daemon(RendererNotificationDaemon(OverlayRenderer())))
