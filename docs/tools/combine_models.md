# `combine_models`

**Category:** Transform & Combine

Perform a Boolean operation between two models.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the resulting model |
| `model_a` | string | *required* | Name of the first model |
| `model_b` | string | *required* | Name of the second model |
| `operation` | string | `"union"` | Boolean operation: `"union"`, `"subtract"`, or `"intersect"` |

**Example usage:**

```json
{
  "name": "combine_models",
  "arguments": {
    "name": "bracket_with_hole",
    "model_a": "bracket",
    "model_b": "cylinder_cutout",
    "operation": "subtract"
  }
}
```

**Example response:**

```json
{
  "name": "bracket_with_hole",
  "bbox": { "x": 40.0, "y": 20.0, "z": 15.0 },
  "volume_mm3": 4100.20
}
```

**Tips:**
- `"subtract"` removes `model_b` from `model_a`.
- Position models with `transform_model` before combining so they overlap correctly.

---

[Back to Tool Index](../README.md)
