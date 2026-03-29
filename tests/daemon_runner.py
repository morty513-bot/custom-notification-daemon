#!/usr/bin/env python3
import asyncio
import os

from notifications import run_daemon
from tests.helpers import TestDaemon


async def main() -> None:
    await run_daemon(TestDaemon(os.environ["NOTIFY_LOG"]))


if __name__ == "__main__":
    asyncio.run(main())
