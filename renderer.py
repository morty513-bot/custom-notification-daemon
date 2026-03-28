#!/usr/bin/env python3

import threading
from abc import ABC, abstractmethod
from typing import Any, Callable

from notifications import (
    Notification,
)


class NotificationRenderer(ABC):
    """Receives Notification objects and presents them to the user."""

    @abstractmethod
    def show(self, notification: Notification) -> None:
        """Display the given notification."""
        ...

    def close(self, notification_id: int) -> None:
        """Close a currently displayed notification by its ID."""
        pass

    def set_handlers(
        self,
        on_action: Callable[[int, str], None],
        on_closed: Callable[[int, int], None],
    ) -> None:
        """Set callbacks for user actions and close events."""
        pass


# Below was the old version but this makes a window handled by sway but I don't want this,
# I want an overlay like a banner or a toast or something
# class GtkRenderer(NotificationRenderer):
#     """Simple GTK3 popup renderer for Wayland / Sway.

#     Each notification gets its own small undecorated window. Windows
#     auto-dismiss after the requested timeout (or 5 s by default). Sway
#     will float these automatically because they carry the NOTIFICATION
#     window-type hint.
#     """

#     _DEFAULT_TIMEOUT_MS = 5000

#     def __init__(self) -> None:
#         import gi

#         gi.require_version("Gtk", "3.0")
#         from gi.repository import Gtk, Gdk, GLib

#         self._Gtk = Gtk
#         self._Gdk = Gdk
#         self._GLib = GLib

#         self._windows: dict[int, Any] = {}
#         self._lock = threading.Lock()
#         self._on_action: Callable[[int, str], None] = lambda _id, _key: None
#         self._on_closed: Callable[[int, int], None] = lambda _id, _reason: None

#         gtk_thread = threading.Thread(target=Gtk.main, daemon=True)
#         gtk_thread.start()

#     # ------------------------------------------------------------------ #
#     # Public API                                                           #
#     # ------------------------------------------------------------------ #

#     def show(self, notification: Notification) -> None:
#         self._GLib.idle_add(self._create_window, notification)

#     def close(self, notification_id: int) -> None:
#         # Programmatic close should not look like a user-dismiss close event.
#         self._GLib.idle_add(
#             self._destroy_window,
#             notification_id,
#             False,
#             CLOSE_REASON_DISMISSED,
#         )

#     def set_handlers(
#         self,
#         on_action: Callable[[int, str], None],
#         on_closed: Callable[[int, int], None],
#     ) -> None:
#         self._on_action = on_action
#         self._on_closed = on_closed

#     # ------------------------------------------------------------------ #
#     # GTK-thread helpers — must only be called via GLib.idle_add          #
#     # ------------------------------------------------------------------ #

#     def _create_window(self, notification: Notification) -> bool:
#         Gtk, Gdk, GLib = self._Gtk, self._Gdk, self._GLib

#         # Replace window if this updates an existing notification
#         if notification.replaces_id:
#             self._destroy_window(notification.replaces_id)

#         win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
#         win.set_decorated(False)
#         win.set_resizable(False)
#         win.set_keep_above(True)
#         win.set_skip_taskbar_hint(True)
#         win.set_skip_pager_hint(True)
#         win.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)
#         win.set_default_size(320, -1)

#         outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
#         outer.set_margin_top(12)
#         outer.set_margin_bottom(12)
#         outer.set_margin_start(16)
#         outer.set_margin_end(16)

#         if notification.app_name:
#             app_lbl = Gtk.Label(label=notification.app_name)
#             app_lbl.set_xalign(0.0)
#             app_lbl.get_style_context().add_class("dim-label")
#             outer.pack_start(app_lbl, False, False, 0)

#         if notification.summary:
#             summary_lbl = Gtk.Label()
#             summary_lbl.set_markup(
#                 f"<b>{GLib.markup_escape_text(notification.summary)}</b>"
#             )
#             summary_lbl.set_xalign(0.0)
#             summary_lbl.set_line_wrap(True)
#             summary_lbl.set_max_width_chars(40)
#             outer.pack_start(summary_lbl, False, False, 0)

