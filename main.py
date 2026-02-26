#!/usr/bin/env python3

import asyncio
from typing import TYPE_CHECKING

from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method
from dbus_next import RequestNameReply


if TYPE_CHECKING:
    import typing
    from dbus_next import Variant

    # For type checking use Python types
    t_str = str  # string
    t_uint32 = int  # uint32
    t_int32 = int  # int32
    t_str_array = list[str]  # array of strings
    t_dict_str_variant = dict[str, Variant]  # dict[string, Variant]
    t_str4 = list[str]  # struct of 4 strings (returned as list)
    t_none: typing.TypeAlias = None
else:
    # At runtime use D-Bus signature strings (required by dbus_next)
    t_str = "s"
    t_uint32 = "u"
    t_int32 = "i"
    t_str_array = "as"
    t_dict_str_variant = "a{sv}"
    t_str4 = "ssss"
    t_none = ""


DBUS_NAME = "org.freedesktop.Notifications"
DBUS_PATH = "/org/freedesktop/Notifications"


class Notifications(ServiceInterface):
    def __init__(self):
        super().__init__(DBUS_NAME)
        self._next_id = 1

    @method()
    def GetCapabilities(self) -> t_str_array:
        return ["body"]

    @method()
    def GetServerInformation(self) -> t_str4:
        # name, vendor, version, spec_version
        return ["notify-console", "local", "0.1", "1.2"]

    @method()
    def Notify(
        self,
        app_name: t_str,
        replaces_id: t_uint32,
        app_icon: t_str,
        summary: t_str,
        body: t_str,
        actions: t_str_array,
        hints: t_dict_str_variant,
        expire_timeout: t_int32,
    ) -> t_uint32:
        nid = self._next_id
        self._next_id += 1

        print("---- Notification ----")
        print(f"id: {nid} (replaces {replaces_id})")
        print(f"app: {app_name}")
        print(f"icon: {app_icon}")
        print(f"summary: {summary}")
        print(f"body: {body}")
        print(f"actions: {list(actions)}")
        print(f"hints: {hints}")
        print(f"expire_timeout(ms): {expire_timeout}")
        print("----------------------", flush=True)

        return nid

    @method()
    def CloseNotification(self, id: t_uint32) -> t_none:
        print(f"CloseNotification({id})", flush=True)


async def main() -> None:
    bus = await MessageBus().connect()

    # Own the service name
    reply = await bus.request_name(DBUS_NAME)
    if reply != RequestNameReply.PRIMARY_OWNER:
        raise SystemExit(
            f"Failed to own {DBUS_NAME}. "
            "Another notification daemon is already running."
        )

    # Export the object. Many clients expect this object path.
    iface = Notifications()
    bus.export(DBUS_PATH, iface)

    print(f"notify-console is running and owns {DBUS_NAME}", flush=True)
    await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
