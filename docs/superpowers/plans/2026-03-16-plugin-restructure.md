# 3dp-mcp Plugin Restructure Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert monolithic 2,253-line `server.py` into a Claude Code plugin with uv package management, modular tool organization, and comprehensive tests.

**Architecture:** Decompose into `src/threedp_mcp/` package with 8 tool modules, shared helpers/constants, thin server entrypoint. Plugin config (`plugin.json`, `.mcp.json`) auto-registers MCP server. Tests use mocked build123d for unit tests, real build123d for integration.

**Tech Stack:** Python 3.11+, uv, build123d, FastMCP, pytest, ruff

**Spec:** `docs/superpowers/specs/2026-03-16-plugin-restructure-design.md`

**Deviations from spec:**
- All `register()` functions take `output_dir` as a third parameter (spec shows only `mcp, models`). This improves testability — tests can pass a `tmp_path` instead of relying on a global.
- `uv.lock` is committed (not gitignored) to ensure reproducible installs for plugin consumers.

---

## Chunk 1: Project Scaffolding and Package Foundation

### Task 1: Create pyproject.toml, Makefile, and plugin configs

**Files:**
- Create: `pyproject.toml`
- Create: `Makefile`
- Create: `plugin.json`
- Create: `.mcp.json`
- Create: `.env.example`
- Modify: `.gitignore`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "threedp-mcp"
version = "1.0.0"
description = "MCP server for 3D-printable CAD modeling with build123d"
readme = "README.md"
license = {text = "CC-BY-NC-ND-4.0"}
requires-python = ">=3.11"
dependencies = [
    "build123d>=0.7",
    "mcp[cli]>=1.0",
    "bd_warehouse>=0.1",
    "qrcode>=7.0",
]

[project.scripts]
threedp-mcp = "threedp_mcp.server:main"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "ruff>=0.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/threedp_mcp"]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "integration: tests requiring build123d and OCP installed",
]
asyncio_mode = "auto"

[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "W"]
```

- [ ] **Step 2: Create `Makefile`**

```makefile
.PHONY: install test test-integration lint format verify run clean list

install:
	uv sync

test:
	uv run pytest -m "not integration" -v

test-integration:
	uv run pytest -v

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

verify: lint test

run:
	uv run threedp-mcp

clean:
	rm -rf .venv outputs/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

list:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sed 's/:.*//' | sort
```

- [ ] **Step 3: Create `plugin.json`**

```json
{
  "name": "3dp-mcp",
  "description": "3D-printable CAD modeling with build123d for FDM printing",
  "version": "1.0.0"
}
```

- [ ] **Step 4: Create `.mcp.json`**

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

- [ ] **Step 5: Create `.env.example`**

```
# Optional — only needed for community/publishing tools
THINGIVERSE_API_KEY=    # search_models (read-only API key for searching)
THINGIVERSE_TOKEN=      # publish_thingiverse (OAuth token with write access, separate from API key)
MYMINIFACTORY_TOKEN=    # publish_myminifactory
CULTS3D_API_KEY=        # publish_cults3d
GITHUB_TOKEN=           # publish_github_release (alternative to gh CLI)
```

- [ ] **Step 6: Update `.gitignore`**

Add these entries to the existing `.gitignore`:

```
# Environment
.env

# uv — uv.lock is committed for reproducibility

# Build artifacts
dist/
*.egg-info
```

- [ ] **Step 7: Run `make install` to verify uv sync works**

Run: `make install`
Expected: uv creates `.venv/` and installs dependencies successfully.

- [ ] **Step 8: Commit**

Stage: `pyproject.toml Makefile plugin.json .mcp.json .env.example .gitignore`
Message: "Add uv project config, Makefile, and plugin manifest"

---

### Task 2: Create package skeleton with constants and helpers

**Files:**
- Create: `src/threedp_mcp/__init__.py`
- Create: `src/threedp_mcp/constants.py`
- Create: `src/threedp_mcp/helpers.py`
- Create: `src/threedp_mcp/tools/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_constants.py`
- Create: `tests/test_helpers.py`

- [ ] **Step 1: Create directory structure**

Create directories: `src/threedp_mcp/tools`, `tests/integration`

- [ ] **Step 2: Create `src/threedp_mcp/__init__.py`**

```python
"""3DP MCP Server — 3D printing CAD modeling with build123d."""

__version__ = "1.0.0"
```

- [ ] **Step 3: Create `src/threedp_mcp/constants.py`**

Extract from `server.py` lines 19-37:

```python
"""Shared constants for 3DP MCP Server."""

MATERIAL_PROPERTIES = {
    "PLA":   {"density": 1.24, "shrinkage": 0.003},
    "PETG":  {"density": 1.27, "shrinkage": 0.004},
    "ABS":   {"density": 1.04, "shrinkage": 0.007},
    "ASA":   {"density": 1.07, "shrinkage": 0.005},
    "TPU":   {"density": 1.21, "shrinkage": 0.005},
    "Nylon": {"density": 1.14, "shrinkage": 0.015},
}

ISO_THREAD_TABLE = {
    "M2":   {"tap_drill": 1.6,  "insert_drill": 3.2,  "clearance_drill": 2.4},
    "M2.5": {"tap_drill": 2.05, "insert_drill": 3.5,  "clearance_drill": 2.9},
    "M3":   {"tap_drill": 2.5,  "insert_drill": 4.0,  "clearance_drill": 3.4},
    "M4":   {"tap_drill": 3.3,  "insert_drill": 5.0,  "clearance_drill": 4.5},
    "M5":   {"tap_drill": 4.2,  "insert_drill": 6.0,  "clearance_drill": 5.5},
    "M6":   {"tap_drill": 5.0,  "insert_drill": 7.0,  "clearance_drill": 6.6},
    "M8":   {"tap_drill": 6.8,  "insert_drill": 9.5,  "clearance_drill": 8.4},
    "M10":  {"tap_drill": 8.5,  "insert_drill": 12.0, "clearance_drill": 10.5},
}
```

Note: Dropped the leading underscore — these are module-level public constants now, accessed via `from threedp_mcp.constants import MATERIAL_PROPERTIES`.

- [ ] **Step 4: Create `src/threedp_mcp/helpers.py`**

Extract from `server.py` lines 41-118 and 1751-1765. Key change: `ensure_exported` now takes `models` and `output_dir` as parameters instead of using globals.

```python
"""Shared helper functions for 3DP MCP Server."""

