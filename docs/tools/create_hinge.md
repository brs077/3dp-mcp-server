# `create_hinge`

**Category:** Parametric Components

Generate a two-part pin hinge. Creates `<name>_leaf_a` and `<name>_leaf_b`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Base name (produces `<name>_leaf_a` and `<name>_leaf_b`) |
| `hinge_type` | string | `"pin"` | Hinge type (currently `"pin"`) |
| `params` | string (JSON) | `"{}"` | JSON object with dimensional parameters |

**Parameters (in the `params` JSON):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `width` | float | `30` | Hinge width in mm |
| `leaf_length` | float | `20` | Length of each leaf in mm |
| `leaf_thickness` | float | `2` | Thickness of each leaf in mm |
| `pin_diameter` | float | `3` | Pin diameter in mm |
| `clearance` | float | `0.3` | Clearance between interlocking barrels in mm |
| `barrel_count` | int | `3` | Number of interlocking barrel segments |

**Example usage:**

```json
{
  "name": "create_hinge",
  "arguments": {
    "name": "lid_hinge",
    "hinge_type": "pin",
    "params": "{\"width\": 40, \"leaf_length\": 25, \"pin_diameter\": 3, \"clearance\": 0.3, \"barrel_count\": 5}"
  }
}
```

**Example response:**

```json
{
  "leaf_a": { "name": "lid_hinge_leaf_a", "bbox": { "x": 40.0, "y": 25.0, "z": 5.0 } },
  "leaf_b": { "name": "lid_hinge_leaf_b", "bbox": { "x": 40.0, "y": 25.0, "z": 5.0 } }
}
```

**Tips:**
- Use an odd `barrel_count` so that one leaf has more barrels, providing a natural "male" and "female" side.
- A clearance of 0.3mm works well for most FDM printers. Increase to 0.4mm for lower-resolution printers.
- The hinge requires a separate pin (e.g., a piece of 3mm filament) to assemble.

---

[Back to Tool Index](../README.md)
