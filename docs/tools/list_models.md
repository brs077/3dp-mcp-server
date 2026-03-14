# `list_models`

**Category:** Core

List all models currently loaded in the server session, with bounding box and volume for each.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| *(none)* | | | |

**Example usage:**

```json
{
  "name": "list_models",
  "arguments": {}
}
```

**Example response:**

```json
{
  "models": [
    { "name": "bracket", "bbox": { "x": 40.0, "y": 20.0, "z": 15.0 }, "volume_mm3": 4502.65 },
    { "name": "knob", "bbox": { "x": 25.0, "y": 25.0, "z": 12.0 }, "volume_mm3": 3100.00 }
  ]
}
```

---

[Back to Tool Index](../README.md)