import math
import os


def shape_to_model_entry(shape, code: str = "") -> dict:
    """Convert a build123d shape into a model entry dict with bbox and volume."""
    bb = shape.bounding_box()
    bbox = {
        "min": [round(bb.min.X, 3), round(bb.min.Y, 3), round(bb.min.Z, 3)],
        "max": [round(bb.max.X, 3), round(bb.max.Y, 3), round(bb.max.Z, 3)],
        "size": [
            round(bb.max.X - bb.min.X, 3),
            round(bb.max.Y - bb.min.Y, 3),
            round(bb.max.Z - bb.min.Z, 3),
        ],
    }
    try:
        volume = round(shape.volume, 3)
    except Exception:
        volume = None
    return {"shape": shape, "code": code, "bbox": bbox, "volume": volume}


def run_build123d_code(code: str) -> dict:
    """Execute build123d code and return a model entry dict.

    The code must assign the final shape to a variable called `result`.
    """
    local_ns: dict = {}
    exec_globals = {"__builtins__": __builtins__}
    exec(code, exec_globals, local_ns)

    if "result" not in local_ns:
        raise ValueError("Code must assign the final shape to a variable called `result`")

    return shape_to_model_entry(local_ns["result"], code)


def select_face(shape, direction: str):
    """Select a face by direction name (top/bottom/front/back/left/right)."""
    all_faces = shape.faces()
    selectors = {
        "top":    lambda f: f.center().Z,
        "bottom": lambda f: -f.center().Z,
        "front":  lambda f: f.center().Y,
        "back":   lambda f: -f.center().Y,
        "right":  lambda f: f.center().X,
        "left":   lambda f: -f.center().X,
    }
    key_fn = selectors.get(direction.lower())
    if key_fn is None:
        raise ValueError(f"Unknown face direction: {direction}. Use: {list(selectors.keys())}")
    return max(all_faces, key=key_fn)


def compute_overhangs(shape, max_angle_deg: float = 45.0) -> dict:
    """Compute overhang statistics for a shape.

    Returns dict with face count, areas, angles, and overhang percentage.
    """
    threshold_rad = math.radians(max_angle_deg)
    all_faces = shape.faces()
    total_area = 0.0
    overhang_faces = []
    overhang_area = 0.0

    for i, face in enumerate(all_faces):
        area = face.area
        total_area += area
        try:
            normal = face.normal_at()
        except Exception:
            continue
        if normal.Z < 0:
            cos_val = min(abs(normal.Z), 1.0)
            angle_from_vertical = math.acos(cos_val)
            if angle_from_vertical > threshold_rad:
                angle_deg = math.degrees(angle_from_vertical)
                overhang_faces.append({"index": i, "area": round(area, 2), "angle_deg": round(angle_deg, 1)})
                overhang_area += area

    return {
        "total_faces": len(all_faces),
        "total_area": round(total_area, 2),
        "overhang_faces": overhang_faces,
        "overhang_face_count": len(overhang_faces),
        "overhang_area": round(overhang_area, 2),
        "overhang_pct": round(overhang_area / total_area * 100, 1) if total_area > 0 else 0,
    }


def ensure_exported(name: str, models: dict, output_dir: str, fmt: str = "stl") -> str:
    """Ensure a model is exported and return the file path.

    Args:
        name: Model name in the models dict.
        models: The session models dictionary.
        output_dir: Directory to write exported files.
        fmt: Export format — "stl" or "step".
    """
    if name not in models:
        raise ValueError(f"Model '{name}' not found. Use list_models() to see available models.")
    path = os.path.join(output_dir, f"{name}.{fmt}")
    if not os.path.exists(path):
        from build123d import export_stl, export_step

        shape = models[name]["shape"]
        if fmt == "stl":
            export_stl(shape, path)
        elif fmt == "step":
            export_step(shape, path)
        else:
            raise ValueError(f"Unsupported format for publishing: {fmt}")
    return path
```

- [ ] **Step 5: Create `src/threedp_mcp/tools/__init__.py`**

```python
"""Tool registration aggregator."""

from . import analysis, community, components, core, modification, publishing, transform, utility


def register_all_tools(mcp, models: dict, output_dir: str):
    """Register all tool modules with the MCP server."""
    for module in [core, transform, modification, analysis, utility, components, community, publishing]:
        module.register(mcp, models, output_dir)
```

Note: `output_dir` is passed through registration so tool modules don't need to compute paths.

- [ ] **Step 6: Create `tests/conftest.py`**

```python
"""Shared test fixtures."""

import os
from unittest.mock import MagicMock

import pytest


class FakeVector:
    """Minimal vector for bounding box corners."""

    def __init__(self, x, y, z):
        self.X = x
        self.Y = y
        self.Z = z


class FakeBoundingBox:
    """Minimal bounding box for mock shapes."""

    def __init__(self, min_v=(0, 0, 0), max_v=(10, 20, 30)):
        self.min = FakeVector(*min_v)
        self.max = FakeVector(*max_v)


class FakeFace:
    """Minimal face for mock shapes."""

    def __init__(self, area=1.0, normal_z=1.0, center=(0, 0, 0)):
        self.area = area
        self._normal_z = normal_z
        self._center = center

    def normal_at(self):
        return FakeVector(0, 0, self._normal_z)

    def center(self):
        return FakeVector(*self._center)


