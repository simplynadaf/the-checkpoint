#!/usr/bin/env bash
# Start the FastAPI web UI, fully detached.
set -euo pipefail

VENV="$HOME/agent-experiance/.venv"
APPDIR="$HOME/checkpoint"
LOG="$APPDIR/ui-server.log"
PIDFILE="$APPDIR/ui-server.pid"
PORT="${1:-8080}"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  kill "$(cat "$PIDFILE")" 2>/dev/null || true
  sleep 1
fi
pkill -f "uvicorn ui.server" 2>/dev/null || true
sleep 1

cd "$APPDIR"
# shellcheck disable=SC1091
source "$VENV/bin/activate"

setsid nohup "$VENV/bin/uvicorn" ui.server:app --host 127.0.0.1 --port "$PORT" \
  > "$LOG" 2>&1 < /dev/null &
echo $! > "$PIDFILE"
echo "launched web ui pid $(cat "$PIDFILE") on port $PORT"
