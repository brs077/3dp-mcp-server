# 3DP MCP Server

MCP server that gives Claude the ability to create 3D-printable CAD models using build123d. Outputs STL/STEP files ready for slicing in Bambu Studio.

## Quick Setup

### macOS

```bash
git clone https://github.com/yourusername/3dp-mcp-server.git
cd 3dp-mcp-server
bash setup.sh
```

### Windows 11

**Option A** — Double-click `setup.bat` in File Explorer.

**Option B** — Run from PowerShell:

```powershell
git clone https://github.com/yourusername/3dp-mcp-server.git
cd 3dp-mcp-server
powershell -ExecutionPolicy Bypass -File setup.ps1
```

That's it. Start a new Claude Code session and ask it to create a model.

## Tools (33)

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
| `create_threaded_hole` | Add threaded or heat-set insert holes (M2–M10) |

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

## Requirements

- Python 3.11+
- macOS (tested on Apple Silicon) or Windows 11
- Claude Code CLI

## Uninstall

### macOS

```bash
claude mcp remove 3dp-mcp-server -s user
rm -rf 3dp-mcp-server
```

### Windows

```powershell
claude mcp remove 3dp-mcp-server -s user
Remove-Item -Recurse -Force 3dp-mcp-server
```
