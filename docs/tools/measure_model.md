# `measure_model`

**Category:** Core

Return precise measurements for a model including bounding box, volume, surface area, and topology counts.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |

**Example usage:**

```json
{
  "name": "measure_model",
  "arguments": {
    "name": "bracket"
  }
}
```

**Example response:**

```json
{
  "bbox": { "x": 40.0, "y": 20.0, "z": 15.0 },
  "volume_mm3": 4502.65,
  "surface_area_mm2": 3120.50,
  "face_count": 12,
  "edge_count": 24
}
```

---

[Back to Tool Index](../README.md)
