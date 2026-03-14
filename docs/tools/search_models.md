# `search_models`

**Category:** Community

Search for publicly shared 3D models on Thingiverse.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | *required* | Search query string |
| `source` | string | `"thingiverse"` | Search source (currently only `"thingiverse"`) |
| `max_results` | int | `10` | Maximum number of results to return |

**Example usage:**

```json
{
  "name": "search_models",
  "arguments": {
    "query": "raspberry pi 4 case",
    "source": "thingiverse",
    "max_results": 5
  }
}
```

**Example response:**

```json
{
  "results": [
    {
      "title": "Raspberry Pi 4 Case with Fan Mount",
      "author": "maker42",
      "url": "https://www.thingiverse.com/thing:4150001",
      "thumbnail": "https://cdn.thingiverse.com/...",
      "like_count": 312,
      "download_count": 18500
    },
    {
      "title": "Modular RPi4 Enclosure",
      "author": "printlab",
      "url": "https://www.thingiverse.com/thing:4230042",
      "thumbnail": "https://cdn.thingiverse.com/...",
      "like_count": 189,
      "download_count": 9200
    }
  ]
}
```

**Tips:**
- Requires the `THINGIVERSE_API_KEY` environment variable to be set. Obtain an API key from the [Thingiverse developer portal](https://www.thingiverse.com/developers).
- Use specific search terms for better results (e.g., "M3 knurled thumb nut" rather than "nut").

---

[Back to Tool Index](../README.md)
