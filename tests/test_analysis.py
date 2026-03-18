"""Tests for threedp_mcp.tools.analysis."""

import json

import pytest

from threedp_mcp.tools.analysis import register


class FakeMCP:
    """Minimal MCP stub that collects registered tools."""

    def __init__(self):
        self._tools = {}

    def tool(self):
        def decorator(fn):
            self._tools[fn.__name__] = fn
            return fn

        return decorator

    def __getattr__(self, name):
        if name in self._tools:
            return self._tools[name]
        raise AttributeError(name)


@pytest.fixture
def mcp_tools(mock_models, tmp_output_dir):
    """Register analysis tools and return (mcp, models, output_dir)."""
    mcp = FakeMCP()
    register(mcp, mock_models, tmp_output_dir)
    return mcp, mock_models, tmp_output_dir


class TestEstimatePrint:
    def test_model_not_found(self, mcp_tools):
        mcp, models, output_dir = mcp_tools
        result = json.loads(mcp._tools["estimate_print"]("nonexistent"))
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_invalid_material(self, mcp_tools):
        mcp, models, output_dir = mcp_tools
        # Add area attribute to mock shape
        models["test_box"]["shape"].area = 2000.0
        result = json.loads(mcp._tools["estimate_print"]("test_box", material="UNOBTANIUM"))
        assert result["success"] is False
        assert "Unknown material" in result["error"]

    def test_valid_estimate_returns_json(self, mcp_tools):
        mcp, models, output_dir = mcp_tools
        # Shape needs .area for surface area calculation
        models["test_box"]["shape"].area = 2200.0
        result = json.loads(mcp._tools["estimate_print"]("test_box", infill_percent=15.0, material="PLA"))
        assert result["success"] is True
        assert result["name"] == "test_box"
        assert result["material"] == "PLA"
        assert "weight_g" in result
        assert "filament_length_m" in result
        assert "estimated_cost_usd" in result
        assert result["weight_g"] > 0


class TestAnalyzeOverhangs:
    def test_model_not_found(self, mcp_tools):
        mcp, models, output_dir = mcp_tools
        result = json.loads(mcp._tools["analyze_overhangs"]("missing_model"))
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_no_overhangs_flat_face(self, mcp_tools):
        from tests.conftest import FakeFace, FakeShape

        mcp, models, output_dir = mcp_tools
        flat_shape = FakeShape(faces=[FakeFace(area=100.0, normal_z=1.0)])
        models["flat"] = {"shape": flat_shape, "bbox": {"size": [10, 10, 10]}, "volume": 1000.0, "code": ""}
        result = json.loads(mcp._tools["analyze_overhangs"]("flat"))
        assert result["success"] is True
        assert result["overhang_face_count"] == 0


class TestSuggestOrientation:
    def test_model_not_found(self, mcp_tools):
        mcp, models, output_dir = mcp_tools
        result = json.loads(mcp._tools["suggest_orientation"]("missing_model"))
        assert result["success"] is False
        assert "not found" in result["error"]


class TestSplitModelByColor:
    def test_source_model_not_found(self, mcp_tools):
        mcp, models, output_dir = mcp_tools
        assignments = json.dumps([{"faces": "rest", "color": "#FF0000", "filament": 0}])
        result = json.loads(mcp._tools["split_model_by_color"]("output", "nonexistent", assignments))
        assert result["success"] is False
        assert "not found" in result["error"]
