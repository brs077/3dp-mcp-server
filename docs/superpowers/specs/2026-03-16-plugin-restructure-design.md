# 3dp-mcp Plugin Restructure Design

## Goal

Convert the monolithic 3dp-mcp-server into a proper Claude Code plugin with uv-managed Python package, Makefile-based workflow, modular tool organization, and comprehensive tests.

## Repository Context

- **Current state**: 2,253-line monolithic `server.py`, 33 MCP tools, 5 helper functions, pip + requirements.txt, no tests, no Makefile
- **Remote setup**: `origin` = fork at `randypitcherii/3dp-mcp-server`, `upstream` = `brs077/3dp-mcp-server`
- **License**: CC BY-NC-ND 4.0

## Naming

- **Plugin name**: `3dp-mcp`
- **PyPI/project name**: `threedp-mcp` (used in pyproject.toml `[project].name`)
- **Python import name**: `threedp_mcp` (the actual package under `src/`)
- **MCP server name**: `3dp-mcp-server` (backward compatible)
- **CLI entrypoint**: `threedp-mcp`

## Repository Structure

```
3dp-mcp-server/
├── plugin.json                  # Claude Code plugin manifest
├── .mcp.json                    # MCP server auto-registration
├── pyproject.toml               # uv/PEP 621 project config
├── Makefile                     # install, test, test-integration, lint, verify
├── src/
│   └── threedp_mcp/
│       ├── __init__.py          # version, package metadata
│       ├── server.py            # FastMCP init + tool registration (thin entrypoint)
│       ├── constants.py         # _MATERIAL_PROPERTIES, _ISO_THREAD_TABLE
│       ├── helpers.py           # _shape_to_model_entry, _run_build123d_code, _select_face, _compute_overhangs, _ensure_exported
│       └── tools/
│           ├── __init__.py      # register_all_tools(mcp, models) aggregator
│           ├── core.py          # create_model, export_model, measure_model, list_models, get_model_code, analyze_printability
│           ├── transform.py     # transform_model, combine_models, import_model
│           ├── modification.py  # shell_model, split_model, add_text, create_threaded_hole
│           ├── analysis.py      # estimate_print, analyze_overhangs, suggest_orientation, section_view, export_drawing, split_model_by_color
│           ├── utility.py       # shrinkage_compensation, pack_models, convert_format
│           ├── components.py    # create_enclosure, create_gear, create_snap_fit, create_hinge, create_dovetail, generate_label
│           ├── community.py     # search_models
│           └── publishing.py    # publish_github_release, publish_thingiverse, publish_myminifactory, publish_cults3d
├── tests/
│   ├── conftest.py              # shared fixtures, mock helpers
│   ├── test_constants.py
│   ├── test_helpers.py
│   ├── test_core.py
│   ├── test_transform.py
│   ├── test_modification.py
│   ├── test_analysis.py
│   ├── test_utility.py
│   ├── test_components.py
│   ├── test_community.py
│   ├── test_publishing.py
│   └── integration/
│       ├── conftest.py          # @pytest.mark.integration auto-mark
│       └── test_full_pipeline.py
├── docs/
│   ├── README.md
│   └── tools/                   # existing per-tool docs (unchanged)
├── scripts/                     # legacy build scripts moved here
│   ├── analyze_all.py
│   ├── build_all_tracks.py
│   ├── build_pit_lane.py
│   ├── build_startfinish.py
│   └── inspect_stls.py
├── .env.example                 # documents optional env vars
├── README.md                    # updated for uv/plugin install
├── CLAUDE.md                    # updated for new structure
├── LICENSE
└── .gitignore                   # updated with .env, uv.lock, etc.
```

## Module Decomposition Pattern

Each tool module exports a `register(mcp, models)` function:

```python
# src/threedp_mcp/tools/core.py
from threedp_mcp.helpers import _shape_to_model_entry, _run_build123d_code

def register(mcp, models: dict):
    @mcp.tool()
    async def create_model(name: str, code: str) -> str:
        # uses `models` dict via closure
        ...
```

**server.py** is thin — tool registration happens at module scope so tools are available whether `main()` is called or the module is imported directly (e.g., in tests):