#         if notification.body:
#             body_lbl = Gtk.Label(label=notification.body)
#             body_lbl.set_xalign(0.0)
#             body_lbl.set_line_wrap(True)
#             body_lbl.set_max_width_chars(40)
#             outer.pack_start(body_lbl, False, False, 0)

#         action_pairs = self._parse_actions(notification.actions)
#         if action_pairs:
#             action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
#             for action_key, action_label in action_pairs:
#                 btn = Gtk.Button(label=action_label)
#                 btn.connect(
#                     "clicked",
#                     self._on_action_clicked,
#                     notification.id,
#                     action_key,
#                 )
#                 action_row.pack_start(btn, False, False, 0)
#             outer.pack_start(action_row, False, False, 2)

#         win.add(outer)
#         win.show_all()

#         with self._lock:
#             self._windows[notification.id] = win

#         timeout_ms = (
#             notification.expire_timeout
#             if notification.expire_timeout > 0
#             else self._DEFAULT_TIMEOUT_MS
#         )
#         GLib.timeout_add(
#             timeout_ms,
#             self._destroy_window,
#             notification.id,
#             True,
#             CLOSE_REASON_EXPIRED,
#         )

#         return False  # don't repeat idle call

#     def _on_action_clicked(
#         self, _button: object, notification_id: int, action_key: str
#     ) -> None:
#         self._on_action(notification_id, action_key)
#         self._destroy_window(notification_id, True, CLOSE_REASON_DISMISSED)

#     def _destroy_window(
#         self,
#         notification_id: int,
#         emit_closed: bool = False,
#         close_reason: int = 0,
#     ) -> bool:
#         with self._lock:
#             win = self._windows.pop(notification_id, None)
#         if win is not None:
#             win.destroy()
#             if emit_closed:
#                 self._on_closed(notification_id, close_reason)
#         return False  # don't repeat timeout/idle call

#     @staticmethod
#     def _parse_actions(actions: list[str]) -> list[tuple[str, str]]:
#         pairs: list[tuple[str, str]] = []
#         for i in range(0, len(actions) - 1, 2):
#             action_key = actions[i]
#             action_label = actions[i + 1]
#             pairs.append((action_key, action_label))
#         return pairs