class FakeShape:
    """Mock build123d shape with configurable properties."""

    def __init__(self, bbox_min=(0, 0, 0), bbox_max=(10, 20, 30), volume=6000.0, faces=None):
        self._bbox = FakeBoundingBox(bbox_min, bbox_max)
        self.volume = volume
        self._faces = faces or [FakeFace()]

    def bounding_box(self):
        return self._bbox

    def faces(self):
        return self._faces

    def edges(self):
        return []


@pytest.fixture
def mock_shape():
    """A default fake shape: 10x20x30mm box."""
    return FakeShape()


@pytest.fixture
def mock_models(mock_shape):
    """Pre-populated models dict with one test model."""
    return {
        "test_box": {
            "shape": mock_shape,
            "code": 'result = Box(10, 20, 30)',
            "bbox": {
                "min": [0, 0, 0],
                "max": [10, 20, 30],
                "size": [10, 20, 30],
            },
            "volume": 6000.0,
        }
    }


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Temporary output directory for file I/O tests."""
    output = tmp_path / "outputs"
    output.mkdir()
    return str(output)


@pytest.fixture
def mock_env(monkeypatch):
    """Factory fixture to set/clear env vars for testing."""

    def _set(**kwargs):
        for key, value in kwargs.items():
            if value is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, value)

    return _set
```

- [ ] **Step 7: Write `tests/test_constants.py`**

```python
"""Tests for threedp_mcp.constants."""

from threedp_mcp.constants import ISO_THREAD_TABLE, MATERIAL_PROPERTIES


class TestMaterialProperties:
    def test_all_materials_have_required_keys(self):
        for name, props in MATERIAL_PROPERTIES.items():
            assert "density" in props, f"{name} missing density"
            assert "shrinkage" in props, f"{name} missing shrinkage"

    def test_density_values_are_positive(self):
        for name, props in MATERIAL_PROPERTIES.items():
            assert props["density"] > 0, f"{name} has non-positive density"

    def test_shrinkage_values_are_positive(self):
        for name, props in MATERIAL_PROPERTIES.items():
            assert props["shrinkage"] > 0, f"{name} has non-positive shrinkage"

    def test_pla_is_present(self):
        assert "PLA" in MATERIAL_PROPERTIES


class TestIsoThreadTable:
    def test_all_threads_have_required_keys(self):
        for size, dims in ISO_THREAD_TABLE.items():
            assert "tap_drill" in dims, f"{size} missing tap_drill"
            assert "insert_drill" in dims, f"{size} missing insert_drill"
            assert "clearance_drill" in dims, f"{size} missing clearance_drill"

    def test_clearance_larger_than_tap(self):
        for size, dims in ISO_THREAD_TABLE.items():
            assert dims["clearance_drill"] > dims["tap_drill"], (
                f"{size}: clearance_drill should be larger than tap_drill"
            )

    def test_insert_larger_than_tap(self):
        for size, dims in ISO_THREAD_TABLE.items():
            assert dims["insert_drill"] > dims["tap_drill"], (
                f"{size}: insert_drill should be larger than tap_drill"
            )

    def test_m3_is_present(self):
        assert "M3" in ISO_THREAD_TABLE
```

- [ ] **Step 8: Write `tests/test_helpers.py`**

```python
"""Tests for threedp_mcp.helpers."""

import os
from unittest.mock import MagicMock, patch

import pytest

from threedp_mcp.helpers import (
    compute_overhangs,
    ensure_exported,
    run_build123d_code,
    select_face,
    shape_to_model_entry,
)


class TestShapeToModelEntry:
    def test_returns_bbox_and_volume(self, mock_shape):
        entry = shape_to_model_entry(mock_shape)
        assert entry["bbox"]["size"] == [10.0, 20.0, 30.0]
        assert entry["volume"] == 6000.0
        assert entry["shape"] is mock_shape

    def test_stores_code(self, mock_shape):
        entry = shape_to_model_entry(mock_shape, code="result = Box(10, 20, 30)")
        assert entry["code"] == "result = Box(10, 20, 30)"

    def test_volume_exception_returns_none(self):
        shape = MagicMock()
        shape.bounding_box.return_value = MagicMock(
            min=MagicMock(X=0, Y=0, Z=0),
            max=MagicMock(X=10, Y=10, Z=10),
        )
        type(shape).volume = property(lambda self: (_ for _ in ()).throw(Exception("no volume")))
        entry = shape_to_model_entry(shape)
        assert entry["volume"] is None


class TestRunBuild123dCode:
    def test_raises_without_result(self):
        with pytest.raises(ValueError, match="must assign the final shape"):
            run_build123d_code("x = 1")

    @patch("threedp_mcp.helpers.shape_to_model_entry")
    def test_returns_model_entry(self, mock_entry):
        mock_entry.return_value = {"shape": "fake", "code": "", "bbox": {}, "volume": 0}
        code = "from unittest.mock import MagicMock; result = MagicMock()"
        entry = run_build123d_code(code)
        assert mock_entry.called


class TestSelectFace:
    def test_selects_top_face(self, mock_shape):
        from tests.conftest import FakeFace

        faces = [
            FakeFace(center=(0, 0, 0)),
            FakeFace(center=(0, 0, 10)),
            FakeFace(center=(0, 0, -10)),
        ]
        shape = MagicMock()
        shape.faces.return_value = faces
        result = select_face(shape, "top")
        assert result.center().Z == 10

    def test_invalid_direction_raises(self, mock_shape):
        with pytest.raises(ValueError, match="Unknown face direction"):
            select_face(mock_shape, "diagonal")


class TestComputeOverhangs:
    def test_no_overhangs_on_flat_faces(self):
        from tests.conftest import FakeFace

        shape = MagicMock()
        shape.faces.return_value = [FakeFace(area=100.0, normal_z=1.0)]
        result = compute_overhangs(shape)
        assert result["overhang_face_count"] == 0

    def test_detects_downward_overhang(self):
        from tests.conftest import FakeFace

        shape = MagicMock()
        shape.faces.return_value = [FakeFace(area=50.0, normal_z=-0.1)]
        result = compute_overhangs(shape, max_angle_deg=45.0)
        assert result["overhang_face_count"] == 1


class TestEnsureExported:
    def test_model_not_found_raises(self, tmp_output_dir):
        with pytest.raises(ValueError, match="not found"):
            ensure_exported("nonexistent", {}, tmp_output_dir)

    def test_unsupported_format_raises(self, mock_models, tmp_output_dir):
        with pytest.raises(ValueError, match="Unsupported format"):
            ensure_exported("test_box", mock_models, tmp_output_dir, fmt="obj")

    def test_returns_existing_file(self, mock_models, tmp_output_dir):
        path = os.path.join(tmp_output_dir, "test_box.stl")
        with open(path, "w") as f:
            f.write("fake stl")
        result = ensure_exported("test_box", mock_models, tmp_output_dir, fmt="stl")
        assert result == path
```

- [ ] **Step 9: Run tests to verify foundation**

Run: `make test`
Expected: All tests in `test_constants.py` and `test_helpers.py` pass.

- [ ] **Step 10: Commit**

Stage: `src/ tests/conftest.py tests/test_constants.py tests/test_helpers.py`
Message: "Add package skeleton with constants, helpers, and tests"

---

## Chunk 2: Tool Module Extraction

### Task 3: Extract core tools

**Files:**
- Create: `src/threedp_mcp/tools/core.py`
- Create: `tests/test_core.py`

**Source:** `server.py` lines 121-332 (create_model, export_model, measure_model, analyze_printability, list_models, get_model_code)

- [ ] **Step 1: Write `tests/test_core.py`**

Test the tool registration and key behaviors. Since tools are registered as MCP handlers, test the inner logic by calling the registered functions directly.

```python
"""Tests for threedp_mcp.tools.core."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from threedp_mcp.tools.core import register


