"""Tests for threedp_mcp.tools.components."""

import json
from unittest.mock import MagicMock


def make_mcp_and_register():
    """Create a mock MCP and register components tools, returning (mcp, tools_dict)."""
    from threedp_mcp.tools.components import register

    tools = {}
    models = {}
    output_dir = "/tmp/test_components_output"

    mcp = MagicMock()

    def tool_decorator():
        def decorator(fn):
            tools[fn.__name__] = fn
            return fn

        return decorator

    mcp.tool = tool_decorator
    register(mcp, models, output_dir)
    return tools, models, output_dir


class TestCreateEnclosure:
    def setup_method(self):
        self.tools, self.models, self.output_dir = make_mcp_and_register()

    def test_negative_width_returns_error(self):
        result = json.loads(
            self.tools["create_enclosure"](name="box", inner_width=-10, inner_depth=50, inner_height=30)
        )
        assert result["success"] is False
        assert "positive" in result["error"].lower() or "Dimensions" in result["error"]

    def test_negative_depth_returns_error(self):
        result = json.loads(self.tools["create_enclosure"](name="box", inner_width=50, inner_depth=-5, inner_height=30))
        assert result["success"] is False

    def test_negative_height_returns_error(self):
        result = json.loads(self.tools["create_enclosure"](name="box", inner_width=50, inner_depth=30, inner_height=0))
        assert result["success"] is False


class TestCreateSnapFit:
    def setup_method(self):
        self.tools, self.models, self.output_dir = make_mcp_and_register()

    def test_invalid_type_returns_error(self):
        result = json.loads(self.tools["create_snap_fit"](name="snap1", snap_type="butterfly"))
        assert result["success"] is False
        assert "butterfly" in result["error"]

    def test_unknown_type_message_mentions_supported(self):
        result = json.loads(self.tools["create_snap_fit"](name="snap1", snap_type="invalid"))
        assert "cantilever" in result["error"]


class TestCreateGear:
    def setup_method(self):
        self.tools, self.models, self.output_dir = make_mcp_and_register()

    def test_zero_teeth_returns_error(self):
        result = json.loads(self.tools["create_gear"](name="gear1", teeth=0))
        assert result["success"] is False
        assert "teeth" in result["error"].lower()

    def test_negative_teeth_returns_error(self):
        result = json.loads(self.tools["create_gear"](name="gear1", teeth=-5))
        assert result["success"] is False


class TestGenerateLabel:
    def setup_method(self):
        self.tools, self.models, self.output_dir = make_mcp_and_register()

    def test_empty_text_returns_error(self):
        result = json.loads(self.tools["generate_label"](name="label1", text=""))
        assert result["success"] is False
        assert "empty" in result["error"].lower() or "text" in result["error"].lower()

    def test_non_empty_text_returns_string(self):
        """generate_label with valid text should return a JSON string (success or failure)."""
        result_str = self.tools["generate_label"](name="label1", text="Hello")
        assert isinstance(result_str, str)
        result = json.loads(result_str)
        # Either succeeds or fails gracefully — both are valid (build123d may not be available)
        assert "success" in result
