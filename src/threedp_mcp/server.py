"""3DP MCP Server — thin entrypoint."""

import os

from mcp.server.fastmcp import FastMCP

from threedp_mcp.tools import register_all_tools

mcp = FastMCP("3dp-mcp-server")
_models: dict[str, dict] = {}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Register all tools at import time
register_all_tools(mcp, _models, OUTPUT_DIR)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
