# `create_dovetail`

**Category:** Parametric Components

Generate a dovetail joint (male or female half) for interlocking two parts.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the dovetail model |
| `dovetail_type` | string | `"male"` | `"male"` (trapezoidal protrusion) or `"female"` (cavity in a block) |
| `width` | float | `20` | Width of the dovetail in mm |
| `height` | float | `10` | Height of the dovetail in mm |
| `depth` | float | `15` | Depth (slide length) in mm |
| `angle` | float | `10` | Dovetail angle in degrees |
| `clearance` | float | `0.2` | Clearance added to the female part in mm |

**Example usage:**

```json
{
  "name": "create_dovetail",
  "arguments": {
    "name": "rail_male",
    "dovetail_type": "male",
    "width": 25,
    "height": 8,
    "depth": 30,
    "angle": 12
  }
}
```

```json
{
  "name": "create_dovetail",
  "arguments": {
    "name": "rail_female",
    "dovetail_type": "female",
    "width": 25,
    "height": 8,
    "depth": 30,
    "angle": 12,
    "clearance": 0.25
  }
}
```

**Example response:**

```json
{
  "name": "rail_male",
  "dovetail_type": "male",
  "bbox": { "x": 25.0, "y": 15.0, "z": 8.0 }
}
```

**Tips:**
- Always create the male and female parts with the same `width`, `height`, `depth`, and `angle` so they mate correctly.
- The `clearance` on the female part ensures a sliding fit. Increase for looser tolerance.
- Use `combine_models` (subtract) to cut a dovetail slot into an existing part.

---

[Back to Tool Index](../README.md)