@pytest.fixture
def core_tools(tmp_output_dir):
    """Register core tools and return the mcp mock with captured tools."""
    mcp = MagicMock()
    models = {}
    registered = {}

    def capture_tool():
        def decorator(fn):
            registered[fn.__name__] = fn
            return fn
        return decorator

    mcp.tool = capture_tool
    register(mcp, models, tmp_output_dir)
    return registered, models, tmp_output_dir


class TestListModels:
    def test_empty_models(self, core_tools):
        tools, models, _ = core_tools
        result = tools["list_models"]()
        parsed = json.loads(result)
        assert parsed["count"] == 0

    def test_with_models(self, core_tools, mock_shape):
        tools, models, _ = core_tools
        from threedp_mcp.helpers import shape_to_model_entry
        models["box1"] = shape_to_model_entry(mock_shape, "result = Box(10,20,30)")
        result = tools["list_models"]()
        parsed = json.loads(result)
        assert parsed["count"] == 1


class TestGetModelCode:
    def test_returns_code(self, core_tools, mock_shape):
        tools, models, _ = core_tools
        from threedp_mcp.helpers import shape_to_model_entry
        models["box1"] = shape_to_model_entry(mock_shape, "result = Box(10,20,30)")
        result = tools["get_model_code"](name="box1")
        parsed = json.loads(result)
        assert parsed["code"] == "result = Box(10,20,30)"

    def test_model_not_found(self, core_tools):
        tools, _, _ = core_tools
        result = tools["get_model_code"](name="nonexistent")
        assert "not found" in result.lower() or "error" in result.lower()


class TestCreateModel:
    @patch("threedp_mcp.helpers.run_build123d_code")
    def test_stores_model(self, mock_run, core_tools, mock_shape):
        tools, models, _ = core_tools
        from threedp_mcp.helpers import shape_to_model_entry
        mock_run.return_value = shape_to_model_entry(mock_shape, "result = Box(10,20,30)")
        result = tools["create_model"](name="mybox", code="result = Box(10,20,30)")
        assert "mybox" in models

    @patch("threedp_mcp.helpers.run_build123d_code")
    def test_error_returns_message(self, mock_run, core_tools):
        tools, models, _ = core_tools
        mock_run.side_effect = Exception("build123d not available")
        result = tools["create_model"](name="fail", code="bad code")
        assert "error" in result.lower()
```

- [ ] **Step 2: Create `src/threedp_mcp/tools/core.py`**

Extract from `server.py` lines 121-332. Adapt to use helpers module and closure-based registration.

Read lines 121-332 of `server.py` and refactor each tool function into the `register()` pattern:
- Replace `_models` global with `models` parameter
- Replace `OUTPUT_DIR` global with `output_dir` parameter
- Replace `_run_build123d_code` with `from threedp_mcp.helpers import run_build123d_code`
- Replace `_shape_to_model_entry` with `from threedp_mcp.helpers import shape_to_model_entry`
- Keep `from build123d import ...` as lazy imports inside function bodies (they're already lazy in the original)

- [ ] **Step 3: Run tests**

Run: `make test`
Expected: `test_core.py` passes.

- [ ] **Step 4: Commit**

Stage: `src/threedp_mcp/tools/core.py tests/test_core.py`
Message: "Extract core tools module with tests"

---

### Task 4: Extract transform tools

**Files:**
- Create: `src/threedp_mcp/tools/transform.py`
- Create: `tests/test_transform.py`

**Source:** `server.py` lines 333-424 (transform_model, import_model) and 495-539 (combine_models)

- [ ] **Step 1: Write `tests/test_transform.py`**

```python
"""Tests for threedp_mcp.tools.transform."""

import json
from unittest.mock import MagicMock, patch

import pytest

from threedp_mcp.tools.transform import register


@pytest.fixture
def transform_tools(tmp_output_dir, mock_models):
    """Register transform tools and return captured tools."""
    mcp = MagicMock()
    registered = {}

    def capture_tool():
        def decorator(fn):
            registered[fn.__name__] = fn
            return fn
        return decorator

    mcp.tool = capture_tool
    register(mcp, mock_models, tmp_output_dir)
    return registered, mock_models