class OverlayRenderer(NotificationRenderer):
    """Renderer that renders notifications as simple overlays on top of all windows.
    
    Uses GTK with GtkLayerShell to create layer surfaces on Wayland/Sway,
    similar to how dunst works. Notifications appear as a banner at the top
    of the screen and are not managed by the window manager.
    """

    _DEFAULT_TIMEOUT_MS = 5000
    _BANNER_HEIGHT = 120

    def __init__(self) -> None:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, Gdk, GLib

        try:
            gi.require_version("GtkLayerShell", "0")
            from gi.repository import GtkLayerShell
        except ValueError:
            raise RuntimeError(
                "GtkLayerShell not found. Install it with: "
                "sudo apt install libgtk-layer-shell0 gir1.2-gtk-layer-shell-0"
            )

        self._Gtk = Gtk
        self._Gdk = Gdk
        self._GLib = GLib
        self._GtkLayerShell = GtkLayerShell

        self._windows: dict[int, Any] = {}
        self._lock = threading.Lock()
        self._on_action: Callable[[int, str], None] = lambda _id, _key: None
        self._on_closed: Callable[[int, int], None] = lambda _id, _reason: None
        self._timeout_sources: dict[int, int] = {}

        gtk_thread = threading.Thread(target=Gtk.main, daemon=True)
        gtk_thread.start()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def show(self, notification: Notification) -> None:
        self._GLib.idle_add(self._create_window, notification)

    def close(self, notification_id: int) -> None:
        """Close a notification programmatically."""
        self._GLib.idle_add(
            self._destroy_window,
            notification_id,
            True,
            2,  # CLOSE_REASON_DISMISSED
        )

    def set_handlers(
        self,
        on_action: Callable[[int, str], None],
        on_closed: Callable[[int, int], None],
    ) -> None:
        self._on_action = on_action
        self._on_closed = on_closed

    # ------------------------------------------------------------------ #
    # GTK-thread helpers — must only be called via GLib.idle_add          #
    # ------------------------------------------------------------------ #

    def _create_window(self, notification: Notification) -> bool:
        Gtk, Gdk, GLib = self._Gtk, self._Gdk, self._GLib
        GtkLayerShell = self._GtkLayerShell

        # Replace window if this updates an existing notification
        if notification.replaces_id:
            self._destroy_window(notification.replaces_id, False, 0)

        # Create window
        win = Gtk.Window(type=Gtk.WindowType.POPUP)
        win.set_decorated(False)
        win.set_resizable(False)
        win.set_keep_above(True)
        win.set_skip_taskbar_hint(True)
        win.set_skip_pager_hint(True)

        # Configure as layer shell surface
        GtkLayerShell.init_for_window(win)
        GtkLayerShell.set_layer(
            win, GtkLayerShell.Layer.TOP
        )  # Layer.TOP to appear above other windows
        GtkLayerShell.set_monitor(win, Gdk.Display.get_default().get_primary_monitor())

        # Position at top of screen
        GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.RIGHT, True)

        # Set size
        win.set_default_size(800, self._BANNER_HEIGHT)
        GtkLayerShell.set_exclusive_zone(win, self._BANNER_HEIGHT)

        # Build UI
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        outer.set_margin_top(8)
        outer.set_margin_bottom(8)
        outer.set_margin_start(16)
        outer.set_margin_end(16)

        if notification.app_name:
            app_lbl = Gtk.Label(label=notification.app_name)
            app_lbl.set_xalign(0.0)
            app_lbl.get_style_context().add_class("dim-label")
            outer.pack_start(app_lbl, False, False, 0)

        if notification.summary:
            summary_lbl = Gtk.Label()
            summary_lbl.set_markup(
                f"<b>{GLib.markup_escape_text(notification.summary)}</b>"
            )
            summary_lbl.set_xalign(0.0)
            summary_lbl.set_line_wrap(True)
            summary_lbl.set_max_width_chars(60)
            outer.pack_start(summary_lbl, False, False, 0)

        if notification.body:
            body_lbl = Gtk.Label(label=notification.body)
            body_lbl.set_xalign(0.0)
            body_lbl.set_line_wrap(True)
            body_lbl.set_max_width_chars(60)
            outer.pack_start(body_lbl, False, False, 0)

        action_pairs = self._parse_actions(notification.actions)
        if action_pairs:
            action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            for action_key, action_label in action_pairs:
                btn = Gtk.Button(label=action_label)
                btn.connect(
                    "clicked",
                    self._on_action_clicked,
                    notification.id,
                    action_key,
                )
                action_row.pack_start(btn, False, False, 0)
            outer.pack_start(action_row, False, False, 2)

        win.add(outer)
        win.show_all()

        with self._lock:
            self._windows[notification.id] = win

        # Set up auto-dismiss timeout
        timeout_ms = (
            notification.expire_timeout
            if notification.expire_timeout > 0
            else self._DEFAULT_TIMEOUT_MS
        )
        timeout_source = GLib.timeout_add(
            timeout_ms,
            self._destroy_window,
            notification.id,
            True,
            1,  # CLOSE_REASON_EXPIRED
        )
        self._timeout_sources[notification.id] = timeout_source

        return False  # don't repeat idle call

    def _on_action_clicked(
        self, _button: object, notification_id: int, action_key: str
    ) -> None:
        self._on_action(notification_id, action_key)
        self._destroy_window(notification_id, True, 2)  # CLOSE_REASON_DISMISSED

    def _destroy_window(
        self,
        notification_id: int,
        emit_closed: bool = False,
        close_reason: int = 0,
    ) -> bool:
        with self._lock:
            win = self._windows.pop(notification_id, None)
            timeout_source = self._timeout_sources.pop(notification_id, None)

        if win is not None:
            # Cancel pending timeout if window is being destroyed early
            if timeout_source is not None:
                self._GLib.source_remove(timeout_source)
            win.destroy()
            if emit_closed:
                self._on_closed(notification_id, close_reason)

        return False  # don't repeat timeout/idle call

    @staticmethod
    def _parse_actions(actions: list[str]) -> list[tuple[str, str]]:
        """Parse actions list into (key, label) tuples."""
        pairs: list[tuple[str, str]] = []
        for i in range(0, len(actions) - 1, 2):
            action_key = actions[i]
            action_label = actions[i + 1]
            pairs.append((action_key, action_label))
        return pairs
