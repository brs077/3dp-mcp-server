"""Tests for threedp_mcp.tools.core."""

import json
from unittest.mock import MagicMock, patch

import pytest

from threedp_mcp.tools.core import register


class MockMCP:
    """Minimal MCP stub that captures registered tools."""

    def __init__(self):
        self.tools = {}

    def tool(self):
        """Decorator that captures the registered function by name."""

        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


@pytest.fixture
def mcp():
    return MockMCP()


@pytest.fixture
def registered(mcp, mock_models, tmp_output_dir):
    """Register core tools and return (mcp, models, output_dir)."""
    register(mcp, mock_models, tmp_output_dir)
    return mcp, mock_models, tmp_output_dir


@pytest.fixture
def empty_registered(mcp, tmp_output_dir):
    """Register core tools with an empty models dict."""
    models = {}
    register(mcp, models, tmp_output_dir)
    return mcp, models, tmp_output_dir


class TestListModels:
    def test_empty_models(self, empty_registered):
        mcp, models, _ = empty_registered
        result = json.loads(mcp.tools["list_models"]())
        assert result["models"] == []
        assert "No models yet" in result["message"]

    def test_populated_models(self, registered):
        mcp, models, _ = registered
        result = json.loads(mcp.tools["list_models"]())
        assert len(result["models"]) == 1
        assert result["models"][0]["name"] == "test_box"
        assert result["models"][0]["volume"] == 6000.0


class TestGetModelCode:
    def test_valid_model_returns_code(self, registered):
        mcp, _, _ = registered
        result = json.loads(mcp.tools["get_model_code"]("test_box"))
        assert result["name"] == "test_box"
        assert result["code"] == "result = Box(10, 20, 30)"

    def test_missing_model_returns_error(self, registered):
        mcp, _, _ = registered
        result = json.loads(mcp.tools["get_model_code"]("nonexistent"))
        assert result["success"] is False
        assert "not found" in result["error"]


class TestCreateModel:
    def test_stores_model_on_success(self, mcp, tmp_output_dir):
        models = {}
        register(mcp, models, tmp_output_dir)

        fake_entry = {
            "shape": MagicMock(),
            "code": "result = Box(1,1,1)",
            "bbox": {"min": [0, 0, 0], "max": [1, 1, 1], "size": [1, 1, 1]},
            "volume": 1.0,
        }
        with (
            patch("threedp_mcp.tools.core.run_build123d_code", return_value=fake_entry),
            patch("threedp_mcp.tools.core.os.makedirs"),
            patch(
                "builtins.__import__",
                side_effect=lambda name, *args, **kwargs: (
                    MagicMock() if name == "build123d" else __import__(name, *args, **kwargs)
                ),
            ),
        ):
            # Patch the lazy build123d imports inside create_model
            with patch.dict("sys.modules", {"build123d": MagicMock()}):
                result = json.loads(mcp.tools["create_model"]("mybox", "result = Box(1,1,1)"))

        assert "mybox" in models
        assert result["success"] is True
        assert result["name"] == "mybox"

    def test_error_returns_error_json(self, mcp, tmp_output_dir):
        models = {}
        register(mcp, models, tmp_output_dir)

        with patch("threedp_mcp.tools.core.run_build123d_code", side_effect=ValueError("bad code")):
            result = json.loads(mcp.tools["create_model"]("bad", "not valid"))

        assert result["success"] is False
        assert "bad code" in result["error"]
        assert "traceback" in result


class TestExportModel:
    def test_missing_model_returns_error(self, registered):
        mcp, _, _ = registered
        result = json.loads(mcp.tools["export_model"]("ghost"))
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_unsupported_format_returns_error(self, registered):
        mcp, _, _ = registered
        with patch.dict("sys.modules", {"build123d": MagicMock()}):
            result = json.loads(mcp.tools["export_model"]("test_box", "obj"))
        assert result["success"] is False
        assert "Unsupported format" in result["error"]

    def test_stl_export_success(self, registered):
        mcp, _, _ = registered
        mock_b123d = MagicMock()
        with patch.dict("sys.modules", {"build123d": mock_b123d}):
            result = json.loads(mcp.tools["export_model"]("test_box", "stl"))
        assert result["success"] is True
        assert result["path"].endswith(".stl")


class TestMeasureModel:
    def test_valid_model_returns_measurements(self, registered):
        mcp, models, _ = registered
        # Give the shape an area attribute
        models["test_box"]["shape"].area = 2200.0
        result = json.loads(mcp.tools["measure_model"]("test_box"))
        assert result["name"] == "test_box"
        assert result["volume_mm3"] == 6000.0
        assert "bbox" in result
        assert "faces" in result

    def test_missing_model_returns_error(self, registered):
        mcp, _, _ = registered
        result = json.loads(mcp.tools["measure_model"]("ghost"))
        assert result["success"] is False
        assert "not found" in result["error"]


class TestAnalyzePrintability:
    def test_valid_model_returns_verdict(self, registered):
        mcp, models, _ = registered
        shape = models["test_box"]["shape"]
        shape.solids = MagicMock(return_value=[MagicMock()])
        shape.area = 2200.0
        result = json.loads(mcp.tools["analyze_printability"]("test_box"))
        assert "verdict" in result
        assert result["verdict"] in ("PRINTABLE", "REVIEW NEEDED")
        assert "checks" in result

    def test_missing_model_returns_error(self, registered):
        mcp, _, _ = registered
        result = json.loads(mcp.tools["analyze_printability"]("ghost"))
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_oversized_model_flags_issue(self, mcp, tmp_output_dir):
        from tests.conftest import FakeShape

        models = {
            "bigbox": {
                "shape": FakeShape(bbox_max=(400, 400, 400), volume=64000000.0),
                "code": "result = Box(400,400,400)",
                "bbox": {"min": [0, 0, 0], "max": [400, 400, 400], "size": [400, 400, 400]},
                "volume": 64000000.0,
            }
        }
        register(mcp, models, tmp_output_dir)
        result = json.loads(mcp.tools["analyze_printability"]("bigbox"))
        assert result["verdict"] == "REVIEW NEEDED"
        assert any("300mm" in issue for issue in result["issues"])
