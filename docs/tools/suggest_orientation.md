# `suggest_orientation`

**Category:** Analysis & Export

Automatically evaluate multiple print orientations and recommend the best ones. Tests 16 orientations (90-degree increments on X and Y axes) and scores each by overhang area, bed contact area, and build height.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |

**Example usage:**

```json
{
  "name": "suggest_orientation",
  "arguments": {
    "name": "bracket"
  }
}
```

**Example response:**

```json
{
  "candidates": [
    { "rank": 1, "rotation": [0, 0, 0], "score": 0.92, "overhang_area_mm2": 12.0, "bed_contact_mm2": 800.0, "height_mm": 15.0 },
    { "rank": 2, "rotation": [90, 0, 0], "score": 0.85, "overhang_area_mm2": 45.0, "bed_contact_mm2": 600.0, "height_mm": 20.0 },
    { "rank": 3, "rotation": [0, 90, 0], "score": 0.78, "overhang_area_mm2": 60.0, "bed_contact_mm2": 400.0, "height_mm": 40.0 }
  ]
}
```

**Tips:**
- After choosing an orientation, apply it with `transform_model` using the suggested `rotation` values.
- Lower overhang area and greater bed contact generally mean better print quality and less wasted support material.

---

[Back to Tool Index](../README.md)
