"""Tests for threedp_mcp.tools.publishing."""

import json
from unittest.mock import patch

import pytest

from threedp_mcp.tools.publishing import register


class FakeMCP:
    """Minimal MCP stub that captures registered tools."""

    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


@pytest.fixture
def publishing_tools(mock_models, tmp_output_dir):
    mcp = FakeMCP()
    register(mcp, mock_models, tmp_output_dir)
    return mcp.tools


class TestPublishGithubRelease:
    def test_model_not_found(self, publishing_tools):
        result = json.loads(
            publishing_tools["publish_github_release"](
                name="nonexistent",
                repo="owner/repo",
                tag="v1.0.0",
            )
        )
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_no_gh_and_no_token(self, publishing_tools, mock_models, tmp_output_dir, mock_env):
        # Create a fake STL so ensure_exported finds an existing file
        import os

        stl_path = os.path.join(tmp_output_dir, "test_box.stl")
        with open(stl_path, "w") as f:
            f.write("fake stl")

        mock_env(GITHUB_TOKEN=None)
        with patch("shutil.which", return_value=None):
            result = json.loads(
                publishing_tools["publish_github_release"](
                    name="test_box",
                    repo="owner/repo",
                    tag="v1.0.0",
                    formats='["stl"]',
                )
            )
        assert result["success"] is False
        assert "GITHUB_TOKEN" in result["error"]


class TestPublishThingiverse:
    def test_no_token_error(self, publishing_tools, mock_env):
        mock_env(THINGIVERSE_TOKEN=None)
        result = json.loads(
            publishing_tools["publish_thingiverse"](
                name="test_box",
                title="My Box",
            )
        )
        assert result["success"] is False
        assert "THINGIVERSE_TOKEN" in result["error"]

    def test_model_not_found(self, publishing_tools, mock_env):
        mock_env(THINGIVERSE_TOKEN="fake_token")
        result = json.loads(
            publishing_tools["publish_thingiverse"](
                name="nonexistent",
                title="My Box",
            )
        )
        assert result["success"] is False
        assert "not found" in result["error"]


class TestPublishMyMiniFactory:
    def test_no_token_error(self, publishing_tools, mock_env):
        mock_env(MYMINIFACTORY_TOKEN=None)
        result = json.loads(
            publishing_tools["publish_myminifactory"](
                name="test_box",
                title="My Box",
            )
        )
        assert result["success"] is False
        assert "MYMINIFACTORY_TOKEN" in result["error"]

    def test_model_not_found(self, publishing_tools, mock_env):
        mock_env(MYMINIFACTORY_TOKEN="fake_token")
        result = json.loads(
            publishing_tools["publish_myminifactory"](
                name="nonexistent",
                title="My Box",
            )
        )
        assert result["success"] is False
        assert "not found" in result["error"]


class TestPublishCults3D:
    def test_no_api_key_error(self, publishing_tools, mock_env):
        mock_env(CULTS3D_API_KEY=None)
        result = json.loads(
            publishing_tools["publish_cults3d"](
                name="test_box",
                title="My Box",
            )
        )
        assert result["success"] is False
        assert "CULTS3D_API_KEY" in result["error"]

    def test_model_not_found(self, publishing_tools, mock_env):
        mock_env(CULTS3D_API_KEY="fake_key")
        result = json.loads(
            publishing_tools["publish_cults3d"](
                name="nonexistent",
                title="My Box",
            )
        )
        assert result["success"] is False
        assert "not found" in result["error"]
