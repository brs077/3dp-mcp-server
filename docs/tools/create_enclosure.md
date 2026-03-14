# `create_enclosure`

**Category:** Parametric Components

Generate a parametric two-part enclosure (body + lid) with optional features. Creates two models: `<name>_body` and `<name>_lid`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Base name (produces `<name>_body` and `<name>_lid`) |
| `inner_width` | float | *required* | Interior width in mm |
| `inner_depth` | float | *required* | Interior depth in mm |
| `inner_height` | float | *required* | Interior height in mm |
| `wall` | float | `2.0` | Wall thickness in mm |
| `lid_type` | string | `"snap"` | `"snap"` (alignment ridge) or `"screw"` (corner screw holes) |
| `features` | string (JSON) | `"[]"` | JSON list of features: `"vent_slots"`, `"screw_posts"`, `"cable_hole"` |

**Example usage:**

```json
{
  "name": "create_enclosure",
  "arguments": {
    "name": "sensor_box",
    "inner_width": 60,
    "inner_depth": 40,
    "inner_height": 25,
    "wall": 2.5,
    "lid_type": "screw",
    "features": "[\"vent_slots\", \"cable_hole\"]"
  }
}
```

**Example response:**

```json
{
  "body": { "name": "sensor_box_body", "bbox": { "x": 65.0, "y": 45.0, "z": 27.5 } },
  "lid": { "name": "sensor_box_lid", "bbox": { "x": 65.0, "y": 45.0, "z": 4.0 } },
  "lid_type": "screw",
  "features": ["vent_slots", "cable_hole"]
}
```

**Tips:**
- The snap-fit lid includes an alignment ridge for a friction fit.
- The screw lid adds M3-sized holes in all four corners of both the body and lid.
- `"screw_posts"` adds internal mounting posts for attaching a PCB.

---

[Back to Tool Index](../README.md)