class TestTransformModel:
    def test_source_not_found(self, transform_tools):
        tools, models = transform_tools
        result = tools["transform_model"](
            name="moved", source_name="nonexistent", operations='[{"type": "translate", "x": 10}]'
        )
        assert "not found" in result.lower() or "error" in result.lower()

    @patch("threedp_mcp.tools.transform.Pos")
    @patch("threedp_mcp.tools.transform.shape_to_model_entry")
    def test_translate_creates_new_model(self, mock_entry, mock_pos, transform_tools, mock_shape):
        tools, models = transform_tools
        mock_pos.return_value.__mul__ = MagicMock(return_value=mock_shape)
        mock_entry.return_value = {"shape": mock_shape, "code": "", "bbox": {}, "volume": 0}
        result = tools["transform_model"](
            name="moved", source_name="test_box", operations='[{"type": "translate", "x": 10}]'
        )
        assert "moved" in models


class TestCombineModels:
    def test_model_a_not_found(self, transform_tools):
        tools, models = transform_tools
        result = tools["combine_models"](
            name="combined", model_a="nonexistent", model_b="test_box", operation="union"
        )
        assert "not found" in result.lower() or "error" in result.lower()

    def test_invalid_operation(self, transform_tools):
        tools, models = transform_tools
        models["box2"] = models["test_box"].copy()
        result = tools["combine_models"](
            name="combined", model_a="test_box", model_b="box2", operation="xor"
        )
        assert "error" in result.lower() or "invalid" in result.lower()


class TestImportModel:
    def test_file_not_found(self, transform_tools):
        tools, _ = transform_tools
        result = tools["import_model"](name="imported", file_path="/nonexistent/model.stl")
        assert "error" in result.lower()
```

- [ ] **Step 2: Create `src/threedp_mcp/tools/transform.py`**

Extract from `server.py` lines 333-424, 495-539. Use the same register pattern as core.py. Import `shape_to_model_entry` from helpers. Lazy-import build123d types (Pos, Rot, Scale, Mirror, Plane, import_stl, import_step) inside function bodies.

- [ ] **Step 3: Run tests, commit**

Run: `make test`
Stage: `src/threedp_mcp/tools/transform.py tests/test_transform.py`
Message: "Extract transform tools module with tests"

---

### Task 5: Extract modification tools

**Files:**
- Create: `src/threedp_mcp/tools/modification.py`
- Create: `tests/test_modification.py`

**Source:** `server.py` lines 540-652 (shell_model, split_model), 1023-1137 (add_text, create_threaded_hole)

- [ ] **Step 1: Write `tests/test_modification.py`**

```python
"""Tests for threedp_mcp.tools.modification."""

import json
from unittest.mock import MagicMock

import pytest

from threedp_mcp.tools.modification import register


@pytest.fixture
def mod_tools(tmp_output_dir, mock_models):
    mcp = MagicMock()
    registered = {}

    def capture_tool():
        def decorator(fn):
            registered[fn.__name__] = fn
            return fn
        return decorator

    mcp.tool = capture_tool
    register(mcp, mock_models, tmp_output_dir)
    return registered, mock_models


class TestShellModel:
    def test_source_not_found(self, mod_tools):
        tools, _ = mod_tools
        result = tools["shell_model"](name="hollow", source_name="nonexistent", thickness=2.0)
        assert "not found" in result.lower() or "error" in result.lower()


class TestSplitModel:
    def test_source_not_found(self, mod_tools):
        tools, _ = mod_tools
        result = tools["split_model"](name="half", source_name="nonexistent")
        assert "not found" in result.lower() or "error" in result.lower()

    def test_invalid_plane(self, mod_tools):
        tools, _ = mod_tools
        result = tools["split_model"](name="half", source_name="test_box", plane="DIAGONAL")
        assert "error" in result.lower()


class TestCreateThreadedHole:
    def test_source_not_found(self, mod_tools):
        tools, _ = mod_tools
        result = tools["create_threaded_hole"](
            name="threaded", source_name="nonexistent",
            position='[0, 0, 0]', thread_spec="M3", depth=10.0
        )
        assert "not found" in result.lower() or "error" in result.lower()

    def test_invalid_thread_spec(self, mod_tools):
        tools, _ = mod_tools
        result = tools["create_threaded_hole"](
            name="threaded", source_name="test_box",
            position='[0, 0, 0]', thread_spec="M99", depth=10.0
        )
        assert "error" in result.lower()
```

- [ ] **Step 2: Create `src/threedp_mcp/tools/modification.py`**

Extract from `server.py`. Import `select_face`, `shape_to_model_entry` from helpers and `ISO_THREAD_TABLE` from constants.

- [ ] **Step 3: Run tests, commit**

Run: `make test`
Stage: `src/threedp_mcp/tools/modification.py tests/test_modification.py`
Message: "Extract modification tools module with tests"

---

### Task 6: Extract analysis tools

**Files:**
- Create: `src/threedp_mcp/tools/analysis.py`
- Create: `tests/test_analysis.py`

**Source:** `server.py` lines 425-494 (estimate_print), 653-802 (section_view, export_drawing, analyze_overhangs), 803-877 (suggest_orientation), 1247-1328 (split_model_by_color)

- [ ] **Step 1: Write `tests/test_analysis.py`**

```python
"""Tests for threedp_mcp.tools.analysis."""

import json
from unittest.mock import MagicMock

import pytest

from threedp_mcp.tools.analysis import register


@pytest.fixture
def analysis_tools(tmp_output_dir, mock_models):
    mcp = MagicMock()
    registered = {}

    def capture_tool():
        def decorator(fn):
            registered[fn.__name__] = fn
            return fn
        return decorator

    mcp.tool = capture_tool
    register(mcp, mock_models, tmp_output_dir)
    return registered, mock_models


