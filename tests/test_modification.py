"""Tests for threedp_mcp.tools.modification."""

import json
from unittest.mock import MagicMock, patch

from threedp_mcp.tools.modification import register


def make_mcp_and_tools(models, output_dir="outputs"):
    """Wire up a fake MCP and register modification tools, returning tool callables by name."""
    tools = {}

    class FakeMcp:
        def tool(self):
            def decorator(fn):
                tools[fn.__name__] = fn
                return fn

            return decorator

    mcp = FakeMcp()
    register(mcp, models, output_dir)
    return tools


class TestShellModel:
    def test_source_not_found(self):
        tools = make_mcp_and_tools({})
        result = json.loads(tools["shell_model"](name="out", source_name="missing"))
        assert result["success"] is False
        assert "missing" in result["error"]

    def test_calls_shell_on_shape(self, mock_models):
        shape = mock_models["test_box"]["shape"]
        shelled = MagicMock()
        shelled.bounding_box.return_value = shape.bounding_box()
        shelled.volume = 1000.0
        shape.shell = MagicMock(return_value=shelled)

        tools = make_mcp_and_tools(mock_models)
        result = json.loads(tools["shell_model"](name="out", source_name="test_box", thickness=2.0))

        assert result["success"] is True
        assert result["name"] == "out"
        assert result["thickness_mm"] == 2.0
        shape.shell.assert_called_once()
        assert "out" in mock_models


class TestSplitModel:
    def test_source_not_found(self):
        tools = make_mcp_and_tools({})
        result = json.loads(tools["split_model"](name="out", source_name="missing"))
        assert result["success"] is False
        assert "missing" in result["error"]

    def test_invalid_plane(self, mock_models):
        tools = make_mcp_and_tools(mock_models)
        result = json.loads(tools["split_model"](name="out", source_name="test_box", plane="DIAGONAL"))
        assert result["success"] is False
        assert "Unknown plane" in result["error"]

    def test_valid_plane_both(self, mock_models):
        from tests.conftest import FakeShape

        shape = mock_models["test_box"]["shape"]

        half_shape = FakeShape(volume=3000.0)

        # The split_model function creates Box objects from build123d and does shape & box.
        # Patch build123d.Box so it returns a MagicMock that FakeShape can operate with.
        fake_box = MagicMock()
        shape.__and__ = MagicMock(return_value=half_shape)
        fake_box.__rand__ = MagicMock(return_value=half_shape)

        with (
            patch("build123d.Box", return_value=fake_box),
            patch("build123d.Pos", return_value=MagicMock(__mul__=MagicMock(return_value=fake_box))),
        ):
            tools = make_mcp_and_tools(mock_models)
            result = json.loads(tools["split_model"](name="half", source_name="test_box", plane="XY", keep="both"))

        assert result["success"] is True
        assert "half_above" in result["results"]
        assert "half_below" in result["results"]


class TestCreateThreadedHole:
    def test_source_not_found(self):
        tools = make_mcp_and_tools({})
        result = json.loads(tools["create_threaded_hole"](name="out", source_name="missing", position="[0,0,0]"))
        assert result["success"] is False
        assert "missing" in result["error"]

    def test_invalid_thread_spec(self, mock_models):
        tools = make_mcp_and_tools(mock_models)
        result = json.loads(
            tools["create_threaded_hole"](name="out", source_name="test_box", position="[0,0,0]", thread_spec="M99")
        )
        assert result["success"] is False
        assert "Unknown thread spec" in result["error"]
        assert "M99" in result["error"]

    def test_valid_thread_spec_recorded(self, mock_models):

        fake_entry = {
            "shape": MagicMock(),
            "bbox": {"min": [0, 0, 0], "max": [10, 20, 30], "size": [10, 20, 30]},
            "volume": 5900.0,
            "code": "",
        }

        fake_cylinder = MagicMock()
        fake_hole = MagicMock()
        fake_pos_instance = MagicMock()
        fake_pos_instance.__mul__ = MagicMock(return_value=fake_hole)

        with (
            patch("build123d.Cylinder", return_value=fake_cylinder),
            patch("build123d.Pos", return_value=fake_pos_instance),
            patch("threedp_mcp.tools.modification.shape_to_model_entry", return_value=fake_entry),
        ):
            tools = make_mcp_and_tools(mock_models)
            result = json.loads(
                tools["create_threaded_hole"](name="out", source_name="test_box", position="[5,5,0]", thread_spec="M3")
            )

        assert result["success"] is True
        assert result["thread_spec"] == "M3"
        assert result["hole_type"] == "tap drill"
        assert "out" in mock_models
