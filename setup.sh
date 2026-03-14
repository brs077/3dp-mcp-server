#!/bin/bash
set -e

# 3DP MCP Server — Setup Script for macOS
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "=== 3DP MCP Server Setup ==="
echo ""

PYTHON=""
for cmd in python3.12 python3.11 python3; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        major=$("$cmd" -c "import sys; print(sys.version_info.major)")
        minor=$("$cmd" -c "import sys; print(sys.version_info.minor)")
        if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
            PYTHON="$cmd"
            echo "[OK] Found $cmd ($version)"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "[ERROR] Python 3.11+ is required but not found."
    echo "Install with: brew install python@3.12"
    exit 1
fi

echo ""
echo "Creating virtual environment..."
"$PYTHON" -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "Installing dependencies (this may take a few minutes for build123d)..."
pip install --upgrade pip -q
pip install "build123d>=0.7" "mcp[cli]>=1.0" -q

echo ""
echo "[OK] Dependencies installed"

echo "Verifying build123d..."
python3 -c "from build123d import Box; b = Box(10,10,10); print(f'[OK] build123d works — test cube volume: {b.volume:.1f} mm³')"

echo "Verifying MCP..."
python3 -c "from mcp.server.fastmcp import FastMCP; print('[OK] MCP server framework works')"

mkdir -p "$SCRIPT_DIR/outputs"

echo ""
echo "Registering MCP server with Claude Code..."
if command -v claude &>/dev/null; then
    claude mcp add 3dp-mcp-server \
        "$VENV_DIR/bin/python3" "$SCRIPT_DIR/server.py" \
        -s user
    echo "[OK] MCP server registered with Claude Code"
else
    echo "[SKIP] 'claude' CLI not found in PATH."
    echo "  Run this manually after installing Claude Code:"
    echo ""
    echo "  claude mcp add 3dp-mcp-server $VENV_DIR/bin/python3 $SCRIPT_DIR/server.py -s user"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To verify, start Claude Code and ask:"
echo '  "What MCP servers are available?"'
echo ""
echo "Then try:"
echo '  "Create a 50x40x10mm box with 2mm fillets on all edges"'
echo ""
echo "STL files will be saved to: $SCRIPT_DIR/outputs/"