class TestEstimatePrint:
    def test_model_not_found(self, analysis_tools):
        tools, _ = analysis_tools
        result = tools["estimate_print"](name="nonexistent")
        assert "not found" in result.lower() or "error" in result.lower()

    def test_valid_estimate(self, analysis_tools):
        tools, _ = analysis_tools
        result = tools["estimate_print"](name="test_box")
        parsed = json.loads(result)
        assert "volume_cm3" in parsed or "filament" in parsed or "estimate" in result.lower()

    def test_invalid_material(self, analysis_tools):
        tools, _ = analysis_tools
        result = tools["estimate_print"](name="test_box", material="Unobtanium")
        assert "error" in result.lower() or "unknown" in result.lower()


class TestAnalyzeOverhangs:
    def test_model_not_found(self, analysis_tools):
        tools, _ = analysis_tools
        result = tools["analyze_overhangs"](name="nonexistent")
        assert "not found" in result.lower() or "error" in result.lower()


class TestSuggestOrientation:
    def test_model_not_found(self, analysis_tools):
        tools, _ = analysis_tools
        result = tools["suggest_orientation"](name="nonexistent")
        assert "not found" in result.lower() or "error" in result.lower()


class TestSplitModelByColor:
    def test_model_not_found(self, analysis_tools):
        tools, _ = analysis_tools
        result = tools["split_model_by_color"](
            name="colored", source_name="nonexistent", assignments='[]'
        )
        assert "not found" in result.lower() or "error" in result.lower()
```

- [ ] **Step 2: Create `src/threedp_mcp/tools/analysis.py`**

Extract from `server.py`. Import `compute_overhangs`, `shape_to_model_entry` from helpers and `MATERIAL_PROPERTIES` from constants.

- [ ] **Step 3: Run tests, commit**

Run: `make test`
Stage: `src/threedp_mcp/tools/analysis.py tests/test_analysis.py`
Message: "Extract analysis tools module with tests"

---

### Task 7: Extract utility tools

**Files:**
- Create: `src/threedp_mcp/tools/utility.py`
- Create: `tests/test_utility.py`

**Source:** `server.py` lines 878-1022 (shrinkage_compensation, pack_models, convert_format)

- [ ] **Step 1: Write `tests/test_utility.py`**

```python
"""Tests for threedp_mcp.tools.utility."""

import json
from unittest.mock import MagicMock

import pytest

from threedp_mcp.tools.utility import register


@pytest.fixture
def utility_tools(tmp_output_dir, mock_models):
    mcp = MagicMock()
    registered = {}

    def capture_tool():
        def decorator(fn):
            registered[fn.__name__] = fn
            return fn
        return decorator

    mcp.tool = capture_tool
    register(mcp, mock_models, tmp_output_dir)
    return registered, mock_models


class TestShrinkageCompensation:
    def test_model_not_found(self, utility_tools):
        tools, _ = utility_tools
        result = tools["shrinkage_compensation"](name="comp", source_name="nonexistent")
        assert "not found" in result.lower() or "error" in result.lower()

    def test_invalid_material(self, utility_tools):
        tools, _ = utility_tools
        result = tools["shrinkage_compensation"](
            name="comp", source_name="test_box", material="Unobtanium"
        )
        assert "error" in result.lower() or "unknown" in result.lower()


class TestPackModels:
    def test_empty_list(self, utility_tools):
        tools, _ = utility_tools
        result = tools["pack_models"](name="packed", model_names='[]')
        assert "error" in result.lower() or "empty" in result.lower() or "no models" in result.lower()


class TestConvertFormat:
    def test_input_not_found(self, utility_tools):
        tools, _ = utility_tools
        result = tools["convert_format"](
            input_path="/nonexistent/model.stl", output_path="/tmp/out.step"
        )
        assert "error" in result.lower()
```

- [ ] **Step 2: Create `src/threedp_mcp/tools/utility.py`**

Extract from `server.py`. Import `shape_to_model_entry` from helpers and `MATERIAL_PROPERTIES` from constants.

- [ ] **Step 3: Run tests, commit**

Run: `make test`
Stage: `src/threedp_mcp/tools/utility.py tests/test_utility.py`
Message: "Extract utility tools module with tests"

---

### Task 8: Extract components tools

**Files:**
- Create: `src/threedp_mcp/tools/components.py`
- Create: `tests/test_components.py`

**Source:** `server.py` lines 1138-1690 (create_enclosure, create_gear, create_snap_fit, create_hinge, create_dovetail, generate_label)

- [ ] **Step 1: Write `tests/test_components.py`**

```python
"""Tests for threedp_mcp.tools.components."""

import json
from unittest.mock import MagicMock

import pytest

from threedp_mcp.tools.components import register


@pytest.fixture
def comp_tools(tmp_output_dir, mock_models):
    mcp = MagicMock()
    registered = {}

    def capture_tool():
        def decorator(fn):
            registered[fn.__name__] = fn
            return fn
        return decorator

    mcp.tool = capture_tool
    register(mcp, mock_models, tmp_output_dir)
    return registered, mock_models


class TestCreateEnclosure:
    def test_negative_dimensions_error(self, comp_tools):
        tools, _ = comp_tools
        result = tools["create_enclosure"](
            name="enc", inner_width=-10, inner_depth=30, inner_height=20
        )
        assert "error" in result.lower()


class TestCreateSnapFit:
    def test_invalid_type(self, comp_tools):
        tools, _ = comp_tools
        result = tools["create_snap_fit"](
            name="snap", snap_type="invalid", params='{}'
        )
        assert "error" in result.lower()


class TestCreateGear:
    def test_zero_teeth_error(self, comp_tools):
        tools, _ = comp_tools
        result = tools["create_gear"](name="gear", module=1.0, teeth=0)
        assert "error" in result.lower()


class TestGenerateLabel:
    def test_empty_text(self, comp_tools):
        tools, _ = comp_tools
        result = tools["generate_label"](name="label", text="")
        assert isinstance(result, str)
