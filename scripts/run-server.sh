#!/bin/bash
# Launcher for 3dp-mcp-server within the plugin environment.
# Activates the venv (created by setup-plugin.sh) and runs server.py.
set -e

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$PLUGIN_ROOT/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Running setup..." >&2
    bash "$PLUGIN_ROOT/scripts/setup-plugin.sh" >&2
fi

exec "$VENV_DIR/bin/python3" "$PLUGIN_ROOT/server.py"
