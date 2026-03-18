"""Tool registration aggregator."""

from . import analysis, community, components, core, modification, publishing, transform, utility


def register_all_tools(mcp, models: dict, output_dir: str):
    """Register all tool modules with the MCP server."""
    for module in [core, transform, modification, analysis, utility, components, community, publishing]:
        module.register(mcp, models, output_dir)
