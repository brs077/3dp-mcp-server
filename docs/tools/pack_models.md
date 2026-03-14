# `pack_models`

**Category:** Utility

Arrange multiple models on the XY build plane with padding between them, aligning all bases to Z=0. Useful for preparing a multi-part print plate.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the packed arrangement |
| `model_names` | string (JSON) | *required* | JSON list of model names to pack |
| `padding` | float | `5.0` | Minimum gap between models in mm |

**Example usage:**

```json
{
  "name": "pack_models",
  "arguments": {
    "name": "print_plate",
    "model_names": "[\"bracket\", \"knob\", \"spacer\"]",
    "padding": 8.0
  }
}
```

**Example response:**

```json
{
  "name": "print_plate",
  "positions": [
    { "model": "bracket", "x": 0.0, "y": 0.0 },
    { "model": "knob", "x": 52.0, "y": 0.0 },
    { "model": "spacer", "x": 52.0, "y": 38.0 }
  ]
}
```

---

[Back to Tool Index](../README.md)
