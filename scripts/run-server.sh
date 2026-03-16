#!/bin/bash
# Launcher for 3dp-mcp-server within the plugin environment.
# Uses uv to run the server entrypoint.
set -e

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

exec uv run --directory "$PLUGIN_ROOT" threedp-mcp
