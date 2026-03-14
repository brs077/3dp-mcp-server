# 3DP MCP Server

MCP server that gives Claude the ability to create 3D-printable CAD models using build123d. Outputs STL/STEP files ready for slicing in Bambu Studio.

## Quick Setup (macOS)

```bash
git clone https://github.com/yourusername/3dp-mcp-server.git
cd 3dp-mcp-server
bash setup.sh
```

That's it. Start a new Claude Code session and ask it to create a model.

## Tools

| Tool | Description |
|------|-------------|
| `create_model` | Execute build123d code, auto-exports STL + STEP |
| `export_model` | Export to STL, STEP, or 3MF |
| `measure_model` | Bounding box, volume, face/edge counts |
| `analyze_printability` | Watertight check, thin wall detection, build volume fit |
| `list_models` | List all models in current session |
| `get_model_code` | Retrieve the code used to create a model |

## Requirements

- Python 3.11+
- macOS (tested on Apple Silicon)
- Claude Code CLI

## Uninstall

```bash
claude mcp remove 3dp-mcp-server -s user
rm -rf 3dp-mcp-server
```
