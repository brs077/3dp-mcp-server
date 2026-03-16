"""Tests for threedp_mcp.tools.utility."""

import json
from unittest.mock import MagicMock

from threedp_mcp.tools.utility import register


def make_mcp_and_tools(models, output_dir="/tmp/test_output"):
    """Register utility tools and return a dict of callables by name."""
    mcp = MagicMock()
    registered = {}

    def tool_decorator():
        def decorator(fn):
            registered[fn.__name__] = fn
            return fn

        return decorator

    mcp.tool = tool_decorator
    register(mcp, models, output_dir)
    return registered


class TestShrinkageCompensation:
    def test_source_not_found(self):
        tools = make_mcp_and_tools({})
        result = json.loads(tools["shrinkage_compensation"]("out", "missing_model"))
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_invalid_material(self):
        mock_shape = MagicMock()
        models = {"my_model": {"shape": mock_shape, "bbox": [10, 10, 10]}}
        tools = make_mcp_and_tools(models)
        result = json.loads(tools["shrinkage_compensation"]("out", "my_model", material="UNOBTAINIUM"))
        assert result["success"] is False
        assert "Unknown material" in result["error"]


class TestPackModels:
    def test_empty_list_error(self):
        tools = make_mcp_and_tools({})
        result = json.loads(tools["pack_models"]("packed", "[]"))
        assert result["success"] is False
        assert "empty" in result["error"]

    def test_model_not_found(self):
        tools = make_mcp_and_tools({})
        result = json.loads(tools["pack_models"]("packed", '["nonexistent"]'))
        assert result["success"] is False
        assert "not found" in result["error"]


class TestConvertFormat:
    def test_input_file_not_found(self, tmp_path):
        tools = make_mcp_and_tools({})
        missing = str(tmp_path / "ghost.stl")
        output = str(tmp_path / "out.step")
        result = json.loads(tools["convert_format"](missing, output))
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_unsupported_input_format(self, tmp_path):
        tools = make_mcp_and_tools({})
        # Create a file with unsupported extension
        bad_file = tmp_path / "model.obj"
        bad_file.write_text("v 0 0 0\n")
        result = json.loads(tools["convert_format"](str(bad_file), str(tmp_path / "out.stl")))
        assert result["success"] is False
        assert "Unsupported input format" in result["error"]
