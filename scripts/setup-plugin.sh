#!/bin/bash
# Setup script for the 3dp-mcp-server plugin.
# Creates a Python virtual environment and installs dependencies.
set -e

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$PLUGIN_ROOT/.venv"

echo "=== 3DP MCP Server Plugin Setup ===" >&2

# Find Python 3.11+
PYTHON=""
for cmd in python3.12 python3.11 python3; do
    if command -v "$cmd" &>/dev/null; then
        major=$("$cmd" -c "import sys; print(sys.version_info.major)")
        minor=$("$cmd" -c "import sys; print(sys.version_info.minor)")
        if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
            PYTHON="$cmd"
            echo "[OK] Found $cmd ($major.$minor)" >&2
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "[ERROR] Python 3.11+ is required but not found." >&2
    echo "Install with: brew install python@3.12" >&2
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..." >&2
    "$PYTHON" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Installing dependencies..." >&2
pip install --upgrade pip -q
pip install -r "$PLUGIN_ROOT/requirements.txt" -q

echo "[OK] 3DP MCP Server plugin ready" >&2
