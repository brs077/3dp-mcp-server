"""Tests for threedp_mcp.helpers."""

import os
from unittest.mock import MagicMock, patch

import pytest

from threedp_mcp.helpers import (
    compute_overhangs,
    ensure_exported,
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


class TestSelectFace:
    def test_selects_top_face(self):
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
