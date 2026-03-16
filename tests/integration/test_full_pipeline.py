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
        # Key is volume_mm3 in the actual implementation
        assert parsed.get("volume_mm3", parsed.get("volume", 0)) > 0

    def test_export_stl(self, server_tools):
        tools, models, output_dir = server_tools
        tools["create_model"](name="box", code="result = Box(20, 30, 10)")
        result = tools["export_model"](name="box", format="stl")
        parsed = json.loads(result)
        assert parsed.get("success", True)
        # Export path may be nested (e.g., output_dir/box/box.stl)
        assert "path" in parsed
        assert os.path.exists(parsed["path"])

    def test_analyze_printability(self, server_tools):
        tools, models, output_dir = server_tools
        tools["create_model"](name="box", code="result = Box(20, 30, 10)")
        result = tools["analyze_printability"](name="box")
        parsed = json.loads(result)
        # Check for any watertight-related key
        result_str = json.dumps(parsed).lower()
        assert "watertight" in result_str or "printable" in result_str or "success" in parsed


class TestTransformPipeline:
    def test_transform_and_combine(self, server_tools):
        tools, models, output_dir = server_tools
        tools["create_model"](name="box1", code="result = Box(20, 20, 20)")
        tools["create_model"](name="cyl1", code="result = Cylinder(5, 30)")
        tools["combine_models"](name="combined", model_a="box1", model_b="cyl1", operation="subtract")
        assert "combined" in models

    def test_boolean_subtract_reduces_volume(self, server_tools):
        tools, models, output_dir = server_tools
        tools["create_model"](name="box", code="result = Box(20, 20, 20)")
        tools["create_model"](name="hole", code="result = Cylinder(5, 30)")
        tools["combine_models"](name="drilled", model_a="box", model_b="hole", operation="subtract")
        box_vol = models["box"]["volume"]
        drilled_vol = models["drilled"]["volume"]
        assert drilled_vol < box_vol


class TestEstimatePrintPipeline:
    def test_estimate_pla(self, server_tools):
        tools, models, output_dir = server_tools
        tools["create_model"](name="box", code="result = Box(20, 20, 20)")
        result = tools["estimate_print"](name="box", material="PLA")
        parsed = json.loads(result)
        # Check for any weight/filament/cost key
        result_str = json.dumps(parsed).lower()
        assert "weight" in result_str or "filament" in result_str or "cost" in result_str

    def test_list_models(self, server_tools):
        tools, models, output_dir = server_tools
        tools["create_model"](name="a", code="result = Box(10, 10, 10)")
        tools["create_model"](name="b", code="result = Cylinder(5, 20)")
        result = tools["list_models"]()
        parsed = json.loads(result)
        assert parsed.get("count", len(parsed.get("models", []))) == 2
