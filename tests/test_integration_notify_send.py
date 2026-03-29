import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest


@pytest.mark.integration
def test_notify_send_delivers_notification() -> None:
    if shutil.which("dbus-run-session") is None:
        pytest.skip("dbus-run-session is required")
    if shutil.which("notify-send") is None:
        pytest.skip("notify-send is required")

    repo_root = Path(__file__).resolve().parents[1]

    test_daemon_source = textwrap.dedent(
        """
        import asyncio
        import json
        import os
        from pathlib import Path

        from notifications import Notification, NotificationDaemon, run_daemon


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


        async def main() -> None:
            await run_daemon(TestDaemon(os.environ["NOTIFY_LOG"]))


        if __name__ == "__main__":
            asyncio.run(main())
        """
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        daemon_script = tmp / "test_daemon.py"
        daemon_script.write_text(test_daemon_source, encoding="utf-8")
        log_file = tmp / "notification.json"
        daemon_log = tmp / "daemon.log"

        env = os.environ.copy()
        env["PYTHONPATH"] = f"{repo_root}{os.pathsep}{env['PYTHONPATH']}" if env.get("PYTHONPATH") else str(repo_root)
        env["NOTIFY_LOG"] = str(log_file)

        session_script = textwrap.dedent(
            """
            set -euo pipefail
            /usr/bin/python3 -u "$1" >"$2" 2>&1 &
            daemon_pid=$!

            for _ in $(seq 1 50); do
              if ! kill -0 "$daemon_pid" 2>/dev/null; then
                echo "daemon exited early" >&2
                cat "$2" >&2 || true
                exit 1
              fi
              if [ -s "$3" ]; then
                break
              fi
              sleep 0.2
            done

            notify-send "custom-notification-daemon test" "hello from notify-send"

            for _ in $(seq 1 50); do
              if [ -s "$3" ]; then
                break
              fi
              sleep 0.2
            done

            if [ ! -s "$3" ]; then
              echo "notification was not received" >&2
              cat "$2" >&2 || true
              exit 1
            fi

            kill "$daemon_pid" 2>/dev/null || true
            wait "$daemon_pid" 2>/dev/null || true
            """
        )

        subprocess.run(
            [
                "dbus-run-session",
                "--",
                "bash",
                "-lc",
                session_script,
                "bash",
                str(daemon_script),
                str(daemon_log),
                str(log_file),
            ],
            check=True,
            env=env,
            cwd=repo_root,
        )

        payload = json.loads(log_file.read_text(encoding="utf-8"))
        assert payload["summary"] == "custom-notification-daemon test"
        assert payload["body"] == "hello from notify-send"
        assert payload["actions"] == []
        assert payload["expire_timeout"] == -1
