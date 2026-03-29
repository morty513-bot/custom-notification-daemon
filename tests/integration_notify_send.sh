#!/usr/bin/env bash
set -euo pipefail

if ! command -v dbus-run-session >/dev/null 2>&1; then
  echo "dbus-run-session is required" >&2
  exit 1
fi

if ! command -v notify-send >/dev/null 2>&1; then
  echo "notify-send is required" >&2
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

log_file="$tmp_dir/notification.json"
pid_file="$tmp_dir/daemon.pid"

cat >"$tmp_dir/test_daemon.py" <<'PY'
#!/usr/bin/env python3
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
PY

chmod +x "$tmp_dir/test_daemon.py"

export PYTHONPATH="$repo_root${PYTHONPATH:+:$PYTHONPATH}"
export NOTIFY_LOG="$log_file"

# Start the daemon inside an isolated session bus.
dbus-run-session -- bash -lc '
  set -euo pipefail
  /usr/bin/python3 -u "$1" >"$2/daemon.log" 2>&1 &
  daemon_pid=$!
  echo "$daemon_pid" >"$3"

  for _ in $(seq 1 50); do
    if ! kill -0 "$daemon_pid" 2>/dev/null; then
      echo "daemon exited early" >&2
      cat "$2/daemon.log" >&2 || true
      exit 1
    fi
    if [ -s "$4" ]; then
      break
    fi
    sleep 0.2
  done

  notify-send "custom-notification-daemon test" "hello from notify-send"

  for _ in $(seq 1 50); do
    if [ -s "$4" ]; then
      break
    fi
    sleep 0.2
  done

  if [ ! -s "$4" ]; then
    echo "notification was not received" >&2
    cat "$2/daemon.log" >&2 || true
    exit 1
  fi

  kill "$daemon_pid" 2>/dev/null || true
  wait "$daemon_pid" 2>/dev/null || true
' bash "$tmp_dir/test_daemon.py" "$tmp_dir" "$pid_file" "$log_file"

echo "Integration test passed"
