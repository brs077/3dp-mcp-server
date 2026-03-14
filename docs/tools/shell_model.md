# `shell_model`

**Category:** Modification

Hollow out a solid model, optionally removing faces to create openings.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the new shelled model |
| `source_name` | string | *required* | Name of the existing model to shell |
| `thickness` | float | `2.0` | Wall thickness in mm |
| `open_faces` | string (JSON) | `"[]"` | JSON list of face directions to remove: `"top"`, `"bottom"`, `"front"`, `"back"`, `"left"`, `"right"` |

**Example usage:**

```json
{
  "name": "shell_model",
  "arguments": {
    "name": "box_shell",
    "source_name": "box",
    "thickness": 1.5,
    "open_faces": "[\"top\"]"
  }
}
```

**Example response:**

```json
{
  "name": "box_shell",
  "bbox": { "x": 50.0, "y": 30.0, "z": 20.0 },
  "volume_mm3": 8200.00,
  "wall_thickness": 1.5,
  "open_faces": ["top"]
}
```

**Tips:**
- Shelling with no open faces creates a fully enclosed hollow object (useful for lightweight parts).
- Opening the top face is common for creating enclosures, trays, and cups.

---

[Back to Tool Index](../README.md)