```

- [ ] **Step 2: Create `src/threedp_mcp/tools/components.py`**

Extract from `server.py`. Import `shape_to_model_entry` from helpers. This is the largest module (552 lines source). Lazy-import all build123d types inside function bodies.

- [ ] **Step 3: Run tests, commit**

Run: `make test`
Stage: `src/threedp_mcp/tools/components.py tests/test_components.py`
Message: "Extract components tools module with tests"

---

### Task 9: Extract community and publishing tools

**Files:**
- Create: `src/threedp_mcp/tools/community.py`
- Create: `src/threedp_mcp/tools/publishing.py`
- Create: `tests/test_community.py`
- Create: `tests/test_publishing.py`

**Source:** `server.py` lines 1691-1765 (search_models), 1768-2254 (publishing tools)

- [ ] **Step 1: Write `tests/test_community.py`**

```python
"""Tests for threedp_mcp.tools.community."""

import json
from unittest.mock import MagicMock, patch

import pytest

from threedp_mcp.tools.community import register


@pytest.fixture
def community_tools(tmp_output_dir):
    mcp = MagicMock()
    models = {}
    registered = {}

    def capture_tool():
        def decorator(fn):
            registered[fn.__name__] = fn
            return fn
        return decorator

    mcp.tool = capture_tool
    register(mcp, models, tmp_output_dir)
    return registered, models


class TestSearchModels:
    def test_no_api_key(self, community_tools, mock_env):
        tools, _ = community_tools
        mock_env(THINGIVERSE_API_KEY=None)
        result = tools["search_models"](query="phone stand")
        assert "api key" in result.lower() or "error" in result.lower() or "thingiverse" in result.lower()

    @patch("threedp_mcp.tools.community.urllib.request.urlopen")
    def test_successful_search(self, mock_urlopen, community_tools, mock_env):
        mock_env(THINGIVERSE_API_KEY="test-key")
        tools, _ = community_tools
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([
            {"id": 123, "name": "Phone Stand", "url": "https://thingiverse.com/thing:123"}
        ]).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response
        result = tools["search_models"](query="phone stand")
        assert "phone" in result.lower() or "123" in result
```

- [ ] **Step 2: Write `tests/test_publishing.py`**

```python
"""Tests for threedp_mcp.tools.publishing."""

import json
from unittest.mock import MagicMock, patch

import pytest

from threedp_mcp.tools.publishing import register


@pytest.fixture
def pub_tools(tmp_output_dir, mock_models):
    mcp = MagicMock()
    registered = {}

    def capture_tool():
        def decorator(fn):
            registered[fn.__name__] = fn
            return fn
        return decorator

    mcp.tool = capture_tool
    register(mcp, mock_models, tmp_output_dir)
    return registered, mock_models


class TestPublishGithubRelease:
    def test_model_not_found(self, pub_tools):
        tools, _ = pub_tools
        result = tools["publish_github_release"](
            name="nonexistent", repo="user/repo", tag="v1.0"
        )
        assert "not found" in result.lower() or "error" in result.lower()


class TestPublishThingiverse:
    def test_no_token(self, pub_tools, mock_env):
        tools, _ = pub_tools
        mock_env(THINGIVERSE_TOKEN=None)
        result = tools["publish_thingiverse"](
            name="test_box", title="Test", description="A test"
        )
        assert "token" in result.lower() or "error" in result.lower()


class TestPublishMyminifactory:
    def test_no_token(self, pub_tools, mock_env):
        tools, _ = pub_tools
        mock_env(MYMINIFACTORY_TOKEN=None)
        result = tools["publish_myminifactory"](
            name="test_box", title="Test", description="A test"
        )
        assert "token" in result.lower() or "error" in result.lower()


class TestPublishCults3d:
    def test_no_api_key(self, pub_tools, mock_env):
        tools, _ = pub_tools
        mock_env(CULTS3D_API_KEY=None)
        result = tools["publish_cults3d"](
            name="test_box", title="Test", description="A test"
        )
        assert "key" in result.lower() or "error" in result.lower()
