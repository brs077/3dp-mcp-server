# `export_model`

**Category:** Core

Export a previously created model to a specific file format.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |
| `format` | string | `"stl"` | Export format: `"stl"`, `"step"`, or `"3mf"` |

**Example usage:**

```json
{
  "name": "export_model",
  "arguments": {
    "name": "bracket",
    "format": "step"
  }
}
```

**Example response:**

```json
{
  "file": "/path/to/outputs/bracket.step",
  "format": "step",
  "size_bytes": 28410
}
```

---

[Back to Tool Index](../README.md)
