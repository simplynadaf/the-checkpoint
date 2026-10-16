#!/usr/bin/env bash
# Play The Checkpoint in the terminal (no web UI). Needs a running decider server.
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
source "$HOME/agent-experiance/.venv/bin/activate"
python -m tests.test_scenarios
