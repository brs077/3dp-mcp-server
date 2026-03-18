# 3DP MCP Server

MCP server that gives Claude the ability to create 3D-printable CAD models using build123d. Outputs STL/STEP files ready for slicing in Bambu Studio.

Also available as a **Claude Code plugin** — install it and all 33 tools are automatically available.

## Install as Plugin (Recommended)

Add the marketplace and install the plugin from within Claude Code:

```
/plugin marketplace add brs077/3dp-mcp-server
/plugin install 3dp-mcp-server@3dp-tools
```

The plugin will automatically set up a Python virtual environment and install dependencies on first use. Requires Python 3.11+.

### Plugin Skills

Once installed, Claude gains six agent skills:

- **design-model** — Design 3D-printable CAD models with build123d
- **modify-model** — Shell, split, add text, combine, transform, and generate 2D drawings
- **parametric-components** — Create enclosures, gears, snap-fits, hinges, dovetails, and labels
- **mechanical-parts** — Create threads, fasteners, bearings, sprockets, flanges, pipes, OpenBuilds parts
- **print-prep** — Analyze printability, suggest orientation, estimate filament/cost, pack build plates
- **publish-model** — Publish to GitHub Releases, Thingiverse, MyMiniFactory, Cults3D, or search for models

## Manual Setup (Alternative)

```bash
git clone https://github.com/randypitcherii/3dp-mcp-server.git
cd 3dp-mcp-server
make install
```

### As a Claude Code Plugin

```bash
claude plugin add /path/to/3dp-mcp-server
```

The plugin auto-registers the MCP server via `.mcp.json`.

### Manual MCP Registration

```bash
claude mcp add 3dp-mcp-server -- uv run --directory /path/to/3dp-mcp-server threedp-mcp
```

## Tools (40)

### Core
| Tool | Description |
|------|-------------|
| `create_model` | Execute build123d code, auto-exports STL + STEP |
| `export_model` | Export to STL, STEP, or 3MF |
| `measure_model` | Bounding box, volume, face/edge counts |
| `analyze_printability` | Watertight check, thin wall detection, build volume fit |
| `list_models` | List all models in current session |
| `get_model_code` | Retrieve the code used to create a model |

### Transform & Combine
| Tool | Description |
|------|-------------|
| `transform_model` | Scale, rotate, mirror, or translate a model |
| `combine_models` | Boolean union, subtract, or intersect two models |
| `import_model` | Import STL or STEP file from disk |

### Modification
| Tool | Description |
|------|-------------|
| `shell_model` | Hollow out a model with optional open faces |
| `split_model` | Split a model along a plane |
| `add_text` | Emboss or deboss text onto a model face |
| `create_threaded_hole` | Add threaded or heat-set insert holes (M2-M10) |

### Analysis & Export
| Tool | Description |
|------|-------------|
| `estimate_print` | Estimate filament usage, weight, and cost |
| `analyze_overhangs` | Find overhang faces needing support material |
| `suggest_orientation` | Suggest optimal print orientation |
| `section_view` | Generate 2D cross-section as SVG |
| `export_drawing` | Multi-view 2D technical drawing as SVG |
| `split_model_by_color` | Split into separate STLs for multi-color printing |

### Utility
| Tool | Description |
|------|-------------|
| `shrinkage_compensation` | Scale model to compensate for material shrinkage |
| `pack_models` | Arrange models on build plate for batch printing |
| `convert_format` | Convert between STL, STEP, 3MF, BREP |

### Parametric Components
| Tool | Description |
|------|-------------|
| `create_enclosure` | Electronics enclosure with snap/screw lid and features |
| `create_gear` | Involute spur gear (via bd_warehouse) |
| `create_snap_fit` | Cantilever snap-fit joints |
| `create_hinge` | Two-part pin hinge assembly |
| `create_dovetail` | Male or female dovetail joints |
| `generate_label` | 3D-printable label with text and optional QR code |

### Mechanical Parts (bd_warehouse)
| Tool | Description |
|------|-------------|
| `create_thread` | ISO metric, ACME, metric trapezoidal, or plastic bottle threads |
| `create_fastener` | Screws, nuts, washers, heat-set inserts (14 types) |
| `create_bearing` | Ball bearings, roller bearings (5 types) |
| `create_sprocket` | Chain sprockets for ANSI chains |
| `create_flange` | ASME B16.5 pipe flanges (5 types) |
| `create_pipe` | Pipe/tube sections |
| `create_openbuilds_part` | V-Slot rails, C-Beam rails, lead screws |

### Community
| Tool | Description |
|------|-------------|
| `search_models` | Search Thingiverse for 3D models |

### Publishing
| Tool | Description |
|------|-------------|
| `publish_github_release` | Upload STL/STEP to GitHub Releases (via `gh` CLI or API) |
| `publish_thingiverse` | Create a Thing and upload STL to Thingiverse |
| `publish_myminifactory` | Create object and upload STL to MyMiniFactory |
| `publish_cults3d` | Create listing on Cults3D via GraphQL API |

## Development

```bash
make install          # Install dependencies
make test             # Run unit tests
make test-integration # Run all tests (requires build123d)
make lint             # Check code style
make format           # Auto-format code
make verify           # Lint + test
make run              # Start the MCP server
make clean            # Remove build artifacts
```

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- macOS (tested on Apple Silicon) or Windows 11
- Claude Code CLI

## Project Structure

```
src/threedp_mcp/
├── server.py       # Thin entrypoint — FastMCP init + tool registration
├── constants.py    # Material properties, ISO thread table
├── helpers.py      # Shared utilities (shape conversion, code execution, etc.)
└── tools/
    ├── core.py         # create, export, measure, analyze, list, get_code
    ├── transform.py    # transform, combine, import
    ├── modification.py # shell, split, add_text, threaded_hole
    ├── analysis.py     # estimate, overhangs, orientation, section, drawing, color_split
    ├── utility.py      # shrinkage, pack, convert
    ├── components.py   # enclosure, gear, snap_fit, hinge, dovetail, label
    ├── mechanical.py   # threads, fasteners, bearings, sprockets, flanges, pipes, openbuilds
    ├── community.py    # search_models
    └── publishing.py   # github, thingiverse, myminifactory, cults3d
```

## Uninstall

### Plugin

```
/plugin uninstall 3dp-mcp-server@3dp-tools
```

### Manual Install

macOS:
```bash
claude mcp remove 3dp-mcp-server -s user
rm -rf 3dp-mcp-server
```

Windows:
```powershell
claude mcp remove 3dp-mcp-server -s user
Remove-Item -Recurse -Force 3dp-mcp-server
```

## License

This project is licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/). You can use it personally and share it with attribution, but commercial use and redistribution of modified versions are not permitted.

Interested in collaborating or commercial licensing? [Open an issue](https://github.com/brs077/3dp-mcp-server/issues) to get in touch.
