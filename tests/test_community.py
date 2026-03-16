"""Tests for threedp_mcp.tools.community."""

import json
from unittest.mock import MagicMock, patch

import pytest

from threedp_mcp.tools.community import register


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
def community_tools(mock_models, tmp_output_dir):
    mcp = FakeMCP()
    register(mcp, mock_models, tmp_output_dir)
    return mcp.tools


class TestSearchModels:
    def test_no_api_key_returns_error(self, community_tools, mock_env):
        mock_env(THINGIVERSE_API_KEY=None)
        result = json.loads(community_tools["search_models"]("cube"))
        assert result["success"] is False
        assert "THINGIVERSE_API_KEY" in result["error"]

    def test_unsupported_source_returns_error(self, community_tools, mock_env):
        mock_env(THINGIVERSE_API_KEY="fake_key")
        result = json.loads(community_tools["search_models"]("cube", source="prusaprinters"))
        assert result["success"] is False
        assert "Unsupported source" in result["error"]

    def test_successful_search_with_mocked_urlopen(self, community_tools, mock_env):
        mock_env(THINGIVERSE_API_KEY="fake_key")
        fake_response_data = {
            "hits": [
                {
                    "name": "Cool Cube",
                    "creator": {"name": "designer_x"},
                    "public_url": "https://www.thingiverse.com/thing:12345",
                    "thumbnail": "https://cdn.thingiverse.com/thumb.jpg",
                    "like_count": 42,
                    "download_count": 100,
                }
            ]
        }
        fake_response = MagicMock()
        fake_response.read.return_value = json.dumps(fake_response_data).encode()
        fake_response.__enter__ = lambda s: s
        fake_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=fake_response):
            result = json.loads(community_tools["search_models"]("cube"))

        assert result["success"] is True
        assert result["result_count"] == 1
        assert result["results"][0]["title"] == "Cool Cube"
        assert result["results"][0]["author"] == "designer_x"

    def test_successful_search_list_response(self, community_tools, mock_env):
        mock_env(THINGIVERSE_API_KEY="fake_key")
        fake_response_data = [
            {
                "name": "Bracket",
                "creator": {"name": "maker"},
                "public_url": "https://www.thingiverse.com/thing:99",
                "thumbnail": "",
                "like_count": 5,
                "download_count": 10,
            }
        ]
        fake_response = MagicMock()
        fake_response.read.return_value = json.dumps(fake_response_data).encode()
        fake_response.__enter__ = lambda s: s
        fake_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=fake_response):
            result = json.loads(community_tools["search_models"]("bracket"))

        assert result["success"] is True
        assert result["result_count"] == 1
