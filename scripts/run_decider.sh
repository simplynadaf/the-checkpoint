#!/usr/bin/env bash
# Start the Strands Decider server, fully detached, surviving the parent shell.
set -euo pipefail

VENV="$HOME/agent-experiance/.venv"
MODEL="StrandsAgents/strands-decider-2B-qwen3.5-v1-2610"
LOG="$HOME/agent-experiance/decider-server.log"
PIDFILE="$HOME/agent-experiance/decider-server.pid"
PORT="${1:-8000}"

# Stop any existing instance
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "stopping existing server (pid $(cat "$PIDFILE"))"
  kill "$(cat "$PIDFILE")" 2>/dev/null || true
  sleep 2
fi
pkill -f "strands-decider serve" 2>/dev/null || true
sleep 1

# shellcheck disable=SC1091
source "$VENV/bin/activate"
export MALLOC_ARENA_MAX=2
export OMP_NUM_THREADS=2

# nohup + setsid, stdin from /dev/null, write our own pidfile
setsid nohup strands-decider serve "$MODEL" \
  --host 127.0.0.1 --port "$PORT" --device cpu \
  > "$LOG" 2>&1 < /dev/null &

echo $! > "$PIDFILE"
echo "launched decider server pid $(cat "$PIDFILE") on port $PORT (log: $LOG)"
