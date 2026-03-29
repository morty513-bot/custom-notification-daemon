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

export PYTHONPATH="$repo_root${PYTHONPATH:+:$PYTHONPATH}"
export NOTIFY_LOG="$log_file"

dbus-run-session -- bash -lc '
  set -euo pipefail
  /usr/bin/python3 -u "$1" >"$2" 2>&1 &
  daemon_pid=$!
  echo "$daemon_pid" >"$3"

  for _ in $(seq 1 50); do
    if ! kill -0 "$daemon_pid" 2>/dev/null; then
      echo "daemon exited early" >&2
      cat "$2" >&2 || true
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
    cat "$2" >&2 || true
    exit 1
  fi

  kill "$daemon_pid" 2>/dev/null || true
  wait "$daemon_pid" 2>/dev/null || true
' bash "$repo_root/tests/daemon_runner.py" "$tmp_dir/daemon.log" "$pid_file" "$log_file"

echo "Integration test passed"