```

- [ ] **Step 3: Create `src/threedp_mcp/tools/community.py`**

Extract from `server.py` lines 1691-1750. Uses `urllib` for HTTP requests, `os.environ.get` for API key.

- [ ] **Step 4: Create `src/threedp_mcp/tools/publishing.py`**

Extract from `server.py` lines 1768-2254. Import `ensure_exported` from helpers. Pass `models` and `output_dir` through closure.

- [ ] **Step 5: Run tests, commit**

Run: `make test`
Stage: `src/threedp_mcp/tools/community.py src/threedp_mcp/tools/publishing.py tests/test_community.py tests/test_publishing.py`
Message: "Extract community and publishing tools with tests"

---

## Chunk 3: Server Entrypoint, Migration, and Integration Tests

### Task 10: Create thin server entrypoint

**Files:**
- Create: `src/threedp_mcp/server.py`

- [ ] **Step 1: Create `src/threedp_mcp/server.py`**

```python
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
```

- [ ] **Step 2: Verify `make run` starts without error**

Run: `make run` (then Ctrl+C after it starts)
Expected: Server starts, shows MCP ready message.

- [ ] **Step 3: Commit**

Stage: `src/threedp_mcp/server.py`
Message: "Add thin server entrypoint"

---

### Task 11: Move legacy files and clean up

**Files:**
- Move: `analyze_all.py` -> `scripts/analyze_all.py`
- Move: `build_all_tracks.py` -> `scripts/build_all_tracks.py`
- Move: `build_pit_lane.py` -> `scripts/build_pit_lane.py`
- Move: `build_startfinish.py` -> `scripts/build_startfinish.py`
- Move: `inspect_stls.py` -> `scripts/inspect_stls.py`
- Delete: `setup.bat`, `setup.ps1`
- Delete: `requirements.txt`
- Delete: old `server.py` (root level)

- [ ] **Step 1: Move legacy scripts**

```
mkdir -p scripts
git mv analyze_all.py scripts/
git mv build_all_tracks.py scripts/
git mv build_pit_lane.py scripts/
git mv build_startfinish.py scripts/
git mv inspect_stls.py scripts/
```

- [ ] **Step 2: Remove replaced files**

```
git rm setup.bat setup.ps1 requirements.txt server.py
```

- [ ] **Step 3: Remove old `.venv/` locally**

The `.venv/` directory is in `.gitignore` so it's not tracked. Just delete locally:
`rm -rf .venv`

- [ ] **Step 4: Commit**

Stage all changes.
Message: "Move legacy scripts to scripts/, remove replaced files"

---

### Task 12: Update README.md and CLAUDE.md

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Rewrite `README.md`**

Update to reflect new uv-based setup, plugin installation, Makefile usage. Keep tool table. Update clone URL to fork. Remove Windows setup.bat/setup.ps1 references — replaced by `make install`.

Key sections:
- Quick Setup: `git clone`, `make install`, `make run`
- Plugin Install: `claude plugin add /path/to/3dp-mcp-server`
- Development: `make test`, `make lint`, `make verify`
- Keep existing tool table
- Update Requirements to mention uv

- [ ] **Step 2: Update `CLAUDE.md`**

Update to reflect new package structure:
- Source is in `src/threedp_mcp/`
- Tools are in `src/threedp_mcp/tools/` (list modules)
- Shared helpers in `src/threedp_mcp/helpers.py`
- Constants in `src/threedp_mcp/constants.py`
- Use `make` targets for development
- Keep build123d coding patterns and design guidelines (unchanged)

- [ ] **Step 3: Commit**

Stage: `README.md CLAUDE.md`
Message: "Update README and CLAUDE.md for new package structure"

---

### Task 13: Integration tests

**Files:**
- Create: `tests/integration/conftest.py`
- Create: `tests/integration/test_full_pipeline.py`

- [ ] **Step 1: Create `tests/integration/conftest.py`**

```python
"""Integration test configuration — auto-marks all tests with @pytest.mark.integration."""

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
```

- [ ] **Step 2: Create `tests/integration/test_full_pipeline.py`**

```python
"""Integration tests — require build123d installed."""

import json
import os

import pytest


@pytest.fixture
def server_tools(tmp_path):
    """Set up a fresh server instance with real build123d."""
    from mcp.server.fastmcp import FastMCP
    from threedp_mcp.tools import register_all_tools

    mcp = FastMCP("test-server")
    models = {}
    output_dir = str(tmp_path / "outputs")
    os.makedirs(output_dir, exist_ok=True)

    registered = {}

    def capture_tool():
        def decorator(fn):
            registered[fn.__name__] = fn
            return fn
        return decorator

    mcp.tool = capture_tool
    register_all_tools(mcp, models, output_dir)
    return registered, models, output_dir


class TestCreateMeasureExportPipeline:
    def test_create_box(self, server_tools):
        tools, models, output_dir = server_tools
        result = tools["create_model"](name="box", code="result = Box(20, 30, 10)")
        parsed = json.loads(result)
        assert "box" in models
        assert parsed["bbox"]["size"] == [20.0, 30.0, 10.0]

    def test_measure_model(self, server_tools):
        tools, models, output_dir = server_tools
        tools["create_model"](name="box", code="result = Box(20, 30, 10)")
        result = tools["measure_model"](name="box")
        parsed = json.loads(result)
        assert parsed["volume"] > 0

    def test_export_stl(self, server_tools):
        tools, models, output_dir = server_tools
        tools["create_model"](name="box", code="result = Box(20, 30, 10)")
        result = tools["export_model"](name="box", format="stl")
        stl_path = os.path.join(output_dir, "box.stl")
        assert os.path.exists(stl_path)

    def test_analyze_printability(self, server_tools):
        tools, models, output_dir = server_tools
        tools["create_model"](name="box", code="result = Box(20, 30, 10)")
        result = tools["analyze_printability"](name="box")
        parsed = json.loads(result)
        assert "watertight" in parsed or "is_watertight" in parsed


class TestTransformPipeline:
    def test_transform_and_combine(self, server_tools):
        tools, models, output_dir = server_tools
        tools["create_model"](name="box1", code="result = Box(20, 20, 20)")
        tools["create_model"](name="cyl1", code="result = Cylinder(5, 30)")
        result = tools["combine_models"](
            name="combined", model_a="box1", model_b="cyl1", operation="subtract"
        )
        assert "combined" in models

    def test_boolean_subtract_reduces_volume(self, server_tools):
        tools, models, output_dir = server_tools
        tools["create_model"](name="box", code="result = Box(20, 20, 20)")
        tools["create_model"](name="hole", code="result = Cylinder(5, 30)")
        tools["combine_models"](
            name="drilled", model_a="box", model_b="hole", operation="subtract"
        )
        box_vol = models["box"]["volume"]
        drilled_vol = models["drilled"]["volume"]
        assert drilled_vol < box_vol
```

- [ ] **Step 3: Run integration tests**

Run: `make test-integration`
Expected: All unit and integration tests pass (integration tests only run if build123d is installed).

- [ ] **Step 4: Commit**

Stage: `tests/integration/`
Message: "Add integration tests for full create-measure-export pipeline"

---

### Task 14: Final verification

- [ ] **Step 1: Run full verify**

Run: `make verify`
Expected: Lint passes, all unit tests pass.

- [ ] **Step 2: Run integration tests**

Run: `make test-integration`
Expected: All tests pass.

- [ ] **Step 3: Verify server starts**

Run: `make run` (Ctrl+C after startup)
Expected: Server starts cleanly.

- [ ] **Step 4: Verify all 33 tools are registered**

Inspect the tool registration by checking all 8 modules register their expected tools. Count expected: core(6) + transform(3) + modification(4) + analysis(6) + utility(3) + components(6) + community(1) + publishing(4) = 33.

- [ ] **Step 5: Final commit if any fixes were needed**

Stage all changes.
Message: "Fix issues found during final verification"
