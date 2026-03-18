"""Community tools — search models on Thingiverse."""

import json
import os
import traceback
import urllib.parse
import urllib.request


def register(mcp, models: dict, output_dir: str):
    @mcp.tool()
    def search_models(query: str, source: str = "thingiverse", max_results: int = 10) -> str:
        """Search for 3D models on Thingiverse.

        Requires THINGIVERSE_API_KEY environment variable.

        Args:
            query: Search query string
            source: Model source - "thingiverse" (default)
            max_results: Maximum number of results (default 10)
        """
        if source.lower() != "thingiverse":
            return json.dumps(
                {"success": False, "error": f"Unsupported source: {source}. Currently only 'thingiverse' is supported."}
            )

        api_key = os.environ.get("THINGIVERSE_API_KEY", "")
        if not api_key:
            return json.dumps(
                {
                    "success": False,
                    "error": "THINGIVERSE_API_KEY environment variable not set. "
                    "Register at https://www.thingiverse.com/developers to get an API key.",
                }
            )

        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.thingiverse.com/search/{encoded_query}?type=things&per_page={max_results}"
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})

            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            results = []
            hits = data if isinstance(data, list) else data.get("hits", data.get("things", []))
            for item in hits[:max_results]:
                results.append(
                    {
                        "title": item.get("name", ""),
                        "author": item.get("creator", {}).get("name", "")
                        if isinstance(item.get("creator"), dict)
                        else "",
                        "url": item.get("public_url", ""),
                        "thumbnail": item.get("thumbnail", ""),
                        "like_count": item.get("like_count", 0),
                        "download_count": item.get("download_count", 0),
                    }
                )

            return json.dumps(
                {
                    "success": True,
                    "query": query,
                    "source": source,
                    "result_count": len(results),
                    "results": results,
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)
