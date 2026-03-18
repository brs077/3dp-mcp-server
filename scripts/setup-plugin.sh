#!/bin/bash
# Setup script for the 3dp-mcp-server plugin.
# Uses uv to install dependencies.
set -e

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== 3DP MCP Server Plugin Setup ===" >&2

# Check for uv
if ! command -v uv &>/dev/null; then
    echo "[ERROR] uv is required but not found." >&2
    echo "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi

echo "Installing dependencies with uv..." >&2
cd "$PLUGIN_ROOT"
uv sync

echo "[OK] 3DP MCP Server plugin ready" >&2