```python
import os
from mcp.server.fastmcp import FastMCP
from threedp_mcp.tools import register_all_tools

mcp = FastMCP("3dp-mcp-server")
_models: dict[str, dict] = {}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Register all tools at import time
register_all_tools(mcp, _models)

def main():
    mcp.run()
```

Note: `outputs/` directory is created lazily at server startup via `os.makedirs(..., exist_ok=True)`. `make clean` removes it; it's recreated on next server start.

**tools/__init__.py** aggregates all modules:

```python
from . import core, transform, modification, analysis, utility, components, community, publishing

def register_all_tools(mcp, models):
    for module in [core, transform, modification, analysis, utility, components, community, publishing]:
        module.register(mcp, models)
```

Session state (`_models` dict) is passed by reference — no globals leaking across modules.

## Plugin Configuration

### plugin.json

```json
{
  "name": "3dp-mcp",
  "description": "3D-printable CAD modeling with build123d for FDM printing",
  "version": "1.0.0"
}
```

### .mcp.json

```json
{
  "mcpServers": {
    "3dp-mcp-server": {
      "command": "uv",
      "args": ["run", "--directory", "${CLAUDE_PLUGIN_ROOT}", "threedp-mcp"]
    }
  }
}
```

### pyproject.toml

- `[project]`: name=`threedp-mcp`, requires-python=`>=3.11`
- Dependencies: `build123d>=0.7`, `mcp[cli]>=1.0`, `bd_warehouse>=0.1`, `qrcode>=7.0`
- Dev deps group: `pytest`, `pytest-asyncio`, `ruff`
- `[project.scripts]`: `threedp-mcp = "threedp_mcp.server:main"`
- `[tool.pytest.ini_options]`: markers for `integration`
- `[tool.ruff]`: line-length=120, target Python 3.11

### Makefile

| Target | Command |
|--------|---------|
| `install` | `uv sync` |
| `test` | `uv run pytest -m "not integration"` |
| `test-integration` | `uv run pytest` (runs all tests including integration) |
| `lint` | `uv run ruff check src/ tests/` |
| `format` | `uv run ruff format src/ tests/` |
| `verify` | lint + test |
| `run` | `uv run threedp-mcp` |
| `clean` | remove `.venv`, `outputs/`, build artifacts |

## Test Strategy

### Unit Tests (mocked)

- Mock `build123d` imports using lightweight fake shapes
- Each tool module gets a corresponding test file
- Test argument validation, error paths, return format
- Test helpers with mock shape objects (bbox, volume, faces)
- Publishing tools mock HTTP/subprocess, verify request construction
- Constants validated for structure (required keys, valid values)

### Integration Tests

- Marked `@pytest.mark.integration`
- Create real shapes via build123d
- Test create → measure → analyze → export pipeline
- Test transform/combine produce valid geometry
- Verify STL/STEP files are written correctly

### Fixtures (conftest.py)

- `mock_shape` — fake shape with bbox, volume, faces attributes
- `mock_models` — pre-populated `_models` dict
- `tmp_output_dir` — temp directory for file I/O tests
- `mock_env` — context manager for env var manipulation (all env var reads in the codebase are deferred to call-time via `os.environ.get()`, so patching works correctly)

## Environment Variables

Documented in `.env.example`:

```
# Optional — only needed for community/publishing tools
THINGIVERSE_API_KEY=    # search_models (read-only API key for searching)
THINGIVERSE_TOKEN=      # publish_thingiverse (OAuth token with write access, separate from API key)
MYMINIFACTORY_TOKEN=    # publish_myminifactory
CULTS3D_API_KEY=        # publish_cults3d
GITHUB_TOKEN=           # publish_github_release (alternative to gh CLI)
```

## Migration Notes

- Legacy scripts (`analyze_all.py`, `build_*.py`, `inspect_stls.py`) move to `scripts/`
- `setup.bat`, `setup.ps1` removed (replaced by `make install` / `uv sync`)
- Old `.venv/` directory removed from repo
- `requirements.txt` removed (replaced by `pyproject.toml`)
- All 33 tools maintain identical signatures and behavior
- MCP server name stays `3dp-mcp-server` for backward compatibility

## Non-Goals

- No skills or agents in initial version (MCP server is the value)
- No CI/CD setup (can add later)
- No changes to tool behavior or signatures
- No new tools
