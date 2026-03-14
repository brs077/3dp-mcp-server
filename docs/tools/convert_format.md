# `convert_format`

**Category:** Utility

Convert a 3D file between formats without storing it as a model in the server. Pure file-to-file conversion.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_path` | string | *required* | Absolute path to the input file |
| `output_path` | string | *required* | Absolute path for the output file |

**Supported formats:** `.stl`, `.step` / `.stp`, `.brep`, `.3mf`

**Example usage:**

```json
{
  "name": "convert_format",
  "arguments": {
    "input_path": "/Users/bryan/models/part.step",
    "output_path": "/Users/bryan/models/part.3mf"
  }
}
```

**Example response:**

```json
{
  "input": "/Users/bryan/models/part.step",
  "output": "/Users/bryan/models/part.3mf",
  "size_bytes": 41200
}
```

---

[Back to Tool Index](../README.md)
