# `create_snap_fit`

**Category:** Parametric Components

Generate a cantilever snap-fit clip for joining two parts.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the snap-fit model |
| `snap_type` | string | `"cantilever"` | Snap-fit type (currently `"cantilever"`) |
| `params` | string (JSON) | `"{}"` | JSON object with dimensional parameters |

**Parameters (in the `params` JSON):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `beam_length` | float | `10` | Length of the cantilever beam in mm |
| `beam_width` | float | `5` | Width of the beam in mm |
| `beam_thickness` | float | `1.5` | Thickness of the beam in mm |
| `hook_depth` | float | `1.0` | Depth of the hook overhang in mm |
| `hook_length` | float | `2.0` | Length of the hook in mm |

**Example usage:**

```json
{
  "name": "create_snap_fit",
  "arguments": {
    "name": "clip",
    "snap_type": "cantilever",
    "params": "{\"beam_length\": 12, \"beam_width\": 6, \"beam_thickness\": 1.5, \"hook_depth\": 1.2}"
  }
}
```

**Example response:**

```json
{
  "name": "clip",
  "snap_type": "cantilever",
  "bbox": { "x": 6.0, "y": 1.5, "z": 13.2 }
}
```

**Tips:**
- Use `combine_models` to attach the snap-fit to your enclosure body.
- Print the beam along its length (not bridging) for maximum strength.

---

[Back to Tool Index](../README.md)
