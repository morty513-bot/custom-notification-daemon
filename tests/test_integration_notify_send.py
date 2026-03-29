import asyncio
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_notify_send_delivers_notification() -> None:
    if shutil.which("notify-send") is None:
        pytest.skip("notify-send is required")

    repo_root = Path(__file__).resolve().parents[1]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        log_file = tmp / "notification.json"
        daemon_log = tmp / "daemon.log"

        env = os.environ.copy()
        env["PYTHONPATH"] = f"{repo_root}{os.pathsep}{env['PYTHONPATH']}" if env.get("PYTHONPATH") else str(repo_root)
        env["NOTIFY_LOG"] = str(log_file)

        daemon = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "tests.daemon_runner",
            stdout=daemon_log.open("wb"),
            stderr=asyncio.subprocess.STDOUT,
            env=env,
            cwd=repo_root,
        )

        try:
            for _ in range(50):
                if not log_file.exists() and daemon.returncode is not None:
                    raise AssertionError(
                        f"daemon exited early; log:\n{daemon_log.read_text(encoding='utf-8', errors='replace')}"
                    )
                if not log_file.exists():
                    await asyncio.sleep(0.2)
                    continue
                break

            await asyncio.create_subprocess_exec(
                "notify-send",
                "custom-notification-daemon test",
                "hello from notify-send",
                env=env,
                cwd=repo_root,
            )

            for _ in range(50):
                if log_file.exists():
                    break
                await asyncio.sleep(0.2)

            assert log_file.exists(), (
                "notification was not received; daemon log:\n"
                f"{daemon_log.read_text(encoding='utf-8', errors='replace')}"
            )

            payload = json.loads(log_file.read_text(encoding="utf-8"))
            assert payload["summary"] == "custom-notification-daemon test"
            assert payload["body"] == "hello from notify-send"
            assert payload["actions"] == []
            assert payload["expire_timeout"] == -1
        finally:
            daemon.terminate()
            try:
                await asyncio.wait_for(daemon.wait(), timeout=5)
            except asyncio.TimeoutError:
                daemon.kill()
                await daemon.wait()
