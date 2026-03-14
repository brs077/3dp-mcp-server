# `transform_model`

**Category:** Transform & Combine

Apply spatial transformations to a model. The `operations` parameter is a JSON string containing a single operation dict or a list of operation dicts applied in order.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the new transformed model |
| `source_name` | string | *required* | Name of the existing model to transform |
| `operations` | string (JSON) | *required* | Transformation operations (see below) |

**Operation keys:**

| Key | Value | Description |
|-----|-------|-------------|
| `"scale"` | `float` or `[x, y, z]` | Uniform or per-axis scale factor |
| `"rotate"` | `[rx, ry, rz]` | Rotation in degrees around X, Y, Z axes |
| `"mirror"` | `"XY"`, `"XZ"`, or `"YZ"` | Mirror across a plane |
| `"translate"` | `[x, y, z]` | Translation in mm |

**Example usage (multiple operations):**

```json
{
  "name": "transform_model",
  "arguments": {
    "name": "bracket_rotated",
    "source_name": "bracket",
    "operations": "[{\"rotate\": [0, 0, 45]}, {\"translate\": [10, 0, 0]}]"
  }
}
```

**Example usage (uniform scale):**

```json
{
  "name": "transform_model",
  "arguments": {
    "name": "bracket_small",
    "source_name": "bracket",
    "operations": "{\"scale\": 0.5}"
  }
}
```

**Example response:**

```json
{
  "name": "bracket_rotated",
  "bbox": { "x": 45.2, "y": 38.1, "z": 15.0 },
  "volume_mm3": 4502.65
}
```

**Tips:**
- Operations are applied sequentially when given as a list. Order matters: rotating then translating differs from translating then rotating.
- Non-uniform scale uses an `[x, y, z]` array, e.g., `[1.0, 1.0, 2.0]` to double the height.

---

[Back to Tool Index](../README.md)
