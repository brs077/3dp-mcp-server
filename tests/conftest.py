"""Shared test fixtures."""

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
            "code": "result = Box(10, 20, 30)",
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
