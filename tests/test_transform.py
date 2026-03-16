"""Tests for threedp_mcp.tools.transform."""

import json
from unittest.mock import MagicMock, patch

from threedp_mcp.tools.transform import register


def make_mcp_and_tools(models, output_dir="/tmp/outputs"):
    """Register transform tools and return a dict of tool_name -> callable."""
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


class TestTransformModel:
    def test_source_not_found_returns_error(self):
        tools = make_mcp_and_tools({})
        result = json.loads(tools["transform_model"]("new", "missing", '{"translate": [1, 0, 0]}'))
        assert result["success"] is False
        assert "missing" in result["error"]

    def test_translate_creates_new_model(self, mock_models):
        translated_shape = MagicMock()
        translated_shape.bounding_box.return_value = MagicMock(
            min=MagicMock(X=1, Y=0, Z=0),
            max=MagicMock(X=11, Y=20, Z=30),
        )
        translated_shape.volume = 6000.0

        # Pos(tx, ty, tz) returns a locator; locator * shape returns translated_shape
        mock_locator = MagicMock()
        mock_locator.__mul__ = MagicMock(return_value=translated_shape)
        mock_pos = MagicMock(return_value=mock_locator)

        mock_b3d = MagicMock()
        mock_b3d.Pos = mock_pos
        mock_b3d.Rot = MagicMock()
        mock_b3d.Mirror = MagicMock()
        mock_b3d.Plane = MagicMock(XY=None, XZ=None, YZ=None)

        with patch.dict("sys.modules", {"build123d": mock_b3d}):
            tools = make_mcp_and_tools(mock_models)
            result = json.loads(tools["transform_model"]("moved", "test_box", '{"translate": [1, 0, 0]}'))

        assert result["success"] is True
        assert result["name"] == "moved"
        assert "moved" in mock_models

    def test_invalid_json_operations_returns_error(self, mock_models):
        tools = make_mcp_and_tools(mock_models)
        result = json.loads(tools["transform_model"]("out", "test_box", "not-json"))
        assert result["success"] is False

    def test_invalid_mirror_plane_returns_error(self, mock_models, mock_shape):
        with patch.dict(
            "sys.modules",
            {
                "build123d": MagicMock(
                    Pos=MagicMock(),
                    Rot=MagicMock(),
                    Mirror=MagicMock(),
                    Plane=MagicMock(XY=None, XZ=None, YZ=None),
                )
            },
        ):
            tools = make_mcp_and_tools(mock_models)
            result = json.loads(tools["transform_model"]("out", "test_box", '{"mirror": "XW"}'))

        assert result["success"] is False
        assert "XW" in result["error"]


class TestCombineModels:
    def test_model_a_not_found_returns_error(self):
        tools = make_mcp_and_tools({})
        result = json.loads(tools["combine_models"]("out", "missing_a", "missing_b"))
        assert result["success"] is False
        assert "missing_a" in result["error"]

    def test_model_b_not_found_returns_error(self, mock_models):
        tools = make_mcp_and_tools(mock_models)
        result = json.loads(tools["combine_models"]("out", "test_box", "missing_b"))
        assert result["success"] is False
        assert "missing_b" in result["error"]

    def test_invalid_operation_returns_error(self, mock_models):
        # Add a second model so both models are found
        second_shape = MagicMock()
        second_shape.bounding_box.return_value = MagicMock(
            min=MagicMock(X=0, Y=0, Z=0),
            max=MagicMock(X=5, Y=5, Z=5),
        )
        second_shape.volume = 125.0
        mock_models["box2"] = {
            "shape": second_shape,
            "code": "result = Box(5, 5, 5)",
            "bbox": {"min": [0, 0, 0], "max": [5, 5, 5], "size": [5, 5, 5]},
            "volume": 125.0,
        }

        tools = make_mcp_and_tools(mock_models)
        result = json.loads(tools["combine_models"]("out", "test_box", "box2", "xor"))
        assert result["success"] is False
        assert "xor" in result["error"]

    def test_union_creates_new_model(self, mock_models):
        # Use MagicMock shapes so __add__ can be controlled
        shape_a = MagicMock()
        shape_b = MagicMock()
        combined_shape = MagicMock()
        combined_shape.bounding_box.return_value = MagicMock(
            min=MagicMock(X=0, Y=0, Z=0),
            max=MagicMock(X=10, Y=20, Z=30),
        )
        combined_shape.volume = 6125.0
        shape_a.__add__ = MagicMock(return_value=combined_shape)

        mock_models["test_box"]["shape"] = shape_a
        mock_models["box2"] = {
            "shape": shape_b,
            "code": "result = Box(5, 5, 5)",
            "bbox": {"min": [0, 0, 0], "max": [5, 5, 5], "size": [5, 5, 5]},
            "volume": 125.0,
        }

        tools = make_mcp_and_tools(mock_models)
        result = json.loads(tools["combine_models"]("combined", "test_box", "box2", "union"))

        assert result["success"] is True
        assert result["name"] == "combined"
        assert result["operation"] == "union"
        assert "combined" in mock_models


class TestImportModel:
    def test_file_not_found_returns_error(self):
        mock_b3d = MagicMock()
        mock_b3d.import_stl = MagicMock(side_effect=FileNotFoundError("file not found"))

        with patch.dict("sys.modules", {"build123d": mock_b3d}):
            tools = make_mcp_and_tools({})
            result = json.loads(tools["import_model"]("imported", "/nonexistent/path/model.stl"))

        assert result["success"] is False

    def test_unsupported_extension_returns_error(self):
        tools = make_mcp_and_tools({})
        result = json.loads(tools["import_model"]("imported", "/some/file.obj"))
        assert result["success"] is False
        assert ".obj" in result["error"]

    def test_stl_import_creates_model(self, mock_models, tmp_path):
        stl_file = tmp_path / "test.stl"
        stl_file.write_text("fake stl content")

        imported_shape = MagicMock()
        imported_shape.bounding_box.return_value = MagicMock(
            min=MagicMock(X=0, Y=0, Z=0),
            max=MagicMock(X=10, Y=10, Z=10),
        )
        imported_shape.volume = 1000.0

        with patch.dict("sys.modules", {"build123d": MagicMock(import_stl=MagicMock(return_value=imported_shape))}):
            tools = make_mcp_and_tools(mock_models)
            result = json.loads(tools["import_model"]("imported", str(stl_file)))

        assert result["success"] is True
        assert result["name"] == "imported"
        assert "imported" in mock_models
